# -*- coding: utf-8 -*-
"""
Contrôle du site produit : liens, ancres, titres, descriptions.

    python build/verifier.py

Lancé automatiquement avant chaque publication. Rend un code de sortie non nul
en cas de problème, ce qui interrompt la mise en ligne : une page cassée par
une modification de contenu ne peut pas atteindre le site public.
"""
import glob
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RACINE, "site")


def main():
    pages = sorted(glob.glob(os.path.join(SITE, "**", "*.html"), recursive=True))
    if not pages:
        print("Aucune page dans site/ — lancer d'abord build/build.py.")
        return 1

    contenus = {p: open(p, encoding="utf-8").read() for p in pages}
    problemes = []
    titres = {}

    for chemin, source in contenus.items():
        nom = os.path.relpath(chemin, SITE)
        if "admin" in nom.split(os.sep):
            continue

        titre = re.search(r"<title>(.+?)</title>", source)
        if not titre:
            problemes.append(f"{nom} : pas de titre")
        else:
            titres.setdefault(titre.group(1), []).append(nom)

        description = re.search(r'<meta name="description" content="(.*?)"', source)
        if not description or len(description.group(1)) < 40:
            problemes.append(f"{nom} : description absente ou trop courte")

        for href in re.findall(r'href="([^"]+)"', source):
            if href.startswith(("http", "mailto:", "//")):
                continue
            if href == "#":
                problemes.append(f"{nom} : lien mort href=\"#\"")
                continue
            cible, _, ancre = href.partition("#")
            if cible.startswith("/"):
                vise = os.path.normpath(os.path.join(SITE, cible.lstrip("/")))
            elif cible:
                vise = os.path.normpath(os.path.join(os.path.dirname(chemin), cible))
            else:
                vise = chemin
            if not os.path.exists(vise):
                problemes.append(f"{nom} : lien vers un fichier absent — {href}")
                continue
            if ancre and f'id="{ancre}"' not in contenus.get(vise, ""):
                problemes.append(f"{nom} : ancre introuvable — {href}")

    for titre, ou in titres.items():
        if len(ou) > 1:
            problemes.append(f"titre en double « {titre} » : {', '.join(ou)}")

    if problemes:
        print(f"{len(problemes)} problème(s) :\n")
        for p in problemes:
            print(f"  - {p}")
        return 1

    print(f"{len(pages)} pages vérifiées : liens, ancres, titres et descriptions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
