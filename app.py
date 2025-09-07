import mimetypes
import os
import random
import requests
from urllib.parse import urlparse
from flask import Flask, render_template, jsonify, request, Response, abort

app = Flask(__name__)

games = [
    {"name": "Forsaken",       "image": "https://i.imgur.com/tMGN1J6.png"},
    {"name": "Undertale",      "image": "https://i.imgur.com/YskHOsA.png"},
    {"name": "Geometry Dash",  "image": "https://i.imgur.com/veRx1kd.png"},
    {"name": "Wordle",         "image": "https://i.imgur.com/Eq9EwdF.png"},
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/randomgame")
def random_game():
    return jsonify(random.choice(games))

# 이미지 프록시
@app.route("/img")
def img_proxy():
    url = request.args.get("url", "").strip()
    if not url:
        abort(400, "missing url")

    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        abort(400, "invalid scheme")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "",
            # PNG, JPEG, WEBP 등 이미지 우선 수락
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        }
        r = requests.get(url, headers=headers, timeout=8, stream=True)
        r.raise_for_status()

        # 1) 원본 응답의 Content-Type 우선
        content_type = r.headers.get("Content-Type")
        # 2) 비어있으면 URL 확장자로 추정 (예: .png → image/png)
        if not content_type:
            guessed, _ = mimetypes.guess_type(url)
            content_type = guessed or "application/octet-stream"

        return Response(
            r.content,
            200,
            headers={
                "Content-Type": content_type,
                "Cache-Control": "public, max-age=86400",
                "Content-Disposition": "inline",
            },
        )
    except requests.RequestException as e:
        abort(502, f"upstream error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002)) # Render가 주는 PORT 사용
    app.run(host="0.0.0.0", port=port, debug=False)