# ROMs (non versionnées)

Déposer ici vos propres fichiers :

| Fichier | Contenu | Vérification |
|---|---|---|
| `us.gba` | Pokémon FireRed USA v1.0 | code jeu `BPRE` à l'offset 0xAC |
| `fr.gba` | Pokémon Rouge Feu (France) | code jeu `BPRF` |
| `hack.ips` | Dragon Ball Z Team Training V8 (patch anglais, ~2,8 Mo) | doit s'appliquer sur `us.gba` |

`build.py` génère ensuite `hack.gba` (hack anglais) et `hack_fr.gba` (hack français) dans ce dossier.
Tous ces fichiers sont ignorés par git.
