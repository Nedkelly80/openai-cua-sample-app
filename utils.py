import os
import requests
from dotenv import load_dotenv
import json
import base64
from PIL import Image
from io import BytesIO
import io
from urllib.parse import urlparse

load_dotenv(override=True)

BLOCKED_DOMAINS = [
    "maliciousbook.com",
    "evilvideos.com",
    "darkwebforum.com",
    "shadytok.com",
    "suspiciouspins.com",
    "ilanbigio.com",
]


def pp(obj):
    print(json.dumps(obj, indent=4))


def show_image(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(BytesIO(image_data))
    image.show()


def calculate_image_dimensions(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(io.BytesIO(image_data))
    return image.size


def sanitize_message(msg: dict) -> dict:
    """Return a copy of the message with image_url omitted for computer_call_output messages."""
    if msg.get("type") == "computer_call_output":
        output = msg.get("output", {})
        if isinstance(output, dict):
            sanitized = msg.copy()
            sanitized["output"] = {**output, "image_url": "[omitted]"}
            return sanitized
    return msg


def create_response(**kwargs):
    url = "https://api.openai.com/v1/responses"
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please create a .env file with your OpenAI API key.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    openai_org = os.getenv("OPENAI_ORG")
    if openai_org:
        headers["Openai-Organization"] = openai_org

    try:
        response = requests.post(url, headers=headers, json=kwargs, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"Network error connecting to OpenAI API: {e}")
        raise

    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        if response.status_code == 401:
            raise ValueError("Invalid OpenAI API key. Please check your OPENAI_API_KEY in .env file.")
        elif response.status_code == 429:
            raise ValueError("OpenAI API rate limit exceeded. Please try again later.")

    return response.json()


def check_blocklisted_url(url: str) -> None:
    """Raise ValueError if the given URL (including subdomains) is in the blocklist."""
    hostname = urlparse(url).hostname or ""
    if any(
        hostname == blocked or hostname.endswith(f".{blocked}")
        for blocked in BLOCKED_DOMAINS
    ):
        raise ValueError(f"Blocked URL: {url}")
