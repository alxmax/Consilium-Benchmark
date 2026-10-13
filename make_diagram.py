"""Generate the Consilium-benchmark architecture poster (Excalidraw + HTML viewer).

One scene, three stacked layers:
  1. PIPELINE   — task -> harness -> 5 modes -> deliverables -> verifier -> report
  2. THE 5 MODES — single-pass lane vs deliberation lane (real voice structure)
  3. RESULT     — trick-question catch-rate (n=4)
Run from the repo root:  python make_diagram.py
"""
import sys, os, glob, re


def _builder_path():
    # The builder ships in the excalidraw-diagram plugin (formerly bundled in
    # requirement-manager); look in every Claude profile's plugin cache.
    home = os.path.expanduser("~")
    hits = []
    for profile in glob.glob(os.path.join(home, ".claude*")):
        cache = os.path.join(profile, "plugins", "cache")
        for plugin in ("excalidraw-diagram", "requirement-manager"):
            hits += glob.glob(os.path.join(cache, plugin, plugin, "*", "skills",
                                           "excalidraw-diagram", "scripts"))
    # This script uses the 1.x Scene API (title(..., size=...)); excalidraw-diagram
    # 2.x replaced it, so only a 1.x builder (or requirement-manager's bundle) fits.
    hits = [h for h in hits if "requirement-manager" in h
            or re.search(r"excalidraw-diagram[\\/]1\.\d+\.\d+[\\/]", h)]
    if not hits:
        raise RuntimeError(
            "excalidraw-diagram 1.x builder not found — install excalidraw-diagram 1.x"
        )
    def _ver(p):
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", p)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
    return max(hits, key=_ver)


sys.path.insert(0, _builder_path())
from excalidraw_builder import Scene  # noqa: E402

s = Scene(seed=7, roles={
    "input": "grey", "harness": "blue", "data": "yellow", "verify": "green",
    "single": "orange", "delib": "violet", "skeptic": "red", "result": "teal",
})

s.title("How the Consilium benchmark works", 40, -72, size=30)
s.label("Left -> right: one task runs through the harness in 5 modes, writes deliverables, and is graded by a script (no AI judging AI). "
        "Same model within a batch (Sonnet 5.5, or Opus 5.5) -- only the process differs.", 40, -30, size=13)

# ---------------- 1 · PIPELINE ----------------
y = s.section("1 - PIPELINE   one task per mode, graded deterministically")
W, H, GAP = 178, 66, 250
xs = [80 + i * GAP for i in range(8)]
task   = s.box("Task\ncode / reasoning Q",     xs[0], y, W, H, fill="input")
harn   = s.box("run_task.py\nclaude -p headless", xs[1], y, W, H, fill="harness")
modes  = s.box("5 modes\n(see layer 2)",       xs[2], y, W, H, fill="delib")
deliv  = s.box("Deliverables\nanswer.md / .hpp", xs[3], y, W, H, fill="data")
verif  = s.box("verify.py\ndeterministic",     xs[4], y, W, H, fill="verify")
score  = s.box("Score\n/100 . /60",            xs[5], y, W, H, fill="result")
analyz = s.box("analyze.py\naggregate n=4",    xs[6], y, W, H, fill="harness")
report = s.box("Report",                        xs[7], y, W, H, fill="result")
chain = [task, harn, modes, deliv, verif, score, analyz, report]
for a, b in zip(chain, chain[1:]):
    s.arrow(a, b)

# integrity satellites (below the spine, short vertical arrows)
audit = s.box("pipeline_audit.json\nskill_engaged .\npipeline_executed",
              xs[1], y + 135, 175, 80, fill="data")
s.arrow(harn, audit)
keys = s.box("Benchmark-scoring\nexternal repo .\nstashed each run",
             xs[4], y + 135, 175, 80, fill="verify")
s.arrow(keys, verif)

# ---------------- 2 · THE 5 MODES ----------------
y = s.section("2 - THE 5 MODES   single-pass vs deliberation (same model)")
sb = s.box("sonnet_bare\n1 call -> answer", 80, y, 185, 64, fill="single")
sp = s.box("superpowers\n1 pass + skills",  300, y, 185, 64, fill="single")
s.lane([sb, sp], "Single-pass -- answer alone  (~$0.30 . seconds)")

yd = y + 175
s.label("Deliberation -- a process  (~$1.3-1.6 . minutes)", 110, yd - 64, size=12)
seq = s.column([{"text": "Generator", "fill": "delib", "w": 200},
                {"text": "Conservator", "fill": "delib", "w": 200},
                {"text": "Control", "fill": "delib", "w": 200}],
               110, yd, gap=60, connect=True)
s.enclose(seq, label="consilium_sequential", pad=18)
dia = s.column([{"text": "Generator", "fill": "delib", "w": 200},
                {"text": "Conservator", "fill": "delib", "w": 200},
                {"text": "Control", "fill": "delib", "w": 200},
                {"text": "Skeptic", "fill": "skeptic", "w": 200}],
               440, yd, gap=60, connect=True)
s.enclose(dia, label="consilium_dialectic", pad=18)
tri = s.column([{"text": "3 personalities\nblind Sequential", "fill": "delib", "w": 200},
                {"text": "democratic vote", "fill": "delib", "w": 200},
                {"text": "Skeptic", "fill": "skeptic", "w": 200}],
               770, yd, gap=60, connect=True)
s.enclose(tri, label="consilium_trias", pad=18)

# ---------------- 3 · RESULT ----------------
y = s.section("3 - RESULT   the trick question, 4 tries each")
rates = [("consilium_sequential", "4 / 4", "delib"),
         ("consilium_dialectic",  "4 / 4", "delib"),
         ("consilium_trias",      "3 / 4", "delib"),
         ("superpowers",          "2 / 4", "single"),
         ("sonnet_bare",          "1 / 4", "single")]
rx = 80
for name, rate, fill in rates:
    s.box(f"{name}\n{rate}", rx, y, 205, 66, fill=fill)
    rx += 225
s.label("Deliberation catches the trap; single-pass mostly misses. Same model -- the difference is the process.",
        80, y + 92, size=13)

# ---------------- legend + glossary ----------------
ly = y + 150
s.legend([("input / task", "grey"), ("harness . runner", "blue"),
          ("deliberation voice", "violet"), ("skeptic challenge", "red"),
          ("deliverable . audit", "yellow"), ("verifier . answer-key isolation", "green"),
          ("single-pass mode", "orange"), ("score . report", "teal")],
         x=80, y=ly, title="Colour = role")
s.glossary([("claude -p", "Claude Code CLI, headless one-shot run"),
            ("skill_engaged", "transcript shows /consilium actually fired"),
            ("pipeline_executed", "full pipeline vs scale_down short-circuit"),
            ("closed_answer", "graded by exact letter + keyword, no AI judge"),
            ("cpp_self_tests", "compile + run the model's own C++ tests")],
           x=620, y=ly, title="Terms")

s.save("benchmark_architecture", out_dir=".",
       crossing_check="error", legend_check="error", overflow_check="error",
       text_overlap_check="error", label_fit_check="error")
print("OK")
