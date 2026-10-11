# DBZPokemonFR — traduction française de « Dragon Ball Z Team Training V8 » (GBA)

Réponds toujours en français à Denis.

## Le projet en bref

Traduction FR d'un ROM hack de Pokémon Rouge Feu sur le thème DBZ. Le hack (auteur : Z-Max) est distribué
en IPS à appliquer sur **Pokémon FireRed USA v1.0 (BPRE)**. On produit un nouvel IPS, toujours appliqué
sur la ROM US, qui contient le hack + la traduction :

- **textes propres au hack** (~2 800 chaînes) : traduits à la main → `data/translations.json` ;
- **textes vanilla non modifiés par le hack** : repris automatiquement de la VF officielle
  (ROM Rouge Feu FR, BPRF) par alignement US↔FR — rien n'est stocké, tout est relu dans `roms/fr.gba` au build ;
- **tables à largeur fixe** (combattants, attaques, objets, capacités, catégories, classes, dresseurs) :
  VF officielle pour les entrées vanilla, `data/glossary.json` pour celles modifiées par le hack ;
- **patch de code** : suffixe « VEGETA ennemi » / « … sauvage » en combat (le moteur US met un préfixe).

## Commandes

```
python build.py              # build complet (≈30 s) -> patch/DBZ-Team-Training-V8-FR.ips
python build.py --fast       # après une modif de traduction : réinsertion + patch seulement (≈5 s)
python tools/check_translations.py --all   # contrôle des traductions (lancé aussi par build.py)
python tests/smoke.py        # test émulateur (Linux/WSL, nécessite `pip install mgba`)
```
Sous Windows, lancer Python en UTF-8 si un script est exécuté hors de build.py : `python -X utf8 tools/xxx.py`.
Dépendances : `pip install -r requirements.txt` (numpy obligatoire ; mgba/pillow/capstone optionnels).

Entrées requises dans `roms/` (jamais commitées, cf. `roms/README.md`) : `us.gba`, `fr.gba`, `hack.ips`.
Sorties : `roms/hack.gba` (hack EN), `roms/hack_fr.gba` (hack FR), `patch/*.ips`.
Ne jamais committer les ROMs, `data/derived/`, `tests/states/` ni `patch/*.ips` (ce dernier contient des textes de la VF officielle) — ils sont dans `.gitignore`.

## Fichiers sources (édités à la main) vs dérivés

| Fichier | Rôle |
|---|---|
| `data/translations.json` | **source principale** : `{id: texte FR}`, id = adresse hex de la chaîne dans la ROM hackée |
| `data/glossary.json` | noms DBZ FR, termes de jeu, attaques, objets, lieux (cohérence obligatoire) |
| `data/nested_translations.json` | chaînes qui commencent au milieu d'une autre (restes d'édition du hack), toujours déplacées |
| `docs/translation-guidelines.md` | règles de style et contraintes de largeur (à suivre pour toute traduction) |
| `data/derived/*` | **régénéré par build.py**, ignoré par git (extractions de texte des ROMs, alignement, tables) |
| `tools/battle_suffix_template.json` | code machine pré-assemblé du hook de combat (régénérable : `python tools/battle_suffix.py`, nécessite arm-none-eabi-as) |

## Pipeline (`build.py`)

1. `ips.py` applique `hack.ips` sur `us.gba` → `hack.gba`.
2. `extract.py` : scanne tous les pointeurs `0x08xxxxxx` et décode les chaînes (`gen3text.py` = table de caractères Gen 3 + codes `\n \l \p [FD xx] [FC ..]`).
3. `align.py` + `refine_align.py` : associe chaque chaîne US à sa VF (alignement de séquence + delta constant des positions de pointeurs, le code étant identique entre US et FR).
4. `classify.py` : chaque chaîne du hack est soit `vanilla_*` (identique à l'US → VF officielle), soit `hack` (à traduire). Le suffixe `_nofr` = vanilla sans équivalent FR trouvé.
5. `tables.py` + `build_tables_fr.py` + `official_extras.py` : tables à largeur fixe et quelques descriptions officielles lues par index.
6. `check_translations.py` (via `validate.py`) : bloque le build en cas d'erreur.
7. `insert.py` : écrit en place si ça tient **et** si aucune autre chaîne référencée ne commence à l'intérieur ; sinon écrit dans l'espace libre (≥ 0x800000, runs de 0xFF) et repointe **uniquement les références de confiance** (`refs.py`). Applique les tables puis `battle_suffix.patch()`.
8. Génère l'IPS et vérifie l'aller-retour.

## Pièges connus (importants)

- **Faux pointeurs** : beaucoup de séquences d'octets ressemblent à des pointeurs. Dans la zone de code (< 0x160000) seuls les pointeurs alignés sur 4 sont réels ; ailleurs, `refs.py` accepte les formes de scripts XSE (`0F 00` loadpointer, `67` preparemsg, trainerbattle `5C`, pointeurs consécutifs, etc.). Repointer un faux pointeur dans le code = écran noir au boot. ~185 références sont rejetées volontairement (presque toutes des fragments).
- **Textes collés sans séparateur** dans la zone du hack (≥ 0x800000) : l'auteur a réécrit des textes par-dessus d'autres ; un script peut pointer au milieu d'une chaîne. Ne jamais réécrire sur place une chaîne contenant le début d'une autre (géré par `insert.py`).
- **Largeurs** : dialogue 35 caractères/ligne (structure `ligne1\nligne2\lligne3…\p`), descriptions d'attaques 4×21, Scouter/Pokédex 3×43, objets 4×44, capacités 1×27. Pas de majuscules accentuées (police), `œ` ok, `º` existe (`NºID`), pas de `°`.
- **Préfixe ennemi** : ne pas « traduire » `Foe ` (0x3fd55b) — il est neutralisé par `battle_suffix.py`. Toute modif du moteur de combat doit garder les vérifications d'octets d'origine (`expect`).
- Le **glitch graphique de la chambre** (côté gauche du décor) existe déjà dans le hack anglais d'origine : ne pas chercher la cause dans la traduction.

## Restant à faire / idées

- Graphismes encore en anglais : barre « MOVE OK BACK » et boutons « lower/BACK/OK » de l'écran de nom, peut-être d'autres écrans (images, pas du texte). Piste : reprendre les graphismes VF de `fr.gba` (données LZ77 + repointage) quand le hack ne les a pas modifiés.
- Suffixe « sauvage » : implémenté, **pas encore vérifié en jeu** (combat sauvage).
- Relecture en jeu au-delà du premier combat contre le rival (seul l'intro → labo → combat rival a été testé).
- Si Denis signale un texte anglais/coupé avec une capture : retrouver la chaîne (`gen3text.encode` + recherche dans `roms/hack.gba`), regarder pourquoi (non extraite, référence rejetée, `_nofr`, chaîne imbriquée), corriger `data/translations.json` (ou les règles), `python build.py`, re-tester.

## Tests

- `tests/smoke.py` : boot jusqu'à l'écran titre + rejoue des états sauvegardés (`tests/states/*.bin` : chambre, route avant Brief, début du combat rival) et enregistre des captures dans `tests/out/`. Les états proviennent d'une build antérieure : s'ils deviennent incohérents après de gros changements, refaire un état en jouant (`tools/emu.py ROM prefix "script" etat_in etat_out`).
- Syntaxe des scripts emu : `w300` attendre 300 frames, `a b start select up down left right`, `up*16` maintenir 16 frames (un pas), `s` capture.
