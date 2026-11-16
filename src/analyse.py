"""
Indicateurs, tableaux et graphiques.
Prend les tables 'adjudications' et 'marche'.
"""
import matplotlib.pyplot as plt
import pandas as pd


def ajouter_indicateurs(adj):
    """Ajoute dispersion (pb), parts des enchérisseurs (%), maturité (années) et année."""
    adj = adj.copy()
    adj["dispersion_pb"] = (adj["taux_limite"] - adj["taux_median"]) * 100
    for t in ["dealers", "directs", "indirects"]:
        adj["part_" + t] = adj["servi_" + t] / adj["servi_comp"] * 100
    adj["maturite"] = adj["terme"].str.split("-").str[0].astype(int)  # "10-Year" -> 10
    adj["annee"] = adj["date"].dt.year
    return adj


def joindre_marche(adj, marche):
    """Ajoute le VIX, la récession et le stress de la VEILLE de chaque adjudication
    (le VIX du jour réagit déjà au résultat)."""
    return pd.merge_asof(adj.sort_values("date"), marche, left_on="date",
                         right_index=True, allow_exact_matches=False)


def ecart_a_l_annee(table, col):
    """Valeur moins la médiane de son année : enlève les tendances de long terme."""
    return table[col] - table.groupby("annee")[col].transform("median")


def correlation_rangs(x, y):
    """Corrélation de Spearman = corrélation des rangs (peu sensible aux valeurs extrêmes)."""
    return x.rank().corr(y.rank())


def tableau_par_groupe(table, groupe, colonnes):
    return table.groupby(groupe, observed=True)[colonnes].agg(["count", "mean", "median", "std"]).round(2)


def tableau_disponibilite(table, colonnes):
    """% d'adjudications où chaque colonne est renseignée, par décennie."""
    return (table[colonnes].notna().groupby(table["annee"] // 10 * 10).mean() * 100).round()


def graphique_evolution(table, col, titre, unite, marche):
    """Médiane par année, récessions en gris."""
    med = table.groupby("annee")[col].median().dropna()
    dates = pd.to_datetime(med.index.astype(str) + "-07-01")
    fig, ax = plt.subplots(figsize=(10, 4))
    m = marche[dates.min():dates.max()]
    ax.fill_between(m.index, 0, 1, where=m["recession"] == 1, transform=ax.get_xaxis_transform(),
                    color="grey", alpha=0.3, label="Récession (NBER)")
    ax.plot(dates, med, marker="o", markersize=3, label="Médiane annuelle")
    ax.set(title=titre, xlabel="Année", ylabel=unite)
    ax.legend()
    plt.show()


def graphique_par_groupe(table, col, groupe, titre, unite, ordre=None):
    """Boîtes à moustaches de 'col' par 'groupe' (sans les points extrêmes)."""
    if ordre is None:
        ordre = sorted(table[groupe].dropna().unique())
    valeurs = [table.loc[table[groupe] == g, col].dropna() for g in ordre]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.boxplot(valeurs, showfliers=False)
    ax.set_xticks(range(1, len(ordre) + 1), ordre)
    ax.set(title=titre, xlabel=groupe, ylabel=unite)
    plt.show()


def graphique_parts(table, par, titre):
    """Parts moyennes des enchérisseurs, en barres empilées, par année ou par maturité."""
    parts = table.groupby(par)[["part_dealers", "part_directs", "part_indirects"]].mean().dropna()
    ax = parts.plot(kind="bar", stacked=True, figsize=(10, 4))
    ax.set(title=titre, ylabel="% du montant compétitif servi", ylim=(0, 100))
    ax.legend(["Primary dealers", "Directs", "Indirects"], loc="upper left", bbox_to_anchor=(1, 1))
    plt.show()
