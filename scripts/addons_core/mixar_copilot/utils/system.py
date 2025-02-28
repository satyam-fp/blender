import requests

def internet_connection():
    try:
        requests.get("https://www.google.com/", timeout=5)
    except Exception:
        return False

    return True