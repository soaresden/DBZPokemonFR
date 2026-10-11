Teste la ROM traduite dans l'émulateur headless.

1. `python tests/smoke.py` (nécessite `pip install mgba pillow`, fonctionne sous Linux/WSL).
2. Ouvre les captures de `tests/out/` et vérifie : écran titre, dialogue de Brief en français, « VEGETA ennemi utilise … » en combat.
3. Pour un scénario précis, utilise `tools/emu.py` avec un état de `tests/states/` (syntaxe dans CLAUDE.md) et regarde les captures.
4. Si mgba n'est pas installable (Windows natif), dis-le et propose à Denis de tester à la main dans mGBA.
