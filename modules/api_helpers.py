import requests
import logging

logger = logging.getLogger(__name__)

TOKEN = None

def fetch_auth_token():
    global TOKEN
    try:
        url = "https://condominium-server.technologist.ai/api/Authentication/accessToken"
        payload = {"email": "telegram@client.am", "password": "123456"}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        TOKEN = data.get("accessToken")
        logger.info(f"Token fetched successfully: {TOKEN}")
        return TOKEN
    except Exception as e:
        logger.error(f"Token fetch failed: {e}")
        TOKEN = None
        return None

def fetch_deposit_and_debt_from_api(unique_code):
    global TOKEN
    if not TOKEN:
        TOKEN = fetch_auth_token()
        if not TOKEN:
            logger.error("Unable to fetch token. Aborting API call.")
            return None, None

    try:
        url = f"https://condominium-server.technologist.ai/api/Customer/telegram/getPropInfo?code={unique_code}"
        headers = {"Authorization": f"Bearer {TOKEN}"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(url)
        return data.get("deposit"), data.get("debt")
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return None, None
