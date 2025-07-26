from __future__ import annotations

from typing import Annotated, Any, Dict, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.services.memory.memory_manager import query
from src.services.rag.prompts.prompt import RAG_PROMPT_TEMPLATE
from src.services.rag.utils.llm import get_response_llm


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str


class RAGChat:
    """Manages the Retrieval-Augmented Generation chat process."""

    def __init__(self, thread_id: str = "assignment"):
        self.thread_id = thread_id
        self.llm = get_response_llm()
        self.prompt_template = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
        self.graph = self._create_rag_graph()

    async def _generate_response(self, state: State) -> Dict[str, Any]:
        """Generate assistant response."""
        prompt = self.prompt_template.format(context=state.get("context", ""))
        messages = [SystemMessage(content=prompt), *state["messages"]]
        response = await self.llm.ainvoke(messages)
        return {"messages": [response]}

    def _create_rag_graph(self):
        builder = StateGraph(State)
        builder.add_node("generate", self._generate_response)
        builder.add_edge(START, "generate")
        builder.add_edge("generate", END)
        return builder.compile(checkpointer=MemorySaver())

    async def process_user_input(self, user_input: str) -> str:
        """Return assistant reply for *user_input*."""
        context_docs = await query(user_input)
        context = "\n".join(context_docs)
        initial_state: State = {
            "messages": [HumanMessage(content=user_input)],
            "context": context,
        }
        config = {"configurable": {"thread_id": self.thread_id}}
        final_state: State = await self.graph.ainvoke(initial_state, config)
        return final_state["messages"][-1].content


async def process_user_input(user_input: str, thread_id: str = "assignment") -> str:
    """Convenience wrapper around `RAGChat.process_user_input`."""
    chat = RAGChat(thread_id=thread_id)
    return await chat.process_user_input(user_input)
