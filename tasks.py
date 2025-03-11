import requests
import datetime
import config
import models
import utils


def dispatch_messages():
    """
    Generates new data (using either OpenAI or a random string) and sends it
    to each node listed in the configuration.
    """
    node_name = config.CONFIG.get("NODE_NAME", "Node1")
    data_method = config.CONFIG.get("DATA_GENERATION_METHOD", "random")
    message = ""
    if data_method == "openai":
        prompt = config.CONFIG.get("OPENAI_PROMPT", "Generate some data:")
        message = utils.generate_data_openai(prompt)
    else:
        length = config.CONFIG.get("RANDOM_STRING_LENGTH", 16)
        case = config.CONFIG.get("RANDOM_STRING_CASE", "camel")
        message = utils.generate_random_string(length, case)

    timestamp = datetime.datetime.utcnow().isoformat()
    # Save the outgoing message locally.
    models.add_message(node_name, timestamp, message)

    payload = {
        "sender": node_name,
        "timestamp": timestamp,
        "message": message
    }
    recipients = config.CONFIG.get("NODE_ADDRESSES", [])
    for node_address in recipients:
        url = f"http://{node_address}/receive"
        try:
            response = requests.post(url, json=payload, timeout=5)
            print(f"Dispatched to {node_address}: {response.status_code}")
        except Exception as e:
            print(f"Failed to dispatch to {node_address}: {e}")


def ping_nodes():
    """
    Checks connectivity with each node by sending a simple GET request.
    Logs the result (status code or error).
    """
    recipients = config.CONFIG.get("NODE_ADDRESSES", [])
    for node_address in recipients:
        url = f"http://{node_address}/"
        try:
            response = requests.get(url, timeout=5)
            print(f"Ping {node_address}: {response.status_code}")
        except Exception as e:
            print(f"Ping {node_address} failed: {e}")
