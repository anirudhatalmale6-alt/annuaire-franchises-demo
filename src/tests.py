# -*- coding: utf-8 -*-
"""Controles de l'annuaire de franchises (Canada / Etats-Unis / Europe).

Deux familles, et la seconde est la seule qui prouve quelque chose :

  A. le fichier de donnees — coherence des montants, des annees, des unites,
     des devises. Pas de reseau, pas de navigateur.
  B. le moteur, dans un VRAI navigateur, sur la VRAIE page : on coche un
     filtre et on compte les cartes que le navigateur a dessinees. Un filtre
     qui « existe dans le code » ne filtre rien tant que personne ne l'a
     clique.

Le port n'est pas ecrit en dur. Sur cette machine, un port choisi a la main a
deja fait tourner toute une suite contre le WordPress d'un autre projet, qui
repondait 404 a tout : trois echecs qui ne parlaient pas du code teste. On
demande un port au systeme, et on verifie que celui qui repond est bien nous
avant d'affirmer quoi que ce soit.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(ICI, 'demo')

ok = [0]
ko = [0]


def t(nom, cond, detail=''):
    if cond:
        ok[0] += 1
        print('  ok   %s' % nom)
    else:
        ko[0] += 1
        print('  ECHEC %s   %s' % (nom, detail))


def port_libre():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


# =========================================================================
# A. le fichier
# =========================================================================
print('\nA. donnees')
with open(os.path.join(DEMO, 'catalogue.json'), encoding='utf-8') as f:
    D = json.load(f)
FI = D['fiches']

t('210 fiches', len(FI) == 210, str(len(FI)))
t('21 categories', len(D['categories']) == 21, str(len(D['categories'])))
t('22 pays', len(D['pays']) == 22, str(len(D['pays'])))
t('5 regions', len(D['regions']) == 5, str(len(D['regions'])))
t('les 3 marches demandes sont couverts',
  {'CA', 'US'}.issubset(set(p['cle'] for p in D['pays'])) and
  len([p for p in D['pays'] if p['region'] != 'na']) >= 15)
t('identifiants uniques', len(set(f['id'] for f in FI)) == len(FI))
t('noms uniques', len(set(f['nom'] for f in FI)) == len(FI))

cats = set(c['cle'] for c in D['categories'])
t('toute fiche a une categorie connue', all(f['categorie'] in cats for f in FI))
t('la categorie « concessionnaires automobiles » existe', 'concession-auto' in cats)
t('la categorie « duty free » existe', 'duty-free' in cats)
manquantes = [c for c in cats if not any(f['categorie'] == c for f in FI)]
t('aucune categorie vide', not manquantes, str(manquantes))
t('10 fiches duty free',
  len([f for f in FI if f['categorie'] == 'duty-free']) == 10,
  str(len([f for f in FI if f['categorie'] == 'duty-free'])))

# Invariants d'argent. Un candidat lit ces montants pour decider s'il peut se
# le permettre : une fiche ou l'apport exige depasse le cout du projet ne veut
# rien dire.
mauvais = [f['nom'] for f in FI if f['liquidites'] > f['investissement']['bas']]
t('liquidites exigees <= investissement bas', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['investissement']['haut'] <= f['investissement']['bas']]
t('fourchette d investissement croissante', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['avoir_net'] < f['liquidites']]
t('avoir net >= liquidites', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['annee_franchisage'] < f['annee_creation']]
t('on ne franchise pas avant d exister', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI
           if f['unites_franchisees'] + f['unites_corpo'] != f['unites']]
t('franchisees + succursales = total', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['unites_franchisees'] < 1]
t('au moins une unite franchisee par enseigne', not mauvais, str(mauvais[:3]))

# Pays et devises.
pays = dict((p['cle'], p) for p in D['pays'])
mauvais = [f['nom'] for f in FI if f['pays_origine'] not in pays]
t('aucun pays d origine inconnu', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if any(p not in pays for p in f['pays'])]
t('aucun code pays inconnu dans le recrutement', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['pays_origine'] not in f['pays']]
t('le pays d origine est toujours ouvert au recrutement', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['devise'] != pays[f['pays_origine']]['devise']]
t('la devise annoncee est celle du pays d origine', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI if f['region'] != pays[f['pays_origine']]['region']]
t('la region correspond au pays d origine', not mauvais, str(mauvais[:3]))

# Aucun pays ne doit etre satisfait par TOUTES les fiches : un filtre que
# tout le monde satisfait ne filtre rien, et c'est exactement le defaut qui
# etait passe au vert la fois precedente.
couverture = {}
for f in FI:
    for p in f['pays']:
        couverture[p] = couverture.get(p, 0) + 1
t('aucun pays n est ouvert par 100 %% des fiches (max %d/%d)'
  % (max(couverture.values()), len(FI)),
  max(couverture.values()) < len(FI))
t('chaque pays a au moins une enseigne', len(couverture) == len(D['pays']),
  '%d pays couverts' % len(couverture))

# La tranche est derivee de la valeur de reference en euros. Si elle ment, le
# filtre le plus utilise de l'annuaire ment.
def tranche_de(v):
    for tr in D['tranches']:
        if tr['bas'] <= v < tr['haut']:
            return tr['cle']
    return None
mauvais = [f['nom'] for f in FI
           if f['investissement']['tranche'] != tranche_de(f['investissement']['eur_bas'])]
t('la tranche correspond a la valeur de reference en euros', not mauvais, str(mauvais[:3]))
# Et le classement multi-devises n'a de sens que si eur_bas suit le montant
# local : deux fiches de la meme devise doivent s'ordonner pareil.
paires = [(a, b) for a in FI for b in FI
          if a['devise'] == b['devise'] and a['id'] < b['id']]
mauvais = [(a['nom'], b['nom']) for a, b in paires[:4000]
           if (a['investissement']['bas'] < b['investissement']['bas']) !=
              (a['investissement']['eur_bas'] < b['investissement']['eur_bas'])
           and a['investissement']['bas'] != b['investissement']['bas']]
t('a devise egale, le classement local et le classement en euros coincident',
  not mauvais, str(mauvais[:2]))

fmts = set(x['cle'] for x in D['formats'])
mauvais = [f['nom'] for f in FI if f['format'] not in fmts]
t('aucun format inconnu', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI
           if f['categorie'] == 'concession-auto' and f['format'] in ('domicile', 'mobile')]
t('aucune concession automobile « a domicile » ou « mobile »', not mauvais, str(mauvais[:3]))
# Une boutique hors taxes est dans une aerogare ou a un poste frontalier.
mauvais = [f['nom'] for f in FI
           if f['categorie'] == 'duty-free' and f['format'] in ('domicile', 'mobile')]
t('aucune boutique hors taxes « a domicile » ou « mobile »', not mauvais, str(mauvais[:3]))

t('tout est marque comme demonstration', all(f.get('demonstration') for f in FI))
t('l avertissement est dans le fichier', 'fictives' in D['avertissement'].lower())
t('la note sur les taux de reference est presente', 'euros' in D['note_taux'].lower())
t('les libelles sont bilingues',
  all(c.get('fr') and c.get('en') for c in D['categories']) and
  all(p.get('fr') and p.get('en') for p in D['pays']) and
  all(f['resume'].get('fr') and f['resume'].get('en') for f in FI))

import donnees
# La table des pays d'origine europeens doit couvrir TOUTES les enseignes
# europeennes : une entree oubliee retomberait sur un tirage aleatoire, en
# silence, et c'est exactement ce qui donnait « fish and chips — Pologne ».
sans = [n for c in donnees.ENSEIGNES for (n, _f, _e, r) in donnees.ENSEIGNES[c]
        if r == 'eu' and n not in donnees.ORIGINE_EU]
t('chaque enseigne europeenne a un pays d origine ecrit', not sans, str(sans[:3]))
inutiles = [n for n in donnees.ORIGINE_EU
            if not any(n == x[0] for c in donnees.ENSEIGNES for x in donnees.ENSEIGNES[c])]
t('aucune entree orpheline dans la table des origines', not inutiles, str(inutiles[:3]))

refait = donnees.construire()
t('regeneration deterministe',
  json.dumps(refait, sort_keys=True) == json.dumps(FI, sort_keys=True))


# =========================================================================
# B. le moteur dans un navigateur
# =========================================================================
print('\nB. moteur (navigateur reel)')
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('  playwright absent, partie B non executee')
    print('\n%d ok, %d echecs' % (ok[0], ko[0]))
    sys.exit(1 if ko[0] else 0)

port = port_libre()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '-b', '127.0.0.1'],
                       cwd=DEMO, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
base = 'http://127.0.0.1:%d/' % port
try:
    import urllib.request
    pret = False
    for _ in range(80):
        try:
            b = urllib.request.urlopen(base, timeout=2).read().decode('utf-8', 'replace')
            # Un 200 ne prouve pas l'identite : on cherche une chaine que SEULE
            # cette page emet.
            if 'Annuaire des franchises' in b and 'Etats-Unis' in b:
                pret = True
                break
        except Exception:
            pass
        time.sleep(0.25)
    if not pret:
        print('  ECHEC le serveur de test n a pas repondu sur le port %d' % port)
        sys.exit(1)

    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={'width': 1280, 'height': 800})
        erreurs = []
        pg.on('pageerror', lambda e: erreurs.append(str(e)))
        pg.on('console', lambda m: erreurs.append(m.text) if m.type == 'error' else None)
        pg.goto(base, wait_until='networkidle')
        pg.wait_for_selector('.fiche')

        def cartes():
            return pg.locator('.fiche').count()

        def total():
            return int(re.sub(r'\D', '', pg.locator('#cpt b').inner_text()))

        def decoche_tout():
            pg.click('#raz')
            pg.wait_for_timeout(200)

        t('aucune erreur JavaScript au chargement', not erreurs, str(erreurs[:2]))
        t('le compteur annonce 210 enseignes', total() == 210, str(total()))
        t('la premiere page en montre 12', cartes() == 12, str(cartes()))
        t('la banniere de demonstration est visible',
          'fictives' in pg.locator('.demo').inner_text().lower())
        bandeau = pg.locator('#marches').inner_text()
        t('le bandeau annonce 22 pays et 21 categories',
          '22' in bandeau and '21' in bandeau, bandeau.replace('\n', ' '))

        # --- categorie
        pg.locator('#filtres input[value="duty-free"]').check()
        pg.wait_for_timeout(200)
        t('filtre duty free : 10 enseignes', total() == 10, str(total()))
        decoche_tout()
        t('effacer les filtres restitue les 210', total() == 210, str(total()))

        # --- region
        pg.locator('#filtres input[value="na"]').check()
        pg.wait_for_timeout(200)
        na = total()
        t('filtre region Amerique du Nord : sous-ensemble strict', 0 < na < 210, str(na))
        decoche_tout()

        # --- pays, et le compteur doit PREDIRE un sous-ensemble strict
        lab = pg.locator('#filtres label', has=pg.locator('input[value="DE"]')).first
        n_de = int(lab.locator('span.n').inner_text())
        pg.locator('#filtres input[value="DE"]').check()
        pg.wait_for_timeout(200)
        t('le compteur du pays Allemagne predit un sous-ensemble strict (%d)' % n_de,
          total() == n_de and 0 < n_de < 210, '%d vs %d' % (total(), n_de))
        decoche_tout()

        # --- multi-devises : une fiche polonaise ne s affiche pas en dollars
        pg.fill('#q', 'CodeKids')
        pg.wait_for_timeout(250)
        t('la recherche par nom trouve une enseigne', total() >= 1, str(total()))
        pg.fill('#q', '')
        pg.wait_for_timeout(200)

        # Chaque carte doit afficher un symbole/code de devise coherent avec la
        # fiche : c'est le point ou un annuaire multi-pays se casse en silence.
        devises = pg.evaluate("""() => {
          const out = [];
          document.querySelectorAll('.fiche').forEach(c => {
            const id = c.dataset.id;
            const dd = c.querySelector('dl dd');
            out.push([id, dd ? dd.textContent : '']);
          });
          return out;
        }""")
        par_id = dict((f['id'], f) for f in FI)
        SYM = {'EUR': '€', 'GBP': '£', 'USD': '$', 'CAD': '$', 'CHF': 'CHF',
               'PLN': 'PLN', 'SEK': 'SEK', 'DKK': 'DKK', 'NOK': 'NOK',
               'CZK': 'CZK', 'RON': 'RON', 'HUF': 'HUF'}
        faux = []
        for ident, txt in devises:
            f = par_id.get(ident)
            if not f:
                faux.append((ident, 'inconnue'))
                continue
            marque = SYM[f['devise']]
            # Intl peut ecrire « zl », « PLN », « kr » selon la locale ; on
            # accepte le code OU le symbole, mais pas une autre devise.
            if marque not in txt and f['devise'] not in txt and \
               not (f['devise'] in ('SEK', 'DKK', 'NOK') and 'kr' in txt) and \
               not (f['devise'] == 'PLN' and 'z' in txt) and \
               not (f['devise'] == 'CZK' and 'K' in txt) and \
               not (f['devise'] == 'HUF' and 'Ft' in txt):
                faux.append((ident, f['devise'], txt))
        t('chaque carte affiche sa propre devise', not faux, str(faux[:3]))

        # --- tri par investissement : il doit se faire sur la valeur de
        #     reference, pas sur le nombre affiche.
        pg.select_option('#tri', 'inv-desc')
        pg.wait_for_timeout(250)
        premiers = pg.evaluate(
            "() => [...document.querySelectorAll('.fiche')].slice(0,5)"
            ".map(c => c.dataset.id)")
        eur = [par_id[i]['investissement']['eur_bas'] for i in premiers]
        t('le tri decroissant classe bien sur la valeur de reference',
          eur == sorted(eur, reverse=True), str(eur))
        # Le piege : une devise faible produit de gros nombres. Si le tri se
        # faisait sur le montant affiche, le forint et la couronne trusteraient
        # la tete de liste.
        t('le sommet du tri n est pas monopolise par les devises faibles',
          not all(par_id[i]['devise'] in ('HUF', 'CZK', 'SEK', 'NOK', 'DKK')
                  for i in premiers),
          str([par_id[i]['devise'] for i in premiers]))
        pg.select_option('#tri', 'pertinence')
        pg.wait_for_timeout(200)

        # --- recherche
        pg.fill('#q', 'renovation')
        pg.wait_for_timeout(250)
        n1 = total()
        pg.fill('#q', 'Rénovation')
        pg.wait_for_timeout(250)
        t('la recherche ignore les accents et la casse', total() == n1 and n1 > 0,
          '%d vs %d' % (n1, total()))
        pg.fill('#q', 'zzzzzz')
        pg.wait_for_timeout(250)
        t('une recherche sans resultat affiche le message vide',
          pg.locator('.vide').count() == 1 and total() == 0)
        pg.fill('#q', '')
        pg.wait_for_timeout(250)

        # --- pagination
        avant = cartes()
        pg.click('#plus')
        pg.wait_for_timeout(200)
        t('« voir plus » ajoute des cartes', cartes() > avant,
          '%d -> %d' % (avant, cartes()))

        # --- panneau categories
        pg.click('a[data-nav="cats"]')
        pg.wait_for_timeout(300)
        t('le panneau des categories liste les 21',
          pg.locator('.cats-liste button').count() == 21,
          str(pg.locator('.cats-liste button').count()))
        pg.locator('.cats-liste button[data-chip="hotellerie"]').click()
        pg.wait_for_timeout(300)
        t('cliquer une categorie ferme le panneau et filtre',
          pg.locator('#panneau.on').count() == 0 and total() == 10, str(total()))
        decoche_tout()

        # --- fiche + demande d information (le produit)
        pg.locator('.fiche .cta').first.click()
        pg.wait_for_timeout(300)
        t('le panneau de fiche s ouvre', pg.locator('#panneau.on').count() == 1)
        txt = pg.locator('#panneau').inner_text().lower()
        t('la fiche montre le pays d origine et le droit d entree',
          'origine' in txt and 'entree' in txt)
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        t('la demande refuse un envoi vide', pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_nom', 'Jean Tremblay')
        pg.fill('#c_mail', 'jean@exemple')     # domaine sans point : injoignable
        pg.select_option('#c_pays', index=1)
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        t('la demande refuse une adresse sans domaine complet',
          pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_mail', 'jean@exemple.ca')
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        t('une demande complete est acceptee', pg.locator('#c_res .ok').count() == 1)
        t('la confirmation dit que rien n a ete envoye',
          'demonstration' in pg.locator('#c_res .ok').inner_text().lower())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(250)

        # --- inscription d une enseigne (c est ce qui fait grandir l annuaire)
        pg.click('a[data-nav="inscrire"]')
        pg.wait_for_timeout(300)
        t('le formulaire d inscription s ouvre', pg.locator('#i_env').count() == 1)
        pg.click('#i_env')
        pg.wait_for_timeout(200)
        t('l inscription refuse un envoi vide', pg.locator('#i_res .msg-err').count() == 1)
        pg.fill('#i_nom', 'Enseigne Essai')
        pg.select_option('#i_cat', index=1)
        pg.select_option('#i_pays', index=1)
        pg.fill('#i_contact', 'Marie Dubois')
        pg.fill('#i_mail', 'marie@exemple.ca')
        pg.fill('#i_bas', '300000')
        pg.fill('#i_haut', '120000')           # fourchette inversee
        pg.click('#i_env')
        pg.wait_for_timeout(200)
        t('l inscription refuse une fourchette inversee',
          pg.locator('#i_res .msg-err').count() == 1)
        pg.fill('#i_haut', '600000')
        pg.click('#i_env')
        pg.wait_for_timeout(200)
        t('une inscription complete est acceptee', pg.locator('#i_res .ok').count() == 1)
        t('la confirmation d inscription dit que rien n a ete enregistre',
          'demonstration' in pg.locator('#i_res .ok').inner_text().lower())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(250)

        # --- comparateur
        for i in range(3):
            pg.locator('.fiche .cmp').nth(i).click()
            pg.wait_for_timeout(80)
        t('la barre de comparaison apparait', pg.locator('#barcmp.on').count() == 1)
        pg.once('dialog', lambda d: d.accept())
        pg.locator('.fiche .cmp').nth(3).click()
        pg.wait_for_timeout(200)
        t('la comparaison est plafonnee a 3',
          pg.locator('#barcmp .pastille').count() == 3,
          str(pg.locator('#barcmp .pastille').count()))
        pg.click('#cmpgo')
        pg.wait_for_timeout(300)
        t('le tableau comparatif s ouvre avec 3 colonnes',
          pg.locator('.cmp-tbl th').count() == 4,
          str(pg.locator('.cmp-tbl th').count()))
        t('le comparatif montre le pays d origine',
          'origine' in pg.locator('.cmp-tbl').inner_text().lower())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(200)

        # --- bilingue
        pg.click('.lang button[data-l="en"]')
        pg.wait_for_timeout(300)
        h1 = pg.locator('#h1').inner_text()
        t('le basculement anglais change le titre',
          'franchise' in h1.lower() and 'country' in h1.lower(), h1)
        txt = pg.locator('#filtres').inner_text().lower()
        t('les filtres passent en anglais',
          'category' in txt and 'country' in txt and 'duty free' in txt, txt[:80])
        t('le menu passe en anglais',
          'List your brand' in pg.locator('header nav').inner_text())
        pg.click('.lang button[data-l="fr"]')
        pg.wait_for_timeout(300)
        m = pg.locator('.fiche dd').first.inner_text().strip()
        t('aucune espace secable a l interieur d un montant',
          not re.search(r'\d \d', m), repr(m))

        t('aucune erreur JavaScript sur tout le parcours', not erreurs, str(erreurs[:3]))

        # --- mobile
        pg.set_viewport_size({'width': 390, 'height': 780})
        pg.wait_for_timeout(300)
        deborde = pg.evaluate(
            'document.documentElement.scrollWidth > document.documentElement.clientWidth + 1')
        t('aucun debordement horizontal en 390 px', not deborde)

        nav.close()
finally:
    srv.terminate()

print('\n%d ok, %d echecs' % (ok[0], ko[0]))
sys.exit(1 if ko[0] else 0)
