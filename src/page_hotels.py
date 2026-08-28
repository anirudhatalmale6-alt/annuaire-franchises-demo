# -*- coding: utf-8 -*-
"""Fabrique demo/hotellerie.html.

La feuille de style n'est PAS recopiee a la main : elle est lue dans
demo/index.html et injectee telle quelle. Les deux pages sont livrees
autonomes — un seul fichier a televerser, rien a lier — mais leur style
reste une seule source. Deux copies d'une meme feuille finissent toujours
par diverger, et c'est la page qu'on ne regarde pas qui prend le retard.

Un controle (tests-hotels.py) verifie que le bloc partage est bien identique
au caractere pres dans les deux fichiers.
"""

import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)


# Le site des maisons de prestige est un site separe : on ne peut pas
# l'atteindre par un chemin relatif. Adresse a changer le jour du nom
# de domaine definitif.
URL_PRESTIGE = 'https://anirudhatalmale6-alt.github.io/maisons-de-prestige/'


def css_commune():
    src = open(os.path.join(DEMO, 'index.html'), encoding='utf-8').read()
    m = re.search(r'<style>\n(.*?)\n</style>', src, re.S)
    if not m:
        raise SystemExit('feuille de style introuvable dans index.html')
    return m.group(1)


CSS_HOTELS = """
/* Propre a l'hotellerie */
.grpline{font-size:11.5px;color:#8b93a5;margin:0 0 2px}
.seg{display:inline-block;background:#f1f3f6;border-radius:6px;padding:3px 9px;
  font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--gris);
  font-weight:700}
.cles{font-variant-numeric:tabular-nums}
.contrats{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.contrats span{border:1px solid var(--trait);border-radius:6px;padding:3px 8px;
  font-size:11.5px;color:var(--gris)}
.calc{font-size:12px;color:var(--gris);margin:-12px 0 18px}
.defs dt{font-weight:700;font-size:13.4px;margin-top:12px}
.defs dd{margin:3px 0 0;font-size:13.2px;color:#4e5563}
.pourquoi{background:#fff;border:1px solid var(--trait);border-radius:12px;
  padding:18px 20px;margin-bottom:18px;box-shadow:var(--ombre)}
.pourquoi h2{margin:0 0 8px;font-size:16px}
.pourquoi p{margin:0;font-size:13.4px;color:#4e5563}
.pourquoi ul{margin:10px 0 0;padding-left:18px;font-size:13.4px;color:#4e5563}
.pourquoi li{margin-bottom:4px}
"""

PAGE = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Franchises hotelieres &middot; section a part</title>
<style>
__CSS_COMMUNE__
__CSS_HOTELS__
</style>

<header>
  <div class="wrap top">
    <div class="logo">Annuaire<b>.</b>Franchises<span class="ph-marque">marque a\
 definir</span><span id="lg-pays"></span></div>
    <nav>
      <a href="index.html" id="nv1"></a>
      <a id="nv4" class="on"></a>
      <!-- Le site de prestige est un SITE SEPARE : lien absolu, pas relatif.
           C'est l'adresse a changer le jour du nom de domaine. -->
      <a id="nv5" href="__URL_PRESTIGE__"></a>
    </nav>
    <div class="droite">
      <div class="lang">
        <button data-l="fr" class="on">FR</button><button data-l="en">EN</button>
      </div>
    </div>
  </div>
</header>

<div class="demo"><div class="wrap" id="bandeau-demo"></div></div>

<section class="hero">
  <div class="wrap">
    <h1 id="h-titre"></h1>
    <p id="h-sous"></p>
    <div class="rech">
      <input id="q" type="search" autocomplete="off">
      <button id="go"></button>
    </div>
    <div class="chips" id="chips"></div>
    <div class="marches" id="marches"></div>
  </div>
</section>

<div class="wrap">
  <div class="corps">
    <aside class="filtres" id="filtres"></aside>
    <main>
      <div class="pourquoi" id="pourquoi"></div>
      <div class="entete-res">
        <div class="cpt" id="cpt"></div>
        <div class="tri">
          <span id="tri-l"></span>
          <select id="tri"></select>
        </div>
      </div>
      <div class="grille" id="grille"></div>
      <div class="vide" id="vide" style="display:none"></div>
      <button class="plus" id="plus" style="display:none"></button>
    </main>
  </div>
</div>

<footer><div class="wrap" id="pied"></div></footer>

<div class="voile" id="voile"></div>
<div class="panneau" id="panneau"></div>

<script>
/* ------------------------------------------------------------------ i18n */
var T = {
 fr: {
  nv1: 'Annuaire generaliste', nv4: 'Hotellerie',
  nv5: 'Maisons de prestige',
  titre: 'Les franchises hotelieres',
  sous: 'Une section a part, parce qu\\'un hotel ne se compare pas a un commerce\\
 sur les memes colonnes : on y investit a la cle, on paie deux redevances, et\\
 le contrat n\\'est pas toujours une franchise.',
  rech: 'Marque, groupe, segment...', go: 'Chercher',
  demo: 'Demonstration. Les %(n)d marques ci-dessous sont <b>fictives</b>, reparties\\
 en %(g)d groupes. Les montants sont tires dans les bandes du segment vise.\\
 Aucun groupe reel, aucune marque reelle, aucun chiffre reel. Le moteur, lui,\\
 est le vrai.',
  m_marques: 'marques', m_groupes: 'groupes', m_segments: 'segments',
  m_pays: 'pays',
  p_titre: 'Ce que cette section fait de different',
  p_intro: 'Les colonnes ne sont pas celles de l\\'annuaire generaliste, parce que\\
 les questions ne sont pas les memes :',
  p_1: '<b>L\\'investissement est a la cle</b>, pas au projet. Le cout total est\\
 <i>calcule</i> a partir de la taille acceptee, jamais tire a part.',
  p_2: '<b>Deux redevances</b> : la marque d\\'un cote, la commercialisation et la\\
 fidelite de l\\'autre. Un candidat compare la somme, elle est affichee.',
  p_3: '<b>Le contrat</b> peut etre une franchise, un contrat de gestion, un bail\\
 ou un engagement de developpement. Le luxe se gere, l\\'economique se franchise.',
  p_4: '<b>La taille</b> : une enseigne accepte des hotels entre N et M cles et\\
 refuse les autres. Le filtre repond a « mon hotel fait 120 chambres, qui le\\
 prend ».',
  p_5: '<b>La conversion</b> d\\'un hotel existant sous la marque : premiere\\
 question d\\'un proprietaire qui a deja des murs.',
  f_segment: 'Segment', f_contrat: 'Type de contrat', f_region: 'Region',
  f_pays: 'Pays ouverts au developpement', f_tranche: 'Investissement par cle',
  f_taille: 'Taille de mon hotel', f_conv: 'Conversion',
  f_conv_l: 'Accepte la conversion d\\'un hotel existant',
  f_taille_0: 'Toutes tailles', f_taille_n: '%(n)d cles',
  raz: 'Effacer les filtres',
  cpt_1: 'enseigne hoteliere', cpt_n: 'enseignes hotelieres',
  cpt_sur: 'sur', tri_l: 'Trier par',
  tri_p: 'Pertinence', tri_ic: 'Investissement / cle croissant',
  tri_id: 'Investissement / cle decroissant', tri_r: 'Taille du reseau',
  tri_az: 'A - Z',
  vide: 'Aucune enseigne ne correspond. Elargissez un critere : la taille de\\
 l\\'hotel et le type de contrat sont les deux plus selectifs.',
  plus: 'Voir plus d\\'enseignes',
  c_inv: 'Investissement / cle', c_taille: 'Taille acceptee',
  c_red: 'Redevances', c_res: 'Reseau', c_cles: 'cles',
  c_hotels: 'hotels', c_cta: 'Demander le dossier',
  d_groupe: 'Groupe', d_segment: 'Segment', d_origine: 'Pays d\\'origine',
  d_inv: 'Investissement par cle', d_projet: 'Cout du projet',
  d_taille: 'Taille acceptee', d_droit: 'Droit d\\'entree',
  d_droit_v: '%(cle)s par cle, minimum %(min)s',
  d_marque: 'Redevance de marque',
  d_com: 'Redevance de commercialisation et fidelite',
  d_total: 'Total des redevances', d_duree: 'Duree du contrat',
  d_duree_v: '%(n)d ans', d_reno: 'Cycle de renovation',
  d_reno_v: 'tous les %(n)d ans', d_conv: 'Conversion acceptee',
  d_oui: 'Oui', d_non: 'Non', d_res: 'Reseau',
  d_res_v: '%(h)s hotels, %(c)s cles', d_moy: 'Taille moyenne',
  d_cre: 'Creation', d_fra: 'Franchise depuis',
  h_calc: 'Le cout du projet n\\'est pas un chiffre a part : c\\'est\\
 l\\'investissement a la cle multiplie par la taille acceptee.',
  h_contrats: 'Contrats proposes', h_soutien: 'Ce que le groupe apporte',
  h_pays: 'Pays ouverts au developpement',
  f_titre: 'Demander le dossier de developpement',
  f_i: 'Demonstration : rien n\\'est envoye. Sur le site reel, la demande part\\
 chez le groupe et une copie reste dans votre espace.',
  f_nom: 'Nom', f_soc: 'Societe', f_mail: 'Courriel', f_tel: 'Telephone',
  f_pays_p: 'Pays du projet', f_cles: 'Nombre de cles envisage',
  fo_contrat: 'Contrat souhaite', f_msg: 'Le projet en quelques lignes',
  f_env: 'Envoyer la demande',
  f_ok: 'Demande enregistree. <b>Ceci est une demonstration</b> : rien n\\'a ete\\
 envoye.',
  f_req: 'Merci de remplir les champs obligatoires.',
  f_mailerr: 'Cette adresse ne ressemble pas a une adresse valide.',
  pied: 'Section hotellerie de l\\'annuaire de franchises &mdash; demonstration\\
 technique. Donnees fictives. Ni une offre de franchise, ni un document\\
 d\\'information precontractuelle au sens de la loi. Les tranches sont classees\\
 sur une valeur de reference en euros ; chaque fiche s\\'affiche dans sa devise.'
 },
 en: {
  nv1: 'General directory', nv4: 'Hospitality',
  nv5: 'Prestige houses',
  titre: 'Hotel franchises',
  sous: 'A separate section, because a hotel cannot be compared to a shop on the\\
 same columns: you invest per key, you pay two fees, and the agreement is not\\
 always a franchise.',
  rech: 'Brand, group, segment...', go: 'Search',
  demo: 'Demonstration. The %(n)d brands below are <b>fictional</b>, held by\\
 %(g)d groups. Figures are drawn within the real ranges of each segment. No real\\
 group, no real brand, no real number. The engine itself is real.',
  m_marques: 'brands', m_groupes: 'groups', m_segments: 'segments',
  m_pays: 'countries',
  p_titre: 'What this section does differently',
  p_intro: 'The columns are not those of the general directory, because the\\
 questions are not the same:',
  p_1: '<b>Investment is per key</b>, not per project. Total cost is <i>computed</i>\\
 from the accepted size, never drawn separately.',
  p_2: '<b>Two fees</b>: brand on one side, sales, marketing and loyalty on the\\
 other. A candidate compares the sum, so the sum is shown.',
  p_3: '<b>The agreement</b> can be a franchise, a management contract, a lease or\\
 a development commitment. Luxury is managed, economy is franchised.',
  p_4: '<b>Size</b>: a brand takes hotels between N and M keys and turns down the\\
 rest. The filter answers "my hotel has 120 rooms, who takes it".',
  p_5: '<b>Conversion</b> of an existing hotel to the brand: the first question of\\
 an owner who already has a building.',
  f_segment: 'Segment', f_contrat: 'Agreement type', f_region: 'Region',
  f_pays: 'Countries open for development', f_tranche: 'Investment per key',
  f_taille: 'My hotel size', f_conv: 'Conversion',
  f_conv_l: 'Accepts conversion of an existing hotel',
  f_taille_0: 'Any size', f_taille_n: '%(n)d keys',
  raz: 'Clear filters',
  cpt_1: 'hotel brand', cpt_n: 'hotel brands', cpt_sur: 'of', tri_l: 'Sort by',
  tri_p: 'Relevance', tri_ic: 'Investment / key, low to high',
  tri_id: 'Investment / key, high to low', tri_r: 'Network size', tri_az: 'A - Z',
  vide: 'No brand matches. Widen one criterion: hotel size and agreement type are\\
 the two most selective.',
  plus: 'Show more brands',
  c_inv: 'Investment / key', c_taille: 'Accepted size', c_red: 'Fees',
  c_res: 'Network', c_cles: 'keys', c_hotels: 'hotels',
  c_cta: 'Request the development pack',
  d_groupe: 'Group', d_segment: 'Segment', d_origine: 'Home country',
  d_inv: 'Investment per key', d_projet: 'Project cost',
  d_taille: 'Accepted size', d_droit: 'Application fee',
  d_droit_v: '%(cle)s per key, minimum %(min)s',
  d_marque: 'Brand fee', d_com: 'Sales, marketing and loyalty fee',
  d_total: 'Total fees', d_duree: 'Term', d_duree_v: '%(n)d years',
  d_reno: 'Renovation cycle', d_reno_v: 'every %(n)d years',
  d_conv: 'Conversion accepted', d_oui: 'Yes', d_non: 'No', d_res: 'Network',
  d_res_v: '%(h)s hotels, %(c)s keys', d_moy: 'Average size',
  d_cre: 'Founded', d_fra: 'Franchising since',
  h_calc: 'Project cost is not a separate figure: it is the per-key investment\\
 multiplied by the accepted size.',
  h_contrats: 'Agreements offered', h_soutien: 'What the group provides',
  h_pays: 'Countries open for development',
  f_titre: 'Request the development pack',
  f_i: 'Demonstration: nothing is sent. On the live site the request goes to the\\
 group and a copy stays in your account.',
  f_nom: 'Name', f_soc: 'Company', f_mail: 'Email', f_tel: 'Phone',
  f_pays_p: 'Project country', f_cles: 'Planned number of keys',
  fo_contrat: 'Preferred agreement', f_msg: 'About the project',
  f_env: 'Send request',
  f_ok: 'Request recorded. <b>This is a demonstration</b>: nothing was sent.',
  f_req: 'Please fill in the required fields.',
  f_mailerr: 'That email address does not look valid.',
  pied: 'Hospitality section of the franchise directory &mdash; technical\\
 demonstration. Fictional data. This is neither an offer of a franchise nor a\\
 pre-contractual disclosure document within the meaning of the law. Brackets are\\
 ranked on a euro reference value; each listing displays in its own currency.'
 }
};

var L = 'fr';
var D = null, PAS = 12, montre = PAS;
var F = {q:'', segs:[], contrats:[], regions:[], pays:[], tranches:[],
         taille:'', conv:false, tri:'p'};

function t(k){ return T[L][k]; }
function loc(){ return L === 'fr' ? 'fr-CA' : 'en-CA'; }
var FMT = {};
function argent(v, dev){
  var k = L + dev;
  if (!FMT[k]) FMT[k] = new Intl.NumberFormat(loc(),
    {style:'currency', currency:dev, maximumFractionDigits:0});
  return FMT[k].format(v);
}
function nb(v){ return v.toLocaleString(loc()); }
/* L'espace avant le %% doit etre INSECABLE en francais : « 4,4 % » coupe en
   fin de ligne se lit « 4,4 » sur une ligne et « % » sur la suivante. */
function pct(v){
  var s = v.toLocaleString(loc(), {minimumFractionDigits:1,
                                   maximumFractionDigits:1});
  return L === 'fr' ? s + '\\u00a0%' : s + '%';
}
function ech(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
                  .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function lib(liste, cle){
  for (var i=0;i<liste.length;i++) if (liste[i].cle === cle) return liste[i][L];
  return cle;
}
function fmt(s, o){
  return s.replace(/%\\((\\w+)\\)[ds]/g, function(_, k){ return o[k]; });
}
function pliage(s){
  return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
}

/* --------------------------------------------------------------- filtrage */
/* `sauf` sert aux compteurs : le nombre affiche a cote d'une case est le
   nombre de fiches qui resteraient SI on la cochait, les autres filtres en
   place. Calcule sur le resultat final, il afficherait 0 partout — exact, et
   parfaitement inutile. */
function passe(f, sauf){
  if (F.q){
    var mots = pliage(F.q).split(/\\s+/).filter(Boolean);
    var champ = pliage(f.nom + ' ' + f.groupe + ' ' + f.resume.fr + ' ' +
                       f.resume.en + ' ' + lib(D.segments, f.segment) + ' ' +
                       lib(D.pays, f.pays_origine));
    for (var i=0;i<mots.length;i++) if (champ.indexOf(mots[i]) < 0) return false;
  }
  if (sauf !== 'segs' && F.segs.length && F.segs.indexOf(f.segment) < 0)
    return false;
  if (sauf !== 'contrats' && F.contrats.length){
    var ok = false;
    for (var a=0;a<F.contrats.length;a++)
      if (f.contrats.indexOf(F.contrats[a]) >= 0){ ok = true; break; }
    if (!ok) return false;
  }
  if (sauf !== 'regions' && F.regions.length && F.regions.indexOf(f.region) < 0)
    return false;
  if (sauf !== 'pays' && F.pays.length){
    var okp = false;
    for (var j=0;j<F.pays.length;j++)
      if (f.pays.indexOf(F.pays[j]) >= 0){ okp = true; break; }
    if (!okp) return false;
  }
  if (sauf !== 'tranches' && F.tranches.length &&
      F.tranches.indexOf(f.investissement_cle.tranche) < 0) return false;
  /* La taille demande « qui prend un hotel de N cles » : N doit tomber DANS
     la fourchette acceptee, pas au-dessus d'un minimum. */
  if (sauf !== 'taille' && F.taille){
    var n = parseInt(F.taille, 10);
    if (n < f.cles.min || n > f.cles.max) return false;
  }
  if (sauf !== 'conv' && F.conv && !f.conversion) return false;
  return true;
}

function liste(){
  var r = D.fiches.filter(function(f){ return passe(f, null); });
  if (F.tri === 'ic') r.sort(function(a,b){
    return a.investissement_cle.eur_bas - b.investissement_cle.eur_bas; });
  else if (F.tri === 'id') r.sort(function(a,b){
    return b.investissement_cle.eur_bas - a.investissement_cle.eur_bas; });
  else if (F.tri === 'r') r.sort(function(a,b){
    return b.reseau.hotels - a.reseau.hotels; });
  else if (F.tri === 'az') r.sort(function(a,b){
    return a.nom.localeCompare(b.nom, loc()); });
  return r;
}

function compte(sauf, test){
  var n = 0;
  for (var i=0;i<D.fiches.length;i++){
    var f = D.fiches[i];
    if (passe(f, sauf) && test(f)) n++;
  }
  return n;
}

/* ---------------------------------------------------------------- rendu */
function cocher(groupe, cle, tableau){
  var i = tableau.indexOf(cle);
  if (i < 0) tableau.push(cle); else tableau.splice(i, 1);
  montre = PAS;
  tout();
}

function bloc(titre, sauf, options, tableau, scroll){
  var h = '<div class="fgrp"><h3>' + ech(titre) + '</h3>' +
          (scroll ? '<div class="scroll">' : '');
  for (var i=0;i<options.length;i++){
    var o = options[i];
    h += '<label><input type="checkbox" data-g="' + sauf + '" data-v="' +
         ech(o.cle) + '"' + (tableau.indexOf(o.cle) >= 0 ? ' checked' : '') +
         '><span>' + ech(o.lib) + '</span><span class="n">' + o.n + '</span></label>';
  }
  return h + (scroll ? '</div>' : '') + '</div>';
}

function filtres(){
  var h = '';

  h += bloc(t('f_segment'), 'segs', D.segments.map(function(s){
    return {cle:s.cle, lib:s[L], n:compte('segs', function(f){
      return f.segment === s.cle; })};
  }), F.segs, false);

  h += bloc(t('f_contrat'), 'contrats', D.contrats.map(function(c){
    return {cle:c.cle, lib:c[L], n:compte('contrats', function(f){
      return f.contrats.indexOf(c.cle) >= 0; })};
  }), F.contrats, false);

  h += bloc(t('f_tranche'), 'tranches', D.tranches.map(function(x){
    return {cle:x.cle, lib:x[L], n:compte('tranches', function(f){
      return f.investissement_cle.tranche === x.cle; })};
  }), F.tranches, false);

  h += '<div class="fgrp"><h3>' + ech(t('f_taille')) + '</h3><select id="taille">' +
       '<option value="">' + ech(t('f_taille_0')) + '</option>';
  for (var i=0;i<D.tailles.length;i++){
    var n = D.tailles[i];
    var q = compte('taille', function(f){
      return n >= f.cles.min && n <= f.cles.max; });
    h += '<option value="' + n + '"' + (F.taille == n ? ' selected' : '') + '>' +
         ech(fmt(t('f_taille_n'), {n:n})) + ' (' + q + ')</option>';
  }
  h += '</select></div>';

  h += '<div class="fgrp"><h3>' + ech(t('f_conv')) + '</h3>' +
       '<label><input type="checkbox" id="conv"' + (F.conv ? ' checked' : '') +
       '><span>' + ech(t('f_conv_l')) + '</span><span class="n">' +
       compte('conv', function(f){ return f.conversion; }) + '</span></label></div>';

  h += bloc(t('f_region'), 'regions', D.regions.map(function(r){
    return {cle:r.cle, lib:r[L], n:compte('regions', function(f){
      return f.region === r.cle; })};
  }), F.regions, false);

  h += bloc(t('f_pays'), 'pays', D.pays.map(function(p){
    return {cle:p.cle, lib:p[L], n:compte('pays', function(f){
      return f.pays.indexOf(p.cle) >= 0; })};
  }), F.pays, true);

  h += '<button class="raz" id="raz">' + ech(t('raz')) + '</button>';

  var el = document.getElementById('filtres');
  el.innerHTML = h;
  var cases = el.querySelectorAll('input[data-g]');
  for (var k=0;k<cases.length;k++){
    cases[k].addEventListener('change', function(){
      var g = this.getAttribute('data-g');
      cocher(g, this.getAttribute('data-v'), F[g]);
    });
  }
  document.getElementById('taille').addEventListener('change', function(){
    F.taille = this.value; montre = PAS; tout();
  });
  document.getElementById('conv').addEventListener('change', function(){
    F.conv = this.checked; montre = PAS; tout();
  });
  document.getElementById('raz').addEventListener('click', function(){
    F.segs = []; F.contrats = []; F.regions = []; F.pays = [];
    F.tranches = []; F.taille = ''; F.conv = false; F.q = '';
    document.getElementById('q').value = '';
    montre = PAS; tout();
  });
}

function carte(f){
  var inv = argent(f.investissement_cle.bas, f.devise) + ' - ' +
            argent(f.investissement_cle.haut, f.devise);
  return '<article class="fiche" data-id="' + ech(f.id) + '">' +
    '<p class="grpline">' + ech(f.groupe) + '</p>' +
    '<div class="haut"><span class="seg">' + ech(lib(D.segments, f.segment)) +
    '</span></div>' +
    '<h2>' + ech(f.nom) + '</h2>' +
    '<p class="res">' + ech(f.resume[L]) + '</p>' +
    '<dl><dt>' + ech(t('c_inv')) + '</dt><dd>' + inv + '</dd>' +
    '<dt>' + ech(t('c_taille')) + '</dt><dd class="cles">' + nb(f.cles.min) +
    ' - ' + nb(f.cles.max) + ' ' + ech(t('c_cles')) + '</dd>' +
    '<dt>' + ech(t('c_red')) + '</dt><dd>' + pct(f.redevances.marque) + ' + ' +
    pct(f.redevances.commercialisation) + '</dd>' +
    '<dt>' + ech(t('c_res')) + '</dt><dd>' + nb(f.reseau.hotels) + ' ' +
    ech(t('c_hotels')) + '</dd></dl>' +
    '<div class="bas"><button class="cta">' + ech(t('c_cta')) + '</button></div>' +
    '</article>';
}

function rendre(){
  var r = liste();
  var g = document.getElementById('grille');
  g.innerHTML = r.slice(0, montre).map(carte).join('');
  document.getElementById('vide').style.display = r.length ? 'none' : 'block';
  document.getElementById('vide').textContent = t('vide');
  var p = document.getElementById('plus');
  p.style.display = r.length > montre ? 'block' : 'none';
  p.textContent = t('plus');

  /* Le compteur annonce le sous-ensemble ET le total : « 12 » tout seul
     laisserait croire que la section en contient douze. */
  document.getElementById('cpt').innerHTML =
    '<b>' + nb(r.length) + '</b> ' +
    ech(r.length === 1 ? t('cpt_1') : t('cpt_n')) + ' ' +
    ech(t('cpt_sur')) + ' ' + nb(D.fiches.length);

  var cartes = g.querySelectorAll('.fiche');
  for (var i=0;i<cartes.length;i++){
    cartes[i].querySelector('.cta').addEventListener('click', (function(id){
      return function(){ ouvrir(id); };
    })(cartes[i].getAttribute('data-id')));
  }
}

/* ---------------------------------------------------------------- fiche */
function ligne(k, v){
  return '<tr><td>' + ech(k) + '</td><td>' + v + '</td></tr>';
}

function ouvrir(id){
  var f = null;
  for (var i=0;i<D.fiches.length;i++) if (D.fiches[i].id === id) f = D.fiches[i];
  if (!f) return;

  var h = '<div class="ph"><div class="cat">' + ech(lib(D.segments, f.segment)) +
    ' &middot; ' + ech(f.groupe) + '</div><h2>' + ech(f.nom) + '</h2>' +
    '<button class="fermer" id="fermer">&times;</button></div><div class="pc">';

  h += '<p style="margin-top:0;color:#4e5563">' + ech(f.resume[L]) + '</p>';
  h += '<table class="faits">' +
    ligne(t('d_groupe'), ech(f.groupe)) +
    ligne(t('d_origine'), ech(lib(D.pays, f.pays_origine))) +
    ligne(t('d_inv'), argent(f.investissement_cle.bas, f.devise) + ' - ' +
          argent(f.investissement_cle.haut, f.devise)) +
    ligne(t('d_taille'), nb(f.cles.min) + ' - ' + nb(f.cles.max) + ' ' +
          ech(t('c_cles'))) +
    ligne(t('d_projet'), argent(f.projet.bas, f.devise) + ' - ' +
          argent(f.projet.haut, f.devise)) +
    ligne(t('d_droit'), ech(fmt(t('d_droit_v'),
          {cle: argent(f.droit_entree.par_cle, f.devise),
           min: argent(f.droit_entree.plancher, f.devise)}))) +
    ligne(t('d_marque'), pct(f.redevances.marque)) +
    ligne(t('d_com'), pct(f.redevances.commercialisation)) +
    ligne(t('d_total'), '<b>' + pct(f.redevances.total) + '</b>') +
    ligne(t('d_duree'), ech(fmt(t('d_duree_v'), {n:f.duree_contrat}))) +
    ligne(t('d_reno'), ech(fmt(t('d_reno_v'), {n:f.renovation_ans}))) +
    ligne(t('d_conv'), ech(f.conversion ? t('d_oui') : t('d_non'))) +
    ligne(t('d_res'), ech(fmt(t('d_res_v'),
          {h: nb(f.reseau.hotels), c: nb(f.reseau.cles)}))) +
    ligne(t('d_moy'), nb(f.reseau.taille_moyenne) + ' ' + ech(t('c_cles'))) +
    /* Une annee n'est pas un montant : nb() y met un separateur de
       milliers et « 1986 » s'affiche « 1 986 ». */
    ligne(t('d_cre'), String(f.annee_creation)) +
    ligne(t('d_fra'), String(f.annee_franchisage)) +
    '</table>';
  h += '<p class="calc">' + ech(t('h_calc')) + '</p>';

  h += '<h4>' + ech(t('h_contrats')) + '</h4><dl class="defs">';
  for (var c=0;c<f.contrats.length;c++){
    for (var d=0;d<D.contrats.length;d++){
      if (D.contrats[d].cle === f.contrats[c]){
        h += '<dt>' + ech(D.contrats[d][L]) + '</dt><dd>' +
             ech(D.contrats[d][L === 'fr' ? 'desc_fr' : 'desc_en']) + '</dd>';
      }
    }
  }
  h += '</dl>';

  h += '<h4>' + ech(t('h_soutien')) + '</h4><div class="prov">';
  for (var s=0;s<f.soutiens.length;s++)
    h += '<span>' + ech(lib(D.soutiens, f.soutiens[s])) + '</span>';
  h += '</div>';

  h += '<h4>' + ech(t('h_pays')) + '</h4><div class="prov">';
  for (var p=0;p<f.pays.length;p++)
    h += '<span>' + ech(lib(D.pays, f.pays[p])) + '</span>';
  h += '</div>';

  h += '<h4>' + ech(t('f_titre')) + '</h4><div class="form">' +
    '<p class="i">' + t('f_i') + '</p>' +
    '<div class="duo"><div><label>' + ech(t('f_nom')) + ' *</label>' +
    '<input id="c_nom"></div><div><label>' + ech(t('f_soc')) + '</label>' +
    '<input id="c_soc"></div></div>' +
    '<div class="duo"><div><label>' + ech(t('f_mail')) + ' *</label>' +
    '<input id="c_mail" type="email"></div><div><label>' + ech(t('f_tel')) +
    '</label><input id="c_tel"></div></div>' +
    '<div class="duo"><div><label>' + ech(t('f_pays_p')) + '</label><select id="c_pays">';
  for (var q=0;q<f.pays.length;q++)
    h += '<option value="' + ech(f.pays[q]) + '">' + ech(lib(D.pays, f.pays[q])) +
         '</option>';
  h += '</select></div><div><label>' + ech(t('f_cles')) + '</label>' +
    '<input id="c_cles" type="number" min="1" value="' + f.cles.min + '"></div></div>' +
    '<label>' + ech(t('fo_contrat')) + '</label><select id="c_contrat">';
  for (var y=0;y<f.contrats.length;y++)
    h += '<option value="' + ech(f.contrats[y]) + '">' +
         ech(lib(D.contrats, f.contrats[y])) + '</option>';
  h += '</select>' +
    '<label>' + ech(t('f_msg')) + '</label><textarea id="c_msg"></textarea>' +
    '<button id="c_env">' + ech(t('f_env')) + '</button>' +
    '<div id="c_res"></div></div>';

  h += '</div>';
  var pan = document.getElementById('panneau');
  pan.innerHTML = h;
  pan.classList.add('on');
  document.getElementById('voile').classList.add('on');
  document.getElementById('fermer').addEventListener('click', fermer);
  document.getElementById('c_env').addEventListener('click', function(){
    envoyer();
  });
}

function envoyer(){
  var nom = document.getElementById('c_nom');
  var mail = document.getElementById('c_mail');
  var res = document.getElementById('c_res');
  nom.classList.remove('err'); mail.classList.remove('err');
  if (!nom.value.trim() || !mail.value.trim()){
    if (!nom.value.trim()) nom.classList.add('err');
    if (!mail.value.trim()) mail.classList.add('err');
    res.innerHTML = '<p class="msg-err">' + ech(t('f_req')) + '</p>';
    return;
  }
  if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(mail.value.trim())){
    mail.classList.add('err');
    res.innerHTML = '<p class="msg-err">' + ech(t('f_mailerr')) + '</p>';
    return;
  }
  res.innerHTML = '<div class="ok">' + t('f_ok') + '</div>';
}

function fermer(){
  document.getElementById('panneau').classList.remove('on');
  document.getElementById('voile').classList.remove('on');
}

/* ----------------------------------------------------------------- page */
function chips(){
  var h = '';
  for (var i=0;i<D.segments.length;i++){
    var s = D.segments[i];
    h += '<button data-s="' + ech(s.cle) + '"' +
         (F.segs.indexOf(s.cle) >= 0 ? ' class="on"' : '') + '>' +
         ech(s[L]) + '</button>';
  }
  var el = document.getElementById('chips');
  el.innerHTML = h;
  var b = el.querySelectorAll('button');
  for (var k=0;k<b.length;k++)
    b[k].addEventListener('click', (function(cle){
      return function(){ cocher('segs', cle, F.segs); };
    })(b[k].getAttribute('data-s')));
}

function tout(){
  document.getElementById('nv1').textContent = t('nv1');
  document.getElementById('nv4').textContent = t('nv4');
  document.getElementById('nv5').textContent = t('nv5');
  document.getElementById('h-titre').textContent = t('titre');
  document.getElementById('h-sous').textContent = t('sous');
  document.getElementById('q').placeholder = t('rech');
  document.getElementById('go').textContent = t('go');
  document.getElementById('bandeau-demo').innerHTML =
    fmt(t('demo'), {n: D.fiches.length, g: D.groupes.length});
  document.getElementById('tri-l').textContent = t('tri_l');
  document.getElementById('pied').innerHTML = t('pied');

  document.getElementById('marches').innerHTML =
    '<div class="marche"><b>' + nb(D.fiches.length) + '</b>' + ech(t('m_marques')) +
    '</div><div class="marche"><b>' + nb(D.groupes.length) + '</b>' +
    ech(t('m_groupes')) + '</div><div class="marche"><b>' +
    nb(D.segments.length) + '</b>' + ech(t('m_segments')) +
    '</div><div class="marche"><b>' + nb(D.pays.length) + '</b>' +
    ech(t('m_pays')) + '</div>';

  document.getElementById('pourquoi').innerHTML =
    '<h2>' + ech(t('p_titre')) + '</h2><p>' + ech(t('p_intro')) + '</p><ul>' +
    '<li>' + t('p_1') + '</li><li>' + t('p_2') + '</li><li>' + t('p_3') +
    '</li><li>' + t('p_4') + '</li><li>' + t('p_5') + '</li></ul>';

  var tri = document.getElementById('tri');
  var opts = [['p','tri_p'],['ic','tri_ic'],['id','tri_id'],['r','tri_r'],
              ['az','tri_az']];
  tri.innerHTML = opts.map(function(o){
    return '<option value="' + o[0] + '"' + (F.tri === o[0] ? ' selected' : '') +
           '>' + ech(t(o[1])) + '</option>'; }).join('');

  chips();
  filtres();
  rendre();
}

function langue(l){
  L = l;
  var b = document.querySelectorAll('.lang button');
  for (var i=0;i<b.length;i++)
    b[i].className = b[i].getAttribute('data-l') === l ? 'on' : '';
  document.documentElement.lang = l;
  tout();
}

var x = new XMLHttpRequest();
x.open('GET', 'hotellerie.json', true);
x.onload = function(){
  if (x.status < 200 || x.status >= 300){ echec(x.status); return; }
  try { D = JSON.parse(x.responseText); }
  catch (e){ echec('JSON'); return; }
  demarrer();
};
/* Un chargement rate se DIT. Une grille vide et muette ressemble a une
   section vide, et c'est un mensonge d'un autre genre. */
x.onerror = function(){ echec('reseau'); };
function echec(code){
  document.getElementById('grille').innerHTML =
    '<div class="vide">hotellerie.json n\\'a pas pu etre charge (' + ech(code) +
    '). Le fichier doit se trouver a cote de cette page.</div>';
}
x.send();

function demarrer(){
  var m = location.search.match(/[?&]l=(fr|en)/);
  document.getElementById('q').addEventListener('input', function(){
    F.q = this.value; montre = PAS; tout();
  });
  document.getElementById('go').addEventListener('click', function(){
    F.q = document.getElementById('q').value; montre = PAS; tout();
  });
  document.getElementById('tri').addEventListener('change', function(){
    F.tri = this.value; rendre();
  });
  document.getElementById('plus').addEventListener('click', function(){
    montre += PAS; rendre();
  });
  document.getElementById('voile').addEventListener('click', fermer);
  var b = document.querySelectorAll('.lang button');
  for (var i=0;i<b.length;i++)
    b[i].addEventListener('click', function(){ langue(this.getAttribute('data-l')); });
  langue(m ? m[1] : 'fr');
}
</script>
"""


def main():
    html = (PAGE.replace('__CSS_COMMUNE__', css_commune())
                .replace('__CSS_HOTELS__', CSS_HOTELS)
                .replace('__URL_PRESTIGE__', URL_PRESTIGE))
    chemin = os.path.join(DEMO, 'hotellerie.html')
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write(html)
    print('%s  (%d octets)' % (chemin, os.path.getsize(chemin)))


if __name__ == '__main__':
    main()
