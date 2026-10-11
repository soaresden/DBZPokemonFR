Denis signale un problème de texte en jeu : $ARGUMENTS

1. Identifie la chaîne : cherche les mots anglais (ou le début du texte français) dans `roms/hack.gba` / `roms/hack_fr.gba` avec `tools/gen3text.py` (`encode(texte, terminate=False)` puis recherche d'octets), et retrouve son id dans `data/derived/hack_classified.json`.
2. Diagnostique la cause parmi : chaîne non extraite (pointeur au milieu d'un texte → `data/nested_translations.json`), référence rejetée par `tools/refs.py`, vanilla sans VF (`_nofr`), ligne trop longue, mauvaise traduction.
3. Corrige à la source (traduction, glossaire ou règle), en respectant `docs/translation-guidelines.md` et `data/glossary.json`.
4. `python build.py`, puis si possible `python tests/smoke.py` ou un test ciblé avec `tools/emu.py`.
5. Explique à Denis en quelques phrases la cause et la correction ; dis clairement si tu n'as pas pu vérifier en jeu.
