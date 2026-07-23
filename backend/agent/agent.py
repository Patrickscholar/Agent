import json
import os

class Agent:
    def __init__(self, config_path="Agent\\backend\\config.json"):
        # Load config from JSON
        self.config = self._load_config(config_path)
        
        # Extract configurations
        self.ollama_config = self.config["ollama"]
        self.agent_config = self.config["agent"]
        self.cost_config = self.config["cost_tracking"]
        self.tools_config = self.config["tools"]
        
        # Cost tracking
        self.total_costs = {"input_tokens": 0, "output_tokens": 0, "time": 0}
        self.call_history = []
        self.verbose = self.agent_config.get("verbose", False)
    
    def _load_config(self, config_path):
        """Load and validate config from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def run(self, task):
        """Main orchestration method - to be implemented"""
        raise NotImplementedError("run() method must be implemented")
    
    def _log_costs(self, stage, metrics):
        """Log costs for a stage"""
        if not self.cost_config.get("enabled"):
            return
        
        print(f"[{stage.upper()}] Tokens: {metrics['input']} in + {metrics['output']} out | "
              f"Time: {metrics['time']:.2f}s")
        
        self.total_costs["input_tokens"] += metrics['input']
        self.total_costs["output_tokens"] += metrics['output']
        self.total_costs["time"] += metrics['time']
        self.call_history.append({"stage": stage, **metrics})
    
    def _print_summary(self):
        """Print summary of costs"""
        total_tokens = self.total_costs["input_tokens"] + self.total_costs["output_tokens"]
        print(f"\n[SUMMARY] Total tokens: {total_tokens} | Total time: {self.total_costs['time']:.2f}s")
    
    def reset_stats(self):
        """Reset cost tracking for next run"""
        self.total_costs = {"input_tokens": 0, "output_tokens": 0, "time": 0}
        self.call_history = []