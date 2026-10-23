from typing import TypedDict, List, Dict, Any, Optional, Union

class AgentState(TypedDict):
    """
    Lightweight State for LangGraph.
    Carries structured data, digital cryptographic SHA-256 evidence, and AST clean markdown.
    """
    target_url: str
    project_id: Optional[int]           # Project ID in the database
    evidence_id: Optional[Union[int, str]] # ID of the evidence stored in the Evidence Layer
    content_sha256: Optional[str]       # Cryptographic SHA-256 fingerprint of evidence
    clean_markdown: Optional[str]       # AST Clean Markdown from Smart Miner v2.0
    evidence_artifact: Optional[Dict[str, Any]] # Structured evidence provenance
    
    # Structured outputs from specialized agents (tokenomics, risk, etc.)
    structured_findings: Optional[Dict[str, Any]]
    
    # Final verification result
    verification_result: Optional[Dict[str, Any]]
    
    # Current status and error management
    current_step: str
    errors: List[str]
