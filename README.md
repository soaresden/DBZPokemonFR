# Dragon Ball Z Team Training V8 — traduction française

Patch IPS qui traduit en français le ROM hack *Dragon Ball Z Team Training V8* (Z-Max), basé sur Pokémon Rouge Feu.

👉 **Patcher en ligne : https://soaresden.github.io/DBZPokemonFR/**
Tu déposes tes trois fichiers (FireRed US v1.0, Rouge Feu FR, patch anglais V8) et la ROM française est
fabriquée dans ton navigateur, avec les mêmes scripts que `build.py` : rien n'est envoyé sur internet.

## Principe

Le patch n'est **pas** fourni dans ce dépôt : il contient les textes de la VF officielle de Pokémon Rouge Feu
(repris pour tout ce que le hack n'a pas modifié). Chacun le reconstruit à partir de **ses propres ROMs** ; le dépôt
ne contient que le code, le glossaire et la traduction des textes propres au hack.

Le patch obtenu s'applique sur une ROM **Pokémon FireRed USA v1.0** (code `BPRE`) avec Rom Patcher JS, Lunar IPS
ou Floating IPS. Il contient déjà le hack : ne pas appliquer le patch anglais en plus.

## Reconstruire le patch

1. Placer dans `roms/` : `us.gba` (FireRed US v1.0), `fr.gba` (Rouge Feu FR), `hack.ips` (patch anglais V8).
2. `pip install -r requirements.txt`
3. `python build.py`

Voir `CLAUDE.md` pour le fonctionnement détaillé, et `docs/translation-guidelines.md` pour les règles de traduction.

Ne sont **pas** versionnés (voir `.gitignore`) : les ROMs, les extractions de texte (`data/derived/`), les états
de sauvegarde des tests, et le patch généré lui-même (réservé à un usage personnel).
