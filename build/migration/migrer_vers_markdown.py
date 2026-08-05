# -*- coding: utf-8 -*-
"""
Migration unique : pages.py + build/contenu/*.html  ->  contenu/**/*.md

Après cette bascule, chaque page est un seul fichier Markdown à en-tête YAML,
ce qui est le format que l'interface d'administration sait lire et écrire.
Ce script ne sert qu'une fois ; il est conservé pour mémoire.

    python build/migrer_vers_markdown.py
"""
import os
import re
import sys
import html as htmlmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages import ACCUEIL, GRILLES, PAGES, RUBRIQUES, SITE, TRANSVERSAUX  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCIEN = os.path.join(RACINE, "build", "contenu")
NOUVEAU = os.path.join(RACINE, "contenu")


def html_vers_markdown(fragment):
    """Convertit le jeu de balises restreint produit par l'extraction.

    <sup> et <cite> sont laissés tels quels : Markdown n'a pas d'équivalent,
    et le HTML en ligne y est autorisé.
    """
    if not fragment.strip():
        return ""

    texte = fragment

    def en_ligne(s):
        s = re.sub(r"</?strong>", "**", s)
        s = re.sub(r"</?em>", "*", s)
        return re.sub(r"\s+", " ", s).strip()

    blocs = []
    for bloc in re.findall(
        r"<h2[^>]*>.*?</h2>|<ul>.*?</ul>|<blockquote>.*?</blockquote>|<p>.*?</p>",
        texte, re.S,
    ):
        if bloc.startswith("<h2"):
            contenu = re.sub(r"</?h2[^>]*>", "", bloc)
            blocs.append("## " + en_ligne(contenu))
        elif bloc.startswith("<ul>"):
            items = re.findall(r"<li>(.*?)</li>", bloc, re.S)
            blocs.append("\n".join("- " + en_ligne(i) for i in items))
        elif bloc.startswith("<blockquote>"):
            paras = re.findall(r"<p>(.*?)</p>", bloc, re.S)
            blocs.append("\n>\n".join("> " + en_ligne(p) for p in paras))
        else:
            blocs.append(en_ligne(re.sub(r"</?p>", "", bloc)))

    return "\n\n".join(blocs)


def yaml_valeur(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    texte = str(v).replace('"', '\\"')
    return f'"{texte}"'


def ecrire(chemin, entete, corps):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    lignes = ["---"]
    for cle, valeur in entete.items():
        if valeur is None or valeur == "":
            continue
        lignes.append(f"{cle}: {yaml_valeur(valeur)}")
    lignes.append("---")
    lignes.append("")
    if corps:
        lignes.append(corps)
        lignes.append("")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))


def lire_ancien(page):
    nom = page.get("fragment", page["slug"].replace("/", "__"))
    chemin = os.path.join(ANCIEN, nom + ".html")
    if not os.path.exists(chemin):
        return ""
    with open(chemin, encoding="utf-8") as f:
        return f.read().strip()


def main():
    # Accueil ---------------------------------------------------------------
    ecrire(os.path.join(NOUVEAU, "accueil.md"), {
        "titre": ACCUEIL["titre"],
        "sous_titre": ACCUEIL["sous_titre"],
        "dates": ACCUEIL["dates"],
        "chapeau": ACCUEIL["chapeau"],
        "description": ACCUEIL["description"],
        "citation": ACCUEIL["citation"],
    }, "")

    # Rubriques -------------------------------------------------------------
    for ordre, rubrique in enumerate(RUBRIQUES, start=1):
        ecrire(os.path.join(NOUVEAU, "rubriques", rubrique["slug"] + ".md"), {
            "titre": rubrique["titre"],
            "nav": rubrique["nav"],
            "surtitre": rubrique["surtitre"],
            "chapeau": rubrique["chapeau"],
            "resume": rubrique["resume"],
            "description": rubrique.get("description", ""),
            "icone": rubrique["icone"],
            "ordre": ordre,
            "sommaire": rubrique.get("sommaire", True),
            "grille": rubrique["slug"] in GRILLES,
        }, html_vers_markdown(lire_ancien(rubrique)))

    # Pages -----------------------------------------------------------------
    compteurs = {}
    for page in PAGES:
        rubrique = page["parent"]
        compteurs[rubrique] = compteurs.get(rubrique, 0) + 1
        nom = page["slug"].split("/")[-1]
        ecrire(os.path.join(NOUVEAU, "pages", nom + ".md"), {
            "titre": page["titre"],
            "chapeau": page["chapeau"],
            "resume": page["resume"],
            "description": page.get("description", ""),
            "rubrique": rubrique,
            "ordre": compteurs[rubrique],
        }, html_vers_markdown(lire_ancien(page)))

    # Réglages généraux -----------------------------------------------------
    reglages = ["---"]
    for cle, valeur in SITE.items():
        reglages.append(f"{cle}: {yaml_valeur(valeur)}")
    reglages.append("transversaux:")
    for libelle, cible, actif in TRANSVERSAUX:
        if actif:
            reglages.append(f"  - libelle: {yaml_valeur(libelle)}")
            reglages.append(f"    cible: {yaml_valeur(cible)}")
    reglages += ["---", ""]
    with open(os.path.join(NOUVEAU, "reglages.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(reglages))

    total = sum(len(files) for _, _, files in os.walk(NOUVEAU))
    print(f"{total} fichiers écrits dans contenu/")


if __name__ == "__main__":
    sys.exit(main())
