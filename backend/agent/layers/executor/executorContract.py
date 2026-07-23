from abc import ABC, abstractmethod

class ExecutorContract(ABC):
    
    @abstractmethod
    def execute(self, plan: dict, tools: list) -> dict:
        """
        Execute the plan steps and call tools as needed.
        
        Args:
            plan: dict - The plan from the planner
                - plan: list of steps
                    - step: int - Step number
                    - description: str - What needs to be done
            tools: list - List of ToolContract instances
        
        Returns:
            dict:
                - result: str - The final output
                - observations: list - Raw observations from each step
                    - step: int - Step number
                    - tool_used: str - Tool that was called, None if no tool
                    - output: any - Raw output from tool or LLM
                - metrics: dict
                    - input: int - Input tokens
                    - output: int - Output tokens
                    - time: float - Execution time in seconds
        """
        pass
    
    @abstractmethod
    def _decide_tool(self, step: str, tools: list) -> dict:
        """
        Decide which tool to use for a given step.
        
        Args:
            step: str - Step description
            tools: list - List of ToolContract instances
        
        Returns:
            dict:
                - tool: str - Tool name, None if no tool needed
                - tool_input: dict - Parameters to pass to tool, None if no tool
        """
        pass