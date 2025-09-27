"""Script d'orchestration: lit un répertoire de logs, parse, analyse, produit rapports.
Ex: python src/run_weekly_report.py --input-dir samples/ --output-dir reports/ --mode local


Fonctionnalités ajoutées :
- mode `local` (lecture des fichiers .log dans un dossier)
- mode `elk` (requête vers Elasticsearch pour récupérer les logs)
- arguments pour filtre date (from/to), seuils d'alerte, nom d'index ES
- logging, gestion d'erreurs, bulk operations minimales
"""
import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd


# Importer les modules du projet
from src.parser import parse_log_file
from src.analyzer import (
    detect_frequent_errors,
    detect_latency_spikes,
    detect_packet_loss,
    summarize_time_series,
)
from src.reporter import generate_excel, generate_pdf

# Importer ESClient si disponible
try:
    from src.elastic_client import ESClient
except Exception:
    ESClient = None

LOG = logging.getLogger("run_weekly_report")

def load_config(path: str = "src/config.yml") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return yaml.safe_load(f)

def read_logs_from_dir(input_dir: Path) -> pd.DataFrame:
    dfs = []
    for f in sorted(input_dir.glob("*.log")):
        try:
            df = parse_log_file(str(f))
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            LOG.warning("Erreur en parsant %s: %s", f, e)
    if not dfs:
        return pd.DataFrame(columns=["ts", "source", "level", "msg", "latency_ms", "packet_loss"]) 
    return pd.concat(dfs, ignore_index=True)

def read_logs_from_es(es_client: ESClient, index: str, start_ts: str = None, end_ts: str = None) -> pd.DataFrame:
    q = {"bool": {"must": []}}
    if start_ts or end_ts:
        range_q = {"range": {"ts": {}}}
        if start_ts:
            range_q["range"]["ts"]["gte"] = start_ts
        if end_ts:
            range_q["range"]["ts"]["lte"] = end_ts
        q["bool"]["must"].append(range_q)

    try:
        res = es_client.es.search(index=index, query=q, size=10000)
        hits = res.get("hits", {}).get("hits", [])
        records = [h.get("_source", {}) for h in hits]
        if not records:
            return pd.DataFrame(columns=["ts", "source", "level", "msg", "latency_ms", "packet_loss"]) 
        df = pd.DataFrame(records)
        for c in ["ts", "source", "level", "msg", "latency_ms", "packet_loss"]:
            if c not in df.columns:
                df[c] = None
        return df[["ts", "source", "level", "msg", "latency_ms", "packet_loss"]]
    except Exception as e:
        LOG.exception("Erreur lors de la lecture depuis ES: %s", e)
        return pd.DataFrame(columns=["ts", "source", "level", "msg", "latency_ms", "packet_loss"]) 

def parse_date(s: str):
    if s is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format de date non supporté: {s}")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Génère un rapport hebdomadaire d'incidents réseau")
    parser.add_argument("--input-dir", help="Répertoire contenant les fichiers .log (mode local)")
    parser.add_argument("--output-dir", required=True, help="Répertoire de sortie pour rapports")
    parser.add_argument("--mode", choices=["local", "elk"], default="local")
    parser.add_argument("--config", default="src/config.yml")
    parser.add_argument("--es-index", default=None, help="Index pattern ES (ex: network-logs-*)")
    parser.add_argument("--start", help="Date/heure de début (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--end", help="Date/heure de fin (YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--latency-threshold", type=float, default=200.0, help="Seuil latence (ms) pour détecter spikes")
    parser.add_argument("--loss-threshold", type=float, default=1.0, help="Seuil perte paquets (%) pour alertes")
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    LOG.info("Mode: %s", args.mode)
    if args.mode == "local":
        if not args.input_dir:
            LOG.error("--input-dir est requis en mode local")
            return
        in_dir = Path(args.input_dir)
        if not in_dir.exists():
            LOG.error("Répertoire d'entrée introuvable: %s", in_dir)
            return
        df_all = read_logs_from_dir(in_dir)
    else:
        es_cfg_host = cfg.get("elk", {}).get("host", "http://localhost:9200")
        if ESClient is None:
            LOG.error("ESClient non disponible. Assurez-vous que src/elastic_client.py existe et elasticsearch lib est installée.")
            return
        es_client = ESClient(host=es_cfg_host)
        index = args.es_index or cfg.get("elk", {}).get("index_prefix", "network-logs-*")
        start = args.start
        end = args.end
        df_all = read_logs_from_es(es_client, index, start, end)

    if df_all.empty:
        LOG.warning("Aucun événement trouvé pour la période donnée. Fin.")
        return

    df_all["ts"] = pd.to_datetime(df_all["ts"], errors="coerce")
    df_all = df_all.sort_values("ts")

    if args.start:
        start_dt = parse_date(args.start)
        df_all = df_all[df_all["ts"] >= start_dt]
    if args.end:
        end_dt = parse_date(args.end)
        df_all = df_all[df_all["ts"] <= end_dt]

    if df_all.empty:
        LOG.warning("Après application des filtres, aucun événement restant.")
        return

    LOG.info("Détection des erreurs fréquentes...")
    top_errors = detect_frequent_errors(df_all, top_n=20)

    LOG.info("Détection des pics de latence (>%sms)...", args.latency_threshold)
    spikes = detect_latency_spikes(df_all, threshold_ms=args.latency_threshold)

    LOG.info("Détection des pertes de paquets (>%s%%)...", args.loss_threshold)
    losses = detect_packet_loss(df_all, threshold_pct=args.loss_threshold)

    LOG.info("Synthèse temporelle...")
    timeseries = summarize_time_series(df_all, freq="1H")

    stamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    excel_path = str(out_dir / f"weekly_report_{stamp}.xlsx")
    pdf_path = str(out_dir / f"weekly_report_{stamp}.pdf")

    try:
        LOG.info("Génération du fichier Excel : %s", excel_path)
        generate_excel(timeseries, top_errors, spikes, excel_path)
    except Exception:
        LOG.exception("Erreur lors de la génération Excel")

    try:
        LOG.info("Génération du fichier PDF : %s", pdf_path)
        generate_pdf(
            "Rapport automatique — incidents réseau",
            top_errors.to_dict() if hasattr(top_errors, "to_dict") else dict(top_errors),
            pdf_path
        )
    except Exception:
        LOG.exception("Erreur lors de la génération PDF")

    LOG.info("Rapport terminé. Résumé:")
    LOG.info("- Nombre total d'événements: %s", len(df_all))
    LOG.info("- Top erreurs (extrait):\n%s", top_errors.head(10))
    LOG.info("- Nombre de spikes détectés: %s", len(spikes))
    LOG.info("- Nombre d'événements avec pertes: %s", len(losses))
    LOG.info("Fichiers générés: %s, %s", excel_path, pdf_path)

if __name__ == "__main__":
    main()
