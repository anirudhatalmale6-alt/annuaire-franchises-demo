# -*- coding: utf-8 -*-
"""Captures de l'annuaire. Fenetre fixe, jamais full_page : une capture de
page entiere depasse les 2000 px de haut et devient illisible."""

import os
import socket
import subprocess
import sys
import time
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(ICI, 'demo')
from playwright.sync_api import sync_playwright

s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '-b', '127.0.0.1'],
                       cwd=DEMO, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
base = 'http://127.0.0.1:%d/' % port
try:
    for _ in range(80):
        try:
            if 'Annuaire des franchises' in urllib.request.urlopen(base, timeout=2)\
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

        pg.screenshot(path=os.path.join(ICI, 'fr-1-accueil.png'))

        pg.locator('#filtres input[value="duty-free"]').check()
        pg.wait_for_timeout(250)
        pg.mouse.wheel(0, 470)
        pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(ICI, 'fr-2-filtres.png'))
        pg.click('#raz'); pg.wait_for_timeout(200)

        # Une vue qui montre plusieurs devises cote a cote : c'est le point
        # qu'un annuaire multi-pays doit prouver a l'oeil.
        pg.locator('#filtres input[value="eu-est"]').check()
        pg.locator('#filtres input[value="eu-nord"]').check()
        pg.wait_for_timeout(250)
        pg.mouse.wheel(0, 470)
        pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(ICI, 'fr-8-devises.png'))
        pg.click('#raz'); pg.wait_for_timeout(200)
        pg.mouse.wheel(0, -900); pg.wait_for_timeout(200)
        pg.locator('.fiche .cta').first.click()
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'fr-3-fiche.png'))
        pg.locator('#panneau').evaluate('e => e.scrollTop = e.scrollHeight')
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'fr-4-demande.png'))
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(250)

        for i in range(3):
            pg.locator('.fiche .cmp').nth(i).click()
            pg.wait_for_timeout(100)
        pg.click('#cmpgo')
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'fr-5-comparaison.png'))
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(250)

        pg.click('.lang button[data-l="en"]')
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'fr-6-anglais.png'))

        pg.click('.lang button[data-l="fr"]')
        pg.wait_for_timeout(250)
        pg.click('a[data-nav="inscrire"]')
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(ICI, 'fr-9-inscription.png'))
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(250)
        pg.set_viewport_size({'width': 390, 'height': 780})
        pg.wait_for_timeout(400)
        pg.mouse.wheel(0, 520)
        pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(ICI, 'fr-7-mobile.png'))
        nav.close()
finally:
    srv.terminate()

for n in sorted(os.listdir(ICI)):
    if n.startswith('fr-') and n.endswith('.png'):
        print('%-22s %d octets' % (n, os.path.getsize(os.path.join(ICI, n))))
