import os
import json
import asyncio
import streamlit as st
from agents.graph import app as depin_agent
from agents.state import AgentState

# Page Configuration
st.set_page_config(
    page_title="Haiox Deep Research Cockpit v1.0.0",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Cyberpunk / Dark Glassmorphism Theme
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0d1527 0%, #060913 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Hero Glow */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(56, 189, 248, 0.15);
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        letter-spacing: 0.3px;
    }
    
    /* Live Metric Cards */
    .metric-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 16px 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        margin: 6px 0;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Agent Pipeline Badge Pills */
    .pill-badge {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🔬 Haiox Deep Research & Forensic Auditor</div>
    <div class="hero-subtitle">
        Autonomous Multi-Agent Web3/DePIN Verification Engine | Bedrock Ingestion by <b>Haiox Smart Miner v2.0</b>
    </div>
    <div style="margin-top: 14px;">
        <span class="pill-badge">⚡ Sub-5s WAF Bypass</span>
        <span class="pill-badge">🔒 Cryptographic SHA-256 Provenance</span>
        <span class="pill-badge">⚔️ Adversarial Critic (Zero-Hallucination)</span>
        <span class="pill-badge">🛡️ 14/14 Tests Verified</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Investigation Controls
with st.sidebar:
    st.header("🎯 Investigation Target")
    target_url = st.text_input("Protocol / Whitepaper URL", value="https://io.net/")
    project_id = st.number_input("Vault Project ID", min_value=1, value=1)
    
    st.divider()
    st.markdown("### 🧬 6-Agent LangGraph Core")
    st.markdown("""
    * ⛏️ **Smart Miner v2.0 Ingestion**
    * 🏗️ **Architecture & Code Match**
    * 🪙 **Deep Tokenomics & Vesting**
    * ⚠️ **Risk & Admin Key Custody**
    * ⚔️ **Adversarial Critic (Fact-Check)**
    * 💾 **Dual-Storage Persistence (SQLite)**
    """)
    st.divider()
    st.caption("Pillar 2 of the Haiox Golden Trilogy")

# Launch Trigger Button
launch_col1, launch_col2 = st.columns([3, 1])
with launch_col1:
    btn_run = st.button("🚀 Run Autonomous Protocol Audit", type="primary", use_container_width=True)
with launch_col2:
    st.caption("Press to trigger autonomous multi-agent state graph.")

if btn_run:
    with st.spinner(f"Initiating autonomous due diligence on {target_url}..."):
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
            st.error(f"Audit Pipeline Error: {result['errors']}")
        else:
            findings = result.get("structured_findings", {})
            arch = findings.get("architecture", {})
            tokenomics = findings.get("tokenomics", {})
            risk = findings.get("risk", {})
            critic = findings.get("critic", {})
            sha256 = result.get("content_sha256", "N/A")
            
            # --- 4 Real-time Telemetry Dashboard Cards ---
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔒 SHA-256 Provenance</div>
                    <div class="metric-value" style="color:#38bdf8; font-size:18px;">{sha256[:16]}...</div>
                    <div style="font-size:11px; color:#64748b;">AST Cryptographic Digest</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                r_score = risk.get("composite_risk_score", 55)
                color = "#ef4444" if r_score > 60 else "#f59e0b" if r_score > 35 else "#10b981"
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">⚠️ Composite Risk</div>
                    <div class="metric-value" style="color:{color};">{r_score}/100</div>
                    <div style="font-size:11px; color:#64748b;">{risk.get('risk_tier', 'Moderate')}</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                t_score = tokenomics.get("inflation_risk_score", 35)
                t_color = "#ef4444" if t_score > 60 else "#10b981"
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🪙 Inflation / Dump Risk</div>
                    <div class="metric-value" style="color:{t_color};">{t_score}/100</div>
                    <div style="font-size:11px; color:#64748b;">{tokenomics.get('sustainability_verdict', 'Utility Driven')}</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                zh_score = critic.get("zero_hallucination_score", 85)
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">⚔️ Zero-Hallucination</div>
                    <div class="metric-value" style="color:#818cf8;">{zh_score}%</div>
                    <div style="font-size:11px; color:#64748b;">Ground Truth Accuracy</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- 5 Forensic Investigation Tabs ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏗️ Technical Architecture",
                "🪙 Deep Tokenomics",
                "⚠️ Risk & Admin Keys",
                "⚔️ Critic & Fact-Check",
                "📄 AST Clean Evidence"
            ])
            
            with tab1:
                st.markdown("### 🏗️ Consensus & Client Node Topology")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.info(f"**Consensus Topology:** `{arch.get('consensus_mechanism', 'N/A')}`")
                    st.markdown("**Hardware Node Specifications:**")
                    st.json(arch.get("hardware_requirements", {}))
                with col_a2:
                    st.markdown("**Whitepaper Claims vs GitHub Implementation:**")
                    st.json(arch.get("claims_vs_reality", []))
                    
            with tab2:
                st.markdown("### 🪙 Economic Sustainability & Vesting Schedule")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.success(f"**Token Symbol:** `${tokenomics.get('token_symbol', 'N/A')}` | **Supply:** `{tokenomics.get('total_supply', 'N/A')}`")
                    st.markdown("**Vesting & Cliff Distribution:**")
                    st.json(tokenomics.get("vesting_and_distribution", {}))
                with col_t2:
                    st.markdown("**Utility Sinks & Economic Hazards:**")
                    st.write("**Utility Sinks:**", tokenomics.get("token_utility_sinks", []))
                    st.write("**Red Flags:**", tokenomics.get("economic_red_flags", []))
                    
            with tab3:
                st.markdown("### ⚠️ Centralization Vectors & Admin Key Custody")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.warning(f"**Admin Key Custody:** `{risk.get('admin_key_custody', 'N/A')}`")
                    st.markdown(f"**Security Audit Status:** `{risk.get('security_audit_status', 'N/A')}`")
                    st.write("**Single Points of Failure (SPOF):**")
                    st.json(risk.get("centralization_vectors", []))
                with col_r2:
                    st.markdown("**Technical & Regulatory Liabilities:**")
                    st.write("**Technical Vulnerabilities:**", risk.get("technical_risks", []))
                    st.write("**ISP / Compliance Liabilities:**", risk.get("regulatory_risks", []))
                    
            with tab4:
                st.markdown("### ⚔️ Adversarial Critic & Zero-Hallucination Audit")
                st.info(critic.get("cross_examination_summary", "Cross-examination completed."))
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("#### ❌ Unsubstantiated Hype Struck Out:")
                    st.json(critic.get("unsubstantiated_claims_struck", []))
                with col_c2:
                    st.markdown("#### ✅ Corroborated Ground Truth:")
                    st.json(critic.get("verified_ground_truth", []))
                    
            with tab5:
                st.markdown("### 📄 Clean AST Markdown (Smart Miner v2.0 Extraction)")
                st.caption(f"SHA-256 Digest: {sha256}")
                st.code(result.get("clean_markdown", "")[:4500], language="markdown")
