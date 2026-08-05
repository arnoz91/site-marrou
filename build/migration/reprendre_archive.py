# -*- coding: utf-8 -*-
"""
Reprise du contenu depuis l'archive : build/archive/ -> contenu/

Reconstitue l'arborescence du site d'origine (7 rubriques de contenu, plus
Association, Cahiers Marrou et Contact) et convertit chaque page en Markdown,
images comprises.

Les en-têtes YAML — titres, chapeaux, résumés — sont conservés quand la page
existait déjà : ils ont été relus, et ce ne sont pas des textes d'origine.

    python build/migration/reprendre_archive.py
"""
import html as htmlmod
import os
import re
import shutil
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARCHIVE = os.path.join(RACINE, "build", "archive")
CONTENU = os.path.join(RACINE, "contenu")
IMAGES = os.path.join(RACINE, "statique", "assets", "images", "archive")
DOCUMENTS = os.path.join(RACINE, "statique", "assets", "documents")

INSECABLE = " "

# --- Arborescence d'origine -------------------------------------------------
# (dossier, libellé de menu, titre de page, icône, source d'archive)
RUBRIQUES = [
    ("vie-et-oeuvre", "Vie et œuvre", "Vie et œuvre", "vie", None),
    ("historien", "l’Historien", "l’Historien", "colonne", None),
    ("theoricien", "Le théoricien", "Le théoricien de l’histoire", "livre", None),
    ("musicologue", "Le musicologue", "Le musicologue", "lyre", None),
    ("citoyen", "Le citoyen", "Le citoyen", "loupe", None),
    ("chretien", "Le chrétien", "Le chrétien", "cahier", None),
    ("apres-marrou", "Après Marrou", "Marrou après Marrou", "personnes", None),
]

# (fichier, rubrique, titre, source d'archive)
PAGES = [
    ("biographie", "vie-et-oeuvre", "Biographie", "biographie"),
    ("les-livres", "vie-et-oeuvre", "Les livres", "les-livres"),
    ("bibliographies", "vie-et-oeuvre", "Bibliographies", "titres-des-bibliographies"),
    ("articles-divers", "vie-et-oeuvre", "Articles divers", "articles-divers"),

    ("antiquite-tardive", "historien", "Antiquité tardive, histoire de l’Église", "antiquites-tardives"),
    ("saint-augustin", "historien", "Saint Augustin et autres Pères de l’Église", "saint-augustin"),
    ("archeologie-prosopographie", "historien", "Archéologie, prosopographie", "archeologie-prosopographie"),
    ("education-culture", "historien", "Éducation, culture", "education-culture"),
    ("troubadours", "historien", "Les troubadours, « l’amour courtois »", "troubadours-amours-courtois"),
    ("le-professeur", "historien", "Le professeur", "professeur"),
    ("directeur-de-recherches", "historien", "Le directeur de recherches", "directeur-recherches"),

    ("methode-historique", "theoricien", "La méthode historique", "la-methode-historique"),
    ("theologie-de-l-histoire", "theoricien", "Une théologie de l’histoire", "une-theologie-de-l-histoire"),

    ("traite-de-la-musique", "musicologue", "Le traité de la musique", "le-traite-de-la-musique"),
    ("chanson-populaire", "musicologue", "La chanson populaire", "la-chanson-populaire"),
    ("contributions-musicologiques", "musicologue", "Contributions musicologiques", "contributions-musicologiques"),
    ("conferences-musicales", "musicologue", "Les conférences musicales", "les-conferences-musicales"),

    ("resistance", "citoyen", "Résistance", "resistance"),
    ("honneur-de-la-france", "citoyen", "Pour l’honneur de la France", "pour-l-honneur-de-la-france"),
    ("contre-les-totalitarismes", "citoyen", "Contre les totalitarismes", "contre-les-totalitarismes"),
    ("syndicalisme", "citoyen", "Le syndicalisme", "le-syndicalisme"),

    ("un-homme-dans-l-eglise", "chretien", "Un homme dans l’Église", "un-homme-dans-l-eglise"),
    ("theologie-de-l-histoire-chretien", "chretien", "Une théologie de l’histoire", "une-theologie-de-l-histoire-2"),

    ("colloques", "apres-marrou", "Colloques", "colloques"),
    ("biographie-riche", "apres-marrou", "Biographie par Pierre Riché", "biographie-riche"),
    ("etudes-marrou", "apres-marrou", "Études sur Marrou, souvenirs", "etudes-marrou"),
    ("marrou-aujourd-hui", "apres-marrou", "Marrou aujourd’hui", "marrou-aujourd-hui"),
]

# Pages hors navigation principale : accessibles par le pied de page
ANNEXES = [
    ("association", "L’Association", "association"),
    ("cahiers-marrou", "Les Cahiers Marrou", "cahiers-marrou"),
    ("contact", "Contact", "contact"),
    ("mentions-legales", "Mentions légales", "mentions-legales"),
]

# Chapeaux et résumés : ce sont les seuls textes qui ne viennent pas du site
# d'origine. La mise en page les exige — sans eux les cartes et les en-têtes
# se vident. Ceux qui existaient déjà sont repris tels quels.
ACCOMPAGNEMENT = {
    "vie-et-oeuvre": ("Une vie, une œuvre : la biographie, les livres, les bibliographies et les articles.",
                      "Biographie, livres, bibliographies, articles"),
    "historien": ("Une œuvre fondatrice sur l’Antiquité tardive, le christianisme ancien et l’éducation.",
                  "Antiquité tardive, Église, éducation"),
    "theoricien": ("L’histoire comme connaissance humaine, et la critique du positivisme.",
                   "Méthode et sens de l’histoire"),
    "musicologue": ("Sous le nom d’Henri Davenson : le traité, la chanson populaire, la critique.",
                    "Henri Davenson et la musique"),
    "citoyen": ("Résistant, syndicaliste, adversaire des totalitarismes et de la torture.",
                "Résistance, syndicalisme, engagements"),
    "chretien": ("Un laïc dans l’Église, et une pensée chrétienne de l’histoire.",
                 "Un homme dans l’Église"),
    "apres-marrou": ("Colloques, études et souvenirs : ce que son œuvre est devenue.",
                     "Colloques, études, souvenirs"),

    "biographie": ("De Marseille à Rome, de Lyon à la Sorbonne, un itinéraire intellectuel, spirituel et civique.",
                   "De l’enfance marseillaise à l’Institut de France"),
    "les-livres": ("L’œuvre publiée, de 1934 aux éditions posthumes.",
                   "L’œuvre publiée, de 1934 aux éditions posthumes."),
    "bibliographies": ("Bibliographies érudites et non érudites, revues et ouvrages collectifs.",
                       "Bibliographies érudites, revues et ouvrages collectifs."),
    "articles-divers": ("Articles, entretiens et contributions retrouvés et archivés.",
                        "Articles, entretiens et contributions."),
    "antiquite-tardive": ("Une période historique réhabilitée, et nommée.",
                          "Une période historique réhabilitée et nommée."),
    "saint-augustin": ("Le christianisme des III<sup>e</sup>—VI<sup>e</sup> siècles.",
                       "Le christianisme des III<sup>e</sup>—VI<sup>e</sup> siècles."),
    "archeologie-prosopographie": ("Inscriptions chrétiennes de la Gaule et prosopographie du Bas-Empire.",
                                   "Inscriptions chrétiennes et grandes entreprises collectives."),
    "education-culture": ("Une histoire de la transmission et de l’accomplissement humain.",
                          "Une histoire de la transmission et de l’accomplissement humain."),
    "troubadours": ("Une incursion médiévale, hors de l’Antiquité tardive.",
                    "Une incursion médiévale, hors de l’Antiquité tardive."),
    "le-professeur": ("De Lyon à la Sorbonne.", "De Lyon à la Sorbonne."),
    "directeur-de-recherches": ("Séminaires, disciples et Centre Lenain de Tillemont.",
                                "Séminaires, disciples et grandes collections."),
    "methode-historique": ("<cite>De la connaissance historique</cite> et la critique du positivisme.",
                           "<cite>De la connaissance historique</cite> et le positivisme."),
    "theologie-de-l-histoire": ("Le sens de l’histoire entre foi chrétienne et prudence historienne.",
                                "Le sens de l’histoire, entre foi et prudence."),
    "traite-de-la-musique": ("Une phénoménologie et une morale musicale selon l’esprit de saint Augustin.",
                             "Une morale musicale selon saint Augustin."),
    "chanson-populaire": ("Cent trente-neuf chansons anciennes choisies et commentées.",
                          "Cent trente-neuf chansons anciennes commentées."),
    "contributions-musicologiques": ("<cite>Esprit</cite>, <cite>Diapason</cite> et l’Académie Charles-Cros.",
                                     "<cite>Esprit</cite>, <cite>Diapason</cite>, Charles-Cros."),
    "conferences-musicales": ("Cinquante-huit séances d’initiation à Lyon, entre 1942 et 1945.",
                              "Cinquante-huit séances d’initiation à Lyon."),
    "resistance": ("Résistance spirituelle, sauvetage et presse clandestine.",
                   "Résistance spirituelle, sauvetage, presse clandestine."),
    "honneur-de-la-france": ("La dénonciation de la torture pendant la guerre d’Algérie.",
                             "La dénonciation de la torture en Algérie."),
    "contre-les-totalitarismes": ("Du fascisme italien à la critique du marxisme.",
                                  "Du fascisme italien à la critique du marxisme."),
    "syndicalisme": ("Le SGEN, l’éducation et la liberté d’enseignement.",
                     "Le SGEN, l’éducation, la liberté d’enseignement."),
    "un-homme-dans-l-eglise": ("Un laïc, marié et père de famille, dans l’Église de son siècle.",
                               "Un laïc dans l’Église de son siècle."),
    "theologie-de-l-histoire-chretien": ("Le versant croyant d’une réflexion menée aussi en historien.",
                                         "Le versant croyant de sa réflexion."),
    "colloques": ("Les rencontres consacrées à son œuvre.", "Les rencontres consacrées à son œuvre."),
    "biographie-riche": ("Le portrait qu’en a donné Pierre Riché.", "Le portrait par Pierre Riché."),
    "etudes-marrou": ("Ce que ses élèves, ses amis et ses lecteurs ont écrit de lui.",
                      "Études, témoignages et souvenirs."),
    "marrou-aujourd-hui": ("Ce que son œuvre dit encore.", "Ce que son œuvre dit encore."),

    "association": ("Faire rayonner l’œuvre d’Henri-Irénée Marrou et favoriser l’étude de ses écrits.", ""),
    "cahiers-marrou": ("La revue annuelle de la Société des amis.", ""),
    "contact": ("Écrire à la Société des amis d’Henri Irénée Marrou.", ""),
    "mentions-legales": ("Éditeur, hébergement et droits.", ""),
}

# Descriptions pour les moteurs de recherche, là où le chapeau est trop bref.
DESCRIPTIONS = {
    "colloques": "Les colloques et journées d’études consacrés à l’œuvre "
                 "d’Henri-Irénée Marrou par la Société des amis.",
    "marrou-aujourd-hui": "Ce que l’œuvre d’Henri-Irénée Marrou dit encore "
                          "aux historiens et aux lecteurs d’aujourd’hui.",
    "biographie-riche": "Le portrait d’Henri-Irénée Marrou donné par Pierre "
                        "Riché dans « Henri Irénée Marrou, historien engagé ».",
    "mentions-legales": "Éditeur, hébergement et droits du site de la Société "
                        "des amis d’Henri Irénée Marrou.",
    "contact": "Écrire à la Société des amis d’Henri Irénée Marrou : adresse, "
               "courriel et siège de l’association.",
    "cahiers-marrou": "Les Cahiers Marrou, revue annuelle de la Société des "
                      "amis : sommaires et numéros parus.",
    "le-professeur": "Henri-Irénée Marrou professeur, de l’enseignement à Lyon "
                     "pendant la guerre à la chaire de la Sorbonne.",
    "antiquite-tardive": "L’Antiquité tardive, période que Marrou a réhabilitée "
                         "et dont il a imposé le nom, et l’histoire de l’Église.",
    "theologie-de-l-histoire-chretien": "Le versant croyant de la réflexion "
                                        "d’Henri-Irénée Marrou sur le sens de l’histoire.",
}

# Les PDF déjà rapatriés dans le site
PDF_LOCAUX = {
    "MarrouCFDTentreFevrier1941e": "marrou-cftc-1941-1943.pdf",
    "Diapason": "diapason-musique-discographie.pdf",
    "Davenson%20Critique": "davenson-critique-musicale-esprit.pdf",
    "Davenson Critique": "davenson-critique-musicale-esprit.pdf",
    "Barbier": "barbier-le-livre-des-chansons.pdf",
}


# --- Conversion -------------------------------------------------------------
def typographie(texte):
    """Guillemets français, apostrophes courbes, ponctuation double espacée.

    N'intervient jamais dans la cible d'un lien : une adresse contient des
    deux-points, qu'une espace insécable rendrait invalide.
    """
    if "](" in texte:
        morceaux = re.split(r"(\]\([^)]*\))", texte)
        return "".join(m if m.startswith("](") else typographie(m) for m in morceaux)
    texte = texte.replace("'", "’")
    # Les pages d'origine mêlent guillemets français et guillemets droits.
    # On ne convertit que si les droits vont par paires : un nombre impair
    # signifie une coquille de saisie, et l'alternance produirait alors un
    # « ouvrant » en fin de citation.
    if texte.count('"') % 2 == 0:
        ouvert = False
        sortie = []
        for c in texte:
            if c == '"':
                sortie.append("«" + INSECABLE if not ouvert else INSECABLE + "»")
                ouvert = not ouvert
            else:
                sortie.append(c)
        texte = "".join(sortie)
    else:
        texte = texte.replace('"', "")
    texte = re.sub(r"[  ]*([;!?])", INSECABLE + r"\1", texte)
    texte = re.sub(r"(\S)[  ]*:(?!//)",
                   lambda m: m.group(1) + (":" if m.group(1).isdigit()
                                           else INSECABLE + ":"), texte)
    texte = re.sub(r"«[  ]*", "«" + INSECABLE, texte)
    texte = re.sub(r"[  ]*»", INSECABLE + "»", texte)
    texte = re.sub(r"[  ]*([,.])", r"\1", texte)
    return re.sub(r"[  ]{2,}(?![;:!?»])", " ", texte)


def lien_propre(cible):
    """Adresse d'origine -> adresse utilisable aujourd'hui."""
    cible = re.sub(r"^(?:https?://web\.archive\.org)?/web/\d+\w*/", "", cible)
    # Une adresse ne contient jamais d'espace : l'ancien site en avait glissé
    # une avant les deux-points de « mailto ».
    cible = re.sub(r"[\s ]+", "", cible)
    for motif, fichier in PDF_LOCAUX.items():
        if motif in cible:
            return "/assets/documents/" + fichier
    if re.search(r"\.(jpg|jpeg|png|gif)$", cible, re.I):
        return "/assets/images/archive/" + os.path.basename(cible)
    if "index.php?page=" in cible:
        return "PAGE:" + cible.split("index.php?page=")[1].split("&")[0]
    if cible.startswith("mailto:"):
        return cible
    if "henrimarrou.org" in cible:
        return ""                      # page de l'ancien site, disparue
    if not cible.startswith("http"):
        return ""
    return re.sub(r"^http://(?=(fr|en)\.wikipedia\.org)", "https://", cible)


def en_ligne(fragment, images):
    """Convertit le balisage de niveau caractère en Markdown."""
    def image(m):
        src = re.search(r'src="([^"]+)"', m.group(0))
        if not src:
            return ""
        nom = os.path.basename(re.sub(r"^.*?/uploads/", "", src.group(1)))
        nom = re.sub(r"[^\w.\- ]", "_", htmlmod.unescape(nom))
        images.add(nom)
        return f"\n\n![](/assets/images/archive/{nom})\n\n"

    fragment = re.sub(r"<img\b[^>]*>", image, fragment)

    def ancre(m):
        cible = lien_propre(htmlmod.unescape(m.group(1)))
        texte = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not texte:
            return ""
        return f"[{texte}]({cible})" if cible and not cible.startswith("PAGE:") else texte
    fragment = re.sub(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', ancre, fragment, flags=re.S)

    fragment = re.sub(r"<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"</?(?:strong|b)\b[^>]*>", "**", fragment)
    fragment = re.sub(r"</?(?:em|i)\b[^>]*>", "*", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    fragment = htmlmod.unescape(fragment).replace(" ", " ")

    fragment = re.sub(r"\*{2,}\s*\*{2,}", " ", fragment)
    fragment = re.sub(r"\*{3,}", "**", fragment)
    if fragment.count("**") % 2:
        fragment = "".join(fragment.rsplit("**", 1))
    if len(re.findall(r"(?<!\*)\*(?!\*)", fragment)) % 2:
        fragment = re.sub(r"(?<!\*)\*(?!\*)(?!.*(?<!\*)\*(?!\*))", "", fragment, flags=re.S)
    return typographie(re.sub(r"[ \t]+", " ", fragment)).strip()


INTERTITRE = re.compile(r"^(?:[IVX]+\.\s*)?(.{3,120})$")


def convertir(source, images, titre_page=""):
    """Transforme le corps archivé d'une page en Markdown."""
    source = re.sub(r"<(script|style)\b.*?</\1>", "", source, flags=re.S | re.I)
    source = re.sub(r"<hr\b[^>]*>", "\n<!--SEP-->\n", source)

    blocs = []
    for brut in re.split(r"(?i)</p>|</div>|</td>|</tr>|<!--SEP-->", source):
        souligne = 'text-decoration: underline' in brut
        centre = 'text-align: center' in brut
        rendu = en_ligne(brut, images)
        if not rendu:
            continue
        for morceau in rendu.split("\n"):
            morceau = morceau.strip()
            if not morceau:
                continue
            nu = re.sub(r"!\[[^\]]*\]\([^)]*\)|[*]", "", morceau).strip()
            titre = souligne and len(nu) < 120 and not morceau.startswith("![")
            gras_centre = centre and morceau.startswith("**") and morceau.endswith("**") and len(nu) < 100
            if titre or gras_centre:
                m = INTERTITRE.match(nu)
                blocs.append("## " + (m.group(1) if m else nu).strip(" *"))
            elif morceau.startswith("![") or morceau.startswith("**") or True:
                blocs.append(morceau)

    # Le premier intertitre reprend souvent le titre de la page (il en tenait
    # lieu sur l'ancien site, qui n'affichait pas de titre au-dessus).
    if blocs and blocs[0].startswith("## ") and titre_page:
        a = re.sub(r"\W+", "", blocs[0][3:]).lower()
        b = re.sub(r"\W+", "", titre_page).lower()
        if a and (a in b or b in a):
            blocs.pop(0)

    # dédoublonnage des lignes vides et des séparateurs
    sortie, precedent = [], None
    for b in blocs:
        if b != precedent:
            sortie.append(b)
        precedent = b
    return "\n\n".join(sortie)


# --- Écriture ---------------------------------------------------------------
def entete_existante(chemin):
    if not os.path.exists(chemin):
        return {}
    brut = open(chemin, encoding="utf-8").read()
    if not brut.startswith("---"):
        return {}
    champs = {}
    for ligne in brut.split("---", 2)[1].strip().split("\n"):
        m = re.match(r'^(\w+): "?(.*?)"?$', ligne.strip())
        if m:
            champs[m.group(1)] = m.group(2)
    return champs


def ecrire(chemin, champs, corps):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    lignes = ["---"]
    for cle, valeur in champs.items():
        if valeur in (None, ""):
            continue
        if isinstance(valeur, bool):
            lignes.append(f"{cle}: {'true' if valeur else 'false'}")
        elif isinstance(valeur, int):
            lignes.append(f"{cle}: {valeur}")
        else:
            lignes.append(f'{cle}: "{str(valeur)}"')
    lignes += ["---", ""]
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + (corps + "\n" if corps else ""))


def lire_archive(nom):
    chemin = os.path.join(ARCHIVE, "pages", nom + ".html")
    return open(chemin, encoding="utf-8").read() if os.path.exists(chemin) else ""


def main():
    images = set()
    os.makedirs(IMAGES, exist_ok=True)

    # anciennes pages : on repart de zéro pour l'arborescence
    for dossier in ("pages", "rubriques"):
        shutil.rmtree(os.path.join(CONTENU, dossier), ignore_errors=True)
        os.makedirs(os.path.join(CONTENU, dossier))

    anciennes = os.path.join(RACINE, "build", "contenu-precedent")

    for ordre, (slug, nav, titre, icone, source) in enumerate(RUBRIQUES, start=1):
        chapeau, resume = ACCOMPAGNEMENT.get(slug, ("", ""))
        champs = entete_existante(os.path.join(anciennes, "rubriques", slug + ".md"))
        champs.update({
            "titre": titre, "nav": nav,
            "surtitre": champs.get("surtitre") or titre,
            "chapeau": chapeau,
            "resume": resume,
            "description": champs.get("description", ""),
            "icone": icone, "ordre": ordre,
            "sommaire": slug != "vie-et-oeuvre",   # portée par le bouton du héros
            "grille": True,
        })
        ecrire(os.path.join(CONTENU, "rubriques", slug + ".md"), champs,
               convertir(lire_archive(source), images, titre) if source else "")

    compteur = {}
    for fichier, rubrique, titre, source in PAGES:
        compteur[rubrique] = compteur.get(rubrique, 0) + 1
        chapeau, resume = ACCOMPAGNEMENT.get(fichier, ("", ""))
        champs = entete_existante(os.path.join(anciennes, "pages", fichier + ".md"))
        champs.update({
            "titre": titre,
            "chapeau": chapeau,
            "resume": resume,
            "description": DESCRIPTIONS.get(fichier, champs.get("description", "")),
            "rubrique": rubrique, "ordre": compteur[rubrique],
        })
        ecrire(os.path.join(CONTENU, "pages", fichier + ".md"), champs,
               convertir(lire_archive(source), images, titre))

    for fichier, titre, source in ANNEXES:
        chapeau, _ = ACCOMPAGNEMENT.get(fichier, ("", ""))
        champs = entete_existante(os.path.join(anciennes, "rubriques", fichier + ".md"))
        champs.update({
            "titre": titre,
            "chapeau": chapeau,
            "description": DESCRIPTIONS.get(fichier, champs.get("description", "")),
            "annexe": True, "ordre": 90,
        })
        ecrire(os.path.join(CONTENU, "annexes", fichier + ".md"), champs,
               convertir(lire_archive(source), images, titre))

    reportees = 0
    for nom in sorted(images):
        origine = os.path.join(ARCHIVE, "medias", nom)
        if os.path.exists(origine):
            shutil.copy2(origine, os.path.join(IMAGES, nom))
            reportees += 1

    print(f"{len(RUBRIQUES)} rubriques, {len(PAGES)} pages, {len(ANNEXES)} annexes")
    print(f"{reportees} images reportées sur {len(images)} référencées")
    manquantes = sorted(i for i in images
                        if not os.path.exists(os.path.join(ARCHIVE, "medias", i)))
    if manquantes:
        print("images introuvables : " + ", ".join(manquantes))


if __name__ == "__main__":
    sys.exit(main())
