import subprocess
import sys
import os

# Agregar el directorio de google_ads al path para importar sus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'google_ads')))

from google_sheets_manager import get_google_sheets_data, update_google_sheets_entry

# Mapeo de ciudades a sus códigos de geotargeting de Google Ads
CITY_TO_GEO_ID = {
    "la paz": "20084",
    "cochabamba": "20083",
    "santa cruz": "20085",
    "potosi": "9069868",
    "beni": "9069869",
    "chuquisaca": "9069870",
    "pando": "9069871",
    "oruro": "9069872",
    "tarija": "9075434"
}

# Ciudad por defecto si no se encuentra la segmentación proporcionada
DEFAULT_CITY = "la paz"
DEFAULT_GEO_ID = CITY_TO_GEO_ID[DEFAULT_CITY]

def monitor_google_sheets():
    """Ejecuta una única vez la verificación en Google Sheets y ejecuta add_campaign.py si una fila cumple con los requisitos."""
    print("Checking Google Sheets for campaign updates...")

    # Obtener los datos de la hoja de Google Sheets
    df = get_google_sheets_data()

    # Convertir nombres de columnas a minúsculas y eliminar espacios adicionales
    df.columns = df.columns.str.lower().str.strip()

    for index, row in df.iterrows():
        # Leer los valores de cada fila y limpiar espacios
        number = str(row.get("number", "")).strip()
        validation_status = str(row.get("validation status", "")).strip()
        customer_id = str(row.get("customer id", "")).strip()
        campaign_name = str(row.get("campaign name", "")).strip()
        requested_budget = str(row.get("requested budget", "")).strip()
        segmentation = str(row.get("segmentation", "")).strip().lower()

        # Mostrar en consola los datos de la fila actual
        print(f"Row {index}: Number={number}, Validation Status={validation_status}, Customer ID={customer_id}, Campaign Name={campaign_name}, Requested Budget={requested_budget}, Segmentation={segmentation}")

        # Verificar si la fila cumple con los criterios para ejecutar add_campaign.py
        if number and customer_id and campaign_name and requested_budget and validation_status.lower() == "incomplete":
            geo_id = CITY_TO_GEO_ID.get(segmentation, DEFAULT_GEO_ID)
            segmentation_used = segmentation if segmentation in CITY_TO_GEO_ID else DEFAULT_CITY

            print(f"Creating campaign for Customer ID: {customer_id}, Campaign Name: {campaign_name}, Segmentation: {segmentation_used} (Geo ID: {geo_id})")

            # Ejecutar add_campaign.py y capturar salida
            result = subprocess.run([
                "python", "src/google_ads/add_campaign.py", "-c", customer_id, "-n", campaign_name, "-l", geo_id
            ], capture_output=True, text=True)

            # Mostrar la salida del script add_campaign.py
            print(result.stdout)
            print(result.stderr)

            # Verificar si la campaña se creó correctamente
            if result.returncode == 0:
                update_google_sheets_entry(campaign_name, "Validation Status", "campaign processing")
                print(f"Campaign Processing: {campaign_name}")
            else:
                print(f"Error creating campaign for {campaign_name}")

if __name__ == "__main__":
    monitor_google_sheets()




'''
python src/google_sheets/monitor_google_sheets_incomplete.py


import time
import subprocess
import sys
import os

# Agregar el directorio de google_ads al path para importar sus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'google_ads')))

from google_sheets_manager import get_google_sheets_data, update_google_sheets_entry

# Mapeo de ciudades a sus códigos de geotargeting de Google Ads
CITY_TO_GEO_ID = {
    "la paz": "20084",
    "cochabamba": "20083",
    "santa cruz": "20085",
    "potosí": "9069868",
    "beni": "9069869",
    "chuquisaca": "9069870",
    "pando": "9069871",
    "oruro": "9069872",
    "tarija": "9075434"
}

# Ciudad por defecto si no se encuentra la segmentación proporcionada
DEFAULT_CITY = "la paz"
DEFAULT_GEO_ID = CITY_TO_GEO_ID[DEFAULT_CITY]

# Intervalo de verificación en segundos (por ejemplo, cada 30 segundos)
CHECK_INTERVAL = 30

def monitor_google_sheets():
    """Monitorea Google Sheets y ejecuta add_campaign.py si una fila cumple con los requisitos."""
    while True:
        print("Checking Google Sheets for campaign updates...")
        
        # Obtener los datos de la hoja de Google Sheets
        df = get_google_sheets_data()
        
        # Convertir nombres de columnas a minúsculas y eliminar espacios adicionales
        df.columns = df.columns.str.lower().str.strip()
        
        for index, row in df.iterrows():
            # Leer los valores de cada fila y limpiar espacios
            number = str(row.get("number", "")).strip()
            validation_status = str(row.get("validation status", "")).strip()
            customer_id = str(row.get("customer id", "")).strip()
            campaign_name = str(row.get("campaign name", "")).strip()
            requested_budget = str(row.get("requested budget", "")).strip()
            segmentation = str(row.get("segmentation", "")).strip().lower()

            # Mostrar en consola los datos de la fila actual
            print(f"Row {index}: Number={number}, Validation Status={validation_status}, Customer ID={customer_id}, Campaign Name={campaign_name}, Requested Budget={requested_budget}, Segmentation={segmentation}")

            # Verificar si la fila cumple con los criterios para ejecutar add_campaign.py
            if number and customer_id and campaign_name and requested_budget and validation_status.lower() == "incomplete":
                geo_id = CITY_TO_GEO_ID.get(segmentation, DEFAULT_GEO_ID)
                segmentation_used = segmentation if segmentation in CITY_TO_GEO_ID else DEFAULT_CITY
                
                print(f"Creating campaign for Customer ID: {customer_id}, Campaign Name: {campaign_name}, Segmentation: {segmentation_used} (Geo ID: {geo_id})")
                
                # Ejecutar add_campaign.py y capturar salida
                result = subprocess.run([
                    "python", "src/google_ads/add_campaign.py", "-c", customer_id, "-n", campaign_name, "-l", geo_id
                ], capture_output=True, text=True)
                
                # Mostrar la salida del script add_campaign.py
                print(result.stdout)
                print(result.stderr)
                
                # Verificar si la campaña se creó correctamente
                if result.returncode == 0:
                    update_google_sheets_entry(campaign_name, "Validation Status", "campaign processing")
                    print(f"Campaign Processing: {campaign_name}")
                else:
                    print(f"Error creating campaign for {campaign_name}")

        # Esperar antes de volver a revisar la hoja de cálculo
        print(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_google_sheets()

'''


