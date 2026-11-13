from pydantic import BaseModel
class BlogState(BaseModel):
    # User Input
    topic : str =""
    audience: str = "general reader"

    # Research Output
    research: str=""
    research_feedback: str=""

    # writer Output
    draft: str=""
    draft_feedback: str=""
    
    # Editor Output
    final_blog : str = ""

    # MetaData 
    revision_count : int=0