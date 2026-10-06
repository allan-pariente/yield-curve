[Construction des courbes]
     │
     ├── 🇺🇸 USA ──────────────► Courbe des US Treasuries (Maturités de 1 mois à 30 ans)
     │
     ├── 🇪🇺 Europe ───────────► Courbe "Zero-Coupon" Euro de la BCE (basée sur les obligations AAA)
     │
     └── 🌍 Pays Émergents ───► Choix d'une approche par "Pays Pilotes" ou par "Spread"

### Plan pour pays émergents :

Afin d'éviter une dispersion des données tout en garantissant la représentativité de la classe d'actifs émergente, notre étude se concentre sur deux acteurs économiques mondiaux : **le Mexique** (représentant de la région LATAM) et **l'Inde** (représentant de l'Asie émergente). 

Ce choix de binôme présente trois avantages pour notre projet de traitement de données :

1. Premièrement, le Mexique et l'Inde possèdent les marchés obligataires souverains locaux les plus profonds, les plus liquides et les plus réglementés de l'univers émergent, nous garantissant des séries temporelles historiques complètes, fiables et gratuites (via la FRED/DBnomics) pour les maturités courtes (3 mois) et longues (10 ans).
2. Deuxièmement, ils offrent une parfaite complémentarité géographique et économique face aux blocs développés (USA et Zone Euro) aussi étudiés.
3. Enfin, d'un point de vue purement technique, leurs dynamiques de taux diffèrent :
   * Le Mexique est historiquement très corrélé à la politique monétaire de la Réserve fédérale américaine,
   * L'Inde réagit davantage à ses propres dynamiques de croissance interne et d'inflation. 

Ce couple permet de tester la robustesse de nos algorithmes de lissage et d'interpolation Pandas sur des formes de courbes de taux structurellement différentes.

### 🇲🇽 Mexique

* **Court Terme (3 Mois)** : IR3MST01MXM156N | [Lien FRED](https://fred.stlouisfed.org/series/IRLTLT01MXM156N)
* **Moyen Terme (2 Ans)** : INTGSTMXM193N (Taux des bons du Trésor à 2 ans) | [Lien FRED](https://fred.stlouisfed.org/series/INTGSTMXM193N)
* **Long Terme (10 Ans)** : IRLTLT01MXM156N | [Lien FRED](https://fred.stlouisfed.org/tags/series?t=10-year%3Bbonds%3Bmexico)

### 🇮🇳 Inde 

* **Court Terme (3 Mois)** : IR3MST01INM156N | [Lien FRED](https://fred.stlouisfed.org/tags/series?pageID=1&ob=pv&od=desc&t=3-month%3Bindia%3Binterbank%3Binterest+rate&et=&addgraph2=)
* **Moyen Terme (2 Ans)** : INTGSTINM193N (Taux des bons du Trésor à 2 ans) | [Lien FRED](https://fred.stlouisfed.org/tags/series?t=bonds%3Bindia%3Binterest+rate)
* **Long Terme (10 Ans)** : IRLTLT01INM156N | [Lien FRED](https://fred.stlouisfed.org/series/INDIRLTLT01STM)
