import json
import re
from typing import Dict, Any, List
from agents.state import AgentState
from core.repositories import get_evidence_by_id
from core.llm_router import call_llm


def rule_based_risk_fallback(raw_content: str, tokenomics_findings: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Deterministic rule-based risk and centralization audit fallback.
    Audits admin key custody, smart contract upgradability, ISP regulatory exposure,
    single points of failure (SPOF), and produces a structured 1-100 risk score.
    """
    lower = raw_content.lower()

    # 1. Centralization Vectors & Admin Key Analysis
    centralization_vectors = []
    if "multisig" in lower or "multi-sig" in lower:
        centralization_vectors.append("Governance governed by multi-sig custody (threshold signature scheme).")
    else:
        centralization_vectors.append("Unverified single-admin control over smart contract upgrades or parameters.")

    if "coordinator" in lower or "centralized" in lower or "gateway" in lower:
        centralization_vectors.append("Centralized coordinator dependency for node routing and verification.")
    else:
        centralization_vectors.append("Closed-source backend telemetry server controlling reward distribution.")

    # 2. Smart Contract & Technical Risks
    technical_risks = [
        "Network telemetry verification relies heavily on off-chain calculation rather than ZK-proofs.",
        "ISP / Residential proxy blacklisting hazard for node operators."
    ]
    if "solana" in lower:
        technical_risks.append("Dependency on Solana network congestion and transaction finality spikes.")
    elif "ethereum" in lower or "evm" in lower:
        technical_risks.append("EVM gas cost bottlenecks during high-frequency micro-reward distributions.")

    # 3. Regulatory & Node Operator Legal Exposure
    regulatory_risks = [
        "Risk of residential IP operators inadvertently violating ISP Terms of Service (ToS).",
        "Potential data privacy / compliance exposure (GDPR / CCPA) from unencrypted network traffic."
    ]

    # 4. Red Flag Screener
    red_flags = []
    if "anonymous team" in lower or "undisclosed team" in lower:
        red_flags.append("Anonymous / Undisclosed core development team.")
    if "points" in lower and "no token" in lower:
        red_flags.append("Unregulated points system with indefinite TGE delay risk.")
    if not red_flags:
        red_flags.append("Early-stage protocol without third-party institutional security audit.")

    # 5. Composite Risk Score Calculation (1 to 100 Scale)
    # Higher score = Greater risk
    base_score = 40
    if len(centralization_vectors) >= 2:
        base_score += 15
    if len(red_flags) >= 2:
        base_score += 20
    if tokenomics_findings and tokenomics_findings.get("inflation_risk_score", 0) > 60:
        base_score += 10

    composite_score = min(max(base_score, 10), 95)

    risk_tier = "Moderate Risk"
    if composite_score >= 70:
        risk_tier = "High Risk / Speculative"
    elif composite_score <= 30:
        risk_tier = "Low / Institutional Grade"

    return {
        "composite_risk_score": composite_score,
        "risk_tier": risk_tier,
        "centralization_vectors": centralization_vectors,
        "admin_key_custody": "Semi-Centralized Team Multi-Sig" if "multisig" in lower else "High Admin Key Exposure",
        "technical_risks": technical_risks,
        "regulatory_risks": regulatory_risks,
        "red_flags": red_flags,
        "security_audit_status": "Audited" if "audit" in lower or "certik" in lower or "halborn" in lower else "Pending Public Security Audit",
        "extraction_method": "deterministic_rule_based_fallback"
    }


async def risk_node(state: AgentState) -> Dict[str, Any]:
    """
    Risk & Centralization Audit Node:
    Conducts forensic security auditing on DePIN/Web3 protocols.
    Assesses admin key privileges, single points of failure (SPOF),
    ISP regulatory exposure, and issues an uncompromising 1-100 risk score.
    """
    print(f"⚠️ [Risk Agent] Forensic risk auditing on Evidence ID: {state.get('evidence_id')}...")

    ev_id = state.get("evidence_id")
    raw_content = state.get("clean_markdown")

    if not raw_content and ev_id:
        evidence_record = get_evidence_by_id(ev_id)
        if evidence_record:
            raw_content = evidence_record.get("content", "")

    if not raw_content:
        err = "No evidence content found for risk analysis."
        print(f"❌ [Risk Agent] {err}")
        return {"errors": state.get("errors", []) + [err]}

    current_findings = state.get("structured_findings") or {}
    tokenomics_findings = current_findings.get("tokenomics", {})
    architecture_findings = current_findings.get("architecture", {})

    prompt = f"""
    You are an elite Web3 Security, Forensic Risk & Smart Contract Auditor.
    Audit the following protocol evidence with strict objectivity and zero marketing bias.

    Extract and critically evaluate:
    1. Centralization Vectors & Admin Key Privileges (Can the team rug, upgrade contracts without timelock, or freeze node rewards?).
    2. Single Points of Failure / SPOF (Centralized gateways, closed-source telemetries, oracle reliance).
    3. Technical Vulnerabilities & Network Congestion bottlenecks.
    4. Regulatory & Node Operator Legal Liabilities (ISP TOS violations, residential proxy abuse).
    5. Red Flags & Team Anonymity.
    6. Overall Composite Risk Score (Integer from 1 to 100, where 100 is critical danger/rugpull and 1 is battle-tested/Ethereum L1 grade).
    7. Risk Tier (Low / Institutional Grade | Moderate Risk | High Risk / Speculative).

    Architecture Context:
    {json.dumps(architecture_findings)[:1000]}

    Tokenomics Context:
    {json.dumps(tokenomics_findings)[:1000]}

    Data Source Evidence (First 5000 chars):
    {raw_content[:5000]}

    Respond ONLY with a valid JSON object matching this exact schema:
    {{
      "composite_risk_score": 55,
      "risk_tier": "Moderate Risk",
      "centralization_vectors": [
        "Identified centralization point 1",
        "Identified centralization point 2"
      ],
      "admin_key_custody": "Team Multi-Sig | Timelock DAO | Single-Key Owner",
      "technical_risks": [
        "Technical hazard 1",
        "Technical hazard 2"
      ],
      "regulatory_risks": [
        "Regulatory/ISP legal hazard 1"
      ],
      "red_flags": [
        "Red flag 1"
      ],
      "security_audit_status": "Audited by [Firm] | Pending Public Security Audit",
      "extraction_method": "llm_deep_analysis"
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
                # Ensure all required keys exist using fallback template
                fallback = rule_based_risk_fallback(raw_content, tokenomics_findings)
                for k, v in fallback.items():
                    if k not in parsed or parsed[k] is None:
                        parsed[k] = v
                findings = parsed
    except Exception as e:
        print(f"⚠️ [Risk Agent] LLM parsing failed: {e}. Switching to rule-based fallback.")

    if not findings or not isinstance(findings, dict):
        findings = rule_based_risk_fallback(raw_content, tokenomics_findings)

    current_findings["risk"] = findings

    print("✅ [Risk Agent] Forensic risk audit successfully compiled.")
    return {
        "structured_findings": current_findings,
        "current_step": "risk_done"
    }
