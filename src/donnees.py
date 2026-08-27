# -*- coding: utf-8 -*-
"""Jeu de donnees de DEMONSTRATION pour l'annuaire de franchises.

CE QUE CE FICHIER N'EST PAS
---------------------------
Ce n'est pas un extrait de franchisedirect.com, ni d'aucun autre annuaire.
Je ne recopie pas la base d'un concurrent : c'est son actif, et une fiche
recopiee est fausse le jour ou l'enseigne change son droit d'entree.

Ce n'est pas non plus une liste de vraies enseignes canadiennes avec des
chiffres que j'aurais devines. Un montant d'investissement invente sur une
marque reelle, c'est une information financiere fausse publiee sous le nom de
quelqu'un d'autre. Je ne le fais pas.

CE QUE C'EST
------------
100 enseignes FICTIVES, clairement marquees comme telles dans l'interface,
dont le seul role est de faire tourner le moteur : les 20 categories, les
filtres, les fourchettes, le tri, la mise en relation. Le jour ou Hakim
fournit ses vraies fiches (les siennes + celles qu'il recrute), elles
remplacent ce fichier sans toucher une ligne du moteur — le format d'entree
est decrit dans « import-modele.csv ».

Les montants sont tires au sort, mais DANS LES BANDES REELLES DE CHAQUE
METIER : un cafe ne demande pas le meme apport qu'une concession automobile.
Le tirage est SEME par le nom de l'enseigne, donc deux executions donnent
exactement le meme fichier — une demo qui change de chiffres a chaque
rechargement n'est pas une demo, c'est un bruit.
"""

import collections
import csv
import hashlib
import json
import os
import random

ICI = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(ICI, 'demo')

# ---------------------------------------------------------------------------
# Les categories. « Concessionnaires automobiles » est demandee nommement par
# le client ; elle n'a rien a faire dans « Services automobiles » (un garage
# et une concession n'ont ni le meme apport, ni le meme candidat).
# Bandes : (investissement bas, investissement haut) en dollars canadiens.
# ---------------------------------------------------------------------------
CATEGORIES = [
    # cle,        fr,                                  en,                             invest bas, invest haut, droit bas, droit haut, redevance
    ('restauration-rapide', 'Restauration rapide', 'Quick service restaurants', 180000, 850000, 25000, 55000, (4.0, 7.0)),
    ('cafe-boulangerie', 'Cafe et boulangerie', 'Coffee and bakery', 150000, 700000, 20000, 45000, (4.0, 6.5)),
    ('restaurant-complet', 'Restaurants a service complet', 'Full-service restaurants', 350000, 1600000, 35000, 75000, (4.0, 6.0)),
    ('alimentation', 'Alimentation et epicerie', 'Food and grocery', 250000, 2200000, 30000, 90000, (2.0, 4.5)),
    ('concession-auto', 'Concessionnaires automobiles', 'Car dealerships', 900000, 6500000, 60000, 250000, (1.0, 3.0)),
    ('services-auto', 'Services automobiles', 'Automotive services', 150000, 900000, 25000, 60000, (5.0, 8.0)),
    ('sante', 'Sante et bien-etre', 'Health and wellness', 90000, 550000, 30000, 70000, (5.0, 8.0)),
    ('remise-en-forme', 'Sport et remise en forme', 'Fitness', 200000, 1400000, 30000, 60000, (5.0, 7.0)),
    ('beaute', 'Beaute et coiffure', 'Beauty and hair', 110000, 480000, 25000, 50000, (5.0, 7.5)),
    ('education', 'Education et soutien scolaire', 'Education and tutoring', 45000, 220000, 20000, 55000, (6.0, 10.0)),
    ('garde-enfants', 'Garde d\'enfants', 'Childcare', 120000, 900000, 30000, 70000, (5.0, 8.0)),
    ('services-entreprises', 'Services aux entreprises', 'Business services', 60000, 300000, 25000, 65000, (6.0, 9.0)),
    ('immobilier', 'Immobilier', 'Real estate', 35000, 250000, 20000, 60000, (5.0, 8.0)),
    ('nettoyage', 'Nettoyage et entretien', 'Cleaning and maintenance', 25000, 180000, 15000, 45000, (5.0, 10.0)),
    ('renovation', 'Renovation et construction', 'Home improvement', 70000, 400000, 30000, 70000, (5.0, 8.0)),
    ('detail', 'Commerce de detail', 'Retail', 130000, 750000, 25000, 55000, (4.0, 7.0)),
    ('animalerie', 'Animalerie et services animaliers', 'Pet care', 90000, 420000, 25000, 50000, (5.0, 7.5)),
    ('logistique', 'Logistique et expedition', 'Shipping and logistics', 100000, 500000, 30000, 60000, (5.0, 8.0)),
    ('aines', 'Services aux aines', 'Senior care', 80000, 350000, 40000, 80000, (5.0, 8.0)),
    ('hotellerie', 'Hotellerie', 'Hospitality', 1200000, 9000000, 50000, 150000, (4.0, 8.0)),
]

# ---------------------------------------------------------------------------
# 100 enseignes fictives, 5 par categorie. Les noms sont inventes ; ils sont
# volontairement « canadiens » de sonorite (francais et anglais melanges,
# comme le marche reel) pour que la demo soit credible a l'oeil sans emprunter
# le nom de personne.
# ---------------------------------------------------------------------------
ENSEIGNES = {
    'restauration-rapide': [
        ('Poutine Boreale', 'Comptoir de poutines et burgers du Nord', 'Northern poutine and burger counter'),
        ('Le Wrap Vert', 'Wraps et bols sante prepares minute', 'Made-to-order healthy wraps and bowls'),
        ('Chicko Grill', 'Poulet grille et sandwichs a emporter', 'Grilled chicken and takeout sandwiches'),
        ('Tacos du Fleuve', 'Tacos et burritos en service rapide', 'Fast-service tacos and burritos'),
        ('Frites & Cie', 'Friterie de quartier, format kiosque', 'Neighbourhood fry shop, kiosk format'),
    ],
    'cafe-boulangerie': [
        ('Cafe Nordika', 'Torrefaction maison et viennoiseries', 'House roasting and pastries'),
        ('Boulangerie Saint-Laurent', 'Pains au levain et sandwichs du midi', 'Sourdough breads and lunch sandwiches'),
        ('Brew Lane', 'Cafe de specialite, format comptoir', 'Specialty coffee, counter format'),
        ('La Mie Doree', 'Boulangerie-patisserie de proximite', 'Neighbourhood bakery and pastry shop'),
        ('Maple Bean Coffee', 'Cafe filtre et bagels, service au volant', 'Drip coffee and bagels, drive-through'),
    ],
    'restaurant-complet': [
        ('Bistro Trois-Rivieres', 'Bistro francais de quartier', 'Neighbourhood French bistro'),
        ('Harbour Grill House', 'Grillades et fruits de mer', 'Grill and seafood'),
        ('Trattoria Mont-Royal', 'Cuisine italienne familiale', 'Family Italian kitchen'),
        ('Le Cerf Blanc', 'Table du terroir, produits locaux', 'Regional table, local products'),
        ('Spice Route Kitchen', 'Cuisine indienne contemporaine', 'Contemporary Indian kitchen'),
    ],
    'alimentation': [
        ('Marche Verger', 'Epicerie fine et fruits et legumes', 'Fine grocery, fruit and vegetables'),
        ('Le Panier du Coin', 'Depanneur nouvelle generation', 'New-generation convenience store'),
        ('Boucherie Cartier', 'Boucherie de detail et pret-a-cuire', 'Retail butcher and ready-to-cook'),
        ('Nutri Vrac', 'Vente en vrac et produits bio', 'Bulk foods and organic products'),
        ('Ocean Fresh Market', 'Poissonnerie et produits de la mer', 'Fish market and seafood'),
    ],
    'concession-auto': [
        ('Groupe Auto Meridien', 'Concession multimarque, neuf et occasion', 'Multi-brand dealership, new and used'),
        ('Northbound Motors', 'Concession VUS et camions legers', 'SUV and light truck dealership'),
        ('Auto Prestige Laurentides', 'Vehicules haut de gamme et location longue duree', 'Premium vehicles and long-term leasing'),
        ('ElectroDrive Canada', 'Concession dediee au vehicule electrique', 'Dedicated electric vehicle dealership'),
        ('Camions Boreal', 'Vehicules commerciaux et flottes', 'Commercial vehicles and fleets'),
    ],
    'services-auto': [
        ('Mecanik Express', 'Entretien rapide et pneus', 'Quick service and tires'),
        ('Pare-Brise Plus', 'Reparation et remplacement de vitres', 'Glass repair and replacement'),
        ('Lave-Auto Cristal', 'Lave-auto automatique et detaillage', 'Automatic car wash and detailing'),
        ('Carrosserie Atlas', 'Debosselage et peinture', 'Body work and paint'),
        ('EV Care Station', 'Entretien de vehicules electriques', 'Electric vehicle servicing'),
    ],
    'sante': [
        ('Clinique Physio Axe', 'Physiotherapie et readaptation', 'Physiotherapy and rehabilitation'),
        ('Vision Claire', 'Optometrie et lunetterie', 'Optometry and eyewear'),
        ('Denti Sourire', 'Clinique dentaire familiale', 'Family dental clinic'),
        ('Audio Nord', 'Audioprothese et depistage auditif', 'Hearing aids and hearing screening'),
        ('Massotherapie Equilibre', 'Massotherapie et osteopathie', 'Massage therapy and osteopathy'),
    ],
    'remise-en-forme': [
        ('Studio Cadence', 'Studio de velo et cours collectifs', 'Cycling studio and group classes'),
        ('Fitzone 24', 'Salle accessible 24 heures', '24-hour access gym'),
        ('Yoga Sereine', 'Studio de yoga et pilates', 'Yoga and pilates studio'),
        ('CrossPoint Athletic', 'Entrainement fonctionnel encadre', 'Coached functional training'),
        ('AquaForme Canada', 'Bassins et cours aquatiques', 'Pools and aquatic classes'),
    ],
    'beaute': [
        ('Salon Belvedere', 'Coiffure hommes et femmes', 'Hair salon, men and women'),
        ('Barbier Rue Neuve', 'Barbier traditionnel', 'Traditional barber shop'),
        ('Ongles & Co', 'Manucure et pose d\'ongles', 'Manicure and nail services'),
        ('Institut Lumiere', 'Soins esthetiques et epilation', 'Aesthetic care and hair removal'),
        ('Glow Skin Studio', 'Soins du visage et dermo-cosmetique', 'Facials and dermo-cosmetics'),
    ],
    'education': [
        ('Academie Chiffres et Lettres', 'Soutien scolaire primaire et secondaire', 'Primary and secondary tutoring'),
        ('Code Junior', 'Ateliers de programmation pour enfants', 'Coding workshops for children'),
        ('Langue Vivante', 'Cours de francais et d\'anglais', 'French and English courses'),
        ('Mathex Tutorat', 'Mathematiques et sciences, en petit groupe', 'Math and science, small groups'),
        ('Prep College Nord', 'Preparation aux examens d\'admission', 'Admission exam preparation'),
    ],
    'garde-enfants': [
        ('Les Petits Explorateurs', 'Garderie educative 0-5 ans', 'Educational daycare, ages 0-5'),
        ('Nid Douillet', 'Garderie en milieu familial encadree', 'Supervised home-based daycare'),
        ('Camp Boussole', 'Camps de jour et activites parascolaires', 'Day camps and after-school activities'),
        ('Eveil Bilingue', 'Prematernelle bilingue', 'Bilingual preschool'),
        ('Bulle & Cabane', 'Halte-garderie de centre commercial', 'Shopping-centre drop-in daycare'),
    ],
    'services-entreprises': [
        ('Compta Simple', 'Tenue de livres et paie pour PME', 'Bookkeeping and payroll for SMEs'),
        ('Imprim Express', 'Impression, signalisation et copie', 'Printing, signage and copying'),
        ('Recrut Local', 'Recrutement et placement de personnel', 'Recruitment and staffing'),
        ('Conseil Croissance', 'Coaching d\'affaires et plan de croissance', 'Business coaching and growth planning'),
        ('Bureau Partage Nord', 'Espaces de travail partages', 'Shared workspaces'),
    ],
    'immobilier': [
        ('Immo Reperes', 'Courtage residentiel', 'Residential brokerage'),
        ('Gestion Loyers Pro', 'Gestion locative pour proprietaires', 'Rental management for landlords'),
        ('Commercial Nord Realty', 'Courtage commercial et industriel', 'Commercial and industrial brokerage'),
        ('Inspection Domus', 'Inspection de batiments residentiels', 'Residential building inspection'),
        ('Evaluation Boreale', 'Evaluation immobiliere agreee', 'Certified property appraisal'),
    ],
    'nettoyage': [
        ('Net Commercial', 'Entretien menager de bureaux', 'Commercial office cleaning'),
        ('Brille Maison', 'Menage residentiel recurrent', 'Recurring residential cleaning'),
        ('Vitres Hauteur', 'Lavage de vitres en hauteur', 'High-rise window washing'),
        ('Restau Sinistre', 'Apres-degat d\'eau et de feu', 'Water and fire damage restoration'),
        ('Tapis & Conduits', 'Nettoyage de tapis et de conduits', 'Carpet and duct cleaning'),
    ],
    'renovation': [
        ('Cuisines Renaissance', 'Renovation de cuisines et salles de bain', 'Kitchen and bathroom renovation'),
        ('Toitures Sentinelle', 'Toiture residentielle', 'Residential roofing'),
        ('Sous-sol Sec', 'Impermeabilisation et drainage', 'Waterproofing and drainage'),
        ('Fenetres Clair-Nord', 'Portes et fenetres', 'Doors and windows'),
        ('Amenagement Paysage Vert', 'Amenagement paysager et pavage', 'Landscaping and paving'),
    ],
    'detail': [
        ('Boutique Fil Rouge', 'Pret-a-porter feminin', 'Women\'s ready-to-wear'),
        ('Jouets Cabriole', 'Jouets et jeux educatifs', 'Toys and educational games'),
        ('Sport Cap Nord', 'Equipement de plein air', 'Outdoor equipment'),
        ('Maison & Deco Nord', 'Decoration et articles de maison', 'Home decor and housewares'),
        ('Telephonie Directe', 'Telephonie mobile et accessoires', 'Mobile phones and accessories'),
    ],
    'animalerie': [
        ('Toutou Chic', 'Toilettage pour chiens et chats', 'Dog and cat grooming'),
        ('Animalerie Pattes Nord', 'Alimentation et accessoires animaliers', 'Pet food and accessories'),
        ('Garderie Canine Boreale', 'Garderie et pension pour chiens', 'Dog daycare and boarding'),
        ('Veto Proximite', 'Clinique veterinaire de quartier', 'Neighbourhood veterinary clinic'),
        ('Dressage Compagnon', 'Education canine et comportement', 'Dog training and behaviour'),
    ],
    'logistique': [
        ('Colis Rapide Canada', 'Depot-relais et expedition', 'Parcel depot and shipping'),
        ('Demenagement Cap', 'Demenagement residentiel et commercial', 'Residential and commercial moving'),
        ('Entrepot Libre-Service', 'Entreposage en libre-service', 'Self-storage'),
        ('Livraison Dernier Kilometre', 'Livraison urbaine du dernier kilometre', 'Urban last-mile delivery'),
        ('Fret Nord Express', 'Courtage de transport routier', 'Road freight brokerage'),
    ],
    'aines': [
        ('Aide a Domicile Serenite', 'Aide a domicile et accompagnement', 'Home care and companionship'),
        ('Soins Infirmiers Nord', 'Soins infirmiers a domicile', 'In-home nursing care'),
        ('Transport Adapte Plus', 'Transport medical adapte', 'Adapted medical transport'),
        ('Residence Bel Age', 'Residence pour aines autonomes', 'Residence for independent seniors'),
        ('Repit Famille', 'Repit et soutien aux proches aidants', 'Respite and caregiver support'),
    ],
    'hotellerie': [
        ('Auberge du Portage', 'Auberge de charme en region', 'Regional boutique inn'),
        ('Hotel Cap Nord', 'Hotel d\'affaires de centre-ville', 'Downtown business hotel'),
        ('Chalets Foret Blanche', 'Chalets locatifs quatre saisons', 'Four-season rental cabins'),
        ('Motel Route 40', 'Motel routier renove', 'Renovated highway motel'),
        ('Suites Longue Duree', 'Suites en sejour prolonge', 'Extended-stay suites'),
    ],
}

PROVINCES = [
    ('QC', 'Quebec', 'Quebec'), ('ON', 'Ontario', 'Ontario'),
    ('BC', 'Colombie-Britannique', 'British Columbia'), ('AB', 'Alberta', 'Alberta'),
    ('MB', 'Manitoba', 'Manitoba'), ('SK', 'Saskatchewan', 'Saskatchewan'),
    ('NS', 'Nouvelle-Ecosse', 'Nova Scotia'), ('NB', 'Nouveau-Brunswick', 'New Brunswick'),
    ('NL', 'Terre-Neuve-et-Labrador', 'Newfoundland and Labrador'),
    ('PE', 'Ile-du-Prince-Edouard', 'Prince Edward Island'),
    ('YT', 'Yukon', 'Yukon'), ('NT', 'Territoires du Nord-Ouest', 'Northwest Territories'),
    ('NU', 'Nunavut', 'Nunavut'),
]
# Le poids demographique compte : une enseigne qui recrute part de l'Ontario
# et du Quebec, pas du Nunavut. Un tirage uniforme donnerait autant de
# franchises au Yukon qu'en Ontario, ce qu'aucun candidat ne croirait.
POIDS_PROV = {'ON': 39, 'QC': 22, 'BC': 14, 'AB': 12, 'MB': 4, 'SK': 3,
              'NS': 3, 'NB': 2, 'NL': 1, 'PE': 1, 'YT': 1, 'NT': 1, 'NU': 1}

FORMATS = [
    ('local', 'Local commercial', 'Retail unit'),
    ('kiosque', 'Kiosque ou ilot', 'Kiosk or cart'),
    ('domicile', 'A domicile', 'Home-based'),
    ('mobile', 'Mobile', 'Mobile'),
    ('master', 'Master franchise / territoire', 'Master franchise / territory'),
]
# Les formats plausibles par categorie. Une concession automobile « a
# domicile » n'existe pas ; laisser le hasard en produire une decredibiliserait
# toute la demo.
FORMATS_PAR_CAT = {
    'restauration-rapide': ['local', 'kiosque', 'master'],
    'cafe-boulangerie': ['local', 'kiosque'],
    'restaurant-complet': ['local', 'master'],
    'alimentation': ['local', 'master'],
    'concession-auto': ['local', 'master'],
    'services-auto': ['local', 'mobile'],
    'sante': ['local'],
    'remise-en-forme': ['local', 'master'],
    'beaute': ['local', 'kiosque'],
    'education': ['local', 'domicile', 'master'],
    'garde-enfants': ['local', 'domicile'],
    'services-entreprises': ['local', 'domicile', 'master'],
    'immobilier': ['local', 'domicile'],
    'nettoyage': ['domicile', 'mobile', 'master'],
    'renovation': ['domicile', 'mobile', 'local'],
    'detail': ['local', 'kiosque'],
    'animalerie': ['local', 'mobile'],
    'logistique': ['local', 'mobile', 'master'],
    'aines': ['local', 'domicile'],
    'hotellerie': ['local'],
}

TRANCHES = [
    ('t1', "Moins de 100 000 $", 'Under $100,000', 0, 100000),
    ('t2', "100 000 $ a 250 000 $", '$100,000 to $250,000', 100000, 250000),
    ('t3', "250 000 $ a 500 000 $", '$250,000 to $500,000', 250000, 500000),
    ('t4', "500 000 $ a 1 M$", '$500,000 to $1M', 500000, 1000000),
    ('t5', "Plus de 1 M$", 'Over $1M', 1000000, 10 ** 12),
]


# Les reseaux regionaux existent, et ils sont nombreux au Canada : une
# enseigne quebecoise qui n'a jamais franchi l'Outaouais, un reseau des
# Prairies, une chaine de l'Atlantique. Un tirage purement pondere donnait
# l'Ontario dans 100 fiches sur 100 — vrai pour les grands reseaux, faux pour
# le marche, et surtout un filtre « Ontario » qui ne filtre rien.
REGIONS = {
    'quebec': ['QC'],
    'atlantique': ['NS', 'NB', 'NL', 'PE'],
    'prairies': ['MB', 'SK', 'AB'],
    'ouest': ['BC', 'AB'],
    'centre': ['ON', 'QC'],
}


def provinces_de(r):
    """Les provinces ouvertes au recrutement, pour une enseigne.

    Une chance sur trois : reseau regional, ferme au reste du pays.
    Sinon : tirage pondere SANS REMISE (Efraimidis-Spirakis, cle
    aleatoire^(1/poids)). Le poids reste demographique, mais l'Ontario n'est
    plus certain d'etre tire — ce qui est le but : un filtre coche a 100/100
    n'est pas un filtre.
    """
    if r.random() < 0.34:
        base = REGIONS[r.choice(list(REGIONS))][:]
        if r.random() < 0.3:
            reste = [p for p in POIDS_PROV if p not in base]
            base.append(r.choice(reste))
        choix = base
    else:
        cles = sorted(POIDS_PROV)
        cles.sort(key=lambda p: -(r.random() ** (1.0 / POIDS_PROV[p])))
        choix = cles[:r.randint(3, 9)]
    ordre = [x[0] for x in PROVINCES]
    return sorted(set(choix), key=ordre.index)


def slug(t):
    out = []
    rempl = {'a': 'aaaaa', 'e': 'eeeee', 'i': 'ii', 'o': 'oo', 'u': 'uu', 'c': 'c'}
    for c in t.lower():
        if c.isalnum():
            out.append(c)
        elif out and out[-1] != '-':
            out.append('-')
    return ''.join(out).strip('-')


def tranche(v):
    for cle, _fr, _en, bas, haut in TRANCHES:
        if bas <= v < haut:
            return cle
    return 't5'


def arrondi(v, pas):
    return int(round(v / float(pas)) * pas)


def construire():
    fiches = []
    for cle, fr, en, ibas, ihaut, dbas, dhaut, red in CATEGORIES:
        for nom, dfr, den in ENSEIGNES[cle]:
            s = slug(nom)
            # Graine derivee du nom : le meme nom donne toujours les memes
            # chiffres, y compris apres reordonnancement de la liste.
            graine = int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)
            r = random.Random(graine)

            bas = arrondi(r.uniform(ibas, ibas + (ihaut - ibas) * 0.45), 5000)
            haut = arrondi(bas * r.uniform(1.35, 2.3), 5000)
            droit = arrondi(r.uniform(dbas, dhaut), 1000)
            # Les liquidites exigees sont une FRACTION de l'investissement bas,
            # pas un tirage independant : sinon on obtient des fiches ou
            # l'apport demande depasse le cout total du projet.
            liquide = arrondi(bas * r.uniform(0.25, 0.45), 5000)
            avoir = arrondi(liquide * r.uniform(2.0, 3.5), 25000)
            redevance = round(r.uniform(*red), 1)
            pub = round(r.uniform(1.0, 3.0), 1)

            creation = r.randint(1978, 2019)
            # On ne franchise jamais avant d'exister. Entre 2 et 12 ans apres.
            debut = min(2024, creation + r.randint(2, 12))
            unites = r.randint(3, 240)
            corpo = min(unites - 1, max(0, int(unites * r.uniform(0.0, 0.25))))
            franchisees = unites - corpo

            dispo = provinces_de(r)

            fiches.append({
                'id': s,
                'nom': nom,
                'categorie': cle,
                'resume': {'fr': dfr, 'en': den},
                'investissement': {'bas': bas, 'haut': haut, 'tranche': tranche(bas)},
                'droit_entree': droit,
                'liquidites': liquide,
                'avoir_net': avoir,
                'redevance': redevance,
                'fonds_pub': pub,
                'annee_creation': creation,
                'annee_franchisage': debut,
                'unites': unites,
                'unites_franchisees': franchisees,
                'unites_corpo': corpo,
                'provinces': dispo,
                'format': r.choice(FORMATS_PAR_CAT[cle]),
                'financement': r.random() < 0.55,
                'formation_semaines': r.choice([1, 2, 3, 4, 6, 8]),
                'delai_semaines': r.choice([8, 12, 16, 20, 26, 39, 52]),
                'demonstration': True,
            })

    fiches.sort(key=lambda f: (f['categorie'], f['nom']))
    return fiches


def ecrire(fiches):
    if not os.path.isdir(DEMO):
        os.makedirs(DEMO)
    data = {
        'avertissement': ('Fiches de DEMONSTRATION. Enseignes fictives, chiffres '
                          'tires dans les bandes reelles de chaque metier. Aucune '
                          'marque reelle, aucun chiffre reel.'),
        'pays': 'CA',
        'categories': [{'cle': c[0], 'fr': c[1], 'en': c[2]} for c in CATEGORIES],
        'provinces': [{'cle': p[0], 'fr': p[1], 'en': p[2]} for p in PROVINCES],
        'formats': [{'cle': f[0], 'fr': f[1], 'en': f[2]} for f in FORMATS],
        'tranches': [{'cle': t[0], 'fr': t[1], 'en': t[2], 'bas': t[3], 'haut': t[4]}
                     for t in TRANCHES],
        'fiches': fiches,
    }
    chemin = os.path.join(DEMO, 'catalogue.json')
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return chemin


COLONNES = [
    'nom', 'categorie', 'resume_fr', 'resume_en', 'investissement_bas',
    'investissement_haut', 'droit_entree', 'liquidites_exigees', 'avoir_net_exige',
    'redevance_pct', 'fonds_pub_pct', 'annee_creation', 'annee_franchisage',
    'unites_total', 'unites_franchisees', 'unites_corpo', 'provinces',
    'format', 'financement', 'formation_semaines', 'delai_semaines',
]


def modele_csv(fiches):
    """Le format d'entree, avec deux lignes remplies comme exemple.

    C'est ce fichier que remplit une enseigne (ou Hakim pour elle). Le moteur
    ne lit rien d'autre : tant que ces colonnes sont la, la fiche s'affiche.
    """
    chemin = os.path.join(ICI, 'import-modele.csv')
    with open(chemin, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(COLONNES)
        for fi in fiches[:2]:
            w.writerow([
                fi['nom'], fi['categorie'], fi['resume']['fr'], fi['resume']['en'],
                fi['investissement']['bas'], fi['investissement']['haut'],
                fi['droit_entree'], fi['liquidites'], fi['avoir_net'],
                fi['redevance'], fi['fonds_pub'], fi['annee_creation'],
                fi['annee_franchisage'], fi['unites'], fi['unites_franchisees'],
                fi['unites_corpo'], '|'.join(fi['provinces']), fi['format'],
                'oui' if fi['financement'] else 'non',
                fi['formation_semaines'], fi['delai_semaines'],
            ])
    return chemin


if __name__ == '__main__':
    fiches = construire()
    c = ecrire(fiches)
    m = modele_csv(fiches)
    par_cat = collections.Counter(f['categorie'] for f in fiches)
    print('%d fiches, %d categories' % (len(fiches), len(par_cat)))
    print('%s  (%d octets)' % (c, os.path.getsize(c)))
    print('%s  (%d octets)' % (m, os.path.getsize(m)))
    bas = min(f['investissement']['bas'] for f in fiches)
    haut = max(f['investissement']['haut'] for f in fiches)
    print('investissement : %d $ a %d $' % (bas, haut))
    for cle, _fr, _en, *_ in CATEGORIES:
        print('  %-22s %d' % (cle, par_cat[cle]))
