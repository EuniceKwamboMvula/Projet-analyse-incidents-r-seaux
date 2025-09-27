# Dashboard Kibana pour analyse des incidents réseau

1. Importer l'index pattern `network-logs-*`.
2. Créer un index pattern sur le timestamp `ts`.
3. Créer les visualisations :
   - Histogramme du nombre d'erreurs par heure.
   - Latence moyenne par interface.
   - Perte de paquets par source.
4. Combiner les visualisations dans un dashboard "Incidents Réseau".
5. Sauvegarder et partager le dashboard si nécessaire.
