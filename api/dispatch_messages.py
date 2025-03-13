import json
import datetime
import requests
import config
import models
import utils

def handler(request, context):
    # Retrieve current node configuration
    node_name = config.CONFIG.get("NODE_NAME", "defaultNode")
    data_method = config.CONFIG.get("DATA_GENERATION_METHOD", "random")
    
    # Generate message content based on configuration
    if data_method == "openai":
        prompt = config.CONFIG.get("OPENAI_PROMPT", "Generate some data:")
        message = utils.generate_data_openai(prompt)
    else:
        length = config.CONFIG.get("RANDOM_STRING_LENGTH", 16)
        case = config.CONFIG.get("RANDOM_STRING_CASE", "camel")
        message = utils.generate_random_string(length, case)
    
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Save the outgoing message to the local database
    models.add_message(node_name, timestamp, message)
    
    # Prepare the payload for recipient nodes
    payload = {
        "sender": node_name,
        "timestamp": timestamp,
        "message": message
    }
    
    recipients = config.CONFIG.get("NODE_ADDRESSES", [])
    logs = []
    
    # Send the message to each recipient node
    for node_address in recipients:
        # Ensure the node address has a scheme
        if not node_address.startswith("http"):
            url = f"http://{node_address}/receive"
        else:
            url = f"{node_address}/receive"
        try:
            res = requests.post(url, json=payload, timeout=5)
            logs.append(f"Dispatched to {node_address}: {res.status_code}")
        except Exception as e:
            logs.append(f"Failed to dispatch to {node_address}: {str(e)}")
    
    response_data = {
        "status": "completed",
        "logs": logs
    }
    
    return {
        "statusCode": 200,
        "body": json.dumps(response_data)
    }
