# Annuaire de franchises — Canada, Etats-Unis, Europe

Le moteur de recherche, les categories, les filtres, la fiche enseigne, la
mise en relation et le depot de fiche par les franchiseurs. Plus une
**section hotellerie a part**, avec ses propres colonnes.

**Demonstration en ligne :**
https://anirudhatalmale6-alt.github.io/annuaire-franchises-demo/
(la section hotellerie : `/hotellerie.html`)

Le nom affiche en haut a gauche est un **placeholder**, marque « marque a
definir ». L'ancien libelle etait a une lettre du nom d'un annuaire qui
existe pour de vrai — pose sur une demonstration, c'est la marque d'un tiers
portee par une page qui n'est pas la sienne.

## Ce que c'est, et ce que ce n'est pas

Le produit d'un annuaire de franchises n'est pas la liste. La liste fait venir
le candidat ; **ce qui se vend, c'est la mise en relation** — la demande
d'information qui part chez le franchiseur. C'est pour ca que « Demander de
l'information » est le bouton principal de chaque carte, et pas un lien en bas
de page.

Les 200 enseignes de l'annuaire generaliste et les 29 marques hotelieres
sont **fictives**, et c'est volontaire :

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
| enseignes | 200 |
| categories | 20, dont **concessionnaires automobiles** et **duty free / boutiques d'aeroport** |
| pays | 22 : Canada, Etats-Unis et 20 pays d'Europe |
| regions | 5 |
| devises | 12, chaque fiche affichee dans la sienne |
| filtres | categorie, region, pays, tranche d'investissement, format d'exploitation, financement propose, nombre minimum d'unites |
| tris | pertinence, investissement croissant/decroissant, unites, franchisage recent, A-Z |
| langues | francais et anglais, y compris le format des montants (`265 000 $ US` / `US$265,000`, `1 280 000 PLN`) |
| controles | **76, tous verts** (`python3 tests.py`) |

L'hotellerie **n'est plus une categorie de cette liste** : voir la section
dediee plus bas.

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

## La section hotellerie

**Fichiers :** `hotels.py` (donnees), `page_hotels.py` (page),
`demo/hotellerie.json`, `demo/hotellerie.html`,
`import-modele-hotellerie.csv`, `tests-hotels.py`, `captures-hotels.py`.

L'hotellerie a ete **sortie** de l'annuaire generaliste. Ce n'est pas une
question de rangement : une enseigne hoteliere ne se compare pas a un
commerce sur les memes colonnes.

| | l'annuaire generaliste | l'hotellerie |
|---|---|---|
| l'investissement | un montant pour le projet | **au nombre de cles** |
| la redevance | une | **deux** : marque, puis commercialisation et fidelite |
| le contrat | une franchise | franchise, **contrat de gestion**, bail, developpement |
| la taille | le format d'exploitation | **une fourchette de cles acceptee** |
| l'enseigne | seule | portee par un **groupe** qui a plusieurs marques |
| l'existant | sans objet | **conversion** d'un hotel deja debout |

Melangee aux autres metiers, elle faussait aussi le filtre par tranche : un
projet a plusieurs millions ecrase les fourchettes de tous les autres.

| | |
|---|---|
| marques | 29 |
| groupes | 10, chacun portant 2 a 4 marques |
| segments | 7 : economique, milieu de gamme, milieu de gamme superieur, haut de gamme, luxe, appart-hotel, lifestyle |
| types de contrat | 4 |
| filtres | segment, type de contrat, investissement par cle, **taille de mon hotel**, conversion, region, pays |
| tris | pertinence, investissement/cle croissant et decroissant, taille du reseau, A-Z |
| langues | francais et anglais |
| controles | **60, tous verts** (`python3 tests-hotels.py`) |

Quatre choix qui portent tout le reste :

1. **Le cout du projet n'est pas tire, il est CALCULE.** C'est
   l'investissement a la cle multiplie par la taille acceptee. Tire a part,
   il finit toujours par contredire le prix a la cle affiche juste au-dessus
   — et c'est le chiffre sur lequel un investisseur decide. Un controle
   verifie l'egalite sur les 29 fiches.

2. **Le filtre « taille de mon hotel » demande l'appartenance, pas un
   minimum.** La question reelle est « mon hotel fait 120 chambres, quelles
   enseignes le prennent » : 120 doit tomber DANS la fourchette acceptee.
   Un filtre « a partir de » aurait repondu a une autre question.

3. **Un contrat de gestion n'existe pas sur un economique de 70 chambres**
   — les honoraires ne paieraient pas l'equipe du groupe. Le tableau des
   contrats possibles est fixe par segment, et deux controles l'imposent :
   aucune enseigne economique en gestion, toute enseigne de luxe en gestion.

4. **Un groupe ne porte jamais deux marques dans le meme segment.** C'est
   ainsi que sont batis les portefeuilles de marques hotelieres ; deux
   marques du meme groupe sur le meme creneau se cannibalisent. Controle.

Et deux details qui se voient : le reseau affiche `hotels x taille moyenne =
cles` (tire a part, on obtenait 40 hotels et 900 cles, soit 22 chambres
l'unite), et le droit d'entree s'ecrit comme dans le metier — **tant par
cle, avec un plancher** — parce que pour un petit hotel c'est le plancher
qui s'applique.

Une seule feuille de style pour les deux pages : `page_hotels.py` la LIT
dans `index.html` et l'injecte. Les deux fichiers restent autonomes — un
seul fichier a televerser, rien a lier — mais le style n'a qu'une source. Un
controle verifie que le bloc partage est identique au caractere pres.

## Remplacer les fiches de demonstration par les vraies

Le format d'entree est dans `import-modele.csv` (point-virgule, UTF-8, deux
lignes remplies en exemple) ; celui de l'hotellerie dans
`import-modele-hotellerie.csv`, qui a ses propres colonnes. Les colonnes suffisent a produire une fiche
complete ; le moteur ne lit rien d'autre. Quand les vraies enseignes arrivent
— les siennes comprises — elles remplacent le fichier sans toucher une ligne
du moteur.

## Reconstruire

```
python3 donnees.py         # demo/catalogue.json + import-modele.csv
python3 tests.py           # 76 controles : donnees, puis moteur dans un navigateur
python3 captures.py        # les 9 captures de l'annuaire

python3 hotels.py          # demo/hotellerie.json + import-modele-hotellerie.csv
python3 page_hotels.py     # demo/hotellerie.html
python3 tests-hotels.py    # 60 controles
python3 captures-hotels.py # les 7 captures de la section
```

**136 controles au total, tous verts.**

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
