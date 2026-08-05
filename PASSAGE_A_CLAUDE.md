# Passage de relais — Site Henri-Irénée Marrou

## 1. Finalité du projet

Créer le nouveau site officiel de la **Société des amis d’Henri Irénée Marrou**, association déclarée sous le régime de la loi de 1901.

Objectif principal : **faire rayonner l’œuvre d’Henri-Irénée Marrou auprès du grand public**, tout en proposant des ressources suffisamment solides pour les historiens, chercheurs, étudiants et lecteurs déjà familiers de son travail.

Le site doit présenter Marrou à la fois comme :

- historien de l’Antiquité tardive et du christianisme ancien ;
- théoricien de l’histoire et de la connaissance historique ;
- intellectuel, chrétien et citoyen engagé ;
- musicologue et auteur sous le nom d’Henri Davenson ;
- personnalité dont l’œuvre reste actuelle.

La dimension chrétienne doit former un **fil transversal**, sans être isolée dans une rubrique fermée.

## 2. Public et tonalité

Le public prioritaire est le **grand public**.

Le site doit donc être :

- clair et accueillant sans devenir simpliste ;
- élégant, sobre et digne d’un historien important ;
- éditorial plutôt qu’institutionnel ou universitaire froid ;
- facile à parcourir sur ordinateur, tablette et téléphone ;
- accessible au zoom du navigateur, sans texte masqué ni composants superposés.

## 3. Direction visuelle validée

La direction retenue est la maquette A, dite « revue savante » :

- fond ivoire ;
- bordeaux profond ;
- touches de mauve clair ;
- grands titres avec une police à empattements ;
- photographie noir et blanc de Marrou ;
- ex-libris de Marrou utilisé comme logo ;
- mise en page évoquant une revue intellectuelle ou un ouvrage imprimé.

Maquette validée :

`C:\Users\david\AppData\Local\Temp\codex-clipboard-ada1ca0a-b4e5-49be-955f-f3066576c65a.png`

Attention : cette image est une **maquette de référence**, pas une source d’assets définitifs. Il faut récupérer ou préparer séparément le véritable ex-libris et la photographie originale, puis les intégrer comme fichiers image propres.

## 4. Principe de navigation souhaité

L’utilisateur ne souhaite pas une longue page d’accueil à faire défiler.

L’accueil doit fonctionner comme une **table des matières tenant sur un écran lorsque la taille de l’écran le permet** :

- identité de Marrou et portrait ;
- accès immédiat aux grandes rubriques ;
- courte citation ou zone éditoriale secondaire ;
- aucun contenu important masqué.

Lorsque l’écran est petit ou que le navigateur est fortement zoomé, il faut accepter un défilement normal plutôt que réduire excessivement les textes ou provoquer des chevauchements.

Chaque rubrique doit s’ouvrir comme une page ou un chapitre autonome. Le bouton de retour doit se trouver **à l’endroit attendu : en haut à gauche de la page intérieure**, sous l’en-tête ou dans une ligne de fil d’Ariane dédiée. Il doit rester discret, clairement visible et ne jamais flotter au-dessus d’un titre.

Rubriques actuellement envisagées :

1. Découvrir / Une vie dans le siècle
2. L’historien
3. Penser et agir
4. Le musicologue
5. Ressources
6. Cahiers Marrou
7. L’Association

Liens ou contenus transversaux prévus :

- chronologie ;
- recherche avancée ;
- « Marrou aujourd’hui ».

## 5. Contenus et arbitrages déjà validés

Les contenus de l’ancien site ont été récupérés en partie depuis Internet Archive et depuis des documents partagés.

Décisions prises :

- conserver les textes historiques récupérés ;
- ne pas les réécrire pour le moment ;
- garder visibles les informations anciennes, quitte à les corriger plus tard ;
- mettre d’abord en avant Marrou comme historien ;
- ajouter ultérieurement les contenus manquants ;
- les ayants droit indiquent disposer des droits nécessaires sur les textes et les images ;
- récupérer autant d’éléments que possible depuis Internet Archive ;
- rendre librement consultables tous les numéros disponibles des Cahiers Marrou ;
- prévoir ultérieurement des versions anglaise, italienne et espagnole.

Personnes appelées à valider ou administrer le contenu :

- Arnaud Zemmour ;
- Fabien Guilloux.

## 6. Fonctions attendues à terme

### Bibliographie avancée

- recherche plein texte ;
- filtres ;
- liens vers les ressources ;
- notices détaillées ;
- exports bibliographiques, notamment BibTeX et RIS.

### Vie de l’association

- actualités ;
- événements ;
- adhésion ;
- dons ;
- lettre d’information ;
- formulaire de contact.

### Administration

Prévoir une interface d’administration protégée pour Arnaud Zemmour et Fabien Guilloux.

Ne jamais conserver de mot de passe en clair dans le dépôt ou dans les contenus publiés. Un ancien document partagé contenait des identifiants en clair : ils doivent être considérés comme compromis, remplacés et supprimés des sources.

## 7. Contraintes d’hébergement

- aucun ancien nom de domaine n’est récupérable ;
- budget visé : **30 euros par an maximum**, sauf discussion ultérieure ;
- aucune date impérative de mise en ligne ;
- la solution devra rester simple à maintenir par l’association.

Une architecture statique avec un petit service externe ou une base légère pour les fonctions dynamiques peut être envisagée afin de respecter le budget. Ne rien déployer publiquement sans validation explicite du commanditaire.

## 8. État actuel des fichiers

Prototype local :

`C:\Users\david\Mon Drive\1 - PROJECTS\A - HENRI IRENEE MARROU\site\`

Le site n’est plus une page unique à ancres : c’est un ensemble de **28 vraies
pages HTML statiques**, produites par un générateur. Voir `site/README.md`.

```
build/pages.py       arborescence, titres, chapeaux — où l'on déclare une page
build/contenu/       corps des pages, un fragment HTML chacun
build/build.py       assemble et produit site/   (python build/build.py)
site/                ← à publier ; contenu généré, ne pas y corriger un texte
```

Chaque page a son titre, sa meta description, son URL canonique et ses balises
OpenGraph. Le seul prérequis est Python 3, sans dépendance.

## 9. Reprise du 4 août 2026 — état résolu

La reprise recommandée au §10 a été effectuée. Le prototype précédent est archivé dans
`_archive_prototype/` et peut être supprimé.

Ce qui a été fait :

- `fixes.css`, `assets/reference-image.css` et `assets/visuals.css` supprimés
  (5,5 Mo de maquette encodée en base64) ;
- `styles.css` entièrement réécrit : une seule feuille, ordonnée, sans `!important`,
  sans hauteur fixe, sans surcharge contradictoire — 20 Ko ;
- le logo et le portrait sont désormais deux vrais fichiers image, référencés par des
  balises `<img>` avec texte alternatif, et non plus des recadrages CSS ;
- le retour au sommaire est placé dans le flux normal, en haut à gauche des pages
  intérieures, sous l’en-tête ;
- l’en-tête est en `position: relative` : il ne peut plus recouvrir le contenu ;
- l’accueil tient sur un écran de bureau via une grille dont la rangée du héros ne
  descend jamais sous son contenu ; en dessous de 1024 × 736 px CSS ce mode est
  désactivé et la page défile normalement.

Deux pièges de méthode rencontrés pendant la vérification, notés dans `site/README.md` :
Chrome headless rogne les captures demandées sous ~500 px de large sous Windows, et il
met la feuille de style en cache entre deux exécutions. Les deux ont d’abord produit de
faux défauts.

## 10. Recommandation de reprise (appliquée)

La meilleure stratégie est de repartir proprement sur la structure existante, plutôt que d’empiler des surcharges :

1. sauvegarder les contenus HTML et le JavaScript utile ;
2. examiner le DOM réel et dresser la liste exacte des classes ;
3. supprimer les feuilles `fixes.css` et `assets/visuals.css` après avoir identifié ce qui mérite d’être conservé ;
4. nettoyer ou réécrire `styles.css` comme une feuille cohérente ;
5. extraire le logo et le portrait dans deux vrais fichiers image optimisés ;
6. reconstruire l’en-tête et l’accueil avec une grille responsive simple ;
7. placer le retour dans le flux normal des pages intérieures ;
8. tester à plusieurs largeurs et plusieurs niveaux de zoom ;
9. ne valider aucune étape sans ouvrir la page et réaliser une capture du rendu réel.

## 11. Critères de validation immédiats — vérifiés par capture

| Critère | État |
| --- | --- |
| Logo visible dans l’en-tête | ✅ |
| Portrait visible sur l’accueil | ✅ |
| Accueil tenant sur un écran de bureau | ✅ 1440 × 900 : hauteur exactement 900 px, aucun débordement |
| Aucun contenu masqué à 125 / 150 / 200 % | ✅ la page défile normalement, rien n’est rogné |
| Retour au sommaire en haut à gauche, hors superposition | ✅ sur les 7 pages intérieures |
| En-tête ne recouvrant ni ne déformant le contenu | ✅ |
| Rendu mobile lisible et défilant | ✅ 390 × 844, menu et loupe accessibles |
| Aucun débordement horizontal | ✅ de 390 px à 1920 px |

## 12. Reprise ergonomique du 4 août 2026

Cinq chantiers menés dans l’ordre demandé par le commanditaire.

**Vraies pages statiques.** 28 pages remplacent la page unique à ancres. Titre,
meta description, URL canonique et OpenGraph propres à chacune : les moteurs de
recherche les indexent séparément et un lien partagé affiche le bon titre. Un
générateur (`build/`) évite de dupliquer l’en-tête 28 fois.

**Contenus intégrés.** Les `.docx` récupérés ont été convertis en 20 pages de
troisième niveau. Les 17 liens `href="#"` inertes sont branchés ; il n’en reste
aucun. La typographie a été normalisée (guillemets français, apostrophes
courbes) et les italiques des titres d’ouvrages préservées.

**Orientation.** Rubrique courante signalée dans la barre de navigation
(`aria-current` + filet bordeaux) ; pied de chapitre précédent/suivant ; pied de
page avec coordonnées et plan du site ; liens transversaux de l’accueil
corrigés — aucun libellé ne promet plus une page inexistante, et les 100 %
d’ancres pointent vers une cible réelle.

**Accès clavier.** Menu mobile : fermeture par Échap, piège de focus, retour du
focus au bouton. La perte de focus au changement de rubrique disparaît d’elle-même
avec les vraies pages.

**Recherche.** Plein texte, entièrement côté navigateur, sans serveur : index de
98 Ko produit à la construction, chargé au premier usage. Insensible aux accents,
multi-mots, surlignage des termes, ouverture par `/`.

### Correction d’une évaluation antérieure

L’estimation « 16 cartes sur 16 ont leur contenu » avait été faite sur les seuls
noms de fichiers. À l’ouverture, **quatre documents sont vides** :
`antiquite-tardive`, `saint-augustin`, `education-culture` et `le-professeur`
(deux ne contiennent que le fil d’Ariane de l’ancien site). Les pages existent et
sont accessibles, avec une mention explicite, et leurs cartes portent l’étiquette
« Contenu à venir ». Ces quatre textes restent à rédiger ou à retrouver.

### Reste à faire

- remplacer l’ex-libris et le portrait, extraits de la maquette faute
  d’originaux, par les fichiers des ayants droit — aux mêmes chemins, le CSS
  n’aura pas à changer ;
- les quatre pages sans texte ci-dessus ;
- fichiers des Cahiers Marrou, exports BibTeX/RIS, administration protégée,
  feuille d’impression, versions anglaise, italienne et espagnole.

## 12. Important pour la collaboration

Le commanditaire souhaite une collaboration visuelle et itérative, mais avec contrôle qualité réel. Il ne faut pas annoncer qu’une correction est terminée sur la seule base du code. Toujours ouvrir le site, vérifier le rendu et fournir ou examiner une capture avant validation.
