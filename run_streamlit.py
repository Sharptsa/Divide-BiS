import streamlit as st
import pandas as pd
import numpy as np
import base64

# Title and text box
st.set_page_config(layout="wide")
col = st.columns([0.18, 0.64, 0.18])[1]
col.title('Divide BiS')
col.checkbox('Mode français', key='fr')
col.text_input('Player, boss, item name or item ID' if not st.session_state.fr
               else "Joueur, boss, nom d'item ou ID d'item", key='query')

# Load and prepare data
df_items = pd.read_csv(r'data/items.csv')
if st.session_state.fr:
    df_items.item_name = df_items.item_name_fr
    df_items.boss = df_items.boss_fr

df_priorities = pd.read_excel(r'data/players_priorities.xlsx')
left, right = (df_priorities, df_items.drop(['item_name', 'drops_per_id'], axis=1)) \
              if not st.session_state.fr \
              else (df_priorities.drop('item_name', axis=1), df_items.drop('drops_per_id', axis=1))
df_priorities = pd.merge(left, right,
                         how='left', on='item_id')
df_priorities['source'] = df_priorities.apply(lambda row: row.rank_in_queue if pd.isna(row.boss)
                          else ''.join([row.boss, ' ' + str(int(row.raid_size)),
                                        ' hm' if row.hm else '']),
                          axis=1)
df_priorities.loc[df_priorities.boss.isna(), 'rank_in_queue'] = np.nan
df_priorities['lootable'] = df_priorities.boss.notna()

# Clean data
df_priorities.hm = df_priorities.hm == True
df_priorities.raid_size = df_priorities.raid_size.fillna(-1).apply(int)
df_priorities.boss.fillna('', inplace=True)
df_priorities.slot.fillna('', inplace=True)
non_lootable_ilvls = {258: [46017],
                      238: [42853, 42608],
                      232: [45825, 45564, 45553, 45551],
                      213: [40207, 40321, 40342, 40432, 40255, 40267],
                      200: [40713, 40705, 40709, 42987, 44253],
                      187: [37111]}
non_lootable_ilvls = {v: k for k in non_lootable_ilvls for v in non_lootable_ilvls[k]}
df_priorities.ilvl = df_priorities.apply(lambda row: int(row.ilvl)
                                         if pd.notna(row.ilvl)
                                         else non_lootable_ilvls[row.item_id],
                                         axis=1)
non_lootable_icons = {37111: 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_orb_03.jpg',
                      40207: 'https://wow.zamimg.com/images/wow/icons/large/inv_shield_56.jpg',
                      40255: 'https://wow.zamimg.com/images/wow/icons/large/inv_trinket_naxxramas03.jpg',
                      40267: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_diseasecleansingtotem.jpg',
                      40321: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofrejuvenation.jpg',
                      40342: 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_thegoldencheep.jpg',
                      40432: 'https://wow.zamimg.com/images/wow/icons/large/inv_offhand_hyjal_d_01.jpg',
                      40705: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofgrace.jpg',
                      40709: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_totemoflife.jpg',
                      40713: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofferocity.jpg',
                      42608: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg',
                      42853: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg',
                      42987: 'https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg',
                      44253: 'https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg',
                      45553: 'https://wow.zamimg.com/images/wow/icons/large/inv_belt_13.jpg',
                      45564: 'https://wow.zamimg.com/images/wow/icons/large/inv_boots_leather01.jpg',
                      45825: 'https://wow.zamimg.com/images/wow/icons/large/inv_belt_48a.jpg',
                      46017: 'https://wow.zamimg.com/images/wow/icons/large/inv_mace_99.jpg',
                      45551: 'https://wow.zamimg.com/images/wow/icons/large/inv_belt_45a.jpg'}
df_priorities.icon = df_priorities.apply(lambda row: row.icon
                                         if pd.notna(row.icon)
                                         else non_lootable_icons[row.item_id],
                                         axis=1)
if st.session_state.fr:
    non_lootable_names_fr = {37111: "Protecteur d'âme",
                             40207: 'Cachet de vigilance',
                             40255: 'Malédiction du mourant',
                             40267: 'Totem de maléfice',
                             40321: "Idole de l'étoile filante",
                             40342: "Idole d'éveil",
                             40432: "Représentation de l'Âme des dragons",
                             40705: 'Libram de renouveau',
                             40709: 'Totem de croissance forestière',
                             40713: 'Idole de la bête vorace',
                             42608: "Totem d'indomptabilité du gladiateur furieux",
                             42853: 'Libram de robustesse du gladiateur furieux',
                             42987: 'Carte de Sombrelune : Grandeur',
                             44253: 'Carte de Sombrelune : Grandeur',
                             45553: 'Ceinture des dragons',
                             45564: 'Souliers de silence',
                             45825: 'Ceinturon garde-écu',
                             46017: "Val'anyr, le marteau des anciens rois",
                             45551: 'Ceinturon indestructible en plaques'}
    df_priorities.item_name = df_priorities.apply(lambda row: row.item_name
                                                  if pd.notna(row.item_name)
                                                  else non_lootable_names_fr[row.item_id],
                                                  axis=1)
df_priorities.rank_in_queue = df_priorities.rank_in_queue.fillna('') \
                                           .apply(lambda x: int(x) if x else x)
df_priorities.loc[df_priorities.received.notna(), 'received'] = \
                                        'No' if not st.session_state.fr else 'Non'
df_priorities.loc[df_priorities.received.isna(), 'received'] = \
                                        'Yes' if not st.session_state.fr else 'Oui'
df_priorities.loc[~df_priorities.lootable, 'received'] = ''
df_priorities = df_priorities.sort_values(['boss', 'raid_size', 'hm', 'ilvl', 'item_name']) \
                                                                    .reset_index(drop=True)


# Add background image
def add_background():
    with open(r'data/background.jpg', 'rb') as img_file:
        encoded_string = base64.b64encode(img_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )


add_background()


# Display dataframe
def display_df(mask, how='standard'):
    to_display = df_priorities.sort_values(['lootable', 'boss', 'raid_size', 'hm',
                                            'ilvl', 'item_name', 'item_id', 'received',
                                            'player'],
                                           ascending=[False, True, True, True,
                                                      True, True, True, False,
                                                      True])
    to_display = to_display.loc[mask, ['source', 'item_name', 'ilvl', 'player', 'received', 'icon']]
    if how == 'player':
        to_display = df_priorities.sort_values(['player', 'lootable', 'received',
                                                'ilvl', 'item_name', 'item_id',
                                                'boss', 'raid_size', 'hm'],
                                               ascending=[True, False, False,
                                                          False, True, True,
                                                          True, True, True])
        to_display = to_display.loc[mask, ['player', 'item_name', 'ilvl', 'source', 'received', 'icon']]

    to_display.item_name = to_display.icon.apply(lambda x: '<img src="' + x + '" width="22" > ') \
                                                                        + to_display.item_name
    to_display.drop('icon', axis=1, inplace=True)
    columns_rename = {'source': 'Source', 'item_id': 'Item ID', 'item_name': 'Item',
                      'ilvl': 'ilvl', 'player': 'Player', 'received': 'Received'}
    if st.session_state.fr:
        columns_rename = {'source': 'Source', 'item_id': "ID d'item'", 'item_name': 'Item',
                          'ilvl': 'ilvl', 'player': 'Joueur', 'received': 'Reçu'}
    to_display.columns = [columns_rename[c] for c in to_display.columns]

    col.markdown(to_display.to_html(escape=False, index=False) \
                .replace('<tr>','<tr style = "background-color: rgba(40, 40, 40, 1.0); color: white">')
                .replace('<th>','<th style = "background-color: rgba(90, 90, 90, 1.0); color: white; text-align: center">')
                .replace('Yes','<span style="color: rgba(37, 153, 37, 1.0)">Yes</span>')
                .replace('Oui','<span style="color: rgba(37, 153, 37, 1.0)">Oui</span>')
                , unsafe_allow_html=True)


# Manage query
if st.session_state.query == '': # No query
    display_df(pd.Series(True, index=df_priorities.index))

else:
    mask_player = df_priorities.player.str.lower().str.contains(st.session_state.query.lower())
    mask_item_name = df_priorities.item_name.str.lower().str.contains(st.session_state.query.lower())
    mask_item_id = df_priorities.item_id.apply(str).str.contains(st.session_state.query)
    mask_source = pd.DataFrame([df_priorities.source.str.lower().str.contains(q) \
                                for q in st.session_state.query.lower().split()]).all()

    masks = [mask_player, mask_item_name, mask_item_id, mask_source]
    mask = pd.DataFrame(masks).any()
    n_activated_masks = sum([m.sum() > 0 for m in masks])

    if n_activated_masks >= 2: # standard display
        display_df(mask)

    elif mask_player.sum() > 0: # player
        display_df(mask, how='player')

    elif mask_item_name.sum() > 0: # item_name
        display_df(mask, how='item')

    elif mask_item_id.sum() > 0: # item_id
        display_df(mask, how='item')

    elif mask_source.sum() > 0: # source
        display_df(mask)

# Add footer
footer_txt = 'Want to join us ? Contact us on our' \
             if not st.session_state.fr \
             else 'Vous voulez nous rejoindre ? Contactez-nous sur notre'
footer_link_txt = 'discord server' \
                  if not st.session_state.fr \
                  else 'serveur discord'
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
height: 4%;
background-color: rgba(200, 200, 200, 1.0);
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>""" + footer_txt + """ <a style='text-align: center;' href="https://discord.gg/WkPu3G8bmp" target="_blank">""" + footer_link_txt + """</a> !</p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

# todo: insert new player priorities
# todo: update after loots
