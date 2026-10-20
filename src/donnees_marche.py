"""Contexte de marché : VIX et récessions.
Responsable : Personne B.

Fonction finale utilisée par le rapport : charger_marche().
Format de sortie : voir docs/organisation.md, table `marche`.
"""
import io
import re

import pandas as pd

from donnees_adjudications import DOSSIER_BRUT, telecharger_ou_lire

URL_VIX = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"
URL_NBER = "https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions"


def charger_vix():
    """Série du VIX (clôture), indexée par date.

    Indices :
    - texte = telecharger_ou_lire(URL_VIX, DOSSIER_BRUT / "vix.csv")
    - pd.read_csv(io.StringIO(texte)) ; regarder les noms de colonnes (DATE, CLOSE)
    - les dates sont au format mois/jour/année : pd.to_datetime(..., format="%m/%d/%Y")
    """
    raise NotImplementedError


def charger_recessions():
    """DataFrame avec une ligne par récession : colonnes `debut` et `fin` (premier jour du mois).

    La page du NBER contient un tableau de dates « pic » (début) et « creux » (fin),
    écrites comme "December 2007 (2007Q4)".
    Indices :
    - texte = telecharger_ou_lire(URL_NBER, DOSSIER_BRUT / "nber.html")
    - pd.read_html(io.StringIO(texte))[0] récupère le tableau (testé, nécessite lxml), MAIS :
      les 2 premières lignes sont des en-têtes, la 1re ligne de données n'a qu'un creux (1854),
      et les dernières lignes sont des moyennes par période ("1945-2020"...) à retirer ;
    - pour transformer "December 2007 (2007Q4)" en date : garder le texte avant la parenthèse
      (.str.split(" \\(").str[0]) puis pd.to_datetime(..., format="%B %Y") ;
    - vérifier le résultat : il doit y avoir 34 récessions depuis 1857, la dernière en 2020.
    """
    raise NotImplementedError


def charger_marche():
    """Table quotidienne : vix, recession (0/1), stress (bas / moyen / haut).

    Indices :
    - recession : un jour vaut 1 s'il est entre le mois qui SUIT le début et le mois de fin inclus
      (convention du NBER)
    - stress : pd.qcut(vix, 3, labels=["bas", "moyen", "haut"])
    """
    raise NotImplementedError
