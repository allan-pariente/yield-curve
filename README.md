# Ce que les adjudications révèlent de la demande pour la dette américaine

Projet de Python pour la data science, ENSAE Paris, 2A, 2026-2027.
Équipe : Allan Pariente, Benjamin, Diego Mallard.

## Le sujet

L'État américain emprunte en vendant ses titres de dette aux enchères : ce sont les adjudications. Pour chacune, le Trésor annonce un montant, les investisseurs proposent des taux, et l'État retient les offres les moins chères jusqu'à atteindre le montant voulu. Le Trésor publie le résultat de chaque adjudication depuis 1979.

Nous utilisons ces résultats pour mesurer la qualité de la demande pour la dette américaine et voir ce qui la fait varier.

## Question de recherche

> Que nous apprennent les adjudications du Trésor sur la demande pour la dette américaine, et cette demande se dégrade-t-elle en période de stress sur les marchés ?

1. Comment mesurer la qualité d'une adjudication avec les données publiques ?
2. Qui achète la dette américaine, et comment cela a-t-il évolué ?
3. Les adjudications se passent-elles moins bien quand les marchés sont inquiets (VIX élevé) ou en récession ?

Nous mesurons la qualité d'une adjudication avec trois indicateurs simples :
- le taux de couverture (*bid-to-cover*) : montant demandé / montant servi. Plus il est élevé, plus il y avait de demande ;
- la dispersion des offres : taux limite - taux médian, en points de base. Des offres serrées signalent une demande solide ;
- la part des enchérisseurs indirects, qui regroupent notamment les banques centrales étrangères.

## Données

| Source | Contenu | Accès |
|---|---|---|
| [Fiscal Data](https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/) (Trésor US) | ~11 000 adjudications depuis 1979, ~120 colonnes | API (JSON) |
| [CBOE](https://www.cboe.com/tradable_products/vix/vix_historical_data/) | Indice VIX quotidien depuis 1990 | CSV |
| [NBER](https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions) | Dates des récessions américaines | Scraping |

Tout est public et téléchargé par le code : aucun fichier à télécharger à la main. Les fichiers bruts sont enregistrés dans `data/raw/` (non versionné), ce qui permet de relancer le projet sans retélécharger.

Ce qui demande du nettoyage : l'API renvoie tout en texte avec des `"null"`, plusieurs types de titres ne sont pas comparables entre eux, certaines colonnes n'existent que depuis 2000 ou 2009, et les adjudications de 1979 à 1983 ont des valeurs incohérentes. Nos choix sont documentés dans `docs/journal_decisions.md`.

## Pipeline : qui fait quoi, dans quel ordre

```
API Fiscal Data --> [Allan] donnees_adjudications.py --> table adjudications --+
                                                                                |
CSV CBOE (VIX) ---+                                                             +--> [Diego] analyse.py --> rapport.ipynb
                  +--> [Benjamin] donnees_marche.py ---> table marche ---------+
Page NBER --------+
```

Les colonnes exactes des deux tables sont fixées dans `docs/organisation.md`. Tant que chacun les respecte, personne n'attend personne : Diego peut commencer ses graphiques avec une petite table inventée au même format.

### Allan : les adjudications

| Étape | Fonction | Ce qu'on obtient |
|---|---|---|
| 1. Télécharger une page de l'API et l'explorer | (notebook 01) | Comprendre les ~120 colonnes |
| 2. Télécharger ou relire un fichier | `telecharger_ou_lire()` | Fichiers bruts dans `data/raw/` |
| 3. Enchaîner toutes les pages | `telecharger_brut()` | 11 154 lignes, tout en texte |
| 4. Remplacer les "null", convertir dates et nombres | `nettoyer()` | Vrais types |
| 5. Garder les notes et bonds nominaux | `nettoyer()` | 2 367 lignes |
| 6. Renommer les colonnes au format convenu | `nettoyer()` | Table `adjudications` |
| 7. Traiter les 7 lignes incohérentes et les termes atypiques | `nettoyer()` | Décisions notées dans `docs/journal_decisions.md` |
| 8. Rédiger les parties 2 et 3 du rapport, et la 5.2 (qui achète ?) | `rapport.ipynb` | |

### Benjamin : le contexte de marché

| Étape | Fonction | Ce qu'on obtient |
|---|---|---|
| 1. Télécharger le VIX | `charger_vix()` | Série quotidienne depuis 1990 |
| 2. Récupérer les récessions sur la page du NBER | `charger_recessions()` | 34 récessions, la dernière en 2020 |
| 3. Construire la table quotidienne | `charger_marche()` | Table `marche` : vix, recession, stress |
| 4. Rédiger la partie 2 (sources de marché) et la 5.3 (stress et récessions) | `rapport.ipynb` | |

### Diego : l'analyse et le rapport

| Étape | Fonction | Ce qu'on obtient |
|---|---|---|
| 1. Calculer les indicateurs | `ajouter_indicateurs()` | dispersion_pb, parts des enchérisseurs |
| 2. Joindre le marché de la veille | `joindre_marche()` | Une table unique pour l'analyse |
| 3. Tableaux descriptifs | `tableau_par_groupe()` | Statistiques par terme, stress, récession |
| 4. Graphiques | `graphique_evolution()`, `graphique_par_groupe()` | Figures du rapport |
| 5. Assembler le rapport, rédiger les parties 1, 4 et 5.1 | `rapport.ipynb` | |
| 6. Bonus si tout est fini | | Comparaison avec la courbe des taux, ou avant/après 1998 |

### Ensemble

- Résumé, limites et conclusion du rapport.
- Test final : quelqu'un qui n'a pas écrit le code clone le dépôt sur une autre machine et lance "Run All" sur `rapport.ipynb`.
- Le calendrier semaine par semaine est dans `docs/organisation.md`.

## Reproduire nos résultats

```bash
git clone <url du dépôt>
cd <dossier du dépôt>
python -m pip install -r requirements.txt
```

Puis ouvrir `rapport.ipynb` et exécuter toutes les cellules ("Run All").

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
