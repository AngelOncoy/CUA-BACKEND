import requests
import base64
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# ===============================
# CONFIGURACIÓN REAL - SANDBOX
# ===============================

PAYPAL_CLIENT_ID = "AeYg6exHd4glD74JDaHGR7sQLgFRbj4S8tYdvzBNoUIQzCBFnzIRE34EySK7JLV6q-ERJqtoMmg3nxe7"
PAYPAL_SECRET = "EIR6pcjg8awja58Hm353vGRL6cw_EBJfllMEoe9JyHzFkYwWc7yM9RtBbRiakUnNDGm6eAEp0RISWfUr"

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

    data = {"grant_type": "client_credentials"}

    response = requests.post(f"{PAYPAL_API}/v1/oauth2/token", headers=headers, data=data)

    if response.status_code != 200:
        log.error("[PAYPAL ERROR TOKEN] " + response.text)
        raise Exception("ERROR AL OBTENER TOKEN PAYPAL")

    return response.json()["access_token"]


# ===============================
# CREAR ORDEN (CREATE ORDER)
# ===============================
def create_paypal_order(amount, description):
    token = get_paypal_token()
    log.info(f"[PAYPAL] Creando orden por {amount} USD")

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
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW",
            "return_url": "http://localhost:8000/m1/paypal/success",
            "cancel_url": "http://localhost:8000/m1/paypal/cancel"
        }
    }

    response = requests.post(f"{PAYPAL_API}/v2/checkout/orders", headers=headers, json=body)

    if response.status_code not in [200, 201]:
        log.error("[PAYPAL ERROR CREATE] " + response.text)
        raise Exception("ERROR AL CREAR ORDEN PAYPAL")

    order = response.json()

    approval_url = next(link["href"] for link in order["links"] if link["rel"] == "approve")

    return {
        "order_id": order["id"],
        "approval_url": approval_url
    }


# ===============================
# CAPTURAR ORDEN (CAPTURE ORDER)
# ===============================
def capture_paypal_order(order_id):
    log.info(f"[PAYPAL] Capturando orden {order_id}")

    token = get_paypal_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    url = f"{PAYPAL_API}/v2/checkout/orders/{order_id}/capture"

    response = requests.post(url, headers=headers)

    if response.status_code not in [200, 201]:
        log.error("[PAYPAL ERROR CAPTURE] " + response.text)
        raise Exception("ERROR AL CAPTURAR ORDEN PAYPAL")

    return response.json()
