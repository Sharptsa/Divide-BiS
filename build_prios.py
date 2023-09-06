import pandas as pd
import numpy as np
import itertools

df_bis = pd.read_csv(r'data/players_bis.csv')
df_items = pd.read_csv(r'data/items.csv')
df_items['weight'] = (1. + (df_items.slot == 'Weapon 2H')) \
    * (1. + 0.5 * (df_items.slot.isin(['Weapon 2H', 'Weapon 1H', 'Trinket']))) \
    * (1. + (df_items.ilvl - 245) / (258 - 245)) \
    / (df_items.drops_per_id / 0.2)

# Assert items are known
iids = []
for iid in df_bis.item_id.unique():
    if iid not in df_items.item_id.unique():
        if iid not in [45825, 45564, 45553, 45551, 40207, 40321, 40713, 40342,
                       37111, 40705, 40432, 40255, 40267, 40709, 42987, 44253,
                       42853, 42608, 46017, 45561, 39728, 40708, 45560, 44255,
                       47673, 47570, 47664, 47666, 47668, 47661, 47665, 47587,
                       47733, 47670]:
            iids.append(iid)
if iids:
    print(f'Found new items: {iids}')
    raise Warning


def add_item(row):
    if 'weight' in df_items.columns:
        df_items.drop('weight', axis=1, inplace=True)
    df_items.loc[df_items.shape[0], :] = row
    df_items.item_id = df_items.item_id.apply(int)
    df_items.raid_size = df_items.raid_size.apply(int)
    df_items.ilvl = df_items.ilvl.apply(int)
    df_items.hm = df_items.hm == True
    df_items.to_csv(r'data/items.csv', index=False)


def evaluate_prios(df):
    # Prepare dataframe
    df = df.copy()
    df = pd.merge(df, df_items[['item_id', 'weight']],
                  how='inner', on='item_id')

    # Compute penalities
    # penalizing = df.groupby('item_id').cumcount(ascending=False)
    penalized = df.groupby('item_id').cumcount(ascending=True)
    # df['penalizing'] = penalizing * df.weight
    df['penalized'] = penalized * df.weight
    # player_penalizing = df.groupby('player').penalizing.sum()
    player_penalized = df.groupby('player').penalized.sum()
    loss = np.var(player_penalized)

    return loss


def optimize_prios(df_source, resim=True, fixed_pre=None, fixed_post=None,
                   epochs=80, target_temp=0.001):
    if fixed_pre is None:
        fixed_pre = {}
    if fixed_post is None:
        fixed_post = {}

    def format_fixed_dict(fixed, df):
        for item_id in df.item_id.unique():
            if item_id not in fixed:
                fixed[item_id] = []
        stored = []
        for k in fixed:
            for i, p in enumerate(fixed[k]):
                fixed[k][i] = df.loc[(df.item_id == k)
                                     & (df.player == p)
                                     & (~df.index.isin(stored))].index[0]
                stored.append(fixed[k][i])

        return fixed

    # Prepare dataframe
    df = df_source.copy()
    # only keep lootable items
    df = df.loc[df.item_id.isin(df_items.item_id), :]
    if resim:
        df = df.sample(df.shape[0]).sort_values('item_id')  # shuffle

    # Format fixed dicts
    fixed_pre = format_fixed_dict(fixed_pre, df)
    fixed_post = format_fixed_dict(fixed_post, df)
    idxs_in_fixed = list(itertools.chain.from_iterable([fixed_pre[k] for k in fixed_pre])) \
        + list(itertools.chain.from_iterable([fixed_post[k] for k in fixed_post]))

    # Create group items and probas
    groups = df.groupby('item_id').item_name.groups
    groups = {k: list(groups[k]) for k in groups}
    groups = {k: [i for i in groups[k] if i not in idxs_in_fixed]
              for k in groups}
    group_probas = {
        k: int(len(groups[k]) * (len(groups[k]) - 1) / 2) for k in groups}
    total_links = sum(group_probas.values())
    group_probas = {
        k: group_probas[k] / sum(group_probas.values()) for k in group_probas}

    # Loop over modifications
    old_loss = evaluate_prios(df)
    min_loss = old_loss
    best_df = df
    temp = evaluate_prios(df) / 2.5
    target_temp *= temp
    lbda = np.exp(np.log(target_temp / temp) / (epochs * total_links))
    temps = []
    losses = []
    for step in range(epochs * total_links * resim):
        if step % total_links == 0:
            print(f'Epoch {int(step / total_links) + 1}/{epochs}...')

        # Modify priorities
        item_id = np.random.choice(
            list(group_probas.keys()), p=list(group_probas.values()))
        first_id, second_id = np.random.choice(
            len(groups[item_id]), replace=False, size=2)
        groups[item_id][first_id], groups[item_id][second_id] = groups[item_id][second_id], \
            groups[item_id][first_id]

        # Evaluate
        groups_with_fixed = {
            k: fixed_pre[k] + groups[k] + fixed_post[k] for k in groups}
        loss = evaluate_prios(
            df.loc[list(itertools.chain.from_iterable(groups_with_fixed.values()))])
        if np.random.random() > np.exp((old_loss - loss) / temp):  # not accepted
            groups[item_id][first_id], groups[item_id][second_id] = groups[item_id][second_id], \
                groups[item_id][first_id]
            loss = old_loss
        old_loss = loss
        temp *= lbda
        temps.append(temp)
        losses.append(loss)

        if loss < min_loss:
            best_df = df.loc[list(itertools.chain.from_iterable(
                groups_with_fixed.values()))]
            min_loss = loss

    # Add non lootable items
    best_df['rank_in_queue'] = best_df.groupby('item_id').cumcount() + 1
    non_lootable = df_source.copy(
    ).loc[~df_source.item_id.isin(df_items.item_id), :]
    best_df = pd.concat([best_df, non_lootable.sort_values('item_id')])
    non_lootable_sources = {'Emblems of Conquest': [45825],
                            'Emblems of Triumph': [47673, 47664, 47666, 47668, 47661,
                                                   47665, 47733, 47670],
                            'Craft': [45564, 45553, 45551, 45561, 45560, 47570, 47587],
                            'P1': [40207, 40321, 40713, 40342, 37111, 40705, 40432,
                                   40255, 40267, 40709, 42987, 44253, 39728, 40708,
                                   44255],
                            'PvP': [42853, 42608],
                            'Legendary': [46017]}
    non_lootable_sources = {
        v: k for k in non_lootable_sources for v in non_lootable_sources[k]}
    best_df.rank_in_queue = best_df.apply(lambda row: str(int(row.rank_in_queue))
                                          if pd.notna(row.rank_in_queue)
                                          else non_lootable_sources[row.item_id],
                                          axis=1)
    best_df['received'] = ''
    best_df['temp_idx'] = range(best_df.shape[0])
    best_df.sort_values(['item_name', 'item_id', 'temp_idx'], inplace=True)
    best_df.drop('temp_idx', axis=1, inplace=True)

    if resim:
        previous_priorities = pd.read_excel(r'data/players_priorities.xlsx')
        previous_priorities.to_excel(
            r'data/players_priorities_previous.xlsx', index=False)
        best_df.to_excel(r'data/players_priorities.xlsx', index=False)

    return best_df, np.array(temps), np.array(losses)


if __name__ == '__main__':
    df_priorities, temps, losses = optimize_prios(df_bis,
                                                  fixed_pre={},
                                                  fixed_post={})

    import matplotlib.pyplot as plt
    plt.plot(np.arange(len(temps)), temps)
    plt.plot(np.arange(len(temps)), losses)
    plt.show()
