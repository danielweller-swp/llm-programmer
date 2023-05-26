import subprocess
import asyncio
from typing import Optional, Type

from pydantic import BaseModel, Field

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from langchain.tools.file_management.utils import (
    BaseFileToolMixin,
)


class ExecuteBashInput(BaseModel):
    """Input for ExecuteBashInput."""

    cmd: str = Field(..., description="The bash command to execute")


def _handle_cmd_output(out, err):
  if out is None:
      out_str = ""
  else:
    out_str = out.decode("utf-8")
  if err is not None:
      err_str = err.decode("utf-8")
      return f"Error: {err_str}"
  else:
      return out_str
class ExecuteBashTool(BaseFileToolMixin, BaseTool):
    name: str = "execute_bash"
    args_schema: Type[BaseModel] = ExecuteBashInput
    description: str = "Execute a shell (bash) command"

    def _run(
        self,
        cmd: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
          print("===START DEBUG BASH EXECUTION===")
          print(f"Calling {cmd}...")          
          proc = subprocess.Popen(f"timeout 5 {cmd}", stdout=subprocess.PIPE, shell=True)
          print(f"Done. Getting stdout/stderr...")          
          out, err = proc.communicate()
          print(f"Done.")
          print("===END DEBUG BASH EXECUTION===")          
          return _handle_cmd_output(out, err)

        except Exception as e:
          return "Error: " + str(e)            

    async def _arun(
        self,
        cmd: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        try:
          print("===START DEBUG BASH EXECUTION===")
          print(f"Calling ${cmd}...")
          proc = await asyncio.create_subprocess_shell(f"timeout 5 {cmd}", stdout=asyncio.subprocess.PIPE, shell=True)
          print(f"Done. Getting stdout/stderr...")
          out, err = await proc.communicate()
          print(f"Done.")
          print("===END DEBUG BASH EXECUTION===")
          return _handle_cmd_output(out, err)

        except Exception as e:
          return "Error: " + str(e)               
