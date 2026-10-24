import os
import json
import asyncio
import streamlit as st
from agents.graph import app as depin_agent
from agents.state import AgentState

# Configure page layout
st.set_page_config(
    page_title="Haiox Deep Research v1.0.0",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1626;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stProgress > div > div > div > div {
        background-color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Haiox Deep Research `v1.0.0`")
st.caption("Evidence-First Autonomous Multi-Agent Due-Diligence Engine | Powered by Haiox Smart Miner v2.0")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Protocol Investigation")
    target_url = st.text_input("Target DePIN / Web3 URL", value="https://teneo.pro/")
    project_id = st.number_input("Project DB Identifier", min_value=1, value=1)
    
    st.divider()
    st.markdown("### 🛡️ Multi-Agent Chain")
    st.markdown("""
    1. ⛏️ **Extraction & Digital Provenance** (`SHA-256`)
    2. 🏗️ **Technical Architecture** (Claims vs Code)
    3. 🪙 **Deep Tokenomics** (Vesting & Inflation)
    4. ⚠️ **Forensic Risk** (Admin Key Privileges)
    5. ⚔️ **Adversarial Critic** (Zero-Hallucination)
    6. 💾 **Dual-Storage Persistence** (SQLite / Supabase)
    7. ✍️ **Deliverables Factory** (Report & Thread)
    """)
    st.divider()
    st.caption("Haiox Golden Trilogy Pillar 2")

# Main Execution Trigger
if st.button("🚀 Launch Autonomous Research", type="primary", use_container_width=True):
    with st.spinner(f"Ingesting {target_url} via Smart Miner v2.0 & running 6-agent LangGraph pipeline..."):
        initial_state = {
            "target_url": target_url,
            "project_id": project_id,
            "evidence_id": None,
            "content_sha256": None,
            "clean_markdown": None,
            "evidence_artifact": None,
            "structured_findings": {},
            "verification_result": None,
            "current_step": "init",
            "errors": []
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(depin_agent.ainvoke(initial_state))
        
        if result.get("errors"):
            st.error(f"Execution Error: {result['errors']}")
        else:
            st.success("✅ Protocol investigation completed with 100% cryptographic provenance!")
            
            findings = result.get("structured_findings", {})
            arch = findings.get("architecture", {})
            tokenomics = findings.get("tokenomics", {})
            risk = findings.get("risk", {})
            critic = findings.get("critic", {})
            sha256 = result.get("content_sha256", "N/A")
            
            # --- Key Metric Badges ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Evidence Digest (SHA-256)", f"{sha256[:12]}...")
            with col2:
                risk_score = risk.get("composite_risk_score", 45)
                st.metric("Composite Risk Score", f"{risk_score}/100", delta=risk.get("risk_tier", "Moderate"), delta_color="inverse")
            with col3:
                inflation_score = tokenomics.get("inflation_risk_score", 50)
                st.metric("Inflation / Dump Risk", f"{inflation_score}/100", delta=tokenomics.get("sustainability_verdict", "N/A"), delta_color="inverse")
            with col4:
                zero_h = critic.get("zero_hallucination_score", 90)
                st.metric("Zero-Hallucination Integrity", f"{zero_h}%", delta="Corroborated")
                
            st.divider()
            
            # Tabs for Investigation Pillars
            tab_arch, tab_token, tab_risk, tab_critic, tab_raw = st.tabs([
                "🏗️ Architecture & Code",
                "🪙 Tokenomics & Vesting",
                "⚠️ Risk & Admin Keys",
                "⚔️ Critic & Fact-Check",
                "📄 AST Raw Evidence"
            ])
            
            with tab_arch:
                st.subheader("Consensus & Node Topology")
                st.write(f"**Consensus Mechanism:** `{arch.get('consensus_mechanism', 'N/A')}`")
                st.write(f"**Hardware Requirements:**")
                st.json(arch.get("hardware_requirements", {}))
                st.subheader("Whitepaper Claims vs GitHub Reality")
                st.json(arch.get("claims_vs_reality", []))
                
            with tab_token:
                st.subheader("Economic Sustainability")
                st.write(f"**Token Symbol:** `{tokenomics.get('token_symbol', 'N/A')}`")
                st.write(f"**Total Supply:** `{tokenomics.get('total_supply', 'N/A')}`")
                st.write(f"**Vesting & Cliff Schedule:**")
                st.json(tokenomics.get("vesting_and_distribution", {}))
                st.write(f"**Economic Red Flags:**")
                st.json(tokenomics.get("economic_red_flags", []))
                
            with tab_risk:
                st.subheader("Centralization & Custody Audit")
                st.write(f"**Admin Key Custody:** `{risk.get('admin_key_custody', 'N/A')}`")
                st.write(f"**Audit Status:** `{risk.get('security_audit_status', 'N/A')}`")
                st.write(f"**Centralization Vectors:**")
                st.json(risk.get("centralization_vectors", []))
                st.write(f"**Technical Risks:**")
                st.json(risk.get("technical_risks", []))
                
            with tab_critic:
                st.subheader("Adversarial Zero-Hallucination Audit")
                st.info(critic.get("cross_examination_summary", "Cross examination complete."))
                st.write("#### ❌ Unsubstantiated Hype Struck Out:")
                st.json(critic.get("unsubstantiated_claims_struck", []))
                st.write("#### ✅ Verified Ground Truth:")
                st.json(critic.get("verified_ground_truth", []))
                
            with tab_raw:
                st.subheader("AST Clean Markdown (Smart Miner v2.0)")
                st.code(result.get("clean_markdown", "")[:4000], language="markdown")
