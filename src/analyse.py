"""Indicateurs de qualité des adjudications et graphiques.
Responsable : Diego.

Règles du cours pour les graphiques : axes nommés avec unités, légende utile, titre clair,
et chaque graphique commenté dans le rapport (ce qu'il montre, ce qu'il confirme ou contredit).
"""
import matplotlib.pyplot as plt
import pandas as pd


def ajouter_indicateurs(adjudications):
    """Ajoute les colonnes :
    - dispersion_pb = (taux_limite - taux_median) * 100
    - part_dealers, part_directs, part_indirects = servi_xxx / servi_comp
    - annee
    """
    raise NotImplementedError


def joindre_marche(adjudications, marche):
    """Ajoute à chaque adjudication le VIX, la récession et le stress de la VEILLE
    (on n'utilise jamais une information connue après l'adjudication).

    Indice : pd.merge_asof(adjudications.sort_values("date"), marche, left_on="date",
    right_index=True, allow_exact_matches=False)
    """
    raise NotImplementedError


def tableau_par_groupe(table, groupe, colonnes):
    """Statistiques descriptives (nombre, moyenne, médiane, écart-type) de `colonnes` par `groupe`.
    Indice : table.groupby(groupe)[colonnes].agg(["count", "mean", "median", "std"])
    """
    raise NotImplementedError


def graphique_evolution(table, colonne, titre, unite):
    """Évolution annuelle d'un indicateur (médiane par année), avec les récessions en gris."""
    raise NotImplementedError


def graphique_par_groupe(table, colonne, groupe, titre, unite):
    """Boîtes à moustaches de `colonne` par `groupe` (terme, stress, récession, format...)."""
    raise NotImplementedError
