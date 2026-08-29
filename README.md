# 👑 SCCT Agent: Victoria\'s Secret & Co. Global Supply Chain Control Tower
### Governed Conversational Analytics, Multi-Tier Sourcing Provenance & Snowflake Cortex Engine

[![CoCo CLI Lifecycle](https://img.shields.io/badge/CoCo-Verified-brightgreen.svg)]()
[![Snowflake Cortex](https://img.shields.io/badge/Snowflake-Cortex%20Analyst%20%26%20Search-blue.svg)]()
[![Model Context Protocol](https://img.shields.io/badge/MCP-Protocol%20Ready-purple.svg)]()
[![Reconciliation Variance](https://img.shields.io/badge/Variance-0.00%25%20Governed-success.svg)]()

---

## 🎯 Executive Summary
Supply chain data across global retail giants like **Victoria\'s Secret & Co. (VS&Co)** is scattered across ERP (SAP), Warehouse/TMS (Manhattan Associates), Quality Lab Systems, and 3PL IoT telematics. Historically, the same operational question yielded contradictory answers across teams:
- **Planning** saw $88.6\%$ OTD (measured strictly against unconstrained customer demand dates).
- **Procurement** saw $97.2\%$ OTD (measured against Tier 1 factory ex-works gate exit dates).
- **Logistics** saw $93.8\%$ OTD (measured against ocean carrier port arrival notices).
- **Finance** tracked standard FOB purchase prices ($\$12.22$), neglecting volatile Section 301 tariffs, demurrage, and drayage fees.

**SCCT Agent (Supply Chain Control Tower Agent)** solves this by:
1. Defining a **13-Entity Multi-Tier Sourcing Ontology** covering Tier 3 Raw Materials (Supima cotton, modal), Tier 2 Fabric Mills (OEKO-TEX/GOTS/REACH certified), Tier 1 Cut-and-Sew Assembly Plants (Sri Lanka, Vietnam, Mexico, India), North American RDCs, and Reverse Logistics.
2. Formulating **Governed Canonical Metrics** with mathematical proofs in a Snowflake Cortex Analyst semantic model.
3. Layering **Conversational Analytics & Cortex Search RAG** for natural language queries and contract intelligence.
4. Delivering **Zero-Divergence Cross-Persona Reconciliation** and **Real-Time Section 301 Tariff Optimization**.

---

## 🏗️ Architecture & Data Lineage

```
[Tier 3 Raw Suppliers]  --> [Tier 2 Fabric Mills & Dyehouses] --> [Tier 1 Assembly Factories]
   (Supima, Tencel)             (OEKO-TEX / REACH Lace)            (Sri Lanka, Vietnam, Mexico)
           |                                                                 |
           +-------------------- [ Purchase Orders (ERP) ] <-----------------+
                                           |
                                [ Shipments & 3PL TMS ] (IoT Temp/Shock)
                                           |
                    +----------------------+----------------------+
                    |                                             |
       [Ocean & Air Freight]                             [Nearshore USMCA Rail]
     (Ports: Savannah / Long Beach)                       (Laredo -> Columbus)
                    |                                             |
                    +----------------------+----------------------+
                                           |
                           [ North American RDCs (Columbus) ]
                                           |
                     +---------------------+---------------------+
                     |                                           |
           [800+ Retail Stores]                         [E-Commerce Direct]
                     |                                           |
                     +---------------------+---------------------+
                                           |
                              [ Reverse Logistics Returns ]
                            (Hygienic Restock vs Destruction)
```

---

## 📐 Canonical Mathematical Proofs

### 1. Governed On-Time Delivery (OTD %)
$$\text{Canonical OTD} = \frac{\sum \mathbf{1}_{\{\text{Destination Receipt} \le \text{Promised Date} \land \text{Defects} = 0\}}}{N_{\text{total shipments}}} \times 100\%$$

### 2. Comprehensive Absorbed Unit Landed Cost
$$\text{Unit Landed Cost} = \text{Unit FOB Price} + \text{Allocated Freight} + (\text{FOB} \times \text{Tariff Rate}) + \text{Drayage Handling}$$

### 3. Days of Inventory (DOI)
$$\text{DOI} = \frac{\sum (\text{Units on Hand} \times \text{Unit Standard Cost})}{\frac{\text{Annualized COGS}}{365}}$$

---

## 🚀 Quick Start (Local Standalone & Snowflake)

### 1. Run Automated Test Suite (11/11 Passing)
```bash
python run_tests.py
```

### 2. Launch Interactive Streamlit Control Tower
```bash
streamlit run app.py
```

### 3. CLI Command Suite (`coco_cli.py`)
```bash
# Ask natural language questions via Cortex Analyst
python coco_cli.py ask "What is the On-Time Delivery rate and Landed Cost by sourcing country for Q3?"

# Reconcile across enterprise personas
python coco_cli.py reconcile --metric on_time_delivery_rate

# Simulate Section 301 tariff shifts
python coco_cli.py tariff --vietnam 25.0 --demand 100000

# Cortex Search contract RAG
python coco_cli.py search "What is the late delivery penalty for MAS Holdings?"

# Dispatch operational MCP actions
python coco_cli.py action PO_EXPEDITE PO-VS-1045 --details "Port of Long Beach dwell mitigation"
```

---

## ❄️ Snowflake Cloud Deployment
To deploy directly to your Snowflake Data Cloud environment:
1. Run `snowflake_sql/01_bronze_raw_tables.sql` (Raw ingestion layer).
2. Run `snowflake_sql/02_silver_conformed_tables.sql` (Conformed entities and cleaning).
3. Run `snowflake_sql/03_gold_semantic_views.sql` (Governed Gold views with canonical metrics).
4. Run `snowflake_sql/04_dynamic_tables_and_tasks.sql` (IoT temperature anomaly streaming tasks).
5. Deploy `ontology/snowflake_cortex_semantic_model.yaml` to Snowflake Cortex Analyst.

---

## 🌟 Key Features
- **100% Governed Semantic Views**: Queries strictly access verified Gold views with zero SQL injection risk.
- **Cross-Persona Reconciliation**: Reconciles Planning, Procurement, Logistics, and Finance to identical canonical numbers.
- **Tariff Landed Cost Optimizer**: Calculates optimal dual-sourcing splits between Asia and nearshore Mexico under Section 301 tariffs.
- **Model Context Protocol (MCP)**: Autonomous dispatch of Jira incidents, Slack alerts, and ERP purchase order expedites.
