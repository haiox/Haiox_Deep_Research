from agents.twitter_agent import twitter_factory_node
from langgraph.graph import StateGraph, END
from agents.persist_agent import persist_research_node
from agents.state import AgentState
from tools.smart_miner_adapter import fetch_miner_payload
from core.repositories import save_evidence

# Import agents connected to the language model
from agents.architecture_agent import architecture_node
from agents.tokenomics_agent import tokenomics_node
from agents.risk_agent import risk_node
from agents.verification_agent import verification_node
from agents.critic_agent import critic_node

# ==========================================
# Nodes
# ==========================================

async def extract_and_evidence_node(state: AgentState):
    print(f"🔄 [Graph] Step 1: Extraction & Evidence Persistence for {state['target_url']}")
    
    payload = await fetch_miner_payload(state["target_url"])
    
    if not payload.get("success"):
        errors = state.get("errors", [])
        errors.append(f"Smart Miner v2.0 extraction failed: {payload.get('error', 'UNKNOWN')}")
        return {"errors": errors, "current_step": "failed"}

    clean_markdown = payload.get("markdown") or payload.get("text", "")
    content_sha256 = payload.get("content_sha256", "")
    evidence_artifact = payload.get("evidence")

    p_id = state.get("project_id") or 1 
    ev_id = save_evidence(
        project_id=p_id, 
        source_url=state["target_url"], 
        raw_content=clean_markdown,
        sha256=content_sha256,
        metadata={
            "routing": payload.get("routing"),
            "tables": payload.get("tables"),
            "headings": payload.get("headings"),
            "metadata": payload.get("metadata"),
            "evidence": evidence_artifact
        }
    )

    if not ev_id:
        errors = state.get("errors", [])
        errors.append("Evidence persistence failed in both PostgreSQL and SQLite fallback.")
        return {"errors": errors, "current_step": "failed"}

    print(f"✅ [Graph] Evidence injected into State -> ID: {ev_id} | SHA-256: {content_sha256[:16]}...")
    return {
        "evidence_id": ev_id,
        "content_sha256": content_sha256,
        "clean_markdown": clean_markdown,
        "evidence_artifact": evidence_artifact,
        "current_step": "evidence_persisted"
    }

# ==========================================
# Graph Construction
# ==========================================

workflow = StateGraph(AgentState)

workflow.add_node("extract_evidence", extract_and_evidence_node)
workflow.add_node("architecture", architecture_node)
workflow.add_node("tokenomics", tokenomics_node)
workflow.add_node("risk", risk_node)
workflow.add_node("critic", critic_node)
workflow.add_node("verification", verification_node)
workflow.add_node("persist_research", persist_research_node)
workflow.add_node("twitter_factory", twitter_factory_node)

workflow.set_entry_point("extract_evidence")
workflow.add_edge("extract_evidence", "architecture")
workflow.add_edge("architecture", "tokenomics")
workflow.add_edge("tokenomics", "risk")
workflow.add_edge("risk", "critic")
workflow.add_edge("critic", "verification")
workflow.add_edge("verification", "persist_research")
workflow.add_edge("persist_research", "twitter_factory")
workflow.add_edge("twitter_factory", END)

app = workflow.compile()
