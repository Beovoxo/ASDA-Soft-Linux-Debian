import json
from asda_linux.parameter_store import ParameterStore

def test_json_round_trip(tmp_path):
    store = ParameterStore()
    store.rows = [{"parameter": "P0-00", "name": "Example", "value": "1"}]
    path = tmp_path / "params.json"
    store.save_json(path)

    loaded = ParameterStore()
    loaded.load_json(path)
    assert loaded.rows == store.rows

def test_csv_round_trip(tmp_path):
    store = ParameterStore()
    store.rows = [{"parameter": "P0-00", "name": "Example",
                   "value": "1", "unit": "", "description": "test"}]
    path = tmp_path / "params.csv"
    store.save_csv(path)

    loaded = ParameterStore()
    loaded.load_csv(path)
    assert loaded.rows[0]["parameter"] == "P0-00"
    assert loaded.rows[0]["value"] == "1"
