# Mettre en place l’administration du site

Le site est prêt. Restent cinq étapes que **vous** devez faire : elles passent
par vos comptes, je ne peux pas les exécuter à votre place.

Comptez une heure la première fois. Ensuite, plus rien à faire.

> **Vous n’avez jamais utilisé GitHub ?** Ce document est un résumé, utile
> pour s’y retrouver ensuite. Pour la mise en place elle-même, suivez plutôt
> [TUTORIEL_GITHUB.md](TUTORIEL_GITHUB.md), qui décrit chaque écran et chaque
> bouton, sans rien supposer.

---

## Étape 1 — Créer le dépôt

1. Créer un compte sur [github.com](https://github.com) si vous n’en avez pas.
   Gratuit, aucune carte bancaire.
2. Créer un dépôt **public**, par exemple `site-marrou`. Avec l’offre
   gratuite, GitHub Pages ne publie que depuis un dépôt public ; un dépôt
   privé demanderait l’abonnement Pro, hors budget. Ce qui doit rester
   confidentiel est déjà exclu par le `.gitignore`.
3. Depuis ce dossier, envoyer le projet (le dépôt local existe déjà) :

```bash
git remote add origin https://github.com/VOTRE-COMPTE/site-marrou.git
git push -u origin main
```

Le dossier `site/` n’est volontairement pas envoyé : il est reconstruit
automatiquement à chaque publication.

## Étape 2 — Activer la publication

Dans le dépôt, **Settings → Pages → Source : GitHub Actions**.

L’envoi de l’étape 1 ayant eu lieu avant, relancer une fois le robot à la
main : onglet **Actions → Construire et publier → Run workflow**. Ensuite le
site se construit et se publie seul.
L’adresse sera `https://VOTRE-COMPTE.github.io/site-marrou/`, en attendant le
vrai nom de domaine.

> **Nom de domaine.** Une fois acheté (une douzaine d’euros par an), l’ajouter
> dans **Settings → Pages → Custom domain**, et mettre à jour `url` dans
> l’écran « Informations générales » de l’administration.

## Étape 3 — Le relais d’authentification

L’interface d’administration doit pouvoir vérifier votre identité GitHub. Cela
demande un tout petit service intermédiaire, gratuit et à installer une fois.

1. Créer un compte sur [Cloudflare](https://dash.cloudflare.com) (gratuit).
2. Suivre les instructions de
   [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) : bouton
   *Deploy to Cloudflare Workers*, puis création d’une « OAuth App » côté
   GitHub dont l’*Authorization callback URL* est l’adresse du relais suivie
   de `/callback`.
3. Déclarer chez Cloudflare les variables `GITHUB_CLIENT_ID`,
   `GITHUB_CLIENT_SECRET` (en *Secret*) et `ALLOWED_DOMAINS`.
4. Reporter l’adresse obtenue (`https://…workers.dev`) dans
   `statique/admin/config.yml`, champ `base_url`.

> Ces services évoluent : si les écrans ne correspondent plus exactement à la
> documentation, fiez-vous à celle du dépôt sveltia-cms-auth, qui fait foi.

## Étape 4 — Compléter la configuration

Dans `statique/admin/config.yml`, remplacer :

```yaml
repo: VOTRE-COMPTE/VOTRE-DEPOT     # → VOTRE-COMPTE/site-marrou
base_url: https://VOTRE-RELAIS.workers.dev   # → l'adresse de l'étape 3
```

Puis renvoyer :

```bash
git add statique/admin/config.yml && git commit -m "Configuration de l'administration" && git push
```

## Étape 5 — Donner les accès

Dans le dépôt, **Settings → Collaborators → Add people**.

| Rôle à donner | Pour qui | Ce que ça permet |
| --- | --- | --- |
| **Write** | Administrateurs (Arnaud Zemmour, Fabien Guilloux) | Publier directement |
| **Triage** | Membres contributeurs | Proposer, sans publier |

**C’est ici que se gèrent les administrateurs.** Ajouter ou retirer quelqu’un
prend dix secondes et ne demande aucune intervention technique.

---

# Utiliser l’administration au quotidien

Aller sur `https://…/admin/`, se connecter avec GitHub.

**Modifier une page** — cliquer sur la page, corriger, **Publier**. En ligne
au bout d’une minute environ.

**Ajouter une page** — « Pages » → *Nouveau*. Renseigner le titre, choisir la
rubrique, écrire. La page apparaît automatiquement dans sa rubrique, dans le
rail de navigation, dans les liens précédent/suivant et dans la recherche.

**Ajouter une image ou un PDF** — bouton d’insertion dans l’éditeur. Les
fichiers atterrissent dans `statique/assets/images/`.

**Relire une proposition** — onglet *Workflow* : les contributions en attente,
à accepter ou refuser.

**Revenir en arrière** — chaque modification est datée et signée dans
l’historique GitHub. Rien n’est jamais perdu.

---

## Les trois niveaux, en pratique

| | Comment | Ce que la personne peut faire |
| --- | --- | --- |
| **Lecteur** | Rien à faire | Tout lire. Aucun compte, aucune trace |
| **Membre** | *Sans compte* : bouton « Proposer une correction » en bas de chaque page, qui ouvre un courriel prérempli.<br>*Avec compte* (accès Triage) : édite dans l’interface, mais son bouton est « Soumettre à relecture » | Proposer, jamais publier |
| **Admin** | Accès Write | Tout modifier, publier, arbitrer les propositions, gérer les accès |

**Une précision honnête sur le niveau membre avec compte :** la barrière est
ergonomique, pas étanche. L’interface conduit vers la relecture, mais
quelqu’un de familier de GitHub pourrait contourner. Pour un conseil
d’administration de personnes de confiance, c’est sans conséquence.

Le bouton « Proposer une correction » sans compte est plus rustique — il ouvre
le logiciel de courrier — mais il ne demande aucune inscription. C’est la voie
à privilégier pour les contributeurs occasionnels. Il pourra être remplacé par
un vrai formulaire plus tard, sans rien changer d’autre au site.

---

## Ce que ça coûte

| Poste | Coût |
| --- | --- |
| Hébergement (GitHub Pages) | 0 € |
| Relais d’authentification (Cloudflare Workers) | 0 € |
| Interface d’administration | 0 € (logiciel libre) |
| Nom de domaine | environ 12 €/an |

**Total : une douzaine d’euros par an**, sous le budget fixé.

Les offres gratuites de ces services évoluent : à revérifier au moment de la
mise en place.

---

## Adhésions, cotisations, dons

Ne pas les coder. **HelloAsso** est gratuit pour les associations loi 1901 et
gère adhésions, paiements, reçus et inscriptions aux événements. Il suffit
d’ajouter un lien depuis le site. C’est plus sûr, plus complet et plus simple
que tout ce qu’on pourrait développer ici.

---

## Si GitHub est un obstacle

C’est le seul vrai point de friction : chaque personne qui édite doit créer un
compte GitHub gratuit. Trois minutes, une fois — mais c’est un mot inconnu
pour beaucoup, et il faut accompagner.

Si cela devait bloquer, la solution de repli est un CMS hébergé avec ses
propres identifiants (Sanity, Contentful…). On échangerait alors la maîtrise
de ses fichiers contre la simplicité d’accès. Le contenu resterait exportable :
rien de ce qui a été fait ici ne serait perdu.
