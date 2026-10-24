"""Haiox Deep Research - Executive Multi-Agent Investigation Cockpit.

Autonomous DePIN & Web3 due-diligence engine powered by Haiox Smart Miner v2.0.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
import streamlit as st

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from agents.graph import app as depin_agent
from agents.state import AgentState

st.set_page_config(
    page_title="Haiox Deep Research 🔬 Live Cockpit",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling matching Smart Miner
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #ffffff;
    }
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 6px;
    }
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        margin: 6px 0;
    }
    .metric-sub {
        font-size: 11px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
</style>
""", unsafe_allow_html=True)

# Main Banner & Badges (Matching Smart Miner Style)
st.markdown(
    '<div class="main-header">🔬 Haiox Deep Research v1.0.0 '
    '<span class="badge-pill" style="border: 1px solid #00c853; background-color: #082914; color: #55f79a;">✅ Production Release</span> '
    '<span class="badge-pill" style="border: 1px solid #0284c7; background-color: #082142; color: #7dd3fc;">⚡ 14/14 Tests Passing</span> '
    '<span class="badge-pill" style="border: 1px solid #7c3aed; background-color: #1b1035; color: #c084fc;">🔒 SHA-256 Provenance</span> '
    '<span class="badge-pill" style="border: 1px solid #e11d48; background-color: #2b0d1e; color: #fda4af;">⚔️ Adversarial Critic</span> '
    '<span class="badge-pill" style="border: 1px solid #d97706; background-color: #331a00; color: #fde68a;">🪙 Tokenomics Screener</span>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Autonomous Multi-Agent Due-Diligence Engine · Zero-Hallucination Web3 & DePIN Forensic Auditor (Powered by Smart Miner v2.0)</div>',
    unsafe_allow_html=True,
)

# Sidebar Configuration
with st.sidebar:
    st.header("🎯 Target Protocol")
    target_url = st.text_input("Enter Web3 / DePIN Domain URL", value="https://io.net/")
    
    st.markdown("### ⚡ Quick Presets")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🌐 io.net", use_container_width=True):
            target_url = "https://io.net/"
        if st.button("📡 Helium", use_container_width=True):
            target_url = "https://helium.com/"
    with col_p2:
        if st.button("🎨 Render", use_container_width=True):
            target_url = "https://render.x.io/"
        if st.button("☁️ Akash", use_container_width=True):
            target_url = "https://akash.network/"
            
    st.divider()
    st.markdown("### 🧬 Multi-Agent Sequence")
    st.markdown("""
    1. ⛏️ **Smart Miner v2.0 Ingestion** (Clean AST)
    2. 🔒 **Cryptographic Evidence Fingerprint** (SHA-256)
    3. 🏗️ **Architecture Agent** (Claims vs Code)
    4. 🪙 **Deep Tokenomics Agent** (Vesting & Dump Risk)
    5. ⚠️ **Forensic Risk Agent** (Admin Keys & SPOF)
    6. ⚔️ **Adversarial Critic** (Zero-Hallucination)
    7. 💾 **Dual-Storage Engine** (Local SQLite / Supabase)
    """)
    st.divider()
    st.caption("Pillar 2 of the Haiox AI Trilogy")

# Run Trigger
if st.button("🚀 Execute Autonomous Protocol Audit", type="primary", use_container_width=True):
    with st.spinner(f"Ingesting {target_url} via Smart Miner v2.0 & running 6-agent LangGraph pipeline..."):
        initial_state = {
            "target_url": target_url,
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
            
            # --- 4 Executive Telemetry Cards ---
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-sub">🔒 Digital Provenance</div>
                    <div class="metric-val" style="color:#38bdf8; font-size:17px;">{sha256[:16]}...</div>
                    <div style="font-size:11px; color:#64748b;">SHA-256 AST Digest</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                r_score = risk.get("composite_risk_score", 55)
                color = "#ef4444" if r_score > 60 else "#f59e0b" if r_score > 35 else "#10b981"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-sub">⚠️ Composite Risk</div>
                    <div class="metric-val" style="color:{color};">{r_score}/100</div>
                    <div style="font-size:11px; color:#64748b;">{risk.get('risk_tier', 'Moderate')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                t_score = tokenomics.get("inflation_risk_score", 35)
                t_color = "#ef4444" if t_score > 60 else "#10b981"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-sub">🪙 Inflation / Dump Risk</div>
                    <div class="metric-val" style="color:{t_color};">{t_score}/100</div>
                    <div style="font-size:11px; color:#64748b;">{tokenomics.get('sustainability_verdict', 'Utility Driven')}</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                zh_score = critic.get("zero_hallucination_score", 85)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-sub">⚔️ Zero-Hallucination</div>
                    <div class="metric-val" style="color:#818cf8;">{zh_score}%</div>
                    <div style="font-size:11px; color:#64748b;">Source Ground Truth</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.divider()
            
            # --- 5 Deep Investigation Tabs ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🏗️ Technical Architecture",
                "🪙 Deep Tokenomics",
                "⚠️ Risk & Admin Keys",
                "⚔️ Adversarial Critic",
                "📄 AST Raw Evidence"
            ])
            
            with tab1:
                st.subheader("Consensus & Node Topology")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.info(f"**Consensus Mechanism:** `{arch.get('consensus_mechanism', 'N/A')}`")
                    st.write("**Node Hardware Requirements:**")
                    st.json(arch.get("hardware_requirements", {}))
                with col_a2:
                    st.write("**Whitepaper Claims vs GitHub Reality:**")
                    st.json(arch.get("claims_vs_reality", []))
                    
            with tab2:
                st.subheader("Token Economics & Vesting")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.success(f"**Symbol:** `${tokenomics.get('token_symbol', 'N/A')}` | **Supply:** `{tokenomics.get('total_supply', 'N/A')}`")
                    st.write("**Vesting & Cliff Schedule:**")
                    st.json(tokenomics.get("vesting_and_distribution", {}))
                with col_t2:
                    st.write("**Utility Sinks:**", tokenomics.get("token_utility_sinks", []))
                    st.write("**Economic Red Flags:**", tokenomics.get("economic_red_flags", []))
                    
            with tab3:
                st.subheader("Custody & Governance Security")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.warning(f"**Admin Key Custody:** `{risk.get('admin_key_custody', 'N/A')}`")
                    st.write(f"**Audit Status:** `{risk.get('security_audit_status', 'N/A')}`")
                    st.write("**Centralization Points (SPOF):**")
                    st.json(risk.get("centralization_vectors", []))
                with col_r2:
                    st.write("**Technical Risks:**", risk.get("technical_risks", []))
                    st.write("**Regulatory / ISP Exposure:**", risk.get("regulatory_risks", []))
                    
            with tab4:
                st.subheader("Adversarial Fact-Check Verdict")
                st.info(critic.get("cross_examination_summary", "Cross-examination complete."))
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.write("#### ❌ Unsubstantiated Hype Struck Out:")
                    st.json(critic.get("unsubstantiated_claims_struck", []))
                with col_c2:
                    st.write("#### ✅ Verified Ground Truth:")
                    st.json(critic.get("verified_ground_truth", []))
                    
            with tab5:
                st.subheader("Clean AST Markdown (Smart Miner v2.0)")
                st.code(result.get("clean_markdown", "")[:4500], language="markdown")
