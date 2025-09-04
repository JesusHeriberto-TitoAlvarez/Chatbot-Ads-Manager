import os
import gspread
from google.oauth2.service_account import Credentials

# Ruta absoluta a las credenciales
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'CredentialsGoogleSheets.json'))

# Configuración
SHEET_ID = "16MQ_9loHwG1JGV24oD4Qh8XL8hSUU08ZteTEHW12H1U"
WORKSHEET_NAME = "Interacciones_Reales_v01"

# Autenticación
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# Leer encabezados
HEADERS = sheet.row_values(1)

def get_user_row(phone_number):
    """Devuelve el número de fila del usuario según su número (columna 'Number')"""
    if "Number" not in HEADERS:
        raise ValueError("La columna 'Number' no está presente en la hoja.")
    col_index = HEADERS.index("Number") + 1
    values = sheet.col_values(col_index)
    for idx, val in enumerate(values[1:], start=2):
        if val.strip() == phone_number.strip():
            return idx
    return None

def create_user_if_not_exists(phone_number):
    """Crea una nueva fila con valores iniciales si el número no está registrado aún."""
    if not get_user_row(phone_number):
        new_row = [""] * len(HEADERS)

        if "Number" in HEADERS:
            new_row[HEADERS.index("Number")] = phone_number
        if "Customer ID" in HEADERS:
            new_row[HEADERS.index("Customer ID")] = "8829466542"
        if "Estado Campana" in HEADERS:
            new_row[HEADERS.index("Estado Campana")] = "no iniciada"
        if "Estado Anuncio" in HEADERS:
            new_row[HEADERS.index("Estado Anuncio")] = "no iniciado"

        sheet.append_row(new_row, value_input_option="USER_ENTERED")
        print(f"Número {phone_number} registrado con Customer ID y estados iniciales.")
    else:
        print(f"ℹEl número {phone_number} ya estaba registrado.")

def update_user_field(phone_number, field_name, value):
    """Actualiza un campo específico de un usuario"""
    row = get_user_row(phone_number)
    if row:
        if field_name in HEADERS:
            col = HEADERS.index(field_name) + 1
            sheet.update_cell(row, col, value)
            print(f"Campo '{field_name}' actualizado para {phone_number} con: {value}")
        else:
            print(f"La columna '{field_name}' no existe en la hoja.")
    else:
        print(f"Número no encontrado: {phone_number}")

def get_user_field(phone_number, field_name):
    """Lee el valor de un campo específico"""
    row = get_user_row(phone_number)
    if row and field_name in HEADERS:
        col = HEADERS.index(field_name) + 1
        return sheet.cell(row, col).value
    return None

def delete_user(phone_number):
    """Elimina por completo la fila de un usuario"""
    row = get_user_row(phone_number)
    if row:
        sheet.delete_rows(row)
        print(f"Fila eliminada para el número {phone_number}")




'''
import os
import gspread
from google.oauth2.service_account import Credentials

# Ruta absoluta a las credenciales
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'CredentialsGoogleSheets.json'))

# Configuración
SHEET_ID = "16MQ_9loHwG1JGV24oD4Qh8XL8hSUU08ZteTEHW12H1U"
WORKSHEET_NAME = "Interacciones_Reales_v01"

# Autenticación
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# Leer encabezados de columna
HEADERS = sheet.row_values(1)

def get_user_row(phone_number):
    """Devuelve la fila donde se encuentra el número de teléfono, o None si no existe."""
    if "Number" not in HEADERS:
        raise ValueError("La columna 'Number' no está presente en la hoja.")
    col_index = HEADERS.index("Number") + 1
    values = sheet.col_values(col_index)
    for idx, val in enumerate(values[1:], start=2):
        if val.strip() == phone_number.strip():
            return idx
    return None

def create_user_if_not_exists(phone_number):
    """Crea una nueva fila con valores iniciales si el número no está registrado aún."""
    if not get_user_row(phone_number):
        new_row = [""] * len(HEADERS)

        if "Number" in HEADERS:
            new_row[HEADERS.index("Number")] = phone_number
        if "Customer ID" in HEADERS:
            new_row[HEADERS.index("Customer ID")] = "8829466542"
        if "Estado campaña" in HEADERS:
            new_row[HEADERS.index("Estado campaña")] = "no iniciada"
        if "Estado anuncio" in HEADERS:
            new_row[HEADERS.index("Estado anuncio")] = "no iniciado"

        sheet.append_row(new_row, value_input_option="USER_ENTERED")
        print(f"Número {phone_number} registrado con estados iniciales.")
    else:
        print(f"ℹEl número {phone_number} ya está registrado.")

def update_user_field(phone_number, field_name, value):
    """Actualiza un campo específico de un usuario identificado por su número."""
    row = get_user_row(phone_number)
    if row:
        if field_name in HEADERS:
            col = HEADERS.index(field_name) + 1
            sheet.update_cell(row, col, value)
            print(f"Campo '{field_name}' actualizado para {phone_number} con: {value}")
        else:
            print(f"La columna '{field_name}' no existe en la hoja.")
    else:
        print(f"Número no encontrado: {phone_number}")

def get_user_field(phone_number, field_name):
    """Obtiene el valor de un campo específico del usuario."""
    row = get_user_row(phone_number)
    if row and field_name in HEADERS:
        col = HEADERS.index(field_name) + 1
        return sheet.cell(row, col).value
    return None

def delete_user(phone_number):
    """Elimina la fila completa de un usuario según su número."""
    row = get_user_row(phone_number)
    if row:
        sheet.delete_rows(row)
        print(f"Fila eliminada para el número {phone_number}")












import os
import gspread
from google.oauth2.service_account import Credentials

# Ruta absoluta a las credenciales
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'CredentialsGoogleSheets.json'))

# Configuración
SHEET_ID = "16MQ_9loHwG1JGV24oD4Qh8XL8hSUU08ZteTEHW12H1U"
WORKSHEET_NAME = "Interacciones_Reales_v01"

# Autenticación
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# Leer encabezados de columna
HEADERS = sheet.row_values(1)

def get_user_row(phone_number):
    """Devuelve la fila donde se encuentra el número de teléfono, o None si no existe."""
    if "Number" not in HEADERS:
        raise ValueError("La columna 'Number' no está presente en la hoja.")
    col_index = HEADERS.index("Number") + 1
    values = sheet.col_values(col_index)
    for idx, val in enumerate(values[1:], start=2):
        if val.strip() == phone_number.strip():
            return idx
    return None

def create_user_if_not_exists(phone_number):
    """Crea una nueva fila con el número y un Customer ID fijo si aún no está registrado."""
    if not get_user_row(phone_number):
        new_row = [""] * len(HEADERS)
        if "Number" in HEADERS:
            new_row[HEADERS.index("Number")] = phone_number
        if "Customer ID" in HEADERS:
            new_row[HEADERS.index("Customer ID")] = "8829466542"                                # CUSTOMER ID
        sheet.append_row(new_row, value_input_option="USER_ENTERED")
        print(f"Número {phone_number} registrado con Customer ID 8829466542.")
    else:
        print(f"ℹEl número {phone_number} ya estaba registrado.")

def update_user_field(phone_number, field_name, value):
    """Actualiza un campo específico de un usuario identificado por su número."""
    row = get_user_row(phone_number)
    if row:
        if field_name in HEADERS:
            col = HEADERS.index(field_name) + 1
            sheet.update_cell(row, col, value)
            print(f"Campo '{field_name}' actualizado para {phone_number} con: {value}")
        else:
            print(f"La columna '{field_name}' no existe en la hoja.")
    else:
        print(f"Número no encontrado: {phone_number}")

def get_user_field(phone_number, field_name):
    """Obtiene el valor de un campo específico del usuario."""
    row = get_user_row(phone_number)
    if row and field_name in HEADERS:
        col = HEADERS.index(field_name) + 1
        return sheet.cell(row, col).value
    return None

def delete_user(phone_number):
    """Elimina la fila completa de un usuario según su número."""
    row = get_user_row(phone_number)
    if row:
        sheet.delete_rows(row)
        print(f"🗑️ Fila eliminada para el número {phone_number}")


















import os
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Ruta al archivo de credenciales (ajustado para que siempre apunte al archivo correcto)
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'CredentialsGoogleSheets.json'))

# Datos de configuración
SHEET_ID = "16MQ_9loHwG1JGV24oD4Qh8XL8hSUU08ZteTEHW12H1U"  # ID real de la hoja
SHEET_NAME = "Interacciones_Reales_v01"  # Hoja específica para registrar interacciones

# Autenticación
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Leer encabezados
HEADERS = sheet.row_values(1)

def get_user_row(phone_number):
    """Devuelve el número de fila del usuario según su número (columna 'Number')"""
    if "Number" not in HEADERS:
        raise ValueError("La columna 'Number' no está presente en la hoja.")
    col_index = HEADERS.index("Number") + 1
    values = sheet.col_values(col_index)
    for idx, val in enumerate(values[1:], start=2):
        if val.strip() == phone_number.strip():
            return idx
    return None

def create_user_if_not_exists(phone_number):
    """Crea una nueva fila con el número si aún no está registrado"""
    if not get_user_row(phone_number):
        new_row = [""] * len(HEADERS)
        if "Number" in HEADERS:
            new_row[HEADERS.index("Number")] = phone_number
            sheet.append_row(new_row, value_input_option="USER_ENTERED")
            print(f"Número {phone_number} registrado correctamente en la hoja.")
        else:
            print("No se encontró la columna 'Number'.")

def update_user_field(phone_number, field_name, value):
    """Actualiza un campo específico de un usuario"""
    row = get_user_row(phone_number)
    if row:
        if field_name in HEADERS:
            col = HEADERS.index(field_name) + 1
            sheet.update_cell(row, col, value)
            print(f"Campo '{field_name}' actualizado para {phone_number} con: {value}")
        else:
            print(f"La columna '{field_name}' no existe en la hoja.")
    else:
        print(f"Número no encontrado: {phone_number}")

def get_user_field(phone_number, field_name):
    """Lee el valor de un campo específico"""
    row = get_user_row(phone_number)
    if row and field_name in HEADERS:
        col = HEADERS.index(field_name) + 1
        return sheet.cell(row, col).value
    return None

def delete_user(phone_number):
    """Elimina por completo la fila de un usuario"""
    row = get_user_row(phone_number)
    if row:
        sheet.delete_rows(row)
        print(f"Fila eliminada para el número {phone_number}")
'''