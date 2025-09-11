"""
Analytics & Reporting Agent using LangChain
============================================
An agentic AI system for answering quantitative and reasoning-based 
executive questions using SQL and contextual explanations.
"""

import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from db import get_db
from config.llm import get_llm

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set Gemini API key with proper error handling
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    os.environ["GOOGLE_API_KEY"] = google_api_key
else:
    print("⚠️  WARNING: GOOGLE_API_KEY not found in environment. Analytics agent may not work properly.")

# -------- Database Utilities --------
def execute_sql(query: str, params: tuple = ()) -> List[Dict]:
    """Execute SQL query using the shared database connection"""
    import sqlite3
    
    # Use the correct database path
    db_path = Path(__file__).parent.parent.parent / "databases" / "erp.db"
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_table_schema(table_name: str) -> str:
    schema = execute_sql(f"PRAGMA table_info({table_name})")
    return f"Table: {table_name}\n" + "\n".join([f"  - {col['name']} ({col['type']})" for col in schema])

def get_all_tables() -> List[str]:
    tables = execute_sql("SELECT name FROM sqlite_master WHERE type='table'")
    return [t['name'] for t in tables]

# -------- Tool Functions --------
@tool
def text_to_sql(question: str, context: Optional[str] = None) -> str:
    """
    Convert a natural language question to SQL, execute it, and return results.
    """
    tables = get_all_tables()
    schema_info = "\n".join([get_table_schema(t) for t in tables[:10]])
    prompt = f"""
    Given the following database schema:
    {schema_info}

    Convert this question to a SQL query: {question}
    Additional context: {context if context else 'None'}
    Return only the SQL query without any explanation.
    SQL Query:
    """
    llm = get_llm()  # Use shared LLM configuration
    response = llm.invoke(prompt)
    # Handle both string and AIMessage responses
    if hasattr(response, 'content'):
        sql_query = response.content.strip()
    else:
        sql_query = str(response).strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    try:
        results = execute_sql(sql_query)
        if results:
            df = pd.DataFrame(results)
            return f"Query executed successfully. Results:\n{df.to_string()}\n\nSQL: {sql_query}"
        else:
            return f"Query executed but returned no results.\nSQL: {sql_query}"
    except Exception as e:
        return f"Error executing SQL query: {str(e)}\nGenerated SQL: {sql_query}"

@tool
def rag_definition(term: str, module: Optional[str] = None) -> str:
    """
    Search for business definitions, metrics, and contextual information.
    """
    # Simulate vector search using Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    # For demo, just search glossary table
    query = "SELECT term, definition, module FROM glossary WHERE term LIKE ?"
    results = execute_sql(query, (f"%{term}%",))
    if module:
        results = [r for r in results if r['module'] == module]
    if not results:
        return f"No definitions found for '{term}'"
    output = f"Found {len(results)} relevant definitions:\n\n"
    for i, item in enumerate(results, 1):
        output += f"{i}. Term: {item['term']}\n   Definition: {item['definition']}\n   Module: {item['module']}\n\n"
    return output

@tool
def analytics_reporting(data: str, operation: str, params: Optional[Dict] = {}) -> str:
    """
    Perform data analysis, aggregation, or visualization.
    """
    try:
        df = pd.read_json(data)
        if operation == "aggregate":
            group_by = params.get('group_by', [])
            agg_func = params.get('agg_func', 'sum')
            value_col = params.get('value_col')
            if group_by and value_col:
                result = df.groupby(group_by)[value_col].agg(agg_func)
                return f"Aggregation result:\n{result.to_string()}"
            else:
                return df.describe().to_string()
        elif operation == "visualize":
            viz_type = params.get('type', 'bar')
            x_col = params.get('x')
            y_col = params.get('y')
            viz_spec = {
                "type": viz_type,
                "data": df.to_dict('records'),
                "encoding": {
                    "x": {"field": x_col, "type": "nominal"},
                    "y": {"field": y_col, "type": "quantitative"}
                }
            }
            return f"Visualization spec:\n{json.dumps(viz_spec, indent=2)}"
        elif operation == "summarize":
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "numeric_summary": df.describe().to_dict(),
                "null_counts": df.isnull().sum().to_dict()
            }
            return f"Data summary:\n{json.dumps(summary, indent=2)}"
        else:
            return f"Unknown operation: {operation}"
    except Exception as e:
        return f"Error in analytics operation: {str(e)}"

# -------- Agent System Prompt --------
ANALYTICS_AGENT_SYSTEM = """You are the Analytics & Reporting Agent for Helios Dynamics.

Your responsibilities:
- Answer executive questions using SQL and contextual explanations
- Retrieve business definitions and metrics
- Perform analytics and generate visualizations

Available tools: {tools}
Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

# -------- Build the Analytics Agent --------
def create_analytics_agent():
    """Create and configure the Analytics Agent"""
    llm = get_llm()  # Use shared LLM configuration
    tools = [text_to_sql, rag_definition, analytics_reporting]
    memory = ConversationBufferMemory()
    prompt = PromptTemplate.from_template(ANALYTICS_AGENT_SYSTEM)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        memory=memory
    )
    return executor

# Export the executor
executor = create_analytics_agent()

if __name__ == "__main__":
    print("📊 Helios Dynamics - Analytics Agent Ready!")
    print("Ask me about revenue, customers, definitions, or analytics.")
    try:
        while True:
            user_input = input("Analytics Agent > ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            try:
                result = executor.invoke({"input": user_input})
                print(f"\n{result['output']}\n")
            except Exception as e:
                print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print("\nGoodbye!")