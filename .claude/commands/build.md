Reconstruis le patch français.

1. Vérifie que `roms/us.gba`, `roms/fr.gba` et `roms/hack.ips` existent (sinon explique à Denis quoi y mettre, cf. roms/README.md).
2. Lance `python build.py` (ou `python build.py --fast` si seuls des fichiers de `data/` ont changé depuis le dernier build complet).
3. Si `check_translations.py` signale des erreurs, corrige les textes concernés dans `data/translations.json` en respectant `docs/translation-guidelines.md`, puis relance.
4. Résume en une ou deux phrases : nombre de textes, erreurs éventuelles, taille du patch.
