import pandas as pd
from src.reporter import generate_excel, generate_pdf

def test_generate_excel(tmp_path):
    df = pd.DataFrame({"ts": [1,2], "value": [10,20]})
    top_errors = pd.Series([("ERR", 2)], index=["ERR"])
    spikes = pd.DataFrame({"ts":[1],"latency_ms":[500]})
    out_file = tmp_path / "test.xlsx"
    generate_excel(df, top_errors, spikes, str(out_file))
    assert out_file.exists()

def test_generate_pdf(tmp_path):
    top_errors = {"ERR": 2}
    out_file = tmp_path / "test.pdf"
    generate_pdf("Rapport", top_errors, str(out_file))
    assert out_file.exists()
