# agent/layers/evaluator/evaluator.py

import time
import json
import ollama

from agent.layers.layerContract import LayerContract
from agent.layers.evaluator.evaluatorContract import EvaluatorContract
from agent.context import Context


class Evaluator(LayerContract, EvaluatorContract):

    def __init__(self, evaluator_config: dict, ollama_config: dict):
        self.model = ollama_config.get("model")
        self.base_url = ollama_config.get("base_url")
        self.temperature = evaluator_config.get("temperature", ollama_config.get("temperature"))

    # ---------------------------
    # EvaluatorContract method
    # ---------------------------
    def evaluate(self, task: str, result: dict) -> dict:
        """
        Pure business logic. No Context dependency.
        Can be tested/used standalone.
        """
        start_time = time.time()

        prompt = self._build_prompt(task, result)

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": self.temperature},
            stream=False
        )

        end_time = time.time()

        try:
            parsed = json.loads(response['response'])
        except json.JSONDecodeError:
            parsed = {
                "done": False,
                "correct": False,
                "thoughts": "Failed to parse evaluator response.",
                "next_action": "Retry the previous step."
            }

        return {
            "done": parsed.get("done", False),
            "correct": parsed.get("correct", False),
            "thoughts": parsed.get("thoughts", ""),
            "next_action": parsed.get("next_action", None),
            "metrics": {
                "input": response.get('prompt_eval_count', 0),
                "output": response.get('eval_count', 0),
                "time": round(end_time - start_time, 3)
            }
        }

    def _build_prompt(self, task: str, result: dict) -> str:
        return f"""You are an evaluator agent. Review the result of an executed task.

Original task: {task}
Result: {result.get('result')}
Observations: {result.get('observations')}

Answer the following:
1. Is the result correct and complete?
2. Is the original task fully done?
3. If not done, what should happen next?

Respond ONLY in valid JSON:
{{
    "done": true or false,
    "correct": true or false,
    "thoughts": "your reasoning",
    "next_action": "what to do next if not done, else null"
}}"""

    # ---------------------------
    # LayerContract method
    # ---------------------------
    def run(self, context: Context) -> None:
        """
        Pipeline adapter. Reads from and writes to shared context.
        """
        result = self.evaluate(context.task, {
            "result": context.result,
            "observations": context.observations
        })

        context.done = result['done']
        context.history.append({
            "plan": context.plan,
            "result": context.result,
            "thoughts": result['thoughts'],
            "next_action": result['next_action']
        })
        context.add_metrics("evaluator", result['metrics'])