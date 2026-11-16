
import os
import hashlib

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load our local environment variables
load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():

    return "eBay notification server is running!"


@app.route("/ebay/notifications", methods=["GET"])
def verify_endpoint():

    challenge_code = request.args.get("challenge_code")

    verification_token = os.getenv("EBAY_VERIFICATION_TOKEN")
    endpoint = os.getenv("EBAY_NOTIFICATION_ENDPOINT")

    if not challenge_code or not verification_token or not endpoint:

        return jsonify({
            "error": "Missing verification settings"
        }), 500

    # eBay requires this exact order:
    # challenge code + verification token + endpoint

    challenge_string = (
        challenge_code +
        verification_token +
        endpoint
    )

    challenge_response = hashlib.sha256(
        challenge_string.encode("utf-8")
    ).hexdigest()

    return jsonify({
        "challengeResponse": challenge_response
    }), 200


@app.route("/ebay/notifications", methods=["POST"])
def receive_notification():

    notification = request.get_json(silent=True)

    if not isinstance(notification, dict):

        return jsonify({
            "error": "Invalid notification"
        }), 400

    # Do not save or print the notification.
    # It may contain personal account information.

    print("eBay notification received.")

    return "", 200


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
