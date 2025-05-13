from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Set odds configuration
set_odds = {
    "tdm": {
        "common": {"slots": 7, "poolSize": 80, "wildcardRate": 17.78, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 100, "wildcardRate": 62.08, "wildcardCount": 2},
        "rare": {"baseRate": 85.7, "poolSize": 60, "wildcardRate": 17.35, "wildcardCount": 2},
        "mythic": {"baseRate": 14.3, "poolSize": 20, "wildcardRate": 2.7, "wildcardCount": 2}
    }
}

def calculate_odds(rarity, config):
    if not config:
        return 0
    if rarity in ["common", "uncommon"]:
        direct = 1 - (1 - 1 / config["poolSize"]) ** config["slots"]
        wildcard = config["wildcardCount"] * (config["wildcardRate"] / 100) * (1 / config["poolSize"])
        return 1 - ((1 - direct) * (1 - wildcard))
    elif rarity in ["rare", "mythic"]:
        direct = (config["baseRate"] / 100) * (1 / config["poolSize"])
        wildcard = config["wildcardCount"] * (config["wildcardRate"] / 100) * (1 / config["poolSize"])
        return 1 - ((1 - direct) * (1 - wildcard))
    return 0

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/check-card')
def check_card():
    name = request.args.get('name')
    set_code = request.args.get('set')
    if not name or not set_code:
        return jsonify({"error": "Card name and set code are required"}), 400

    r = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={name}&set={set_code}')
    if r.status_code != 200:
        return jsonify({"error": "Card not found in the specified set"}), 404

    card = r.json()
    rarity = card['rarity']
    config = set_odds.get(set_code.lower(), {}).get(rarity)
    probability = calculate_odds(rarity, config)

    return jsonify({
        "card_name": card['name'],
        "set": card['set'],
        "rarity": rarity,
        "estimated_odds": f"{probability * 100:.2f}%"
    })

if __name__ == '__main__':
    app.run(debug=True)
