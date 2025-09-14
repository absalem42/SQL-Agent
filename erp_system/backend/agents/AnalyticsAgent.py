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

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# Set Gemini API key from environment variable
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
mdPath = "metrics.md"
presist_dir = "metrics_docs"



# -------- Database Utilities --------
def execute_sql(query: str, params: tuple = ()) -> List[Dict]:
    import sqlite3
    conn = sqlite3.connect(os.getenv("DB_PATH", ""))
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
    Convert a natural language question to SQL, execute it, and return results. Make sure  it is only a read only query and does not modify the database.
    """
    tables = get_all_tables()
    schema_info = "\n".join([get_table_schema(t) for t in tables])  # Limit to first 3 tables for brevity
    prompt = f"""
    Given the following database schema:
    {schema_info}

    Convert this question to a SQL query: {question}
    Additional context: {context if context else 'None'}
    Return only the SQL query without any explanation.
    SQL Query:
    """

    llm = GoogleGenerativeAI(model="gemini-1.5-flash")
    sql_query = llm.invoke(prompt).strip().replace("```sql", "").replace("```", "").strip()
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
def rag_definition(query: str) -> str:
    """
    Search for business definitions, metrics, and contextual information.
    """
    # Fail-safe: if embeddings or API key aren't available, return a graceful message
    try:
        # Ensure persist directory exists to avoid runtime errors
        os.makedirs(presist_dir, exist_ok=True)
        # Use current Google embeddings model name
        embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        vectordb = Chroma(persist_directory=presist_dir, embedding_function=embedding_model)
        retriever = vectordb.as_retriever()
        llm = GoogleGenerativeAI(model="gemini-1.5-flash")
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
        result = qa_chain.invoke({
            "query": (
                "You are the first tool in a business analytics agent. "
                "You will receive a question from the user, and you have access to a knowledge base "
                "of business definitions and metrics. Based on the question, search the knowledge base "
                "and return any relevant definitions or metrics that might help the next tool. "
                "Return only relevant information, and nothing else. "
                f"Here is the question: {query}"
            )
        })
        answer = result.get("result", "")
        return answer if answer else "No relevant information found."
    except Exception as e:
        return f"RAG unavailable ({e}). Proceed with SQL analysis without RAG context."

@tool
def analytics_reporting(input_data):
    """
    Simple analytics function for data analysis and visualization.
    Input: dict with 'data' and optional 'operation' and 'params'
    """
    try:
        # Parse input if it's a string
        if isinstance(input_data, str):
            # Remove markdown code blocks if present
            input_data = input_data.strip()
            if input_data.startswith('```json'):
                input_data = input_data[7:]  # Remove ```json
            if input_data.endswith('```'):
                input_data = input_data[:-3]  # Remove ```
            input_data = input_data.strip()
            input_data = json.loads(input_data)
        
        # Get data and create DataFrame
        data = input_data.get("data", [])
        if not data:
            return "No data provided"
        
        df = pd.DataFrame(data)
        if df.empty:
            return "Empty dataset"
        
        # Get operation type
        operation = input_data.get("operation", "summarize")
        params = input_data.get("params", {})
        
        # Handle operations
        if operation == "visualize":
            viz_type = params.get("type", "bar")
            x_col = params.get("x", df.columns[0])
            y_col = params.get("y", df.columns[1] if len(df.columns) > 1 else df.columns[0])
            
            # Support multiple chart types
            chart_types = ["bar", "line", "scatter", "pie", "area", "histogram", "box"]
            if viz_type not in chart_types:
                viz_type = "bar"
            
            viz_spec = {
                "type": viz_type,
                "data": df.to_dict('records'),
                "x": x_col,
                "y": y_col,
                "title": params.get("title", f"{viz_type} chart")
            }
            
            # Add specific configs for different chart types
            if viz_type == "pie":
                viz_spec["label"] = x_col
                viz_spec["value"] = y_col
            elif viz_type == "histogram":
                viz_spec["column"] = x_col
            elif viz_type == "box":
                viz_spec["column"] = y_col
                viz_spec["category"] = x_col
            
            return json.dumps(viz_spec, indent=2)
        
        elif operation == "aggregate":
            group_col = params.get("group_by")
            value_col = params.get("value_col")
            agg_func = params.get("agg_func", "sum")
            
            if group_col and value_col:
                result = df.groupby(group_col)[value_col].agg(agg_func)
                return result.to_string()
            else:
                return df.describe().to_string()
        
        else:  # summarize
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(3).to_dict('records')
            }
            return json.dumps(summary, indent=2)
            
    except Exception as e:
        return f"Error: {str(e)}"

# -------- Agent System Prompt --------
ANALYTICS_AGENT_SYSTEM = """You are the Analytics & Reporting Agent for Helios Dynamics.

Your responsibilities:
- Retrieve business definitions and metrics for anything you terms you do not understand or unsure of using the rag_definition tool. It does not have access to the database, so use it for definitions and context only.
- Answer executive questions using SQL and contextual explanations. You can use the text_to_sql tool to convert natural language questions into SQL queries and execute them against the database. Make sure to input a normal natural language question to the text_to_sql tool, and not SQL directly. Ensure that the SQL queries are read-only and do not modify the database.
- Perform analytics and generate visualizations. You can use the analytics_reporting tool, which take json as input based the retrieved data from sql to perform data analysis, aggregation, or visualization. When using analytics_reporting tool, format your input like this:

Action Input: {{
  "data": [{{"column1": "value1", "column2": 123}}],
  "operation": "visualize",
  "params": {{"type": "bar", "x": "column1", "y": "column2"}}
}}


DO NOT use strings for the data field - use actual JSON objects.

After you finish excuting return in the final answer the following:
-data retreived in table format, if any
-json output of any visualizations you created, if any
-Your insights and analysis of the data

Available tools: {tools}
Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action, for text_to_sql provide the question and optional context, for rag_definition provide the term and optional module, for analytics_reporting provide a dict with data and operation
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question, always include your insights on the data and any visualizations if applicable.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

# -------- Build the Analytics Agent --------
def create_analytics_agent():
    llm = GoogleGenerativeAI(model="gemini-1.5-flash")
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