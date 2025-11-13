import requests
import base64
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# ===============================
# CONFIGURACIÓN REAL
# ===============================

PAYPAL_CLIENT_ID = "AZI_HY7jvdyGbxTsf6jxYfxubNipuwgAYi_8_f59pjmHGyy70sVRCc6FAH5Xk2yiw8qxGfl8WaLC4WFg"
PAYPAL_SECRET = "EN_qIEAgAEI7kW3TfeDMEW65rSpm0rvm8lzV2CcYIjFJMLLNY_2Qt-ljsbnI-8IrE5vJ5dmVyqq8y1Za"

PAYPAL_API = "https://api-m.sandbox.paypal.com"


# ===============================
# TOKEN
# ===============================

def get_paypal_token():
    log.info("[PAYPAL] Solicitando token...")

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = { "grant_type": "client_credentials" }

    response = requests.post(f"{PAYPAL_API}/v1/oauth2/token", headers=headers, data=data)

    if response.status_code != 200:
        log.error(response.text)
        raise Exception("ERROR AL OBTENER TOKEN PAYPAL")

    return response.json()["access_token"]


# ===============================
# CREAR ORDEN
# ===============================

def create_paypal_order(amount, description):
    token = get_paypal_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": f"{amount:.2f}"
                },
                "description": description
            }
        ],
        "application_context": {
            "brand_name": "CUA TEST",
            "return_url": "http://localhost:8000/m1/paypal/success",
            "cancel_url": "http://localhost:8000/m1/paypal/cancel"
        }
    }

    response = requests.post(f"{PAYPAL_API}/v2/checkout/orders", headers=headers, json=body)

    if response.status_code not in [200, 201]:
        log.error("[PAYPAL ERROR] " + response.text)
        raise Exception("ERROR AL CREAR ORDEN PAYPAL")

    order = response.json()

    approval_url = next(link["href"] for link in order["links"] if link["rel"] == "approve")

    return approval_url
