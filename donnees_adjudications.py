"""Collecte et nettoyage des résultats d'adjudications du Trésor américain.

Source : API Fiscal Data, jeu de données « Treasury Securities Auctions Data »
https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/

Ce module produit la table `adjudications` utilisée par `analyse.py`, avec
exactement les colonnes convenues dans `docs/organisation.md` (voir
`COLONNES_CONVENUES`). Fonctions principales :

    telecharger_ou_lire()   : télécharge un fichier JSON, ou le relit s'il existe déjà
    telecharger_brut()      : enchaîne toutes les pages de l'API, tout en texte
    nettoyer()              : types, notes et bonds nominaux, renommage, incohérences
    lignes_incoherentes()   : détail des lignes jugées incohérentes (pour inspection)
    charger_adjudications() : enchaîne les deux précédentes -> table `adjudications`

Pour remplir `data/raw/` (une seule fois, connexion internet requise) :

    python src/donnees_adjudications.py            # télécharge les pages manquantes
    python src/donnees_adjudications.py --forcer   # retélécharge tout
"""

from __future__ import annotations

import json
import re
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------

URL_API = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    "/v1/accounting/od/auctions_query"
)

# Racine du dépôt = dossier parent de src/
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_BRUT = RACINE / "data" / "raw"

# L'API accepte jusqu'à 10 000 lignes par page. 1 000 donne ~12 pages pour
# ~11 000 adjudications : des fichiers de taille raisonnable et peu de requêtes.
TAILLE_PAGE = 1000


# --------------------------------------------------------------------------
# Étape 2 : télécharger ou relire un fichier
# --------------------------------------------------------------------------

def telecharger_ou_lire(
    nom_fichier: str,
    params: dict | None = None,
    url: str = URL_API,
    dossier: Path | str = DOSSIER_BRUT,
    forcer: bool = False,
    pause: float = 0.2,
    tentatives: int = 3,
) -> dict:
    """Renvoie la réponse JSON de l'API, en la mettant en cache dans `dossier`.

    - Si `dossier/nom_fichier` existe (et `forcer` est faux), on relit le
      fichier : aucune requête réseau.
    - Sinon on interroge l'API, on enregistre la réponse telle quelle, puis
      on la renvoie.

    Paramètres
    ----------
    nom_fichier : nom du fichier de cache, par exemple "page_001.json".
    params      : paramètres de la requête (taille de page, numéro, tri...).
    url         : point d'accès de l'API.
    dossier     : dossier du cache (créé s'il n'existe pas).
    forcer      : si vrai, retélécharge même si le fichier existe.
    pause       : délai en secondes après un téléchargement, par politesse
                  envers l'API.
    tentatives  : nombre d'essais en cas d'erreur réseau ou serveur.
    """
    dossier = Path(dossier)
    chemin = dossier / nom_fichier

    if chemin.exists() and not forcer:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)

    dossier.mkdir(parents=True, exist_ok=True)

    derniere_erreur: Exception | None = None
    for essai in range(1, tentatives + 1):
        try:
            reponse = requests.get(url, params=params, timeout=60)
            reponse.raise_for_status()
            contenu = reponse.json()
            break
        except (requests.RequestException, ValueError) as erreur:
            derniere_erreur = erreur
            if essai < tentatives:
                time.sleep(2 * essai)  # attente croissante : 2 s, 4 s...
    else:
        raise RuntimeError(
            f"Échec du téléchargement de {nom_fichier} après {tentatives} essais"
        ) from derniere_erreur

    # On n'écrit le fichier qu'une fois la réponse valide : pas de cache corrompu.
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(contenu, f, ensure_ascii=False)

    time.sleep(pause)
    return contenu


# --------------------------------------------------------------------------
# Étape 3 : enchaîner toutes les pages
# --------------------------------------------------------------------------

def _params_page(numero: int, taille_page: int) -> dict:
    """Paramètres d'une requête pour la page `numero` (la numérotation commence à 1).

    Le tri par date puis par CUSIP rend l'ordre des pages stable d'un
    téléchargement à l'autre, ce qui est indispensable pour ne perdre ni
    dupliquer aucune ligne en passant d'une page à l'autre.
    """
    return {
        "format": "json",
        "sort": "auction_date,cusip",
        "page[size]": taille_page,
        "page[number]": numero,
    }


def telecharger_brut(
    taille_page: int = TAILLE_PAGE,
    dossier: Path | str = DOSSIER_BRUT,
    forcer: bool = False,
) -> pd.DataFrame:
    """Télécharge toutes les adjudications et renvoie une table brute.

    La table est « brute » : toutes les colonnes sont du texte (dtype `str`),
    y compris les nombres, les dates et les valeurs manquantes, que l'API
    renvoie sous la forme de la chaîne "null". Le typage se fait dans
    `nettoyer()`.

    Chaque page est enregistrée dans `dossier/page_XXX.json`. Un second appel
    relit ces fichiers sans toucher au réseau (sauf si `forcer=True`).
    """
    dossier = Path(dossier)

    # La première page nous apprend combien il y en a en tout.
    premiere = telecharger_ou_lire(
        "page_001.json",
        params=_params_page(1, taille_page),
        dossier=dossier,
        forcer=forcer,
    )
    meta = premiere["meta"]
    nb_pages = int(meta["total-pages"])
    nb_total = int(meta["total-count"])

    # Un cache écrit avec une autre taille de page mélangerait les pages.
    if len(premiere["data"]) != min(taille_page, nb_total):
        raise ValueError(
            f"{dossier / 'page_001.json'} ne contient pas {taille_page} lignes : "
            "cache écrit avec une autre taille de page. Relancer avec forcer=True."
        )

    lignes = list(premiere["data"])
    for numero in range(2, nb_pages + 1):
        page = telecharger_ou_lire(
            f"page_{numero:03d}.json",
            params=_params_page(numero, taille_page),
            dossier=dossier,
            forcer=forcer,
        )
        lignes.extend(page["data"])

    # Garde-fou : on doit avoir exactement le nombre de lignes annoncé par l'API.
    if len(lignes) != nb_total:
        raise ValueError(
            f"{len(lignes)} lignes reçues, mais l'API en annonce {nb_total}. "
            f"Supprimer {dossier} et relancer, ou appeler avec forcer=True."
        )

    # Tout en texte : on ne laisse pas pandas deviner les types. L'API renvoie
    # déjà des chaînes ; si jamais un vrai null JSON apparaît, on le ramène à
    # "null" pour que nettoyer() n'ait qu'un seul cas à traiter.
    lignes_texte = [
        {cle: "null" if valeur is None else str(valeur) for cle, valeur in ligne.items()}
        for ligne in lignes
    ]
    return pd.DataFrame(lignes_texte, dtype=str)


# --------------------------------------------------------------------------
# Étapes 4 à 7 : nettoyage
# --------------------------------------------------------------------------

# Les différentes façons dont l'API (ou un export) écrit « pas de valeur ».
VALEURS_NULLES = ["null", "", "None", "nan", "NaN", "N/A"]

# Colonnes à ne jamais convertir en nombre (un CUSIP peut être 100 % chiffres).
COLONNES_TEXTE = {"cusip", "security_type", "security_term"}

# Étape 5 : seuls ces types sont gardés. Les TIPS (indexés sur l'inflation) et
# les titres à taux variable ne sont pas comparables à des titres nominaux, que
# l'API les signale par un type à part ou par un indicateur "Yes".
TYPES_CONSERVES = ("Note", "Bond")
INDICATEURS_NON_NOMINAUX = ("tips", "floating_rate", "inflation_index_security")

# Étape 7 : maturités « normales » des notes et bonds, en années.
# Le `terme` de la table est le terme d'origine du titre (`original_security_term`) :
# une réouverture est donc rattachée à son titre d'origine (« 10-Year », et non
# « 9-Year 10-Month »). Il reste quelques termes d'origine atypiques (« 5-Year 2-Month ») ;
# on les rattache à la maturité standard la plus proche si l'écart est d'au plus 6 mois.
TERMES_STANDARD = (2, 3, 4, 5, 7, 10, 20, 30)
TOLERANCE_TERME = 0.5

# Étape 6 : colonne de l'API -> colonne de la table `adjudications`.
# Toutes ces colonnes de l'API doivent exister (sinon erreur explicite).
#
# 1) Les colonnes convenues dans docs/organisation.md : c'est la table livrée.
RENOMMAGE_CONVENU = {
    "auction_date": "date",
    "original_security_term": "terme",        # terme d'origine pour une réouverture
    "reopening": "reouverture",
    "auction_format": "format",
    "high_yield": "taux_limite",
    "avg_med_yield": "taux_median",
    "total_accepted": "montant",
    "bid_to_cover_ratio": "couverture",
    "comp_accepted": "servi_comp",
    "primary_dealer_accepted": "servi_dealers",
    "direct_bidder_accepted": "servi_directs",
    "indirect_bidder_accepted": "servi_indirects",
}
COLONNES_CONVENUES = list(RENOMMAGE_CONVENU.values())

# 2) Colonnes de travail : nécessaires aux règles de l'étape 7 ou utiles pour
#    inspecter les lignes, mais hors du format convenu. Elles ne sont renvoyées
#    qu'avec `nettoyer(..., avec_complements=True)`.
RENOMMAGE_COMPLEMENTAIRE = {
    "cusip": "cusip",
    "security_type": "type_titre",
    "security_term": "terme_residuel",
    "issue_date": "date_emission",
    "maturity_date": "date_echeance",
    "total_tendered": "montant_demande",
    "low_yield": "taux_bas",
    "offering_amt": "montant_offert",
    "int_rate": "taux_coupon",
}

# Au-delà de cette part de lignes écartées comme incohérentes, on prévient :
# une règle est probablement mal calibrée.
SEUIL_ALERTE_INCOHERENCES = 0.01


def _convertir_types(brut: pd.DataFrame) -> pd.DataFrame:
    """Étape 4 : "null" -> valeur manquante, puis dates, booléens et nombres.

    Le type de chaque colonne est détecté à partir de son contenu, pour ne pas
    dépendre de la liste exacte des ~120 colonnes de l'API :
      - nom terminant par "_date"  -> date (AAAA-MM-JJ), si toutes les valeurs s'y prêtent ;
      - uniquement "Yes" / "No"    -> booléen ;
      - tout se lit comme un nombre -> nombre ;
      - sinon                      -> texte.
    Une colonne n'est convertie que si TOUTES ses valeurs non manquantes passent
    la conversion : on ne perd jamais une valeur en silence.
    """
    df = brut.copy()
    df = df.mask(df.isin(VALEURS_NULLES))  # "null" -> valeur manquante

    for nom in df.columns:
        serie = df[nom]
        if nom in COLONNES_TEXTE or "cusip" in nom or serie.notna().sum() == 0:
            continue
        nb_valeurs = serie.notna().sum()

        if nom.endswith("_date"):
            conv = pd.to_datetime(serie, format="%Y-%m-%d", errors="coerce")
            if conv.notna().sum() == nb_valeurs:
                df[nom] = conv
                continue
            # Un nom en « _date » ne garantit pas une date (ref_cpi_on_dated_date est
            # un indice) : on essaie le nombre ci-dessous avant de laisser en texte.

        if set(serie.dropna().unique()) <= {"Yes", "No"}:
            df[nom] = serie.map({"Yes": True, "No": False}).astype("boolean")
            continue

        conv = pd.to_numeric(serie, errors="coerce")
        if conv.notna().sum() == nb_valeurs:
            df[nom] = conv
        elif nom.endswith("_date"):
            warnings.warn(f"Colonne {nom} : ni date ni nombre, laissée en texte.")
    return df


def _garder_nominaux(df: pd.DataFrame) -> pd.DataFrame:
    """Étape 5 : notes et bonds nominaux uniquement."""
    types = df["security_type"].str.strip()
    masque = types.isin(TYPES_CONSERVES)
    if not masque.any():
        raise ValueError(
            "Aucun titre de type Note ou Bond. Types présents : "
            f"{types.value_counts().to_dict()}"
        )
    for nom in INDICATEURS_NON_NOMINAUX:
        # Un indicateur absent ou mal typé ne filtre rien (voir bilan).
        if nom in df.columns and str(df[nom].dtype) == "boolean":
            masque &= ~df[nom].fillna(False).astype(bool)
    return df[masque].copy()


def _ajouter_termes(df: pd.DataFrame) -> pd.DataFrame:
    """Étape 7 (termes atypiques) : durée en années, maturité de référence, drapeau.

    - terme_annees   : durée exacte ("9-Year 10-Month" -> 9.83) ;
    - terme_ref      : maturité standard la plus proche (2, 3, 5, 7, 10, 20, 30...)
                       si l'écart est d'au plus 6 mois, sinon valeur manquante ;
    - terme_atypique : vrai si la durée exacte n'est pas une maturité standard
                       (termes d'origine particuliers, ou maturités disparues comme 6 ans).

    Calculé sur la colonne `terme` (terme d'origine).
    """
    texte = df["terme"].astype("string")
    annees = pd.to_numeric(
        texte.str.extract(r"(\d+)\s*-?\s*Year", flags=re.IGNORECASE, expand=False),
        errors="coerce",
    )
    mois = pd.to_numeric(
        texte.str.extract(r"(\d+)\s*-?\s*Month", flags=re.IGNORECASE, expand=False),
        errors="coerce",
    )
    exact = (annees.fillna(0) + mois.fillna(0) / 12).where(annees.notna() | mois.notna())
    exact = exact.to_numpy(dtype=float, na_value=np.nan)

    standard = np.array(TERMES_STANDARD, dtype=float)
    ecarts = np.abs(np.nan_to_num(exact, nan=1e9)[:, None] - standard[None, :])
    proche = standard[ecarts.argmin(axis=1)]
    dans_tolerance = ecarts.min(axis=1) <= TOLERANCE_TERME

    df = df.copy()
    df["terme_annees"] = exact
    df["terme_ref"] = pd.array(np.where(dans_tolerance, proche, np.nan), dtype="Int64")
    df["terme_atypique"] = ~np.isin(exact, standard)
    return df


def lignes_incoherentes(df: pd.DataFrame) -> pd.DataFrame:
    """Étape 7 (lignes incohérentes) : une colonne booléenne par règle.

    Prend la table de `nettoyer(..., avec_complements=True)` (les règles utilisent
    des colonnes de travail). Une valeur manquante ne déclenche jamais une règle.

      - couverture et montant servi doivent être strictement positifs ;
      - le montant servi ne peut pas dépasser le montant demandé (marge de 1 %) ;
      - taux limite >= taux médian >= taux bas ;
      - émission le jour de l'adjudication ou après ; échéance après l'émission.
    """
    r = pd.DataFrame(index=df.index)
    r["couverture_non_positive"] = df["couverture"] <= 0
    r["montant_servi_non_positif"] = df["montant"] <= 0
    r["servi_superieur_au_demande"] = df["montant"] > 1.01 * df["montant_demande"]
    r["taux_limite_sous_median"] = df["taux_limite"] < df["taux_median"] - 1e-6
    r["taux_median_sous_bas"] = df["taux_median"] < df["taux_bas"] - 1e-6
    r["emission_avant_adjudication"] = df["date_emission"] < df["date"]
    r["echeance_avant_emission"] = df["date_echeance"] <= df["date_emission"]
    return r.fillna(False).astype(bool)


def nettoyer(
    brut: pd.DataFrame,
    ecarter_incoherentes: bool = True,
    avec_complements: bool = False,
) -> pd.DataFrame:
    """Transforme la table brute de `telecharger_brut()` en table `adjudications`.

    Étapes : 4 (types), 5 (notes et bonds nominaux avec résultat), 6 (renommage et
    sélection des colonnes), 7 (lignes incohérentes, termes atypiques). Chaque
    décision est expliquée dans docs/journal_decisions.md.

    Par défaut, la table a exactement les colonnes de `COLONNES_CONVENUES`
    (docs/organisation.md), triée par date puis CUSIP. Le compte de lignes à chaque
    étape est dans `resultat.attrs["bilan"]`.

    - `ecarter_incoherentes=False` garde les lignes incohérentes et les repère par
      une colonne booléenne `incoherente` (avec `lignes_incoherentes()` pour le détail).
    - `avec_complements=True` ajoute les colonnes de travail (`RENOMMAGE_COMPLEMENTAIRE`)
      et les colonnes de l'étape 7b (`terme_annees`, `terme_ref`, `terme_atypique`).
    """
    renommage = {**RENOMMAGE_CONVENU, **RENOMMAGE_COMPLEMENTAIRE}
    manquantes = [c for c in renommage if c not in brut.columns]
    if manquantes:
        raise KeyError(
            f"Colonnes absentes de la table brute : {manquantes}. "
            f"Colonnes disponibles : {sorted(brut.columns)}"
        )
    bilan = {"lignes_brutes": len(brut)}
    bilan["types_titres_bruts"] = brut["security_type"].value_counts().to_dict()

    df = _convertir_types(brut)                       # étape 4
    nb_avant_exclusion = int(df["security_type"].str.strip().isin(TYPES_CONSERVES).sum())
    df = _garder_nominaux(df)                         # étape 5
    bilan["retires_tips_ou_taux_variable"] = nb_avant_exclusion - len(df)

    # Une adjudication annoncée mais sans résultat (montant servi manquant) n'est pas
    # une observation : on l'écarte avant tout calcul.
    sans_resultat = df["total_accepted"].isna()
    bilan["retires_sans_resultat"] = int(sans_resultat.sum())
    df = df[~sans_resultat]
    bilan["notes_et_bonds_nominaux"] = len(df)

    df = df[list(renommage)].rename(columns=renommage)  # étape 6
    df["terme"] = df["terme"].str.strip()
    df["reouverture"] = df["reouverture"].astype(bool)

    sans_date = df["date"].isna()                     # sans date : jointure impossible
    bilan["sans_date_adjudication"] = int(sans_date.sum())
    df = df[~sans_date]

    regles = lignes_incoherentes(df)                  # étape 7
    ecartees = regles.any(axis=1)
    bilan["incoherentes_ecartees"] = int(ecartees.sum())
    bilan["incoherentes_par_regle"] = {k: int(v) for k, v in regles.sum().items() if v}
    if ecartees.mean() > SEUIL_ALERTE_INCOHERENCES:
        warnings.warn(
            f"{ecartees.sum()} lignes écartées comme incohérentes "
            f"({ecartees.mean():.1%}) : vérifier les règles de lignes_incoherentes()."
        )
    if ecarter_incoherentes:
        df = df[~ecartees]
    else:
        df = df.assign(incoherente=ecartees)

    df = _ajouter_termes(df)
    bilan["termes_atypiques_gardes"] = int(df["terme_atypique"].sum())
    bilan["sans_terme_ref"] = int(df["terme_ref"].isna().sum())

    df = df.sort_values(["date", "cusip"]).reset_index(drop=True)
    if not avec_complements:
        colonnes = COLONNES_CONVENUES + (["incoherente"] if "incoherente" in df.columns else [])
        df = df[colonnes]
    bilan["lignes_finales"] = len(df)
    df.attrs["bilan"] = bilan
    return df


def charger_adjudications(forcer: bool = False) -> pd.DataFrame:
    """Point d'entrée pour le reste du projet : renvoie la table `adjudications`.

    Télécharge (ou relit dans data/raw/) toutes les pages, puis nettoie.
    """
    return nettoyer(telecharger_brut(forcer=forcer))


def main(argv: list[str] | None = None) -> None:
    """Remplit `data/raw/` avec toutes les pages de l'API (voir l'en-tête du module)."""
    import argparse

    parseur = argparse.ArgumentParser(description=main.__doc__)
    parseur.add_argument("--forcer", action="store_true",
                         help="retélécharge même si les fichiers existent")
    args = parseur.parse_args(argv)

    brut = telecharger_brut(forcer=args.forcer)
    fichiers = sorted(DOSSIER_BRUT.glob("page_*.json"))
    print(f"{len(fichiers)} fichiers dans {DOSSIER_BRUT}")
    print(f"{len(brut):,} adjudications, {brut.shape[1]} colonnes")


if __name__ == "__main__":
    main()
