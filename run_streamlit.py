import streamlit as st
import pandas as pd
import numpy as np
import base64

st.set_page_config(layout="wide")
col = st.columns([0.19, 0.62, 0.19])[1]

# Load and prepare data
df_items = pd.read_csv(r'data/items.csv')
df_priorities = pd.read_csv(r'data/players_priorities.csv')
df_priorities = pd.merge(df_priorities, df_items.drop(['item_name', 'drops_per_id'], axis=1),
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
                      238: [42853, 42608,],
                      232: [45825, 45564, 45553],
                      213: [40207, 40321, 40342, 40432, 40255, 40267],
                      200: [40713, 40705, 40709, 42987, 44253],
                      187: [37111]}
non_lootable_ilvls = {v: k for k in non_lootable_ilvls for v in non_lootable_ilvls[k]}
df_priorities.ilvl = df_priorities.apply(lambda row: int(row.ilvl)
                                         if pd.notna(row.ilvl)
                                         else non_lootable_ilvls[row.item_id],
                                         axis=1)
df_priorities.rank_in_queue = df_priorities.rank_in_queue.fillna('') \
                                           .apply(lambda x: int(x) if x else x)
df_priorities = df_priorities.sort_values(['boss', 'raid_size', 'hm', 'ilvl', 'item_name']) \
                                                                            .reset_index()


# def style_df(row):
#     style = np.array([''] * len(row), dtype='<U32')
#     if row.rank_in_queue == 1:
#         style[row.index == 'rank_in_queue'] = 'background-color: green'
#     return list(style)
# df_priorities.style.apply(lambda row: style_df(row), axis = 1)


# Title and text box
col.title('Divide BiS')
col.text_input('Enter player, boss, item name or item ID', key='query')


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
    if how == 'standard':
        to_display = df_priorities.sort_values(['boss', 'raid_size', 'hm', 'ilvl',
                                                'item_name', 'item_id']) \
                     .loc[mask & (df_priorities.rank_in_queue == 1),
                          ['source', 'item_name', 'ilvl', 'player', 'rank_in_queue']]

    elif how == 'player':
        to_display = df_priorities.sort_values(['lootable', 'rank_in_queue', 'ilvl',
                                                'boss', 'raid_size', 'hm'],
                                               ascending=[False, True, False,
                                                          True, True, True]) \
                     .loc[mask, ['player', 'item_name', 'ilvl',
                                              'source', 'rank_in_queue']]

    elif how == 'item':
        to_display = df_priorities.sort_values(['lootable', 'boss', 'raid_size', 'hm', 'ilvl',
                                                'item_name', 'rank_in_queue', 'player'],
                                               ascending=[False, True, True, True, True,
                                                          True, True, True, True]) \
                     .loc[mask, ['source', 'item_name', 'ilvl', 'player', 'rank_in_queue']]

    columns_rename = {'source': 'Source', 'item_id': 'Item ID', 'item_name': 'Item name',
                      'ilvl': 'ilvl', 'player': 'Player', 'rank_in_queue': 'Obtained in'}
    to_display.columns = [columns_rename[c] for c in to_display.columns]

    col.dataframe(to_display)


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
        display_df(mask, )

    elif mask_player.sum() > 0: # player
        display_df(mask, how='player')

    elif mask_item_name.sum() > 0: # item_name
        display_df(mask, how='item')

    elif mask_item_id.sum() > 0: # item_id
        display_df(mask, how='item')

    elif mask_source.sum() > 0: # source
        display_df(mask)

# todo: item image column
# todo: hide index
