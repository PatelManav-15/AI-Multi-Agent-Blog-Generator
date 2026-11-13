from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from state import BlogState
from agent import get_llm, researcher_agent, writer_agent, editor_agent

MAX_REVISION = 3

def researcher_node(state: BlogState):
    research = researcher_agent(get_llm(), state.topic, state.audience, state.research_feedback)
    return {"research": research, "research_feedback": ""}

def review_research(state: BlogState):
    decision = interrupt({"stage": "research", "content": state.research})
    if decision.get("action") == "revise":
        return {"research_feedback": decision.get("feedback", "Please improve the research.")}
    return {"research_feedback": ""}

def route_research(state: BlogState) -> Literal["research", "writer"]:
    return "research" if state.research_feedback else "writer"

def writer_node(state: BlogState):
    draft = writer_agent(get_llm(), state.topic, state.audience, state.research, state.draft_feedback)
    return {"draft": draft, "draft_feedback": ""}

def review_draft(state: BlogState):
    decision = interrupt({"stage": "draft", "content": state.draft})
    if decision.get("action") == "revise" and state.revision_count < MAX_REVISION:
        return {"draft_feedback": decision.get("feedback", "Please improve the draft."), "revision_count": state.revision_count + 1}
    return {"draft_feedback": ""}

def route_draft(state: BlogState) -> Literal["writer", "edit"]:
    return "writer" if state.draft_feedback else "edit"

def editor_node(state: BlogState):
    final = editor_agent(get_llm(), state.topic, state.audience, state.draft)
    return {"final_blog": final}

def build_blog_graph():
    graph = StateGraph(BlogState)
    graph.add_node("research", researcher_node)
    graph.add_node("review_research", review_research)
    graph.add_node("writer", writer_node)
    graph.add_node("review_draft", review_draft)
    graph.add_node("edit", editor_node)
    graph.add_edge(START, "research")
    graph.add_edge("research", "review_research")
    graph.add_conditional_edges("review_research", route_research)
    graph.add_edge("writer", "review_draft")
    graph.add_conditional_edges("review_draft", route_draft)
    graph.add_edge("edit", END)
    return graph.compile(checkpointer=InMemorySaver())
