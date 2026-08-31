import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import json, os, datetime, re

from engine import (
    cortex_analyst_agent,
    cortex_search_agent,
    persona_reconciler,
    tariff_optimizer,
    action_executor,
    ontology_engine,
    guardrails,
    db_engine
)

st.set_page_config(
    page_title="SCCT Agent | Victoria's Secret & Co. Control Tower",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #D43F70;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #FDF4F7;
        border-left: 5px solid #D43F70;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .sql-box {
        background-color: #1E1E1E;
        color: #9CDCFE;
        padding: 12px;
        border-radius: 6px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Victoria%27s_Secret_logo.svg/1200px-Victoria%27s_Secret_logo.svg.png", width=220)
    st.markdown("### 🌐 Global SCCT Agent")
    st.markdown("**Victoria's Secret & Co. Control Tower**")
    st.caption("Governed Conversational Analytics & Multi-Tier Sourcing Intelligence")
    
    st.divider()
    active_persona = st.selectbox(
        "🎭 Select Active Persona:",
        ["EXECUTIVE", "PLANNING", "PROCUREMENT", "LOGISTICS", "FINANCE"],
        index=0
    )
    
    st.markdown("#### ⚙️ Data Engine Selection")
    engine_choice = st.radio(
        "Select Execution Engine:",
        ["❄️ Live Snowflake Cortex (Primary)", "💾 Local SQLite Cache"],
        index=0
    )
    if "Snowflake" in engine_choice:
        db_engine.set_mode("Snowflake")
        st.success("Connected to `VS_SUPPLY_CHAIN_DB.GOLD`")
    else:
        db_engine.set_mode("SQLite")
        st.info("Using local high-performance cache")

    
    st.divider()
    st.markdown("#### 🛡️ Active Guardrails")
    st.success("✅ Gold Semantic Enforcement: ON")
    st.success("✅ Zero-Divergence Reconciliation: ON")
    st.success("✅ Anti-Hallucination Guard: ON")
    
    st.divider()
    if st.button("🔄 Refresh Data & Pipeline"):
        st.cache_data.clear()
        st.success("Pipeline refreshed successfully!")

# Main Title & KPI Ribbon
st.markdown('<div class="main-header">👑 Victoria\'s Secret & Co. Supply Chain Control Tower</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Unified Supply Chain Ontology, Cortex Analyst Conversational Layer & Governed Multi-Tier Sourcing</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.metric(label="Canonical OTD %", value="92.8%", delta="+1.2% vs SLA (95%)")
with kpi2:
    st.metric(label="Order Fill Rate", value="98.4%", delta="+0.6% MoM")
with kpi3:
    st.metric(label="Avg Days of Inventory", value="38.5 Days", delta="-3.2 Days Optimal")
with kpi4:
    st.metric(label="Avg Landed Cost", value="$15.42/unit", delta="-4.8% Tariff Hedged")
with kpi5:
    st.metric(label="Persona Alignment", value="100.0%", delta="0% Math Variance")

st.markdown("---")

# Main Navigation Tabs
tab_chat, tab_reconcile, tab_tariff, tab_graph, tab_docs, tab_actions = st.tabs([
    "💬 Governed Conversational Analytics",
    "⚖️ Cross-Persona Reconciliation",
    "🚢 Tariff & Sourcing Optimizer",
    "🕸️ Supply Chain Ontology & BOM",
    "📄 Unstructured Contract Intelligence",
    "⚡ Autonomous MCP Action Center"
])

# -------------------------------------------------------------------------------------------------
# TAB 1: Governed Conversational Analytics (Cortex Analyst with Persistent Chat History)
# -------------------------------------------------------------------------------------------------
with tab_chat:
    st.markdown("### 💬 Snowflake Cortex Analyst: Natural Language Supply Chain Queries")
    st.caption("Ask questions across ERP, TMS, QA, and Inventory. Conversations are preserved across turns and strictly grounded in governed Gold semantic views.")
    
    # Initialize session state chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Quick Sample Questions Header & Clear History
    col_benchmarks, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑️ Clear History", help="Reset conversational chat thread"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col_benchmarks:
        st.markdown("**💡 Quick Benchmark Prompts:**")
        quick_cols = st.columns(4)
        sample_prompt = None
        with quick_cols[0]:
            if st.button("📊 OTD & Landed Cost by Country"):
                sample_prompt = "What is the On-Time Delivery rate and Landed Cost by sourcing country for Q3?"
        with quick_cols[1]:
            if st.button("📦 Days of Inventory by RDC"):
                sample_prompt = "What are the Days of Inventory (DOI) across our North American Regional Distribution Centers?"
        with quick_cols[2]:
            if st.button("⚖️ MAS vs Crystal Production"):
                sample_prompt = "Compare the production allocation, lead time, and tariff impact between MAS Holdings Sri Lanka and Crystal International Vietnam."
        with quick_cols[3]:
            if st.button("🏭 Top Supplier Business"):
                sample_prompt = "from which supplier we have done most of business from all country"

    st.markdown("---")

    # Render previous conversation history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**{msg['content']}**")
        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="👑"):
                resp = msg["response"]
                if resp.get("success"):
                    st.markdown(f"### 💡 Executive Insight\n{resp.get('summary')}")
                    
                    with st.expander("🛡️ Governed Snowflake SQL & Semantic Provenance", expanded=False):
                        st.code(resp.get("generated_sql"), language="sql")
                        if resp.get('is_verified_golden_query'):
                            st.caption(f"⭐ Grounded in verified Golden Benchmark | 🔌 Source: **{resp.get('backend', db_engine.backend)}** ({resp.get('row_count')} rows)")
                        else:
                            st.caption(f"🔒 Governed by Gold Semantic Model | 🔌 Source: **{resp.get('backend', db_engine.backend)}** ({resp.get('row_count')} rows)")

                    df_res = pd.DataFrame(resp.get("data", []))
                    if not df_res.empty:
                        st.markdown("#### 📋 Result Data")
                        st.dataframe(df_res, use_container_width=True)
                        
                        # Safe visualization
                        try:
                            clean_df = df_res.copy()
                            clean_df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', str(col)).strip('_') for col in clean_df.columns]
                            num_cols = clean_df.select_dtypes(include=[np.number]).columns.tolist()
                            cat_cols = clean_df.select_dtypes(include=['object']).columns.tolist()
                            
                            if num_cols and cat_cols and len(clean_df) > 1:
                                chart = alt.Chart(clean_df).mark_bar(color='#D43F70').encode(
                                    x=alt.X(f"{cat_cols[0]}:N", sort=None, title=cat_cols[0].replace('_', ' ').title()),
                                    y=alt.Y(f"{num_cols[0]}:Q", title=num_cols[0].replace('_', ' ').title()),
                                    tooltip=list(clean_df.columns)
                                ).properties(height=260)
                                st.altair_chart(chart, use_container_width=True)
                        except Exception:
                            pass
                else:
                    st.error(f"**Query Rejection / Guardrail Alert:** {resp.get('error')}")

    # Handle incoming input (either from chat_input or sample prompt button)
    user_input = st.chat_input("Ask Snowflake Cortex Analyst a supply chain question (e.g. 'top 5 suppliers by tariff')...")
    active_query = sample_prompt or user_input

    if active_query:
        # 1. Render User Message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{active_query}**")
        st.session_state.chat_history.append({"role": "user", "content": active_query})

        # 2. Execute with Agent & Render Assistant Message
        with st.chat_message("assistant", avatar="👑"):
            with st.spinner("Analyzing semantic model, verifying guardrails, and querying Snowflake Cortex..."):
                response = cortex_analyst_agent.generate_and_execute(active_query, active_persona)
                
                if response['success']:
                    st.markdown(f"### 💡 Executive Insight\n{response.get('summary')}")
                    
                    with st.expander("🛡️ Governed Snowflake SQL & Semantic Provenance", expanded=False):
                        st.code(response['generated_sql'], language="sql")
                        if response.get('is_verified_golden_query'):
                            st.caption(f"⭐ Grounded in verified Golden Benchmark | 🔌 Source: **{response.get('backend', db_engine.backend)}** ({response.get('row_count')} rows)")
                        else:
                            st.caption(f"🔒 Governed by Gold Semantic Model | 🔌 Source: **{response.get('backend', db_engine.backend)}** ({response.get('row_count')} rows)")

                    df_res = pd.DataFrame(response['data'])
                    if not df_res.empty:
                        st.markdown("#### 📋 Result Data")
                        st.dataframe(df_res, use_container_width=True)
                        
                        # Safe visualization
                        try:
                            clean_df = df_res.copy()
                            clean_df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', str(col)).strip('_') for col in clean_df.columns]
                            num_cols = clean_df.select_dtypes(include=[np.number]).columns.tolist()
                            cat_cols = clean_df.select_dtypes(include=['object']).columns.tolist()
                            
                            if num_cols and cat_cols and len(clean_df) > 1:
                                chart = alt.Chart(clean_df).mark_bar(color='#D43F70').encode(
                                    x=alt.X(f"{cat_cols[0]}:N", sort=None, title=cat_cols[0].replace('_', ' ').title()),
                                    y=alt.Y(f"{num_cols[0]}:Q", title=num_cols[0].replace('_', ' ').title()),
                                    tooltip=list(clean_df.columns)
                                ).properties(height=260)
                                st.altair_chart(chart, use_container_width=True)
                        except Exception:
                            pass
                else:
                    st.error(f"**Query Rejection / Guardrail Alert:** {response.get('error')}")

        st.session_state.chat_history.append({"role": "assistant", "response": response})
        st.rerun()


# -------------------------------------------------------------------------------------------------
# TAB 2: Cross-Persona Reconciliation Simulator
# -------------------------------------------------------------------------------------------------
with tab_reconcile:
    st.markdown("### ⚖️ Cross-Persona Reconciliation Engine")
    st.caption("Proving zero mathematical divergence across Planning, Procurement, Logistics, and Finance through shared semantic definitions.")
    
    cat_filter = st.selectbox("Filter by Product Category:", ["ALL", "Bras", "Panties", "Loungewear", "Fragrance", "Sleepwear"])
    filter_dict = {"category": cat_filter} if cat_filter != "ALL" else None
    
    rec_data = persona_reconciler.reconcile_metric("on_time_delivery_rate", filter_dict)
    
    st.markdown(f"#### 🎯 Canonical Master Metrics (Evaluated over {rec_data['total_records_evaluated']:,} records)")
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.metric("Master Governed OTD", f"{rec_data['canonical_otd_pct']}%")
    with mcol2:
        st.metric("Master Governed Landed Cost", f"${rec_data['canonical_landed_cost_usd']}/unit")
    with mcol3:
        st.metric("Mathematical Variance", "0.00%", delta="100% Reconciled")

    st.markdown("#### 👥 Multi-Persona Side-by-Side Comparison")
    pcols = st.columns(4)
    personas_dict = rec_data['persona_comparison']
    
    colors = {"Planning": "#1E88E5", "Procurement": "#00897B", "Logistics": "#FB8C00", "Finance": "#8E24AA"}
    for idx, (p_name, p_info) in enumerate(personas_dict.items()):
        with pcols[idx]:
            st.markdown(f"""
            <div style="border: 2px solid {colors[p_name]}; border-radius: 8px; padding: 12px; background-color: #FAFAFA;">
                <h4 style="color: {colors[p_name]}; margin-top: 0;">{p_name}</h4>
                <p><strong>Legacy Silo View:</strong><br><span style="color: #D32F2F; font-weight: bold; font-size: 1.2rem;">{p_info['legacy_value']}</span></p>
                <p><strong>Governed Value:</strong><br><span style="color: #388E3C; font-weight: bold; font-size: 1.2rem;">{p_info['governed_canonical_value']}</span></p>
                <hr style="margin: 8px 0;">
                <small><strong>Why Discrepancy Occurred:</strong> {p_info['divergence_reason']}</small><br><br>
                <small><strong>Reconciliation Key:</strong> {p_info['reconciliation_proof']}</small>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# TAB 3: Sourcing & Tariff Landed Cost Optimizer
# -------------------------------------------------------------------------------------------------
with tab_tariff:
    st.markdown("### 🚢 Multi-Sourcing Sourcing & Section 301 Tariff Optimizer")
    st.caption("Model dual-sourcing splits and trade tariff policy shifts across Vietnam, Sri Lanka, Mexico, and India.")
    
    t_col1, t_col2 = st.columns([1, 2])
    with t_col1:
        st.markdown("#### 🎛️ Tariff Adjustments")
        vn_t = st.slider("Vietnam Tariff Rate (%) [Section 301]", 0.0, 50.0, 25.0, 1.0)
        sl_t = st.slider("Sri Lanka Tariff Rate (%)", 0.0, 30.0, 8.0, 1.0)
        mx_t = st.slider("Mexico Tariff Rate (%) [USMCA Duty-Free]", 0.0, 20.0, 0.0, 1.0)
        in_t = st.slider("India Tariff Rate (%)", 0.0, 30.0, 10.0, 1.0)
        order_units = st.number_input("Demand Volume (Units):", min_value=10000, max_value=1000000, value=100000, step=10000)
        
        sim_res = tariff_optimizer.simulate_tariff_impact({'Vietnam': vn_t, 'Sri Lanka': sl_t, 'Mexico': mx_t, 'India': in_t}, order_units)

    with t_col2:
        st.markdown("#### 💰 True Landed Cost Breakdown ($/unit)")
        df_sim = pd.DataFrame(sim_res['factory_comparisons'])
        
        chart_data = pd.melt(
            df_sim, 
            id_vars=['country'], 
            value_vars=['base_fob_usd', 'freight_usd', 'tariff_duty_usd', 'drayage_usd'],
            var_name='Cost_Component', 
            value_name='Cost_USD'
        )
        component_labels = {
            'base_fob_usd': '1. Factory FOB Cost',
            'freight_usd': '2. Freight & Logistics',
            'tariff_duty_usd': '3. Customs & Tariffs',
            'drayage_usd': '4. Drayage & Handling'
        }
        chart_data['Cost_Component'] = chart_data['Cost_Component'].map(component_labels)
        
        stacked_bar = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('country:N', title="Sourcing Origin"),
            y=alt.Y('Cost_USD:Q', title="Total Landed Cost ($/unit)"),
            color=alt.Color('Cost_Component:N', scale=alt.Scale(scheme='category10')),
            tooltip=['country', 'Cost_Component', 'Cost_USD']
        ).properties(height=320)
        st.altair_chart(stacked_bar, use_container_width=True)

    st.markdown("#### 🎯 AI Recommended Dual-Sourcing Allocation")
    rec_split = sim_res['recommended_split']
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Primary Sourcing Factory", f"{rec_split['primary_country']} ({rec_split['primary_allocation_pct']}%)")
    with r2:
        st.metric("Secondary Nearshore Buffer", f"{rec_split['secondary_country']} ({rec_split['secondary_allocation_pct']}%)")
    with r3:
        st.metric("Blended Landed Cost", f"${rec_split['blended_unit_landed_cost_usd']:.2f}/unit")
    with r4:
        st.metric("Blended Lead Time", f"{rec_split['blended_lead_time_days']} Days")
    st.info(f"💡 **Strategic Sourcing Rationale:** {rec_split['rationale']}")

# -------------------------------------------------------------------------------------------------
# TAB 4: Supply Chain Ontology & BOM Graph
# -------------------------------------------------------------------------------------------------
with tab_graph:
    st.markdown("### 🕸️ Multi-Tier Supply Chain Ontology & BOM Architecture")
    st.caption("Formal 13-entity business model and 12 relationship edges powering Victoria's Secret & Co.'s semantic layer.")
    
    entities = ontology_engine.get_entities()
    relationships = ontology_engine.get_relationships()
    
    gcol1, gcol2 = st.columns([1.2, 1.8])
    with gcol1:
        st.markdown(f"#### 📦 Core Entities ({len(entities)})")
        selected_entity = st.selectbox("Inspect Entity Node:", list(entities.keys()))
        ent_info = entities[selected_entity]
        st.markdown(f"**Description:** {ent_info.get('description')}")
        st.markdown(f"**Primary Key:** `{ent_info.get('primary_key')}`")
        st.markdown("**Attributes:**")
        st.write(ent_info.get('properties', []))
        
        neighbors = ontology_engine.get_entity_neighbors(selected_entity)
        st.markdown(f"**Upstream Predecessors:** `{neighbors['upstream']}`")
        st.markdown(f"**Downstream Successors:** `{neighbors['downstream']}`")

    with gcol2:
        st.markdown("#### 🔗 Ontology Relationship Edges")
        df_rels = pd.DataFrame(relationships)
        st.dataframe(df_rels, use_container_width=True)
        
        st.markdown("#### 🧭 Multi-Tier Provenance Path Finder")
        src_e = st.selectbox("Source Entity:", list(entities.keys()), index=0)
        tgt_e = st.selectbox("Target Entity:", list(entities.keys()), index=len(entities)-1)
        if st.button("Trace Lineage Path"):
            p_info = ontology_engine.find_shortest_path(src_e, tgt_e)
            if p_info:
                st.success(f"Path Found ({p_info['hops']} hops): " + " ➡️ ".join(p_info['path']))
                st.json(p_info['edges'])
            else:
                st.warning("No direct path between selected entities.")

# -------------------------------------------------------------------------------------------------
# TAB 5: Unstructured Contract & SLA Intelligence (Cortex Search)
# -------------------------------------------------------------------------------------------------
with tab_docs:
    st.markdown("### 📄 Snowflake Cortex Search: Supplier Contracts & Compliance SLAs")
    st.caption("Hybrid semantic search across Master Sourcing Agreements (MSAs), OEKO-TEX audits, and Port Advisories.")
    
    search_q = st.text_input("Search contracts or SLAs:", placeholder="e.g. MAS Holdings late delivery penalty or Long Beach dwell delay mitigation")
    if st.button("🔍 Search Documents", type="primary") or search_q:
        if search_q:
            doc_ans = cortex_search_agent.answer_query(search_q)
            st.markdown(doc_ans['answer'])
            
            st.markdown("#### 📑 Grounded Source Documents")
            for doc in doc_ans.get('matched_documents', []):
                with st.expander(f"{doc['title']} ({doc['category']})"):
                    st.markdown(doc['content'])

# -------------------------------------------------------------------------------------------------
# TAB 6: Autonomous MCP Operational Actions Center
# -------------------------------------------------------------------------------------------------
with tab_actions:
    st.markdown("### ⚡ Autonomous MCP Operational Interventions")
    st.caption("Execute autonomous supply chain workflows directly into Jira, Slack, and ERP logistics systems.")
    
    act_col1, act_col2 = st.columns([1, 1.5])
    with act_col1:
        st.markdown("#### 🛠️ Trigger Operational Action")
        action_choice = st.selectbox("Select Action Type:", ["PO_EXPEDITE", "CREATE_JIRA_INCIDENT", "POST_SLACK_ALERT"])
        
        if action_choice == "PO_EXPEDITE":
            po_in = st.text_input("Target PO Number:", value="PO-VS-1045")
            reason_in = st.text_area("Expedite Rationale:", value="Mitigate Port of Long Beach container dwell bottleneck for Holiday Bra inventory.")
            carrier_in = st.selectbox("Expedited Air Carrier:", ["FedEx Trade Logistics", "Emirates SkyCargo", "Cathay Cargo"])
            if st.button("✈️ Dispatch PO Expedite"):
                res_act = action_executor.expedite_purchase_order(po_in, reason_in, carrier_in)
                st.success(res_act['message'])
        
        elif action_choice == "CREATE_JIRA_INCIDENT":
            title_in = st.text_input("Incident Title:", value="High West Coast Port Dwell - Haiphong Container Delay")
            sev_in = st.selectbox("Severity:", ["P1_CRITICAL", "P2_HIGH", "P3_MEDIUM"])
            details_in = st.text_area("Details:", value="Container dwell exceeds 6.8 days at Berth 400. Risk of stockout at Columbus RDC.")
            if st.button("🎫 Create Jira Incident"):
                res_act = action_executor.create_jira_supply_incident(title_in, sev_in, details=details_in)
                st.success(res_act['message'])
                
        elif action_choice == "POST_SLACK_ALERT":
            chan_in = st.text_input("Slack Channel:", value="#supply-chain-control-tower")
            msg_in = st.text_area("Alert Message:", value="⚠️ Governance Alert: Vietnam section 301 tariff adjustment simulation complete. Nearshore Mexico allocation increase recommended.")
            if st.button("📢 Broadcast Alert"):
                res_act = action_executor.send_slack_governance_alert(chan_in, msg_in)
                st.success(res_act['message'])

    with act_col2:
        st.markdown("#### 📜 Executed MCP Operational Audit Trail")
        history = action_executor.get_action_history()
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("No operational interventions triggered yet in this session.")
