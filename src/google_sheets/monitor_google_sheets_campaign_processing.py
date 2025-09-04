import pandas as pd
import sys
import os

# Agregar el directorio de google_ads al path para importar sus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'google_ads')))

from google_sheets_manager import get_google_sheets_data, update_google_sheets_entry
from google_ads_manager import get_campaign_details

def monitor_google_sheets():
    """Monitorea Google Sheets y actualiza todos los detalles de la campaña cuando Validation Status es 'Campaign Processing'."""
    print("Checking Google Sheets for campaign processing updates...")

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

        # Mostrar en consola los datos de la fila actual
        print(f"Row {index}: Number={number}, Validation Status={validation_status}, Customer ID={customer_id}, Campaign Name={campaign_name}, Requested Budget={requested_budget}")

        # Verificar si la fila cumple con los criterios para actualizar datos de la campaña
        if number and customer_id and campaign_name and requested_budget and validation_status.lower() == "campaign processing":
            print(f"Retrieving campaign details for Customer ID: {customer_id}, Campaign Name: {campaign_name}")
            
            # Obtener detalles de la campaña desde Google Ads
            campaign_data = get_campaign_details(customer_id, campaign_name)
            
            if campaign_data:
                update_google_sheets_entry(campaign_name, "Campaign ID", campaign_data.get("Campaign ID"))
                update_google_sheets_entry(campaign_name, "Assigned Budget", campaign_data.get("Assigned Budget (Bs)"))
                update_google_sheets_entry(campaign_name, "Campaign Status", campaign_data.get("Status"))
                update_google_sheets_entry(campaign_name, "Total Spend (BOB)", (campaign_data.get("Assigned Budget (Bs)") * ((pd.to_datetime(campaign_data.get("End Date")) - pd.to_datetime(campaign_data.get("Start Date"))).days + 1)))
                update_google_sheets_entry(campaign_name, "Start Date", campaign_data.get("Start Date"))
                update_google_sheets_entry(campaign_name, "End Date", campaign_data.get("End Date"))
                update_google_sheets_entry(campaign_name, "Validation Status", "Campaign Ready")
                print(f"Updated Google Sheets with campaign details for {campaign_name}")
            else:
                print(f"Failed to retrieve campaign details for {campaign_name}")

if __name__ == "__main__":
    monitor_google_sheets()




'''
python src/google_sheets/monitor_google_sheets_campaign_processing.py




import time
import pandas as pd
import sys
import os

# Agregar el directorio de google_ads al path para importar sus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'google_ads')))

from google_sheets_manager import get_google_sheets_data, update_google_sheets_entry
from google_ads_manager import get_campaign_details

# Intervalo de verificación en segundos
CHECK_INTERVAL = 30

def monitor_google_sheets():
    """Monitorea Google Sheets y actualiza todos los detalles de la campaña cuando Validation Status es 'Campaign Processing'."""
    while True:
        print("Checking Google Sheets for campaign processing updates...")
        
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

            # Mostrar en consola los datos de la fila actual
            print(f"Row {index}: Number={number}, Validation Status={validation_status}, Customer ID={customer_id}, Campaign Name={campaign_name}, Requested Budget={requested_budget}")

            # Verificar si la fila cumple con los criterios para actualizar datos de la campaña
            if number and customer_id and campaign_name and requested_budget and validation_status.lower() == "campaign processing":
                print(f"Retrieving campaign details for Customer ID: {customer_id}, Campaign Name: {campaign_name}")
                
                # Obtener detalles de la campaña desde Google Ads
                campaign_data = get_campaign_details(customer_id, campaign_name)
                
                if campaign_data:
                    update_google_sheets_entry(campaign_name, "Campaign ID", campaign_data.get("Campaign ID"))
                    update_google_sheets_entry(campaign_name, "Assigned Budget", campaign_data.get("Assigned Budget (Bs)"))
                    update_google_sheets_entry(campaign_name, "Campaign Status", campaign_data.get("Status"))
                    update_google_sheets_entry(campaign_name, "Total Spend (BOB)", (campaign_data.get("Assigned Budget (Bs)") * ((pd.to_datetime(campaign_data.get("End Date")) - pd.to_datetime(campaign_data.get("Start Date"))).days + 1)))
                    update_google_sheets_entry(campaign_name, "Start Date", campaign_data.get("Start Date"))
                    update_google_sheets_entry(campaign_name, "End Date", campaign_data.get("End Date"))
                    update_google_sheets_entry(campaign_name, "Validation Status", "Campaign Ready")
                    print(f"✅ Updated Google Sheets with campaign details for {campaign_name}")
                else:
                    print(f"❌ Failed to retrieve campaign details for {campaign_name}")

        # Esperar antes de volver a revisar la hoja de cálculo
        print(f"Waiting {CHECK_INTERVAL} seconds before next check...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_google_sheets()

'''
