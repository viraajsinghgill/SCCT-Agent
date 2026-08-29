import os, json

def generate_documents():
    docs_dir = os.path.join(os.path.dirname(__file__), 'contracts')
    os.makedirs(docs_dir, exist_ok=True)
    
    docs = [
        {
            'doc_id': 'DOC-MSA-MAS-001',
            'title': "Master Sourcing Agreement: MAS Holdings Active Fab & Victoria's Secret & Co.",
            'category': 'Vendor Contract & SLA',
            'supplier': 'MAS Holdings Active Fab (Sri Lanka)',
            'effective_date': '2024-01-01',
            'key_clauses': {
                'lead_time_sla': 'Standard production lead time is strictly 45 business days from Purchase Order confirmation.',
                'otd_target': 'Contractual minimum On-Time In-Full (OTIF) delivery requirement is 95.0%.',
                'penalty_terms': 'If OTD falls below 90.0% in any calendar quarter, Supplier shall credit VS&Co 2.5% of total quarterly invoice value. If OTD drops below 85.0%, Supplier shall pay expedited air-freight differential in full.',
                'force_majeure': 'Monsoons and Colombo port strikes exceeding 5 consecutive days require 48-hour formal notification.',
                'esg_compliance': 'Mandatory OEKO-TEX Standard 100 Class II compliance on all intimate apparel fabrics.'
            },
            'content': """# MASTER SOURCING AGREEMENT (MSA-VS-MAS-2024)
**Buyer:** Victoria's Secret & Co. (Reynoldsburg, OH)
**Supplier:** MAS Holdings Active Fab (Colombo, Sri Lanka)

## Section 4: Performance Service Level Agreement (SLA)
1. **On-Time Delivery (OTD):** Supplier covenants to achieve minimum 95.0% On-Time Delivery measured at Port of Savannah destination receipt against customer promised date.
2. **Quality & Defect Acceptance:** Critical defect rate shall not exceed 0.00% (Zero Tolerance for broken needles/metal contaminants). Major defect AQL is 1.5.
3. **Liquidated Damages & Penalties:** 
   - A drop below 90% OTD triggers an automatic 2.5% rebate on all delayed lots.
   - For delays exceeding 14 calendar days during peak Semi-Annual Sale promotional windows, MAS Holdings shall fund 100% of expedited air-freight via FedEx/Emirates SkyCargo.

## Section 7: Material Compliance & OEKO-TEX Certification
All synthetic laces, microfibers, and Lycra blends must hold active OEKO-TEX Standard 100 Annex 6 certification and comply with California Proposition 65 without exception.
"""
        },
        {
            'doc_id': 'DOC-MSA-CRY-002',
            'title': "Master Manufacturing Agreement: Crystal International Vietnam & Victoria's Secret & Co.",
            'category': 'Vendor Contract & SLA',
            'supplier': 'Crystal International Vietnam Ltd',
            'effective_date': '2024-03-15',
            'key_clauses': {
                'lead_time_sla': '38 calendar days standard cut-and-sew cycle.',
                'otd_target': '96.0% On-Time Delivery threshold.',
                'penalty_terms': 'Late delivery penalty of 1.0% per week of delay up to a cap of 10% of PO FOB value.',
                'tariffs_duties': 'Goods subject to Section 301 and standard US Harmonized Tariff Schedule (HTS Code 6212.10 - Brassieres). Tariff fluctuations beyond +/- 5% trigger bilateral pricing renegotiation.'
            },
            'content': """# MASTER MANUFACTURING AGREEMENT (MMA-VS-CRY-2024)
**Buyer:** Victoria's Secret & Co.
**Manufacturer:** Crystal International Vietnam Ltd (Haiphong, Vietnam)

## Article 5: Delivery & Liquidated Damages
- **Promised Delivery Date:** Crystal International must acknowledge POs within 72 hours.
- **Section 301 Tariff Adjustments:** In the event of changes to US tariff schedules on Vietnamese apparel exports, landed cost variance will be shared 50/50 between Buyer and Manufacturer.
- **Expedite Protocol:** If production bottlenecks threaten Holiday Season stock arrival at Long Beach Gateway RDC, Crystal International shall allocate overtime shifts at its own expense.
"""
        },
        {
            'doc_id': 'DOC-SOP-REVERSE-003',
            'title': "Global Reverse Logistics Standard Operating Procedure: Intimates & Apparel Restock Grading",
            'category': 'Operational SOP',
            'supplier': "Victoria's Secret Supply Chain Operations",
            'effective_date': '2024-06-01',
            'key_clauses': {
                'hygienic_inspection': 'Bras and sleepwear with original tags and hygiene liners intact qualify for Grade A Sellable Restock.',
                'quarantine_liquidation': 'Items with missing tags, minor wrinkles, or opened packaging are routed to Grade B Liquidation/Outlet channels.',
                'mandatory_destruction': 'Panties and opened swimwear without intact sanitary strips must be destroyed immediately for consumer safety compliance.'
            },
            'content': """# REVERSE LOGISTICS STANDARD OPERATING PROCEDURE (SOP-RL-2024-08)
**Scope:** North American Regional Distribution Centers (Columbus, Ontario, Atlanta, Toronto)

## 1. Hygienic Grading Protocol
- **Grade A (Sellable Restock):** Tags attached, hygiene liner intact, no perfume/deodorant residue. Automated return to sellable inventory within 24 hours.
- **Grade B (Liquidation / Off-Price):** Intact structure but minor cosmetic packaging defect. Rerouted to Columbus Outlet liquidation sorting.
- **Grade C (Immediate Destruction):** Compromised sanitary hygiene seal on intimate bottoms. Automated disposal manifest generation.
"""
        },
        {
            'doc_id': 'DOC-ALERT-LGB-004',
            'title': "Port of Long Beach / Los Angeles Congestion & Intermodal Rail Advisory",
            'category': 'Supply Chain Disruption Incident Report',
            'supplier': "Logistics Control Tower Operations",
            'effective_date': '2025-08-15',
            'key_clauses': {
                'congestion_delay': 'Average container vessel dwell time increased to 6.8 days at Long Beach Berth 400.',
                'mitigation_plan': 'Reroute 30% of Southeast Asia volume through Suez/Panama to Port of Savannah; activate Union Pacific Priority Intermodal block-trains to Columbus Central RDC.'
            },
            'content': """# SUPPLY CHAIN DISRUPTION ADVISORY: WEST COAST CONTAINER DWELL
**Incident Ref:** DISR-2025-LGB-09
**Impacted Lanes:** Haiphong -> Long Beach, Colombo -> Long Beach

**Summary:**
Due to high peak-season container arrivals, dwell times at Port of Long Beach container terminals have risen from 2.1 days to 6.8 days.
**Recommended Operational Actions:**
1. Invoke Carrier SCAC Priority Dwell agreements with Maersk and MSC.
2. Divert urgent holiday SKU shipments (Dream Angels Bra, Satin Pajama Sets) to air expedite via FedEx Trade Logistics.
3. Accelerate Mexico nearshore production runs at Tegra Global to cushion Midwest RDC inventory buffers.
"""
        }
    ]

    for doc in docs:
        filepath = os.path.join(docs_dir, f"{doc['doc_id']}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=2)

    print(f"Generated {len(docs)} sample contracts and SOP documents in {docs_dir}")

if __name__ == '__main__':
    generate_documents()
