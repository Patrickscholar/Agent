from tools.toolsContract import ToolContract
from typing import Dict, Any
import os


class CreateFileTool(ToolContract):

    def get_definition(self) -> str:
        return (
            "Creates a new file at the specified path. "
            "If the parent directory does not exist, it is created. "
            "Optionally writes content into the file."
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:

        path = input_data["path"]
        content = input_data.get("content", "")

        directory = os.path.dirname(path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

        return {
            "success": True,
            "message": "File created successfully.",
            "data": {
                "path": path
            }
        }