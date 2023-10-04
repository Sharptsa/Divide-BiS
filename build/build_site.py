from jinja2 import Environment, select_autoescape, FileSystemLoader

from bis_list_parser import parse_bis_list, LEGENDARIES
import os
from unidecode import unidecode

MIN_GLOW = 277


def build_site():
    path = os.path.join(os.path.dirname(__file__), "./")
    env = Environment(loader=FileSystemLoader(path), autoescape=select_autoescape())
    env.filters["format_received"] = format_received
    env.filters["format_source"] = format_source

    bis_list_en = parse_bis_list("en")
    bis_list_fr = parse_bis_list("fr")

    template = env.get_template("main_template.j2")
    template.stream(locale="en", bis_list=bis_list_en).dump(
        os.path.join(os.path.dirname(__file__), "../static/index.html")
    )
    template.stream(locale="fr", bis_list=bis_list_fr).dump(
        os.path.join(os.path.dirname(__file__), "../static/index_fr.html")
    )


def format_received(bis, locale="en"):
    if bis["received"] == 1:
        text = "Oui" if locale == "fr" else "Yes"
    elif bis["received"] == 0.5:
        text = "Solo"
    elif bis["received"] == 0:
        text = "Non" if locale == "fr" else "No"
    else:
        text = ""

    if text not in ["Yes", "Oui", "Solo"]:
        color_class = ""
    elif bis["item_id"] in LEGENDARIES:
        color_class = "leg"
    elif bis["ilvl"] >= MIN_GLOW:
        color_class = "glow"
    else:
        color_class = "noglow"

    return f'<span class="{color_class}">{text}</span>'


def format_source(source, locale="en"):
    if locale == "fr":
        return (
            source.replace("Legendary", "Légendaire")
            .replace("Emblems of Conquest", "Emblèmes de Conquête")
            .replace("Emblems of Triumph", "Emblèmes de Triomphe")
            .replace("Emblems of Frost", "Emblèmes de Givre")
        )

    return source


if __name__ == "__main__":
    build_site()
