import argparse 
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# URL final del anuncio
FINAL_URL = "https://www.chatbotadsmanager.com/"

def create_ad_group_and_ad(client, customer_id, campaign_id, ad_group_name, titles, descriptions, keywords):
    """Crea un grupo de anuncios y un anuncio dentro de la campaña especificada."""
    ad_group_service = client.get_service("AdGroupService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    
    # Crear grupo de anuncios
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_name
    ad_group.campaign = client.get_service("CampaignService").campaign_path(customer_id, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    
    try:
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        print(f"Grupo de anuncios creado con éxito: {ad_group_resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    
    # Crear anuncio Responsive Search Ad (RSA)
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # Se crea en estado pausado
    ad_group_ad.ad_group = ad_group_resource_name
    
    ad = ad_group_ad.ad
    ad.final_urls.append(FINAL_URL)
    rsa = ad.responsive_search_ad
    
    # Validar límites antes de asignar títulos y descripciones
    titles = [t.strip() for t in titles if t.strip()]
    descriptions = [d.strip() for d in descriptions if d.strip()]
    keywords = [k.strip() for k in keywords if k.strip()]

    if len(titles) < 3 or len(titles) > 15:
        print(f"Error: Se requieren entre 3 y 15 títulos, proporcionados: {len(titles)}")
        return
    if len(descriptions) < 2 or len(descriptions) > 4:
        print(f"Error: Se requieren entre 2 y 4 descripciones, proporcionadas: {len(descriptions)}")
        return
    if len(keywords) > 10:
        print(f"Error: Se permiten hasta 10 palabras clave, proporcionadas: {len(keywords)}")
        return

    # Agregar títulos y descripciones dentro de los límites
    for title in titles[:15]:  # Máximo 15 títulos
        asset = client.get_type("AdTextAsset")
        asset.text = title
        rsa.headlines.append(asset)

    for description in descriptions[:4]:  # Máximo 4 descripciones
        asset = client.get_type("AdTextAsset")
        asset.text = description
        rsa.descriptions.append(asset)
    
    try:
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        print(f"Anuncio creado con éxito: {ad_group_ad_response.results[0].resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    
    # Agregar palabras clave
    for keyword in keywords[:10]:  # Máximo 10 palabras clave
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_resource_name
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        ad_group_criterion.keyword.text = keyword
        ad_group_criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.EXACT
        
        try:
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=[ad_group_criterion_operation]
            )
            print(f"Palabra clave agregada: {keyword}")
        except GoogleAdsException as ex:
            handle_googleads_exception(ex)

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
        description="Crea un grupo de anuncios y un anuncio en una campaña especificada."
    )
    parser.add_argument("-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads.")
    parser.add_argument("-n", "--campaign_id", type=str, required=True, help="El ID de la campaña donde se agregará el anuncio.")
    parser.add_argument("-g", "--ad_group_name", type=str, required=True, help="El nombre del grupo de anuncios.")
    parser.add_argument("-t", "--titles", type=str, required=True, help="Títulos separados por barra vertical '|'.")
    parser.add_argument("-d", "--descriptions", type=str, required=True, help="Descripciones separadas por barra vertical '|'.")
    parser.add_argument("-k", "--keywords", type=str, required=True, help="Palabras clave separadas por barra vertical '|'.")
    
    args = parser.parse_args()
    
    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        
        create_ad_group_and_ad(
            googleads_client,
            args.customer_id,
            args.campaign_id,
            args.ad_group_name,
            args.titles.split("|"),
            args.descriptions.split("|"),
            args.keywords.split("|")
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

        
'''
Para ejecutar:
python src/google_ads/add_ad_to_campaign.py -c 8829466542 -n 22323091843 -g "CAMPAÑA 16_QQP" -t "Title1,Title2,Title3" -d "Description1,Description2,Description3" -k "Keyword1,Keyword2,Keyword3"






import argparse 
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# URL final del anuncio
FINAL_URL = "https://www.chatbotadsmanager.com/"

def create_ad_group_and_ad(client, customer_id, campaign_id, ad_group_name, titles, descriptions, keywords):
    """Crea un grupo de anuncios y un anuncio dentro de la campaña especificada."""
    ad_group_service = client.get_service("AdGroupService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    
    # Crear grupo de anuncios
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_name
    ad_group.campaign = client.get_service("CampaignService").campaign_path(customer_id, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    
    try:
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        print(f"Grupo de anuncios creado con éxito: {ad_group_resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    
    # Crear anuncio Responsive Search Ad (RSA)
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # Se crea en estado pausado
    ad_group_ad.ad_group = ad_group_resource_name
    
    ad = ad_group_ad.ad
    ad.final_urls.append(FINAL_URL)
    rsa = ad.responsive_search_ad
    
    # Validar límites antes de asignar títulos y descripciones
    titles = [t.strip() for t in titles if t.strip()]
    descriptions = [d.strip() for d in descriptions if d.strip()]
    keywords = [k.strip() for k in keywords if k.strip()]

    if len(titles) < 3 or len(titles) > 15:
        print(f"Error: Se requieren entre 3 y 15 títulos, proporcionados: {len(titles)}")
        return
    if len(descriptions) < 2 or len(descriptions) > 4:
        print(f"Error: Se requieren entre 2 y 4 descripciones, proporcionadas: {len(descriptions)}")
        return
    if len(keywords) > 10:
        print(f"Error: Se permiten hasta 10 palabras clave, proporcionadas: {len(keywords)}")
        return

    # Agregar títulos y descripciones dentro de los límites
    for title in titles[:15]:  # Máximo 15 títulos
        asset = client.get_type("AdTextAsset")
        asset.text = title
        rsa.headlines.append(asset)

    for description in descriptions[:4]:  # Máximo 4 descripciones
        asset = client.get_type("AdTextAsset")
        asset.text = description
        rsa.descriptions.append(asset)
    
    try:
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        print(f"Anuncio creado con éxito: {ad_group_ad_response.results[0].resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    
    # Agregar palabras clave
    for keyword in keywords[:10]:  # Máximo 10 palabras clave
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_resource_name
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        ad_group_criterion.keyword.text = keyword
        ad_group_criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.EXACT
        
        try:
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=[ad_group_criterion_operation]
            )
            print(f"Palabra clave agregada: {keyword}")
        except GoogleAdsException as ex:
            handle_googleads_exception(ex)

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
        description="Crea un grupo de anuncios y un anuncio en una campaña especificada."
    )
    parser.add_argument("-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads.")
    parser.add_argument("-n", "--campaign_id", type=str, required=True, help="El ID de la campaña donde se agregará el anuncio.")
    parser.add_argument("-g", "--ad_group_name", type=str, required=True, help="El nombre del grupo de anuncios.")
    parser.add_argument("-t", "--titles", type=str, required=True, help="Títulos separados por coma.")
    parser.add_argument("-d", "--descriptions", type=str, required=True, help="Descripciones separadas por coma.")
    parser.add_argument("-k", "--keywords", type=str, required=True, help="Palabras clave separadas por coma.")
    
    args = parser.parse_args()
    
    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        
        create_ad_group_and_ad(
            googleads_client,
            args.customer_id,
            args.campaign_id,
            args.ad_group_name,
            args.titles.split(","),
            args.descriptions.split(","),
            args.keywords.split(",")
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)














import argparse
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# URL final del anuncio
FINAL_URL = "https://www.chatbotadsmanager.com/"

def create_ad_group_and_ad(client, customer_id, campaign_id, ad_group_name, titles, descriptions, keywords):
    """Crea un grupo de anuncios y un anuncio dentro de la campaña especificada."""
    ad_group_service = client.get_service("AdGroupService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    
    # Crear grupo de anuncios
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_name
    ad_group.campaign = client.get_service("CampaignService").campaign_path(customer_id, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = 1000000  # Oferta de CPC (1 Bs)
    
    try:
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        print(f"✅ Grupo de anuncios creado con éxito: {ad_group_resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    
    # Crear anuncio Responsive Search Ad (RSA)
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # Se crea en estado pausado
    ad_group_ad.ad_group = ad_group_resource_name
    
    ad = ad_group_ad.ad
    ad.final_urls.append(FINAL_URL)
    rsa = ad.responsive_search_ad
    
    # Agregar títulos y descripciones
    for i, title in enumerate(titles[:15]):  # Máximo 15 títulos
        rsa.headlines.append(client.get_type("AdTextAsset"))
        rsa.headlines[i].text = title
    
    for i, description in enumerate(descriptions[:4]):  # Máximo 4 descripciones
        rsa.descriptions.append(client.get_type("AdTextAsset"))
        rsa.descriptions[i].text = description
    
    try:
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        print(f"✅ Anuncio creado con éxito: {ad_group_ad_response.results[0].resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    
    # Agregar palabras clave
    for keyword in keywords[:10]:  # Máximo 10 palabras clave
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_resource_name
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        ad_group_criterion.keyword.text = keyword
        ad_group_criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.EXACT
        
        try:
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=[ad_group_criterion_operation]
            )
            print(f"✅ Palabra clave agregada: {keyword}")
        except GoogleAdsException as ex:
            handle_googleads_exception(ex)

def handle_googleads_exception(exception):
    """Manejo de errores para Google Ads API."""
    print(
        f'Request con ID "{exception.request_id}" falló con estado '
        f'"{exception.error.code().name}" e incluye los siguientes errores:'
    )
    for error in exception.failure.errors:
        print(f'🔹 Error con mensaje "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"🔹 En el campo: {field_path_element.field_name}")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crea un grupo de anuncios y un anuncio en una campaña especificada."
    )
    parser.add_argument("-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads.")
    parser.add_argument("-g", "--ad_group_name", type=str, required=True, help="El nombre del grupo de anuncios.")
    parser.add_argument("-t", "--titles", type=str, required=True, help="Títulos separados por coma.")
    parser.add_argument("-d", "--descriptions", type=str, required=True, help="Descripciones separadas por coma.")
    parser.add_argument("-k", "--keywords", type=str, required=True, help="Palabras clave separadas por coma.")
    parser.add_argument("-n", "--campaign_id", type=str, required=True, help="El ID de la campaña donde se agregará el anuncio.")
    
    args = parser.parse_args()
    
    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        
        create_ad_group_and_ad(
            googleads_client,
            args.customer_id,
            args.campaign_id,
            args.ad_group_name,
            args.titles.split(","),
            args.descriptions.split(","),
            args.keywords.split(",")
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)







import argparse
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# URL final del anuncio
FINAL_URL = "https://www.chatbotadsmanager.com/"

def create_ad_group_and_ad(client, customer_id, campaign_id, ad_group_name, titles, descriptions, keywords):
    """Crea un grupo de anuncios y un anuncio dentro de la campaña especificada."""
    ad_group_service = client.get_service("AdGroupService")
    ad_group_ad_service = client.get_service("AdGroupAdService")
    ad_group_criterion_service = client.get_service("AdGroupCriterionService")
    
    # Crear grupo de anuncios
    ad_group_operation = client.get_type("AdGroupOperation")
    ad_group = ad_group_operation.create
    ad_group.name = ad_group_name
    ad_group.campaign = client.get_service("CampaignService").campaign_path(customer_id, campaign_id)
    ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
    ad_group.type = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ad_group.cpc_bid_micros = 1000000  # Oferta de CPC (1 Bs)
    
    try:
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        print(f"✅ Grupo de anuncios creado con éxito: {ad_group_resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return
    
    # Crear anuncio Responsive Search Ad (RSA)
    ad_group_ad_operation = client.get_type("AdGroupAdOperation")
    ad_group_ad = ad_group_ad_operation.create
    ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # Se crea en estado pausado
    ad_group_ad.ad_group = ad_group_resource_name
    
    ad = ad_group_ad.ad
    ad.final_urls.append(FINAL_URL)
    rsa = ad.responsive_search_ad
    
    # Agregar títulos y descripciones
    for i, title in enumerate(titles[:3]):  # Máximo 3 títulos
        rsa.headlines.append(client.get_type("AdTextAsset"))
        rsa.headlines[i].text = title
    
    for i, description in enumerate(descriptions[:3]):  # Máximo 3 descripciones
        rsa.descriptions.append(client.get_type("AdTextAsset"))
        rsa.descriptions[i].text = description
    
    try:
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        print(f"✅ Anuncio creado con éxito: {ad_group_ad_response.results[0].resource_name}")
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    
    # Agregar palabras clave
    for keyword in keywords[:3]:  # Máximo 3 palabras clave
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_resource_name
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        ad_group_criterion.keyword.text = keyword
        ad_group_criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum.EXACT
        
        try:
            ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=[ad_group_criterion_operation]
            )
            print(f"✅ Palabra clave agregada: {keyword}")
        except GoogleAdsException as ex:
            handle_googleads_exception(ex)

def handle_googleads_exception(exception):
    """Manejo de errores para Google Ads API."""
    print(
        f'Request con ID "{exception.request_id}" falló con estado '
        f'"{exception.error.code().name}" e incluye los siguientes errores:'
    )
    for error in exception.failure.errors:
        print(f'🔹 Error con mensaje "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"🔹 En el campo: {field_path_element.field_name}")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crea un grupo de anuncios y un anuncio en una campaña especificada."
    )
    parser.add_argument("-c", "--customer_id", type=str, required=True, help="El ID del cliente de Google Ads.")
    parser.add_argument("-g", "--ad_group_name", type=str, required=True, help="El nombre del grupo de anuncios.")
    parser.add_argument("-t", "--titles", type=str, required=True, help="Títulos separados por coma.")
    parser.add_argument("-d", "--descriptions", type=str, required=True, help="Descripciones separadas por coma.")
    parser.add_argument("-k", "--keywords", type=str, required=True, help="Palabras clave separadas por coma.")
    parser.add_argument("-n", "--campaign_id", type=str, required=True, help="El ID de la campaña donde se agregará el anuncio.")
    
    args = parser.parse_args()
    
    try:
        googleads_client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
        if not googleads_client:
            raise ValueError("Error al cargar GoogleAdsClient. Verifica google-ads.yaml.")
        
        create_ad_group_and_ad(
            googleads_client,
            args.customer_id,
            args.campaign_id,
            args.ad_group_name,
            args.titles.split(","),
            args.descriptions.split(","),
            args.keywords.split(",")
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


'''