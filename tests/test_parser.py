import pandas as pd
from src.parser import parse_log_file

def test_parse_core_log():
    df = parse_log_file("samples/sample_core.log")
    assert not df.empty
    assert all(col in df.columns for col in ["ts", "source", "level", "msg", "latency_ms", "packet_loss"])
    # Vérifie que les latences sont bien float
    assert df["latency_ms"].dtype.kind in "f"
