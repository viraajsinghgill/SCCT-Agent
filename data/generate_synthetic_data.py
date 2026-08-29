import random, datetime, json, os, sqlite3
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

def generate_dataset():
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/contracts', exist_ok=True)

    products = [
        {'sku_id': 'VS-BRA-001', 'sku_name': 'Dream Angels Wicked Unlined Bra', 'brand': "Victoria's Secret", 'category': 'Bras', 'subcategory': 'Unlined', 'unit_standard_cost_usd': 14.50, 'base_msrp_usd': 49.50, 'primary_material': 'Recycled Lace & Nylon'},
        {'sku_id': 'VS-BRA-002', 'sku_name': 'Body by Victoria Smooth Demi Bra', 'brand': "Victoria's Secret", 'category': 'Bras', 'subcategory': 'T-Shirt & Demi', 'unit_standard_cost_usd': 12.80, 'base_msrp_usd': 44.50, 'primary_material': 'Microfiber & Memory Foam'},
        {'sku_id': 'VS-BRA-003', 'sku_name': 'Very Sexy Push-Up Shine Strap Bra', 'brand': "Victoria's Secret", 'category': 'Bras', 'subcategory': 'Push-Up', 'unit_standard_cost_usd': 18.20, 'base_msrp_usd': 69.50, 'primary_material': 'Satin, Rhinestones & Underwire'},
        {'sku_id': 'VS-PAN-101', 'sku_name': 'Cotton Modal Seamless Hipster Panty', 'brand': "Victoria's Secret", 'category': 'Panties', 'subcategory': 'Hipster', 'unit_standard_cost_usd': 3.20, 'base_msrp_usd': 14.50, 'primary_material': 'Supima Cotton & Modal'},
        {'sku_id': 'VS-PAN-102', 'sku_name': 'Lace-Trim Cheeky Panty 5-Pack', 'brand': "Victoria's Secret", 'category': 'Panties', 'subcategory': 'Cheeky', 'unit_standard_cost_usd': 8.50, 'base_msrp_usd': 35.00, 'primary_material': 'Stretch Lace & Elastane'},
        {'sku_id': 'PK-HOD-201', 'sku_name': 'PINK Everyday Lounge Fleece Hoodie', 'brand': 'PINK', 'category': 'Loungewear', 'subcategory': 'Hoodies & Sweats', 'unit_standard_cost_usd': 16.00, 'base_msrp_usd': 59.95, 'primary_material': 'Organic Cotton Fleece'},
        {'sku_id': 'PK-LEG-202', 'sku_name': 'PINK High-Waist Pocket Workout Legging', 'brand': 'PINK', 'category': 'Activewear', 'subcategory': 'Leggings', 'unit_standard_cost_usd': 13.50, 'base_msrp_usd': 49.95, 'primary_material': 'Recycled Spandex & Polyester'},
        {'sku_id': 'VB-FRG-301', 'sku_name': 'Bombshell Eau de Parfum 100ml', 'brand': 'VS Beauty', 'category': 'Fragrance', 'subcategory': 'Fine Fragrance', 'unit_standard_cost_usd': 11.20, 'base_msrp_usd': 79.95, 'primary_material': 'Glass Flacon & Essential Oils'},
        {'sku_id': 'VB-MST-302', 'sku_name': 'Bare Vanilla Shimmer Fragrance Mist', 'brand': 'VS Beauty', 'category': 'Beauty', 'subcategory': 'Body Mist', 'unit_standard_cost_usd': 2.80, 'base_msrp_usd': 19.95, 'primary_material': 'PET Bottle & Vanilla Extract'},
        {'sku_id': 'VS-SLP-401', 'sku_name': 'Luxe Satin Button-Down Long Pajama Set', 'brand': "Victoria's Secret", 'category': 'Sleepwear', 'subcategory': 'Pajama Sets', 'unit_standard_cost_usd': 21.00, 'base_msrp_usd': 89.50, 'primary_material': '100% Glossy Mulberry Silk/Satin'}
    ]
    df_products = pd.DataFrame(products)

    factories = [
        {'vendor_code': 'VEN-MAS-01', 'factory_name': 'MAS Holdings Active Fab', 'country': 'Sri Lanka', 'region': 'South Asia', 'lead_time_baseline_days': 45, 'labor_audit_score': 96, 'tariff_base_rate_pct': 8.0, 'monthly_capacity_units': 500000},
        {'vendor_code': 'VEN-CRY-02', 'factory_name': 'Crystal International Vietnam Ltd', 'country': 'Vietnam', 'region': 'Southeast Asia', 'lead_time_baseline_days': 38, 'labor_audit_score': 92, 'tariff_base_rate_pct': 12.0, 'monthly_capacity_units': 750000},
        {'vendor_code': 'VEN-TEG-03', 'factory_name': 'Tegra Global Nearshore Plant', 'country': 'Mexico', 'region': 'North America', 'lead_time_baseline_days': 14, 'labor_audit_score': 89, 'tariff_base_rate_pct': 0.0, 'monthly_capacity_units': 300000},
        {'vendor_code': 'VEN-BDX-04', 'factory_name': 'Brandix Apparel Eco-Campus', 'country': 'India', 'region': 'South Asia', 'lead_time_baseline_days': 50, 'labor_audit_score': 94, 'tariff_base_rate_pct': 10.0, 'monthly_capacity_units': 400000},
        {'vendor_code': 'VEN-SRI-05', 'factory_name': 'PT Sritex Intimates Indonesia', 'country': 'Indonesia', 'region': 'Southeast Asia', 'lead_time_baseline_days': 42, 'labor_audit_score': 90, 'tariff_base_rate_pct': 11.5, 'monthly_capacity_units': 350000}
    ]
    df_factories = pd.DataFrame(factories)

    mills = [
        {'mill_code': 'MIL-FOR-01', 'mill_name': 'Formosa Taffeta Tech Mills', 'country': 'Taiwan', 'material_type': 'Recycled Polyamide & Microfiber', 'reach_compliant': 'YES', 'oeko_tex_status': 'CERTIFIED'},
        {'mill_code': 'MIL-TOR-02', 'mill_name': 'Toray Advanced Textile Mills', 'country': 'Japan', 'material_type': 'High-Elongation Spandex Mesh', 'reach_compliant': 'YES', 'oeko_tex_status': 'CERTIFIED'},
        {'mill_code': 'MIL-OCN-03', 'mill_name': 'Ocean Lanka Knitting Mills', 'country': 'Sri Lanka', 'material_type': 'Organic Cotton Single Jersey', 'reach_compliant': 'YES', 'oeko_tex_status': 'CERTIFIED'},
        {'mill_code': 'MIL-PAC-04', 'mill_name': 'Pacific Textiles Ltd', 'country': 'China', 'material_type': 'Jacquard Stretch Lace & Satin', 'reach_compliant': 'YES', 'oeko_tex_status': 'CERTIFIED'}
    ]
    df_mills = pd.DataFrame(mills)

    raw_suppliers = [
        {'supplier_id': 'RAW-SUP-01', 'supplier_name': 'Supima Cotton Growers Guild', 'country': 'USA', 'raw_material': 'Extra-Long Staple Supima Cotton', 'gots_certified': 'YES'},
        {'supplier_id': 'RAW-SUP-02', 'supplier_name': 'Asahi Kasei Fibers Corp', 'country': 'Japan', 'raw_material': 'Roica Recycled Elastane', 'gots_certified': 'NO'},
        {'supplier_id': 'RAW-SUP-03', 'supplier_name': 'Lenzing AG Austria', 'country': 'Austria', 'raw_material': 'TENCEL MicroModal Fibers', 'gots_certified': 'YES'},
        {'supplier_id': 'RAW-SUP-04', 'supplier_name': 'Huntsman Textile Chemicals', 'country': 'USA', 'raw_material': 'AVITERA Eco-Dyes & Finishes', 'gots_certified': 'YES'}
    ]
    df_raw_suppliers = pd.DataFrame(raw_suppliers)

    rdcs = [
        {'rdc_code': 'RDC-COL-01', 'rdc_name': 'Columbus Central Omnichannel DC', 'city': 'Columbus', 'state': 'OH', 'capacity_units': 15000000, 'region': 'Midwest'},
        {'rdc_code': 'RDC-ONT-02', 'rdc_name': 'Inland Empire Gateway DC', 'city': 'Ontario', 'state': 'CA', 'capacity_units': 10000000, 'region': 'West Coast'},
        {'rdc_code': 'RDC-ATL-03', 'rdc_name': 'Southeast Regional Logistics Hub', 'city': 'Atlanta', 'state': 'GA', 'capacity_units': 8000000, 'region': 'Southeast'},
        {'rdc_code': 'RDC-TOR-04', 'rdc_name': 'Greater Toronto Distribution Center', 'city': 'Mississauga', 'state': 'ON', 'capacity_units': 5000000, 'region': 'Canada'}
    ]
    df_rdcs = pd.DataFrame(rdcs)

    start_date = datetime.date(2025, 1, 1)
    carriers = ['Maersk Ocean Line', 'MSC Mediterranean', 'Hapag-Lloyd', 'FedEx Trade Logistics', 'Hub Group Intermodal', 'CH Robinson']
    ports_map = {
        'Sri Lanka': ('Port of Colombo', 'Port of Savannah'),
        'Vietnam': ('Port of Haiphong', 'Port of Long Beach'),
        'Mexico': ('Laredo Border Cross', 'Columbus Rail Ramp'),
        'India': ('Nhava Sheva Port', 'Port of New York/NJ'),
        'Indonesia': ('Tanjung Priok Port', 'Port of Long Beach')
    }

    pos, shipments, inspections, omni_orders, customer_returns = [], [], [], [], []
    po_counter, ship_counter, insp_counter, order_counter, return_counter = 1000, 5000, 8000, 90000, 20000

    for i in range(1200):
        po_counter += 1
        po_number = f"PO-VS-{po_counter}"
        prod = random.choice(products)
        fac = random.choice(factories)
        ordered_units = random.choice([2500, 5000, 7500, 10000, 15000, 20000])
        fob_cost = round(prod['unit_standard_cost_usd'] * random.uniform(0.92, 1.08), 2)
        day_offset = random.randint(0, 360)
        po_date = start_date + datetime.timedelta(days=day_offset)
        factory_ack_date = po_date + datetime.timedelta(days=random.randint(2, 4))
        actual_lead_time = max(8, int(np.random.normal(fac['lead_time_baseline_days'], 3)))
        ex_factory_date = po_date + datetime.timedelta(days=actual_lead_time)
        po_status = 'COMPLETED' if (datetime.date(2026, 2, 1) - ex_factory_date).days > 30 else random.choice(['IN_PRODUCTION', 'IN_TRANSIT', 'COMPLETED'])

        pos.append({
            'po_number': po_number,
            'po_line_num': 1,
            'sku_id': prod['sku_id'],
            'vendor_code': fac['vendor_code'],
            'factory_site_code': fac['vendor_code'] + '-PLANT',
            'ordered_qty': ordered_units,
            'unit_price_raw': f"${fob_cost:.2f}",
            'currency': 'USD',
            'po_creation_timestamp': str(po_date),
            'vendor_ack_date': str(factory_ack_date),
            'target_ex_factory_date': str(po_date + datetime.timedelta(days=fac['lead_time_baseline_days'])),
            'raw_status': po_status
        })

        ship_counter += 1
        shipment_id = f"SHP-VS-{ship_counter}"
        origin_p, dest_p = ports_map[fac['country']]
        rdc = random.choice(df_rdcs.to_dict('records'))
        carrier = random.choice(carriers)
        mode = 'TRUCK_RAIL' if fac['country'] == 'Mexico' else ('AIR_EXPEDITE' if random.random() < 0.08 else 'OCEAN_FCL')
        transit_days = 4 if mode == 'AIR_EXPEDITE' else (7 if mode == 'TRUCK_RAIL' else random.randint(22, 30))
        atd = ex_factory_date + datetime.timedelta(days=random.randint(1, 2))
        eta = atd + datetime.timedelta(days=transit_days)
        
        is_delayed = random.random() < 0.06
        delay_days = random.randint(4, 8) if is_delayed else 0
        ata = eta + datetime.timedelta(days=delay_days)
        
        freight_per_unit = 0.45 if mode == 'OCEAN_FCL' else (2.80 if mode == 'AIR_EXPEDITE' else 0.65)
        freight_total = round(ordered_units * freight_per_unit * random.uniform(0.95, 1.05), 2)
        iot_temp = round(random.gauss(21.0, 3.0), 1)
        iot_shock = round(float(np.random.exponential(0.4)), 2)
        if prod['category'] == 'Fragrance' and random.random() < 0.03:
            iot_temp = round(random.choice([38.5, 41.2, 2.1]), 1)

        shipments.append({
            'shipment_raw_id': shipment_id,
            'container_num': f"MSCU-{random.randint(100000, 999999)}",
            'bill_of_lading': f"BOL-VS-{random.randint(2000000, 8999999)}",
            'po_number': po_number,
            'carrier_scac': carrier,
            'origin_port': origin_p,
            'dest_port': dest_p,
            'dest_rdc_code': rdc['rdc_name'],
            'mode': mode,
            'etd_date': str(ex_factory_date),
            'atd_date': str(atd),
            'eta_date': str(eta),
            'ata_date': str(ata),
            'freight_charge_raw': f"${freight_total:.2f}",
            'iot_temp_celsius': iot_temp,
            'iot_shock_g_force': iot_shock
        })

        insp_counter += 1
        qa_pass = random.random() > 0.02
        crit_defects = 0 if qa_pass else 1
        maj_defects = 0 if qa_pass else random.randint(2, 4)
        inspections.append({
            'inspection_id': f"QA-INS-{insp_counter}",
            'batch_lot_number': f"LOT-{po_number}-B1",
            'vendor_code': fac['vendor_code'],
            'fabric_mill_code': random.choice(mills)['mill_code'],
            'sku_id': prod['sku_id'],
            'po_number': po_number,
            'oeko_tex_cert_id': f"OEKO-TEX-STD100-{random.randint(10000, 99999)}",
            'gots_cert_id': f"GOTS-ORG-{random.randint(2000, 9999)}",
            'reach_chemical_test': 'PASS',
            'colorfastness_score': round(random.uniform(4.5, 5.0), 1),
            'dimensional_shrinkage_pct': round(random.uniform(1.2, 2.5), 2),
            'tensile_strength_n': round(random.uniform(460, 580), 1),
            'inspection_verdict': 'PASSED' if qa_pass else 'REJECTED_QUARANTINE',
            'defect_critical_count': crit_defects,
            'defect_major_count': maj_defects,
            'inspection_timestamp': str(ex_factory_date)
        })

        order_counter += 1
        order_id = f"ORD-OMNI-{order_counter}"
        channel = random.choice(['RETAIL_STORES_NORTH_AMERICA', 'E_COMMERCE_DIRECT', 'OUTLET_STORES'])
        promised_delivery = eta + datetime.timedelta(days=4)
        actual_delivered = ata + datetime.timedelta(days=4)
        units_fulfilled = ordered_units if qa_pass else int(ordered_units * 0.95)

        omni_orders.append({
            'order_id': order_id,
            'po_number': po_number,
            'channel_code': channel,
            'customer_id': f"CUST-{random.randint(10000, 99999)}",
            'sku_id': prod['sku_id'],
            'units_ordered': ordered_units,
            'units_fulfilled': units_fulfilled,
            'order_placed_ts': str(po_date),
            'promised_delivery_ts': str(promised_delivery),
            'actual_delivery_ts': str(actual_delivered),
            'order_status': 'DELIVERED'
        })

        if random.random() < 0.20:
            return_counter += 1
            ret_reason = random.choice(['WRONG_SIZE_FIT', 'FABRIC_FEEL_TEXTURE', 'COLOR_NOT_AS_EXPECTED', 'CHANGED_MIND', 'MINOR_STITCH_DEFECT'])
            hygiene = 'GRADE_A_PRISTINE' if ret_reason in ['CHANGED_MIND', 'WRONG_SIZE_FIT'] and random.random() > 0.15 else random.choice(['GRADE_B_MINOR_WRINKLE', 'GRADE_C_HYGIENIC_FLAG'])
            disposition = 'SELLABLE_RESTOCK' if hygiene == 'GRADE_A_PRISTINE' else ('LIQUIDATION' if hygiene == 'GRADE_B_MINOR_WRINKLE' else 'DESTROY_HYGIENE')
            customer_returns.append({
                'return_id': f"RET-VS-{return_counter}",
                'order_id': order_id,
                'sku_id': prod['sku_id'],
                'return_request_ts': str(actual_delivered + datetime.timedelta(days=random.randint(3, 21))),
                'return_reason_raw': ret_reason,
                'hygiene_inspection_grade': hygiene,
                'disposition_code': disposition,
                'refund_amount_usd': round(prod['base_msrp_usd'] * random.randint(1, 3), 2)
            })

    inventory_records = []
    inv_id = 7000
    for rdc in df_rdcs.to_dict('records'):
        for prod in products:
            inv_id += 1
            velocity = random.randint(180, 850)
            target_days = random.randint(28, 55)
            on_hand = int(velocity * target_days * random.uniform(0.75, 1.35))
            in_transit = int(velocity * random.randint(10, 25))
            safety_stock = int(velocity * 18)
            inventory_records.append({
                'inventory_id': f"INV-LOC-{inv_id}",
                'rdc_name': rdc['rdc_name'],
                'sku_id': prod['sku_id'],
                'units_on_hand': on_hand,
                'units_in_transit': in_transit,
                'units_allocated': int(on_hand * 0.4),
                'safety_stock_threshold': safety_stock,
                'daily_sales_velocity': velocity,
                'carrying_cost_per_unit': round(prod['unit_standard_cost_usd'] * 0.18 / 365, 4)
            })
    df_inventory = pd.DataFrame(inventory_records)

    db_path = 'data/supply_chain_scct.db'
    conn = sqlite3.connect(db_path)
    df_products.to_sql('DIM_PRODUCTS', conn, if_exists='replace', index=False)
    df_factories.to_sql('DIM_FACTORIES', conn, if_exists='replace', index=False)
    df_mills.to_sql('DIM_FABRIC_MILLS', conn, if_exists='replace', index=False)
    df_raw_suppliers.to_sql('DIM_RAW_SUPPLIERS', conn, if_exists='replace', index=False)
    df_rdcs.to_sql('DIM_RDC', conn, if_exists='replace', index=False)
    pd.DataFrame(pos).to_sql('RAW_ERP_PURCHASE_ORDERS', conn, if_exists='replace', index=False)
    pd.DataFrame(shipments).to_sql('RAW_TMS_SHIPMENTS', conn, if_exists='replace', index=False)
    pd.DataFrame(inspections).to_sql('RAW_QA_INSPECTIONS', conn, if_exists='replace', index=False)
    pd.DataFrame(omni_orders).to_sql('RAW_OMNICHANNEL_ORDERS', conn, if_exists='replace', index=False)
    pd.DataFrame(customer_returns).to_sql('RAW_CUSTOMER_RETURNS', conn, if_exists='replace', index=False)
    df_inventory.to_sql('CNF_INVENTORY_LEDGER', conn, if_exists='replace', index=False)

    conn.execute('DROP VIEW IF EXISTS VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS;')
    conn.execute("""
    CREATE VIEW VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS AS
    SELECT
        po.po_number,
        po.sku_id,
        p.sku_name,
        p.brand,
        p.category,
        p.subcategory,
        f.factory_name,
        f.country AS sourcing_country,
        f.region AS sourcing_region,
        s.carrier_scac AS carrier_name,
        s.mode AS transport_mode,
        s.origin_port,
        s.dest_port,
        s.dest_rdc_code AS rdc_name,
        o.channel_code AS destination_channel,
        po.po_creation_timestamp AS order_date,
        o.promised_delivery_ts AS promised_delivery_date,
        o.actual_delivery_ts AS actual_delivery_date,
        po.ordered_qty AS units_ordered,
        o.units_fulfilled AS units_fulfilled,
        COALESCE(qa.defect_critical_count + qa.defect_major_count, 0) AS defect_count,
        (CASE WHEN s.iot_temp_celsius > 35.0 OR s.iot_temp_celsius < 5.0 OR s.iot_shock_g_force > 3.0 THEN 1 ELSE 0 END) AS is_iot_anomaly,
        CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) AS unit_fob_price_usd,
        (CAST(REPLACE(s.freight_charge_raw, '$', '') AS FLOAT) / CAST(po.ordered_qty AS FLOAT)) AS allocated_freight_usd,
        (CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) AS customs_duty_usd,
        1.25 AS drayage_handling_usd,
        (CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) + 
         (CAST(REPLACE(s.freight_charge_raw, '$', '') AS FLOAT) / CAST(po.ordered_qty AS FLOAT)) + 
         (CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) + 
         1.25) AS unit_landed_cost_usd,
        (CAST(po.ordered_qty AS FLOAT) * (CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) + (CAST(REPLACE(s.freight_charge_raw, '$', '') AS FLOAT) / CAST(po.ordered_qty AS FLOAT)) + (CAST(REPLACE(po.unit_price_raw, '$', '') AS FLOAT) * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) + 1.25)) AS total_landed_cost_usd,
        ROUND((julianday(o.actual_delivery_ts) - julianday(po.po_creation_timestamp)), 1) AS lead_time_days,
        (CASE WHEN f.country = 'Vietnam' THEN 12.0 WHEN f.country = 'Sri Lanka' THEN 8.0 WHEN f.country = 'Mexico' THEN 0.0 ELSE 15.0 END) AS tariff_rate_pct
    FROM RAW_ERP_PURCHASE_ORDERS po
    LEFT JOIN RAW_TMS_SHIPMENTS s ON po.po_number = s.po_number
    LEFT JOIN RAW_OMNICHANNEL_ORDERS o ON po.po_number = o.po_number
    LEFT JOIN RAW_QA_INSPECTIONS qa ON po.po_number = qa.po_number
    LEFT JOIN DIM_FACTORIES f ON po.vendor_code = f.vendor_code
    LEFT JOIN DIM_PRODUCTS p ON po.sku_id = p.sku_id;
    """)

    conn.commit()
    conn.close()
    print(f"Clean dataset generated in {db_path}")

if __name__ == '__main__':
    generate_dataset()
