# -*- coding: utf-8 -*-
"""Controles de l'annuaire de franchises.

Deux familles, et la seconde est la seule qui prouve quoi que ce soit :

  A. le fichier de donnees — coherence des montants, des annees, des unites.
     Pas de reseau, pas de navigateur.
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

t('100 fiches', len(FI) == 100, str(len(FI)))
t('20 categories', len(D['categories']) == 20, str(len(D['categories'])))
t('13 provinces et territoires', len(D['provinces']) == 13, str(len(D['provinces'])))
t('identifiants uniques', len(set(f['id'] for f in FI)) == len(FI))
t('noms uniques', len(set(f['nom'] for f in FI)) == len(FI))

cats = set(c['cle'] for c in D['categories'])
t('toute fiche a une categorie connue', all(f['categorie'] in cats for f in FI))
t('la categorie « concessionnaires automobiles » existe', 'concession-auto' in cats)
manquantes = [c for c in cats if not any(f['categorie'] == c for f in FI)]
t('aucune categorie vide', not manquantes, str(manquantes))

# L'invariant qui compte : un candidat lit ces montants pour decider s'il peut
# se le permettre. Une fiche ou l'apport exige depasse le cout du projet est
# une fiche qui ne veut rien dire.
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
mauvais = [f['nom'] for f in FI if not f['provinces']]
t('toute fiche est ouverte dans au moins une province', not mauvais, str(mauvais[:3]))
provs = set(p['cle'] for p in D['provinces'])
mauvais = [f['nom'] for f in FI if any(p not in provs for p in f['provinces'])]
t('aucun code de province inconnu', not mauvais, str(mauvais[:3]))

# La tranche est un champ derive. S'il ment, le filtre « investissement »
# ment, et c'est le filtre le plus utilise d'un annuaire de franchises.
def tranche_de(v):
    for tr in D['tranches']:
        if tr['bas'] <= v < tr['haut']:
            return tr['cle']
    return None
mauvais = [f['nom'] for f in FI
           if f['investissement']['tranche'] != tranche_de(f['investissement']['bas'])]
t('la tranche correspond au montant', not mauvais, str(mauvais[:3]))

# Un format doit exister pour le metier. « Concession automobile a domicile »
# suffirait a faire fermer l'onglet.
fmts = set(x['cle'] for x in D['formats'])
mauvais = [f['nom'] for f in FI if f['format'] not in fmts]
t('aucun format inconnu', not mauvais, str(mauvais[:3]))
mauvais = [f['nom'] for f in FI
           if f['categorie'] == 'concession-auto' and f['format'] in ('domicile', 'mobile')]
t('aucune concession automobile « a domicile » ou « mobile »', not mauvais, str(mauvais[:3]))

t('tout est marque comme demonstration', all(f.get('demonstration') for f in FI))
t('l avertissement est dans le fichier', 'fictives' in D['avertissement'].lower())
t('les libelles sont bilingues',
  all(c.get('fr') and c.get('en') for c in D['categories']) and
  all(f['resume'].get('fr') and f['resume'].get('en') for f in FI))

# Deux executions doivent donner le meme fichier : une demo dont les chiffres
# bougent a chaque reconstruction ne peut pas etre comparee a une capture.
import donnees
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
            if 'Annuaire des franchises au Canada' in b:
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
            return int(pg.locator('#cpt b').inner_text().replace(' ', '')
                       .replace(' ', '').replace(' ', ''))

        t('aucune erreur JavaScript au chargement', not erreurs, str(erreurs[:2]))
        t('le compteur annonce 100 enseignes', total() == 100, str(total()))
        t('la premiere page en montre 12', cartes() == 12, str(cartes()))
        t('la banniere de demonstration est visible',
          'fictives' in pg.locator('.demo').inner_text().lower())

        # --- filtre categorie
        pg.locator('#filtres input[value="concession-auto"]').check()
        pg.wait_for_timeout(120)
        t('filtre categorie : 5 concessionnaires', total() == 5, str(total()))
        noms = pg.locator('.fiche h2').all_inner_texts()
        t('les cartes affichees sont bien les concessions', len(noms) == 5, str(noms))
        pg.locator('#filtres input[value="concession-auto"]').uncheck()
        pg.wait_for_timeout(120)
        t('decocher restitue les 100', total() == 100, str(total()))

        # --- le compteur d'une case ne se compte pas lui-meme
        lab = pg.locator('#filtres label', has=pg.locator('input[value="ON"]')).first
        n_on = int(lab.locator('span.n').inner_text())
        pg.locator('#filtres input[value="ON"]').check()
        pg.wait_for_timeout(120)
        # Le compteur doit PREDIRE, et sur un sous-ensemble STRICT : verifier
        # « 100 == 100 » quand toutes les fiches sont ouvertes en Ontario ne
        # prouve rien du tout.
        t('le compteur de la case Ontario predit un sous-ensemble strict (%d)' % n_on,
          total() == n_on and 0 < n_on < 100, '%d vs %d' % (total(), n_on))
        lab2 = pg.locator('#filtres label', has=pg.locator('input[value="QC"]')).first
        n_qc = int(lab2.locator('span.n').inner_text())
        t('le compteur du Quebec reste calcule hors de lui-meme', n_qc > 0, str(n_qc))
        pg.locator('#filtres input[value="ON"]').uncheck()
        pg.wait_for_timeout(120)

        # --- filtre investissement
        pg.locator('#filtres input[value="t5"]').check()
        pg.wait_for_timeout(120)
        gros = total()
        t('filtre « plus de 1 M$ » : sous-ensemble non vide', 0 < gros < 100, str(gros))
        pg.locator('#filtres input[value="t5"]').uncheck()
        pg.wait_for_timeout(120)

        # --- recherche, accents plies
        pg.fill('#q', 'renovation')
        pg.wait_for_timeout(200)
        n1 = total()
        pg.fill('#q', 'Rénovation')
        pg.wait_for_timeout(200)
        t('la recherche ignore les accents et la casse', total() == n1 and n1 > 0,
          '%d vs %d' % (n1, total()))
        pg.fill('#q', 'zzzzzz')
        pg.wait_for_timeout(200)
        t('une recherche sans resultat affiche le message vide',
          pg.locator('.vide').count() == 1 and total() == 0)
        pg.fill('#q', '')
        pg.wait_for_timeout(200)

        # --- tri
        pg.select_option('#tri', 'inv-asc')
        pg.wait_for_timeout(150)
        p1 = pg.locator('.fiche').first.inner_text()
        pg.select_option('#tri', 'inv-desc')
        pg.wait_for_timeout(150)
        p2 = pg.locator('.fiche').first.inner_text()
        t('le tri par investissement change la premiere carte', p1 != p2)
        pg.select_option('#tri', 'pertinence')
        pg.wait_for_timeout(150)

        # --- pagination
        avant = cartes()
        pg.click('#plus')
        pg.wait_for_timeout(150)
        t('« voir plus » ajoute des cartes', cartes() > avant,
          '%d -> %d' % (avant, cartes()))

        # --- fiche + formulaire (le produit)
        pg.locator('.fiche .cta').first.click()
        pg.wait_for_timeout(250)
        t('le panneau de fiche s ouvre', pg.locator('#panneau.on').count() == 1)
        t('la fiche montre le droit d entree',
          'entree' in pg.locator('#panneau').inner_text().lower() or
          'fee' in pg.locator('#panneau').inner_text().lower())
        pg.click('#c_env')
        pg.wait_for_timeout(150)
        t('le formulaire refuse un envoi vide',
          pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_nom', 'Jean Tremblay')
        pg.fill('#c_mail', 'jean@exemple')     # domaine sans point : injoignable
        pg.select_option('#c_prov', index=1)
        pg.click('#c_env')
        pg.wait_for_timeout(150)
        t('le formulaire refuse une adresse sans domaine complet',
          pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_mail', 'jean@exemple.ca')
        pg.click('#c_env')
        pg.wait_for_timeout(150)
        t('un envoi complet est accepte', pg.locator('#c_res .ok').count() == 1)
        t('la confirmation dit que rien n a ete envoye',
          'demonstration' in pg.locator('#c_res .ok').inner_text().lower())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(200)

        # --- comparateur
        for i in range(3):
            pg.locator('.fiche .cmp').nth(i).click()
            pg.wait_for_timeout(80)
        t('la barre de comparaison apparait a 3 enseignes',
          pg.locator('#barcmp.on').count() == 1)
        pg.once('dialog', lambda d: d.accept())
        pg.locator('.fiche .cmp').nth(3).click()
        pg.wait_for_timeout(150)
        t('la comparaison est plafonnee a 3',
          pg.locator('#barcmp .pastille').count() == 3,
          str(pg.locator('#barcmp .pastille').count()))
        pg.click('#cmpgo')
        pg.wait_for_timeout(250)
        t('le tableau comparatif s ouvre avec 3 colonnes',
          pg.locator('.cmp-tbl th').count() == 4,
          str(pg.locator('.cmp-tbl th').count()))
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(150)

        # --- bilingue
        pg.click('.lang button[data-l="en"]')
        pg.wait_for_timeout(250)
        h1 = pg.locator('#h1').inner_text()
        t('le basculement anglais change le titre', 'franchise' in h1.lower() and
          'budget' in h1.lower(), h1)
        txt = pg.locator('#filtres').inner_text()
        # inner_text rend le texte PEINT : « Categorie » est en petites
        # capitales par CSS, donc « CATEGORY ». Comparer sans tenir compte de
        # la casse, sinon on teste la feuille de style et pas la traduction.
        t('les filtres passent en anglais',
          'category' in txt.lower() and 'quick service' in txt.lower(), txt[:60])
        t('les montants passent au format anglais',
          pg.locator('.fiche dd').first.inner_text().strip().startswith('$'),
          pg.locator('.fiche dd').first.inner_text())
        pg.click('.lang button[data-l="fr"]')
        pg.wait_for_timeout(250)
        m = pg.locator('.fiche dd').first.inner_text().strip()
        t('les montants reviennent au format francais', m.endswith('$'), m)
        # Les separateurs de milliers doivent etre INSECABLES, sinon
        # « 605 000 $ » se coupe en fin de ligne et le prix devient illisible.
        t('aucune espace secable a l interieur d un montant',
          not re.search(r'\d \d', m), repr(m))

        t('aucune erreur JavaScript sur tout le parcours', not erreurs, str(erreurs[:3]))

        # --- mobile
        pg.set_viewport_size({'width': 390, 'height': 780})
        pg.wait_for_timeout(250)
        deborde = pg.evaluate(
            'document.documentElement.scrollWidth > document.documentElement.clientWidth + 1')
        t('aucun debordement horizontal en 390 px', not deborde)

        nav.close()
finally:
    srv.terminate()

print('\n%d ok, %d echecs' % (ok[0], ko[0]))
sys.exit(1 if ko[0] else 0)
