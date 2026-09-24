"""
LangGraph workflow for video generation pipeline
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import structlog

logger = structlog.get_logger()


class VideoState(TypedDict):
    """State that flows through the graph"""
    job_id: str
    niche: str
    num_images: int
    
    # Agent outputs
    topics: list[str]
    selected_topic: str
    script: str
    shots: list[str]
    image_paths: list[str]
    audio_path: str
    video_path: str
    seo_title: str
    seo_description: str
    seo_tags: list[str]
    youtube_video_id: str
    youtube_url: str
    
    # Error tracking
    error: str | None


def create_video_graph():
    """
    Create the video generation workflow graph
    
    Flow:
    START → Research → Script → Shots → [Images + Voice] → Video → SEO → Upload → END
    """
    
    # Import agent nodes
    from src.agents.research_agent import research_agent_node
    from src.agents.script_agent import script_agent_node
    from src.agents.shot_agent import shot_agent_node
    from src.agents.image_agent import image_agent_node
    from src.agents.voice_agent import voice_agent_node
    from src.agents.video_agent import video_agent_node
    from src.agents.seo_agent import seo_agent_node
    from src.agents.upload_agent import upload_agent_node
    
    # Create the graph
    workflow = StateGraph(VideoState)
    
    # Add nodes (use _agent suffix to avoid state key conflicts)
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("script_agent", script_agent_node)
    workflow.add_node("shots_agent", shot_agent_node)
    workflow.add_node("images_agent", image_agent_node)
    workflow.add_node("voice_agent", voice_agent_node)
    workflow.add_node("video_agent", video_agent_node)
    workflow.add_node("seo_agent", seo_agent_node)
    workflow.add_node("upload_agent", upload_agent_node)
    
    # Define edges (sequential flow)
    workflow.set_entry_point("research_agent")
    workflow.add_edge("research_agent", "script_agent")
    workflow.add_edge("script_agent", "shots_agent")
    workflow.add_edge("shots_agent", "images_agent")
    workflow.add_edge("images_agent", "voice_agent")
    workflow.add_edge("voice_agent", "video_agent")
    workflow.add_edge("video_agent", "seo_agent")
    workflow.add_edge("seo_agent", "upload_agent")
    workflow.add_edge("upload_agent", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("video_graph_created")
    
    return app


# Visualization helper
def visualize_graph():
    """Generate visual representation of the graph"""
    try:
        app = create_video_graph()
        graph_image = app.get_graph().draw_mermaid_png()
        
        with open("workflow_diagram.png", "wb") as f:
            f.write(graph_image)
        
        print("✓ Workflow diagram saved as workflow_diagram.png")
        
    except Exception as e:
        print(f"✗ Could not generate diagram: {e}")
        print("Install graphviz: pip install graphviz")


if __name__ == "__main__":
    # Generate workflow diagram
    visualize_graph()
