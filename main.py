from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Set odds configuration
set_odds = {
    "fin": {  # Final Fantasy
        "common": {"slots": 10, "poolSize": 100, "wildcardRate": 18, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 85, "wildcardRate": 50, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 15, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 20, "wildcardRate": 2.5, "wildcardCount": 2}
    },
    "tdm": {  # Tarkir: Dragonstorm
        "common": {"slots": 10, "poolSize": 100, "wildcardRate": 18, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 85, "wildcardRate": 50, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 15, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 20, "wildcardRate": 2.5, "wildcardCount": 2}
    },
    "dft": {  # Aetherdrift
        "common": {"slots": 10, "poolSize": 100, "wildcardRate": 17, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 80, "wildcardRate": 40, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 12, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 20, "wildcardRate": 2, "wildcardCount": 2}
    },
    "inr": {  # Innistrad Remastered
        "common": {"slots": 10, "poolSize": 110, "wildcardRate": 14, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 90, "wildcardRate": 38, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 50, "wildcardRate": 10, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 15, "wildcardRate": 2, "wildcardCount": 2}
    },
    "fdn": {  # Magic: The Gathering Foundations
        "common": {"slots": 10, "poolSize": 80, "wildcardRate": 20, "wildcardCount": 1},
        "uncommon": {"slots": 3, "poolSize": 40, "wildcardRate": 30, "wildcardCount": 1},
        "rare": {"baseRate": 100, "poolSize": 25, "wildcardRate": 0, "wildcardCount": 0},
        "mythic": {"baseRate": 0, "poolSize": 0, "wildcardRate": 0, "wildcardCount": 0}
    },
    "j25": {  # Foundations Jumpstart
        "common": {"slots": 10, "poolSize": 100, "wildcardRate": 0, "wildcardCount": 0},
        "uncommon": {"slots": 3, "poolSize": 60, "wildcardRate": 0, "wildcardCount": 0},
        "rare": {"baseRate": 100, "poolSize": 40, "wildcardRate": 0, "wildcardCount": 0},
        "mythic": {"baseRate": 0, "poolSize": 0, "wildcardRate": 0, "wildcardCount": 0}
    },
    "dsk": {  # Duskmourn: House of Horror
        "common": {"slots": 10, "poolSize": 95, "wildcardRate": 17, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 85, "wildcardRate": 42, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 11, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 25, "wildcardRate": 2.5, "wildcardCount": 2}
    },
    "blb": {  # Bloomburrow
        "common": {"slots": 10, "poolSize": 100, "wildcardRate": 18, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 90, "wildcardRate": 50, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 12, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 20, "wildcardRate": 2.5, "wildcardCount": 2}
    },
    "arc": {  # Assassin’s Creed
        "common": {"slots": 10, "poolSize": 90, "wildcardRate": 0, "wildcardCount": 0},
        "uncommon": {"slots": 3, "poolSize": 70, "wildcardRate": 0, "wildcardCount": 0},
        "rare": {"baseRate": 85, "poolSize": 50, "wildcardRate": 0, "wildcardCount": 0},
        "mythic": {"baseRate": 15, "poolSize": 20, "wildcardRate": 0, "wildcardCount": 0}
    },
    "mh3": {  # Modern Horizons 3
        "common": {"slots": 10, "poolSize": 105, "wildcardRate": 20, "wildcardCount": 2},
        "uncommon": {"slots": 3, "poolSize": 95, "wildcardRate": 50, "wildcardCount": 1},
        "rare": {"baseRate": 85, "poolSize": 60, "wildcardRate": 15, "wildcardCount": 2},
        "mythic": {"baseRate": 15, "poolSize": 25, "wildcardRate": 3, "wildcardCount": 2}
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

    try:
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
            "price": card.get("prices", {}).get("usd", None),
            "estimated_odds": f"{probability * 100:.2f}%",
            "image_url": card.get('image_uris', {}).get('normal', "")
            
        })

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
