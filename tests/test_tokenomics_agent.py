import asyncio
import pytest
from agents.tokenomics_agent import tokenomics_node, rule_based_tokenomics_fallback
from agents.state import AgentState


def test_rule_based_tokenomics_fallback():
    """Verify deterministic tokenomics fallback parses supply, vesting, and risks."""
    sample_content = """
    # Grass Protocol Economics
    Token Symbol: $GRASS
    Total Supply: 1,000,000,000 GRASS tokens.
    Community node rewards account for 55% of the total allocation.
    Includes a 12-month linear vesting duration with a 3-month cliff period.
    Tokens are used for DAO governance and node telemetry staking slashing.
    Beware of multi-tiered referral points prior to Token Generation Event (TGE).
    """
    result = rule_based_tokenomics_fallback(sample_content)

    assert result["token_symbol"] == "GRASS"
    assert "1,000,000,000" in result["total_supply"]
    assert "emission_model" in result
    assert "vesting_and_distribution" in result
    assert "cliff_period" in result["vesting_and_distribution"]
    assert "inflation_risk_score" in result
    assert isinstance(result["inflation_risk_score"], int)
    assert len(result["economic_red_flags"]) > 0
    assert "sustainability_verdict" in result


@pytest.mark.asyncio
async def test_tokenomics_node_state_execution():
    """Verify tokenomics_node processes AgentState correctly and updates structured_findings."""
    mock_state: AgentState = {
        "target_url": "https://teneo.pro",
        "project_id": 1,
        "evidence_id": "mock_ev_tokenomics",
        "content_sha256": "1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        "clean_markdown": "# Teneo Protocol\nToken Ticker: $TENEO\nTotal Supply: 500 Million.\nStaking yield for compute nodes with referral points.",
        "evidence_artifact": None,
        "structured_findings": {
            "architecture": {
                "consensus_mechanism": "Solana Sealevel Runtime",
                "hardware_requirements": {"cpu": "2 Core", "ram": "4GB"}
            }
        },
        "verification_result": None,
        "current_step": "architecture_done",
        "errors": []
    }

    result = await tokenomics_node(mock_state)

    assert result["current_step"] == "tokenomics_done"
    assert "structured_findings" in result
    assert "tokenomics" in result["structured_findings"]
    # Preserve architecture findings from previous step
    assert "architecture" in result["structured_findings"]
    
    tokenomics = result["structured_findings"]["tokenomics"]
    assert "token_symbol" in tokenomics
    assert "total_supply" in tokenomics
    assert "vesting_and_distribution" in tokenomics
    assert "inflation_risk_score" in tokenomics
    assert "economic_red_flags" in tokenomics
