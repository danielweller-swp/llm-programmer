from typing import Any, Dict, List, Optional, Union, Callable

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult

def extract_comment(action_log: str):
  index = action_log.index("Action:")
  return action_log[:index]

class MyCallbackHandler(BaseCallbackHandler):
    def __init__(self, on_event: Callable[[dict], None]) -> None:
        """Initialize callback handler."""
        self.on_event = on_event

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        return

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing."""
        return

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""
        return

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        return

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        return


    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        return

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        return

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Do nothing."""
        return

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        msg = extract_comment(action.log)
        self.on_event({
            "type": "action",
            "msg": msg,
            "tool": action.tool,
            "tool_input": action.tool_input
            })
        return        

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        return

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        return

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        return

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        msg = extract_comment(finish.log)

        self.on_event({
            "type": "end",
            "msg": msg,
            "return_values": finish.return_values
        })
