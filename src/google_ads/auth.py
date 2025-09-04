from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def verify_google_ads_api():
    """Verifica si la conexión con la API de Google Ads es válida."""
    try:
        # Cargar la configuración de autenticación desde google-ads.yaml
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")

        # Si llegamos aquí sin errores, significa que la autenticación es exitosa
        print("✅ Conexión con la API de Google Ads establecida correctamente.")

        # Verificar acceso llamando a un servicio de la API (sin requerir datos de cliente)
        customer_service = client.get_service("CustomerService")
        print("✅ Se pudo acceder al servicio 'CustomerService'. La API está funcionando.")

    except GoogleAdsException as ex:
        print(f"❌ Error en autenticación con Google Ads: {ex}")
        for error in ex.failure.errors:
            print(f"🔹 Código de error: {error.error_code.authorization_error}")
            print(f"🔹 Mensaje: {error.message}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

# Ejecutar la prueba de conexión sin depender de clientes existentes
verify_google_ads_api()

'''
python src\google_ads\auth.py
'''