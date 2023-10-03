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
            [row.boss, " " + str(int(row.raid_size)), " hm" if row.hm else " nm"]
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
        277: [50400],
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
    non_lootable_icons = {
        37111: "https://wow.zamimg.com/images/wow/icons/large/inv_misc_orb_03.jpg",
        40207: "https://wow.zamimg.com/images/wow/icons/large/inv_shield_56.jpg",
        40255: "https://wow.zamimg.com/images/wow/icons/large/inv_trinket_naxxramas03.jpg",
        40267: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_diseasecleansingtotem.jpg",
        40321: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofrejuvenation.jpg",
        40342: "https://wow.zamimg.com/images/wow/icons/large/inv_misc_thegoldencheep.jpg",
        40432: "https://wow.zamimg.com/images/wow/icons/large/inv_offhand_hyjal_d_01.jpg",
        40705: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofgrace.jpg",
        40709: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_totemoflife.jpg",
        40713: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofferocity.jpg",
        42608: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg",
        42853: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg",
        42987: "https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg",
        44253: "https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg",
        45553: "https://wow.zamimg.com/images/wow/icons/large/inv_belt_13.jpg",
        45564: "https://wow.zamimg.com/images/wow/icons/large/inv_boots_leather01.jpg",
        45825: "https://wow.zamimg.com/images/wow/icons/large/inv_belt_48a.jpg",
        46017: "https://wow.zamimg.com/images/wow/icons/large/inv_mace_99.jpg",
        45551: "https://wow.zamimg.com/images/wow/icons/large/inv_belt_45a.jpg",
        45561: "https://wow.zamimg.com/images/wow/icons/large/inv_boots_plate_01.jpg",
        39728: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg",
        40708: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_unrelentingstorm.jpg",
        45560: "https://wow.zamimg.com/images/wow/icons/large/inv_boots_plate_06.jpg",
        44255: "https://wow.zamimg.com/images/wow/icons/large/inv_inscription_tarotgreatness.jpg",
        47673: "https://wow.zamimg.com/images/wow/icons/large/inv_shield_56.jpg",
        47570: "https://wow.zamimg.com/images/wow/icons/large/inv_bracer_32a.jpg",
        47664: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg",
        47666: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_diseasecleansingtotem.jpg",
        47668: "https://wow.zamimg.com/images/wow/icons/large/inv_qirajidol_strife.jpg",
        47661: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_libramofhope.jpg",
        47665: "https://wow.zamimg.com/images/wow/icons/large/spell_nature_slowingtotem.jpg",
        47587: "https://wow.zamimg.com/images/wow/icons/large/inv_bracer_37.jpg",
        47733: "https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_57.jpg",
        47670: "https://wow.zamimg.com/images/wow/icons/large/inv_relics_idolofrejuvenation.jpg",
        49894: "https://wow.zamimg.com/images/wow/icons/large/inv_boots_leather_8.jpg",
        50400: "https://wow.zamimg.com/images/wow/icons/large/inv_jewelry_ring_85.jpg",
        50454: "https://wow.zamimg.com/images/wow/icons/large/trade_herbalism.jpg",
    }
    df_priorities.icon = df_priorities.apply(
        lambda row: row.icon if pd.notna(row.icon) else non_lootable_icons[row.item_id],
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
    df_priorities["ICC"] = df_priorities.boss.apply(
        lambda x: any(
            [
                val in x
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
                    "Lana'Thel",
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
    df_priorities = df_priorities.sort_values(
        [
            "ICC",
            "TOC",
            "boss",
            "raid_size",
            "hm",
            "item_name",
            "ilvl",
            "player",
            "received",
        ],
        ascending=[False, False, True, False, False, True, False, True, False],
    ).reset_index(drop=True)

    return df_priorities.T.to_dict().values()
