import json
import os
import re
from core.llm_router import call_llm
from agents.state import AgentState

async def twitter_factory_node(state: AgentState):
    print("✍️ [Graph] Step 6: Generating Content (Twitter & GitHub Reports)")
    
    findings = state.get("structured_findings", {})
    verification = state.get("verification_result", {})
    target_url = state.get("target_url", "Unknown Project")
    sha256 = state.get("content_sha256", "N/A")
    
    if not findings:
        return {"errors": state.get("errors", []) + ["No findings available to generate content."]}

    prompt = f"""
    Act as a Web3 & DePIN On-Chain Analyst.
    Write a 4-tweet Twitter thread based on the research data below.
    
    Project: {target_url}
    SHA-256 Cryptographic Digest: {sha256}
    Data: {json.dumps(findings)}
    
    RULES:
    1. Language: STRICTLY ENGLISH.
    2. Tone: Professional, investigative, Alpha Caller style.
    3. Format: Number each tweet clearly (e.g., 🧵 1/4:, 2/4:).
    4. Output raw tweets ONLY. Do not write introductory sentences.
    """
    
    try:
        thread_content = await call_llm(prompt)
        
        # Fallback mechanism if LLM is unavailable or empty
        if not thread_content or not thread_content.strip() or "Error" in thread_content:
            token_info = findings.get("tokenomics", {})
            risk_info = findings.get("risk", {})
            thread_content = (
                f"🧵 1/4: Deep dive into {target_url} powered by Haiox Deep Research & Smart Miner v2.0.\n"
                f"Cryptographic Evidence Proof [SHA-256: {sha256[:16]}...]. Zero hallucination guaranteed.\n\n"
                f"🧵 2/4: Tokenomics Architecture: {json.dumps(token_info)[:180]}...\n\n"
                f"🧵 3/4: Risk Assessment & Decentralization: {json.dumps(risk_info)[:180]}...\n\n"
                f"🧵 4/4: Full verified audit report and AST source document compiled into Haiox Research Vault."
            )

        # File generation logic
        project_name_match = re.search(r'https?://(?:www\.)?([^/]+)', target_url)
        project_name = project_name_match.group(1).replace('.', '_') if project_name_match else "project"
        
        os.makedirs("output_threads", exist_ok=True)
        
        # 1. Save the Twitter Thread
        thread_filepath = os.path.join("output_threads", f"{project_name}_thread.txt")
        with open(thread_filepath, "w", encoding="utf-8") as f:
            f.write(thread_content.strip())
            
        # 2. Save the GitHub Markdown Report
        report_filepath = os.path.join("output_threads", f"{project_name}_GitHub_Report.md")
        with open(report_filepath, "w", encoding="utf-8") as f:
            f.write(f"# 🕵️‍♂️ DePIN Research Report: {target_url}\n\n")
            f.write(f"> **Digital Evidence SHA-256**: `{sha256}`  \n")
            f.write(f"> **Extractor Engine**: Haiox Smart Miner v2.0 (AST Normalizer & Cryptographic Provenance)  \n\n")
            f.write("## 🏗️ Technical Architecture & Claims vs Code\n")
            f.write(f"```json\n{json.dumps(findings.get('architecture', {}), indent=2)}\n```\n\n")
            f.write("## 📊 Tokenomics\n")
            f.write(f"```json\n{json.dumps(findings.get('tokenomics', {}), indent=2)}\n```\n\n")
            f.write("## ⚠️ Risk Analysis\n")
            f.write(f"```json\n{json.dumps(findings.get('risk', {}), indent=2)}\n```\n\n")
            f.write("## ⚔️ Adversarial Critic & Zero-Hallucination Audit\n")
            f.write(f"```json\n{json.dumps(findings.get('critic', {}), indent=2)}\n```\n\n")
            f.write("## ⚖️ Verification Results\n")
            f.write(f"```json\n{json.dumps(verification, indent=2)}\n```\n")

        print(f"✅ [Content Factory] Twitter thread saved in: {thread_filepath}")
        print(f"✅ [Content Factory] GitHub Report saved in: {report_filepath}")
        
        return {"current_step": "content_generated"}
        
    except Exception as e:
        print(f"❌ [Content Factory] Error: {e}")
        return {"errors": state.get("errors", []) + [str(e)]}
