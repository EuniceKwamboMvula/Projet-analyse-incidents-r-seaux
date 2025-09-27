# Analyse automatique des incidents réseau


## Description
Outil pour ingérer des logs (Core, Transmission, IP), détecter patterns d'incidents (erreurs fréquentes, pics de latence, pertes de paquets) et générer un rapport hebdomadaire en PDF et Excel.


## Structure du repo
projet-analyse-incidents-reseau/
├── README.md
├── requirements.txt
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── logstash/
│ └── logstash.conf
├── elasticsearch/
│ └── index_template.json
├── kibana/
│ └── README_KIBANA.md
├── src/
│ ├── __init__.py
│ ├── config.yml
│ ├── parser.py
│ ├── analyzer.py
│ ├── reporter.py
│ ├── elastic_client.py
│ ├── utils.py
│ └── run_weekly_report.py
├── samples/
│ ├── sample_core.log
│ ├── sample_transmission.log
│ └── sample_ip.log
├── reports/
│ └── (générés: weekly_report_YYYYMMDD.pdf / .xlsx)
├── notebooks/
│ └── exploration.ipynb
├── tests/
│ ├── test_parser.py
│ ├── test_analyzer.py
│ └── test_reporter.py
└── .github/
└── workflows/
└── ci.yml


## Prérequis
- Docker & docker-compose
- Python 3.9+


## Installation rapide (dev)
1. Copier `.env.example` -> `.env` et ajuster si besoin.
2. Lancer ELK pour dev : `docker-compose up -d`.
3. Créer un venv : `python -m venv .venv && source .venv/bin/activate`
4. Installer dépendances : `pip install -r requirements.txt`
5. Exécuter le parser localement ou envoyer les logs à Logstash.


## Usage
- Parser local : `python src/run_weekly_report.py --input-dir samples/ --output-dir reports/ --mode local`
- Mode ELK : pousser logs vers Logstash, utiliser Kibana pour dashboards, puis exécuter le reporter en mode `elk`.


## Rapport
Le rapport hebdomadaire contient : résumé exécutif, incidents critiques, timeline de trafic/latence, top 10 erreurs, recommandations.


## CI
Tests unitaires via GitHub Actions (.github/workflows/ci.yml)


## Licence
MIT