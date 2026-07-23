# agent/layers/planner/planner.py

import time
import ollama

from agent.layers.layerContract import LayerContract
from agent.layers.planner.plannerContract import PlannerContract
from agent.context import Context


class Planner(LayerContract, PlannerContract):

    def __init__(self, planner_config: dict, ollama_config: dict):
        self.model = ollama_config.get("model")
        self.base_url = ollama_config.get("base_url")
        self.temperature = planner_config.get("temperature", ollama_config.get("temperature"))

    # ---------------------------
    # PlannerContract method
    # ---------------------------
    def plan(self, task: str) -> dict:
        """
        Pure business logic. No Context dependency.
        Can be tested/used standalone.
        """
        start_time = time.time()

        prompt = self._build_prompt(task)

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                "temperature": self.temperature
            },
            stream=False
        )

        end_time = time.time()

        return {
            "plan": response['response'],
            "metrics": {
                "input": response.get('prompt_eval_count', 0),
                "output": response.get('eval_count', 0),
                "time": round(end_time - start_time, 3)
            }
        }

    def _build_prompt(self, task: str) -> str:
        return f"""You are a planning agent. Break down the following task into clear,
actionable steps. Each step should be specific and executable.

Task: {task}

Provide a numbered list of steps to complete this task."""

    # ---------------------------
    # LayerContract method
    # ---------------------------
    def run(self, context: Context) -> None:
        """
        Pipeline adapter. Reads from and writes to shared context.
        """
        result = self.plan(context.task)

        context.plan = result['plan']
        context.add_metrics("planner", result['metrics'])