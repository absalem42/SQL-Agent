import os
from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

class MockLLM(LLM):
    """Mock LLM for testing when Ollama is not available"""
    
    # Use class variable instead of instance variable
    _call_count: int = 0
    
    @property
    def _llm_type(self) -> str:
        return "mock"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # Increment call count to avoid infinite loops
        MockLLM._call_count += 1
        
        # Simple mock responses for testing
        prompt_lower = prompt.lower()
        
        if "thought:" in prompt_lower and "action:" in prompt_lower:
            # This is a ReAct agent prompt - provide a structured response
            
            # Extract the question/input from the prompt
            question = ""
            if "question:" in prompt_lower:
                question_part = prompt_lower.split("question:")[-1]
                if "thought:" in question_part:
                    question = question_part.split("thought:")[0].strip()
                else:
                    question = question_part.strip()
            
            # Check which tools are available in the prompt
            available_tools = []
            if "get_customers" in prompt_lower:
                available_tools.append("get_customers")
            if "get_orders" in prompt_lower:
                available_tools.append("get_orders")
            if "get_leads" in prompt_lower:
                available_tools.append("get_leads")
            if "execute_with_sales_agent" in prompt_lower:
                available_tools.append("execute_with_sales_agent")
            if "get_system_info" in prompt_lower:
                available_tools.append("get_system_info")
            if "classify_and_route" in prompt_lower:
                available_tools.append("classify_and_route")
            if "get_customer_summary" in prompt_lower:
                available_tools.append("get_customer_summary")
            if "search_customers" in prompt_lower:
                available_tools.append("search_customers")
            
            # Check if we've already taken an action (to avoid loops)
            if "observation:" in prompt_lower and MockLLM._call_count > 1:
                return """Thought: I now have the final answer
Final Answer: Here is the information you requested based on the previous action."""
            
            # Router Agent responses
            if "execute_with_sales_agent" in available_tools:
                if "system" in question or "info" in question:
                    return """I should get system information.

Action: get_system_info
Action Input: """
                else:
                    return f"""I need to route this request to the Sales Agent.

Action: execute_with_sales_agent
Action Input: {question}"""
            
            # Sales Agent responses
            elif "get_customers" in available_tools:
                if "summary" in question:
                    return """I should get customer summary statistics.

Action: get_customer_summary
Action Input: """
                elif "search" in question or "find" in question:
                    # Extract search term
                    search_term = question.replace("search", "").replace("find", "").replace("customer", "").strip()
                    return f"""I need to search for specific customers.

Action: search_customers
Action Input: {search_term}"""
                elif "lead" in question:
                    return """I should get the list of leads.

Action: get_leads
Action Input: """
                elif "order" in question:
                    return """I should get the list of orders.

Action: get_orders
Action Input: """
                else:
                    return """I should get the list of customers.

Action: get_customers
Action Input: """
            
            # Fallback for unknown tools
            else:
                if "customer" in question:
                    return """I need to help with customer information.

Action: get_customers
Action Input: """
                else:
                    return """I need to help with this request.

Final Answer: I can help you with various tasks. Please specify what you need assistance with."""
        else:
            # Regular response
            return "Mock response: I'm a test LLM. Ollama is not available."
    
    def bind(self, **kwargs):
        """Add bind method to be compatible with ReAct agents"""
        # Reset call count for new conversations
        MockLLM._call_count = 0
        return self

def get_llm():
    """Get the appropriate LLM instance"""
    import os
    
    # Try Google Gemini first
    if GOOGLE_GENAI_AVAILABLE:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            try:
                print("🤖 Using Google Gemini")
                return ChatGoogleGenerativeAI(
                    # model="gemini-2.5-flash",
                    model="gemini-2.5-flash-lite",
                    google_api_key=google_api_key,
                    temperature=0.1,
                    convert_system_message_to_human=True
                )
            except Exception as e:
                print(f"⚠️ Google Gemini configuration error: {e}")
    
    # Fallback to Ollama
    if OLLAMA_AVAILABLE:
        try:
            # Try to connect to Ollama - try both localhost and host.docker.internal
            import requests
            ollama_urls = [
                "http://localhost:11434",
                "http://host.docker.internal:11434",
                "http://172.17.0.1:11434",  # Docker bridge network
            ]
            
            for base_url in ollama_urls:
                try:
                    response = requests.get(f"{base_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Connected to Ollama at {base_url}")
                        return OllamaLLM(
                            model="llama3.1:8b",  # Use the model we actually have
                            base_url=base_url,
                            temperature=0.1
                        )
                except requests.RequestException:
                    continue
                    
            print("⚠️ Ollama not reachable from any URL")
        except Exception as e:
            print(f"Warning: Ollama configuration error: {e}")
    
    print("Using MockLLM for testing")
    return MockLLM()
