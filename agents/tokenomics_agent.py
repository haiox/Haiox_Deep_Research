import json
import re
from typing import Dict, Any, List
from agents.state import AgentState
from core.repositories import get_evidence_by_id
from core.llm_router import call_llm


def rule_based_tokenomics_fallback(raw_content: str) -> Dict[str, Any]:
    """
    Deterministic rule-based tokenomics analysis fallback.
    Extracts token symbols, supply figures, vesting cues, emission models,
    and inflation/sustainability red flags directly from raw AST markdown.
    """
    lower = raw_content.lower()

    # 1. Detect Token Symbol or Name
    token_symbol = "DETECTED_UTILITY_TOKEN"
    symbol_match = re.search(r'\$([A-Z0-9]{2,10})|ticker:\s*([A-Z0-9]{2,10})|symbol:\s*([A-Z0-9]{2,10})', raw_content, re.IGNORECASE)
    if symbol_match:
        token_symbol = [g for g in symbol_match.groups() if g][0].upper()
    elif "grass" in lower:
        token_symbol = "GRASS"
    elif "teneo" in lower:
        token_symbol = "TENEO"
    elif "bless" in lower:
        token_symbol = "BLESS"
    elif "dawn" in lower:
        token_symbol = "DAWN"

    # 2. Total Supply Detection
    total_supply = "Not fixed / Dynamic minting"
    supply_match = re.search(r'(total\s*supply|max\s*supply)[:\s]+([0-9,\.]+\s*(?:billion|million|b|m)?)', raw_content, re.IGNORECASE)
    if supply_match:
        total_supply = supply_match.group(2).strip()

    # 3. Model & Emission Schedule
    emission_type = "Dynamic DePIN Node Rewards"
    if "burn and mint" in lower or "bme" in lower:
        emission_type = "Burn-and-Mint Equilibrium (BME)"
    elif "halving" in lower:
        emission_type = "Halving / Deflationary Schedule"
    elif "staking yield" in lower or "apy" in lower:
        emission_type = "Staking & Compute Reward Pool"

    # 4. Vesting & Lockup Analysis
    vesting_schedule = {
        "cliff_period": "3-6 Months typical",
        "vesting_duration": "12-36 Months linear",
        "investor_allocation_pct": "Estimated 15% - 25%",
        "community_node_pct": "Estimated 40% - 60%"
    }
    if "tge" in lower:
        vesting_schedule["tge_unlock"] = "Initial unlock at Token Generation Event"

    # 5. Economic Sustainability & Red Flags (Pump & Dump / Ponzinomics Screening)
    economic_risks: List[str] = []
    if "referral" in lower or "points" in lower or "tier" in lower:
        economic_risks.append("Heavy reliance on multi-tiered point/referral incentives before TGE.")
    if "infinite" in lower or "unlimited supply" in lower or "no max supply" in lower:
        economic_risks.append("Uncapped maximum token supply creates severe long-term inflationary sell pressure.")
    if "no lock" in lower or "instant unlock" in lower:
        economic_risks.append("High risk of team/investor market dumping on TGE liquidity.")
    if not economic_risks:
        economic_risks.append("Node reward emission rate dependent on sustained buyer demand for compute/bandwidth.")

    # 6. Token Utility Sinks
    utilities = []
    if "governance" in lower:
        utilities.append("DAO Governance Voting")
    if "node" in lower or "bandwidth" in lower or "compute" in lower:
        utilities.append("Node Operator Staking & Telemetry Slashing")
    if "fee" in lower or "discount" in lower:
        utilities.append("Protocol Service Access Fees")
    if not utilities:
        utilities = ["Bandwidth/Compute Exchange Token", "Ecosystem Participation Reward"]

    return {
        "token_symbol": token_symbol,
        "total_supply": total_supply,
        "emission_model": emission_type,
        "token_utility_sinks": utilities,
        "vesting_and_distribution": vesting_schedule,
        "inflation_risk_score": 65 if len(economic_risks) > 1 else 35,  # 1-100 scale
        "economic_red_flags": economic_risks,
        "sustainability_verdict": "Medium-Term Speculative" if len(economic_risks) > 1 else "Sustainable Utility Driven",
        "extraction_method": "deterministic_rule_based_fallback"
    }


async def tokenomics_node(state: AgentState) -> Dict[str, Any]:
    """
    Deep Tokenomics Agent Node:
    Conducts deep financial and tokenomics due diligence.
    Examines emission formulas, vesting cliffs, inflationary sell-pressure,
    points-to-token transition mechanisms, and ponzinomics/dumping red flags.
    """
    print(f"🪙 [Tokenomics Agent] Deep auditing Evidence ID: {state.get('evidence_id')}...")

    ev_id = state.get("evidence_id")
    raw_content = state.get("clean_markdown")

    if not raw_content and ev_id:
        evidence_record = get_evidence_by_id(ev_id)
        if evidence_record:
            raw_content = evidence_record.get("content", "")

    if not raw_content:
        err = "No evidence content found for tokenomics analysis."
        print(f"❌ [Tokenomics Agent] {err}")
        return {"errors": state.get("errors", []) + [err]}

    prompt = f"""
    You are an elite Web3 Tokenomics & Crypto-Economic Auditor. 
    Analyze the following DePIN/Web3 project evidence with deep financial scrutiny.
    
    Extract and critically evaluate:
    1. Token Identity (Symbol, Ticker, Standard).
    2. Total / Max Supply & Circulating Supply mechanics.
    3. Emission Model (Burn-and-mint, staking yield, linear inflation, halving).
    4. Real Utility Sinks (Where is natural buy pressure coming from vs speculative farming?).
    5. Vesting & Distribution Schedule (Team, VCs, Community nodes, Cliff periods).
    6. Ponzinomics & Dump Risk Screening (Evaluate referral systems, uncapped minting, aggressive farmer dumping).
    7. Overall Economic Sustainability Verdict.

    Data Source Content (First 5000 chars):
    {raw_content[:5000]}

    Respond ONLY with a valid JSON object matching this exact schema:
    {{
      "token_symbol": "string",
      "total_supply": "string",
      "emission_model": "string",
      "token_utility_sinks": ["Utility 1", "Utility 2"],
      "vesting_and_distribution": {{
        "cliff_period": "string",
        "vesting_duration": "string",
        "investor_allocation_pct": "string",
        "community_node_pct": "string"
      }},
      "inflation_risk_score": 45,
      "economic_red_flags": [
        "Identified economic/dump risk 1",
        "Identified economic/dump risk 2"
      ],
      "sustainability_verdict": "Sustainable Utility Driven | Speculative Farm | High Risk Inflationary",
      "extraction_method": "llm_deep_analysis"
    }}
    Do not write any markdown codeblocks like ```json or introductory text.
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
                fallback = rule_based_tokenomics_fallback(raw_content)
                for k, v in fallback.items():
                    if k not in parsed or not parsed[k]:
                        parsed[k] = v
                findings = parsed
    except Exception as e:
        print(f"⚠️ [Tokenomics Agent] LLM parsing failed: {e}. Switching to rule-based fallback.")

    if not findings or not isinstance(findings, dict):
        findings = rule_based_tokenomics_fallback(raw_content)

    current_findings = state.get("structured_findings") or {}
    current_findings["tokenomics"] = findings

    print("✅ [Tokenomics Agent] Deep tokenomics audit successfully compiled.")
    return {
        "structured_findings": current_findings,
        "current_step": "tokenomics_done"
    }
