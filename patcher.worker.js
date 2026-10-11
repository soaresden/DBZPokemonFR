// Fabrique la ROM française dans le navigateur, avec les mêmes scripts Python que build.py.
// Les ROMs du visiteur restent ici : rien n'est envoyé nulle part.
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js");

const TOOLS = [
  "ips", "gen3text", "extract", "align", "refine_align", "classify", "tables",
  "build_tables_fr", "official_extras", "check_translations", "validate", "insert",
  "refs", "battle_suffix"
].map((n) => `tools/${n}.py`);
const DATA = [
  "tools/battle_suffix_template.json",
  "data/translations.json", "data/glossary.json", "data/nested_translations.json"
];

// Même enchaînement que build.py ; chaque ligne = une étape affichée dans la page.
const STEPS = [
  ["Application du hack anglais", "prepare()"],
  ["Lecture des textes de FireRed US", "run('tools/extract.py', 'roms/us.gba', 'data/derived/us.json')"],
  ["Lecture des textes de Rouge Feu FR", "run('tools/extract.py', 'roms/fr.gba', 'data/derived/fr.json')"],
  ["Lecture des textes du hack", "run('tools/extract.py', 'roms/hack.gba', 'data/derived/hack.json')"],
  ["Alignement avec la VF officielle", "run('tools/align.py'); run('tools/refine_align.py')"],
  ["Tri des textes du hack", "run('tools/classify.py')"],
  ["Noms, attaques et objets", "run('tools/tables.py'); run('tools/build_tables_fr.py'); run('tools/official_extras.py')"],
  ["Vérification des traductions", "run('tools/check_translations.py')"],
  ["Insertion du français", "run('tools/insert.py')"],
  ["Création du patch", "finish()"]
];

const HELPERS = `
import sys, os, io, runpy, contextlib
os.chdir('/work')
sys.path.insert(0, '/work/tools')
os.makedirs('data/derived', exist_ok=True)
os.makedirs('patch', exist_ok=True)

def run(script, *args):
    sys.argv = [script, *args]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            runpy.run_path(script, run_name='__main__')
    except SystemExit as e:
        if e.code not in (None, 0):
            raise RuntimeError(f'{script} : {e.code}\\n{out.getvalue()[-1500:]}')
    except Exception as e:
        raise RuntimeError(f'{script} : {e}\\n{out.getvalue()[-1500:]}')

def prepare():
    from ips import apply_ips
    us = open('roms/us.gba', 'rb').read()
    if os.path.exists('roms/hack.ips'):
        hack = bytes(apply_ips(bytearray(us), open('roms/hack.ips', 'rb').read()))
        open('roms/hack.gba', 'wb').write(hack)

def finish():
    from ips import apply_ips, make_ips
    us = open('roms/us.gba', 'rb').read()
    fr = open('roms/hack_fr.gba', 'rb').read()
    p = make_ips(us, fr)
    if bytes(apply_ips(bytearray(us), p)) != fr:
        raise RuntimeError('le patch ne redonne pas la même ROM (aller-retour IPS)')
    open('patch/DBZ-Team-Training-V8-FR.ips', 'wb').write(p)
`;

const post = (msg, transfer) => self.postMessage(msg, transfer || []);

self.onmessage = async ({ data }) => {
  const { files, base } = data; // files : { us, fr, hackIps?, hackRom? } en ArrayBuffer
  try {
    post({ type: "status", text: "Chargement de Python dans le navigateur…" });
    const py = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.27.2/full/" });
    await py.loadPackage("numpy");

    post({ type: "status", text: "Récupération des traductions…" });
    const FS = py.FS;
    for (const dir of ["/work", "/work/tools", "/work/data", "/work/roms"]) FS.mkdirTree(dir);
    await Promise.all([...TOOLS, ...DATA].map(async (path) => {
      const res = await fetch(`${base}${path}?v=${data.version}`);
      if (!res.ok) throw new Error(`fichier introuvable sur le site : ${path}`);
      FS.writeFile(`/work/${path}`, new Uint8Array(await res.arrayBuffer()));
    }));

    FS.writeFile("/work/roms/us.gba", new Uint8Array(files.us));
    FS.writeFile("/work/roms/fr.gba", new Uint8Array(files.fr));
    if (files.hackIps) FS.writeFile("/work/roms/hack.ips", new Uint8Array(files.hackIps));
    else FS.writeFile("/work/roms/hack.gba", new Uint8Array(files.hackRom));

    py.runPython(HELPERS);
    for (let i = 0; i < STEPS.length; i++) {
      post({ type: "step", index: i, total: STEPS.length, text: STEPS[i][0] });
      await new Promise((r) => setTimeout(r, 0)); // laisse partir le message avant le calcul
      py.runPython(STEPS[i][1]);
    }

    const rom = FS.readFile("/work/roms/hack_fr.gba");
    const ips = FS.readFile("/work/patch/DBZ-Team-Training-V8-FR.ips");
    post({ type: "done", rom: rom.buffer, ips: ips.buffer }, [rom.buffer, ips.buffer]);
  } catch (err) {
    post({ type: "error", text: String(err && err.message || err) });
  }
};
