import asyncio
import pytest
from agents.architecture_agent import architecture_node, rule_based_architecture_fallback
from agents.graph import app as depin_agent
from agents.state import AgentState


def test_rule_based_architecture_fallback():
    """Verify deterministic rule-based architectural parsing without LLM."""
    mock_content = """
    # Grass DePIN Network
    Decentralized network aggregating residential bandwidth.
    Runs on Solana blockchain with smart contract settlement.
    Nodes can run as lightweight browser extension or Docker desktop node.
    Requires minimum 4GB RAM, standard 2-core CPU, and residential IP.
    Check our open-source client at https://github.com/grass-org/node-client
    """
    result = rule_based_architecture_fallback(mock_content)

    assert "consensus_mechanism" in result
    assert "Solana" in result["consensus_mechanism"]
    assert "hardware_requirements" in result
    assert "claims_vs_reality" in result
    assert len(result["claims_vs_reality"]) > 0
    assert "github_verifications" in result
    assert len(result["github_verifications"]) > 0
    assert result["github_verifications"][0]["repo"] == "grass-org/node-client"
    assert "architectural_bottlenecks" in result


@pytest.mark.asyncio
async def test_architecture_node_state_execution():
    """Verify architecture_node processes AgentState correctly."""
    mock_state: AgentState = {
        "target_url": "https://example-depin.network",
        "project_id": 1,
        "evidence_id": "mock_ev_123",
        "content_sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "clean_markdown": "# Example Protocol\nHigh throughput PoS chain with validator nodes.\nhttps://github.com/example/core",
        "evidence_artifact": None,
        "structured_findings": {},
        "verification_result": None,
        "current_step": "evidence_persisted",
        "errors": []
    }

    result = await architecture_node(mock_state)

    assert result["current_step"] == "architecture_done"
    assert "structured_findings" in result
    assert "architecture" in result["structured_findings"]
    arch = result["structured_findings"]["architecture"]
    assert "consensus_mechanism" in arch
    assert "hardware_requirements" in arch
    assert "claims_vs_reality" in arch


@pytest.mark.asyncio
async def test_full_graph_with_architecture_agent():
    """Verify end-to-end LangGraph execution including the new Architecture Agent."""
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
    assert final_state["current_step"] in ("content_generated", "persisted_ok")
    assert "structured_findings" in final_state
    assert "architecture" in final_state["structured_findings"]
    assert "tokenomics" in final_state["structured_findings"]
    assert "risk" in final_state["structured_findings"]
