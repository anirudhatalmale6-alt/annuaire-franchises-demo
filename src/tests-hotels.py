# -*- coding: utf-8 -*-
"""Controles de la section hotellerie.

D'abord les donnees — c'est la que se joue la credibilite d'une fiche
hoteliere : le cout du projet doit etre le produit de l'investissement a la
cle par la taille acceptee, les deux redevances doivent s'additionner a ce
qui est affiche, un hotel economique ne doit pas proposer un contrat de
gestion, et le nombre de cles du reseau doit etre coherent avec le nombre
d'hotels.

Ensuite la page, dans un vrai navigateur : les compteurs des filtres doivent
PREDIRE le resultat, le filtre doit rendre un sous-ensemble strict, et le
cout du projet affiche dans la fiche doit etre celui qu'on recalcule a partir
du JSON.
"""

import http.server
import json
import os
import re
import socket
import subprocess
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
sys.path.insert(0, ICI)

from hotels import (SEGMENTS, CONTRATS_PAR_SEGMENT, DUREE,  # noqa: E402
                    GROUPES, construire, tranche_cle)

OK = []


def t(nom, cond, detail=''):
    OK.append(bool(cond))
    print('%s %s%s' % ('  ok  ' if cond else ' ECHEC', nom,
                       ('   -> ' + str(detail)) if not cond and detail else ''))


# On regenere avant de controler : un controle qui lit un fichier vieux de
# trois modifications valide un livrable qui n'existe plus.
subprocess.run([sys.executable, os.path.join(ICI, 'hotels.py')],
               check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, os.path.join(ICI, 'page_hotels.py')],
               check=True, stdout=subprocess.DEVNULL)

DEMO = dossier_pages(ICI)
D = json.load(open(os.path.join(DEMO, 'hotellerie.json'), encoding='utf-8'))
FI = D['fiches']
SEG = dict((s[0], s) for s in SEGMENTS)

print('\n--- les donnees se tiennent, fiche par fiche ---')

t('la section contient des fiches', len(FI) > 0, len(FI))
t('%d marques pour %d groupes' % (len(FI), len(D['groupes'])),
  len(FI) == sum(len(ms) for _p, ms in GROUPES.values())
  and len(D['groupes']) == len(GROUPES))
t('les identifiants sont uniques', len({f['id'] for f in FI}) == len(FI))
t('les %d segments sont tous representes' % len(SEGMENTS),
  all(any(f['segment'] == s[0] for f in FI) for s in SEGMENTS),
  [s[0] for s in SEGMENTS if not any(f['segment'] == s[0] for f in FI)])

# Un groupe hotelier ne porte pas deux marques dans le meme segment : c'est
# ainsi que sont batis les portefeuilles de marques, et deux marques du meme
# groupe sur le meme creneau se cannibalisent.
par_groupe = {}
for f in FI:
    par_groupe.setdefault(f['groupe'], []).append(f['segment'])
collision = {g: s for g, s in par_groupe.items() if len(s) != len(set(s))}
t('aucun groupe ne porte deux marques dans le meme segment',
  not collision, collision)
t('chaque groupe declare porte au moins une marque',
  all(g in par_groupe for g in GROUPES), sorted(set(GROUPES) - set(par_groupe)))

hors_taille = [(f['id'], f['cles']) for f in FI
               if not (SEG[f['segment']][5] <= f['cles']['min']
                       < f['cles']['max'] <= SEG[f['segment']][6])]
t('la taille acceptee tient dans la bande de son segment, min < max',
  not hors_taille, hors_taille[:3])

hors_inv = [(f['id'], f['investissement_cle']['eur_bas']) for f in FI
            if not (SEG[f['segment']][3] <= f['investissement_cle']['eur_bas']
                    <= SEG[f['segment']][4])]
t('l\'investissement a la cle tient dans la bande de son segment',
  not hors_inv, hors_inv[:3])

# LE controle central. Un cout de projet tire a part finit toujours par
# contredire le prix a la cle affiche juste au-dessus, et c'est le chiffre
# sur lequel un investisseur decide.
faux = [(f['id'], f['projet'],
         f['investissement_cle']['bas'] * f['cles']['min'],
         f['investissement_cle']['haut'] * f['cles']['max'])
        for f in FI
        if f['projet']['bas'] != f['investissement_cle']['bas'] * f['cles']['min']
        or f['projet']['haut'] != f['investissement_cle']['haut'] * f['cles']['max']]
t('le cout du projet est le PRODUIT investissement/cle x taille acceptee',
  not faux, faux[:2])

mauvais = [(f['id'], f['redevances']) for f in FI
           if abs(f['redevances']['total']
                  - (f['redevances']['marque']
                     + f['redevances']['commercialisation'])) > 0.051]
t('le total des redevances est bien la somme des deux', not mauvais,
  mauvais[:3])
t('aucun total de redevances au-dela de 12 %',
  all(f['redevances']['total'] <= 12 for f in FI),
  max(f['redevances']['total'] for f in FI))

# Un contrat de gestion sur un economique de 70 chambres n'existe pas : les
# honoraires ne paieraient pas l'equipe du groupe.
illegaux = [(f['id'], f['segment'], c) for f in FI for c in f['contrats']
            if c not in CONTRATS_PAR_SEGMENT[f['segment']]]
t('aucun type de contrat impossible pour son segment', not illegaux,
  illegaux[:3])
t('aucune enseigne economique ne propose un contrat de gestion',
  not [f['id'] for f in FI
       if f['segment'] == 'economique' and 'gestion' in f['contrats']])
# Le segment « luxe » est parti sur le site de prestige. Le controle porte
# donc sur son ABSENCE — laisser en place l'ancienne regle (« toute enseigne
# de luxe propose la gestion ») aurait donne un vert permanent : une
# assertion sur un ensemble vide est vraie et ne verifie rien.
t('le segment « luxe » a bien quitte cette section',
  'luxe' not in {s[0] for s in SEGMENTS}
  and not [f['id'] for f in FI if f['segment'] == 'luxe'])
# Le contrat de gestion n'apparait qu'a partir du milieu de gamme
# SUPERIEUR. Au-dessous, les honoraires ne paieraient pas l'equipe du
# groupe. Ce n'est PAS « toutes les enseignes haut de gamme le proposent » :
# le haut de gamme se franchise aussi, et souvent.
bas = [f['id'] for f in FI
       if f['segment'] in ('economique', 'milieu') and 'gestion' in f['contrats']]
t('aucune enseigne sous le milieu de gamme superieur ne propose la gestion',
  not bas, bas)
avec = [f['id'] for f in FI if 'gestion' in f['contrats']]
t('la gestion existe, sur une partie seulement du catalogue (%d/%d)'
  % (len(avec), len(FI)), 0 < len(avec) < len(FI), len(avec))

hors_duree = [(f['id'], f['contrats'][0], f['duree_contrat']) for f in FI
              if not (DUREE[f['contrats'][0]][0] <= f['duree_contrat']
                      <= DUREE[f['contrats'][0]][1])]
t('la duree du contrat tient dans la bande de son contrat principal',
  not hors_duree, hors_duree[:3])

t('on ne franchise jamais avant d\'avoir cree l\'enseigne',
  all(f['annee_franchisage'] >= f['annee_creation'] for f in FI))

# Tire a part, le nombre de cles du reseau donne des reseaux de 40 hotels et
# 900 cles — soit 22 chambres l'unite, ce qu'aucune de ces marques n'accepte.
incoh = [(f['id'], f['reseau']) for f in FI
         if f['reseau']['cles'] != f['reseau']['hotels'] * f['reseau']['taille_moyenne']
         or not (f['cles']['min'] <= f['reseau']['taille_moyenne'] <= f['cles']['max'])]
t('le reseau est coherent : cles = hotels x taille moyenne, dans la bande',
  not incoh, incoh[:2])

devise_de = dict((p['cle'], p['devise']) for p in D['pays'])
t('chaque fiche s\'affiche dans la devise de son pays d\'origine',
  all(f['devise'] == devise_de[f['pays_origine']] for f in FI))
t('le pays d\'origine fait toujours partie des pays ouverts',
  all(f['pays_origine'] in f['pays'] for f in FI))
t('la tranche affichee est celle que la valeur de reference commande',
  all(f['investissement_cle']['tranche']
      == tranche_cle(f['investissement_cle']['eur_bas']) for f in FI))

t('le droit d\'entree a bien ses deux composantes, toutes deux positives',
  all(f['droit_entree']['par_cle'] > 0 and f['droit_entree']['plancher'] > 0
      for f in FI))
# Un plancher qui ne s'applique jamais est un champ decoratif.
mordu = [f['id'] for f in FI
         if f['droit_entree']['plancher']
         > f['droit_entree']['par_cle'] * f['cles']['min']]
t('le plancher du droit d\'entree mord vraiment sur au moins une fiche',
  len(mordu) > 0, len(mordu))

# Un filtre que toutes les fiches satisfont ne filtre rien.
n_conv = sum(1 for f in FI if f['conversion'])
t('la conversion partage vraiment le catalogue', 0 < n_conv < len(FI),
  '%d/%d' % (n_conv, len(FI)))
occupees = {f['investissement_cle']['tranche'] for f in FI}
t('les tranches par cle ne sont pas toutes dans le meme panier',
  len(occupees) >= 3, sorted(occupees))

# Deterministe : les captures et les controles doivent parler du meme jeu.
t('deux reconstructions donnent le meme fichier, au caractere pres',
  json.dumps(construire(), sort_keys=True)
  == json.dumps(construire(), sort_keys=True))

print('\n--- les deux pages partagent une seule feuille de style ---')

idx = open(os.path.join(DEMO, 'index.html'), encoding='utf-8').read()
hot = open(os.path.join(DEMO, 'hotellerie.html'), encoding='utf-8').read()
css_idx = re.search(r'<style>\n(.*?)\n</style>', idx, re.S).group(1)
t('le bloc de style de l\'annuaire se retrouve tel quel dans l\'hotellerie',
  css_idx in hot, len(css_idx))
t('l\'annuaire renvoie vers la section hotellerie',
  'hotellerie.html' in idx)
t('la section renvoie vers l\'annuaire generaliste', 'index.html' in hot)
t('les deux pages restent hors des moteurs le temps de la demonstration',
  'noindex' in hot)

print('\n--- la page, dans un vrai navigateur ---')


def port_libre():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Muet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    from playwright.sync_api import sync_playwright

    port = port_libre()
    srv = http.server.ThreadingHTTPServer(
        ('127.0.0.1', port), lambda *a, **k: Muet(*a, directory=DEMO, **k))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = 'http://127.0.0.1:%d/' % port

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        pg = nav.new_page(viewport={'width': 1280, 'height': 900})
        erreurs = []
        pg.on('pageerror', lambda e: erreurs.append(str(e)))
        pg.on('console',
              lambda m: erreurs.append(m.text) if m.type == 'error' else None)
        pg.goto(base + 'hotellerie.html', wait_until='networkidle')
        pg.wait_for_selector('.fiche', timeout=10000)

        def total():
            txt = pg.locator('#cpt').inner_text()
            return int(re.sub(r'[^\d]', '', txt.split('sur')[0]
                              .split('of')[0]))

        def cartes():
            return pg.locator('.fiche').count()

        t('la grille se remplit', cartes() > 0, cartes())
        t('le compteur annonce le sous-ensemble ET le total',
          str(len(FI)) in pg.locator('#cpt').inner_text()
          and ('sur' in pg.locator('#cpt').inner_text()),
          pg.locator('#cpt').inner_text())
        t('le compteur part bien du catalogue entier', total() == len(FI),
          total())

        avant = cartes()
        pg.click('#plus')
        pg.wait_for_timeout(200)
        t('« voir plus » ajoute des cartes', cartes() > avant,
          '%d -> %d' % (avant, cartes()))

        # Le compteur a cote d'une case doit PREDIRE le resultat du clic.
        # Calcule sur le resultat final il afficherait 0 partout : exact, et
        # parfaitement inutile.
        case = pg.locator('.fgrp input[data-g="segs"][data-v="haut"]')
        annonce = int(case.locator('xpath=../span[@class="n"]').inner_text())
        case.check()
        pg.wait_for_timeout(250)
        attendu = sum(1 for f in FI if f['segment'] == 'haut')
        t('le compteur du segment « haut de gamme » predisait le resultat (%d)'
          % attendu,
          annonce == attendu == total(),
          'annonce %d, obtenu %d, attendu %d' % (annonce, total(), attendu))
        t('filtrer sur un segment rend un sous-ensemble STRICT',
          0 < total() < len(FI), total())
        pg.click('#raz')
        pg.wait_for_timeout(250)
        t('effacer les filtres restitue le catalogue entier',
          total() == len(FI), total())

        # La taille : « mon hotel fait N cles, qui le prend ». N doit tomber
        # DANS la fourchette, pas au-dessus d'un minimum.
        n_test = D['tailles'][2]
        pg.select_option('#taille', str(n_test))
        pg.wait_for_timeout(250)
        att = sum(1 for f in FI
                  if f['cles']['min'] <= n_test <= f['cles']['max'])
        t('le filtre taille (%d cles) rend exactement les enseignes qui '
          'acceptent cette taille (%d)' % (n_test, att),
          total() == att, total())
        t('le filtre taille est un sous-ensemble strict', 0 < att < len(FI), att)
        pg.click('#raz')
        pg.wait_for_timeout(250)

        pg.locator('.fgrp input[data-g="contrats"][data-v="gestion"]').check()
        pg.wait_for_timeout(250)
        att_g = sum(1 for f in FI if 'gestion' in f['contrats'])
        t('le filtre « contrat de gestion » rend les %d enseignes concernees'
          % att_g, total() == att_g, total())
        seg_vus = pg.locator('.fiche .seg').all_inner_texts()
        t('aucune enseigne economique dans les contrats de gestion',
          all('conomique' not in s for s in seg_vus), seg_vus[:4])
        pg.click('#raz')
        pg.wait_for_timeout(250)

        # Le tri se fait sur la valeur de reference en euros : lire les
        # montants affiches ne prouverait rien, ils sont dans 12 devises.
        pg.select_option('#tri', 'ic')
        pg.wait_for_timeout(250)
        noms = pg.locator('.fiche h2').all_inner_texts()
        attendu_noms = [f['nom'] for f in sorted(
            FI, key=lambda f: f['investissement_cle']['eur_bas'])][:len(noms)]
        t('le tri par investissement a la cle suit la valeur de reference',
          noms == attendu_noms, list(zip(noms, attendu_noms))[:3])
        pg.select_option('#tri', 'p')
        pg.wait_for_timeout(250)

        # La fiche : le cout du projet affiche doit etre celui qu'on
        # recalcule, sinon la page raconte autre chose que ses donnees.
        pg.locator('.fiche .cta').first.click()
        pg.wait_for_timeout(300)
        t('le panneau de fiche s\'ouvre',
          pg.locator('#panneau.on').count() == 1)
        titre = pg.locator('#panneau h2').inner_text()
        f0 = [f for f in FI if f['nom'] == titre][0]
        corps = pg.locator('#panneau').inner_text()
        chiffres = re.sub(r'[^\d]', ' ', corps).split()
        t('la fiche affiche le cout du projet calcule (%s)'
          % f0['projet']['bas'],
          str(f0['projet']['bas']) in ''.join(
              re.sub(r'[^\d]', '', corps)),
          str(f0['projet']['bas']))
        t('la fiche nomme les deux redevances separement',
          'edevance' in corps or 'fee' in corps.lower())
        t('la fiche dit d\'ou vient le cout du projet',
          'multiplie par' in corps or 'multiplied by' in corps)
        t('la fiche annonce la taille acceptee', str(f0['cles']['min'])
          in ''.join(re.sub(r'[^\d]', '', corps)), f0['cles']['min'])
        # « 1986 » affiche « 1 986 » : nb() traitait une annee comme un
        # montant. Quatre chiffres colles, pas un separateur de milliers.
        annees = re.findall(r'\b1\s9\d\d\b|\b2\s0\d\d\b', corps)
        t('les annees s\'ecrivent sans separateur de milliers',
          not annees and str(f0['annee_creation']) in corps, annees[:3])

        t('le formulaire de la fiche est bien une demonstration',
          'monstration' in corps or 'emonstration' in corps.lower())

        # Un formulaire qui accepte n'importe quoi n'est pas un formulaire.
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        t('le formulaire refuse les champs obligatoires vides',
          pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_nom', 'Test')
        pg.fill('#c_mail', 'pas-une-adresse')
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        t('le formulaire refuse une adresse invalide',
          pg.locator('#c_res .msg-err').count() == 1)
        pg.fill('#c_mail', 'client@exemple.com')
        pg.click('#c_env')
        pg.wait_for_timeout(200)
        ok_txt = pg.locator('#c_res .ok').inner_text()
        t('l\'accuse de reception dit que RIEN n\'a ete envoye',
          'rien' in ok_txt.lower() or 'nothing' in ok_txt.lower(), ok_txt)
        pg.click('#voile')
        pg.wait_for_timeout(250)

        # Les montants ne doivent pas se couper en fin de ligne.
        txt = pg.locator('body').inner_text()
        coupes = re.findall(r'\d \d{3}(?!\d)', txt)
        t('aucune espace secable a l\'interieur d\'un montant',
          not coupes, coupes[:4])

        print('\n--- anglais ---')
        cles = pg.evaluate("()=>[Object.keys(T.fr).sort().join(','),"
                           "Object.keys(T.en).sort().join(',')]")
        t('les deux langues portent exactement les memes cles',
          cles[0] == cles[1],
          set(cles[0].split(',')) ^ set(cles[1].split(',')))
        pg.click('.lang button[data-l="en"]')
        pg.wait_for_timeout(300)
        t('le titre passe en anglais',
          'Hotel franchises' in pg.locator('#h-titre').inner_text(),
          pg.locator('#h-titre').inner_text())
        # inner_text rend le texte APRES text-transform : les titres de
        # filtre sortent en capitales. Et « Segment » s'ecrit pareil dans les
        # deux langues — le controle passait au vert sans rien prouver. On
        # prend un libelle qui change vraiment.
        titres = ' | '.join(pg.locator('.fgrp h3').all_inner_texts()).upper()
        t('les filtres passent en anglais',
          'MY HOTEL SIZE' in titres and 'TAILLE DE MON HOTEL' not in titres,
          titres)
        t('le compteur passe en anglais',
          ' of ' in pg.locator('#cpt').inner_text(),
          pg.locator('#cpt').inner_text())
        pg.click('.lang button[data-l="fr"]')
        pg.wait_for_timeout(250)

        pg.set_viewport_size({'width': 390, 'height': 800})
        pg.wait_for_timeout(300)
        deborde = pg.evaluate("()=>document.documentElement.scrollWidth>"
                              "document.documentElement.clientWidth+1")
        t('aucun debordement horizontal en 390 px', not deborde)
        pg.set_viewport_size({'width': 1280, 'height': 900})

        t('aucune erreur JavaScript sur tout le parcours', not erreurs,
          erreurs[:3])

        # Le lien depuis l'annuaire generaliste doit VRAIMENT mener ici.
        pg.goto(base + 'index.html', wait_until='networkidle')
        pg.wait_for_timeout(400)
        lien = pg.locator('header nav a#nv4')
        t('le lien « Hotellerie » de l\'annuaire est visible et libelle',
          lien.count() == 1 and lien.inner_text().strip() != '',
          lien.inner_text() if lien.count() else 'absent')
        lien.click()
        pg.wait_for_selector('.fiche', timeout=10000)
        t('le lien mene bien a la section hotellerie',
          'hotellerie.html' in pg.url and pg.locator('.fiche').count() > 0,
          pg.url)

        nav.close()
    srv.shutdown()

    print('\n%d controles, %d verts, %d rouges'
          % (len(OK), sum(OK), len(OK) - sum(OK)))
    sys.exit(0 if all(OK) else 1)


if __name__ == '__main__':
    main()
