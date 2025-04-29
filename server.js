const express = require('express');
const app = express();
const PORT = 3000;


app.get('/', (req, res) => {
  res.send('Welcome! Use /check-card?name=CardName');
});

app.get('/check-card', async (req, res) => {
  const { name } = req.query;
  if (!name) return res.status(400).json({ error: 'Card name is required.' });

  try {
    const response = await fetch(`https://api.scryfall.com/cards/named?fuzzy=${encodeURIComponent(name)}`);
    if (!response.ok) return res.status(404).json({ error: 'Card not found.' });
    const card = await response.json();

    if (card.set !== 'fdn') {
      return res.json({ card_name: card.name, in_set: false });
    }

    const rarity = card.rarity;
    let probability = 0;

    if (rarity === 'common') {
      const commonSlot = 1 - Math.pow((1 - 1/80), 7);
      const wildcardSlot = 2 * (17.78/100) * (1/80);
      probability = commonSlot + wildcardSlot;
    } else if (rarity === 'uncommon') {
      const uncommonSlot = 1 - Math.pow((1 - 1/100), 3);
      const wildcardSlot = 2 * (62.08/100) * (1/100);
      probability = uncommonSlot + wildcardSlot;
    } else if (rarity === 'rare') {
      const rareSlot = (85.7/100) * (1/60);
      const wildcardSlot = 2 * (17.35/100) * (1/60);
      probability = rareSlot + wildcardSlot;
    } else if (rarity === 'mythic') {
      const mythicSlot = (14.3/100) * (1/20);
      const wildcardSlot = 2 * (2.7/100) * (1/20);
      probability = mythicSlot + wildcardSlot;
    }

    res.json({
      card_name: card.name,
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
