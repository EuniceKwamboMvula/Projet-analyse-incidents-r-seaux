# Utiliser une image Python officielle
FROM python:3.10-slim

# Créer le dossier de l'application
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY samples/ ./samples/
COPY config.yml ./src/config.yml

# Définir le point d'entrée
ENTRYPOINT ["python", "src/run_weekly_report.py"]
