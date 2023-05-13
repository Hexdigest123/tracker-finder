from playwright.sync_api import sync_playwright
from flask import Flask, request
from flask_cors import CORS

IP = "0.0.0.0"
PORT = 80
CORS_ENABLED = False  # change to true if your request is being blocked by CORS
facebook_pixel_indicator = [
    "connect.facebook.net",
    "facebook pixel",
    "facebook-pixel",
    "pixelids"
]

app = Flask(__name__)
if CORS_ENABLED:
    CORS(app)


def search_tracker(url: str) -> object:
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        chrome_user = playwright.devices["Desktop Chrome"]
        browser = chromium.launch()
        context = browser.new_context(**chrome_user)
        context.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
        page = context.new_page()

        page.goto(url)
        gtag_found = True if page.content().find("googletagmanager") != -1 else False
        tiktok_found = True if page.content().find("analytics.tiktok.com") != -1 else False
        for indicator in facebook_pixel_indicator:
            facebook_found = True if page.content().lower().find(indicator) != -1 else False
            if facebook_found:
                break

        browser.close()
    return {"gtag": gtag_found, "tpixel": tiktok_found, "fpixel": facebook_found}


@app.route("/")
def index():
    return "<h1>This is a backend API</h1>"


@app.route("/scan", methods=["GET"])
def search():
    url = request.args.get("url").lower()
    return 200, search_tracker(url)


if __name__ == "__main__":
    app.run(host=IP, port=PORT)
    print(f"Running on https://{IP}:{PORT}")
