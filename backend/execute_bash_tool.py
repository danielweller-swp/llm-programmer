import subprocess
import asyncio
from typing import Optional, Type

from pydantic import BaseModel, Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool

class ExecuteBashInput(BaseModel):
    """Input for ExecuteBashInput."""

    cmd: str = Field(..., description="The bash command to execute")


def _handle_cmd_output(out, err):
  out_str = out.decode("utf-8")
  err_str = err.decode("utf-8")

  if out_str == "" and err_str != "":
    return f"Error: {err_str}"
  elif out_str != "" and err_str == "":
    return out_str
  elif out_str == "" and err_str == "":
     return ""
  else:
     return f"Output: {out_str}\nError: {err_str}"

class ExecuteBashTool(BaseTool):
    name: str = "execute_bash"
    args_schema: Type[BaseModel] = ExecuteBashInput
    description: str = "Execute a shell (bash) command"
    verbose = True

    def _run(
        self,
        cmd: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
          proc = subprocess.Popen(f"timeout 30 {cmd}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
          out, err = proc.communicate()
          return _handle_cmd_output(out, err)

        except Exception as e:
          return "Error: " + str(e)            

    async def _arun(
        self,
        cmd: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        try:
          proc = await asyncio.create_subprocess_shell(f"timeout 5 {cmd}", stdout=asyncio.subprocess.PIPE, shell=True)
          out, err = await proc.communicate()
          return _handle_cmd_output(out, err)

        except Exception as e:
          return "Error: " + str(e)               
