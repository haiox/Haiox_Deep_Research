import asyncio
import pytest
from agents.risk_agent import risk_node, rule_based_risk_fallback
from agents.state import AgentState


def test_rule_based_risk_fallback():
    """Verify deterministic risk audit fallback computes score, centralization, and flags."""
    sample_content = """
    # Dawn Internet DePIN Protocol
    Operating decentralized wireless mesh networks.
    Node reward distributions are routed via our centralized telemetry coordinator.
    Contract upgrades are managed by team multi-sig without on-chain timelock.
    Operators run hardware on residential lines.
    Security audit conducted by CertiK.
    """
    tokenomics_context = {"inflation_risk_score": 65}
    result = rule_based_risk_fallback(sample_content, tokenomics_context)

    assert "composite_risk_score" in result
    assert isinstance(result["composite_risk_score"], int)
    assert 1 <= result["composite_risk_score"] <= 100
    assert "risk_tier" in result
    assert "centralization_vectors" in result
    assert len(result["centralization_vectors"]) > 0
    assert "admin_key_custody" in result
    assert "technical_risks" in result
    assert "regulatory_risks" in result
    assert "security_audit_status" in result
    assert "Audited" in result["security_audit_status"]


@pytest.mark.asyncio
async def test_risk_node_state_execution():
    """Verify risk_node correctly updates AgentState with forensic risk audit."""
    mock_state: AgentState = {
        "target_url": "https://dawninternet.com",
        "project_id": 1,
        "evidence_id": "mock_ev_risk",
        "content_sha256": "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
        "clean_markdown": "# DAWN Protocol\nCentralized coordinator manages node telemetry.\nUnverified admin keys.",
        "evidence_artifact": None,
        "structured_findings": {
            "architecture": {"consensus_mechanism": "Solana"},
            "tokenomics": {"token_symbol": "DAWN", "inflation_risk_score": 50}
        },
        "verification_result": None,
        "current_step": "tokenomics_done",
        "errors": []
    }

    result = await risk_node(mock_state)

    assert result["current_step"] == "risk_done"
    assert "structured_findings" in result
    findings = result["structured_findings"]
    assert "architecture" in findings
    assert "tokenomics" in findings
    assert "risk" in findings
    
    risk_data = findings["risk"]
    assert "composite_risk_score" in risk_data
    assert "risk_tier" in risk_data
    assert "centralization_vectors" in risk_data
    assert "admin_key_custody" in risk_data
