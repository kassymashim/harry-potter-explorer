from flask import Flask, render_template, request, url_for
import requests, time

app = Flask(__name__)

HP_API_BASE = "https://hp-api.onrender.com/api"
CACHE_TTL_SEC = 15 * 60  # 15 minutes
_cache = {"characters": {"t": 0, "data": None}}

# ---------- Data Fetching & Caching ----------
def get_all_characters():
    """Fetch and cache the full list of characters from the HP API."""
    now = time.time()
    entry = _cache["characters"]
    if entry["data"] is not None and (now - entry["t"] < CACHE_TTL_SEC):
        return entry["data"]

    url = f"{HP_API_BASE}/characters"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()  # list of dicts

    norm = []
    for x in data:
        norm.append({
            "name": x.get("name") or "",
            "house": x.get("house") or "",
            "patronus": x.get("patronus") or "",
            "image": x.get("image") or "",
        })

    entry["data"] = norm
    entry["t"] = now
    return norm


# ---------- Static content ----------
HOUSES = [
    {"name": "Гриффиндор (Gryffindor)", "colors": ["#740001", "#d3a625"], "symbol": "🦁",
     "motto": "Храбрость, отвага и рыцарство",
     "blurb": "Дом, ценящий смелость, честность и готовность к подвигам. Основан Годриком Гриффиндором."},
    {"name": "Слизерин (Slytherin)", "colors": ["#1a472a", "#aaaaaa"], "symbol": "🐍",
     "motto": "Амбиции, находчивость и решительность",
     "blurb": "Дом амбициозных и целеустремлённых. Основан Салазаром Слизерином."},
    {"name": "Хаффлпафф (Hufflepuff)", "colors": ["#ecb939", "#372e29"], "symbol": "🦡",
     "motto": "Трудолюбие, верность и справедливость",
     "blurb": "Дом, где ценят честный труд, доброту и терпение. Основан Хельгой Хаффлпафф."},
    {"name": "Когтевран (Ravenclaw)", "colors": ["#0e1a40", "#946b2d"], "symbol": "🦅",
     "motto": "Мудрость, творчество и острый ум",
     "blurb": "Дом для любознательных и остроумных. Основан Ровеной Когтевран."},
]

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/houses")
def houses():
    return render_template("houses.html", houses=HOUSES)

@app.route("/characters")
def characters():
    q = (request.args.get("q") or "").strip().lower()
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    data = get_all_characters()
    if q:
        filtered = [c for c in data if q in c["name"].lower()]
    else:
        filtered = data

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    def page_url(p):
        return url_for("characters", q=q or None, page=p, page_size=page_size)

    prev_url = page_url(page - 1) if page > 1 else None
    next_url = page_url(page + 1) if end < total else None

    return render_template(
        "characters.html",
        items=items, total=total, page=page, page_size=page_size,
        q=(request.args.get("q") or ""), prev_url=prev_url, next_url=next_url
    )

if __name__ == "__main__":
    # Dev defaults for local run
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
