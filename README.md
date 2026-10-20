# Ce que les adjudications révèlent de la demande pour la dette américaine

Projet de Python pour la data science, ENSAE Paris, 2A, 2026-2027.
Équipe : Diego Mallard, [Personne A], [Personne B].

## Le sujet

L'État américain emprunte en vendant ses titres de dette aux enchères : ce sont les **adjudications**. Pour chacune, le Trésor annonce un montant, les investisseurs proposent des taux, et l'État retient les offres les moins chères jusqu'à atteindre le montant voulu. Le Trésor publie le résultat de chaque adjudication depuis 1979.

Nous utilisons ces résultats pour mesurer **la qualité de la demande pour la dette américaine** et voir ce qui la fait varier.

## Question de recherche

> Que nous apprennent les adjudications du Trésor sur la demande pour la dette américaine, et cette demande se dégrade-t-elle en période de stress sur les marchés ?

1. Comment mesurer la qualité d'une adjudication avec les données publiques ?
2. Qui achète la dette américaine, et comment cela a-t-il évolué ?
3. Les adjudications se passent-elles moins bien quand les marchés sont inquiets (VIX élevé) ou en récession ?

Nous mesurons la qualité d'une adjudication avec trois indicateurs simples :
- le **taux de couverture** (*bid-to-cover*) : montant demandé / montant servi. Plus il est élevé, plus il y avait de demande ;
- la **dispersion des offres** : taux limite − taux médian, en points de base. Des offres serrées signalent une demande solide ;
- la **part des enchérisseurs indirects**, qui regroupent notamment les banques centrales étrangères.

## Données

| Source | Contenu | Accès |
|---|---|---|
| [Fiscal Data](https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/) (Trésor US) | ~11 000 adjudications depuis 1979, ~120 colonnes | API (JSON) |
| [CBOE](https://www.cboe.com/tradable_products/vix/vix_historical_data/) | Indice VIX quotidien depuis 1990 | CSV |
| [NBER](https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions) | Dates des récessions américaines | Scraping |

Tout est public et téléchargé par le code : aucun fichier à télécharger à la main. Les fichiers bruts sont enregistrés dans `data/raw/` (non versionné), ce qui permet de relancer le projet sans retélécharger.

Ce qui demande du nettoyage : l'API renvoie tout en texte avec des `"null"`, plusieurs types de titres ne sont pas comparables entre eux, certaines colonnes n'existent que depuis 2000 ou 2009, et les adjudications de 1979 à 1983 ont des valeurs incohérentes. Nos choix sont documentés dans `docs/journal_decisions.md`.

## Reproduire nos résultats

```bash
git clone <url du dépôt>
cd <dossier du dépôt>
python -m pip install -r requirements.txt
```

Puis ouvrir `rapport.ipynb` et exécuter toutes les cellules (« Run All »).

## Organisation du dépôt

```
├── rapport.ipynb               # LE rendu : s'exécute de bout en bout
├── README.md
├── requirements.txt
├── src/
│   ├── donnees_adjudications.py   # collecte et nettoyage des adjudications
│   ├── donnees_marche.py          # VIX et récessions
│   └── analyse.py                 # indicateurs et graphiques
├── notebooks/                  # brouillons de travail, un par personne
└── docs/
    ├── organisation.md         # qui fait quoi, calendrier, règles Git
    └── journal_decisions.md    # nos choix de nettoyage et leurs raisons
```
