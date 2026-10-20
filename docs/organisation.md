# Organisation

Objectif : un projet simple, propre et fini. Mieux vaut trois analyses bien commentées que dix à moitié faites. Tout ce qui est marqué *bonus* ne se fait que si le reste est terminé.

## Qui fait quoi

### Allan : les adjudications (`src/donnees_adjudications.py`)
1. Télécharger toutes les adjudications depuis l'API (plusieurs pages à enchaîner).
2. Remplacer les `"null"` par des valeurs manquantes, convertir les dates et les nombres.
3. Ne garder que les notes et bonds nominaux (on retire bills, TIPS, FRN, CMB : ils ne sont pas cotés de la même façon). Compter combien de lignes on retire à chaque étape.
4. Repérer les 7 adjudications de 1979-1983 où le taux limite est inférieur au taux médian (impossible en principe), et décider quoi en faire.
5. Écrire ces choix dans `docs/journal_decisions.md`.

Livre : la table `adjudications` (format ci-dessous).

### Benjamin : le contexte de marché (`src/donnees_marche.py`)
1. Télécharger le VIX (un fichier CSV).
2. Récupérer les dates des récessions sur la page du NBER (scraping).
3. Construire une table quotidienne : VIX, récession oui/non, niveau de stress (bas, moyen, haut).

Livre : la table `marche` (format ci-dessous).

### Diego : l'analyse (`src/analyse.py`)
1. Calculer les indicateurs : dispersion, parts des types d'enchérisseurs.
2. Joindre les adjudications au contexte de marché de la veille.
3. Faire les graphiques et les tableaux du rapport, assembler `rapport.ipynb`.
4. *Bonus* : comparer le taux des adjudications à la courbe des taux du marché, et montrer pourquoi cette comparaison est bruitée (déjà testée, résultats dans le journal).

### Tout le monde
- Chacun rédige les commentaires de ses propres résultats dans le rapport.
- Chacun doit pouvoir expliquer tout le projet à l'oral.

## Format des tables échangées

Chacun livre une fonction qui renvoie un DataFrame avec exactement ces colonnes. Si on veut changer, on se prévient.

Conventions : taux en % (4.25 = 4,25 %), écarts en points de base (pb), dates au format `datetime`, valeurs manquantes en `NaN`.

`adjudications` (A) : une ligne par adjudication de note ou bond nominal.

| Colonne | Contenu |
|---|---|
| `date` | Date de l'adjudication |
| `terme` | `2-Year`, `10-Year`... (terme d'origine pour une réouverture) |
| `reouverture` | `True` / `False` |
| `format` | `Price-Based` (1979-83), `Multi-Price` (jusqu'en 1998) ou `Single-Price` |
| `taux_limite` | Taux de la dernière offre servie (%) |
| `taux_median` | Taux médian, ou moyen avant 1998 (%) |
| `montant` | Montant adjugé ($) |
| `couverture` | Taux de couverture |
| `servi_comp` | Montant compétitif servi ($) |
| `servi_dealers`, `servi_directs`, `servi_indirects` | Montant servi à chaque type d'enchérisseur ($) |

`marche` (B) : une ligne par jour, indexée par la date.

| Colonne | Contenu |
|---|---|
| `vix` | Clôture du VIX |
| `recession` | 1 si le mois est en récession, 0 sinon |
| `stress` | `bas`, `moyen` ou `haut` (tiers du VIX) |

## Calendrier

Date de rendu à confirmer auprès du chargé de TD.

| Semaine | Objectif |
|---|---|
| 26 oct. | Validation du sujet par le chargé de TD. Dépôt GitHub propre. Chacun fait tourner son téléchargement. |
| 2 nov. | A : table brute propre (types, `null`). B : VIX + récessions. Diego : premiers graphiques sur une table provisoire. |
| 9 nov. | A : filtres + journal. B : table `marche` finie. Diego : indicateurs + jointure. |
| 16 nov. | Analyses descriptives (chacun commente ses graphiques). |
| 23 nov. | Rédaction du rapport. |
| 30 nov. | Test de reproductibilité : quelqu'un qui n'a pas écrit le code clone le dépôt sur une autre machine (ou le SSP Cloud) et lance "Run All". |
| 7 déc. | Marge, relecture, bonus éventuels. |
| Janvier | Préparation de l'oral. |

## Règles Git (simples)

- Chacun travaille sur ses fichiers : son module dans `src/` et son notebook dans `notebooks/`. Pas de conflit possible.
- `rapport.ipynb` : une seule personne à la fois le modifie, on se prévient sur le groupe. Un notebook modifié par deux personnes en même temps se corrompt.
- `git pull` avant de commencer, `git add`, `git commit -m "message clair"`, `git push` à la fin. Des petits commits fréquents.
- Bonus : travailler sur des branches et passer par des *pull requests* (le cours le valorise).
- Ne jamais versionner `data/` (déjà dans `.gitignore`).
