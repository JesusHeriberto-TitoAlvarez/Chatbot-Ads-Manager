from google.ads.googleads.client import GoogleAdsClient

def get_campaign_details(customer_id, campaign_name):
    """Obtiene todos los detalles posibles de una campaña en Google Ads."""
    client = GoogleAdsClient.load_from_storage("google-ads.yaml", version="v18")
    ga_service = client.get_service("GoogleAdsService")

    query = f'''
        SELECT 
            campaign.id, 
            campaign.name, 
            campaign.status,
            campaign.advertising_channel_type,
            campaign.start_date,
            campaign.end_date,
            campaign_budget.amount_micros,
            campaign.bidding_strategy_type,
            campaign.serving_status,
            campaign.optimization_score,
            metrics.cost_micros  -- 🔥 Agregamos el gasto total de la campaña
        FROM campaign
        WHERE campaign.name = '{campaign_name}'
    '''

    response = ga_service.search(customer_id=customer_id, query=query)

    for row in response:
        campaign_data = {
            "Campaign ID": row.campaign.id,
            "Campaign Name": row.campaign.name,
            "Status": row.campaign.status.name,
            "Channel Type": row.campaign.advertising_channel_type.name,
            "Start Date": row.campaign.start_date,
            "End Date": row.campaign.end_date,
            "Assigned Budget (Bs)": row.campaign_budget.amount_micros / 1_000_000,  # Convertir a Bs
            "Total Spend (Bs)": row.metrics.cost_micros / 1_000_000,  # 🔥 Convertimos micros a Bs
            "Bidding Strategy": row.campaign.bidding_strategy_type.name,
            "Serving Status": row.campaign.serving_status.name,
            "Optimization Score": row.campaign.optimization_score,
        }
        print("✅ Campaign details retrieved:", campaign_data)
        return campaign_data

    print(f"❌ No campaign found for name: {campaign_name}")
    return None

'''

'''