# Scripts de migration — usage unique, conservés pour mémoire

Ces trois scripts ont servi une seule fois et **n'ont plus à être relancés**.
Ils documentent d'où vient le contenu du site.

| Script | Ce qu'il a fait |
| --- | --- |
| `extraire_docx.py` | Converti les `.docx` récupérés de l'ancien site en fragments HTML |
| `pages.py` | Ancien manifeste des pages, avant le passage à un fichier par page |
| `migrer_vers_markdown.py` | Fusionné manifeste + fragments en `contenu/**/*.md` |

La source de vérité est désormais `contenu/`.
