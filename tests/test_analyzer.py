import pandas as pd
from src.analyzer import detect_frequent_errors, detect_latency_spikes, detect_packet_loss

def make_sample_df():
    data = {
        "ts": pd.date_range("2025-09-20", periods=5, freq="T"),
        "source": ["CORE"]*5,
        "level": ["ERROR", "INFO", "ERROR", "WARN", "ERROR"],
        "msg": ["err1", "ok", "err2", "warn", "err1"],
        "latency_ms": [100, 50, 300, 150, 500],
        "packet_loss": [0.5, 0, 2, 0, 5]
    }
    return pd.DataFrame(data)

def test_detect_frequent_errors():
    df = make_sample_df()
    top = detect_frequent_errors(df, top_n=2)
    assert "err1" in top.index

def test_detect_latency_spikes():
    df = make_sample_df()
    spikes = detect_latency_spikes(df, threshold_ms=200)
    assert len(spikes) == 2

def test_detect_packet_loss():
    df = make_sample_df()
    losses = detect_packet_loss(df, threshold_pct=1.0)
    assert len(losses) == 2
