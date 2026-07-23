from tools.toolsContract import ToolContract
from typing import Dict, Any
import os


class EditFileTool(ToolContract):

    def get_definition(self) -> str:
        return (
            "Edits an existing file by replacing its contents."
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:

        path = input_data["path"]
        content = input_data["content"]

        if not os.path.exists(path):
            return {
                "success": False,
                "message": "File not found.",
                "data": {}
            }

        with open(path, "w") as file:
            file.write(content)

        return {
            "success": True,
            "message": "File updated successfully.",
            "data": {
                "path": path
            }
        }