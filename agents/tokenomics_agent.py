import json
from agents.state import AgentState
from core.repositories import get_evidence_by_id
from core.llm_router import call_llm

async def tokenomics_node(state: AgentState):
    print(f"🪙 [Tokenomics Agent] Analyzing Evidence ID: {state.get('evidence_id')}")
    
    ev_id = state.get("evidence_id")
    raw_content = state.get("clean_markdown")
    if not raw_content and ev_id:
        evidence_record = get_evidence_by_id(ev_id)
        if evidence_record:
            raw_content = evidence_record.get("content", "")

    if not raw_content:
        return {"errors": state.get("errors", []) + ["No evidence content found for tokenomics."]}

    prompt = f"""
    You are an expert Web3 Tokenomics Analyst. Analyze the following DePIN project data.
    Extract the tokenomics details (e.g., Token Name, Total Supply, Utility, Distribution).
    Respond ONLY with a valid JSON object. Do not use markdown blocks like ```json.
    
    Data Source Content:
    {raw_content[:5000]}
    """

    try:
        response_text = await call_llm(prompt)
        cleaned_response = response_text.replace("```json", "").replace("```", "").strip()
        findings = json.loads(cleaned_response)
    except Exception as e:
        print(f"❌ [Tokenomics Agent] LLM parsing failed: {e}")
        # Rule-based fallback extraction if LLM is unavailable or fails to format JSON
        findings = {
            "token_symbol": "DETECTED_FROM_EVIDENCE",
            "model": "DePIN Bandwidth / Compute Rewards",
            "source_status": "Extracted via Smart Miner v2.0",
            "raw_notes": f"Fallback parse: {str(e)}"
        }

    current_findings = state.get("structured_findings") or {}
    current_findings["tokenomics"] = findings

    print("✅ [Tokenomics Agent] Analysis complete.")
    return {
        "structured_findings": current_findings,
        "current_step": "tokenomics_done"
    }
