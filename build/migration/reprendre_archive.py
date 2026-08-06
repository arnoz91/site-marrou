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
import difflib
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
    "saint-augustin": "Saint Augustin et les Pères de l’Église au cœur de "
                      "l’œuvre d’Henri-Irénée Marrou : sa thèse de 1937 et son "
                      "histoire du christianisme ancien.",
    "theologie-de-l-histoire-chretien": "Le versant croyant de la réflexion "
                                        "d’Henri-Irénée Marrou sur le sens de l’histoire.",
}

# Les .docx du dossier de récupération sont une transcription RELUE de
# l'ancien site : coquilles corrigées (« facisme » -> « fascisme »), espaces
# parasites supprimées, guillemets français. Là où ils existent, leur texte
# fait foi ; l'archive fournit en plus les images et les liens, qu'ils ont
# perdus. Les rubriques « Le chrétien » et « Marrou après Marrou » n'ont pas
# été transcrites : pour elles, l'archive reste la seule source.
CORRECTIONS = {
    "biographie": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Biographie.docx",
    "les-livres": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Les livres.docx",
    "bibliographies": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Bibliographie.docx",
    "articles-divers": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Articles divers/"
                       "SAHIM_SiteInternet_Onglet_Vie et œuvre_Articles divers.docx",
    "antiquite-tardive": "SAHIM_SiteInternet_Onglet_l_Historien_Antiquité tardive, histoire de l_Eglise.docx",
    "saint-augustin": "SAHIM_SiteInternet_Onglet_l_Historien_Saint Augustin et autres Pères de l_Eglise.docx",
    "archeologie-prosopographie": "SAHIM_SiteInternet_Onglet_l_Historien_Archéologie, prosopographie.docx",
    "education-culture": "SAHIM_SiteInternet_Onglet_l_Historien_Education, culture.docx",
    "troubadours": "SAHIM_SiteInternet_Onglet_l_Historien_Les troubadours, l_amour courtois.docx",
    "le-professeur": "SAHIM_SiteInternet_Onglet_l_Historien_Le professeur.docx",
    "directeur-de-recherches": "SAHIM_SiteInternet_Onglet_l_Historien_Le directeur de recherches.docx",
    "methode-historique": "SAHIM_SiteInternet_Onglet_Le théoricien de l_histoire_La méthode historique.docx",
    "theologie-de-l-histoire": "SAHIM_SiteInternet_Onglet_Le théoricien de l_histoire_Une théologie de l_histoire.docx",
    "traite-de-la-musique": "SAHIM_SiteInternet_Onglet_Musicologue_TraitéMusique.docx",
    "chanson-populaire": "SAHIM_SiteInternet_Onglet_Musicologue_ChansonPopulaire.docx",
    "contributions-musicologiques": "SAHIM_SiteInternet_Onglet_Musicologue_ContributionsMusicologiques.docx",
    "conferences-musicales": "SAHIM_SiteInternet_Onglet_Musicologue_ConférencesMusicales.docx",
    "resistance": "SAHIM_SiteInternet_Onglet_Le citoyen_Résistance.docx",
    "honneur-de-la-france": "SAHIM_SiteInternet_Onglet_Le citoyen_Pour l_honneur de la France.docx",
    "contre-les-totalitarismes": "SAHIM_SiteInternet_Onglet_Le citoyen_Contre les totalitarismes.docx",
    "syndicalisme": "SAHIM_SiteInternet_Onglet_Le citoyen_le syndicalisme.docx/"
                    "SAHIM_SiteInternet_Onglet_Le citoyen_le syndicalisme.docx",
    "association": "SAHIM_SiteInternet_Page_Association.docx",
    "cahiers-marrou": "SAHIM_SiteInternet_Page_CahiersMarrou.docx",
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
                   lambda m: m.group(1) + ":"
                   if m.group(1).isdigit() and (texte[m.end():m.end()+1] or " ").isdigit()
                   else m.group(1) + INSECABLE + ":", texte)
    texte = re.sub(r"«[  ]*", "«" + INSECABLE, texte)
    texte = re.sub(r"[  ]*»", INSECABLE + "»", texte)
    texte = re.sub(r"[  ]*([,.])", r"\1", texte)
    texte = parentheses(texte)
    return re.sub(r"[  ]{2,}(?![;:!?»])", " ", texte)


def parentheses(texte):
    """Normalise les parenthèses, très irrégulières dans la saisie d'origine.

    On y trouvait « ( 1904 – 1925) », « ( comme il aimait le rappeler ) » ou
    « à Lyon( 1940 ) ». En français la parenthèse est collée à son contenu
    et précédée d'une espace : « à Lyon (1940) ».
    """
    texte = re.sub(r"\([  ]+", "(", texte)              # ( texte -> (texte
    texte = re.sub(r"[  ]+\)", ")", texte)              # texte ) -> texte)
    texte = re.sub(r"(?<=[^\s(\[«‘“—–-])\(", " (", texte)      # mot( -> mot (
    texte = re.sub(r"\)(?=[^\s.,;:!?)\]»…—–-])", ") ", texte)  # )mot -> ) mot
    return texte


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


MARQUEUR_PDF = re.compile(r"[  ]*[\[(][  ]*voir (?:le )?pdf[  ]*[\])]", re.I)


def reliens(texte, liens):
    """Rétablit les renvois vers les documents joints, sans la mention.

    L'ancien site signalait un PDF par un « (voir pdf) » posé à côté du lien.
    Le lien porte l'information à lui seul, et la mention alourdissait des
    listes déjà denses. Là où elle tenait lieu de ponctuation — « …janvier
    1943 [voir pdf] Des résumés… » — on la remplace par un point.
    """
    for ancre, cible in liens:
        ancre = typographie(ancre).strip()
        if ancre and ancre in texte and f"]({cible})" not in texte:
            texte = texte.replace(ancre, f"[{ancre}]({cible})", 1)

    def coupe(m):
        avant = texte[:m.start()].rstrip()
        apres = texte[m.end():].lstrip()
        if avant and apres and avant[-1] not in ".!?:;»…" and apres[0].isupper():
            return "."
        return ""

    return MARQUEUR_PDF.sub(coupe, texte)


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

    # Le soulignement de l'ancien éditeur sert à deux choses : marquer une
    # section (tout le paragraphe souligné) ou mettre en valeur un nom de revue
    # en tête d'entrée. Ce second cas devient du gras à l'intérieur du texte.
    fragment = re.sub(
        r'<span[^>]*text-decoration:\s*underline[^>]*>(.*?)</span>',
        lambda m: (lambda t: f"**{t}** " if t else "")(
            re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()),
        fragment, flags=re.S)

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


# Un astérisque n'est une puce que s'il est suivi d'une espace :
# « *Cette liste… » est une mise en italique, pas une énumération.
PUCE = re.compile(r"^(?:[-–—•·][ 	 ]*|\*(?!\*)[ 	 ]+)")


def listes(blocs):
    """Rétablit de vraies listes à puces.

    L'ancien site n'utilisait pas de balise de liste : les énumérations sont
    des paragraphes précédés d'un tiret ou d'un astérisque, ou de simples
    paragraphes courts après un deux-points. D'où deux corrections :

      - un seul marqueur par puce — « - – Tristesse » devenait « • – Tristesse » ;
      - les énumérations sans marqueur redeviennent des listes.
    """
    sortie = []
    for i, bloc in enumerate(blocs):
        if bloc.startswith("## ") or bloc.startswith("!["):
            sortie.append(bloc)
            continue

        corps = bloc[2:] if bloc.startswith("- ") else bloc
        if PUCE.match(corps.lstrip("*")) or PUCE.match(corps):
            # on retire tous les marqueurs empilés, on n'en remet qu'un
            gras = corps.startswith("**")
            nu = PUCE.sub("", corps.lstrip("*")).lstrip()
            sortie.append("- " + ("**" + nu if gras else nu))
            continue

        # Énumération annoncée par un deux-points : les paragraphes courts qui
        # suivent, tous bâtis sur le même modèle, forment une liste.
        precedent = sortie[-1] if sortie else ""
        court = len(re.sub(r"\*+", "", bloc)) < 160
        if court and bloc.lstrip("*").startswith("«"):
            annonce = precedent.rstrip().endswith(":") or precedent.startswith("- «")
            if annonce:
                sortie.append("- " + bloc)
                continue
        sortie.append(bloc)
    return sortie


def convertir(source, images, titre_page="", corriges=None):
    """Transforme le corps archivé d'une page en Markdown."""
    source = re.sub(r"<(script|style)\b.*?</\1>", "", source, flags=re.S | re.I)
    source = re.sub(r"<hr\b[^>]*>", "\n<!--SEP-->\n", source)

    blocs = []
    for brut in re.split(r"(?i)</p>|</div>|</td>|</tr>|<!--SEP-->", source):
        # Un bloc n'est un intertitre que s'il est souligné DANS SA TOTALITÉ.
        # Souligné en partie, c'est le nom de revue en tête d'une entrée de
        # bibliographie : le promouvoir en titre donnait 43 gros titres sur la
        # page « Articles divers », chacun redoublant le paragraphe suivant.
        nu_bloc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", brut)).strip()
        souligne_txt = re.sub(r"\s+", " ", " ".join(
            re.sub(r"<[^>]+>", " ", m) for m in re.findall(
                r'<span[^>]*text-decoration:\s*underline[^>]*>(.*?)</span>',
                brut, re.S))).strip()
        souligne = bool(souligne_txt) and len(souligne_txt) >= len(nu_bloc) * 0.85
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

    blocs = listes(blocs)

    # Le premier intertitre reprend souvent le titre de la page (il en tenait
    # lieu sur l'ancien site, qui n'affichait pas de titre au-dessus).
    if blocs and blocs[0].startswith("## ") and titre_page:
        a = re.sub(r"\W+", "", blocs[0][3:]).lower()
        b = re.sub(r"\W+", "", titre_page).lower()
        if a and (a in b or b in a):
            blocs.pop(0)

    # Le HTML archivé imbrique les balises : la découpe rendait parfois la fin
    # d'un paragraphe une seconde fois, comme bloc autonome. On l'écarte AVANT
    # d'appliquer les corrections — après, les deux blocs auraient été relus
    # différemment et l'un ne serait plus contenu dans l'autre.
    # La comparaison se fait sur le texte nu : le bloc long peut contenir un
    # lien ou une espace insécable que le bloc court n'a pas, et une égalité
    # de chaînes brutes ne verrait alors pas l'inclusion.
    def nu_bloc(t):
        t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
        return re.sub(r"[^\w]", "", t).lower()

    longs = sorted((b for b in blocs if len(b) > 80), key=len, reverse=True)
    nus = {b: nu_bloc(b) for b in longs}
    inclus = set()
    for i, grand in enumerate(longs):
        for petit in longs[i + 1:]:
            if petit not in inclus and nus[petit] and nus[petit] in nus[grand]:
                inclus.add(petit)
    blocs = [b for b in blocs if b not in inclus]

    blocs = appliquer_corrections(blocs, corriges)

    # Dédoublonnage : consécutif pour les petits blocs, global pour les
    # paragraphes longs — la découpe du HTML archivé, aux balises
    # imbriquées, en rendait parfois un deux fois dans la même page.
    sortie, precedent, vus = [], None, set()
    for b in blocs:
        if b != precedent and not (len(b) > 80 and b in vus):
            sortie.append(b)
            vus.add(b)
        precedent = b

    # Dernier filet, par ressemblance : deux blocs très proches sont la même
    # phrase, l'une venant de l'archive et l'autre de la version relue, quand
    # l'appariement des corrections s'est décalé d'un paragraphe. On garde la
    # seconde — c'est celle qui a été relue.
    def nu_final(t):
        t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
        return re.sub(r"[^\w]", "", t).lower()

    longs = [(i, nu_final(b)) for i, b in enumerate(sortie) if len(b) > 60]
    a_jeter = set()
    for k, (i, ni) in enumerate(longs):
        for j, nj in longs[k + 1:]:
            if i in a_jeter or j in a_jeter or not ni or not nj:
                continue
            court, long_ = (ni, nj) if len(ni) <= len(nj) else (nj, ni)
            if difflib.SequenceMatcher(None, court, long_[:len(court)]).ratio() > 0.9:
                a_jeter.add(i)
    return "\n\n".join(b for i, b in enumerate(sortie) if i not in a_jeter)


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


def paragraphes_corriges(fichier_docx):
    """Texte relu par l'association : (paragraphe, liens) pour chaque entrée.

    Les liens sont ceux que porte le .docx lui-même. Sans eux, la relecture
    ferait perdre les renvois vers les PDF : elle n'apporte que du texte, et
    le texte remplace le bloc archivé, balisage compris.
    """
    import docx
    from docx.oxml.ns import qn
    chemin = os.path.join(RACINE, "SAHIM_Site Internet_Récupération")
    for forme in (fichier_docx, unicodedata.normalize("NFD", fichier_docx)):
        p = os.path.join(chemin, forme.replace("/", os.sep))
        if os.path.exists(p):
            break
    else:
        return []
    document = docx.Document(p)
    chrome = re.compile(r"^(vous êtes ici|haut du formulaire|bas du formulaire|recherche\s*:)", re.I)
    sortie = []
    for par in document.paragraphs:
        texte = unicodedata.normalize("NFC", par.text).strip()
        if not texte or chrome.match(texte):
            continue
        liens = []
        for balise in par._p.findall(qn("w:hyperlink")):
            rid = balise.get(qn("r:id"))
            if not rid or rid not in document.part.rels:
                continue
            ancre = unicodedata.normalize("NFC", "".join(
                n.text or "" for n in balise.iter(qn("w:t")))).strip()
            cible = lien_propre(document.part.rels[rid].target_ref)
            # Seuls les renvois vers un document joint sont repris ici : les
            # liens internes sont déjà portés par le HTML archivé.
            if ancre and cible.startswith("/assets/documents/"):
                liens.append((ancre, cible))
        sortie.append((texte, liens))
    return sortie


def appliquer_corrections(blocs, corriges):
    """Remplace le texte de chaque bloc par sa version relue.

    L'appariement se fait sur le texte nu : la version relue a corrigé des
    coquilles mais garde l'ordre et la découpe des paragraphes. Les blocs
    d'image et les blocs sans correspondance nette sont laissés intacts —
    ce sont eux qui portent ce que les .docx ont perdu.
    """
    if not corriges:
        return blocs

    def nu(t):
        t = re.sub(r"!?\[[^\]]*\]\([^)]*\)", "", t)
        return re.sub(r"[^\w]", "", t).lower()

    nus = [nu(texte) for texte, _ in corriges]
    sortie, depart = [], 0
    for bloc in blocs:
        if bloc.startswith("!["):
            sortie.append(bloc)
            continue
        titre = bloc.startswith("## ")
        cible = nu(bloc)
        if len(cible) < 12:
            sortie.append(bloc)
            continue

        meilleur, score = None, 0.0
        # Fenêtre large : la biographie compte 42 paragraphes, et une
        # fenêtre courte laissait les derniers sans correspondance.
        # Petite marge en arrière : un bloc de l'archive peut correspondre à
        # un paragraphe déjà dépassé quand la découpe diffère légèrement.
        for i in range(max(0, depart - 3), min(depart + 40, len(corriges))):
            r = difflib.SequenceMatcher(None, cible, nus[i]).ratio()
            if r > score:
                meilleur, score = i, r
        if meilleur is None or score < 0.72:
            sortie.append(bloc)
            continue

        remplacement = typographie(corriges[meilleur][0])

        # Le .docx a perdu la mise en valeur du nom de revue en tête d'entrée
        # (elle était portée par un soulignement). On la replace : dans une
        # liste de plusieurs dizaines de références, c'est elle qui permet de
        # repérer une entrée d'un coup d'œil.
        amorce = re.match(r"\*\*(.{2,60}?)\*\*", bloc)
        if amorce and remplacement.startswith(amorce.group(1)):
            n = len(amorce.group(1))
            remplacement = f"**{remplacement[:n]}**{remplacement[n:]}"
        remplacement = reliens(remplacement, corriges[meilleur][1])
        # on conserve le balisage du bloc d'origine (titre, citation, puce)
        if titre:
            remplacement = "## " + re.sub(r"^[IVX]+\.\s*", "", remplacement)
        elif bloc.startswith("> "):
            remplacement = "> " + remplacement
        elif bloc.startswith("- "):
            remplacement = "- " + PUCE.sub("", remplacement).lstrip()
        sortie.append(remplacement)
        depart = meilleur + 1
    return sortie


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
               convertir(lire_archive(source), images, titre,
                        paragraphes_corriges(CORRECTIONS[slug]) if slug in CORRECTIONS else None)
               if source else "")

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
               convertir(lire_archive(source), images, titre,
                         paragraphes_corriges(CORRECTIONS[fichier])
                         if fichier in CORRECTIONS else None))

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
               convertir(lire_archive(source), images, titre,
                         paragraphes_corriges(CORRECTIONS[fichier])
                         if fichier in CORRECTIONS else None))

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
