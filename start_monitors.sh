#!/bin/bash

# Cambia al directorio correcto antes de ejecutar los scripts
cd /app || exit

# Ejecuta cada script con la ruta absoluta
python3 /app/src/google_sheets/monitor_google_sheets_incomplete.py
python3 /app/src/google_sheets/monitor_google_sheets_campaign_processing.py
python3 /app/src/google_sheets/monitor_google_sheets_campaign_ready.py
python3 /app/src/google_sheets/monitor_google_sheets_ad_processing.py
