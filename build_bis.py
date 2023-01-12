from selenium import webdriver
import re
import time
import numpy as np
import pandas as pd


def get_items_from_eightyupgrades(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)

    elems = re.findall('gear-slot_itemName__[A-Z0-9]* item-(?:epic|rare|legendary).*?</a>',
                                                            driver.page_source)
    driver.close()

    slots = np.array([int(re.findall('equippedSlotId&quot;:([0-9]*)', e)[0])
                                                            for e in elems])
    wanted_slots = [1, 2, 3, 15, 5, 9, 16, 10, 6, 7, 8, 11, 12, 13, 14, 18]
    accepted_slots = wanted_slots + [17]
    assert all([s in slots for s in wanted_slots])
    mask = np.isin(slots, accepted_slots)

    slots = slots[mask]
    ids = np.array([int(re.findall('item=([0-9]*)', e)[0]) for e in elems])[mask]
    names = np.array([re.findall('>(.*?)<', e)[0] for e in elems], dtype='<U50')[mask]

    def convert_tier_to_token(item_slot, item_name):
        assert item_slot in [1, 3, 5, 10, 7] and 'Conqueror' in item_name
        if 'Deathbringer' in item_name or 'Aegis' in item_name \
                                       or 'Sanctification' in item_name:
            # Warlock / Paladin / Priest
            if item_slot == 1: # Head
                return 45638, 'Crown of the Wayward Conqueror'
            elif item_slot == 3: # Shoulder
                return 45656, 'Mantle of the Wayward Conqueror'
            elif item_slot == 5: # Chest
                return 45632, 'Breastplate of the Wayward Conqueror'
            elif item_slot == 10: # Hands
                return 45641, 'Gauntlets of the Wayward Conqueror'
            elif item_slot == 7: # Legs
                return 45653, 'Legplates of the Wayward Conqueror'

        elif 'Worldbreaker' in item_name or 'Siegebreaker' in item_name \
                                         or 'Scourgestalker' in item_name:
            # Shaman / Warrior / Hunter
            if item_slot == 1: # Head
                return 45639, 'Crown of the Wayward Protector'
            elif item_slot == 3: # Shoulder
                return 45657, 'Mantle of the Wayward Protector'
            elif item_slot == 5: # Chest
                return 45633, 'Breastplate of the Wayward Protector'
            elif item_slot == 10: # Hands
                return 45642, 'Gauntlets of the Wayward Protector'
            elif item_slot == 7: # Legs
                return 45654, 'Legplates of the Wayward Protector'

        elif 'Terrorblade' in item_name or 'Darkruned' in item_name \
             or 'Kirin Tor' in item_name or 'Nightsong' in item_name:
            # Rogue / DK / Mage / Druid
            if item_slot == 1: # Head
                return 45640, 'Crown of the Wayward Vanquisher'
            elif item_slot == 3: # Shoulder
                return 45658, 'Mantle of the Wayward Vanquisher'
            elif item_slot == 5: # Chest
                return 45634, 'Breastplate of the Wayward Vanquisher'
            elif item_slot == 10: # Hands
                return 45643, 'Gauntlets of the Wayward Vanquisher'
            elif item_slot == 7: # Legs
                return 45655, 'Legplates of the Wayward Vanquisher'

        else:
            raise Warning('Unrecognized class')

    for i, n in enumerate(names):
        if 'Conqueror' in n:
            ids[i], names[i] = convert_tier_to_token(slots[i], n)
        elif n in ['Drape of the Skyborn', 'Sunglimmer Cloak', "Brann's Signet Ring",
                                                                'Starshine Circle']:
            ids[i], names[i] = 46053, 'Reply-Code Alpha'
        elif n in ['Drape of the Skyherald', 'Sunglimmer Drape', "Brann's Sealing Ring",
                                                                    'Starshine Signet']:
            ids[i], names[i] = 46052, 'Reply-Code Alpha'

    return ids, names


def get_items_from_text(txt):
    ids = np.array([int(line.split()[0]) for line in txt.split('\n')])
    names = np.array([' '.join(line.split()[1:]) for line in txt.split('\n')],
                                                                dtype='<U50')

    return ids, names


def get_items(player):
    with open(rf'data/players/{player}.txt', 'r') as f:
        content = f.read()

    if 'eightyupgrades' in content:
        return get_items_from_eightyupgrades(content)

    return get_items_from_text(content)


def build_bis(players):
    res = [get_items(p) for p in players]
    player_dfs = [pd.DataFrame({'player': p,
                                'item_id': res[i][0],
                                'item_name': res[i][1]})
                               for i, p in enumerate(players)]
    df = pd.concat(player_dfs)
    df.to_csv(r'data/players_bis.csv', index=False)
