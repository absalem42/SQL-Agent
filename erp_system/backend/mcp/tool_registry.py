"""
Tool Registry for MCP (Model Context Protocol) adapter
Manages registration and retrieval of tools for the agent system.
"""

from typing import List, Dict, Any, Callable
from langchain.tools import Tool

class ToolRegistry:
    """Registry for managing agent tools"""
    
    def __init__(self):
        self._tools: List[Tool] = []
        self._tool_map: Dict[str, Tool] = {}
    
    def register_tool(self, tool: Any) -> None:
        """Register a tool in the registry"""
        # Accept any tool type from LangChain (Tool, StructuredTool, etc.)
        if hasattr(tool, 'name') and hasattr(tool, 'run'):
            self._tools.append(tool)
            self._tool_map[tool.name] = tool
        else:
            raise TypeError(f"Expected tool with 'name' and 'run' attributes, got {type(tool)}")
    
    def get_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_tool(self, name: str) -> Tool:
        """Get a specific tool by name"""
        return self._tool_map.get(name)
    
    def list_tool_names(self) -> List[str]:
        """Get list of all tool names"""
        return list(self._tool_map.keys())
    
    def clear(self) -> None:
        """Clear all registered tools"""
        self._tools.clear()
        self._tool_map.clear()
