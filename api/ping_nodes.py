import json
import requests
import config

def handler(request, context):
    recipients = config.CONFIG.get("NODE_ADDRESSES", [])
    logs = []
    
    # Ping each recipient node
    for node_address in recipients:
        if not node_address.startswith("http"):
            url = f"http://{node_address}/"
        else:
            url = node_address
        try:
            res = requests.get(url, timeout=5)
            logs.append(f"Ping {node_address}: {res.status_code}")
        except Exception as e:
            logs.append(f"Ping {node_address} failed: {str(e)}")
    
    response_data = {
        "status": "completed",
        "logs": logs
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(response_data)
    }
