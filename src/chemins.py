# -*- coding: utf-8 -*-
"""Ou se trouvent les pages servies.

En local, les pages sont dans `demo/` a cote des sources. Dans le depot
livre, elles sont A LA RACINE et les sources dans `src/` — c'est de la
racine que GitHub Pages les sert.

Sans cette fonction, un `python3 hotels.py` lance depuis `src/` ecrit son
JSON dans `src/demo/`, un dossier que personne ne sert : le script dit
« ecrit », la page reste vide, et rien ne signale l'ecart.
"""

import os


def dossier_pages(ici):
    demo = os.path.join(ici, 'demo')
    if os.path.isdir(demo):
        return demo
    parent = os.path.dirname(ici)
    if os.path.isfile(os.path.join(parent, 'index.html')):
        return parent
    return demo
