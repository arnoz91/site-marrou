# -*- coding: utf-8 -*-
"""
Manifeste du site : l'arborescence, les titres et les textes d'accroche.

C'est le seul endroit où l'on déclare une page. `build.py` en déduit la
navigation, les fils d'Ariane, les cartes de rubrique, les liens
précédent/suivant et l'index de recherche.

Champs d'une page :
  slug        chemin du fichier produit, sans .html  (« historien/resistance »)
  titre       le <h1>
  nav         libellé court dans la barre de navigation (rubriques seulement)
  surtitre    petite capitale au-dessus du titre
  chapeau     phrase d'introduction, sous le titre
  resume      texte de la carte dans la rubrique parente
  description meta description ; à défaut, le chapeau est utilisé
  fragment    nom du fichier de build/contenu/ ; à défaut, le slug
  parent      slug de la rubrique parente
"""

SITE = {
    "nom": "Société des amis d’Henri Irénée Marrou",
    "titre_court": "Henri-Irénée Marrou",
    "url": "https://www.henrimarrou.org",
    "courriel": "contact@henrimarrou.org",
}

ACCUEIL = {
    "slug": "index",
    "titre": "Henri-Irénée Marrou",
    "sous_titre": "Historien, penseur, témoin",
    "dates": "1904—1977",
    "chapeau": "Henri Irénée Marrou est une des grandes personnalités "
               "d’historiens du XX<sup>e</sup> siècle.",
    "description": "Historien de l’Antiquité tardive, théoricien de l’histoire, "
                   "chrétien et citoyen engagé, musicologue sous le nom d’Henri "
                   "Davenson : découvrir la vie et l’œuvre d’Henri-Irénée Marrou.",
    "citation": "Il n’y a pas de défaite qui ne puisse être surmontée si on "
                "refuse de s’y résigner.",
    "citation_source": "Henri-Irénée Marrou, tract clandestin, 1941",
}

# --- Rubriques de premier niveau, dans l'ordre de la navigation --------------
RUBRIQUES = [
    {
        "slug": "decouvrir",
        "nav": "Découvrir",
        "titre": "Une vie dans le siècle",
        "surtitre": "Découvrir",
        "icone": "vie",
        "chapeau": "De Marseille à Rome, de Lyon à la Sorbonne, un itinéraire "
                   "intellectuel, spirituel et civique.",
        "resume": "Biographie, de l’enfance marseillaise à l’Institut de France",
        # Déjà porté par le bouton du héros : hors de la grille du sommaire,
        # qui reste ainsi à six cartes, soit deux rangées pleines de trois.
        "sommaire": False,
        "description": "Biographie d’Henri-Irénée Marrou (1904-1977) : l’enfance "
                       "marseillaise, l’École normale supérieure, Rome, Lyon et la "
                       "Résistance, la Sorbonne, l’Institut de France.",
    },
    {
        "slug": "historien",
        "nav": "L’historien",
        "titre": "L’historien",
        "surtitre": "Chapitre 01",
        "icone": "colonne",
        "chapeau": "Une œuvre fondatrice sur l’Antiquité tardive, le christianisme "
                   "ancien et l’éducation.",
        "resume": "Antiquité tardive, Église, éducation",
        "description": "L’œuvre d’historien d’Henri-Irénée Marrou : Antiquité "
                       "tardive, saint Augustin et les Pères de l’Église, "
                       "archéologie chrétienne, histoire de l’éducation.",
    },
    {
        "slug": "penser-agir",
        "nav": "Penser et agir",
        "titre": "Penser et agir",
        "surtitre": "Chapitre 02",
        "icone": "livre",
        "chapeau": "L’histoire comme connaissance humaine ; l’engagement comme "
                   "exigence de vérité et de dignité.",
        "resume": "Méthode, foi, engagements",
        "description": "Henri-Irénée Marrou théoricien de l’histoire et citoyen "
                       "engagé : méthode historique, théologie de l’histoire, "
                       "Résistance, critique des totalitarismes, guerre d’Algérie.",
    },
    {
        "slug": "musicologue",
        "nav": "Le musicologue",
        "titre": "Henri Davenson, musicologue",
        "surtitre": "Chapitre 03",
        "icone": "lyre",
        "chapeau": "Une autre signature pour penser l’écoute, la tradition et les "
                   "formes populaires.",
        "resume": "Henri Davenson et la musique",
        "description": "Sous le nom d’Henri Davenson, Marrou musicologue : le "
                       "Traité de la musique selon l’esprit de saint Augustin, "
                       "Le Livre des chansons, la critique musicale.",
    },
    {
        "slug": "ressources",
        "nav": "Ressources",
        "titre": "Œuvres et ressources",
        "surtitre": "Chapitre 04",
        "icone": "loupe",
        "chapeau": "Livres, articles, revues, archives et références réunis et "
                   "librement consultables.",
        "resume": "Œuvres, bibliographie, archives",
        "description": "Les livres d’Henri-Irénée Marrou, ses bibliographies "
                       "érudites et non érudites, les revues et ouvrages "
                       "collectifs auxquels il a contribué.",
    },
    {
        "slug": "cahiers",
        "nav": "Cahiers Marrou",
        "titre": "Les Cahiers Marrou",
        "surtitre": "Chapitre 05",
        "icone": "cahier",
        "chapeau": "La revue annuelle de la Société des amis, librement "
                   "consultable.",
        "resume": "Lire librement tous les numéros",
        "description": "Les Cahiers Marrou, revue annuelle de la Société des amis "
                       "d’Henri Irénée Marrou : numéros et hors-séries en libre "
                       "consultation.",
    },
    {
        "slug": "association",
        "nav": "L’Association",
        "titre": "La Société des amis",
        "surtitre": "Chapitre 06",
        "icone": "personnes",
        "chapeau": "Faire rayonner l’œuvre d’Henri-Irénée Marrou et favoriser "
                   "l’étude de ses écrits.",
        "resume": "Actualités, adhésion, contact",
        "description": "La Société des amis d’Henri Irénée Marrou (Davenson), "
                       "association loi 1901 créée en 2007 : but, conseil "
                       "d’administration, adhésion et contact.",
    },
]

# --- Pages de second niveau -------------------------------------------------
PAGES = [
    # L'historien ------------------------------------------------------------
    {
        "slug": "historien/antiquite-tardive", "parent": "historien",
        "titre": "L’Antiquité tardive",
        "chapeau": "Une période historique réhabilitée, et nommée.",
        "resume": "Une période historique réhabilitée et nommée.",
    },
    {
        "slug": "historien/saint-augustin", "parent": "historien",
        "titre": "Saint Augustin et les Pères de l’Église",
        "chapeau": "Le christianisme des III<sup>e</sup>—VI<sup>e</sup> siècles.",
        "resume": "Le christianisme des III<sup>e</sup>—VI<sup>e</sup> siècles.",
    },
    {
        "slug": "historien/archeologie-prosopographie", "parent": "historien",
        "titre": "Archéologie et prosopographie",
        "chapeau": "Inscriptions chrétiennes de la Gaule et prosopographie du "
                   "Bas-Empire : deux grandes entreprises collectives.",
        "resume": "Inscriptions chrétiennes et grandes entreprises collectives.",
    },
    {
        "slug": "historien/education-culture", "parent": "historien",
        "titre": "Éducation et culture",
        "chapeau": "Une histoire de la transmission et de l’accomplissement humain.",
        "resume": "Une histoire de la transmission et de l’accomplissement humain.",
    },
    {
        "slug": "historien/le-professeur", "parent": "historien",
        "titre": "Le professeur",
        "chapeau": "De Lyon à la Sorbonne.",
        "resume": "De Lyon à la Sorbonne.",
        "description": "Henri-Irénée Marrou professeur : l’enseignement à Lyon "
                       "pendant la guerre, puis la chaire d’histoire du "
                       "christianisme ancien à la Sorbonne.",
    },
    {
        "slug": "historien/directeur-de-recherches", "parent": "historien",
        "titre": "Le directeur de recherches",
        "chapeau": "Séminaires, disciples et Centre Lenain de Tillemont.",
        "resume": "Séminaires, disciples et Centre Lenain de Tillemont.",
    },
    {
        "slug": "historien/troubadours", "parent": "historien",
        "titre": "Les troubadours et l’amour courtois",
        "chapeau": "Une incursion médiévale, hors de l’Antiquité tardive.",
        "resume": "Une incursion médiévale, hors de l’Antiquité tardive.",
    },

    # Penser et agir ---------------------------------------------------------
    {
        "slug": "penser-agir/methode-historique", "parent": "penser-agir",
        "titre": "La méthode historique",
        "chapeau": "<cite>De la connaissance historique</cite> et la critique du "
                   "positivisme.",
        "resume": "<cite>De la connaissance historique</cite> et la critique du "
                  "positivisme.",
    },
    {
        "slug": "penser-agir/theologie-de-l-histoire", "parent": "penser-agir",
        "titre": "Une théologie de l’histoire",
        "chapeau": "Le sens de l’histoire entre foi chrétienne et prudence "
                   "historienne.",
        "resume": "Le sens de l’histoire entre foi chrétienne et prudence "
                  "historienne.",
    },
    {
        "slug": "penser-agir/resistance", "parent": "penser-agir",
        "titre": "La Résistance",
        "chapeau": "Résistance spirituelle, sauvetage et presse clandestine.",
        "resume": "Résistance spirituelle, sauvetage et presse clandestine.",
    },
    {
        "slug": "penser-agir/contre-les-totalitarismes", "parent": "penser-agir",
        "titre": "Contre les totalitarismes",
        "chapeau": "Du fascisme italien à la critique du marxisme.",
        "resume": "Du fascisme italien à la critique du marxisme.",
    },
    {
        "slug": "penser-agir/honneur-de-la-france", "parent": "penser-agir",
        "titre": "Pour l’honneur de la France",
        "chapeau": "La dénonciation de la torture pendant la guerre d’Algérie.",
        "resume": "La dénonciation de la torture pendant la guerre d’Algérie.",
    },
    {
        "slug": "penser-agir/syndicalisme", "parent": "penser-agir",
        "titre": "Le syndicalisme",
        "chapeau": "Le SGEN, l’éducation et la liberté d’enseignement.",
        "resume": "Le SGEN, l’éducation et la liberté d’enseignement.",
    },

    # Le musicologue ---------------------------------------------------------
    {
        "slug": "musicologue/traite-de-la-musique", "parent": "musicologue",
        "titre": "Le Traité de la musique",
        "chapeau": "Une phénoménologie et une morale musicale selon l’esprit de "
                   "saint Augustin.",
        "resume": "Une phénoménologie et une morale musicale selon l’esprit de "
                  "saint Augustin.",
    },
    {
        "slug": "musicologue/chanson-populaire", "parent": "musicologue",
        "titre": "Le Livre des chansons",
        "chapeau": "Cent trente-neuf chansons anciennes choisies et commentées.",
        "resume": "Cent trente-neuf chansons anciennes choisies et commentées.",
    },
    {
        "slug": "musicologue/conferences-musicales", "parent": "musicologue",
        "titre": "Les conférences musicales",
        "chapeau": "Cinquante-huit séances d’initiation à Lyon, entre 1942 et 1945.",
        "resume": "Cinquante-huit séances d’initiation à Lyon entre 1942 et 1945.",
    },
    {
        "slug": "musicologue/critique-musicale", "parent": "musicologue",
        "titre": "La critique musicale",
        "chapeau": "<cite>Esprit</cite>, <cite>Diapason</cite> et l’Académie "
                   "Charles-Cros.",
        "resume": "<cite>Esprit</cite>, <cite>Diapason</cite> et l’Académie "
                  "Charles-Cros.",
    },

    # Ressources -------------------------------------------------------------
    {
        "slug": "ressources/les-livres", "parent": "ressources",
        "fragment": "ressources-livres",
        "titre": "Les livres",
        "chapeau": "L’œuvre publiée, de 1934 aux éditions posthumes. Seules les "
                   "dates des premières éditions sont mentionnées.",
        "resume": "L’œuvre publiée, de 1934 aux éditions posthumes.",
    },
    {
        "slug": "ressources/bibliographie", "parent": "ressources",
        "fragment": "ressources-bibliographie",
        "titre": "Bibliographies",
        "chapeau": "Bibliographies érudites et non érudites, revues et ouvrages "
                   "collectifs auxquels Marrou a contribué.",
        "resume": "Bibliographies érudites, revues et ouvrages collectifs.",
    },
    {
        "slug": "ressources/articles", "parent": "ressources",
        "fragment": "ressources-articles",
        "titre": "Articles divers",
        "chapeau": "Articles, entretiens et contributions hors du champ strictement "
                   "érudit.",
        "resume": "Articles, entretiens et contributions non érudites.",
    },
]

# Rubriques dont la page se compose d'une grille de cartes vers ses enfants
GRILLES = {"historien", "penser-agir", "musicologue", "ressources"}

# Liens transversaux du bandeau d'accueil : libellé, cible, disponible ?
# Aucun libellé ne doit promettre une page qui n'existe pas.
TRANSVERSAUX = [
    ("Biographie", "decouvrir", True),
    ("Les livres", "ressources/les-livres", True),
    ("Nous contacter", "association#contact", True),
]
