/*
 * Comportements du site : menu mobile et recherche plein texte.
 * Le site est composé de vraies pages HTML : aucun routage ici.
 */
(function () {
  'use strict';

  var BASE = window.BASE_SITE || '';

  /* ---------------------------------------------------------------------
     Menu mobile
     Fermeture par Échap, par clic à l'extérieur, et retour du focus sur le
     bouton. Tant que le menu est ouvert, la tabulation reste à l'intérieur.
     --------------------------------------------------------------------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');

  function menuOuvert() {
    return toggle && toggle.getAttribute('aria-expanded') === 'true';
  }

  function ouvrirMenu(ouvrir) {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', String(ouvrir));
    nav.dataset.open = String(ouvrir);
    if (ouvrir) {
      var premier = nav.querySelector('a');
      if (premier) premier.focus();
    }
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      ouvrirMenu(!menuOuvert());
    });

    document.addEventListener('keydown', function (event) {
      if (!menuOuvert()) return;

      if (event.key === 'Escape') {
        ouvrirMenu(false);
        toggle.focus();
        return;
      }
      if (event.key !== 'Tab') return;

      // Piège de focus : bouton + liens du menu forment la boucle.
      var boucle = [toggle].concat(Array.prototype.slice.call(nav.querySelectorAll('a')));
      var index = boucle.indexOf(document.activeElement);
      if (index === -1) return;
      var suivant = event.shiftKey ? index - 1 : index + 1;
      if (suivant < 0) suivant = boucle.length - 1;
      if (suivant >= boucle.length) suivant = 0;
      event.preventDefault();
      boucle[suivant].focus();
    });

    document.addEventListener('click', function (event) {
      if (menuOuvert() && !event.target.closest('.site-header')) ouvrirMenu(false);
    });
  }

  /* ---------------------------------------------------------------------
     Recherche plein texte
     L'index est produit à la construction du site et chargé au premier
     usage seulement. Aucun serveur : la recherche fonctionne même en
     ouvrant les fichiers directement.
     --------------------------------------------------------------------- */
  var dialogue = document.querySelector('[data-search-dialog]');
  var champ = document.querySelector('#site-query');
  var etat = document.querySelector('[data-search-status]');
  var liste = document.querySelector('[data-search-results]');
  var formulaire = document.querySelector('[data-site-search]');
  var chargement = null;

  function sansAccent(texte) {
    return texte.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  function chargerIndex() {
    if (chargement) return chargement;
    chargement = new Promise(function (resoudre, rejeter) {
      if (window.INDEX_RECHERCHE) return resoudre(window.INDEX_RECHERCHE);
      var script = document.createElement('script');
      script.src = BASE + 'recherche.js';
      script.onload = function () { resoudre(window.INDEX_RECHERCHE || []); };
      script.onerror = function () { rejeter(new Error('index indisponible')); };
      document.head.appendChild(script);
    });
    return chargement;
  }

  function extrait(texte, mots) {
    var nu = sansAccent(texte);
    var position = -1;
    for (var i = 0; i < mots.length && position === -1; i++) {
      position = nu.indexOf(mots[i]);
    }
    if (position === -1) return texte.slice(0, 150) + '…';
    var debut = Math.max(0, position - 60);
    var morceau = texte.slice(debut, debut + 200);
    return (debut > 0 ? '…' : '') + morceau.trim() + '…';
  }

  function surligner(texte, mots) {
    var sortie = document.createDocumentFragment();
    var nu = sansAccent(texte);
    var coupures = [];
    mots.forEach(function (mot) {
      var depuis = 0;
      var trouve;
      while ((trouve = nu.indexOf(mot, depuis)) !== -1) {
        coupures.push([trouve, trouve + mot.length]);
        depuis = trouve + mot.length;
      }
    });
    coupures.sort(function (a, b) { return a[0] - b[0]; });

    var curseur = 0;
    coupures.forEach(function (paire) {
      if (paire[0] < curseur) return;
      sortie.appendChild(document.createTextNode(texte.slice(curseur, paire[0])));
      var marque = document.createElement('mark');
      marque.textContent = texte.slice(paire[0], paire[1]);
      sortie.appendChild(marque);
      curseur = paire[1];
    });
    sortie.appendChild(document.createTextNode(texte.slice(curseur)));
    return sortie;
  }

  function chercher(index, requete) {
    var mots = sansAccent(requete).split(/[^a-z0-9œæ]+/).filter(function (mot) {
      return mot.length > 1;
    });
    if (!mots.length) return [];

    return index.map(function (page) {
      var titre = sansAccent(page.titre);
      var texte = sansAccent(page.texte);
      var score = 0;
      var tous = true;
      mots.forEach(function (mot) {
        var dansTitre = titre.indexOf(mot) !== -1;
        var occurrences = texte.split(mot).length - 1;
        if (!dansTitre && !occurrences) tous = false;
        score += (dansTitre ? 25 : 0) + Math.min(occurrences, 12);
      });
      return { page: page, score: tous ? score : score / 6 };
    }).filter(function (resultat) {
      return resultat.score > 0;
    }).sort(function (a, b) {
      return b.score - a.score;
    }).slice(0, 12).map(function (resultat) {
      return { page: resultat.page, mots: mots };
    });
  }

  function afficher(resultats, requete) {
    liste.textContent = '';
    if (!resultats.length) {
      etat.textContent = 'Aucun résultat pour « ' + requete + ' ».';
      return;
    }
    etat.textContent = resultats.length === 1
      ? '1 page trouvée.'
      : resultats.length + ' pages trouvées.';

    resultats.forEach(function (resultat) {
      var page = resultat.page;
      var li = document.createElement('li');
      var lien = document.createElement('a');
      lien.href = BASE + page.url;

      var titre = document.createElement('strong');
      titre.appendChild(surligner(page.titre, resultat.mots));
      lien.appendChild(titre);

      if (page.rubrique) {
        var rubrique = document.createElement('small');
        rubrique.textContent = page.rubrique;
        lien.appendChild(rubrique);
      }

      var apercu = document.createElement('span');
      apercu.appendChild(surligner(extrait(page.texte, resultat.mots), resultat.mots));
      lien.appendChild(apercu);

      li.appendChild(lien);
      liste.appendChild(li);
    });
  }

  function lancer() {
    var requete = (champ.value || '').trim();
    if (requete.length < 2) {
      liste.textContent = '';
      etat.textContent = requete ? 'Saisissez au moins deux caractères.' : '';
      return;
    }
    etat.textContent = 'Recherche…';
    chargerIndex().then(function (index) {
      afficher(chercher(index, requete), requete);
    }).catch(function () {
      liste.textContent = '';
      etat.textContent = 'L’index de recherche n’a pas pu être chargé.';
    });
  }

  var minuteur;
  document.querySelector('[data-search-open]')?.addEventListener('click', function () {
    if (!dialogue) return;
    dialogue.showModal();
    champ.focus();
    champ.select();
    chargerIndex().catch(function () {});
  });

  if (formulaire) {
    formulaire.addEventListener('submit', function (event) {
      event.preventDefault();
      lancer();
    });
  }

  if (champ) {
    // Recherche au fil de la frappe, temporisée.
    champ.addEventListener('input', function () {
      clearTimeout(minuteur);
      minuteur = setTimeout(lancer, 180);
    });
  }

  if (dialogue) {
    // Clic sur le fond : fermeture.
    dialogue.addEventListener('click', function (event) {
      if (event.target === dialogue) dialogue.close();
    });
  }

  // Raccourci « / » pour ouvrir la recherche, comme sur la plupart des sites.
  document.addEventListener('keydown', function (event) {
    if (event.key !== '/' || event.metaKey || event.ctrlKey) return;
    var actif = document.activeElement;
    if (actif && /^(INPUT|TEXTAREA|SELECT)$/.test(actif.tagName)) return;
    if (dialogue && !dialogue.open) {
      event.preventDefault();
      dialogue.showModal();
      champ.focus();
    }
  });
})();
