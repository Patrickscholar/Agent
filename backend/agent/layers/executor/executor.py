# agent/layers/executor/executor.py

import time
import ollama

from agent.layers.layerContract import LayerContract
from agent.layers.executor.executorContract import ExecutorContract
from agent.context import Context


class Executor(LayerContract, ExecutorContract):

    def __init__(self, executor_config: dict, ollama_config: dict, tools: list):
        self.tools = tools  # injected once, not passed per call
        self.model = ollama_config.get("model")
        self.base_url = ollama_config.get("base_url")
        self.temperature = executor_config.get("temperature", ollama_config.get("temperature"))

    # ---------------------------
    # ExecutorContract method
    # ---------------------------
    def execute(self, plan: dict) -> dict:
        """
        Pure business logic. No Context dependency.
        Executes each step in the plan, calling tools when needed.
        """
        start_time = time.time()

        observations = []
        total_input_tokens = 0
        total_output_tokens = 0
        final_output = None

        for step in plan['plan']:
            description = step['description']

            tool_decision = self._decide_tool(description)

            if tool_decision['tool']:
                tool = self._get_tool(tool_decision['tool'])
                tool_result = tool.run(tool_decision['tool_input'])
                output = tool_result['result']
                tool_used = tool_decision['tool']
            else:
                response = ollama.generate(
                    model=self.model,
                    prompt=description,
                    options={"temperature": self.temperature},
                    stream=False
                )
                output = response['response']
                tool_used = None
                total_input_tokens += response.get('prompt_eval_count', 0)
                total_output_tokens += response.get('eval_count', 0)

            observations.append({
                "step": step['step'],
                "tool_used": tool_used,
                "output": output
            })

            final_output = output  # last step's output becomes the result

        end_time = time.time()

        return {
            "result": final_output,
            "observations": observations,
            "metrics": {
                "input": total_input_tokens,
                "output": total_output_tokens,
                "time": round(end_time - start_time, 3)
            }
        }

    def _decide_tool(self, step: str) -> dict:
        """
        Ask Ollama which tool (if any) should be used for this step.
        """
        tools_text = ""
        for tool in self.tools:
            definition = tool.get_definition()
            tools_text += f"\n- Name: {definition['name']}\n  Description: {definition['description']}\n  Parameters: {definition['parameters']}"

        prompt = f"""You have access to the following tools:
{tools_text}

Step to execute: {step}

Decide if a tool is needed. Respond ONLY in valid JSON:
{{
    "tool": "tool_name or null",
    "tool_input": {{ "param": "value" }} or null
}}"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0},
            stream=False
        )

        import json
        try:
            decision = json.loads(response['response'])
        except json.JSONDecodeError:
            decision = {"tool": None, "tool_input": None}

        return decision

    def _get_tool(self, tool_name: str):
        for tool in self.tools:
            if tool.get_definition()['name'] == tool_name:
                return tool
        raise ValueError(f"Tool '{tool_name}' not found in registered tools")

    # ---------------------------
    # LayerContract method
    # ---------------------------
    def run(self, context: Context) -> None:
        """
        Pipeline adapter. Reads from and writes to shared context.
        """
        result = self.execute(context.plan)

        context.observations = result['observations']
        context.result = result['result']
        context.add_metrics("executor", result['metrics'])