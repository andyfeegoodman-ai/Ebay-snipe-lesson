
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

SEARCH_URL = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"


def get_access_token():

    response = requests.post(
        TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=20
    )

    response.raise_for_status()

    return response.json()["access_token"]


def search_auctions():

    print("Connecting to eBay...")

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_GB"
    }

    parameters = {
    "q": "phone",
    "limit": 10
    }

    response = requests.get(
        SEARCH_URL,
        headers=headers,
        params=parameters,
        timeout=20
    )

    response.raise_for_status()

    results = response.json()

    auctions = results.get("itemSummaries", [])

    print("\nAuction search complete!")
    print("Auctions found:", len(auctions))

    for auction in auctions:

        print("\n----------------------------")
        print("Title:", auction.get("title", "Unknown"))

        price = auction.get("price", {})

        print(
            "Price:",
            price.get("value", "Unknown"),
            price.get("currency", "")
        )

        print("Buying options:", auction.get("buyingOptions", []))

        print("Ends:", auction.get("itemEndDate", "Not an auction"))

        print("URL:", auction.get("itemWebUrl", "Unknown")) 


if __name__ == "__main__":

    try:
        search_auctions()

    except requests.exceptions.RequestException as error:
        print("\nAPI connection error:")
        print(error)

        if error.response is not None:
            print(error.response.text)

    except Exception as error:
        print("\nUnexpected error:")
        print(error)
