# -*- coding: utf-8 -*-
"""Jeu de donnees de DEMONSTRATION — annuaire de franchises Canada / USA / Europe.

CE QUE CE FICHIER N'EST PAS
---------------------------
Ce n'est pas un extrait de franchisedirect.com, ni d'aucun autre annuaire. Je
ne recopie pas la base d'un concurrent : c'est son actif, et une fiche
recopiee devient fausse le jour ou l'enseigne change son droit d'entree.

Ce n'est pas non plus une liste de vraies enseignes avec des chiffres devines.
Un montant d'investissement invente sur une marque reelle, c'est une
information financiere fausse publiee sous le nom de quelqu'un d'autre.

CE QUE C'EST
------------
210 enseignes FICTIVES sur 22 pays, clairement marquees comme telles dans
l'interface. Leur role est de faire tourner le moteur a l'echelle demandee :
21 categories, 22 pays, 5 regions, 8 devises, les filtres, les tris, la mise
en relation. Le jour ou les vraies fiches arrivent, elles remplacent ce
fichier sans qu'on touche une ligne du moteur (format : import-modele.csv).

Les montants sont tires DANS LES BANDES REELLES DE CHAQUE METIER, et le
tirage est SEME par le nom de l'enseigne : deux executions donnent exactement
le meme fichier.
"""

import collections
import csv
import hashlib
import json
import os
import random

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)

# ---------------------------------------------------------------------------
# LES PAYS. Le repertoire couvre trois marches : Canada, Etats-Unis, Europe.
# ---------------------------------------------------------------------------
# cle, fr, en, region, devise
PAYS = [
    ('CA', 'Canada', 'Canada', 'na', 'CAD'),
    ('US', 'Etats-Unis', 'United States', 'na', 'USD'),

    ('FR', 'France', 'France', 'eu-ouest', 'EUR'),
    ('BE', 'Belgique', 'Belgium', 'eu-ouest', 'EUR'),
    ('NL', 'Pays-Bas', 'Netherlands', 'eu-ouest', 'EUR'),
    ('DE', 'Allemagne', 'Germany', 'eu-ouest', 'EUR'),
    ('AT', 'Autriche', 'Austria', 'eu-ouest', 'EUR'),
    ('IE', 'Irlande', 'Ireland', 'eu-ouest', 'EUR'),
    ('GB', 'Royaume-Uni', 'United Kingdom', 'eu-ouest', 'GBP'),
    ('CH', 'Suisse', 'Switzerland', 'eu-ouest', 'CHF'),

    ('ES', 'Espagne', 'Spain', 'eu-sud', 'EUR'),
    ('IT', 'Italie', 'Italy', 'eu-sud', 'EUR'),
    ('PT', 'Portugal', 'Portugal', 'eu-sud', 'EUR'),
    ('GR', 'Grece', 'Greece', 'eu-sud', 'EUR'),

    ('SE', 'Suede', 'Sweden', 'eu-nord', 'SEK'),
    ('DK', 'Danemark', 'Denmark', 'eu-nord', 'DKK'),
    ('NO', 'Norvege', 'Norway', 'eu-nord', 'NOK'),
    ('FI', 'Finlande', 'Finland', 'eu-nord', 'EUR'),

    ('PL', 'Pologne', 'Poland', 'eu-est', 'PLN'),
    ('CZ', 'Tchequie', 'Czechia', 'eu-est', 'CZK'),
    ('RO', 'Roumanie', 'Romania', 'eu-est', 'RON'),
    ('HU', 'Hongrie', 'Hungary', 'eu-est', 'HUF'),
]

REGIONS = [
    ('na', 'Amerique du Nord', 'North America'),
    ('eu-ouest', 'Europe de l\'Ouest', 'Western Europe'),
    ('eu-sud', 'Europe du Sud', 'Southern Europe'),
    ('eu-nord', 'Europe du Nord', 'Northern Europe'),
    ('eu-est', 'Europe centrale et de l\'Est', 'Central and Eastern Europe'),
]

# TAUX DE REFERENCE, FIGES, POUR LE CLASSEMENT UNIQUEMENT.
# Un annuaire multi-devises doit pouvoir repondre a « montre-moi tout ce qui
# est sous 250 000 » sans que la reponse depende de la devise d'affichage. On
# range donc sur une valeur commune en euros. CE NE SONT PAS DES TAUX DU JOUR
# et ils ne servent JAMAIS a afficher un montant : chaque fiche s'affiche dans
# SA devise, telle que l'enseigne l'annonce. Sur le site reel, ce tableau se
# remplace par un flux de taux, et seul le classement bouge.
TAUX_EUR = {
    'EUR': 1.0, 'USD': 0.92, 'CAD': 0.68, 'GBP': 1.17, 'CHF': 1.05,
    'PLN': 0.23, 'SEK': 0.088, 'DKK': 0.134, 'NOK': 0.086,
    'CZK': 0.040, 'RON': 0.20, 'HUF': 0.0025,
}

# ---------------------------------------------------------------------------
# LES CATEGORIES. Bandes d'investissement exprimees EN EUROS (reference), puis
# converties dans la devise du pays de l'enseigne pour l'affichage.
# « concession-auto » et « duty-free » sont demandees nommement par le client.
# ---------------------------------------------------------------------------
# cle, fr, en, invest bas, invest haut, droit bas, droit haut, (redevance min, max)
CATEGORIES = [
    ('restauration-rapide', 'Restauration rapide', 'Quick service restaurants',
     120000, 580000, 17000, 38000, (4.0, 7.0)),
    ('cafe-boulangerie', 'Cafe et boulangerie', 'Coffee and bakery',
     100000, 480000, 14000, 31000, (4.0, 6.5)),
    ('restaurant-complet', 'Restaurants a service complet', 'Full-service restaurants',
     240000, 1100000, 24000, 52000, (4.0, 6.0)),
    ('alimentation', 'Alimentation et epicerie', 'Food and grocery',
     170000, 1500000, 20000, 62000, (2.0, 4.5)),
    ('concession-auto', 'Concessionnaires automobiles', 'Car dealerships',
     620000, 4400000, 41000, 170000, (1.0, 3.0)),
    ('duty-free', 'Duty free et boutiques d\'aeroport', 'Duty free and airport retail',
     300000, 2600000, 35000, 140000, (3.0, 8.0)),
    ('services-auto', 'Services automobiles', 'Automotive services',
     100000, 610000, 17000, 41000, (5.0, 8.0)),
    ('sante', 'Sante et bien-etre', 'Health and wellness',
     61000, 375000, 20000, 48000, (5.0, 8.0)),
    ('remise-en-forme', 'Sport et remise en forme', 'Fitness',
     136000, 950000, 20000, 41000, (5.0, 7.0)),
    ('beaute', 'Beaute et coiffure', 'Beauty and hair',
     75000, 326000, 17000, 34000, (5.0, 7.5)),
    ('education', 'Education et soutien scolaire', 'Education and tutoring',
     31000, 150000, 14000, 37000, (6.0, 10.0)),
    ('garde-enfants', 'Garde d\'enfants', 'Childcare',
     82000, 610000, 20000, 48000, (5.0, 8.0)),
    ('services-entreprises', 'Services aux entreprises', 'Business services',
     41000, 204000, 17000, 44000, (6.0, 9.0)),
    ('immobilier', 'Immobilier', 'Real estate',
     24000, 170000, 14000, 41000, (5.0, 8.0)),
    ('nettoyage', 'Nettoyage et entretien', 'Cleaning and maintenance',
     17000, 122000, 10000, 31000, (5.0, 10.0)),
    ('renovation', 'Renovation et construction', 'Home improvement',
     48000, 272000, 20000, 48000, (5.0, 8.0)),
    ('detail', 'Commerce de detail', 'Retail',
     88000, 510000, 17000, 37000, (4.0, 7.0)),
    ('animalerie', 'Animalerie et services animaliers', 'Pet care',
     61000, 285000, 17000, 34000, (5.0, 7.5)),
    ('logistique', 'Logistique et expedition', 'Shipping and logistics',
     68000, 340000, 20000, 41000, (5.0, 8.0)),
    ('aines', 'Services aux aines', 'Senior care',
     54000, 238000, 27000, 54000, (5.0, 8.0)),
]

# ---------------------------------------------------------------------------
# 200 enseignes fictives : 5 nord-americaines et 5 europeennes par categorie.
# L'HOTELLERIE N'EST PLUS ICI : elle a sa propre section (hotels.py), parce
# qu'une enseigne hoteliere ne se compare pas a un commerce sur les memes
# colonnes — on y investit AU NOMBRE DE CLES, on paie une redevance de marque
# ET une redevance de commercialisation, et le contrat peut etre une franchise
# ou un contrat de gestion. Melangee ici, elle faussait aussi le filtre par
# tranche : un hotel a plusieurs millions ecrasait toutes les fourchettes.
# Les noms sont inventes ; leur sonorite suit le marche vise pour que la demo
# soit credible a l'oeil sans emprunter le nom de personne.
# (nom, resume fr, resume en, region d'origine)
# ---------------------------------------------------------------------------
ENSEIGNES = {
    'restauration-rapide': [
        ('Poutine Boreale', 'Comptoir de poutines et burgers du Nord', 'Northern poutine and burger counter', 'na'),
        ('Le Wrap Vert', 'Wraps et bols sante prepares minute', 'Made-to-order healthy wraps and bowls', 'na'),
        ('Chicko Grill', 'Poulet grille et sandwichs a emporter', 'Grilled chicken and takeout sandwiches', 'na'),
        ('Tacos du Fleuve', 'Tacos et burritos en service rapide', 'Fast-service tacos and burritos', 'na'),
        ('Frites & Cie', 'Friterie de quartier, format kiosque', 'Neighbourhood fry shop, kiosk format', 'na'),
        ('Croq Comptoir', 'Sandwicherie et salades a emporter', 'Sandwich and salad counter', 'eu'),
        ('Wurst Haus', 'Saucisses grillees et frites, format comptoir', 'Grilled sausages and fries, counter format', 'eu'),
        ('Pita Meridiana', 'Pitas et grillades mediterraneennes', 'Pitas and Mediterranean grills', 'eu'),
        ('Chippy Corner', 'Fish and chips a emporter', 'Fish and chips takeaway', 'eu'),
        ('Bolla Pasta', 'Pates fraiches en service rapide', 'Fresh pasta, fast service', 'eu'),
    ],
    'cafe-boulangerie': [
        ('Cafe Nordika', 'Torrefaction maison et viennoiseries', 'House roasting and pastries', 'na'),
        ('Boulangerie Saint-Laurent', 'Pains au levain et sandwichs du midi', 'Sourdough breads and lunch sandwiches', 'na'),
        ('Brew Lane', 'Cafe de specialite, format comptoir', 'Specialty coffee, counter format', 'na'),
        ('La Mie Doree', 'Boulangerie-patisserie de proximite', 'Neighbourhood bakery and pastry shop', 'na'),
        ('Maple Bean Coffee', 'Cafe filtre et bagels, service au volant', 'Drip coffee and bagels, drive-through', 'na'),
        ('Cafe Belleville', 'Cafe de quartier et petite restauration', 'Neighbourhood cafe and light meals', 'eu'),
        ('Panetteria Aurora', 'Pains, focaccias et patisserie italienne', 'Breads, focaccia and Italian pastry', 'eu'),
        ('Kanelbulle Kaffe', 'Cafe et brioches a la cannelle', 'Coffee and cinnamon buns', 'eu'),
        ('Horno Dorado', 'Boulangerie traditionnelle au four a bois', 'Traditional wood-fired bakery', 'eu'),
        ('Bean & Brick', 'Cafe de specialite et brunch', 'Specialty coffee and brunch', 'eu'),
    ],
    'restaurant-complet': [
        ('Bistro Trois-Rivieres', 'Bistro francais de quartier', 'Neighbourhood French bistro', 'na'),
        ('Harbour Grill House', 'Grillades et fruits de mer', 'Grill and seafood', 'na'),
        ('Trattoria Mont-Royal', 'Cuisine italienne familiale', 'Family Italian kitchen', 'na'),
        ('Le Cerf Blanc', 'Table du terroir, produits locaux', 'Regional table, local products', 'na'),
        ('Spice Route Kitchen', 'Cuisine indienne contemporaine', 'Contemporary Indian kitchen', 'na'),
        ('Brasserie Lumiere', 'Brasserie parisienne, service continu', 'Parisian brasserie, all-day service', 'eu'),
        ('Osteria del Ponte', 'Osteria regionale et cave a vins', 'Regional osteria and wine cellar', 'eu'),
        ('Taberna del Sol', 'Tapas et cuisine du sud', 'Tapas and southern cooking', 'eu'),
        ('The Copper Fork', 'Cuisine britannique moderne', 'Modern British cooking', 'eu'),
        ('Gasthaus Lindenhof', 'Auberge et cuisine regionale', 'Inn and regional cuisine', 'eu'),
    ],
    'alimentation': [
        ('Marche Verger', 'Epicerie fine et fruits et legumes', 'Fine grocery, fruit and vegetables', 'na'),
        ('Le Panier du Coin', 'Depanneur nouvelle generation', 'New-generation convenience store', 'na'),
        ('Boucherie Cartier', 'Boucherie de detail et pret-a-cuire', 'Retail butcher and ready-to-cook', 'na'),
        ('Nutri Vrac', 'Vente en vrac et produits bio', 'Bulk foods and organic products', 'na'),
        ('Ocean Fresh Market', 'Poissonnerie et produits de la mer', 'Fish market and seafood', 'na'),
        ('Halles Vertes', 'Marche de primeurs et epicerie fine', 'Greengrocer market and fine grocery', 'eu'),
        ('Bio Speisekammer', 'Epicerie biologique et vrac', 'Organic grocery and bulk foods', 'eu'),
        ('Mercado Fresco', 'Epicerie de quartier et produits frais', 'Neighbourhood grocery and fresh produce', 'eu'),
        ('Corner Pantry', 'Superette de proximite ouverte tard', 'Late-opening convenience store', 'eu'),
        ('Pescheria Blu', 'Poissonnerie et plats prepares', 'Fishmonger and prepared dishes', 'eu'),
    ],
    'concession-auto': [
        ('Groupe Auto Meridien', 'Concession multimarque, neuf et occasion', 'Multi-brand dealership, new and used', 'na'),
        ('Northbound Motors', 'Concession VUS et camions legers', 'SUV and light truck dealership', 'na'),
        ('Auto Prestige Laurentides', 'Vehicules haut de gamme et location longue duree', 'Premium vehicles and long-term leasing', 'na'),
        ('ElectroDrive Canada', 'Concession dediee au vehicule electrique', 'Dedicated electric vehicle dealership', 'na'),
        ('Camions Boreal', 'Vehicules commerciaux et flottes', 'Commercial vehicles and fleets', 'na'),
        ('Groupe Auto Vendome', 'Concession multimarque et atelier integre', 'Multi-brand dealership with in-house workshop', 'eu'),
        ('AutoHaus Rheinpark', 'Concession et centre de reprise', 'Dealership and trade-in centre', 'eu'),
        ('Motori Adriatico', 'Concession citadines et utilitaires', 'City car and van dealership', 'eu'),
        ('Northgate Motors', 'Concession occasion garantie', 'Warrantied used-car dealership', 'eu'),
        ('ElectroMobil Nordic', 'Concession electrique et bornes de recharge', 'Electric dealership and charging points', 'eu'),
    ],
    'duty-free': [
        ('Duty Free Frontiere', 'Boutique hors taxes de poste frontalier', 'Border-crossing duty free store', 'na'),
        ('SkyShop Travel Retail', 'Boutique hors taxes en aerogare', 'Airport terminal duty free store', 'na'),
        ('Maple Duty Free', 'Hors taxes : spiritueux, tabac, confiserie', 'Duty free: spirits, tobacco, confectionery', 'na'),
        ('AirScent Beauty', 'Parfums et cosmetiques en aeroport', 'Airport perfume and cosmetics', 'na'),
        ('Border Wines & Spirits', 'Vins et spiritueux hors taxes', 'Duty free wines and spirits', 'na'),
        ('Voyage Hors Taxes', 'Boutique hors taxes multi-rayons', 'Multi-department duty free store', 'eu'),
        ('AeroLux Boutique', 'Maroquinerie et horlogerie en aerogare', 'Airport leather goods and watches', 'eu'),
        ('Terminal Parfums', 'Parfumerie de voyage et coffrets', 'Travel perfumery and gift sets', 'eu'),
        ('Sky Spirits Europe', 'Spiritueux et produits regionaux en aeroport', 'Airport spirits and regional products', 'eu'),
        ('Gateway Travel Retail', 'Boutique de voyage, presse et souvenirs', 'Travel retail: press and souvenirs', 'eu'),
    ],
    'services-auto': [
        ('Mecanik Express', 'Entretien rapide et pneus', 'Quick service and tires', 'na'),
        ('Pare-Brise Plus', 'Reparation et remplacement de vitres', 'Glass repair and replacement', 'na'),
        ('Lave-Auto Cristal', 'Lave-auto automatique et detaillage', 'Automatic car wash and detailing', 'na'),
        ('Carrosserie Atlas', 'Debosselage et peinture', 'Body work and paint', 'na'),
        ('EV Care Station', 'Entretien de vehicules electriques', 'Electric vehicle servicing', 'na'),
        ('Pneus Express Europe', 'Pneumatiques et entretien courant', 'Tires and routine servicing', 'eu'),
        ('Glas Klar Service', 'Vitrage automobile, reparation et pose', 'Auto glass repair and fitting', 'eu'),
        ('Lavado Cristal', 'Lavage automatique et nettoyage interieur', 'Automatic wash and interior cleaning', 'eu'),
        ('BodyShop Direct', 'Carrosserie et peinture rapide', 'Body shop and fast paint', 'eu'),
        ('Volt Garage', 'Atelier dedie aux vehicules electriques', 'Workshop for electric vehicles', 'eu'),
    ],
    'sante': [
        ('Clinique Physio Axe', 'Physiotherapie et readaptation', 'Physiotherapy and rehabilitation', 'na'),
        ('Vision Claire', 'Optometrie et lunetterie', 'Optometry and eyewear', 'na'),
        ('Denti Sourire', 'Clinique dentaire familiale', 'Family dental clinic', 'na'),
        ('Audio Nord', 'Audioprothese et depistage auditif', 'Hearing aids and hearing screening', 'na'),
        ('Massotherapie Equilibre', 'Massotherapie et osteopathie', 'Massage therapy and osteopathy', 'na'),
        ('Physio Elan', 'Kinesitherapie et reeducation', 'Physiotherapy and rehabilitation', 'eu'),
        ('OptikKlar', 'Optique et examen de vue', 'Optics and eye testing', 'eu'),
        ('Sorriso Dental', 'Cabinet dentaire et orthodontie', 'Dental practice and orthodontics', 'eu'),
        ('HearWell Clinics', 'Audioprothese et bilans auditifs', 'Hearing aids and hearing assessments', 'eu'),
        ('Kine Equilibre', 'Kinesitherapie et osteopathie', 'Physiotherapy and osteopathy', 'eu'),
    ],
    'remise-en-forme': [
        ('Studio Cadence', 'Studio de velo et cours collectifs', 'Cycling studio and group classes', 'na'),
        ('Fitzone 24', 'Salle accessible 24 heures', '24-hour access gym', 'na'),
        ('Yoga Sereine', 'Studio de yoga et pilates', 'Yoga and pilates studio', 'na'),
        ('CrossPoint Athletic', 'Entrainement fonctionnel encadre', 'Coached functional training', 'na'),
        ('AquaForme Canada', 'Bassins et cours aquatiques', 'Pools and aquatic classes', 'na'),
        ('Velo Studio Lumen', 'Studio de velo en salle', 'Indoor cycling studio', 'eu'),
        ('FitHaus 24', 'Salle de sport ouverte en continu', 'Round-the-clock gym', 'eu'),
        ('Yoga Serena', 'Yoga, pilates et meditation', 'Yoga, pilates and meditation', 'eu'),
        ('CrossBase Athletic', 'Entrainement fonctionnel en petit groupe', 'Small-group functional training', 'eu'),
        ('AquaNordic', 'Bassins, aquagym et ecole de natation', 'Pools, aqua fitness and swim school', 'eu'),
    ],
    'beaute': [
        ('Salon Belvedere', 'Coiffure hommes et femmes', 'Hair salon, men and women', 'na'),
        ('Barbier Rue Neuve', 'Barbier traditionnel', 'Traditional barber shop', 'na'),
        ('Ongles & Co', 'Manucure et pose d\'ongles', 'Manicure and nail services', 'na'),
        ('Institut Lumiere', 'Soins esthetiques et epilation', 'Aesthetic care and hair removal', 'na'),
        ('Glow Skin Studio', 'Soins du visage et dermo-cosmetique', 'Facials and dermo-cosmetics', 'na'),
        ('Salon Rive Gauche', 'Coiffure et coloration vegetale', 'Hair salon and plant-based colouring', 'eu'),
        ('Barbier Kreuzberg', 'Barbier et soins de la barbe', 'Barber and beard care', 'eu'),
        ('Nail Atelier', 'Manucure, pedicure et pose', 'Manicure, pedicure and extensions', 'eu'),
        ('Instituto Luz', 'Institut de beaute et epilation', 'Beauty institute and hair removal', 'eu'),
        ('Glow Nordic Skin', 'Soins du visage et cosmetique nordique', 'Facials and Nordic cosmetics', 'eu'),
    ],
    'education': [
        ('Academie Chiffres et Lettres', 'Soutien scolaire primaire et secondaire', 'Primary and secondary tutoring', 'na'),
        ('Code Junior', 'Ateliers de programmation pour enfants', 'Coding workshops for children', 'na'),
        ('Langue Vivante', 'Cours de francais et d\'anglais', 'French and English courses', 'na'),
        ('Mathex Tutorat', 'Mathematiques et sciences, en petit groupe', 'Math and science, small groups', 'na'),
        ('Prep College Nord', 'Preparation aux examens d\'admission', 'Admission exam preparation', 'na'),
        ('Academie Plume et Chiffres', 'Soutien scolaire tous niveaux', 'Tutoring, all levels', 'eu'),
        ('CodeKids Europe', 'Programmation et robotique pour enfants', 'Coding and robotics for children', 'eu'),
        ('Lingua Viva', 'Ecole de langues pour particuliers et entreprises', 'Language school, individuals and companies', 'eu'),
        ('MatheMax Nachhilfe', 'Soutien en mathematiques et sciences', 'Math and science tutoring', 'eu'),
        ('Exam Prep Academy', 'Preparation aux examens nationaux', 'National exam preparation', 'eu'),
    ],
    'garde-enfants': [
        ('Les Petits Explorateurs', 'Garderie educative 0-5 ans', 'Educational daycare, ages 0-5', 'na'),
        ('Nid Douillet', 'Garderie en milieu familial encadree', 'Supervised home-based daycare', 'na'),
        ('Camp Boussole', 'Camps de jour et activites parascolaires', 'Day camps and after-school activities', 'na'),
        ('Eveil Bilingue', 'Prematernelle bilingue', 'Bilingual preschool', 'na'),
        ('Bulle & Cabane', 'Halte-garderie de centre commercial', 'Shopping-centre drop-in daycare', 'na'),
        ('Les Petits Nuages', 'Creche et pre-maternelle', 'Nursery and preschool', 'eu'),
        ('Kita Sonnenschein', 'Creche a pedagogie active', 'Active-pedagogy nursery', 'eu'),
        ('Piccoli Passi', 'Creche et jardin d\'enfants', 'Nursery and kindergarten', 'eu'),
        ('Bright Corner Nursery', 'Creche bilingue et periscolaire', 'Bilingual nursery and after-school', 'eu'),
        ('Duimelot Opvang', 'Accueil de la petite enfance', 'Early-years childcare', 'eu'),
    ],
    'services-entreprises': [
        ('Compta Simple', 'Tenue de livres et paie pour PME', 'Bookkeeping and payroll for SMEs', 'na'),
        ('Imprim Express', 'Impression, signalisation et copie', 'Printing, signage and copying', 'na'),
        ('Recrut Local', 'Recrutement et placement de personnel', 'Recruitment and staffing', 'na'),
        ('Conseil Croissance', 'Coaching d\'affaires et plan de croissance', 'Business coaching and growth planning', 'na'),
        ('Bureau Partage Nord', 'Espaces de travail partages', 'Shared workspaces', 'na'),
        ('Compta Facile Europe', 'Comptabilite et paie pour TPE', 'Accounting and payroll for small firms', 'eu'),
        ('PrintPoint Express', 'Impression numerique et signaletique', 'Digital printing and signage', 'eu'),
        ('TalentLink Recrutement', 'Recrutement et interim specialise', 'Specialist recruitment and temping', 'eu'),
        ('Wachstum Beratung', 'Conseil en croissance pour PME', 'Growth consulting for SMEs', 'eu'),
        ('DeskShare Europe', 'Bureaux partages et salles de reunion', 'Shared offices and meeting rooms', 'eu'),
    ],
    'immobilier': [
        ('Immo Reperes', 'Courtage residentiel', 'Residential brokerage', 'na'),
        ('Gestion Loyers Pro', 'Gestion locative pour proprietaires', 'Rental management for landlords', 'na'),
        ('Commercial Nord Realty', 'Courtage commercial et industriel', 'Commercial and industrial brokerage', 'na'),
        ('Inspection Domus', 'Inspection de batiments residentiels', 'Residential building inspection', 'na'),
        ('Evaluation Boreale', 'Evaluation immobiliere agreee', 'Certified property appraisal', 'na'),
        ('Cle de Voute Immobilier', 'Transaction residentielle', 'Residential property sales', 'eu'),
        ('Casa Prima Realty', 'Vente et location residentielle', 'Residential sales and lettings', 'eu'),
        ('Mietwerk Verwaltung', 'Gestion locative et syndic', 'Rental and building management', 'eu'),
        ('Survey & Stone', 'Diagnostic et expertise du bati', 'Building surveys and diagnostics', 'eu'),
        ('Valora Estimation', 'Estimation et expertise immobiliere', 'Property valuation and appraisal', 'eu'),
    ],
    'nettoyage': [
        ('Net Commercial', 'Entretien menager de bureaux', 'Commercial office cleaning', 'na'),
        ('Brille Maison', 'Menage residentiel recurrent', 'Recurring residential cleaning', 'na'),
        ('Vitres Hauteur', 'Lavage de vitres en hauteur', 'High-rise window washing', 'na'),
        ('Restau Sinistre', 'Apres-degat d\'eau et de feu', 'Water and fire damage restoration', 'na'),
        ('Tapis & Conduits', 'Nettoyage de tapis et de conduits', 'Carpet and duct cleaning', 'na'),
        ('Net Bureau Europe', 'Nettoyage de bureaux et locaux', 'Office and premises cleaning', 'eu'),
        ('Glanz Reinigung', 'Nettoyage residentiel et vitrerie', 'Residential cleaning and windows', 'eu'),
        ('Brilla Casa', 'Menage a domicile sur abonnement', 'Subscription home cleaning', 'eu'),
        ('HighPane Window Care', 'Vitrerie en hauteur et facades', 'High-level window and facade care', 'eu'),
        ('Sinistre Secours', 'Remise en etat apres sinistre', 'Post-disaster restoration', 'eu'),
    ],
    'renovation': [
        ('Cuisines Renaissance', 'Renovation de cuisines et salles de bain', 'Kitchen and bathroom renovation', 'na'),
        ('Toitures Sentinelle', 'Toiture residentielle', 'Residential roofing', 'na'),
        ('Sous-sol Sec', 'Impermeabilisation et drainage', 'Waterproofing and drainage', 'na'),
        ('Fenetres Clair-Nord', 'Portes et fenetres', 'Doors and windows', 'na'),
        ('Amenagement Paysage Vert', 'Amenagement paysager et pavage', 'Landscaping and paving', 'na'),
        ('Cuisines Atelier Nord', 'Cuisines et salles de bain sur mesure', 'Bespoke kitchens and bathrooms', 'eu'),
        ('Dachwerk Bedachung', 'Couverture et isolation de toiture', 'Roofing and roof insulation', 'eu'),
        ('Cantieri Rinnova', 'Renovation d\'appartements cle en main', 'Turnkey apartment renovation', 'eu'),
        ('ClearFrame Windows', 'Menuiseries exterieures et vitrage', 'Exterior joinery and glazing', 'eu'),
        ('Jardins Paysage Europe', 'Paysagisme et amenagement exterieur', 'Landscaping and outdoor works', 'eu'),
    ],
    'detail': [
        ('Boutique Fil Rouge', 'Pret-a-porter feminin', 'Women\'s ready-to-wear', 'na'),
        ('Jouets Cabriole', 'Jouets et jeux educatifs', 'Toys and educational games', 'na'),
        ('Sport Cap Nord', 'Equipement de plein air', 'Outdoor equipment', 'na'),
        ('Maison & Deco Nord', 'Decoration et articles de maison', 'Home decor and housewares', 'na'),
        ('Telephonie Directe', 'Telephonie mobile et accessoires', 'Mobile phones and accessories', 'na'),
        ('Boutique Fil et Lin', 'Pret-a-porter et accessoires', 'Ready-to-wear and accessories', 'eu'),
        ('Spielwerk Toys', 'Jouets en bois et jeux educatifs', 'Wooden toys and educational games', 'eu'),
        ('Cima Outdoor', 'Materiel de randonnee et de montagne', 'Hiking and mountain equipment', 'eu'),
        ('Casa Deco Iberia', 'Decoration et art de la table', 'Home decor and tableware', 'eu'),
        ('MobilePoint Europe', 'Telephonie, reparation et accessoires', 'Phones, repair and accessories', 'eu'),
    ],
    'animalerie': [
        ('Toutou Chic', 'Toilettage pour chiens et chats', 'Dog and cat grooming', 'na'),
        ('Animalerie Pattes Nord', 'Alimentation et accessoires animaliers', 'Pet food and accessories', 'na'),
        ('Garderie Canine Boreale', 'Garderie et pension pour chiens', 'Dog daycare and boarding', 'na'),
        ('Veto Proximite', 'Clinique veterinaire de quartier', 'Neighbourhood veterinary clinic', 'na'),
        ('Dressage Compagnon', 'Education canine et comportement', 'Dog training and behaviour', 'na'),
        ('Patte de Velours', 'Toilettage chiens et chats', 'Dog and cat grooming', 'eu'),
        ('TierWohl Shop', 'Alimentation et accessoires pour animaux', 'Pet food and accessories', 'eu'),
        ('Zampe Felici', 'Toilettage et petite animalerie', 'Grooming and small pet shop', 'eu'),
        ('PawSquare Daycare', 'Garderie et pension canine', 'Dog daycare and boarding', 'eu'),
        ('Veterinaria Proxima', 'Cabinet veterinaire de proximite', 'Local veterinary practice', 'eu'),
    ],
    'logistique': [
        ('Colis Rapide Canada', 'Depot-relais et expedition', 'Parcel depot and shipping', 'na'),
        ('Demenagement Cap', 'Demenagement residentiel et commercial', 'Residential and commercial moving', 'na'),
        ('Entrepot Libre-Service', 'Entreposage en libre-service', 'Self-storage', 'na'),
        ('Livraison Dernier Kilometre', 'Livraison urbaine du dernier kilometre', 'Urban last-mile delivery', 'na'),
        ('Fret Nord Express', 'Courtage de transport routier', 'Road freight brokerage', 'na'),
        ('Colis Point Europe', 'Point relais et expedition de colis', 'Parcel pickup point and shipping', 'eu'),
        ('Umzug Direkt', 'Demenagement de particuliers et bureaux', 'Home and office removals', 'eu'),
        ('BoxRoom Self Storage', 'Box de stockage en libre-service', 'Self-storage units', 'eu'),
        ('Ultimo Miglio Delivery', 'Livraison urbaine du dernier kilometre', 'Urban last-mile delivery', 'eu'),
        ('Cargo Lien Europe', 'Commission de transport et groupage', 'Freight forwarding and groupage', 'eu'),
    ],
    'aines': [
        ('Aide a Domicile Serenite', 'Aide a domicile et accompagnement', 'Home care and companionship', 'na'),
        ('Soins Infirmiers Nord', 'Soins infirmiers a domicile', 'In-home nursing care', 'na'),
        ('Transport Adapte Plus', 'Transport medical adapte', 'Adapted medical transport', 'na'),
        ('Residence Bel Age', 'Residence pour aines autonomes', 'Residence for independent seniors', 'na'),
        ('Repit Famille', 'Repit et soutien aux proches aidants', 'Respite and caregiver support', 'na'),
        ('Presence a Domicile', 'Aide a domicile et compagnie', 'Home help and companionship', 'eu'),
        ('SeniorHilfe Pflege', 'Soins et assistance a domicile', 'Home nursing and assistance', 'eu'),
        ('Assistenza Sereni', 'Assistance aux personnes agees', 'Assistance for older people', 'eu'),
        ('HomeCare Partners', 'Aide a domicile sur mesure', 'Tailored home care', 'eu'),
        ('Residence Age d\'Or', 'Residence services pour seniors', 'Serviced residence for seniors', 'eu'),
    ],
}

FORMATS = [
    ('local', 'Local commercial', 'Retail unit'),
    ('kiosque', 'Kiosque ou ilot', 'Kiosk or cart'),
    ('domicile', 'A domicile', 'Home-based'),
    ('mobile', 'Mobile', 'Mobile'),
    ('master', 'Master franchise / territoire', 'Master franchise / territory'),
]
# Les formats plausibles par metier. Une concession automobile « a domicile »
# n'existe pas ; laisser le hasard en produire une decredibiliserait tout.
# Une boutique hors taxes non plus : elle est dans une aerogare ou a un poste
# frontalier, donc local ou kiosque, jamais mobile.
FORMATS_PAR_CAT = {
    'restauration-rapide': ['local', 'kiosque', 'master'],
    'cafe-boulangerie': ['local', 'kiosque'],
    'restaurant-complet': ['local', 'master'],
    'alimentation': ['local', 'master'],
    'concession-auto': ['local', 'master'],
    'duty-free': ['local', 'kiosque', 'master'],
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
}

# Tranches, en EUROS de reference (voir TAUX_EUR).
TRANCHES = [
    ('t1', 'Moins de 100 000 EUR', 'Under EUR 100,000', 0, 100000),
    ('t2', '100 000 a 250 000 EUR', 'EUR 100,000 to 250,000', 100000, 250000),
    ('t3', '250 000 a 500 000 EUR', 'EUR 250,000 to 500,000', 250000, 500000),
    ('t4', '500 000 EUR a 1 M EUR', 'EUR 500,000 to 1M', 500000, 1000000),
    ('t5', 'Plus de 1 M EUR', 'Over EUR 1M', 1000000, 10 ** 12),
]

# Poids demographique approximatif, pour que le tirage des pays ressemble au
# marche : une enseigne recrute d'abord la ou il y a des candidats.
POIDS_PAYS = {
    'US': 60, 'DE': 22, 'GB': 20, 'FR': 19, 'IT': 17, 'ES': 14, 'PL': 10,
    'CA': 10, 'RO': 5, 'NL': 5, 'BE': 4, 'CZ': 4, 'PT': 4, 'SE': 3, 'GR': 3,
    'HU': 3, 'AT': 3, 'CH': 3, 'DK': 2, 'FI': 2, 'NO': 2, 'IE': 2,
}


# Le pays d'origine d'une enseigne europeenne n'est PAS tire au hasard.
# Un tirage libre produisait « Chippy Corner, fish and chips — Pologne » et
# « Dachwerk Bedachung — Tchequie » : chaque fiche etait plausible isolement,
# et l'ensemble sonnait faux. Le nom porte une langue, la langue porte un
# pays ; on l'ecrit une fois pour toutes. Les noms anglais sont repartis
# volontairement entre le Royaume-Uni, l'Irlande, l'Europe centrale et les
# pays nordiques — une enseigne au nom anglais y est courante.
ORIGINE_EU = {
    'Croq Comptoir': 'FR', 'Wurst Haus': 'DE', 'Pita Meridiana': 'GR',
    'Chippy Corner': 'GB', 'Bolla Pasta': 'IT',
    'Cafe Belleville': 'FR', 'Panetteria Aurora': 'IT', 'Kanelbulle Kaffe': 'SE',
    'Horno Dorado': 'ES', 'Bean & Brick': 'CZ',
    'Brasserie Lumiere': 'FR', 'Osteria del Ponte': 'IT', 'Taberna del Sol': 'ES',
    'The Copper Fork': 'GB', 'Gasthaus Lindenhof': 'DE',
    'Halles Vertes': 'FR', 'Bio Speisekammer': 'DE', 'Mercado Fresco': 'ES',
    'Corner Pantry': 'PL', 'Pescheria Blu': 'IT',
    'Groupe Auto Vendome': 'FR', 'AutoHaus Rheinpark': 'DE',
    'Motori Adriatico': 'IT', 'Northgate Motors': 'GB', 'ElectroMobil Nordic': 'NO',
    'Voyage Hors Taxes': 'BE', 'AeroLux Boutique': 'CH', 'Terminal Parfums': 'FR',
    'Sky Spirits Europe': 'IE', 'Gateway Travel Retail': 'GB',
    'Pneus Express Europe': 'FR', 'Glas Klar Service': 'DE', 'Lavado Cristal': 'ES',
    'BodyShop Direct': 'GB', 'Volt Garage': 'NL',
    'Physio Elan': 'FR', 'OptikKlar': 'DE', 'Sorriso Dental': 'IT',
    'HearWell Clinics': 'GB', 'Kine Equilibre': 'BE',
    'Velo Studio Lumen': 'FR', 'FitHaus 24': 'AT', 'Yoga Serena': 'IT',
    'CrossBase Athletic': 'PL', 'AquaNordic': 'FI',
    'Salon Rive Gauche': 'FR', 'Barbier Kreuzberg': 'DE', 'Nail Atelier': 'HU',
    'Instituto Luz': 'PT', 'Glow Nordic Skin': 'DK',
    'Academie Plume et Chiffres': 'FR', 'CodeKids Europe': 'IE',
    'Lingua Viva': 'IT', 'MatheMax Nachhilfe': 'DE', 'Exam Prep Academy': 'RO',
    'Les Petits Nuages': 'FR', 'Kita Sonnenschein': 'DE', 'Piccoli Passi': 'IT',
    'Bright Corner Nursery': 'GB', 'Duimelot Opvang': 'NL',
    'Compta Facile Europe': 'FR', 'PrintPoint Express': 'GB',
    'TalentLink Recrutement': 'BE', 'Wachstum Beratung': 'AT',
    'DeskShare Europe': 'RO',
    'Cle de Voute Immobilier': 'FR', 'Casa Prima Realty': 'ES',
    'Mietwerk Verwaltung': 'DE', 'Survey & Stone': 'GB', 'Valora Estimation': 'CH',
    'Net Bureau Europe': 'FR', 'Glanz Reinigung': 'DE', 'Brilla Casa': 'IT',
    'HighPane Window Care': 'HU', 'Sinistre Secours': 'BE',
    'Cuisines Atelier Nord': 'FR', 'Dachwerk Bedachung': 'DE',
    'Cantieri Rinnova': 'IT', 'ClearFrame Windows': 'GB',
    'Jardins Paysage Europe': 'CH',
    'Boutique Fil et Lin': 'FR', 'Spielwerk Toys': 'DE', 'Cima Outdoor': 'IT',
    'Casa Deco Iberia': 'PT', 'MobilePoint Europe': 'PL',
    'Patte de Velours': 'FR', 'TierWohl Shop': 'DE', 'Zampe Felici': 'IT',
    'PawSquare Daycare': 'CZ', 'Veterinaria Proxima': 'ES',
    'Colis Point Europe': 'FR', 'Umzug Direkt': 'DE',
    'BoxRoom Self Storage': 'GB', 'Ultimo Miglio Delivery': 'IT',
    'Cargo Lien Europe': 'NL',
    'Presence a Domicile': 'FR', 'SeniorHilfe Pflege': 'DE',
    'Assistenza Sereni': 'IT', 'HomeCare Partners': 'GB',
    'Residence Age d\'Or': 'BE',
}


def pays_de_region(reg):
    return [p[0] for p in PAYS if p[3] == reg]


NA = pays_de_region('na')
EU = [p[0] for p in PAYS if p[3] != 'na']


def slug(t):
    out = []
    for c in t.lower():
        if c.isalnum():
            out.append(c)
        elif out and out[-1] != '-':
            out.append('-')
    return ''.join(out).strip('-')


def tranche(v_eur):
    for cle, _fr, _en, bas, haut in TRANCHES:
        if bas <= v_eur < haut:
            return cle
    return 't5'


def arrondi_utile(v):
    """Arrondir a une precision qui a du sens pour l'ordre de grandeur.

    Une devise faible (le forint, la couronne) produit des nombres a sept
    chiffres : les arrondir au millier laisserait « 41 237 000 », ce qu'aucune
    enseigne n'ecrit. On arrondit a ~3 chiffres significatifs.
    """
    if v <= 0:
        return 0
    import math
    ordre = 10 ** max(0, int(math.floor(math.log10(v))) - 2)
    return int(round(v / ordre) * ordre)


def pays_ouverts(r, origine):
    """Les pays ou l'enseigne recrute. L'origine en fait toujours partie.

    Un tiers des reseaux restent NATIONAUX — c'est la realite du marche, et
    c'est aussi ce qui rend le filtre « pays » utile : un filtre que toutes
    les fiches satisfont ne filtre rien.
    """
    if r.random() < 0.33:
        return [origine]
    meme_region = [p[0] for p in PAYS
                   if p[3] == dict((x[0], x[3]) for x in PAYS)[origine]
                   and p[0] != origine]
    bassin = meme_region[:]
    # Un reseau sur deux deborde de sa region.
    if r.random() < 0.5:
        autres = [p[0] for p in PAYS if p[0] != origine and p[0] not in meme_region]
        bassin += autres
    # Tirage pondere SANS REMISE : cle = alea^(1/poids). Un tri sur
    # « -poids * alea » donnerait presque toujours le pays le plus lourd.
    bassin.sort(key=lambda p: -(r.random() ** (1.0 / POIDS_PAYS[p])))
    n = r.randint(1, min(9, len(bassin)))
    return sorted(set([origine] + bassin[:n]),
                  key=[x[0] for x in PAYS].index)


def construire():
    devise_de = dict((p[0], p[4]) for p in PAYS)
    fiches = []
    for cle, fr, en, ibas, ihaut, dbas, dhaut, red in CATEGORIES:
        for nom, dfr, den, reg in ENSEIGNES[cle]:
            s = slug(nom)
            graine = int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)
            r = random.Random(graine)

            if reg == 'na':
                origine = r.choice(NA)
            else:
                origine = ORIGINE_EU.get(nom)
                if origine is None:
                    origine = sorted(
                        EU, key=lambda p: -(r.random() ** (1.0 / POIDS_PAYS[p])))[0]
            dev = devise_de[origine]

            # Montants tires en euros de reference, puis convertis dans la
            # devise du pays : c'est l'ordre correct. L'inverse (tirer en
            # devise locale puis convertir) donnerait des fourchettes qui ne
            # se comparent plus d'un pays a l'autre.
            eur_bas = r.uniform(ibas, ibas + (ihaut - ibas) * 0.45)
            eur_haut = eur_bas * r.uniform(1.35, 2.3)
            taux = TAUX_EUR[dev]
            bas = arrondi_utile(eur_bas / taux)
            haut = arrondi_utile(eur_haut / taux)
            droit = arrondi_utile(r.uniform(dbas, dhaut) / taux)
            # Les liquidites sont une FRACTION de l'investissement bas, pas un
            # tirage independant : sinon l'apport exige peut depasser le cout
            # total du projet, et la fiche ne veut plus rien dire.
            liquide = arrondi_utile(bas * r.uniform(0.25, 0.45))
            avoir = arrondi_utile(liquide * r.uniform(2.0, 3.5))

            creation = r.randint(1972, 2019)
            debut = min(2024, creation + r.randint(2, 12))
            unites = r.randint(3, 640)
            corpo = min(unites - 1, max(0, int(unites * r.uniform(0.0, 0.25))))

            fiches.append({
                'id': s,
                'nom': nom,
                'categorie': cle,
                'resume': {'fr': dfr, 'en': den},
                'pays_origine': origine,
                'region': dict((p[0], p[3]) for p in PAYS)[origine],
                'devise': dev,
                'investissement': {
                    'bas': bas, 'haut': haut,
                    'eur_bas': int(round(eur_bas)),
                    'tranche': tranche(eur_bas),
                },
                'droit_entree': droit,
                'liquidites': liquide,
                'avoir_net': avoir,
                'redevance': round(r.uniform(*red), 1),
                'fonds_pub': round(r.uniform(1.0, 3.0), 1),
                'annee_creation': creation,
                'annee_franchisage': debut,
                'unites': unites,
                'unites_franchisees': unites - corpo,
                'unites_corpo': corpo,
                'pays': pays_ouverts(r, origine),
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
        'note_taux': ('Les tranches d\'investissement sont classees sur une valeur '
                      'de reference en euros (taux figes). Chaque fiche s\'affiche '
                      'dans sa propre devise.'),
        'categories': [{'cle': c[0], 'fr': c[1], 'en': c[2]} for c in CATEGORIES],
        'pays': [{'cle': p[0], 'fr': p[1], 'en': p[2], 'region': p[3], 'devise': p[4]}
                 for p in PAYS],
        'regions': [{'cle': x[0], 'fr': x[1], 'en': x[2]} for x in REGIONS],
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
    'nom', 'categorie', 'resume_fr', 'resume_en', 'pays_origine', 'devise',
    'investissement_bas', 'investissement_haut', 'droit_entree',
    'liquidites_exigees', 'avoir_net_exige', 'redevance_pct', 'fonds_pub_pct',
    'annee_creation', 'annee_franchisage', 'unites_total', 'unites_franchisees',
    'unites_corpo', 'pays_ouverts', 'format', 'financement',
    'formation_semaines', 'delai_semaines',
]


def modele_csv(fiches):
    chemin = os.path.join(ICI, 'import-modele.csv')
    with open(chemin, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(COLONNES)
        for fi in fiches[:2]:
            w.writerow([
                fi['nom'], fi['categorie'], fi['resume']['fr'], fi['resume']['en'],
                fi['pays_origine'], fi['devise'],
                fi['investissement']['bas'], fi['investissement']['haut'],
                fi['droit_entree'], fi['liquidites'], fi['avoir_net'],
                fi['redevance'], fi['fonds_pub'], fi['annee_creation'],
                fi['annee_franchisage'], fi['unites'], fi['unites_franchisees'],
                fi['unites_corpo'], '|'.join(fi['pays']), fi['format'],
                'oui' if fi['financement'] else 'non',
                fi['formation_semaines'], fi['delai_semaines'],
            ])
    return chemin


if __name__ == '__main__':
    fiches = construire()
    c = ecrire(fiches)
    m = modele_csv(fiches)
    print('%d fiches, %d categories, %d pays, %d devises'
          % (len(fiches), len(CATEGORIES), len(PAYS),
             len(set(f['devise'] for f in fiches))))
    print('%s  (%d octets)' % (c, os.path.getsize(c)))
    print('%s  (%d octets)' % (m, os.path.getsize(m)))
    par_reg = collections.Counter(f['region'] for f in fiches)
    for r in REGIONS:
        print('  %-28s %d' % (r[1], par_reg[r[0]]))
    ouv = collections.Counter()
    for f in fiches:
        for p in f['pays']:
            ouv[p] += 1
    print('  pays les plus ouverts :', ouv.most_common(5))
    print('  pays les moins ouverts :', ouv.most_common()[-3:])
