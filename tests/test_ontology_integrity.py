import os, json
from engine.ontology_engine import ontology_engine
from engine.db_engine import db_engine

def test_ontology_entities_loaded():
    entities = ontology_engine.get_entities()
    assert len(entities) >= 10
    assert "ProductSKU" in entities
    assert "GarmentManufacturer_Tier1" in entities
    assert "ShipmentLogistics" in entities

def test_ontology_relationships_connected():
    rels = ontology_engine.get_relationships()
    assert len(rels) >= 8
    path_info = ontology_engine.find_shortest_path("RawMaterialSupplier_Tier3", "StoreAndChannel")
    assert path_info is not None
    assert path_info['hops'] >= 2

def test_database_tables_and_views_exist():
    tables = [t['name'] for t in db_engine.list_tables()]
    assert "DIM_PRODUCTS" in tables
    assert "DIM_FACTORIES" in tables
    assert "RAW_ERP_PURCHASE_ORDERS" in tables
    assert "VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS" in tables
    assert "VS_GOLD_INVENTORY_LEDGER_METRICS" in tables

def test_gold_view_row_count():
    df = db_engine.execute_query("SELECT COUNT(*) AS total FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS;")
    assert df.iloc[0]['total'] >= 10
