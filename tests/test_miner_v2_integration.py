import asyncio
import os
import pytest
from pathlib import Path

from tools.smart_miner_adapter import fetch_miner_payload, fetch_raw_data_from_miner
from core.repositories import save_evidence, get_evidence_by_id, save_research_report, SQLITE_DB_PATH
from agents.graph import app as depin_agent


@pytest.mark.asyncio
async def test_smart_miner_adapter_extraction():
    """Verify Smart Miner v2.0 extracts clean markdown and SHA-256 evidence."""
    url = "https://example.com"
    payload = await fetch_miner_payload(url)
    
    assert payload["success"] is True
    assert len(payload["markdown"]) > 0
    assert "content_sha256" in payload
    assert len(payload["content_sha256"]) == 64  # Valid SHA-256 hex digest
    assert payload["routing"]["strategy"] in ("static", "dynamic", "metadata")
    assert payload["status"] == "ok"


@pytest.mark.asyncio
async def test_smart_miner_backward_compatibility():
    """Verify legacy fetch_raw_data_from_miner returns markdown string."""
    url = "https://example.com"
    raw_markdown = await fetch_raw_data_from_miner(url)
    assert isinstance(raw_markdown, str)
    assert len(raw_markdown) > 0


def test_sqlite_repository_fallback():
    """Verify repository falls back to local SQLite when Postgres is absent."""
    test_url = "https://test-depin.io"
    test_content = "# Test DePIN Architecture\n\nHigh speed telemetry node."
    test_sha256 = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    ev_id = save_evidence(
        project_id=99,
        source_url=test_url,
        raw_content=test_content,
        sha256=test_sha256,
        metadata={"test": True}
    )
    assert ev_id is not None
    assert isinstance(ev_id, int)

    # Fetch back
    record = get_evidence_by_id(ev_id)
    assert record is not None
    assert record["source_url"] == test_url
    assert record["content"] == test_content
    assert record["content_sha256"] == test_sha256

    # Save research report
    report_id = save_research_report(
        evidence_id=ev_id,
        tokenomics={"token": "TEST", "supply": 1000},
        risk={"score": 2.5},
        verification={"status": "verified"}
    )
    assert report_id is not None
    assert isinstance(report_id, int)


@pytest.mark.asyncio
async def test_full_graph_workflow_end_to_end():
    """Verify complete LangGraph pipeline with Smart Miner 2.0 evidence."""
    target_url = "https://example.com"
    initial_state = {
        "target_url": target_url,
        "project_id": 1,
        "evidence_id": None,
        "content_sha256": None,
        "clean_markdown": None,
        "evidence_artifact": None,
        "structured_findings": None,
        "verification_result": None,
        "current_step": "init",
        "errors": []
    }

    result = await depin_agent.ainvoke(initial_state)

    assert result["current_step"] == "content_generated"
    assert result["evidence_id"] is not None
    assert len(result["content_sha256"]) == 64
    assert result["structured_findings"] is not None
    assert "tokenomics" in result["structured_findings"]
    assert "risk" in result["structured_findings"]
    assert result["verification_result"] is not None
    assert len(result["errors"]) == 0

    # Verify generated output files
    report_file = Path("output_threads/example_com_GitHub_Report.md")
    thread_file = Path("output_threads/example_com_thread.txt")
    assert report_file.exists()
    assert thread_file.exists()
    
    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Digital Evidence SHA-256" in content
        assert result["content_sha256"] in content
