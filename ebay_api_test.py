
import os
import requests
from dotenv import load_dotenv

# Load credentials from our .env file
load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

# eBay Sandbox address
TOKEN_URL = (
    "https://api.sandbox.ebay.com/"
    "identity/v1/oauth2/token"
)

def get_access_token():

    if not CLIENT_ID or not CLIENT_SECRET:

        print("ERROR: Credentials not found.")
        print("Please check your .env file.")
        return

    print("Connecting to eBay Sandbox...")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    try:

        response = requests.post(
            TOKEN_URL,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET),
            timeout=20
        )

        if response.status_code == 200:

            result = response.json()

            print("\nSUCCESS!")
            print("Connected to eBay Sandbox.")
            print(
                "Token expires in:",
                result.get("expires_in"),
                "seconds"
            )

            print("\nYour API connection is working!")

            return result["access_token"]

        else:

            print("\nConnection failed.")
            print("Status code:", response.status_code)
            print("Response:", response.text)

    except requests.exceptions.RequestException as error:

        print("Connection error:", error)


if __name__ == "__main__":

    get_access_token()
