# Consignes de traduction — Dragon Ball Z Team Training (hack de Pokémon Rouge Feu) → français

Tu traduis en français les textes d'un ROM hack de Pokémon Rouge Feu sur le thème Dragon Ball Z.
Le fichier d'entrée est une liste JSON d'objets :
- `id` : identifiant (ne pas modifier)
- `en` : texte anglais du hack à traduire
- `en_vanilla` (optionnel) : le texte d'origine de Pokémon Rouge Feu US dont le hack est parti
- `fr_vanilla` (optionnel) : la traduction OFFICIELLE française de ce texte d'origine (Rouge Feu FR)
- `contexte` (optionnel) : où le texte apparaît et les contraintes de taille

Écris le fichier de sortie indiqué : une liste JSON `[{"id": "...", "fr": "..."}, ...]`, un objet par entrée d'entrée, dans le même ordre, **sans rien omettre**.

## Méthode
1. Quand `fr_vanilla` existe et que `en` est proche de `en_vanilla`, PARS de `fr_vanilla` (style officiel, tutoiement, ton) et adapte seulement ce que le hack a changé (POKéMON → combattants, noms, lieux, objets…). Si `en` s'éloigne beaucoup, traduis librement `en`.
2. Ton : celui des Pokémon officiels en français — les PNJ tutoient le joueur, phrases courtes, vivantes, un peu familières quand le texte anglais l'est.
3. Le jeu affiche uniquement des MAJUSCULES SANS ACCENT pour les noms propres et termes de jeu écrits en majuscules dans `en` (ARENE, CONSEIL 4, DRESSEUR, FREEZER…). Le texte courant peut utiliser les accents normaux (é è ê à ç ù î ô…) et les majuscules accentuées sont interdites (écris « Etage », « A bientôt », jamais « Étage » ni « À »). Le caractère « œ » est autorisé. Pas de guillemets « » : utilise “ ” ou rien. Pas de caractères spéciaux hors : lettres, chiffres, espace . , ! ? ' - … : / ( ) “ ” $ % + & = ; × ♂ ♀ ▶ < > *
4. Les balises de contrôle doivent être conservées EXACTEMENT, au même nombre et dans une position qui garde le sens :
   - `\n` = saut à la 2e ligne de la boîte, `\l` = ligne suivante (défilement), `\p` = nouvelle boîte de dialogue.
   - `[FD 01]` = nom du joueur, `[FD 06]` = nom du rival, `[FD 02]`/`[FD 03]`/`[FD 04]`... = variables (nom d'un combattant, d'un objet, d'une attaque, nombre…). `[FC ...]` = couleur/police/pause : recopie-les tels quels.
   - Autres jetons entre crochets (`[PK][MN]`, `[Lv]`, `[K]`, `[e]`, `[er]`…) : à recopier tels quels.
5. Structure des lignes d'un dialogue : `ligne1\nligne2\lligne3\lligne4\pligne1\nligne2…`. Après `\p` on recommence avec `\n` puis `\l`. Chaque ligne fait **35 caractères maximum** (balises non comptées). Tu peux changer le nombre de lignes (ajouter des `\l`, ou des `\p` pour couper une longue réplique) tant que la structure reste valide. Jamais deux balises de saut consécutives, jamais de balise en fin de texte sauf si `en` se termine ainsi (ex. `\p` final : conserve-le).
6. Si `contexte` indique une contrainte plus stricte (descriptions d'objets, d'attaques, entrées du Scouter), respecte-la : ces textes ne défilent pas, tout doit tenir dans le nombre de lignes indiqué, séparées par `\n` uniquement.
7. Les textes très courts en majuscules (panneaux, noms de lieux, menus) restent courts et en MAJUSCULES.
8. Applique STRICTEMENT le glossaire `data/glossary.json` (noms des personnages, attaques, objets, termes de jeu). Les noms qui n'y sont pas restent tels quels (GOKU, VEGETA, GOHAN, PICCOLO, BULMA, TRUNKS…). « Fighter(s) » → « combattant(s) ». « TRAINER » → « DRESSEUR ». « GYM » → « ARENE », « GYM LEADER » → « CHAMPION D'ARENE », « ELITE FOUR » → « CONSEIL 4 », « CHAMPION » (de la ligue) → « MAITRE », « MART » → « BOUTIQUE », « HEAL CENTER » → « CENTRE DE SOINS », « HM/TM » → « CS/CT », « BOX » → « BOITE », « BADGE » → « BADGE », « CAPSULE » → « CAPSULE ». Villes : traduis les noms de villes/routes du hack de façon fidèle et courte, en majuscules, cohérente à travers le lot (ex. « NAMEK TOWN » → « BOURG NAMEK », « MAKYO TOWN » → « MAKYO VILLE », « NORTH FOREST » → « FORET NORD », « MT.MOON » → « MT. SELENITE » comme en VF officielle quand le lieu vanilla existe).
9. Pour les lieux et noms vanilla qui existent dans Rouge Feu FR (villes de Kanto, routes, MT. SELENITE, GROTTE, SYLPHE SARL, etc.), utilise le nom officiel FR quand le hack a gardé le nom vanilla.
10. Ne traduis pas mot à mot : le résultat doit sonner naturel en français, comme un jeu Pokémon officiel.

## Vérification avant d'écrire
- même nombre d'entrées, mêmes `id`, même ordre ;
- mêmes balises `[FD xx]` / `[FC …]` (même ensemble) que dans `en` ;
- aucune ligne > 35 caractères ; aucune majuscule accentuée ; aucun caractère interdit ;
- JSON valide (échappe les backslashes : dans le JSON, `\n` du jeu s'écrit `\\n`, comme dans le fichier d'entrée).

## Lieux (section `places` du glossaire — obligatoire pour la cohérence entre lots)
Utilise exactement les traductions de `places` dans data/glossary.json (BOURG NAMEK, MAKYO VILLE, GINGER VILLE, WEST CITY et SATAN CITY conservés, VILLAGE ARU, ROYAUME SAIYAN, MONT PAOZU, FORET NORD, ILE TORTUE GENIALE, BASE RED RIBBON, MAGASIN Z, ZONE BABIDI, CASINO PILAF, MANOIR SATAN, TOUR DIVINE, PLATEAU DRAGON, LIGUE DRAGON, PANTHEON…).

## Limites STRICTES des boîtes fixes (mesurées sur le jeu)
- Description d'attaque (adresses 0x48xxxx) : max 4 lignes de **21 caractères** chacune, séparées par `\n` uniquement. Sois concis, abrège si besoin (ATQ, DEF, VIT, ATQ.SPE, DEF.SPE, PV).
- Entrée Scouter/Pokédex (adresses 0x44xxxx-0x45xxxx) : max **3 lignes de 43 caractères**, `\n` uniquement.
- Description d'objet : max 4 lignes de 44 caractères, `\n` uniquement.
- Description de capacité spéciale : 1 ligne de 27 caractères max.
