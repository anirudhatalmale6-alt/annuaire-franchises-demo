# Annuaire de franchises — Canada, Etats-Unis, Europe

Le moteur de recherche, les categories, les filtres, la fiche enseigne, la
mise en relation et le depot de fiche par les franchiseurs.

**Demonstration en ligne :**
https://anirudhatalmale6-alt.github.io/annuaire-franchises-demo/

## Ce que c'est, et ce que ce n'est pas

Le produit d'un annuaire de franchises n'est pas la liste. La liste fait venir
le candidat ; **ce qui se vend, c'est la mise en relation** — la demande
d'information qui part chez le franchiseur. C'est pour ca que « Demander de
l'information » est le bouton principal de chaque carte, et pas un lien en bas
de page.

Les 210 enseignes affichees sont **fictives**, et c'est volontaire :

- Je ne recopie pas la base de franchisedirect.com. C'est leur actif, et une
  fiche recopiee est fausse le jour ou l'enseigne change son droit d'entree.
- Je n'invente pas de montants sur de vraies marques. Un droit d'entree devine
  sur une enseigne reelle, c'est une information financiere fausse publiee
  sous le nom de quelqu'un d'autre.

Les montants sont tires **dans les bandes reelles de chaque metier** (un cafe
et une concession automobile n'ont pas le meme apport), avec une graine fixe :
deux reconstructions donnent le meme fichier, au caractere pres.

## Le moteur, dans le detail

| | |
|---|---|
| enseignes | 210 |
| categories | 21, dont **concessionnaires automobiles** et **duty free / boutiques d'aeroport** |
| pays | 22 : Canada, Etats-Unis et 20 pays d'Europe |
| regions | 5 |
| devises | 12, chaque fiche affichee dans la sienne |
| filtres | categorie, region, pays, tranche d'investissement, format d'exploitation, financement propose, nombre minimum d'unites |
| tris | pertinence, investissement croissant/decroissant, unites, franchisage recent, A-Z |
| langues | francais et anglais, y compris le format des montants (`265 000 $ US` / `US$265,000`, `1 280 000 PLN`) |
| controles | **76, tous verts** (`python3 tests.py`) |

### Le multi-devises, en une phrase

Chaque fiche s'affiche dans la devise de son pays — une enseigne polonaise
annonce des zlotys. Mais le **filtre** et le **tri** par investissement se font
sur une valeur de reference commune en euros, sinon « moins de 250 000 » ne
veut rien dire d'un pays a l'autre, et une devise faible remonterait en tete
de toutes les listes parce que ses nombres sont plus gros. Les taux de
reference sont figes dans `donnees.py` et ne servent **qu'au classement** : sur
le site reel, ils se remplacent par un flux de taux et rien d'autre ne bouge.

Quatre choix qui ne se voient pas mais qui comptent :

1. **Les compteurs a cote des cases predisent le resultat.** Le « 63 » a cote
   d'« Allemagne » est le nombre de fiches qui resteraient si on cochait cette
   case, les autres filtres restant en place. Un compteur
   calcule sur le resultat final afficherait « 0 » partout : exact, et
   parfaitement inutile. Un controle verifie que le chiffre annonce est bien
   celui obtenu apres le clic.

2. **Les fourchettes sont coherentes entre elles.** Les liquidites exigees ne
   depassent jamais le cout du projet, l'avoir net ne descend jamais sous les
   liquidites, on ne franchise jamais avant d'avoir cree l'enseigne, et
   franchisees + succursales = total. Cinq controles, parce qu'un candidat lit
   ces chiffres pour decider s'il peut se le permettre.

3. **Les formats sont plausibles par metier.** Une concession automobile « a
   domicile », ou une boutique hors taxes « mobile », suffiraient a faire
   fermer l'onglet. Deux controles l'interdisent.

4. **Le pays d'origine d'une enseigne europeenne est ecrit, pas tire au sort.**
   Le tirage libre produisait « Chippy Corner, fish and chips — Pologne ».
   Chaque fiche etait plausible seule, l'ensemble sonnait faux. Un controle
   verifie que les 105 enseignes europeennes ont toutes leur pays declare, et
   qu'aucune entree de la table ne designe une enseigne qui n'existe plus.

## Remplacer les fiches de demonstration par les vraies

Le format d'entree est dans `import-modele.csv` (point-virgule, UTF-8, deux
lignes remplies en exemple). Les colonnes suffisent a produire une fiche
complete ; le moteur ne lit rien d'autre. Quand les vraies enseignes arrivent
— les siennes comprises — elles remplacent le fichier sans toucher une ligne
du moteur.

## Reconstruire

```
python3 donnees.py    # fabrique demo/catalogue.json + import-modele.csv
python3 tests.py      # 76 controles : donnees, puis moteur dans un vrai navigateur
python3 captures.py   # les 9 captures
```

## Comment un annuaire grandit

Pas en recopiant celui du voisin : **en faisant deposer leur fiche aux
franchiseurs**. C'est le formulaire « Inscrire une enseigne » de l'entete, et
c'est le vrai moteur de croissance du produit. Un annuaire de reference se
mesure au nombre d'enseignes qui ont choisi d'y etre, pas au nombre de lignes
copiees.

## Ce qui n'y est pas encore, et qui viendra

- L'espace franchiseur : l'enseigne met sa fiche a jour elle-meme et suit ses
  demandes.
- Le suivi des demandes cote candidat.
- Les pages par categorie et par pays, adressables et indexables (c'est ce
  qui amene le trafic sur ce type de site).
- La qualification du candidat avant transmission au franchiseur : c'est ce
  qui fait la valeur d'une demande, et donc son prix.
