import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuración de Google Sheets
SHEET_ID = "16MQ_9loHwG1JGV24oD4Qh8XL8hSUU08ZteTEHW12H1U"
SHEET_NAME = "Interacciones_Reales_v01"  # Asegúrate de que el nombre coincida
CREDENTIALS_FILE = "CredentialsGoogleSheets.json"  # Ruta al archivo de credenciales

# Autenticación con Google Sheets
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def get_google_sheets_data():
    """Obtiene los datos de la hoja de Google Sheets como un DataFrame de Pandas."""
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_google_sheets_entry_by_row(row_index, updates):
    """Actualiza múltiples celdas en una fila específica de Google Sheets."""
    headers = sheet.row_values(1)
    for column_name, new_value in updates.items():
        if column_name in headers:
            column_index = headers.index(column_name) + 1
            try:
                sheet.update_cell(row_index, column_index, new_value)
                print(f"Fila {row_index} actualizada: {column_name} = {new_value}")
            except Exception as e:
                print(f"Error al actualizar la fila {row_index} en Google Sheets: {e}")

def update_google_sheets_entry(campaign_name, column_name, new_value):
    """Modifica una celda específica de una campaña usando el Campaign Name como referencia."""
    df = get_google_sheets_data()
    df.columns = df.columns.str.lower().str.strip()
    row_index = df.index[df["campaign name"].str.lower().str.strip() == campaign_name.lower().strip()].tolist()

    if row_index:
        row_number = row_index[0] + 2  # Ajuste por encabezado
        update_google_sheets_entry_by_row(row_number, {column_name: new_value})
    else:
        print(f"No se encontró la campaña con nombre {campaign_name}.")

def add_new_entry(user_name, number, customer_id, campaign_name, requested_budget, assigned_budget, ad_group_id, ad_group_name, ad_group_status, titles, descriptions, keywords, start_date, end_date, validation_status):
    """Agrega una nueva entrada en Google Sheets con los datos proporcionados."""
    sheet.append_row([user_name, number, customer_id, campaign_name, requested_budget, assigned_budget, ad_group_id, ad_group_name, ad_group_status, titles, descriptions, keywords, start_date, end_date, validation_status])
    print(f"Nueva entrada agregada para {campaign_name}")

def add_user_phone_number(number):
    """
    Agrega una nueva fila con solo el número, dejando el resto de columnas vacías.
    Se asegura que el número esté en la columna 'Number'.
    """
    try:
        headers = sheet.row_values(1)
        row_data = [""] * len(headers)
        if "Number" in headers:
            number_index = headers.index("Number")
            row_data[number_index] = number
            sheet.append_row(row_data)
            print(f"Número {number} registrado correctamente en Google Sheets.")
        else:
            print("La columna 'Number' no fue encontrada en la hoja.")
    except Exception as e:
        print(f"Error al agregar número en Google Sheets: {e}")


def update_user_name_by_number(number, new_name):
    """
    Busca una fila por número de teléfono y actualiza la columna 'User Name' con el nombre indicado.
    """
    try:
        df = get_google_sheets_data()
        df.columns = df.columns.str.lower().str.strip()

        if "number" not in df.columns:
            print("❌ La columna 'Number' no fue encontrada en el DataFrame.")
            return

        row_index = df.index[df["number"].astype(str) == str(number)].tolist()
        if row_index:
            row_number = row_index[0] + 2  # +2 por encabezado
            update_google_sheets_entry_by_row(row_number, {"User Name": new_name})
            print(f"✅ Nombre actualizado para {number}: {new_name}")
        else:
            print(f"⚠️ No se encontró el número {number} en la hoja.")
    except Exception as e:
        print(f"❌ Error al actualizar nombre por número: {e}")





'''

'''