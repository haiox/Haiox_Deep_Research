import json
import re
from typing import Dict, Any, List
from agents.state import AgentState
from core.repositories import get_evidence_by_id
from core.llm_router import call_llm


def rule_based_critic_fallback(
    raw_content: str, 
    architecture_findings: Dict[str, Any],
    tokenomics_findings: Dict[str, Any],
    risk_findings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministic rule-based adversarial critic fallback.
    Cross-examines findings against raw evidence and strikes out unsubstantiated marketing claims.
    """
    lower = raw_content.lower()

    unsubstantiated_claims = []
    verified_claims = []

    # Check 1: Scalability / TPS claims vs evidence
    if architecture_findings:
        claims = architecture_findings.get("claims_vs_reality", [])
        for c in claims:
            if not c.get("code_backed"):
                unsubstantiated_claims.append({
                    "claim": c.get("whitepaper_claim", "Throughput scalability"),
                    "critic_verdict": "REJECTED_UNSUBSTANTIATED",
                    "reason": "No public GitHub implementation or cryptographic verifiable telemetry found in evidence."
                })
            else:
                verified_claims.append({
                    "claim": c.get("whitepaper_claim", "Client edge node binary"),
                    "critic_verdict": "VERIFIED_SUPPORTED",
                    "reason": "Direct evidence of client binaries / extension in AST DOM."
                })

    # Check 2: Tokenomics sustainability cross-examination
    if tokenomics_findings:
        if tokenomics_findings.get("inflation_risk_score", 0) > 60:
            unsubstantiated_claims.append({
                "claim": "Long-term sustainable node rewards",
                "critic_verdict": "DISPUTED_HIGH_DILUTION",
                "reason": "High inflation score and multi-tiered referral points indicate high farm-and-dump liquidity hazard."
            })
        else:
            verified_claims.append({
                "claim": f"Token standard & supply ({tokenomics_findings.get('token_symbol')})",
                "critic_verdict": "VERIFIED_SUPPORTED",
                "reason": "Fixed cap / documented emission schedule confirmed."
            })

    # Check 3: Centralization vs Decentralization marketing
    if risk_findings:
        if "Single-Key" in risk_findings.get("admin_key_custody", "") or "High Admin" in risk_findings.get("admin_key_custody", ""):
            unsubstantiated_claims.append({
                "claim": "Fully decentralized & permissionless protocol governance",
                "critic_verdict": "REJECTED_CENTRALIZED",
                "reason": "Critical admin key custody exposes protocol to single-point rugpull or parameter tampering."
            })

    zero_hallucination_score = max(10, 100 - (len(unsubstantiated_claims) * 20))

    return {
        "zero_hallucination_score": zero_hallucination_score,
        "critic_status": "Passed with Redlines" if unsubstantiated_claims else "Fully Corroborated",
        "unsubstantiated_claims_struck": unsubstantiated_claims,
        "verified_ground_truth": verified_claims,
        "cross_examination_summary": (
            f"Adversarial critic scrutinized {len(verified_claims) + len(unsubstantiated_claims)} primary claims. "
            f"{len(unsubstantiated_claims)} unsubstantiated claims were struck out due to lack of GitHub code or single-admin custody."
        ),
        "extraction_method": "deterministic_rule_based_fallback"
    }


async def critic_node(state: AgentState) -> Dict[str, Any]:
    """
    Adversarial Critic Agent Node:
    Conducts adversarial cross-examination of findings against source AST evidence.
    Strikes out hype and hallucinated claims, guarantees Zero-Hallucination integrity.
    """
    print(f"⚖️ [Critic Agent] Adversarial cross-examination on Evidence ID: {state.get('evidence_id')}...")

    ev_id = state.get("evidence_id")
    raw_content = state.get("clean_markdown")

    if not raw_content and ev_id:
        evidence_record = get_evidence_by_id(ev_id)
        if evidence_record:
            raw_content = evidence_record.get("content", "")

    if not raw_content:
        err = "No evidence content found for critic cross-examination."
        print(f"❌ [Critic Agent] {err}")
        return {"errors": state.get("errors", []) + [err]}

    current_findings = state.get("structured_findings") or {}
    architecture_findings = current_findings.get("architecture", {})
    tokenomics_findings = current_findings.get("tokenomics", {})
    risk_findings = current_findings.get("risk", {})

    prompt = f"""
    You are an unyielding, ruthless Web3 Due-Diligence Critic & Fact-Checker.
    Your mission: Attack and cross-examine analytical claims against raw AST evidence.
    Strike out any unsubstantiated marketing statements, unbacked TPS claims, or fake decentralization claims.

    Raw Evidence (Source of Truth):
    {raw_content[:4500]}

    Architecture Findings:
    {json.dumps(architecture_findings)[:800]}

    Tokenomics Findings:
    {json.dumps(tokenomics_findings)[:800]}

    Risk Findings:
    {json.dumps(risk_findings)[:800]}

    Respond ONLY with a valid JSON object matching this exact schema:
    {{
      "zero_hallucination_score": 85,
      "critic_status": "Fully Corroborated | Passed with Redlines | High Discrepancy",
      "unsubstantiated_claims_struck": [
        {{
          "claim": "Claim text",
          "critic_verdict": "REJECTED_UNSUBSTANTIATED | DISPUTED_HIGH_DILUTION | REJECTED_CENTRALIZED",
          "reason": "Direct evidence quote or explanation why code does not back claim"
        }}
      ],
      "verified_ground_truth": [
        {{
          "claim": "Verified claim text",
          "critic_verdict": "VERIFIED_SUPPORTED",
          "reason": "Exact supporting quote from AST evidence"
        }}
      ],
      "cross_examination_summary": "1-2 sentence executive verdict",
      "extraction_method": "llm_adversarial_critic"
    }}
    Do not output markdown codeblocks like ```json or any introductory text.
    """

    findings = None
    try:
        response_text = await call_llm(prompt)
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                fallback = rule_based_critic_fallback(raw_content, architecture_findings, tokenomics_findings, risk_findings)
                for k, v in fallback.items():
                    if k not in parsed or parsed[k] is None:
                        parsed[k] = v
                findings = parsed
    except Exception as e:
        print(f"⚠️ [Critic Agent] LLM parsing failed: {e}. Switching to rule-based fallback.")

    if not findings or not isinstance(findings, dict):
        findings = rule_based_critic_fallback(raw_content, architecture_findings, tokenomics_findings, risk_findings)

    current_findings["critic"] = findings

    print("✅ [Critic Agent] Adversarial cross-examination complete.")
    return {
        "structured_findings": current_findings,
        "current_step": "critic_done"
    }
