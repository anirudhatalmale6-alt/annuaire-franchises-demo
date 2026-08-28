# -*- coding: utf-8 -*-
"""Captures de la section hotellerie. Fenetre fixe, jamais full_page."""

import os
import socket
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)

s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port),
                        '-b', '127.0.0.1'],
                       cwd=DEMO, stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT)
base = 'http://127.0.0.1:%d/hotellerie.html' % port
try:
    for _ in range(80):
        try:
            if 'hotelieres' in urllib.request.urlopen(base, timeout=2)\
                    .read().decode('utf-8', 'replace'):
                break
        except Exception:
            pass
        time.sleep(0.25)

    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={'width': 1280, 'height': 800})
        pg.goto(base, wait_until='networkidle')
        pg.wait_for_selector('.fiche')

        pg.screenshot(path=os.path.join(ICI, 'ho-1-accueil.png'))

        # Le point de la section : filtrer par TAILLE d'hotel. On descend sur
        # la grille pour que la capture montre le resultat, pas l'entete.
        pg.select_option('#taille', '120')
        pg.wait_for_timeout(300)
        pg.mouse.wheel(0, 520)
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'ho-2-taille.png'))
        pg.click('#raz'); pg.wait_for_timeout(250)

        # Le contrat de gestion : ce qui n'existe pas dans l'annuaire
        # generaliste.
        pg.locator('.fgrp input[data-g="contrats"][data-v="gestion"]').check()
        pg.wait_for_timeout(300)
        pg.mouse.wheel(0, 520)
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'ho-3-gestion.png'))
        pg.click('#raz'); pg.wait_for_timeout(250)
        pg.mouse.wheel(0, -1200); pg.wait_for_timeout(250)

        pg.locator('.fiche .cta').first.click()
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'ho-4-fiche.png'))
        pg.locator('#panneau').evaluate('e => e.scrollTop = e.scrollHeight')
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'ho-5-dossier.png'))
        pg.click('#voile')
        pg.wait_for_timeout(300)

        pg.click('.lang button[data-l="en"]')
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'ho-6-anglais.png'))
        pg.click('.lang button[data-l="fr"]')
        pg.wait_for_timeout(300)

        pg.set_viewport_size({'width': 390, 'height': 780})
        pg.wait_for_timeout(400)
        pg.mouse.wheel(0, 560)
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'ho-7-mobile.png'))
        nav.close()
finally:
    srv.terminate()

for n in sorted(os.listdir(ICI)):
    if n.startswith('ho-') and n.endswith('.png'):
        print('%-22s %d octets' % (n, os.path.getsize(os.path.join(ICI, n))))
