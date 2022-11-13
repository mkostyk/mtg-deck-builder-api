# Quick temporary API documentation

Better documentation is on its way. It will come soon. Maybe. \
Also, this will probably change a lot, so do not get too familiar with it.

## About response codes
I could make some list here, but c'mon, you all know it - 2XX good, 4XX bad

## GET cards/ - Get list of cards
- id - card ID
- name - card name
- type - card type

### Maximum cards returned: 10

### Examples:
```GET http://127.0.0.1:8000/cards/?name=elf&type=creature``` \
```GET http://127.0.0.1:8000/cards/?id=1111```

### Response example: 
```
[
    {
        "id": 1111,
        "scryfall_id": "5d6178ed-6353-4733-81e1-7b3dc592c3bd",
        "card_name": "Aether Tunnel",
        "card_faces": null,
        "keywords": "Enchant",
        "image_uri": "https://cards.scryfall.io/normal/front/5/d/5d6178ed-6353-4733-81e1-7b3dc592c3bd.jpg?1562302252",
        "mana_cost": "{1}{U}",
        "cmc": "2.0",
        "loyalty": null,
        "power": null,
        "toughness": null,
        "type_line": "Enchantment — Aura",
        "card_text": "Enchant creature\nEnchanted creature gets +1/+0 and can't be blocked.",
        "color_identity": "U",
        "legalities": {
            "duel": "legal",
            "brawl": "not_legal",
            "penny": "not_legal",
            "future": "not_legal",
            "legacy": "legal",
            "modern": "legal",
            "pauper": "not_legal",
            "alchemy": "not_legal",
            "pioneer": "legal",
            "vintage": "legal",
            "explorer": "legal",
            "historic": "legal",
            "standard": "not_legal",
            "commander": "legal",
            "gladiator": "legal",
            "oldschool": "not_legal",
            "premodern": "not_legal",
            "historicbrawl": "legal",
            "paupercommander": "not_legal"
        },
        "rulings_uri": "https://api.scryfall.com/cards/5d6178ed-6353-4733-81e1-7b3dc592c3bd/rulings",
        "rarity": "uncommon",
        "flavor_text": "If you can't find a doorway, make one.",
        "artist": "Lucas Graciano",
        "edhrec_rank": 5236,
        "prices": {
            "eur": "0.49",
            "tix": "0.03",
            "usd": "0.24",
            "eur_foil": "0.39",
            "usd_foil": "0.88",
            "usd_etched": "None"
        }
    }
]
```

## GET decks/ - Get list of decks
- id - deck ID
- name - deck name
- user - user ID

### Examples:
```GET http://127.0.0.1:8000/decks/?id=3``` \
```GET http://127.0.0.1:8000/decks/?user_id=1&name=Test Deck```

### Response example:
```
[
    {
        "id": 1,
        "name": "Test Deck #1",
        "user_id": 1,
        "private": false
    },
    {
        "id": 3,
        "name": "Test Deck #3",
        "user_id": 1,
        "private": false
    }
]
```

## GET cardsInDeck/ - Get list of cards in a particular deck

- deck_id - deck ID

### Example:
```GET http://127.0.0.1:8000/cardsInDeck/?deck_id=1```

### Response example:
```
[
    {
        "id": 1,
        "deck_id": 1,
        "card_id": 2137
    },
    {
        "id": 2,
        "deck_id": 1,
        "card_id": 24567
    }
]
```

## POST - decks/ - Add a new deck

Requires authentication (Basic AUTH) - Tokens will come. Maybe.

- name - deck name
- user_id - id of creator
- private - boolean saying if deck is private or not

### Example:
```POST http://127.0.0.1:8000/decks/```

### Body example:
```
{
	"name": "Testing again",
	"user_id": 5,
	"private": false
}
```

### Response example:
```
{
    "id": 9,
    "name": "Testing again",
    "user_id": 5,
    "private": false
}
```

## POST - cardsInDeck/ - Add a new card to a deck

Requires authentication (Basic AUTH) - Tokens will come. Maybe.

- deck_id - deck to which card should be added
- card_id - id of card that should be added

### Example:
```POST http://127.0.0.1:8000/cardsInDeck/```

### Body example:
```
{
	"deck_id": 9,
	"card_id": 1115
}
```

### Response example:
```
{
    "id": 6,
    "deck_id": 9,
    "card_id": 1115
}
```