import os
import subprocess
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
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            if out is None:
                out_str = ""
            else:
              out_str = out.decode("utf-8")
            if err is not None:
                err_str = err.decode("utf-8")
                return f"Error: {err_str}"
            else:
                return out_str

        except Exception as e:
            return "Error: " + str(e)            

    async def _arun(
        self,
        cmd: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        # TODO: Add aiofiles method
        raise NotImplementedError
