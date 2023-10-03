import numpy as np
import pandas as pd
import os

LEGENDARIES = [46017]


def parse_bis_list(locale="en"):
    items_path = os.path.join(os.path.dirname(__file__), "../data/items.csv")
    df_items = pd.read_csv(items_path)

    if locale == "fr":
        df_items.item_name = df_items.item_name_fr
        df_items.boss = df_items.boss_fr

    bis_path = os.path.join(
        os.path.dirname(__file__), "../data/players_priorities.xlsx"
    )
    df_priorities = pd.read_excel(bis_path)
    left, right = (
        (df_priorities, df_items.drop(["item_name", "drops_per_id"], axis=1))
        if not locale == "fr"
        else (
            df_priorities.drop("item_name", axis=1),
            df_items.drop("drops_per_id", axis=1),
        )
    )
    df_priorities = pd.merge(left, right, how="left", on="item_id")
    df_priorities["source"] = df_priorities.apply(
        lambda row: row.rank_in_queue
        if pd.isna(row.boss)
        else "".join(
            [row.boss, " " + str(int(row.raid_size)), " HM" if row.hm else " NM"]
        ),
        axis=1,
    )
    df_priorities.loc[df_priorities.boss.isna(), "rank_in_queue"] = np.nan
    df_priorities["legendary"] = df_priorities.item_id.isin(LEGENDARIES)
    df_priorities["lootable"] = (
        (df_priorities.boss.notna())
        | (df_priorities.source == "Craft")
        | (df_priorities.legendary)
    )

    # Clean data
    df_priorities.hm = df_priorities.hm == True
    df_priorities.raid_size = df_priorities.raid_size.fillna(-1).apply(int)
    df_priorities.boss.fillna("", inplace=True)
    df_priorities.loc[df_priorities.source == "Craft", "boss"] = "ZZZ"
    df_priorities.slot.fillna("", inplace=True)
    non_lootable_ilvls = {
        277: [50400, 52572],
        264: [49894, 50454],
        258: [46017],
        245: [47673, 47570, 47664, 47666, 47668, 47661, 47665, 47587, 47733, 47670],
        238: [42853, 42608],
        232: [45825, 45564, 45553, 45551, 45561, 45560],
        213: [40207, 40321, 40342, 40432, 40255, 40267, 39728],
        200: [40713, 40705, 40709, 42987, 44253, 40708, 44255],
        187: [37111],
    }
    non_lootable_ilvls = {
        v: k for k in non_lootable_ilvls for v in non_lootable_ilvls[k]
    }
    df_priorities.ilvl = df_priorities.apply(
        lambda row: int(row.ilvl)
        if pd.notna(row.ilvl)
        else non_lootable_ilvls[row.item_id],
        axis=1,
    )
    
    if locale == "fr":
        non_lootable_names_fr = {
            37111: "Protecteur d'âme",
            40207: "Cachet de vigilance",
            40255: "Malédiction du mourant",
            40267: "Totem de maléfice",
            40321: "Idole de l'étoile filante",
            40342: "Idole d'éveil",
            40432: "Représentation de l'Âme des dragons",
            40705: "Libram de renouveau",
            40709: "Totem de croissance forestière",
            40713: "Idole de la bête vorace",
            42608: "Totem d'indomptabilité du gladiateur furieux",
            42853: "Libram de robustesse du gladiateur furieux",
            42987: "Carte de Sombrelune : Grandeur",
            44253: "Carte de Sombrelune : Grandeur",
            45553: "Ceinture des dragons",
            45564: "Souliers de silence",
            45825: "Ceinturon garde-écu",
            46017: "Val'anyr, le marteau des anciens rois",
            45551: "Ceinturon indestructible en plaques",
            45561: "Bottines de la destinée",
            39728: "Totem de détresse",
            40708: "Totem du plan élémentaire",
            45560: "Dispensateurs de mort à pointes",
            44255: "Carte de Sombrelune : Grandeur",
            47673: "Cachet de virulence",
            47570: "Brise-épée en saronite",
            47664: "Libram de défiance",
            47666: "Totem du vent électrifiant",
            47668: "Idole de mutilation",
            47661: "Libram de vaillance",
            47665: "Totem des marées calmantes",
            47587: "Brassards royaux en voile lunaire",
            47733: "Cercle du réparacoeur",
            47670: "Idole de la fureur lunaire",
            49894: "Bottes cénariennes bénies",
            50400: "Bague de sagesse sans fin du Verdict des cendres",
            50454: "Idole du saule noir",
            52572: "Bague de puissance sans fin du Verdict des cendres",
        }
        df_priorities.item_name = df_priorities.apply(
            lambda row: row.item_name
            if pd.notna(row.item_name)
            else non_lootable_names_fr[row.item_id],
            axis=1,
        )
    df_priorities.rank_in_queue = df_priorities.rank_in_queue.fillna("").apply(
        lambda x: int(x) if x else x
    )
    df_priorities["TOC"] = df_priorities.boss.apply(
        lambda x: any(
            [
                val in x
                for val in [
                    # EN
                    "Beasts",
                    "Jaraxxus",
                    "Champions",
                    "Twin",
                    "Anub",
                    "Chest",
                    # FR
                    "Jumelle",
                    "Bêtes",
                    "Coffre",
                ]
            ]
        )
    )
    df_priorities["ICC"] = df_priorities.apply(
        lambda row: any(
            [
                val in row.boss
                for val in [
                    # EN
                    "Marrowgar",
                    "Deathwhisper",
                    "Gunship",
                    "Saurfang",
                    "Festergut",
                    "Rotface",
                    "Putricide",
                    "Prince Council",
                    "Lana'thel",
                    "Valithria",
                    "Sindragosa",
                    "Lich King",
                    "ICC",
                    # FR
                    "Gargamoelle",
                    "Murmemort",
                    "Cannonière",
                    "Saurcroc",
                    "Pulentraille",
                    "Trognepus",
                    "Conseil des Princes",
                    "Roi-Liche",
                ]
            ]
        )
        or row.item_id == 49623,
        axis=1,
    )
    df_priorities["ICC"] = df_priorities["ICC"].astype(int)
    df_priorities["TOC"] = df_priorities["TOC"].astype(int)
    df_priorities["hm"] = df_priorities["hm"].astype(int)
    df_priorities.loc[df_priorities.received == "X", "received"] = 1.0
    df_priorities.loc[df_priorities.received == "SOLO", "received"] = 0.5
    df_priorities.loc[df_priorities.received.isna(), "received"] = 0.0
    df_priorities.loc[
        ~df_priorities.lootable & ~df_priorities.legendary, "received"
    ] = -1.0

    return df_priorities.T.to_dict().values()
