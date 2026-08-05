# -*- coding: utf-8 -*-
"""
Reprise des textes depuis les .docx, en corrigeant deux défauts de la
première extraction :

1. **Les liens hypertextes étaient perdus** — et avec eux leur texte, ce qui
   produisait des phrases tronquées (« publiées dans . »). python-docx
   n'expose pas les runs situés dans un élément <w:hyperlink> ; il faut
   parcourir le XML du paragraphe dans l'ordre.

2. **Les marques d'emphase étaient malformées.** Word découpe un paragraphe en
   dizaines de runs et marque en gras ou en italique jusqu'aux espaces. Traduit
   naïvement, cela donne « **texte ** » ou « **** », que Markdown ne comprend
   pas. Il faut fusionner les segments voisins et sortir les espaces des
   marques.

Seul le CORPS des fichiers de contenu/ est remplacé ; les en-têtes YAML,
relus et complétés à la main, sont conservés.

    python build/migration/reprendre_textes.py
"""
import os
import re
import sys
import unicodedata

import docx
from docx.oxml.ns import qn

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import extraire_docx  # noqa: E402
from extraire_docx import CHROME, INTERTITRE, SOURCES, typographie  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(ICI))
CONTENU = os.path.join(RACINE, "contenu")

# extraire_docx calcule la racine depuis son propre emplacement ; il a depuis
# été rangé dans build/migration/, ce qui fausse le chemin des sources.
extraire_docx.SOURCE = os.path.join(RACINE, "SAHIM_Site Internet_Récupération")
chemin_source = extraire_docx.chemin_source

# Les liens de l'ancien site vers ses propres pages ne mènent plus nulle part :
# on garde leur texte, on jette l'adresse.
INTERNE = re.compile(r"henrimarrou\.org/index|/index\.php", re.I)

# Les .docx ont été récupérés depuis Internet Archive : toutes les adresses
# sont enveloppées dans web.archive.org.
ARCHIVE = re.compile(r"^https?://web\.archive\.org/web/\d+\w*/(.*)$", re.I)


# Les PDF de l'ancien site ont été retrouvés : ils sont désormais servis par
# le site lui-même, et ne dépendent plus d'archive.org.
DOCUMENTS = {
    "MarrouCFDTentreFevrier1941e": "marrou-cftc-1941-1943.pdf",
    "Diapason": "diapason-musique-discographie.pdf",
    "Henri%20Davenson%20Critique": "davenson-critique-musicale-esprit.pdf",
    "Barbier": "barbier-le-livre-des-chansons.pdf",
}


def nettoyer_lien(cible):
    """Déballe les adresses archivées et écarte celles qui ne mènent nulle part.

    Trois cas :
      - PDF retrouvé en local  -> lien vers le site lui-même ;
      - lien externe (Wikipédia…) -> lien direct, l'instantané n'apporte rien ;
      - page de l'ancien site  -> abandonné, seul le texte du lien est gardé.
    """
    for motif, fichier in DOCUMENTS.items():
        if motif in cible:
            return "/assets/documents/" + fichier

    archive = ARCHIVE.match(cible)
    if archive:
        # Document de l'ancien site non retrouvé en local : l'archive est le
        # seul accès qui subsiste, on garde donc l'enveloppe telle quelle.
        if "henrimarrou.org/uploads" in archive.group(1):
            return cible
        cible = archive.group(1)
        cible = re.sub(r"^(https?):/(?!/)", r"\1://", cible)
        if cible.startswith("mailto :"):
            cible = cible.replace("mailto :", "mailto:", 1)

    if INTERNE.search(cible):
        return ""
    if cible.startswith("mailto:"):
        return cible
    if not cible.startswith("http"):
        cible = "https://" + cible
    # Wikipédia et les grands sites sont en HTTPS depuis longtemps.
    return re.sub(r"^http://(?=(fr|en)\.wikipedia\.org)", "https://", cible)


def segments(paragraphe):
    """Runs et hyperliens du paragraphe, dans l'ordre, fusionnés par style."""
    sortie = []

    def ajouter(texte, italique, gras, lien):
        if not texte:
            return
        # tuple() indispensable : une liste n'est jamais égale à un tuple,
        # et la comparaison échouait silencieusement — aucun segment n'était
        # fusionné, d'où les mots coupés au milieu.
        if sortie and tuple(sortie[-1][1:]) == (italique, gras, lien):
            sortie[-1][0] += texte
        else:
            sortie.append([texte, italique, gras, lien])

    for noeud in paragraphe._p:
        if noeud.tag == qn("w:r"):
            texte = "".join(n.text or "" for n in noeud.iter(qn("w:t")))
            rpr = noeud.find(qn("w:rPr"))
            ital = rpr is not None and rpr.find(qn("w:i")) is not None
            gras = rpr is not None and rpr.find(qn("w:b")) is not None
            ajouter(texte, ital, gras, None)

        elif noeud.tag == qn("w:hyperlink"):
            texte = "".join(n.text or "" for n in noeud.iter(qn("w:t")))
            rid = noeud.get(qn("r:id"))
            cible = ""
            if rid and rid in paragraphe.part.rels:
                cible = nettoyer_lien(paragraphe.part.rels[rid].target_ref)
            ajouter(texte, False, False, cible or None)

    # Word coupe parfois un mot en plein milieu et change de style : « Pro »
    # italique, « so » gras, « pographie » italique. Traduit tel quel, cela
    # donne *Pro**so**pographie*, illisible. Quand la frontière tombe entre
    # deux lettres, le style du fragment le plus long l'emporte sur tout le mot.
    i = 1
    while i < len(sortie):
        avant, apres = sortie[i - 1], sortie[i]
        colles = (avant[0] and apres[0]
                  and avant[0][-1].isalpha() and apres[0][0].isalpha())
        if colles and avant[3] is None and apres[3] is None and avant[1:] != apres[1:]:
            # On n'absorbe que la fin du mot, pas tout le segment suivant :
            # « Carnets posthume » italique + « s ( » romain doit donner
            # « Carnets posthumes » italique, puis « ( » romain.
            fin_du_mot = re.match(r"[^\W\d_]+", apres[0]).group()
            reste = apres[0][len(fin_du_mot):]
            gagnant = avant if len(avant[0]) >= len(fin_du_mot) else apres
            avant[0] += fin_du_mot
            avant[1], avant[2] = gagnant[1], gagnant[2]
            if reste:
                apres[0] = reste
                i += 1
            else:
                del sortie[i]
        else:
            i += 1

    # « Les » gras, puis une espace nue, puis « livres » gras : trois segments
    # qui donneraient **Les** **livres**. On les réunit en **Les livres**, sans
    # quoi le nettoyage des marques vides recollerait les deux mots.
    i = 1
    while i < len(sortie) - 1:
        avant, milieu, apres = sortie[i - 1], sortie[i], sortie[i + 1]
        if not milieu[0].strip() and avant[1:] == apres[1:] and avant[3] is None:
            avant[0] += milieu[0] + apres[0]
            del sortie[i:i + 2]
        else:
            i += 1

    return sortie


def marquer(texte, marque):
    """Applique **/* en gardant les espaces à l'extérieur des marques.

    Markdown exige que le délimiteur touche un caractère non blanc :
    « ** mot ** » n'est pas du gras, « **mot** » l'est.
    """
    gauche = len(texte) - len(texte.lstrip())
    droite = len(texte) - len(texte.rstrip())
    coeur = texte.strip()
    if not coeur:
        return texte
    return texte[:gauche] + marque + coeur + marque + (texte[len(texte) - droite:] if droite else "")


def guillemets(texte, etat):
    """Guillemets droits -> français, en suivant l'ouverture d'un segment à
    l'autre. Une paire est souvent coupée en deux runs Word : la traiter
    segment par segment isolément produisait un « » » en début de citation.

    Doit s'appliquer AVANT les marques Markdown, sinon la paire chevauche
    les délimiteurs et les déséquilibre.
    """
    sortie = []
    for caractere in texte.replace("'", "’"):
        if caractere == '"':
            sortie.append("« " if not etat["ouvert"] else " »")
            etat["ouvert"] = not etat["ouvert"]
        else:
            sortie.append(caractere)
    return "".join(sortie)


def rendre(paragraphe):
    morceaux = []
    etat = {"ouvert": False}
    for texte, italique, gras, lien in segments(paragraphe):
        texte = guillemets(unicodedata.normalize("NFC", texte), etat)
        if not texte.strip():
            morceaux.append(texte)
            continue
        if lien:
            # Les espaces qui entourent le libellé sont des séparateurs de mots :
            # les avaler collerait le lien au texte voisin.
            avant = texte[:len(texte) - len(texte.lstrip())]
            apres = texte[len(texte.rstrip()):]
            morceaux.append(f"{avant}[{texte.strip()}]({lien}){apres}")
            continue
        if italique:
            texte = marquer(texte, "*")
        if gras:
            texte = marquer(texte, "**")
        morceaux.append(texte)

    rendu = "".join(morceaux)
    if etat["ouvert"]:
        # Nombre impair de guillemets droits dans la source : le dernier
        # ouvrant n'a pas de fermant. Mieux vaut le retirer que le laisser.
        rendu = "".join(rendu.rsplit("« ", 1))
    return assainir(rendu)


def assainir(texte):
    """Garantit un Markdown valide, quelles que soient les fantaisies de Word.

    Word applique gras et italique jusqu'aux espaces et découpe les phrases en
    dizaines de runs ; certaines combinaisons produisent des marques
    déséquilibrées, que Markdown affiche telles quelles à l'écran. On préfère
    perdre un gras-italique çà et là plutôt qu'afficher des astérisques.
    """
    # Marques vides : on retire les astérisques, jamais l'espace qu'elles
    # encadrent — sans quoi « **Les** **livres** » devenait « Leslivres ».
    texte = re.sub(r"\*{2,}(\s*)\*{2,}", r"\1", texte)
    texte = re.sub(r"\*{3,}", "**", texte)             # gras-italique -> gras

    if texte.count("**") % 2:                          # gras non apparié
        texte = "".join(texte.rsplit("**", 1))
    if len(re.findall(r"(?<!\*)\*(?!\*)", texte)) % 2:  # italique non apparié
        texte = re.sub(r"(?<!\*)\*(?!\*)(?!.*(?<!\*)\*(?!\*))", "", texte)

    texte = re.sub(r"»(?=[\w])", "» ", texte)          # « … »n°2  ->  « … » n°2
    texte = re.sub(r"\s+([,.])", r"\1", texte)         # virgule et point collés
    texte = re.sub(r"[ \t]+", " ", texte)
    return typographie_francaise(texte).strip()


# Espace insécable : la ponctuation double ne doit jamais se retrouver seule
# en début de ligne. Les deux-points d'une URL et d'une heure sont épargnés.
INSECABLE = " "


def typographie_francaise(texte):
    """N'intervient jamais dans la cible d'un lien : une adresse contient des
    deux-points, qu'une espace insécable rendrait invalide."""
    morceaux = re.split(r"(\]\([^)]*\))", texte)
    for i, morceau in enumerate(morceaux):
        if morceau.startswith("]("):
            continue
        # « [  ]* » et non « ?» : les sources contiennent déjà des espaces
        # multiples et parfois insécables, qu'il faut absorber, pas doubler.
        morceau = re.sub(r"[  ]*([;!?])", INSECABLE + r"\1", morceau)
        # Ancré sur le caractère qui précède : un simple regard arrière
        # laisserait le motif reculer et ajouterait une espace à celle
        # déjà présente. Les URL et les heures sont épargnées.
        # Seule une heure — chiffres des deux côtés — garde ses deux-points
        # collés. « n°6: » est une référence, pas une heure : elle prend
        # l'espace insécable comme toute ponctuation double.
        morceau = re.sub(r"(\S)[  ]*:(?!//)",
                         lambda m: m.group(1) + ":" if m.group(1).isdigit()
                         and re.match(r"\d", morceau[m.end():m.end() + 1] or " ")
                         else m.group(1) + INSECABLE + ":", morceau)
        morceau = re.sub(r"«[  ]*", "«" + INSECABLE, morceau)
        morceau = re.sub(r"[  ]*»", INSECABLE + "»", morceau)
        # Restent les suites d'espaces héritées de la source, en dehors de
        # la ponctuation double : une seule espace ordinaire suffit.
        morceaux[i] = re.sub(r"[  ]{2,}(?![;:!?»])", " ", morceau)
    return "".join(morceaux)


def convertir(chemin):
    document = docx.Document(chemin)
    lignes, premier = [], True

    for paragraphe in document.paragraphs:
        brut = unicodedata.normalize("NFC", paragraphe.text).strip()
        if not brut or CHROME.match(brut):
            continue
        rendu = rendre(paragraphe)
        if not rendu:
            continue

        if premier:
            premier = False
            if re.fullmatch(r"\*\*.*\*\*", rendu) and len(brut) < 90:
                continue   # titre du document : la page a déjà son <h1>

        titre = INTERTITRE.match(brut)
        if titre:
            lignes.append(("h2", titre.group(2).strip()))
        elif brut.startswith("*") and not rendu.startswith("**"):
            lignes.append(("li", rendu.lstrip("*").lstrip()))
        elif brut.startswith("«") and len(brut) > 160:
            lignes.append(("quote", rendu))
        else:
            lignes.append(("p", rendu))

    blocs, i = [], 0
    while i < len(lignes):
        genre, texte = lignes[i]
        if genre == "li":
            groupe = []
            while i < len(lignes) and lignes[i][0] == "li":
                groupe.append("- " + lignes[i][1])
                i += 1
            blocs.append("\n".join(groupe))
            continue
        blocs.append({"h2": "## " + texte,
                      "quote": "> " + texte}.get(genre, texte))
        i += 1
    return "\n\n".join(blocs)


def main():
    remplaces, liens = 0, 0
    # Quelques noms de page ne se déduisent pas du slug d'origine.
    exceptions = {"ressources-livres": "les-livres",
                  "ressources-bibliographie": "bibliographie",
                  "ressources-articles": "articles"}

    for slug, relatif in sorted(SOURCES.items()):
        nom = exceptions.get(slug, slug.split("/")[-1])
        for dossier in ("pages", "rubriques"):
            cible = os.path.join(CONTENU, dossier, nom + ".md")
            if os.path.exists(cible):
                break
        else:
            cible = os.path.join(CONTENU, "pages",
                                 slug.replace("ressources-", "") + ".md")
            if not os.path.exists(cible):
                print(f"  ignoré (pas de page) : {slug}")
                continue

        source = chemin_source(relatif)
        if source is None:
            continue
        corps = convertir(source)
        liens += len(re.findall(r"\]\(http", corps))

        with open(cible, encoding="utf-8") as f:
            actuel = f.read()
        _, entete, _ = actuel.split("---", 2)
        with open(cible, "w", encoding="utf-8") as f:
            f.write("---" + entete + "---\n\n" + (corps + "\n" if corps else ""))
        remplaces += 1

    print(f"{remplaces} textes repris, {liens} liens externes rétablis")


if __name__ == "__main__":
    sys.exit(main())
