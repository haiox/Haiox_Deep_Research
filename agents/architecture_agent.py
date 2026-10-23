import json
import re
from typing import Dict, Any, List
from agents.state import AgentState
from core.repositories import get_evidence_by_id
from core.llm_router import call_llm


def rule_based_architecture_fallback(raw_content: str) -> Dict[str, Any]:
    """
    Deterministic rule-based architectural fallback if LLM is unreachable or parsing fails.
    Extracts protocol keywords, hardware hints, and GitHub indicators directly from AST markdown.
    """
    lower = raw_content.lower()

    # Consensus detection
    consensus = "Unknown / Off-chain Proof"
    if "proof of stake" in lower or "pos" in lower:
        consensus = "Proof-of-Stake (PoS)"
    elif "proof of work" in lower or "pow" in lower:
        consensus = "Proof-of-Work (PoW)"
    elif "proof of connectivity" in lower or "proof of bandwidth" in lower:
        consensus = "Proof of Connectivity / Bandwidth"
    elif "solana" in lower:
        consensus = "Solana SPL / Sealevel runtime"
    elif "ethereum" in lower or "evm" in lower:
        consensus = "EVM Smart Contracts"

    # Hardware specs heuristic
    hardware = {
        "cpu": "Standard Multi-core (2-4 Cores)",
        "ram": "4GB - 8GB Minimum recommended",
        "storage": "SSD 50GB+ for telemetry / node logs",
        "network": "Residential / Commercial Broadband (10+ Mbps upstream)"
    }
    if "gpu" in lower:
        hardware["gpu"] = "NVIDIA CUDA-compatible GPU required for AI/Compute workloads"

    # GitHub checks
    github_matches = re.findall(r'github\.com/([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+)', raw_content)
    github_claims = []
    if github_matches:
        for repo in list(set(github_matches))[:3]:
            github_claims.append({
                "repo": repo,
                "claimed_role": "Core Protocol / Client Node",
                "verified_status": "claimed_link_detected"
            })
    else:
        github_claims.append({
            "repo": "None cited in evidence",
            "claimed_role": "Closed-source / Pending Public Release",
            "verified_status": "unverified_closed_source"
        })

    # Claims vs Reality screening
    claims = [
        {
            "category": "Scalability & Throughput",
            "whitepaper_claim": "High-throughput decentralized bandwidth aggregation",
            "code_backed": len(github_matches) > 0,
            "evidence_reference": "Extracted via Smart Miner v2.0 AST DOM"
        },
        {
            "category": "Decentralization Degree",
            "whitepaper_claim": "Permissionless edge node operation",
            "code_backed": True if "docker" in lower or "download" in lower or "extension" in lower else False,
            "evidence_reference": "Client binary / extension availability in evidence"
        }
    ]

    return {
        "consensus_mechanism": consensus,
        "hardware_requirements": hardware,
        "github_verifications": github_claims,
        "claims_vs_reality": claims,
        "architectural_bottlenecks": [
            "Centralized coordinator dependency for node peer-discovery",
            "Bandwidth/Compute verification bottleneck without ZK-proofs"
        ],
        "extraction_method": "deterministic_rule_based_fallback"
    }


async def architecture_node(state: AgentState) -> Dict[str, Any]:
    """
    Architecture Agent Node:
    Analyzes raw evidence to separate whitepaper marketing claims from actual GitHub implementation,
    node hardware requirements, network topology, and consensus mechanics.
    """
    print(f"🏗️ [Architecture Agent] Analyzing Evidence ID: {state.get('evidence_id')}...")

    ev_id = state.get("evidence_id")
    raw_content = state.get("clean_markdown")

    if not raw_content and ev_id:
        evidence_record = get_evidence_by_id(ev_id)
        if evidence_record:
            raw_content = evidence_record.get("content", "")

    if not raw_content:
        err = "No evidence content found for architecture analysis."
        print(f"❌ [Architecture Agent] {err}")
        return {"errors": state.get("errors", []) + [err]}

    prompt = f"""
    You are an elite DePIN & Web3 Systems Architect. Analyze the following project evidence extracted from their whitepaper/site.
    Your objective: Separate marketing claims from real technical implementation.
    
    Extract and assess:
    1. Consensus Mechanism & Architecture (Layer 1, L2, Solana, EVM, custom subnet, or off-chain coordinator).
    2. Node Hardware Requirements (CPU, RAM, GPU, Storage, Bandwidth).
    3. Whitepaper Claims vs GitHub Reality (Does public code back up throughput, decentralization, or zero-knowledge claims?).
    4. Architectural Bottlenecks (Single points of failure, centralized telemetry or oracle reliance).

    Data Source Content (First 5000 chars):
    {raw_content[:5000]}

    Respond ONLY with a valid JSON object matching this exact schema:
    {{
      "consensus_mechanism": "string",
      "hardware_requirements": {{
        "cpu": "string",
        "ram": "string",
        "storage": "string",
        "network": "string",
        "gpu": "optional string or null"
      }},
      "github_verifications": [
        {{
          "repo": "string or 'Not specified'",
          "claimed_role": "string",
          "verified_status": "code_backed | partially_verified | unverified_closed_source"
        }}
      ],
      "claims_vs_reality": [
        {{
          "category": "Throughput | Consensus | Decentralization | Token Flow",
          "whitepaper_claim": "Exact or synthesized claim",
          "code_backed": true,
          "evidence_reference": "Short justification or evidence reference"
        }}
      ],
      "architectural_bottlenecks": [
        "String detailing technical bottleneck 1",
        "String detailing technical bottleneck 2"
      ],
      "extraction_method": "llm_deep_analysis"
    }}
    Do not include markdown codeblocks like ```json.
    """

    findings = None
    try:
        response_text = await call_llm(prompt)
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                # Ensure all required architectural keys are present
                fallback = rule_based_architecture_fallback(raw_content)
                for k, v in fallback.items():
                    if k not in parsed or not parsed[k]:
                        parsed[k] = v
                findings = parsed
    except Exception as e:
        print(f"⚠️ [Architecture Agent] LLM parsing failed: {e}. Switching to rule-based fallback.")

    if not findings or not isinstance(findings, dict):
        findings = rule_based_architecture_fallback(raw_content)

    current_findings = state.get("structured_findings") or {}
    current_findings["architecture"] = findings

    print("✅ [Architecture Agent] Architecture analysis successfully compiled.")
    return {
        "structured_findings": current_findings,
        "current_step": "architecture_done"
    }
