import argparse
import datetime
import sys
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

_DATE_FORMAT = "%Y%m%d"  # Formato de fecha para Google Ads

# Variables configurables
CAMPAIGN_TYPE = "SEARCH"  # Tipo de campaña (solo búsqueda está activada)
DURATION_DAYS = 1  # La campaña durará un día
DEFAULT_BUDGET_ASSIGNED = 1000000  # Presupuesto en micros (1,000,000 micros = Bs 1.00 aprox.)


def main(client, customer_id, campaign_name, segmentation):
    """Crea una nueva campaña en Google Ads con segmentación geográfica."""
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_service = client.get_service("CampaignService")
    campaign_criterion_service = client.get_service("CampaignCriterionService")

    # Crear un presupuesto para la campaña
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = f"{campaign_name} Budget"
    campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    campaign_budget.amount_micros = DEFAULT_BUDGET_ASSIGNED
    campaign_budget.explicitly_shared = False  # Se asigna el presupuesto mínimo
    assigned_budget = DEFAULT_BUDGET_ASSIGNED / 1000000  # Convertimos a unidades estándar

    print(f"Creando campaña con:")
    print(f"   - Customer ID: {customer_id}")
    print(f"   - Campaign Name: {campaign_name}")
    print(f"   - City ID (Segmentación): {segmentation}")
    print(f"   - Assigned Budget: {assigned_budget} Bs")

    # Agregar el presupuesto a Google Ads
    try:
        campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    except Exception as e:
        print(f"Error inesperado al crear presupuesto: {e}")
        return

    # Crear la campaña
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH  # Solo búsqueda
    campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Se inicia pausada
    campaign.campaign_budget = campaign_budget_response.results[0].resource_name

    # Configurar la estrategia de puja automática
    # 🔥 Configuración para garantizar mayor visibilidad 🔥
    campaign.bidding_strategy_type = client.enums.BiddingStrategyTypeEnum.TARGET_IMPRESSION_SHARE
    campaign.target_impression_share = client.get_type("TargetImpressionShare")
    campaign.target_impression_share.location = client.enums.TargetImpressionShareLocationEnum.TOP_OF_PAGE  # Ubicación en la parte superior
    campaign.target_impression_share.cpc_bid_ceiling_micros = 1000000  # CPC máximo de Bs 1.00
    campaign.target_impression_share.location_fraction_micros = 1000000  # 100% de impresiones objetivo

    # Configurar fechas de inicio y fin
    start_time = datetime.date.today()
    campaign.start_date = start_time.strftime("%Y-%m-%d")
    end_time = start_time + datetime.timedelta(days=DURATION_DAYS)
    campaign.end_date = end_time.strftime("%Y-%m-%d")

    print(f"Enviando solicitud para crear campaña...")

    try:
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_id = campaign_response.results[0].resource_name.split("/")[-1]
        print(f"Campaña creada con éxito: ID {campaign_id}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    except Exception as e:
        print(f"Error inesperado al crear campaña: {e}")
        return

    # Configurar segmentación geográfica como criterio de campaña
    campaign_criterion_operation = client.get_type("CampaignCriterionOperation")
    campaign_criterion = campaign_criterion_operation.create
    campaign_criterion.campaign = campaign_response.results[0].resource_name
    campaign_criterion.location.geo_target_constant = f"geoTargetConstants/{segmentation}"

    try:
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[campaign_criterion_operation]
        )
        print(f"Segmentación geográfica aplicada para Segmentation ID: {segmentation}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error al aplicar segmentación geográfica: {e}")


def handle_googleads_exception(exception):
    """Manejo de errores para Google Ads API."""
    print(
        f'Request con ID "{exception.request_id}" falló con estado '
        f'"{exception.error.code().name}" e incluye los siguientes errores:'
    )
    for error in exception.failure.errors:
        print(f'Error con mensaje "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"En el campo: {field_path_element.field_name}")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agrega una campaña con segmentación geográfica para un cliente especificado."
    )
    parser.add_argument(
        "-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads."
    )
    parser.add_argument(
        "-n", "--campaign_name", type=str, required=True, help="El nombre de la campaña a crear."
    )
    parser.add_argument(
        "-l", "--city_id", type=str, required=True, help="El ID de la ciudad para segmentación geográfica."
    )
    args = parser.parse_args()

    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        main(googleads_client, args.customer_id, args.campaign_name, args.city_id)
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado en la ejecución: {e}")
        raise e  # Forzar la impresión del error completo



'''
Para ejecutar:
python src/google_ads/add_campaign.py -c 8829466542 -n "CAMPAÑA 33" -l 20084












CODIGO FUNCIOANDO PERFECTAMENTE CON CPC MANUAL
import argparse
import datetime
import sys
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

_DATE_FORMAT = "%Y%m%d"  # Formato de fecha para Google Ads

# Variables configurables
CAMPAIGN_TYPE = "SEARCH"  # Tipo de campaña (solo búsqueda está activada)
DURATION_DAYS = 1  # La campaña durará un día
DEFAULT_BUDGET_ASSIGNED = 500000  # Presupuesto en micros (500,000 micros = Bs 3.50 aprox.)

def main(client, customer_id, campaign_name, segmentation):
    """Crea una nueva campaña en Google Ads con segmentación geográfica."""
    campaign_budget_service = client.get_service("CampaignBudgetService")
    campaign_service = client.get_service("CampaignService")
    campaign_criterion_service = client.get_service("CampaignCriterionService")

    # Crear un presupuesto para la campaña
    campaign_budget_operation = client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = f"{campaign_name} Budget"
    campaign_budget.delivery_method = (
        client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    campaign_budget.amount_micros = DEFAULT_BUDGET_ASSIGNED  # Se asigna el presupuesto mínimo
    assigned_budget = DEFAULT_BUDGET_ASSIGNED / 1000000  # Convertimos a unidades estándar

    print(f"Creando campaña con:")
    print(f"   - Customer ID: {customer_id}")
    print(f"   - Campaign Name: {campaign_name}")
    print(f"   - City ID (Segmentación): {segmentation}")
    print(f"   - Assigned Budget: {assigned_budget} Bs")

    # Agregar el presupuesto a Google Ads
    try:
        campaign_budget_response = (
            campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[campaign_budget_operation]
            )
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    except Exception as e:
        print(f"Error inesperado al crear presupuesto: {e}")
        return

    # Crear la campaña
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH  # Solo búsqueda
    )
    campaign.status = client.enums.CampaignStatusEnum.PAUSED  # Se inicia pausada
    campaign.manual_cpc = client.get_type("ManualCpc")
    campaign.campaign_budget = campaign_budget_response.results[0].resource_name

    # Configurar fechas de inicio y fin
    start_time = datetime.date.today()
    campaign.start_date = start_time.strftime("%Y-%m-%d")
    end_time = start_time + datetime.timedelta(days=DURATION_DAYS)
    campaign.end_date = end_time.strftime("%Y-%m-%d")

    print(f"Enviando solicitud para crear campaña...")

    try:
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_id = campaign_response.results[0].resource_name.split("/")[-1]
        print(f"Campaña creada con éxito: ID {campaign_id}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    except Exception as e:
        print(f"Error inesperado al crear campaña: {e}")
        return

    # Configurar segmentación geográfica como criterio de campaña
    campaign_criterion_operation = client.get_type("CampaignCriterionOperation")
    campaign_criterion = campaign_criterion_operation.create
    campaign_criterion.campaign = campaign_response.results[0].resource_name
    campaign_criterion.location.geo_target_constant = f"geoTargetConstants/{segmentation}"

    try:
        campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id, operations=[campaign_criterion_operation]
        )
        print(f"Segmentación geográfica aplicada para Segmentation ID: {segmentation}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error al aplicar segmentación geográfica: {e}")

def handle_googleads_exception(exception):
    """Manejo de errores para Google Ads API."""
    print(
        f'Request con ID "{exception.request_id}" falló con estado '
        f'"{exception.error.code().name}" e incluye los siguientes errores:'
    )
    for error in exception.failure.errors:
        print(f'Error con mensaje "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"En el campo: {field_path_element.field_name}")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agrega una campaña con segmentación geográfica para un cliente especificado."
    )
    parser.add_argument(
        "-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads."
    )
    parser.add_argument(
        "-n", "--campaign_name", type=str, required=True, help="El nombre de la campaña a crear."
    )
    parser.add_argument(
        "-l", "--city_id", type=str, required=True, help="El ID de la ciudad para segmentación geográfica."
    )
    args = parser.parse_args()

    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        main(googleads_client, args.customer_id, args.campaign_name, args.city_id)
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado en la ejecución: {e}")
        raise e  # Forzar la impresión del error completo







'''