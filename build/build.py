# -*- coding: utf-8 -*-
"""
Générateur du site.

    python build/build.py

Lit contenu/ (un fichier Markdown par page, en-tête YAML) et produit site/,
du HTML statique ordinaire, plus recherche.js pour la recherche plein texte.

contenu/ est la source de vérité : c'est ce que modifie l'interface
d'administration, et c'est ce que l'on édite à la main le cas échéant.
site/ est produit — toute correction qu'on y ferait serait écrasée.
"""
import html
import json
import os
import re
import shutil
import sys
import unicodedata

from urllib.parse import quote, urlencode

import yaml
from markdown_it import MarkdownIt

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENU = os.path.join(RACINE, "contenu")     # les textes, édités par l'admin
STATIQUE = os.path.join(RACINE, "statique")   # feuille de style, scripts, images
SITE_DIR = os.path.join(RACINE, "site")       # produit, jamais édité à la main

# html=True autorise le HTML en ligne : <sup>e</sup>, <cite>…, que Markdown
# ne sait pas exprimer et dont ce corpus a besoin.
MD = MarkdownIt("commonmark", {"html": True, "linkify": False})

ICONES = {
    "vie": '<path d="M32 8v48M16 20l16-8 16 8M14 34c0 6 4 10 9 10s9-4 9-10M32 34c0 6 4 10 9 10s9-4 9-10M14 34l9-14 9 14M32 34l9-14 9 14"/>',
    "colonne": '<path d="M12 54h40M17 50V25m10 25V25m10 25V25m10 25V25M10 20h44L32 8 10 20Z"/>',
    "livre": '<path d="M8 13c9-3 17-1 24 5v36C25 48 17 46 8 49V13Zm48 0c-9-3-17-1-24 5v36c7-6 15-8 24-5V13Z"/>',
    "lyre": '<path d="M24 11h16M21 17h22M24 17c0 9-8 13-8 24 0 9 7 14 16 14s16-5 16-14c0-11-8-15-8-24M27 29v17m5-20v22m5-19v17"/>',
    "loupe": '<circle cx="28" cy="28" r="17"/><path d="m41 41 12 12M20 23h16M20 29h12M20 35h9"/>',
    "cahier": '<path d="M14 9h31a5 5 0 0 1 5 5v41H19a5 5 0 0 1-5-5V9Zm5 0v46m9-35h14M28 28h14M28 36h10"/>',
    "personnes": '<circle cx="24" cy="23" r="8"/><circle cx="43" cy="25" r="6"/><path d="M9 53c1-12 7-18 15-18s15 6 16 18m0-14c8-1 13 5 14 14"/>',
}


# --------------------------------------------------------------------------
# Lecture du contenu
# --------------------------------------------------------------------------
def lire_md(chemin):
    """Sépare l'en-tête YAML du corps Markdown."""
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    if brut.startswith("---"):
        _, entete, corps = brut.split("---", 2)
        donnees = yaml.safe_load(entete) or {}
    else:
        donnees, corps = {}, brut
    donnees["corps"] = corps.strip()
    donnees["fichier"] = os.path.basename(chemin)[:-3]
    return donnees


def charger():
    reglages = lire_md(os.path.join(CONTENU, "reglages.md"))
    accueil = lire_md(os.path.join(CONTENU, "accueil.md"))

    rubriques = sorted(
        (lire_md(os.path.join(CONTENU, "rubriques", n))
         for n in os.listdir(os.path.join(CONTENU, "rubriques")) if n.endswith(".md")),
        key=lambda r: r.get("ordre", 99),
    )
    for rubrique in rubriques:
        rubrique["slug"] = rubrique["fichier"]

    pages = sorted(
        (lire_md(os.path.join(CONTENU, "pages", n))
         for n in os.listdir(os.path.join(CONTENU, "pages")) if n.endswith(".md")),
        key=lambda p: (p.get("rubrique", ""), p.get("ordre", 99)),
    )
    connues = {r["slug"] for r in rubriques}
    for page in pages:
        if page.get("rubrique") not in connues:
            raise SystemExit(
                f"contenu/pages/{page['fichier']}.md : rubrique "
                f"« {page.get('rubrique')} » inconnue."
            )
        page["slug"] = f"{page['rubrique']}/{page['fichier']}"

    doublons = [s for s in {p["fichier"] for p in pages}
                if [p["fichier"] for p in pages].count(s) > 1]
    if doublons:
        raise SystemExit(f"Noms de page en double : {', '.join(doublons)}")

    return reglages, accueil, rubriques, pages


# --------------------------------------------------------------------------
# Petits utilitaires
# --------------------------------------------------------------------------
def sans_balises(fragment):
    """Texte nu, pour les meta et l'index de recherche.

    Les balises de niveau caractère disparaissent sans laisser d'espace,
    sinon « III<sup>e</sup> siècle » deviendrait « III e siècle ».
    """
    texte = re.sub(r"</?(?:sup|sub|em|strong|cite|i|b|span|a|mark)\b[^>]*>", "", fragment)
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", html.unescape(texte)).strip()


def attribut(texte):
    return html.escape(sans_balises(str(texte)), quote=True)


def ancre(texte):
    nu = unicodedata.normalize("NFD", sans_balises(texte)).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", nu.lower())).strip("-")[:60]


def corps_html(page, depuis=""):
    """Rend le Markdown, et donne un identifiant à chaque intertitre.

    Les chemins écrits « /assets/… » dans le contenu sont ramenés au relatif :
    le site doit fonctionner aussi bien à la racine d'un domaine que dans un
    sous-dossier, et même ouvert directement depuis le disque.
    """
    if not page.get("corps"):
        return ""
    rendu = MD.render(page["corps"])
    prefixe = "../" * profondeur(depuis)
    rendu = rendu.replace('href="/assets/', f'href="{prefixe}assets/')
    rendu = rendu.replace('src="/assets/', f'src="{prefixe}assets/')
    return re.sub(r"<h2>(.*?)</h2>",
                  lambda m: f'<h2 id="{ancre(m.group(1))}">{m.group(1)}</h2>',
                  rendu).strip()


def profondeur(slug):
    return slug.count("/")


def vers(slug, depuis):
    """Lien relatif entre deux pages, sans dépendre du domaine ni du sous-chemin."""
    prefixe = "../" * profondeur(depuis)
    if slug in ("", "index"):
        return prefixe + "index.html"
    cible, _, an = slug.partition("#")
    return prefixe + cible + ".html" + (("#" + an) if an else "")


# --------------------------------------------------------------------------
# Gabarit
# --------------------------------------------------------------------------
def entete(ctx, courant, depuis):
    liens = []
    for rubrique in ctx["rubriques"]:
        marque = ' aria-current="page"' if rubrique["slug"] == courant else ""
        liens.append(
            f'<a href="{vers(rubrique["slug"], depuis)}"{marque}>{rubrique["nav"]}</a>'
        )
    prefixe = "../" * profondeur(depuis)
    return f"""    <header class="site-header">
      <a class="brand" href="{vers('index', depuis)}">
        <img class="brand__mark" src="{prefixe}assets/images/ex-libris.png" width="480" height="385" alt="" />
        <span class="brand__name">Société des amis<br />d’Henri Irénée Marrou</span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="navigation-principale">
        <span></span><span></span><span></span><span class="sr-only">Ouvrir le menu</span>
      </button>
      <nav id="navigation-principale" class="main-nav" aria-label="Navigation principale">
        {chr(10) + '        '.join(liens)}
      </nav>
      <button class="search-button" type="button" aria-label="Rechercher sur le site" data-search-open>
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m16.5 16.5 4 4"></path></svg>
      </button>
    </header>"""


def pied(ctx, depuis):
    site = ctx["reglages"]
    rubriques = "".join(
        f'<li><a href="{vers(r["slug"], depuis)}">{r["nav"]}</a></li>'
        for r in ctx["rubriques"]
    )
    return f"""    <footer class="site-footer">
      <div class="site-footer__grid">
        <div>
          <p class="site-footer__nom">{site['nom']}</p>
          <p>Association déclarée sous le régime de la loi de 1901, créée en 2007.<br />
             Siège : 3 rue Castex, 75004 Paris.</p>
          <p><a href="mailto:{site['courriel']}">{site['courriel']}</a></p>
        </div>
        <nav aria-label="Plan du site">
          <p class="site-footer__titre">Le site</p>
          <ul>{rubriques}</ul>
        </nav>
        <div>
          <p class="site-footer__titre">Soutenir</p>
          <ul>
            <li><a href="{vers('association', depuis)}#adherer">Adhérer à la Société</a></li>
            <li><a href="{vers('cahiers', depuis)}">Lire les Cahiers Marrou</a></li>
            <li><a href="mailto:{site['courriel']}">Nous écrire</a></li>
          </ul>
        </div>
      </div>
    </footer>"""


def dialogue_recherche(depuis):
    return f"""    <dialog class="search-dialog" data-search-dialog>
      <form method="dialog" class="search-dialog__top">
        <strong>Rechercher sur le site</strong>
        <button aria-label="Fermer la recherche">×</button>
      </form>
      <form data-site-search role="search">
        <label for="site-query">Saisissez un mot-clé</label>
        <div>
          <input id="site-query" name="query" type="search" autocomplete="off"
                 placeholder="Marrou, saint Augustin, musique…" />
          <button type="submit">Rechercher</button>
        </div>
        <p class="form-status" aria-live="polite" data-search-status></p>
      </form>
      <ol class="search-results" data-search-results></ol>
    </dialog>
    <script>window.BASE_SITE = {json.dumps("../" * profondeur(depuis))};</script>"""


def document(ctx, slug, titre_onglet, description, corps, courant,
             classe_body="", avec_pied=True):
    site = ctx["reglages"]
    prefixe = "../" * profondeur(slug)
    canonique = site["url"].rstrip("/") + "/" + ("" if slug == "index" else slug + ".html")
    classe = f' class="{classe_body}"' if classe_body else ""
    return f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{titre_onglet}</title>
    <meta name="description" content="{attribut(description)}" />
    <link rel="canonical" href="{canonique}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{site['nom']}" />
    <meta property="og:title" content="{attribut(titre_onglet)}" />
    <meta property="og:description" content="{attribut(description)}" />
    <meta property="og:image" content="{site['url'].rstrip('/')}/assets/images/marrou-portrait.jpg" />
    <meta property="og:locale" content="fr_FR" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="icon" href="{prefixe}assets/images/ex-libris.png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{prefixe}styles.css" />
    <script src="{prefixe}app.js" defer></script>
  </head>
  <body{classe}>
    <a class="skip-link" href="#contenu">Aller au contenu</a>

{entete(ctx, courant, slug)}

{corps}

{pied(ctx, slug) if avec_pied else ''}

{dialogue_recherche(slug)}
  </body>
</html>
"""


# --------------------------------------------------------------------------
# Corps des pages
# --------------------------------------------------------------------------
def corps_accueil(ctx):
    accueil, site = ctx["accueil"], ctx["reglages"]
    cartes = []
    sommaire = [r for r in ctx["rubriques"] if r.get("sommaire", True)]
    for i, rubrique in enumerate(sommaire, start=1):
        cartes.append(f"""        <a href="{vers(rubrique['slug'], 'index')}">
          <svg viewBox="0 0 64 64" aria-hidden="true">{ICONES.get(rubrique.get('icone'), '')}</svg>
          <span><strong>{rubrique['nav']}</strong><small>{rubrique['resume']}</small></span><b>{i:02d}</b>
        </a>""")

    liens = "".join(
        f'<a href="{vers(t["cible"], "index")}">{t["libelle"]}</a>'
        for t in site.get("transversaux", [])
    )

    return f"""    <main id="contenu">
      <section class="portal" aria-labelledby="portal-title">
        <div class="portal__hero">
          <div class="portal__identity">
            <p class="eyebrow">{accueil['dates']}</p>
            <h1 id="portal-title">{accueil['titre']}</h1>
            <p class="portal__subtitle">{accueil['sous_titre']}</p>
            <span class="rule" aria-hidden="true"></span>
            <p>{accueil['chapeau']}</p>
            <a class="button button--primary" href="{vers('decouvrir', 'index')}">Découvrir Marrou <span aria-hidden="true">→</span></a>
          </div>
          <div class="portal__portrait">
            <img src="assets/images/marrou-portrait.jpg"
                 width="1548" height="1012" fetchpriority="high"
                 alt="Portrait photographique d’Henri-Irénée Marrou, en extérieur, coiffé d’une calotte." />
          </div>
        </div>

        <nav class="portal__chapters" aria-label="Sommaire du site">
{chr(10).join(cartes)}
        </nav>

        <div class="portal__utility">
          <blockquote><p>« {accueil['citation']} »</p></blockquote>
          <div>{liens}</div>
        </div>
      </section>
    </main>"""


def fil_ariane(ctx, page, depuis):
    """Retour au niveau supérieur, en haut à gauche, dans le flux."""
    parent = page.get("rubrique")
    if parent:
        rubrique = next(r for r in ctx["rubriques"] if r["slug"] == parent)
        return (f'      <a class="back-to-portal" href="{vers(parent, depuis)}">'
                f'<span aria-hidden="true">←</span> {rubrique["nav"]}</a>')
    return (f'      <a class="back-to-portal" href="{vers("index", depuis)}">'
            f'<span aria-hidden="true">←</span> Retour au sommaire</a>')


def freres(ctx, page):
    parent = page.get("rubrique")
    if parent:
        return [p for p in ctx["pages"] if p.get("rubrique") == parent]
    return ctx["rubriques"]


def enchainement(ctx, page, depuis):
    """Pied de chapitre : page précédente et suivante parmi les sœurs."""
    voisines = freres(ctx, page)
    slugs = [p["slug"] for p in voisines]
    if page["slug"] not in slugs or len(voisines) < 2:
        return ""
    i = slugs.index(page["slug"])
    precedent = voisines[i - 1] if i > 0 else None
    suivant = voisines[i + 1] if i < len(voisines) - 1 else None
    if not precedent and not suivant:
        return ""

    gauche = (f'<a class="chapter-nav__prev" href="{vers(precedent["slug"], depuis)}">'
              f'<span aria-hidden="true">←</span><span><small>Précédent</small>'
              f'<strong>{precedent.get("nav", precedent["titre"])}</strong></span></a>'
              ) if precedent else "<span></span>"
    droite = (f'<a class="chapter-nav__next" href="{vers(suivant["slug"], depuis)}">'
              f'<span><small>Suivant</small>'
              f'<strong>{suivant.get("nav", suivant["titre"])}</strong></span>'
              f'<span aria-hidden="true">→</span></a>'
              ) if suivant else "<span></span>"
    return f"""      <nav class="chapter-nav" aria-label="Pages voisines">
        {gauche}
        {droite}
      </nav>"""


def rail(ctx, page, rendu, depuis):
    """Colonne de droite : sections de la page, puis pages voisines.

    Sans elle, le texte occuperait la moitié gauche et la moitié droite
    resterait vide. La colonne de lecture doit rester étroite — c'est ce qui
    rend un texte long lisible — mais l'espace récupéré porte deux repères.
    """
    blocs = []

    sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', rendu)
    if len(sections) >= 3:
        items = "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in sections)
        blocs.append('<nav class="page-rail__toc" aria-label="Sections de cette page">'
                     '<p class="page-rail__titre">Sur cette page</p>'
                     f'<ul>{items}</ul></nav>')

    parent = page.get("rubrique")
    if parent:
        rubrique = next(r for r in ctx["rubriques"] if r["slug"] == parent)
        items = ""
        for voisine in [p for p in ctx["pages"] if p.get("rubrique") == parent]:
            ici = ' aria-current="page"' if voisine["slug"] == page["slug"] else ""
            items += (f'<li><a href="{vers(voisine["slug"], depuis)}"{ici}>'
                      f'{voisine["titre"]}</a></li>')
        blocs.append('<nav class="page-rail__voisines" aria-label="Autres pages de la rubrique">'
                     f'<p class="page-rail__titre">{rubrique["nav"]}</p>'
                     f'<ul>{items}</ul></nav>')

    if not blocs:
        return ""
    return ('        <aside class="page-rail">\n          '
            + "\n          ".join(blocs) + "\n        </aside>")


def grille_enfants(ctx, rubrique):
    cartes = []
    for enfant in [p for p in ctx["pages"] if p.get("rubrique") == rubrique["slug"]]:
        vide = "" if enfant.get("corps") else '<span class="card-flag">Contenu à venir</span>'
        cartes.append(
            f'          <a href="{vers(enfant["slug"], rubrique["slug"])}">'
            f'<strong>{enfant["titre"]}</strong>'
            f'<span>{enfant["resume"]}</span>{vide}</a>'
        )
    return ('        <div class="chapter-content chapter-content--cards">\n'
            + "\n".join(cartes) + "\n        </div>")


def bouton_correction(ctx, page):
    """Proposer une correction, sans compte à créer : un courriel prérempli.

    Volontairement rudimentaire et sans coût. Peut être remplacé plus tard par
    un formulaire, sans rien changer d'autre au site.
    """
    site = ctx["reglages"]
    sujet = f"Correction — {sans_balises(page['titre'])}"
    corps = (f"Page : {site['url'].rstrip('/')}/{page['slug']}.html\r\n\r\n"
             "Correction ou complément proposé :\r\n\r\n")
    # Encodage d'URL d'abord (accents, tirets longs, retours à la ligne),
    # échappement HTML ensuite pour l'attribut — l'ordre inverse casserait tout.
    requete = urlencode({"subject": sujet, "body": corps}, quote_via=quote)
    lien = html.escape(f"mailto:{site['courriel']}?{requete}", quote=True)
    return (f'      <p class="page-correction"><a href="{lien}">'
            'Proposer une correction ou un complément pour cette page</a></p>')


def corps_page(ctx, page):
    depuis = page["slug"]
    rendu = corps_html(page, page["slug"])
    surtitre = page.get("surtitre")
    if not surtitre and page.get("rubrique"):
        surtitre = next(r for r in ctx["rubriques"]
                        if r["slug"] == page["rubrique"])["nav"]

    morceaux = []
    if page.get("grille"):
        morceaux.append(grille_enfants(ctx, page))
    if rendu or not page.get("grille"):
        texte = rendu or (
            '<p class="notice">Cette page attend son texte. Le document récupéré '
            'de l’ancien site est vide ; le contenu sera ajouté dès qu’il aura été '
            'retrouvé ou rédigé.</p>'
        )
        article = f'        <article class="prose">\n{texte}\n        </article>'
        cote = rail(ctx, page, rendu, depuis)
        morceaux.append(
            f'      <div class="chapter-body">\n{article}\n{cote}\n      </div>'
            if cote else article
        )
    if page["slug"] == "association":
        courriel = ctx["reglages"]["courriel"]
        morceaux.append(f"""        <div class="association-actions" id="contact">
          <a class="button button--primary" href="mailto:{courriel}">Contacter l’Association</a>
          <a class="button button--outline" id="adherer" href="mailto:{courriel}?subject=Adh%C3%A9sion">Adhérer</a>
        </div>""")

    return f"""    <main id="contenu">
      <article class="page-panel">
{fil_ariane(ctx, page, depuis)}
        <div class="chapter-hero">
          <p class="chapter-number">{surtitre or ''}</p>
          <h1>{page['titre']}</h1>
          <p>{page['chapeau']}</p>
        </div>
{chr(10).join(morceaux)}
{bouton_correction(ctx, page)}
{enchainement(ctx, page, depuis)}
      </article>
    </main>"""


# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------
def ecrire(chemin_relatif, contenu):
    chemin = os.path.join(SITE_DIR, chemin_relatif)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)


def main():
    reglages, accueil, rubriques, pages = charger()
    ctx = {"reglages": reglages, "accueil": accueil,
           "rubriques": rubriques, "pages": pages}

    # Reconstruction complète : site/ est jetable et entièrement reproductible.
    shutil.rmtree(SITE_DIR, ignore_errors=True)
    shutil.copytree(STATIQUE, SITE_DIR)

    index = []

    ecrire("index.html", document(
        ctx, "index",
        f"{accueil['titre']} — {reglages['nom']}",
        accueil["description"],
        corps_accueil(ctx),
        courant=None, classe_body="page-accueil", avec_pied=False,
    ))
    index.append({
        "url": "index.html", "titre": accueil["titre"], "rubrique": "Accueil",
        "extrait": sans_balises(accueil["chapeau"]),
        "texte": sans_balises(accueil["chapeau"] + " " + accueil["description"]),
    })

    for page in rubriques + pages:
        courant = page.get("rubrique", page["slug"])
        titre_onglet = f"{sans_balises(page['titre'])} — {reglages['titre_court']}"
        description = page.get("description") or page["chapeau"]
        ecrire(page["slug"] + ".html",
               document(ctx, page["slug"], titre_onglet, description,
                        corps_page(ctx, page), courant))

        nom_rubrique = next((r["nav"] for r in rubriques if r["slug"] == courant), "")
        index.append({
            "url": page["slug"] + ".html",
            "titre": sans_balises(page["titre"]),
            "rubrique": nom_rubrique,
            "extrait": sans_balises(page["chapeau"])[:180],
            "texte": (sans_balises(page["titre"]) + " " +
                      sans_balises(page["chapeau"]) + " " +
                      sans_balises(corps_html(page, page["slug"])))[:20000],
        })

    # Index chargé par balise <script> et non par fetch() : la recherche
    # fonctionne aussi quand on ouvre les fichiers directement, sans serveur.
    ecrire("recherche.js", "window.INDEX_RECHERCHE = "
           + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n")

    poids = os.path.getsize(os.path.join(SITE_DIR, "recherche.js")) / 1024
    vides = [p["slug"] for p in pages if not p.get("corps")]
    print(f"{len(index)} pages produites dans site/")
    print(f"recherche.js : {len(index)} entrées, {poids:.0f} Ko")
    if vides:
        print("\nPages sans contenu :")
        for slug in vides:
            print(f"  - {slug}")


if __name__ == "__main__":
    sys.exit(main())
