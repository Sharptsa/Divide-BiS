import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import base64
import unidecode

# Title and text box
st.set_page_config(layout="wide")
col = st.columns([0.17, 0.66, 0.17])[1]
col.title('Divide BiS')
col.checkbox('Mode français', key='fr')
col.text_input('Player, boss, item name or item ID' if not st.session_state.fr
               else "Joueur, boss, nom d'item ou ID d'item", key='query')

# Load and prepare data
df_items = pd.read_csv(r'data/items.csv')
legendaries = [46017, 49623]
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
                                        ' hm' if row.hm else ' nm']),
                          axis=1)
df_priorities.loc[df_priorities.boss.isna(), 'rank_in_queue'] = np.nan
df_priorities['legendary'] = df_priorities.item_id.isin(legendaries)
df_priorities['lootable'] = (df_priorities.boss.notna()) | (df_priorities.source == 'Craft') \
                                                         | (df_priorities.legendary)

# Clean data
df_priorities.hm = df_priorities.hm == True
df_priorities.raid_size = df_priorities.raid_size.fillna(-1).apply(int)
df_priorities.boss.fillna('', inplace=True)
df_priorities.loc[df_priorities.source == 'Craft', 'boss'] = 'ZZZ'
df_priorities.slot.fillna('', inplace=True)
non_lootable_ilvls = {284: [49623],
                      277: [50400, 52572, 50402],
                      264: [49894, 50454],
                      258: [46017],
                      245: [47673, 47570, 47664, 47666, 47668, 47661, 47665, 47587,
                            47733, 47670],
                      238: [42853, 42608],
                      232: [45825, 45564, 45553, 45551, 45561, 45560],
                      213: [40207, 40321, 40342, 40432, 40255, 40267, 39728],
                      200: [40713, 40705, 40709, 42987, 44253, 40708, 44255],
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
                      45551: 'https://wow.zamimg.com/images/wow/icons/large/inv_belt_45a.jpg',
                      45561: 'https://wow.zamimg.com/images/wow/icons/large/inv_boots_plate_01.jpg',
                      39728: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg',
                      40708: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_unrelentingstorm.jpg',
                      45560: 'https://wow.zamimg.com/images/wow/icons/large/inv_boots_plate_06.jpg',
                      44255: 'https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg',
                      47673: 'https://wow.zamimg.com/images/wow/icons/large/inv_shield_56.jpg',
                      47570: 'https://wow.zamimg.com/images/wow/icons/large/inv_bracer_32a.jpg',
                      47664: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg',
                      47666: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_diseasecleansingtotem.jpg',
                      47668: 'https://wow.zamimg.com/images/wow/icons/large/inv_qirajidol_strife.jpg',
                      47661: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg',
                      47665: 'https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg',
                      47587: 'https://wow.zamimg.com/images/wow/icons/large/inv_bracer_37.jpg',
                      47733: 'https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_57.jpg',
                      47670: 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofrejuvenation.jpg',
                      49894: 'https://wow.zamimg.com/images/wow/icons/large/inv_boots_leather_8.jpg',
                      50400: 'https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_85.jpg',
                      50454: 'https://wow.zamimg.com/images/wow/icons/large/trade_herbalism.jpg',
                      52572: 'https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_81.jpg',
                      50402: 'https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_81.jpg',
                      49623: 'https://wow.zamimg.com/images/wow/icons/large/inv_axe_113.jpg'}
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
                             45551: 'Ceinturon indestructible en plaques',
                             45561: 'Bottines de la destinée',
                             39728: 'Totem de détresse',
                             40708: 'Totem du plan élémentaire',
                             45560: 'Dispensateurs de mort à pointes',
                             44255: 'Carte de Sombrelune : Grandeur',
                             47673: 'Cachet de virulence',
                             47570: 'Brise-épée en saronite',
                             47664: 'Libram de défiance',
                             47666: 'Totem du vent électrifiant',
                             47668: 'Idole de mutilation',
                             47661: 'Libram de vaillance',
                             47665: 'Totem des marées calmantes',
                             47587: 'Brassards royaux en voile lunaire',
                             47733: 'Cercle du réparacoeur',
                             47670: 'Idole de la fureur lunaire',
                             49894: 'Bottes cénariennes bénies',
                             50400: 'Bague de sagesse sans fin du Verdict des cendres',
                             50454: 'Idole du saule noir',
                             52572: 'Bague de puissance sans fin du Verdict des cendres',
                             50402: 'Bague de vengeance sans fin du Verdict des cendres',
                             49623: 'Deuillelombre'}
    df_priorities.item_name = df_priorities.apply(lambda row: row.item_name
                                                  if pd.notna(row.item_name)
                                                  else non_lootable_names_fr[row.item_id],
                                                  axis=1)
df_priorities.rank_in_queue = df_priorities.rank_in_queue.fillna('') \
                                           .apply(lambda x: int(x) if x else x)
df_priorities['TOC'] = df_priorities.boss.apply(lambda x: any([val in x for val in
                                                ['Beasts', 'Bêtes',
                                                 'Jaraxxus',
                                                 'Champions',
                                                 'Twin', 'Jumelles',
                                                 'Anub',
                                                 'Tribute', 'offrande']]))
df_priorities['ICC'] = df_priorities.apply(lambda row: any([val in row.boss for val in
                                                  ['Marrowgar', 'Gargamoelle',
                                                   'Deathwhisper', 'Murmemort',
                                                   'Gunship', 'Cannonière',
                                                   'Saurfang', 'Saurcroc',
                                                   'Festergut', 'Pulentraille',
                                                   'Rotface', 'Trognepus',
                                                   'Putricide',
                                                   'Prince Council', 'Conseil des Princes',
                                                   "Lana'thel",
                                                   'Valithria',
                                                   'Sindragosa',
                                                   'Lich King', 'Roi-Liche',
                                                   'ICC']])
                                                or row.item_id == 49623,
                                                axis=1)
df_priorities.loc[df_priorities.received == 'X', 'received'] = 1.
df_priorities.loc[df_priorities.received == 'SOLO', 'received'] = 0.5
df_priorities.loc[df_priorities.received.isna(), 'received'] = 0.
df_priorities.loc[~df_priorities.lootable, 'received'] = -1.
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
def display_df(mask, how='standard', min_glow=277):
    to_display = df_priorities.sort_values(['ICC', 'TOC', 'lootable', 'legendary',
                                            'boss', 'raid_size', 'hm',
                                            'ilvl', 'item_name', 'item_id', 'received',
                                            'player'],
                                           ascending=[False, False, False, False,
                                                      True, True, True,
                                                      True, True, True, False,
                                                      True])
    to_display = to_display.loc[mask, ['source', 'item_name', 'ilvl', 'player', 'received',
                                       'icon', 'item_id']]
    if how == 'player':
        to_display = df_priorities.sort_values(['player', 'lootable', 'received',
                                                'ilvl', 'ICC', 'TOC', 'legendary', 'item_name', 'item_id',
                                                'boss', 'raid_size', 'hm'],
                                               ascending=[True, False, False,
                                                          False, False, False, False, True, True,
                                                          True, True, True])
        to_display = to_display.loc[mask, ['player', 'item_name', 'ilvl', 'source', 'received',
                                           'icon', 'item_id']]

    def glow_fnc(row):
        if row.received not in ['Yes', 'Oui', 'Solo']:
            return row.received
        elif row.item_id in legendaries:
            return row.received + ' leg'
        elif row.ilvl >= min_glow:
            return row.received + ' glow'
        else:
            return row.received + ' noglow'

    def item_name_icon_hyperlink_fnc(row):
        return f'<a href="https://www.wowhead.com/wotlk{"/fr" if st.session_state.fr else ""}/item={row.item_id}" style="text-decoration: none; color: white;"><img src="{row.icon}" width="22" > {row.item_name}</a>'

    to_display.loc[to_display.received == 1., 'received'] = 'Oui' if st.session_state.fr else 'Yes'
    to_display.loc[to_display.received == 0.5, 'received'] = 'Solo'
    to_display.loc[to_display.received == 0., 'received'] = 'Non' if st.session_state.fr else 'No'
    to_display.loc[to_display.received == -1., 'received'] = ''
    to_display.received = to_display.apply(glow_fnc, axis=1)
    to_display.source = to_display.source.apply(lambda x: x.replace(' nm', ''))
    to_display.item_name = to_display.apply(item_name_icon_hyperlink_fnc, axis=1)
    to_display.drop(['icon', 'item_id'], axis=1, inplace=True)
    columns_rename = {'source': 'Source', 'item_name': 'Item',
                      'ilvl': 'ilvl', 'player': 'Player', 'received': 'Received'}
    if st.session_state.fr:
        columns_rename = {'source': 'Source', 'item_name': 'Item',
                          'ilvl': 'ilvl', 'player': 'Joueur', 'received': 'Reçu'}
    to_display.columns = [columns_rename[c] for c in to_display.columns]

    html_block = to_display.to_html(escape=False, index=False) \
                .replace('<tr>','<tr style = "background-color: rgba(40, 40, 40, 1.0); color: white">') \
                .replace('<th>','<th style = "background-color: rgba(90, 90, 90, 1.0); color: white; text-align: center">') \
                .replace('Yes noglow','<span style="color: rgba(37, 153, 37, 1.0)">Yes</span>') \
                .replace('Oui noglow','<span style="color: rgba(37, 153, 37, 1.0)">Oui</span>') \
                .replace('Solo noglow','<span style="color: rgba(37, 153, 37, 1.0)">Solo</span>') \
                .replace('Yes glow','<span style="color: rgba(255, 215, 0, 1.0)">Yes</span>') \
                .replace('Oui glow','<span style="color: rgba(255, 215, 0, 1.0)">Oui</span>') \
                .replace('Solo glow','<span style="color: rgba(255, 215, 0, 1.0)">Solo</span>') \
                .replace('Yes leg','<span style="color: rgba(255, 128, 0, 1.0)">Yes</span>') \
                .replace('Oui leg','<span style="color: rgba(255, 128, 0, 1.0)">Oui</span>') \
                .replace('Solo leg','<span style="color: rgba(255, 128, 0, 1.0)">Solo</span>')
    if st.session_state.fr:
        html_block = html_block.replace('Legendary', 'Légendaire') \
                               .replace('Emblems of Conquest', 'Emblèmes de Conquête') \
                               .replace('Emblems of Triumph', 'Emblèmes de Triomphe')

    # New code with tooltip
    # html_string = '''
    # <script language="javascript">
    # const whTooltips = {colorLinks: true, iconizeLinks: false, renameLinks: false}
    # </script>
    # <script src="https://wow.zamimg.com/js/tooltips.js"></script>
    # '''
    # with col:
    #     components.html(html_block + html_string)

    col.markdown(html_block, unsafe_allow_html=True) # old code without tooltip


# Manage query
if st.session_state.query == '': # No query
    display_df(pd.Series(True, index=df_priorities.index))

else:

    def approx_fnc(x):
        return unidecode.unidecode(x).lower()

    mask_player = df_priorities.player.apply(approx_fnc).str.contains(approx_fnc(st.session_state.query))
    mask_item_name = df_priorities.item_name.apply(approx_fnc).str.contains(approx_fnc(st.session_state.query))
    mask_item_id = df_priorities.item_id.apply(str) == st.session_state.query
    mask_source = pd.DataFrame([df_priorities.source.apply(approx_fnc).str.contains(q) \
                                for q in approx_fnc(st.session_state.query).split()]).all()

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
