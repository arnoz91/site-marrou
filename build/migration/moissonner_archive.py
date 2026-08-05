# -*- coding: utf-8 -*-
"""
Récupération du site d'origine depuis Internet Archive.

    python build/migration/moissonner_archive.py

L'ancien henrimarrou.org n'existe plus. Les .docx qui en avaient été tirés
étaient incomplets : deux rubriques entières manquaient (« Le chrétien »,
« Marrou après Marrou »), ainsi que les images et les PDF des Cahiers.

Ce script télécharge les 32 pages archivées, en extrait le corps, et
rapatrie les fichiers joints. Résultat dans build/archive/ :
  pages/<slug>.html   le contenu brut de chaque page
  medias/             images et PDF, sous leur nom d'origine
  inventaire.json     ce qui a été trouvé, et ce qui manque
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CIBLE = os.path.join(RACINE, "build", "archive")
INSTANT = "20210507155052"      # dernier instantané complet du site

PAGES = [
    ("accueil", "index.php"),
    ("association", "index.php?page=association"),
    ("cahiers-marrou", "index.php?page=cahiers-marrou"),
    ("contact", "index.php?page=contact"),
    ("mentions-legales", "index.php?page=mentions-legales"),
    ("biographie", "index.php?page=biographie"),
    ("les-livres", "index.php?page=les-livres"),
    ("titres-des-bibliographies", "index.php?page=titres-des-bibliographies"),
    ("articles-divers", "index.php?page=articles-divers"),
    ("antiquites-tardives", "index.php?page=antiquites-tardives"),
    ("saint-augustin", "index.php?page=saint-augustin"),
    ("archeologie-prosopographie", "index.php?page=archeologie-prosopographie"),
    ("education-culture", "index.php?page=education-culture"),
    ("troubadours-amours-courtois", "index.php?page=troubadours-amours-courtois"),
    ("professeur", "index.php?page=professeur"),
    ("directeur-recherches", "index.php?page=directeur-recherches"),
    ("la-methode-historique", "index.php?page=la-methode-historique"),
    ("une-theologie-de-l-histoire", "index.php?page=une-theologie-de-l-histoire"),
    ("le-traite-de-la-musique", "index.php?page=le-traite-de-la-musique"),
    ("la-chanson-populaire", "index.php?page=la-chanson-populaire"),
    ("contributions-musicologiques", "index.php?page=contributions-musicologiques"),
    ("les-conferences-musicales", "index.php?page=les-conferences-musicales"),
    ("resistance", "index.php?page=resistance"),
    ("pour-l-honneur-de-la-france", "index.php?page=pour-l-honneur-de-la-france"),
    ("contre-les-totalitarismes", "index.php?page=contre-les-totalitarismes"),
    ("le-syndicalisme", "index.php?page=le-syndicalisme"),
    ("un-homme-dans-l-eglise", "index.php?page=un-homme-dans-l-eglise"),
    ("une-theologie-de-l-histoire-2", "index.php?page=une-theologie-de-l-histoire-2"),
    ("colloques", "index.php?page=colloques"),
    ("biographie-riche", "index.php?page=biographie-riche"),
    ("etudes-marrou", "index.php?page=etudes-marrou"),
    ("marrou-aujourd-hui", "index.php?page=marrou-aujourd-hui"),
    ("adhesion", "index.php?page=adhesion"),
]

# L'archive enveloppe les adresses de deux façons : absolue et racine.
ENVELOPPE = re.compile(r'(?:https?://web\.archive\.org)?/web/\d+\w*/', re.I)


def extraire_corps(page):
    """Découpe <div class="content">…</div> en comptant les balises.

    Une expression régulière non gloutonne s'arrête au premier </div>
    rencontré, qui appartient presque toujours à un bloc intérieur — c'est
    ainsi que la première tentative rendait des pages vides.
    """
    depart = page.find('<div class="content">')
    if depart == -1:
        return ""
    curseur = depart + len('<div class="content">')
    profondeur = 1
    for balise in re.finditer(r"<(/?)div\b", page[curseur:]):
        profondeur += -1 if balise.group(1) else 1
        if profondeur == 0:
            return page[curseur:curseur + balise.start()]
    return page[curseur:]


def telecharger(url, destination=None, attendu=None, essais=4):
    """curl plutôt qu'urllib : l'archive redirige vers l'instantané voisin.

    Internet Archive limite le débit : en rafale, il renvoie des réponses
    vides sans erreur HTTP. D'où la temporisation entre deux requêtes et les
    reprises tant que le contenu attendu n'est pas là — sans quoi la moisson
    paraît réussir alors qu'elle rend des pages blanches.
    """
    for essai in range(essais):
        if essai:
            time.sleep(4 * essai)
        commande = ["curl", "-sSL", "-m", "90", "--retry", "2",
                    "-A", "Mozilla/5.0 (compatible; recuperation-site-marrou)"]
        if destination:
            commande += ["-o", destination]
        commande.append(url)
        r = subprocess.run(commande, capture_output=True)

        if destination:
            if os.path.exists(destination) and os.path.getsize(destination) > 500:
                return True
            continue
        page = r.stdout.decode("utf-8", "replace")
        if attendu is None or attendu in page:
            return page
    return False if destination else ""


def main():
    os.makedirs(os.path.join(CIBLE, "pages"), exist_ok=True)
    os.makedirs(os.path.join(CIBLE, "medias"), exist_ok=True)

    inventaire, medias = {}, set()

    for slug, chemin in PAGES:
        url = f"https://web.archive.org/web/{INSTANT}/http://henrimarrou.org/{chemin}"
        page = telecharger(url, attendu='<div class="content">')
        time.sleep(2)   # le service limite le débit
        texte = extraire_corps(page).strip()
        texte = re.sub(r"<!--.*?-->", "", texte, flags=re.S)

        # Les adresses archivées redeviennent des adresses d'origine.
        texte = ENVELOPPE.sub("", texte)
        with open(os.path.join(CIBLE, "pages", slug + ".html"), "w", encoding="utf-8") as f:
            f.write(texte)

        nu = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", texte)).strip()
        inventaire[slug] = {"signes": len(nu), "trouve": bool(texte)}

        for attribut in ("src", "href"):
            for lien in re.findall(rf'{attribut}="([^"]+)"', texte):
                lien = ENVELOPPE.sub("", lien)
                if re.search(r"\.(jpg|jpeg|png|gif|pdf)$", lien.split("?")[0], re.I):
                    if not lien.startswith("http"):
                        lien = urllib.parse.urljoin("http://henrimarrou.org/", lien)
                    medias.add(lien)
        print(f"  {len(nu):6d} signes  {slug}")

    print(f"\n{len(medias)} fichiers joints à récupérer")
    obtenus, manquants = [], []
    for media in sorted(medias):
        nom = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(media).path))
        nom = re.sub(r"[^\w.\- ]", "_", nom)
        destination = os.path.join(CIBLE, "medias", nom)
        url = f"https://web.archive.org/web/{INSTANT}id_/" + urllib.parse.quote(media, safe=":/")
        time.sleep(1)
        if telecharger(url, destination):
            obtenus.append(nom)
            print(f"  {os.path.getsize(destination)//1024:5d} Ko  {nom}")
        else:
            manquants.append(media)
            print(f"     ÉCHEC  {media}")

    with open(os.path.join(CIBLE, "inventaire.json"), "w", encoding="utf-8") as f:
        json.dump({"pages": inventaire, "medias": obtenus, "manquants": manquants},
                  f, ensure_ascii=False, indent=1)

    vides = [s for s, v in inventaire.items() if v["signes"] == 0]
    print(f"\n{len(inventaire)} pages, {len(obtenus)} fichiers joints")
    if vides:
        print(f"pages vides sur le site d'origine : {', '.join(vides)}")


if __name__ == "__main__":
    sys.exit(main())
