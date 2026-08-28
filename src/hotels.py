# -*- coding: utf-8 -*-
"""Section HOTELLERIE de l'annuaire de franchises.

Section a part, et pas une 21e categorie : une enseigne hoteliere ne se
compare pas a un commerce sur les memes colonnes.

  - on n'y investit pas « un montant », on investit AU NOMBRE DE CLES ;
  - on ne paie pas une redevance, on en paie DEUX : la marque d'un cote, la
    commercialisation et la fidelite de l'autre ;
  - le contrat n'est pas toujours une franchise : au-dela du milieu de gamme
    superieur, c'est souvent un contrat de gestion, ou un bail ;
  - une enseigne accepte des hotels d'une certaine TAILLE, et refuse les
    autres ;
  - et il y a un etage de plus qu'ailleurs : le GROUPE, qui porte plusieurs
    marques reparties par segment.

Melangee a l'annuaire generaliste, l'hotellerie faussait aussi le filtre par
tranche d'investissement : un projet a plusieurs millions ecrase toutes les
fourchettes des autres metiers.

LE LUXE N'EST PLUS ICI NON PLUS. Le meme raisonnement, un cran plus loin :
au-dessus du haut de gamme on ne signe presque jamais une franchise, on
confie l'exploitation au groupe, et la remuneration cesse d'etre une
redevance pour devenir un couple honoraires de base / honoraires
d'incitation, assis sur deux assiettes differentes. Cette colonne-la n'existe
pas ici. Les maisons de prestige ont donc leur propre site (../prestige/), et
les trois marques de luxe qui figuraient dans cette liste y sont parties :
une marque a deux endroits, c'est un total qui se contredit.

Tout ce qui est ici est FICTIF. Aucun groupe reel, aucune marque reelle,
aucun chiffre reel. Les montants sont tires dans les bandes du segment vise,
avec une graine fixe : deux reconstructions donnent le meme fichier.
"""

import hashlib
import json
import os
import random

from donnees import (PAYS, REGIONS, TAUX_EUR, POIDS_PAYS, arrondi_utile,
                     pays_ouverts, slug)

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)

# ---------------------------------------------------------------------------
# LES SEGMENTS. C'est la table qui tient toute la coherence : le segment
# CHOISIT les fourchettes, il n'est pas plaque apres coup sur des chiffres
# tires au hasard. Sans elle on obtient un hotel de luxe de 45 000 EUR la
# cle, ou un economique de 900 chambres — chaque fiche reste plausible seule
# et l'ensemble sonne faux.
#
# cle, fr, en,
#   investissement par cle (EUR, hors foncier) bas/haut,
#   taille acceptee bas/haut (nombre de cles),
#   redevance de marque (%), redevance de commercialisation et fidelite (%),
#   droit d'entree par cle (EUR), plancher du droit d'entree (EUR)
# ---------------------------------------------------------------------------
SEGMENTS = [
    ('economique', 'Economique', 'Economy',
     55000, 95000, 60, 140, (3.5, 5.0), (2.0, 3.5), (300, 500), (40000, 60000)),
    ('milieu', 'Milieu de gamme', 'Midscale',
     95000, 150000, 90, 200, (4.0, 5.5), (2.5, 4.0), (350, 550), (45000, 70000)),
    ('milieu-sup', 'Milieu de gamme superieur', 'Upper midscale',
     130000, 190000, 100, 220, (4.5, 5.5), (2.5, 4.0), (400, 600), (50000, 75000)),
    ('haut', 'Haut de gamme', 'Upscale',
     180000, 280000, 120, 300, (5.0, 6.0), (3.0, 4.5), (450, 650), (55000, 85000)),
    ('appart', 'Appart-hotel et sejour prolonge', 'Extended stay',
     85000, 160000, 80, 180, (4.0, 5.5), (2.5, 4.0), (350, 550), (45000, 70000)),
    ('lifestyle', 'Lifestyle et boutique', 'Lifestyle and boutique',
     160000, 300000, 50, 150, (5.0, 6.5), (3.0, 4.5), (500, 700), (60000, 90000)),
]

CONTRATS = [
    ('franchise', 'Franchise', 'Franchise',
     'Le proprietaire exploite lui-meme sous la marque. Il paie les '
     'redevances et applique les standards.',
     'The owner operates the hotel under the brand, pays the fees and '
     'applies the standards.'),
    ('gestion', 'Contrat de gestion', 'Management contract',
     'Le groupe exploite l\'hotel pour le compte du proprietaire, contre '
     'des honoraires de gestion assis sur le chiffre d\'affaires et le '
     'resultat.',
     'The group operates the hotel for the owner against management fees '
     'based on revenue and profit.'),
    ('location', 'Location / bail', 'Lease',
     'Le groupe loue les murs et exploite a ses risques. Le proprietaire '
     'percoit un loyer, fixe ou indexe sur le chiffre d\'affaires.',
     'The group leases the building and operates at its own risk. The owner '
     'receives a fixed or revenue-indexed rent.'),
    ('developpement', 'Contrat de developpement (territoire)',
     'Development agreement',
     'Un investisseur s\'engage sur plusieurs hotels dans un territoire '
     'donne, selon un calendrier d\'ouvertures.',
     'An investor commits to several hotels in a territory, on an agreed '
     'opening schedule.'),
]

# Un contrat de gestion sur un hotel economique de 70 chambres n'existe pas :
# les honoraires ne paieraient pas l'equipe du groupe. Le bail, lui, ne se
# pratique guere qu'en milieu de gamme urbain et en appart-hotel.
CONTRATS_PAR_SEGMENT = {
    'economique': ['franchise', 'developpement'],
    'milieu': ['franchise', 'location', 'developpement'],
    'milieu-sup': ['franchise', 'gestion', 'location', 'developpement'],
    'haut': ['franchise', 'gestion', 'location'],
    'appart': ['franchise', 'gestion', 'location', 'developpement'],
    'lifestyle': ['franchise', 'gestion'],
}

# Duree du contrat, en annees. Un contrat de gestion est toujours plus long
# qu'une franchise : le groupe y engage ses propres equipes.
DUREE = {
    'franchise': (10, 20),
    'gestion': (15, 25),
    'location': (12, 20),
    'developpement': (5, 10),
}

# La conversion d'un hotel existant sous la marque, par segment. C'est la
# question numero un d'un proprietaire qui a deja des murs : le luxe l'accepte
# rarement sans reconstruction lourde, l'economique presque toujours.
CONVERSION = {
    'economique': .90, 'milieu': .85, 'milieu-sup': .75, 'haut': .55,
    'appart': .60, 'lifestyle': .70,
}

SOUTIENS = [
    ('marque', 'Marque et standards', 'Brand and standards'),
    ('centrale', 'Centrale de reservation', 'Central reservation system'),
    ('fidelite', 'Programme de fidelite', 'Loyalty programme'),
    ('commercialisation', 'Plan de commercialisation', 'Sales and marketing plan'),
    ('revenue', 'Gestion tarifaire (revenue management)', 'Revenue management'),
    ('formation', 'Formation des equipes', 'Team training'),
    ('achats', 'Achats groupes', 'Group purchasing'),
    ('technique', 'Assistance technique et plan de renovation',
     'Technical services and renovation plan'),
]

# ---------------------------------------------------------------------------
# LES GROUPES ET LEURS MARQUES. Dix groupes fictifs, 29 marques.
#
# Un groupe ne porte JAMAIS deux marques dans le meme segment — c'est ainsi
# que sont batis les portefeuilles de marques hotelieres, et un controle le
# verifie. Le pays du groupe est ecrit, pas tire : le nom porte une langue,
# la langue porte un pays.
#
# groupe -> (pays, [(marque, segment, resume fr, resume en)])
# ---------------------------------------------------------------------------
GROUPES = {
    'Groupe Aubelis': ('FR', [
        ('Aubelis Hotels', 'milieu-sup',
         'Hotels urbains et de gare, clientele affaires et loisirs',
         'City and station hotels for business and leisure guests'),
        ('Aubelis Express', 'economique',
         'Format compact, petit-dejeuner inclus, entretien reduit',
         'Compact format, breakfast included, low maintenance'),
        ('Aubelis Residences', 'appart',
         'Appartements avec cuisine, sejours d\'une semaine et plus',
         'Serviced apartments with kitchen, one week and up'),
    ]),
    'Nordhaven Hospitality': ('SE', [
        ('Nordhaven Hotels', 'haut',
         'Hotels design, restauration et salles de reunion',
         'Design hotels with restaurant and meeting rooms'),
        ('Nordhaven Lodge', 'milieu',
         'Hotels de destination nature, quatre saisons',
         'Nature destination hotels, four seasons'),
        ('Fjell Stay', 'economique',
         'Hotels d\'etape sans restaurant, reception automatisee',
         'Stopover hotels, no restaurant, automated front desk'),
    ]),
    'Cassiopee Hospitality': ('CH', [
        ('Cassiopee Maison', 'lifestyle',
         'Petites unites de caractere, bar et table d\'auteur',
         'Small character properties with signature bar and kitchen'),
        ('Cassiopee City', 'milieu-sup',
         'Hotels de centre-ville, sejours courts',
         'City-centre hotels for short stays'),
    ]),
    'Vantara Hotels': ('CA', [
        ('Vantara Hotels & Suites', 'milieu-sup',
         'Chambres et suites, piscine interieure, salles de reunion',
         'Rooms and suites, indoor pool, meeting rooms'),
        ('Vantara Extended', 'appart',
         'Studios equipes, tarif degressif a la semaine',
         'Equipped studios, weekly rates'),
        ('Vantara Inns', 'economique',
         'Hotels routiers renoves, stationnement gratuit',
         'Renovated highway hotels, free parking'),
    ]),
    'Solmar Hoteles': ('ES', [
        ('Solmar Resorts', 'haut',
         'Resorts balneaires, restauration multiple et spa',
         'Seaside resorts with multiple restaurants and spa'),
        ('Solmar Playa', 'milieu',
         'Hotels de bord de mer, formule demi-pension',
         'Seafront hotels, half-board'),
        ('Solmar Boutique', 'lifestyle',
         'Maisons de ville restaurees, moins de cent cles',
         'Restored townhouses, under one hundred keys'),
    ]),
    'Rivermark Hotels': ('US', [
        ('Rivermark Hotels', 'haut',
         'Hotels d\'affaires, etage de reunion et lounge',
         'Business hotels with meeting floor and lounge'),
        ('Rivermark Stay', 'appart',
         'Sejour prolonge, cuisine complete, buanderie',
         'Extended stay, full kitchen, laundry'),
        ('Rivermark Road', 'economique',
         'Hotels d\'autoroute, ouverture 24 h',
         'Highway hotels, 24-hour front desk'),
    ]),
    'Terra Alta Hospitality': ('IT', [
        ('Terra Alta Dimore', 'lifestyle',
         'Demeures historiques converties, table regionale',
         'Converted historic houses with regional kitchen'),
        ('Terra Alta Hotels', 'milieu-sup',
         'Hotels de ville moyenne, clientele mixte',
         'Mid-size city hotels, mixed clientele'),
    ]),
    'Kestrel Hospitality': ('GB', [
        ('Kestrel Court', 'milieu',
         'Hotels de peripherie urbaine, seminaires et mariages',
         'Edge-of-town hotels for conferences and weddings'),
        ('Kestrel Halt', 'economique',
         'Hotels d\'aeroport et de zone d\'activite',
         'Airport and business-park hotels'),
    ]),
    'Maple Ridge Hotels': ('CA', [
        ('Maple Ridge Hotels', 'milieu',
         'Hotels regionaux, salles polyvalentes',
         'Regional hotels with function rooms'),
        ('Maple Ridge Lodges', 'lifestyle',
         'Lodges de montagne et de bord de lac',
         'Mountain and lakeside lodges'),
    ]),
    'Danube Hospitality': ('AT', [
        ('Danube Grand', 'haut',
         'Hotels de congres, grandes capacites de reunion',
         'Convention hotels with large meeting capacity'),
        ('Danube Stadt', 'milieu-sup',
         'Hotels urbains compacts, clientele affaires',
         'Compact city hotels for business guests'),
        ('Danube Kompakt', 'economique',
         'Format economique urbain, chambres optimisees',
         'Urban economy format, optimised rooms'),
    ]),
}

# Tranches d'investissement PAR CLE, en euros de reference. C'est l'unite du
# metier : « moins de 250 000 » de projet total ne veut rien dire quand un
# hotel fait entre 60 et 300 chambres.
TRANCHES_CLE = [
    ('c1', 'Moins de 100\u00a0000 EUR la cle', 'Under EUR 100,000 per key',
     0, 100000),
    ('c2', '100\u00a0000 a 175\u00a0000 EUR la cle',
     'EUR 100,000 to 175,000 per key', 100000, 175000),
    ('c3', '175\u00a0000 a 300\u00a0000 EUR la cle',
     'EUR 175,000 to 300,000 per key', 175000, 300000),
    ('c4', 'Plus de 300\u00a0000 EUR la cle', 'Over EUR 300,000 per key',
     300000, 10 ** 12),
]

# Tailles d'hotel proposees au filtre. Le filtre repond a « mon hotel fait
# N chambres, quelles enseignes l'acceptent » — donc N doit tomber DANS la
# fourchette acceptee par l'enseigne, pas au-dessus d'un minimum.
TAILLES = [60, 90, 120, 150, 200, 250]


def tranche_cle(v_eur):
    for cle, _fr, _en, bas, haut in TRANCHES_CLE:
        if bas <= v_eur < haut:
            return cle
    return 'c4'


def construire():
    devise_de = dict((p[0], p[4]) for p in PAYS)
    region_de = dict((p[0], p[3]) for p in PAYS)
    seg_de = dict((s[0], s) for s in SEGMENTS)
    fiches = []

    for groupe, (origine, marques) in GROUPES.items():
        for nom, seg, rfr, ren in marques:
            s = slug(nom)
            graine = int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)
            r = random.Random(graine)
            (_c, _fr, _en, ibas, ihaut, kbas, khaut,
             red_m, red_c, dcle, dplanch) = seg_de[seg]

            dev = devise_de[origine]
            taux = TAUX_EUR[dev]

            # La taille acceptee : une fourchette DANS la fourchette du
            # segment, jamais l'inverse.
            cles_min = r.randint(kbas, kbas + int((khaut - kbas) * .35))
            cles_max = min(khaut, int(cles_min * r.uniform(1.4, 2.2)))

            # L'investissement se tire PAR CLE, en euros de reference, puis
            # se convertit. Le cout du projet, lui, ne se tire pas : il se
            # CALCULE. Tire a part, il finirait par contredire le prix a la
            # cle affiche juste au-dessus.
            eur_cle_bas = r.uniform(ibas, ibas + (ihaut - ibas) * .5)
            eur_cle_haut = min(ihaut, eur_cle_bas * r.uniform(1.2, 1.6))
            cle_bas = arrondi_utile(eur_cle_bas / taux)
            cle_haut = arrondi_utile(eur_cle_haut / taux)
            projet_bas = cle_bas * cles_min
            projet_haut = cle_haut * cles_max

            # Droit d'entree : tant par cle, avec un plancher. C'est la forme
            # reelle, et elle change tout pour un petit hotel — 80 cles a
            # 500 EUR font moins que le plancher, c'est le plancher qui
            # s'applique.
            droit_cle = arrondi_utile(r.uniform(*dcle) / taux)
            droit_planch = arrondi_utile(r.uniform(*dplanch) / taux)

            marque_pct = round(r.uniform(*red_m), 1)
            com_pct = round(r.uniform(*red_c), 1)

            possibles = CONTRATS_PAR_SEGMENT[seg]
            principal = possibles[0]
            autres = [c for c in possibles[1:] if r.random() < .55]
            contrats = [principal] + autres
            d_bas, d_haut = DUREE[principal]
            duree = r.randint(d_bas, d_haut)

            creation = r.randint(1968, 2016)
            debut = min(2024, creation + r.randint(3, 15))

            # Le reseau : on tire le nombre d'HOTELS et la taille MOYENNE,
            # et on multiplie. Tirer le nombre de cles a part donnerait des
            # reseaux de 40 hotels et 900 cles, soit 22 chambres l'unite.
            hotels = r.randint(6, 420)
            taille_moy = r.randint(cles_min, cles_max)
            cles_reseau = hotels * taille_moy

            soutiens = ['marque', 'centrale', 'commercialisation', 'formation']
            for s_ in ('fidelite', 'revenue', 'achats', 'technique'):
                if r.random() < .7:
                    soutiens.append(s_)

            fiches.append({
                'id': s,
                'nom': nom,
                'groupe': groupe,
                'segment': seg,
                'resume': {'fr': rfr, 'en': ren},
                'pays_origine': origine,
                'region': region_de[origine],
                'devise': dev,
                'cles': {'min': cles_min, 'max': cles_max},
                'investissement_cle': {
                    'bas': cle_bas, 'haut': cle_haut,
                    'eur_bas': int(round(eur_cle_bas)),
                    'tranche': tranche_cle(eur_cle_bas),
                },
                'projet': {'bas': projet_bas, 'haut': projet_haut},
                'droit_entree': {'par_cle': droit_cle, 'plancher': droit_planch},
                'redevances': {
                    'marque': marque_pct,
                    'commercialisation': com_pct,
                    'total': round(marque_pct + com_pct, 1),
                },
                'contrats': contrats,
                'duree_contrat': duree,
                'conversion': r.random() < CONVERSION[seg],
                'renovation_ans': r.choice([5, 6, 7, 8]),
                'annee_creation': creation,
                'annee_franchisage': debut,
                'reseau': {'hotels': hotels, 'cles': cles_reseau,
                           'taille_moyenne': taille_moy},
                'pays': pays_ouverts(r, origine),
                'soutiens': soutiens,
                'demonstration': True,
            })

    fiches.sort(key=lambda f: (f['segment'], f['nom']))
    return fiches


def ecrire(fiches):
    if not os.path.isdir(DEMO):
        os.makedirs(DEMO)
    data = {
        'avertissement': (
            'Fiches de DEMONSTRATION. Groupes et marques fictifs, chiffres '
            'tires dans les bandes du segment vise. Aucun groupe reel, '
            'aucune marque reelle, aucun chiffre reel.'),
        'note_taux': (
            'Le classement et le filtre par investissement se font sur une '
            'valeur de reference en euros (taux figes). Chaque fiche '
            's\'affiche dans la devise de son pays.'),
        'segments': [{'cle': s[0], 'fr': s[1], 'en': s[2]} for s in SEGMENTS],
        'contrats': [{'cle': c[0], 'fr': c[1], 'en': c[2],
                      'desc_fr': c[3], 'desc_en': c[4]} for c in CONTRATS],
        'soutiens': [{'cle': s[0], 'fr': s[1], 'en': s[2]} for s in SOUTIENS],
        'pays': [{'cle': p[0], 'fr': p[1], 'en': p[2], 'region': p[3],
                  'devise': p[4]} for p in PAYS],
        'regions': [{'cle': x[0], 'fr': x[1], 'en': x[2]} for x in REGIONS],
        'tranches': [{'cle': t[0], 'fr': t[1], 'en': t[2], 'bas': t[3],
                      'haut': t[4]} for t in TRANCHES_CLE],
        'tailles': TAILLES,
        'groupes': [{'nom': g, 'pays': p, 'marques': [m[0] for m in ms]}
                    for g, (p, ms) in GROUPES.items()],
        'fiches': fiches,
    }
    chemin = os.path.join(DEMO, 'hotellerie.json')
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return chemin


COLONNES = [
    'marque', 'groupe', 'segment', 'resume_fr', 'resume_en', 'pays_origine',
    'devise', 'cles_min', 'cles_max', 'investissement_cle_bas',
    'investissement_cle_haut', 'droit_entree_par_cle', 'droit_entree_plancher',
    'redevance_marque_pct', 'redevance_commercialisation_pct', 'contrats',
    'duree_contrat_annees', 'conversion_acceptee', 'cycle_renovation_ans',
    'annee_creation', 'annee_franchisage', 'reseau_hotels',
    'reseau_taille_moyenne', 'pays_ouverts', 'soutiens',
]


def modele_csv(fiches):
    import csv
    chemin = os.path.join(ICI, 'import-modele-hotellerie.csv')
    with open(chemin, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(COLONNES)
        for fi in fiches[:2]:
            w.writerow([
                fi['nom'], fi['groupe'], fi['segment'], fi['resume']['fr'],
                fi['resume']['en'], fi['pays_origine'], fi['devise'],
                fi['cles']['min'], fi['cles']['max'],
                fi['investissement_cle']['bas'], fi['investissement_cle']['haut'],
                fi['droit_entree']['par_cle'], fi['droit_entree']['plancher'],
                fi['redevances']['marque'], fi['redevances']['commercialisation'],
                '|'.join(fi['contrats']), fi['duree_contrat'],
                'oui' if fi['conversion'] else 'non', fi['renovation_ans'],
                fi['annee_creation'], fi['annee_franchisage'],
                fi['reseau']['hotels'], fi['reseau']['taille_moyenne'],
                '|'.join(fi['pays']), '|'.join(fi['soutiens']),
            ])
    return chemin


if __name__ == '__main__':
    fi = construire()
    c1 = ecrire(fi)
    c2 = modele_csv(fi)
    print('%s  (%d octets)' % (c1, os.path.getsize(c1)))
    print('%s  (%d octets)' % (c2, os.path.getsize(c2)))
    print('%d marques, %d groupes, %d segments'
          % (len(fi), len(GROUPES), len(SEGMENTS)))
    for s in SEGMENTS:
        n = sum(1 for f in fi if f['segment'] == s[0])
        print('  %-28s %2d marques' % (s[1], n))
