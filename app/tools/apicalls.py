import requests
from app.utils.logger import get_logger

from app.utils.setting import settings

logger = get_logger(__name__)

BASE_URL = settings.REST_COUNTRIES_API_URL

def fetch_country_data(country: str):
    url = f"{BASE_URL}/{country}"
    try:
        logger.info("REST Countries request started", extra={"country": country, "url": url})
        response = requests.get(url, timeout=10)
        logger.info(
            "REST Countries response received",
            extra={"country": country, "status_code": response.status_code},
        )
        
        if response.status_code == 404:
            logger.warning("Country not found", extra={"country": country})
            return {"error": f"Country '{country}' not found."}
            
        response.raise_for_status()
        data = response.json()
        
    
        if data and isinstance(data, list):
            logger.info("REST Countries data parsed", extra={"country": country, "matches": len(data)})
            return {"data": data[0]}
        logger.error("Unexpected REST Countries data format", extra={"country": country})
        return {"error": "Unexpected data format received from API."}
        
    except requests.exceptions.RequestException as e:
        logger.exception("REST Countries request failed", extra={"country": country})
        return {"error": "Failed to connect to the country database."}
