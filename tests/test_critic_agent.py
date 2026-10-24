import asyncio
import pytest
from agents.critic_agent import critic_node, rule_based_critic_fallback
from agents.state import AgentState
from agents.graph import app as depin_agent


def test_rule_based_critic_fallback():
    """Verify adversarial critic strikes out unsubstantiated claims and verifies evidence."""
    mock_content = """
    # Teneo DePIN Protocol
    Operating decentralized node telemetry.
    Client download available for desktop.
    Token $TENEO with high referral points.
    Single-Key owner controls smart contracts.
    """
    arch = {
        "claims_vs_reality": [
            {"whitepaper_claim": "100,000 TPS instant settlement", "code_backed": False},
            {"whitepaper_claim": "Client desktop node binary", "code_backed": True}
        ]
    }
    tokenomics = {"token_symbol": "TENEO", "inflation_risk_score": 75}
    risk = {"admin_key_custody": "High Admin Key Exposure (Single-Key Owner)"}

    result = rule_based_critic_fallback(mock_content, arch, tokenomics, risk)

    assert "zero_hallucination_score" in result
    assert isinstance(result["zero_hallucination_score"], int)
    assert "unsubstantiated_claims_struck" in result
    assert len(result["unsubstantiated_claims_struck"]) >= 2
    assert "verified_ground_truth" in result
    assert len(result["verified_ground_truth"]) >= 1
    assert "cross_examination_summary" in result


@pytest.mark.asyncio
async def test_critic_node_state_execution():
    """Verify critic_node updates AgentState with adversarial cross-examination."""
    mock_state: AgentState = {
        "target_url": "https://teneo.pro",
        "project_id": 1,
        "evidence_id": "mock_ev_critic",
        "content_sha256": "11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        "clean_markdown": "# Teneo Network\nDecentralized node network with desktop node.",
        "evidence_artifact": None,
        "structured_findings": {
            "architecture": {"consensus_mechanism": "Solana"},
            "tokenomics": {"token_symbol": "TENEO", "inflation_risk_score": 40},
            "risk": {"composite_risk_score": 45}
        },
        "verification_result": None,
        "current_step": "risk_done",
        "errors": []
    }

    result = await critic_node(mock_state)

    assert result["current_step"] == "critic_done"
    assert "structured_findings" in result
    findings = result["structured_findings"]
    assert "critic" in findings
    critic_data = findings["critic"]
    assert "zero_hallucination_score" in critic_data
    assert "unsubstantiated_claims_struck" in critic_data


@pytest.mark.asyncio
async def test_full_graph_with_critic_node():
    """Verify full graph execution with the integrated Adversarial Critic node."""
    initial_state = {
        "target_url": "https://example.com",
        "project_id": 1,
        "evidence_id": None,
        "content_sha256": None,
        "clean_markdown": None,
        "evidence_artifact": None,
        "structured_findings": {},
        "verification_result": None,
        "current_step": "init",
        "errors": []
    }

    final_state = await depin_agent.ainvoke(initial_state)

    assert len(final_state.get("errors", [])) == 0
    assert "structured_findings" in final_state
    findings = final_state["structured_findings"]
    assert "architecture" in findings
    assert "tokenomics" in findings
    assert "risk" in findings
    assert "critic" in findings
