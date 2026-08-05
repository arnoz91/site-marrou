"""
Extraction unique des .docx récupérés vers des fragments HTML éditables.

À lancer une seule fois : le résultat atterrit dans build/contenu/ et devient
la source du site. Une fois extrait, on édite le fragment HTML, plus le .docx.

    python build/extraire_docx.py
"""
import os
import re
import sys
import html
import unicodedata

import docx

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "SAHIM_Site Internet_Récupération")
CIBLE = os.path.join(RACINE, "build", "contenu")

# Restes de chrome de l'ancien site, à ne pas reprendre
CHROME = re.compile(
    r"^(vous êtes ici|haut du formulaire|bas du formulaire|recherche\s*:)", re.I
)
# Intertitre de type « I. Enfance et prime jeunesse (1904-1925) »
INTERTITRE = re.compile(r"^(I{1,3}|IV|VI{0,3}|IX|XI{0,2})\.\s+(.{3,120})$")

# fragment -> fichier .docx source (chemin relatif dans le dossier de récupération)
SOURCES = {
    "decouvrir": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Biographie.docx",
    "ressources-livres": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Les livres.docx",
    "ressources-bibliographie": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Bibliographie.docx",
    "ressources-articles": "SAHIM_SiteInternet_Onglet_Vie et œuvre_Articles divers/"
                           "SAHIM_SiteInternet_Onglet_Vie et œuvre_Articles divers.docx",
    "association": "SAHIM_SiteInternet_Page_Association.docx",
    "cahiers": "SAHIM_SiteInternet_Page_CahiersMarrou.docx",

    "historien/archeologie-prosopographie":
        "SAHIM_SiteInternet_Onglet_l_Historien_Archéologie, prosopographie.docx",
    "historien/directeur-de-recherches":
        "SAHIM_SiteInternet_Onglet_l_Historien_Le directeur de recherches.docx",
    "historien/troubadours":
        "SAHIM_SiteInternet_Onglet_l_Historien_Les troubadours, l_amour courtois.docx",
    "historien/antiquite-tardive":
        "SAHIM_SiteInternet_Onglet_l_Historien_Antiquité tardive, histoire de l_Eglise.docx",
    "historien/saint-augustin":
        "SAHIM_SiteInternet_Onglet_l_Historien_Saint Augustin et autres Pères de l_Eglise.docx",
    "historien/education-culture":
        "SAHIM_SiteInternet_Onglet_l_Historien_Education, culture.docx",
    "historien/le-professeur":
        "SAHIM_SiteInternet_Onglet_l_Historien_Le professeur.docx",

    "penser-agir/methode-historique":
        "SAHIM_SiteInternet_Onglet_Le théoricien de l_histoire_La méthode historique.docx",
    "penser-agir/theologie-de-l-histoire":
        "SAHIM_SiteInternet_Onglet_Le théoricien de l_histoire_Une théologie de l_histoire.docx",
    "penser-agir/resistance":
        "SAHIM_SiteInternet_Onglet_Le citoyen_Résistance.docx",
    "penser-agir/contre-les-totalitarismes":
        "SAHIM_SiteInternet_Onglet_Le citoyen_Contre les totalitarismes.docx",
    "penser-agir/honneur-de-la-france":
        "SAHIM_SiteInternet_Onglet_Le citoyen_Pour l_honneur de la France.docx",
    "penser-agir/syndicalisme":
        "SAHIM_SiteInternet_Onglet_Le citoyen_le syndicalisme.docx/"
        "SAHIM_SiteInternet_Onglet_Le citoyen_le syndicalisme.docx",

    "musicologue/traite-de-la-musique":
        "SAHIM_SiteInternet_Onglet_Musicologue_TraitéMusique.docx",
    "musicologue/chanson-populaire":
        "SAHIM_SiteInternet_Onglet_Musicologue_ChansonPopulaire.docx",
    "musicologue/conferences-musicales":
        "SAHIM_SiteInternet_Onglet_Musicologue_ConférencesMusicales.docx",
    "musicologue/critique-musicale":
        "SAHIM_SiteInternet_Onglet_Musicologue_ContributionsMusicologiques.docx",
}


def chemin_source(relatif):
    """Le dossier de récupération vient de macOS : accents en forme décomposée."""
    for forme in (relatif, unicodedata.normalize("NFD", relatif)):
        p = os.path.join(SOURCE, forme.replace("/", os.sep))
        if os.path.exists(p):
            return p
    return None


def typographie(texte):
    """Guillemets français et apostrophes courbes, comme le reste du site."""
    texte = re.sub(r'"([^"]{1,400})"', r"« \1 »", texte)
    return texte.replace("'", "’").replace('"', " »")


def paragraphe_html(par):
    """Rend un paragraphe en conservant italiques et gras (titres d'ouvrages).

    Les runs Word sont très fragmentés : on fusionne les segments voisins de
    même formatage, sinon on obtient <strong>Biographie d</strong><strong>’</strong>…
    """
    segments = []
    for run in par.runs:
        texte = unicodedata.normalize("NFC", run.text)
        if not texte:
            continue
        style = (bool(run.italic), bool(run.bold))
        if segments and segments[-1][0] == style:
            segments[-1][1] += texte
        else:
            segments.append([style, texte])

    morceaux = []
    for (italique, gras), texte in segments:
        rendu = html.escape(texte, quote=False)
        if texte.strip():
            if italique:
                rendu = f"<em>{rendu}</em>"
            if gras:
                rendu = f"<strong>{rendu}</strong>"
        morceaux.append(rendu)
    # La typographie s'applique au paragraphe assemblé : une paire de guillemets
    # est souvent coupée en deux runs Word, et par run on ne la verrait pas.
    # Les balises produites ici n'ont aucun attribut, aucun risque de collision.
    return re.sub(r"[ \t]+", " ", typographie("".join(morceaux))).strip()


def convertir(chemin):
    document = docx.Document(chemin)
    lignes = []
    premier = True
    for par in document.paragraphs:
        brut = unicodedata.normalize("NFC", par.text).strip()
        if not brut or CHROME.match(brut):
            continue
        contenu = paragraphe_html(par) or html.escape(brut)

        # Le premier paragraphe est souvent le titre du document, entièrement
        # en gras : la page a déjà son <h1>, on ne le répète pas.
        if premier:
            premier = False
            if re.fullmatch(r"<strong>.*</strong>", contenu) and len(brut) < 90:
                continue

        titre = INTERTITRE.match(brut)
        if titre:
            lignes.append(("h2", html.escape(titre.group(2).strip())))
        elif brut.startswith("*"):
            lignes.append(("li", contenu.lstrip("* ").lstrip()))
        elif brut.startswith("«") and len(brut) > 160:
            lignes.append(("quote", contenu))
        else:
            lignes.append(("p", contenu))

    # regroupement des puces consécutives en une seule liste
    sortie, i = [], 0
    while i < len(lignes):
        genre, texte = lignes[i]
        if genre == "li":
            groupe = []
            while i < len(lignes) and lignes[i][0] == "li":
                groupe.append(f"  <li>{lignes[i][1]}</li>")
                i += 1
            sortie.append("<ul>\n" + "\n".join(groupe) + "\n</ul>")
            continue
        if genre == "h2":
            sortie.append(f"<h2>{texte}</h2>")
        elif genre == "quote":
            sortie.append(f"<blockquote><p>{texte}</p></blockquote>")
        else:
            sortie.append(f"<p>{texte}</p>")
        i += 1
    return "\n".join(sortie)


def main():
    os.makedirs(CIBLE, exist_ok=True)
    vides, ecrits = [], 0
    for slug, relatif in sorted(SOURCES.items()):
        chemin = chemin_source(relatif)
        if chemin is None:
            print(f"  INTROUVABLE  {relatif}")
            continue
        fragment = convertir(chemin)
        destination = os.path.join(CIBLE, slug.replace("/", "__") + ".html")
        if os.path.exists(destination):
            print(f"  conservé     {slug}  (fragment déjà édité)")
            continue
        if not fragment.strip():
            vides.append(slug)
            fragment = ""
        with open(destination, "w", encoding="utf-8") as f:
            f.write(fragment + ("\n" if fragment else ""))
        ecrits += 1
        print(f"  {len(fragment):6d} car.  {slug}")

    print(f"\n{ecrits} fragments écrits dans build/contenu/")
    if vides:
        print("\nDocuments source VIDES — page à rédiger :")
        for slug in vides:
            print(f"  - {slug}")


if __name__ == "__main__":
    sys.exit(main())
