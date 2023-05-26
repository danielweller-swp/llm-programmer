# Copied and adapted from langchain's initialize.py
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from typing import Any, Optional, Sequence
from langchain.agents.agent import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.tools.base import BaseTool
from typing import Type
from langchain.agents.agent import BaseSingleActionAgent

def initialize_agent(
    tools: Sequence[BaseTool],
    llm: BaseLanguageModel,
    agent_cls: Type[BaseSingleActionAgent],
    callback_manager: Optional[BaseCallbackManager] = None,
    agent_kwargs: Optional[dict] = None,
    **kwargs: Any,
) -> AgentExecutor:
    agent_kwargs = agent_kwargs or {}
    agent_obj = agent_cls.from_llm_and_tools(
        llm, tools, callback_manager=callback_manager, **agent_kwargs
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent_obj,
        tools=tools,
        callback_manager=callback_manager,
        **kwargs,
    )
