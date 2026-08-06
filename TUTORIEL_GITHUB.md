# Mettre le site en ligne — tutoriel pas à pas

Ce document s’adresse à quelqu’un qui **n’a jamais utilisé GitHub**. Il ne
suppose rien : chaque écran, chaque bouton est décrit. Suivez-le dans l’ordre,
sans sauter d’étape.

Comptez **une heure et demie** la première fois, en une seule fois de
préférence. Ensuite, plus jamais : la mise à jour du site se fera depuis une
page web, sans rien de tout ceci.

> **Si un écran ne ressemble pas à ce qui est décrit**, c’est que le service a
> changé son interface depuis la rédaction. Le principe reste le même :
> cherchez le libellé le plus proche. Les noms exacts qui comptent vraiment
> sont signalés en gras.

---

## Ce que vous allez construire

Trois choses, chacune gratuite :

| | À quoi ça sert | Analogie |
| --- | --- | --- |
| **GitHub** | Range les textes du site et fabrique les pages | L’imprimerie et son archive |
| **GitHub Pages** | Diffuse les pages sur Internet | Le kiosque |
| **Un « relais » Cloudflare** | Vérifie que celui qui veut modifier le site en a le droit | Le portier |

À la fin, les administrateurs iront sur une adresse du type
`https://…/admin/`, se connecteront, corrigeront un texte, cliqueront sur
**Publier** — et le site sera à jour une minute plus tard.

## Le vocabulaire, une fois pour toutes

Cinq mots reviendront. Ils n’ont rien de compliqué.

- **Dépôt** (*repository*, ou *repo*) — le dossier du projet, hébergé chez
  GitHub. Le nôtre contiendra les textes, les images et le programme qui
  fabrique les pages.
- **Envoyer / pousser** (*push*) — copier vers GitHub ce qui est sur votre
  ordinateur.
- **Commit** — une modification enregistrée, datée et signée. L’historique du
  site en est la suite. **Rien n’est jamais perdu** : on peut toujours revenir
  à un état antérieur.
- **Actions** — le robot de GitHub. Chez nous, il refabrique le site à chaque
  modification et le remet en ligne.
- **OAuth** — le mécanisme qui permet de dire « connectez-moi avec mon compte
  GitHub » sans donner son mot de passe à un autre site.

## Avant de commencer

Munissez-vous de :

- une **adresse électronique** à laquelle vous avez accès tout de suite ;
- un **téléphone** (GitHub demande une double authentification) ;
- de quoi noter deux ou trois codes provisoirement — un bloc-notes fait
  l’affaire, mais **ne les enregistrez pas dans le dossier du projet**.

> ### Point de sécurité, à lire
>
> Le dossier `SAHIM_Site Internet_Récupération/` contient un document où
> figurent des identifiants **en clair**. Il est volontairement exclu de tout
> envoi (fichier `.gitignore`), et doit le rester.
>
> Le mot de passe de `himarroudavenson@gmail.com` a circulé dans ce document :
> **considérez-le comme compromis et changez-le**, indépendamment de tout ce
> qui suit.

---

# Étape 1 — Créer votre compte GitHub

*Environ 10 minutes.*

1. Allez sur **[github.com](https://github.com)** et cliquez sur **Sign up**
   (en haut à droite).
2. Saisissez votre adresse électronique, puis un mot de passe, puis un nom
   d’utilisateur. Ce nom sera visible : `sahim`, `amis-marrou`, votre nom…
   Il apparaîtra dans l’adresse provisoire du site, choisissez-le sobre.
3. GitHub envoie un **code à huit chiffres** par courriel. Recopiez-le.
4. GitHub pose quelques questions sur votre usage : répondez ce que vous
   voulez, cela n’a aucune conséquence. À la fin, choisissez l’offre
   **Free**.
5. **Activez la double authentification** quand GitHub le propose (il
   l’exigera de toute façon sous trente jours). Le plus simple : « Set up
   using an app », puis installez *Google Authenticator* ou *Microsoft
   Authenticator* sur votre téléphone et scannez le carré noir et blanc.
   **Notez les codes de secours** que GitHub affiche ensuite, et gardez-les
   ailleurs que dans le projet.

✅ **Vous devez pouvoir** vous déconnecter, vous reconnecter, et voir votre nom
en haut à droite.

---

# Étape 2 — Créer le dépôt

*Environ 5 minutes.*

1. En haut à droite, cliquez sur le **+** puis **New repository**.
2. Remplissez :
   - **Repository name** : `site-marrou`
   - **Description** : *Site de la Société des amis d’Henri Irénée Marrou*
   - **Public** ← important, voir l’encadré
   - Ne cochez **rien** d’autre : ni *Add a README*, ni *.gitignore*, ni
     *license*. Le projet apporte déjà les siens, et les cocher créerait un
     conflit à l’envoi.
3. **Create repository**.

GitHub affiche alors une page d’instructions. Ignorez-la, la suite est
ci-dessous.

> ### Pourquoi public ?
>
> Avec l’offre gratuite, **GitHub Pages ne publie que depuis un dépôt public**.
> Un dépôt privé exigerait l’abonnement Pro, soit environ 45 €/an — au-delà du
> budget fixé.
>
> Ce n’est pas gênant : le contenu du site est fait pour être lu. Ce qui doit
> rester privé (le dossier de récupération, les identifiants) est déjà exclu
> par le fichier `.gitignore`, et le restera.

## Envoyer le projet

Sur votre ordinateur, ouvrez un terminal **dans le dossier du projet** et
lancez ces deux commandes, en remplaçant `VOTRE-COMPTE` par votre nom
d’utilisateur GitHub.

```bash
git remote add origin https://github.com/VOTRE-COMPTE/site-marrou.git
```

```bash
git push -u origin main
```

Une fenêtre de navigateur s’ouvre et demande d’autoriser *Git Credential
Manager* à accéder à votre compte : acceptez. C’est la seule fois.

Rechargez la page du dépôt sur GitHub : vos fichiers y sont.

> Le dossier `site/` n’apparaît pas, et c’est normal — il est refabriqué à
> chaque publication. Le dossier `SAHIM_Site Internet_Récupération/` non plus,
> et c’est voulu.

✅ **Vous devez voir** les dossiers `build`, `contenu`, `statique` sur la page
du dépôt.

---

# Étape 3 — Activer la publication

*Environ 3 minutes, puis 2 minutes d’attente.*

1. Dans le dépôt, onglet **Settings** (la roue dentée, en haut à droite de la
   barre d’onglets — pas le Settings de votre compte).
2. Colonne de gauche, rubrique **Pages**.
3. Sous **Build and deployment**, champ **Source** : choisissez
   **GitHub Actions** (et non « Deploy from a branch »).

Rien d’autre à valider, le choix est enregistré aussitôt.

## Lancer la première publication

L’envoi de l’étape 2 a eu lieu avant que Pages ne soit activé : il faut
relancer le robot une fois à la main.

1. Onglet **Actions**.
2. Colonne de gauche, cliquez sur **Construire et publier**.
3. Bouton **Run workflow** à droite, puis **Run workflow** dans le petit
   menu qui s’ouvre.
4. Attendez : une pastille jaune tourne, puis devient **verte**. Comptez une à
   deux minutes.

Votre site est en ligne à l’adresse :

```
https://VOTRE-COMPTE.github.io/site-marrou/
```

✅ **Ouvrez-la.** Vous devez voir la page d’accueil, avec l’ex-libris et le
portrait.

> ### Si la pastille est rouge
>
> Cliquez dessus : GitHub affiche le journal, et la ligne en rouge dit ce qui
> ne va pas. Les deux causes courantes :
> - *« Get Pages site failed »* → l’étape 3.3 n’a pas été faite ou pas
>   enregistrée ;
> - une erreur dans `verifier.py` → un lien cassé dans le contenu. Le message
>   nomme la page et le lien fautif.

## Le nom de domaine, plus tard

L’adresse en `github.io` est provisoire et fonctionne parfaitement. Quand
l’association aura acheté `henrimarrou.org` (une douzaine d’euros par an) :

1. **Settings → Pages → Custom domain** : saisir le nom, **Save** ;
2. chez le vendeur du domaine, créer les enregistrements DNS que GitHub
   indique alors à l’écran ;
3. cocher **Enforce HTTPS** une fois le certificat délivré (quelques heures) ;
4. dans l’administration du site, écran **Réglages → Informations générales**,
   corriger le champ **Adresse du site**.

---

# Étape 4 — Le relais d’authentification

*Environ 25 minutes. C’est l’étape la plus longue, et la seule un peu ingrate.*

## Pourquoi cette étape

L’interface d’administration est une page web sans serveur. Pour vous
connecter à GitHub, elle a besoin d’un intermédiaire minuscule qui détient un
secret — un secret qu’on ne peut pas laisser dans une page web publique. Ce
sera un **Worker Cloudflare** : gratuit, et vous n’y toucherez plus jamais.

Trois sous-étapes, dans cet ordre : **installer le relais**, **le déclarer à
GitHub**, **relier les deux**.

## 4a — Installer le relais

1. Créez un compte sur **[dash.cloudflare.com](https://dash.cloudflare.com)**
   (gratuit ; aucune carte bancaire pour l’offre Workers Free). Validez
   l’adresse électronique.
2. Allez sur **[github.com/sveltia/sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth)**.
3. Dans le fichier de présentation (le *README*, affiché sous la liste des
   fichiers), cliquez sur le bouton **Deploy to Cloudflare Workers**.
4. Cloudflare demande d’autoriser l’accès à votre compte GitHub : acceptez.
5. Laissez les valeurs proposées et lancez le déploiement.

Au bout d’une minute, Cloudflare affiche l’adresse du relais. Elle ressemble à :

```
https://sveltia-cms-auth.quelquechose.workers.dev
```

**Copiez-la dans votre bloc-notes.** Elle servira deux fois.

> Si vous ne retrouvez pas l’adresse : tableau de bord Cloudflare →
> **Workers & Pages** → cliquez sur `sveltia-cms-auth`. Elle est affichée en
> haut de la page.

## 4b — Déclarer le relais à GitHub

1. Sur GitHub, allez sur
   **[github.com/settings/developers](https://github.com/settings/developers)**
   (c’est le Settings de votre **compte**, pas celui du dépôt).
2. **OAuth Apps** → **New OAuth App**.
3. Remplissez :

   | Champ | Valeur |
   | --- | --- |
   | **Application name** | `Administration site Marrou` |
   | **Homepage URL** | l’adresse de votre site (celle en `github.io` pour l’instant) |
   | **Authorization callback URL** | l’adresse du relais **suivie de** `/callback` |

   Le troisième champ est le seul qui doit être exact au caractère près :

   ```
   https://sveltia-cms-auth.quelquechose.workers.dev/callback
   ```

4. **Register application**.
5. GitHub affiche un **Client ID**. Copiez-le.
6. Cliquez sur **Generate a new client secret**. GitHub affiche un long code :
   **c’est la seule fois où il est visible**. Copiez-le immédiatement.

⚠️ Ces deux codes sont des clés. Ne les mettez dans aucun fichier du projet,
ne les envoyez par courriel à personne. Ils vont être collés directement chez
Cloudflare à l’étape suivante, après quoi vous pourrez les effacer de votre
bloc-notes.

## 4c — Relier les deux

1. Retournez sur Cloudflare, **Workers & Pages** → `sveltia-cms-auth`.
2. Onglet **Settings**, rubrique **Variables and Secrets** (ou *Variables
   d’environnement* selon la langue).
3. Ajoutez trois entrées. Les noms doivent être **exactement** ceux-ci, en
   majuscules :

   | Nom | Valeur | Type |
   | --- | --- | --- |
   | `GITHUB_CLIENT_ID` | le Client ID de l’étape 4b | Texte |
   | `GITHUB_CLIENT_SECRET` | le secret de l’étape 4b | **Secret** (chiffré) |
   | `ALLOWED_DOMAINS` | `VOTRE-COMPTE.github.io` | Texte |

   Pour `GITHUB_CLIENT_SECRET`, choisissez bien le type **Secret** : la valeur
   devient illisible même pour vous, ce qui est le comportement voulu.

   `ALLOWED_DOMAINS` limite l’usage du relais à votre seul site. Quand le vrai
   nom de domaine sera en place, revenez y ajouter `,www.henrimarrou.org`.

4. **Save** puis **Deploy** si Cloudflare le demande.

✅ **Vous devez avoir**, dans votre bloc-notes, l’adresse du relais. Les deux
codes GitHub peuvent maintenant être effacés.

---

# Étape 5 — Compléter la configuration

*Environ 5 minutes.*

Deux valeurs restent à écrire dans le projet. On peut le faire directement sur
GitHub, sans terminal.

1. Dans le dépôt, ouvrez `statique` → `admin` → `config.yml`.
2. Cliquez sur le **crayon** (*Edit this file*), en haut à droite du fichier.
3. Repérez ces deux lignes :

   ```yaml
     repo: VOTRE-COMPTE/VOTRE-DEPOT
     base_url: https://VOTRE-RELAIS.workers.dev
   ```

   et remplacez-les par, par exemple :

   ```yaml
     repo: sahim/site-marrou
     base_url: https://sveltia-cms-auth.quelquechose.workers.dev
   ```

   Attention à ne pas toucher aux espaces en début de ligne : dans ce format,
   l’indentation a un sens.

4. En bas, bouton vert **Commit changes**. Laissez « Commit directly to the
   `main` branch ». **Commit changes** à nouveau.

Le robot repart tout seul. Une minute plus tard, l’interface est active.

✅ **Vérification** : ouvrez `https://VOTRE-COMPTE.github.io/site-marrou/admin/`.
Un bouton **Sign in with GitHub** doit s’afficher. Cliquez : GitHub demande
d’autoriser l’application, acceptez — et l’interface s’ouvre sur la liste des
pages du site.

> ### Si ça ne marche pas
>
> | Symptôme | Cause presque certaine |
> | --- | --- |
> | Page blanche | `repo:` mal orthographié, ou indentation cassée dans `config.yml` |
> | « Redirect URI mismatch » | Le *callback URL* de l’étape 4b ne se termine pas par `/callback`, ou comporte une faute |
> | « Not allowed » / « Forbidden » | `ALLOWED_DOMAINS` ne correspond pas au domaine depuis lequel vous ouvrez la page |
> | Connexion qui tourne sans fin | `GITHUB_CLIENT_SECRET` mal recopié — régénérez-en un et remettez-le |

---

# Étape 6 — Donner les accès

*Environ 5 minutes.*

1. Dépôt → **Settings** → colonne de gauche, **Collaborators**.
2. **Add people**, saisissez le nom d’utilisateur GitHub de la personne (elle
   doit avoir créé son compte au préalable — étape 1, en trois minutes).
3. Choisissez son rôle :

   | Rôle | Pour qui | Ce que ça permet |
   | --- | --- | --- |
   | **Write** | Administrateurs | Modifier et publier directement |
   | **Triage** | Membres contributeurs | Proposer une modification, sans publier |

4. La personne reçoit une invitation par courriel, qu’elle doit accepter.

**C’est ici, et uniquement ici, que se gèrent les administrateurs.** Ajouter ou
retirer quelqu’un prend dix secondes et ne demande aucune intervention
technique.

---

# C’est fini. Le quotidien, maintenant

Plus jamais de terminal ni de configuration. Tout se passe sur une page.

## Corriger un texte

1. Aller sur `https://…/admin/`, **Sign in with GitHub**.
2. **Pages** dans la colonne de gauche, cliquer sur la page.
3. Corriger dans l’éditeur. La colonne de droite montre le rendu.
4. **Publier** (ou **Soumettre à relecture**, pour un membre).
5. Une minute plus tard, c’est en ligne. Rechargez la page publique pour voir.

## Ajouter une page

**Pages → Nouveau**. Renseignez le titre, choisissez la rubrique, écrivez.
La page apparaît d’elle-même dans sa rubrique, dans le rail de navigation,
dans les liens précédent/suivant et dans la recherche du site : il n’y a
aucune liste à tenir à jour.

## Ajouter une image ou un PDF

Bouton d’insertion dans l’éditeur. Les fichiers sont rangés dans
`statique/assets/images/`.

## Relire une proposition

Onglet **Workflow** : les contributions en attente, à accepter ou refuser.

## Revenir en arrière

Chaque modification est datée et signée dans l’historique GitHub (onglet
**Commits** du dépôt). On peut toujours retrouver et rétablir un état
antérieur. **Rien n’est jamais perdu** — c’est la principale raison d’avoir
choisi GitHub plutôt qu’un éditeur en ligne classique.

---

# Aide-mémoire

| Où | Adresse |
| --- | --- |
| Le site | `https://VOTRE-COMPTE.github.io/site-marrou/` |
| L’administration | `https://VOTRE-COMPTE.github.io/site-marrou/admin/` |
| Le dépôt | `https://github.com/VOTRE-COMPTE/site-marrou` |
| Les publications en cours | onglet **Actions** du dépôt |
| Les accès | **Settings → Collaborators** |
| Le relais | tableau de bord Cloudflare → **Workers & Pages** |

## Ce que ça coûte

| Poste | Coût |
| --- | --- |
| GitHub Free + Pages (dépôt public) | 0 € |
| Cloudflare Workers (offre gratuite) | 0 € |
| Interface d’administration (logiciel libre) | 0 € |
| Nom de domaine | environ 12 €/an |

**Total : une douzaine d’euros par an.**

Les offres gratuites de ces services évoluent : à revérifier au moment de la
mise en place.

## Les questions qu’on se pose

**Faut-il que tout le monde ait un compte GitHub ?** Non — seulement les
personnes qui modifient le site. Les lecteurs n’ont rien à faire, et le bouton
« Proposer une correction » en bas de chaque page fonctionne sans aucun compte
(il ouvre un courriel prérempli).

**Que se passe-t-il si je fais une bêtise dans l’éditeur ?** Rien
d’irréversible. La modification est enregistrée comme une nouvelle version ;
l’ancienne reste consultable et rétablissable.

**Et si GitHub ferme, ou change ses conditions ?** Tout le contenu du site
est dans des fichiers texte ordinaires, lisibles sans aucun logiciel
particulier. On peut les emporter ailleurs en les copiant.

**Puis-je travailler à plusieurs en même temps ?** Oui, tant que ce n’est pas
sur la même page au même moment. Si deux personnes modifient la même page,
GitHub signale le conflit au lieu d’écraser silencieusement l’un des deux.
