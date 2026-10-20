# Journal des décisions

Chaque choix qui modifie les données ou l'interprétation est noté ici : quoi, pourquoi, combien de lignes. Le correcteur ne connaît pas ces données : c'est ce fichier qui lui explique notre travail.

Format : `date, auteur : décision. Pourquoi. Combien de lignes concernées.`

---

## 2026-10-20 : changement de sujet

Ancien sujet : reconstruire des courbes de taux (États-Unis, zone euro, Mexique, Inde).
Problème : ces courbes sont déjà nettoyées par le Trésor et la BCE. Il n'y avait presque rien à nettoyer ni à croiser, alors que c'est le cœur de la notation. Les séries des pays émergents étaient en plus mal identifiées et seulement mensuelles.

Nouveau sujet : les adjudications du Trésor américain. Un premier test sur les vraies données a donné :
- 11 154 adjudications de 1979 à 2026 ; en retirant bills (8 361), TIPS (270) et FRN (155), il reste 2 368 notes et bonds nominaux, dont 1 pas encore réalisée ;
- le taux de couverture est renseigné à partir de 2000, les types d'enchérisseurs à partir de 2009 ;
- 7 adjudications de notes et bonds de 1979-1983 (format `Price-Based`) ont un taux limite inférieur au taux médian, ce qui est impossible : à examiner (le même problème touche 420 bills, que nous n'utilisons pas) ;
- la dispersion (taux limite - taux médian) est nettement liée au taux de couverture (corrélation de rang environ -0,5 à année donnée) : c'est un indicateur exploitable ;
- le taux le plus bas n'est pas utilisable : une seule offre isolée peut le faire varier de plusieurs dizaines de points de base ;
- comparer le taux d'adjudication au taux du marché de la veille donne surtout du bruit, car le marché bouge autant dans la journée que l'écart qu'on cherche à mesurer (piste abandonnée, éventuellement présentée en bonus).

Pièges à garder en tête :
- avant 1998, le taux du milieu est une moyenne ; depuis, une médiane ;
- le lien dispersion / taux de couverture est en partie mécanique (les deux viennent des mêmes offres) ;
- sur 47 ans, beaucoup de choses ont une tendance : une corrélation sur toute la période peut être trompeuse, il faut aussi regarder année par année.

## Décisions à prendre

- [ ] (A) Que faire des 7 notes et bonds de 1979-1983 incohérents (corriger, ou retirer) ?
- [ ] (A) Fenêtre d'étude : 1979, 2000 ou 2009 selon l'indicateur ?
- [ ] (B) Seuils du niveau de stress : tiers du VIX sur toute la période ?
