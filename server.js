
const express = require('express');
const app = express();
const PORT = 3000;
const fetch = require('node-fetch');

const setOdds = {
  tdm: {
    common: { slots: 7, poolSize: 80, wildcardRate: 17.78, wildcardCount: 2 },
    uncommon: { slots: 3, poolSize: 100, wildcardRate: 62.08, wildcardCount: 2 },
    rare: { baseRate: 85.7, poolSize: 60, wildcardRate: 17.35, wildcardCount: 2 },
    mythic: { baseRate: 14.3, poolSize: 20, wildcardRate: 2.7, wildcardCount: 2 }
  },
  // Add more sets here using same format as above
};

function calculateOdds(rarity, config) {
  if (!config) return 0;

  if (rarity === 'common' || rarity === 'uncommon') {
    const direct = 1 - Math.pow((1 - 1 / config.poolSize), config.slots);
    const wildcard = config.wildcardCount * (config.wildcardRate / 100) * (1 / config.poolSize);
    return 1 - ((1 - direct) * (1 - wildcard));
  } else if (rarity === 'rare' || rarity === 'mythic') {
    const direct = (config.baseRate / 100) * (1 / config.poolSize);
    const wildcard = config.wildcardCount * (config.wildcardRate / 100) * (1 / config.poolSize);
    return 1 - ((1 - direct) * (1 - wildcard));
  }

  return 0;
}

app.get('/', (req, res) => {
  res.send('Welcome! Use /check-card?name=CardName&set=SetCode');
});

app.get('/check-card', async (req, res) => {
  const { name, set } = req.query;

  if (!name || !set) {
    return res.status(400).json({ error: 'Card name and set code are required.' });
  }

  try {
    const response = await fetch(`https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}&set=${set}`);
    if (!response.ok) return res.status(404).json({ error: 'Card not found in specified set.' });

    const card = await response.json();
    const setCode = card.set.toLowerCase();
    const rarity = card.rarity;

    const setConfig = setOdds[setCode];
    if (!setConfig) {
      return res.status(400).json({ error: 'Set not supported yet. Add it to the configuration.' });
    }

    const rarityConfig = setConfig[rarity];
    const probability = calculateOdds(rarity, rarityConfig);

    res.json({
      card_name: card.name,
      set: card.set,
      in_set: true,
      rarity,
      estimated_odds: `${(probability * 100).toFixed(2)}%`
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error.' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running at http://localhost:${PORT}`);
});
