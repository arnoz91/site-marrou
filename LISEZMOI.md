# Site de la Société des amis d’Henri Irénée Marrou

Direction visuelle « Revue savante » (maquette A) validée le 4 août 2026.
**Le contenu de `site/` est généré** : ne pas y corriger un texte, il serait
écrasé à la construction suivante. Voir « Modifier le site » plus bas.

## Organisation

```
contenu/            LES TEXTES — la source de vérité, éditée via /admin
  accueil.md
  reglages.md
  rubriques/        les 7 grandes sections
  pages/            les 20 pages de contenu
statique/           feuille de style, scripts, images, interface /admin
build/
  build.py          assemble contenu/ + statique/ -> site/
  verifier.py       contrôle les liens avant publication
  migration/        scripts d'usage unique, conservés pour mémoire
site/               PRODUIT — jamais édité à la main, absent du dépôt
```

28 pages. Chacune a son titre, sa meta description, son URL canonique et ses
balises OpenGraph : les moteurs les indexent séparément, et un lien partagé
affiche le titre de la page concernée.

## Modifier le site

**En temps normal, par l’interface d’administration** — voir
[ADMINISTRATION.md](ADMINISTRATION.md). Un enregistrement suffit : le site
se reconstruit et se publie seul.

À la main, si besoin :

| Ce que l’on veut changer | Où |
| --- | --- |
| Le texte d’une page | `contenu/pages/<nom>.md` |
| Une rubrique | `contenu/rubriques/<nom>.md` |
| L’accueil | `contenu/accueil.md` |
| Nom, adresse, courriel, liens du bandeau | `contenu/reglages.md` |
| Ajouter une page | un nouveau fichier dans `contenu/pages/` |
| L’apparence | `statique/styles.css` |
| Le comportement | `statique/app.js` |

Chaque fichier de page a un en-tête `titre / chapeau / resume / rubrique /
ordre`, puis le texte en Markdown. Le nom du fichier donne l’adresse de la
page ; `rubrique` la range ; `ordre` la place dans sa rubrique.

Puis :

```bash
pip install -r build/requirements.txt   # une seule fois
python build/build.py
python build/verifier.py
```

`verifier.py` contrôle liens, ancres, titres et descriptions. Il tourne aussi
avant chaque publication : **une page cassée ne peut pas atteindre le site**.

## Aperçu local

```bash
python -m http.server 4321 --directory site
```

Puis <http://localhost:4321>. Le site fonctionne aussi en ouvrant
`site/index.html` directement, recherche comprise : l’index est chargé par
balise `<script>` et non par `fetch()`, qui serait bloqué sur `file://`.

## Recherche

Recherche plein texte entièrement côté navigateur, sans serveur ni base de
données — donc sans coût d’hébergement. `build.py` produit `recherche.js`
(98 Ko, 28 entrées), chargé au premier usage seulement.

Elle est insensible aux accents (« resistance » trouve « Résistance »),
accepte plusieurs mots, classe les résultats en privilégiant les titres et
surligne les termes trouvés. Ouverture par la loupe ou par la touche `/`.

À l’échelle actuelle c’est instantané. Ce dispositif tient sans peine
jusqu’à quelques centaines de pages ; au-delà, il faudra un index inversé.

## Mise en page des pages de contenu

La colonne de lecture est volontairement étroite (40rem, environ 70 signes) :
au-delà, l’œil perd la ligne en revenant à la marge. Mais une colonne étroite
seule laisserait la moitié droite vide, ce qui se lit comme un défaut.

L’espace récupéré porte donc un **rail** : le sommaire de la page (dès trois
sections) et les autres pages de la rubrique, avec la page courante marquée.
On passe ainsi de « La méthode historique » à « La Résistance » sans remonter.

En dessous de 71rem le rail se dissout (`display: contents`) et ses deux blocs
se replacent là où ils servent : le sommaire **avant** le texte, les pages
voisines **après**. L’inverse repoussait l’article très bas sur téléphone.

## L’ex-libris

C’est l’emblème de l’association : il doit se voir. Deux leviers ont été
utilisés ensemble, car la taille seule ne suffisait pas.

- **Le contraste.** Le premier détourage laissait un trait gris à 55 % : à
  60 px le dessin se lisait comme une tache. Il est désormais détouré en noir
  franc sur fond transparent, avec une courbe qui renforce les traits fins.
- **La taille.** `clamp(2.8rem, min(5.8vw, 11vh), 5.4rem)`, et un cran de plus
  sur l’accueil (`6.4rem`), où l’en-tête porte l’identité. Les pages
  intérieures gardent un en-tête plus discret, pour laisser la place au texte.

Conséquence à ne pas défaire : la barre de navigation se replie désormais à
**78rem** et non 71 — l’emblème plus large faisait passer les sept rubriques
sur deux lignes vers 1200 px, ce qui suffisait à faire déborder l’accueil.

## L’accueil sans défilement

L’accueil doit tenir sur un écran quel que soit le zoom. Deux mécanismes s’y
emploient, à conserver ensemble :

1. **Les tailles de l’accueil sont bornées en hauteur autant qu’en largeur** :
   `clamp(plancher, min(formule-vw, N vh), plafond)`. Le terme en `vh` ne mord
   que sur les écrans courts — quand l’utilisateur zoome — et laisse la mise
   en page intacte sur un grand écran.
2. **La rangée du héros est en `minmax(min-content, 1fr)`** : elle absorbe la
   place disponible sans jamais descendre sous son contenu. Si l’espace manque
   vraiment, la page défile au lieu de rogner.

Ne jamais remplacer ces `clamp()` par des valeurs fixes : c’est ce qui faisait
déborder l’accueil.

Trois conséquences à ne pas défaire : la barre de navigation se replie à
**78rem** ; **l’accueil n’a pas de pied de page** — le bandeau de citation en
tient lieu, avec les liens transversaux ; et **le portrait est posé en absolu
dans un cadre**. Ce dernier point n’est pas décoratif : une `<img>` en flux
impose au héros une hauteur minimale déduite de sa largeur et de son rapport
d’image. Sur une fenêtre large et courte — le cas normal une fois retirées les
barres du navigateur — cela faisait déborder l’accueil, d’autant plus que
l’écran était large. En absolu, l’image ne pèse plus rien dans le calcul.

**La barre de défilement occupe une place réservée en permanence**
(`scrollbar-gutter: stable` sur `html`). L’accueil tient sur un écran, donc
sans barre ; les pages intérieures en ont une. Sans cette réserve, les 15 px
d’écart décalaient toute la barre de navigation d’une page à l’autre, ce qui
se voit immédiatement. Ne pas retirer cette règle.

**Tester en hauteur de fenêtre, pas en hauteur d’écran.** Un écran 1440 × 900
donne une fenêtre d’environ 760 px de haut une fois les barres du navigateur
retirées. Le défaut ci-dessus était passé inaperçu parce que les essais ne
couvraient que des couples « large et haut » ou « étroit et court ». Le
balayage à utiliser croise 9 largeurs (1000 → 2560) et 9 hauteurs (480 → 1000).

État vérifié :

| Écran | 100 % | 125 % | 150 % | 175 % | 200 % |
| --- | --- | --- | --- | --- | --- |
| 1920 × 1080 | tient | tient | tient | — | tient |
| 1440 × 900 | tient | tient | tient | tient | défile |
| 1366 × 768 | tient | tient | tient | — | — |
| 1280 × 800 | tient | tient | tient | — | — |

## Vérification du rendu

Les captures se font en navigateur réel, jamais sur la seule lecture du code :

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --hide-scrollbars --window-size=1440,900 --screenshot=home.png "http://localhost:4321/"
```

Deux pièges rencontrés, à ne pas réintroduire :

- Chrome headless impose sous Windows une largeur de fenêtre minimale
  (~500 px). Une capture demandée à 390 px est **rognée**, pas rétrécie : le
  rendu mobile se vérifie en plaçant la page dans une `iframe` de la largeur
  voulue.
- Chrome met `styles.css` en cache entre deux exécutions : utiliser un
  `--user-data-dir` neuf, ou une URL avec paramètre variable, après chaque
  modification.

## Ce qui reste à faire

**Quatre pages sans texte.** Les documents récupérés de l’ancien site sont
vides pour `historien/antiquite-tardive`, `saint-augustin`, `education-culture`
et `le-professeur`. Les pages existent, sont accessibles, et affichent une
mention explicite ; leurs cartes portent l’étiquette « Contenu à venir ». Il
faut rédiger ces textes ou retrouver les originaux.

**Les visuels.** L’ex-libris et le portrait sont extraits de la maquette de
référence (1536 × 1024), faute d’originaux. Les remplacer aux mêmes chemins
suffira, le CSS n’aura pas à changer.

**Ensuite.** Les fichiers des Cahiers Marrou en consultation libre · les
exports BibTeX/RIS · l’administration protégée (Arnaud Zemmour, Fabien
Guilloux) · une feuille de style d’impression · les versions anglaise,
italienne et espagnole.
