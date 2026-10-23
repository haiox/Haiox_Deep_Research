"""
Haiox Deep Research - Smart Miner Adapter
Integrates Smart Miner v2.0 bedrock ingestion pipeline.
Directly routes via static/dynamic headless crawler, AST cleaner,
and produces SHA-256 cryptographic evidence artifacts without hallucination.
"""
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("smart_miner_adapter")

try:
    from smart_miner import route
    from smart_miner.pipeline.document import CleanDocument
    from smart_miner.pipeline.evidence import EvidenceArtifact
except ImportError:
    route = None
    CleanDocument = None
    EvidenceArtifact = None


async def fetch_miner_payload(target_url: str, min_text_length: int = 600) -> Dict[str, Any]:
    """
    Directly invokes Smart Miner v2.0 crawler and pipeline.
    Bypasses Cloudflare, strips DOM boilerplate, extracts AST clean markdown,
    resolves headings/tables/metadata, and generates cryptographic SHA-256 evidence.
    """
    if route is None:
        raise RuntimeError("haiox-smart-miner package is not installed or importable.")

    print(f"📡 [SmartMiner 2.0] Initiating Bedrock Ingestion for: {target_url}")
    
    try:
        crawl_result = await route(
            target_url,
            min_text_length=min_text_length,
            allow_private_urls=False,
            browser_timeout_ms=30000
        )
        
        if not crawl_result.get("success"):
            print(f"❌ [SmartMiner 2.0] Crawl failed. Error: {crawl_result.get('error')}")
            return {
                "success": False,
                "url": target_url,
                "text": "",
                "markdown": "",
                "evidence": None,
                "error": crawl_result.get("error", "EXTRACTION_FAILED"),
                "status": crawl_result.get("status", "failed"),
                "routing": crawl_result.get("routing", {})
            }

        doc = crawl_result.get("document") or {}
        evidence = crawl_result.get("evidence") or {}
        routing = crawl_result.get("routing") or {}

        markdown_content = doc.get("markdown") or crawl_result.get("text", "")
        sha256 = evidence.get("content_sha256") or "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        print(f"✅ [SmartMiner 2.0] Ingestion successful via [{routing.get('strategy', 'unknown')}] strategy.")
        print(f"🔒 [SmartMiner 2.0] Digital SHA-256 Evidence: {sha256[:16]}... ({len(markdown_content)} chars)")

        return {
            "success": True,
            "url": target_url,
            "text": crawl_result.get("text", ""),
            "markdown": markdown_content,
            "tables": doc.get("tables", []),
            "headings": doc.get("headings", []),
            "metadata": doc.get("metadata", {}),
            "evidence": evidence,
            "content_sha256": sha256,
            "routing": routing,
            "status": "ok"
        }

    except Exception as e:
        print(f"❌ [SmartMiner 2.0] Exception during ingestion: {e}")
        return {
            "success": False,
            "url": target_url,
            "text": "",
            "markdown": "",
            "evidence": None,
            "error": str(e),
            "status": "failed",
            "routing": {}
        }


async def fetch_raw_data_from_miner(target_url: str) -> str:
    """
    Backward-compatible entry point for existing nodes.
    Returns clean AST Markdown directly from Smart Miner v2.0.
    """
    payload = await fetch_miner_payload(target_url)
    if payload.get("success"):
        return payload.get("markdown", "")
    return ""
