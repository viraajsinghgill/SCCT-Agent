---
name: metric-governance-validator
description: "Reconcile metric divergence across enterprise personas (Planning, Procurement, Logistics, Finance) and validate zero mathematical variance using governed semantic layers."
version: 1.0.0
tags:
  - snowflake
  - metric-governance
  - reconciliation
  - cross-persona
---

# Metric Governance & Cross-Persona Reconciliation Skill

## Overview
When enterprise teams consult siloed operational systems, identical business metrics (e.g. On-Time Delivery, Landed Cost, Days of Inventory) yield conflicting answers. This skill reconciles cross-persona discrepancies and proves mathematical equality through governed semantic definitions.

## Reconciliation Protocol
1. **Identify Grain & Timestamp Anchors**:
   - **Planning**: Historically measured against Customer Requested Date without carrier defect tracking.
   - **Procurement**: Historically measured against Factory Ex-Works PO Confirmation SLA.
   - **Logistics**: Historically measured against Carrier Port Arrival Notice.
   - **Canonical Resolution**: Canonical OTD resolves strictly to **Destination Receipt on or before Promised Date with Zero QA Defects**.
2. **Enforce Absorbed Landed Cost**:
   $$\text{Canonical Landed Cost} = \text{Unit FOB Price} + \text{Allocated Freight} + \text{Customs Tariff Duties} + \text{Drayage/Handling}$$
3. **Automated Regression Verification**:
   - Execute side-by-side reconciliation tests to confirm that all personas resolve to zero variance when querying the governed Gold layer.
