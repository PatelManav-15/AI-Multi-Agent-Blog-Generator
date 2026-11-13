
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# Get LLM
def get_llm(
    model_name: str = "openai/gpt-oss-20b",
    temperature: float = 0.5
):
    api_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )
    return llm


# Research Agent
RESEARCH_PROMPT = ChatPromptTemplate.from_messages([
    {
        "role": "system",
        "content": """
        You are a research agent. Given a blog topic and
        target audience, produce a clear, structured
        research outline.

        Include:
        1. 5-7 key points the blog should cover
        2. Important facts, statistics, or examples
        3. Suggested angle or hook

        Be concise. Use bullet points.
        Do not write the full blog yet.
        """
    },
    {
        "role": "user",
        "content": """
        Topic: {topic}
        Audience: {audience}
        {revision_hints}

        Write the research outline now.
        """
    }
])


def researcher_agent(
    llm: ChatGroq,
    topic: str,
    audience: str,
    feedback: str = ""
) -> str:

    revision_hints = (
        f"The human provided this feedback on your "
        f"previous research: {feedback}. Please address it."
    )

    if not feedback:
        revision_hints = "This is your first attempt."

    chain = RESEARCH_PROMPT | llm

    result = chain.invoke({
        "topic": topic,
        "audience": audience,
        "revision_hints": revision_hints
    })

    return result.content


# Writer Agent
WRITER_PROMPT = ChatPromptTemplate.from_messages([
    {
        "role": "system",
        "content": """
        You are a blog writer agent. Using the research
        notes provided, write a complete, engaging blog.

        Rules:
        - Length: 500-800 words
        - Structure: Catchy title, introduction,
          3-5 sections with H2 headings, conclusion
        - Tone: Clear, friendly, suited to the audience
        - Use Markdown formatting
        - Do not add a word count at the end
        """
    },
    {
        "role": "user",
        "content": """
        Topic: {topic}
        Audience: {audience}
        Research Notes: {research}

        {revision_hints}

        Write the full blog post now.
        """
    }
])


def writer_agent(
    llm: ChatGroq,
    topic: str,
    audience: str,
    research: str = "",
    feedback: str = ""
) -> str:

    revision_hints = (
        f"The human provided this feedback on your "
        f"previous draft: {feedback}. "
        f"Please apply these changes."
    )

    if not feedback:
        revision_hints = "This is your first attempt."

    chain = WRITER_PROMPT | llm
    print(revision_hints)

    result = chain.invoke({
        "topic": topic,
        "audience": audience,
        "research": research,
        "revision_hints": revision_hints
    })

    return result.content


# Editor Agent
EDITOR_PROMPT = ChatPromptTemplate.from_messages([
    {
        "role": "system",
        "content": """
        You are an editor agent, the final quality
        gate before publishing.

        Take the draft and produce a polished version.

        Specifically:
        - Fix grammar, spelling, and awkward phrasing
        - Tighten wordy sentences
        - Improve flow and transitions
        - Improve the title and introduction if needed
        - Keep the same structure and Markdown formatting
        - Use natural, simple, human-friendly language
        - Avoid unnecessarily complex words

        Output only the final polished blog post.
        """
    },
    {
        "role": "user",
        "content": """
        Topic: {topic}
        Audience: {audience}
        Draft: {draft}

        Return the polished blog post.
        """
    }
])


def editor_agent(
    llm: ChatGroq,
    topic: str,
    audience: str,
    draft: str = ""
) -> str:

    chain = EDITOR_PROMPT | llm

    result = chain.invoke({
        "topic": topic,
        "audience": audience,
        "draft": draft
    })

    return result.content
