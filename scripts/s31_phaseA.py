"""Session 31 phase A. The publication audit.

Nothing is written or changed here. Gate A halts the session if any credential or
key is found, since a secret in git history is not removed by deleting the file.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM                            # noqa: E402

OUT = ROOT / "outputs" / "session-31"
OUT.mkdir(parents=True, exist_ok=True)
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          cwd=ROOT).stdout


l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
     capture_output=True, text=True).stdout.strip().strip("{} ").split()]
s0 = VM.sample()
for k, v in (("load_1min", l[0]), ("load_5min", l[1]), ("load_15min", l[2]),
             ("compressor_gib", s0["compressor_gib"]),
             ("swap_used_mb", s0["swap_used_mb"]), ("swap_free_mb", s0["swap_free_mb"])):
    add("machine_at_phase_A", item=k, value=v)

TRACKED = [p for p in sh("git ls-files").split("\n") if p]
add("scope", item="tracked_files", value=len(TRACKED))

# ---- root files and top-level directories -------------------------------------------
for p in sorted(ROOT.iterdir()):
    if p.name in (".git",):
        continue
    if p.is_file():
        add("root_file", item=p.name, value=p.stat().st_size,
            tracked=int(p.name in TRACKED))
    else:
        n = sum(1 for x in p.rglob("*") if x.is_file())
        b = sum(x.stat().st_size for x in p.rglob("*") if x.is_file())
        tr = sum(1 for t in TRACKED if t.startswith(p.name + "/"))
        add("top_level_directory", item=p.name + "/", value=b, n_files=n, tracked=tr)

# ---- the four documents a reader looks for -------------------------------------------
for name, patterns in (("README", ("README.md", "README", "README.rst")),
                       ("license", ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")),
                       ("requirements.txt", ("requirements.txt",)),
                       (".gitignore", (".gitignore",))):
    found = next((f for f in patterns if (ROOT / f).exists()), None)
    add("reader_document", item=name, value=found or "ABSENT",
        note=(ROOT / found).read_text()[:3000].replace("\n", " | ") if found else
             "no file of this kind exists at the repository root")

# ---- tracked files above 10 megabytes --------------------------------------------------
big = []
for t in TRACKED:
    p = ROOT / t
    if p.exists() and p.stat().st_size > 10 * 1024 * 1024:
        big.append((p.stat().st_size, t))
for sz, t in sorted(big, reverse=True):
    add("large_tracked_file", item=t, value=sz,
        note=f"{sz/1048576:.2f} MB")
add("size", item="tracked_files_above_10mb", value=len(big))
add("size", item="git_directory_kib", value=int(sh("du -sk .git | cut -f1").strip()))
add("size", item="working_tree_kib", value=int(sh("du -sk . | cut -f1").strip()))
add("size", item="tracked_bytes",
    value=sum((ROOT / t).stat().st_size for t in TRACKED if (ROOT / t).exists()))

# ---- classification --------------------------------------------------------------------
CLASS = {"session output": 0, "derived artifact": 0, "document": 0, "code": 0,
         "frozen input": 0, "other": 0}
for t in TRACKED:
    if t.startswith("outputs/"):
        c = "session output"
    elif t.startswith("data/raw/"):
        c = "frozen input"
    elif t.startswith("data/"):
        c = "derived artifact"
    elif t.startswith("docs/") or t.endswith(".md"):
        c = "document"
    elif t.startswith(("src/", "scripts/", "tests/")) or t.endswith(".py"):
        c = "code"
    else:
        c = "other"
    CLASS[c] += 1
for c, n in CLASS.items():
    add("classification", item=c, value=n)
add("classification", item="note",
    note="frozen inputs are separated from derived artifacts because the licence "
         "question falls on them differently. data/raw carries the purchased and "
         "vendor-sourced series and data/interim carries reconstructions built from them")

# ---- the credential and identifier sweep ------------------------------------------------
SECRET = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("generic_assignment", re.compile(
        r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|"
        r"client[_-]?secret|password|passwd)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    ("bearer", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}")),
]
IDENT = [
    ("absolute_home_path", re.compile(r"/Users/GualyCr/")),
    ("email_address", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("other_user_home", re.compile(r"/Users/(?!GualyCr)[A-Za-z0-9._\-]+/")),
]
TEXT_EXT = {".py", ".md", ".txt", ".csv", ".json", ".toml", ".cfg", ".yml", ".yaml",
            ".ini", ".sh", ".svg", ".gitignore", ""}
secret_hits, ident_hits = [], []
per_file = {}
for t in TRACKED:
    p = ROOT / t
    if not p.exists():
        continue
    if p.suffix.lower() not in TEXT_EXT:
        continue
    try:
        txt = p.read_text(errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(txt.split("\n"), 1):
        for name, rx in SECRET:
            if rx.search(line):
                secret_hits.append((name, t, i, line.strip()[:160]))
        for name, rx in IDENT:
            m = rx.search(line)
            if m:
                ident_hits.append((name, t, i, m.group(0)))
                per_file[(name, t)] = per_file.get((name, t), 0) + 1
add("sweep", item="text_files_swept",
    value=sum(1 for t in TRACKED if (ROOT / t).suffix.lower() in TEXT_EXT
              and (ROOT / t).exists()),
    note="every tracked text file rather than a sample")
for name, t, i, line in secret_hits:
    add("credential", item=name, file=t, line=i, value=line)
add("credential_summary", item="hits", value=len(secret_hits),
    note="; ".join(sorted({h[0] for h in secret_hits})) or "none")
for (name, t), n in sorted(per_file.items(), key=lambda kv: -kv[1]):
    add("identifier_by_file", item=name, file=t, value=n)
for name in {h[0] for h in ident_hits}:
    hits = [h for h in ident_hits if h[0] == name]
    files = sorted({h[1] for h in hits})
    add("identifier_summary", item=name, value=len(hits), n_files=len(files),
        note=f"across {len(files)} tracked files. Examples, " +
             "; ".join(f"{h[1]}:{h[2]}" for h in hits[:3]))
    if name == "email_address":
        for h in hits[:40]:
            add("email_hit", item=h[3], file=h[1], line=h[2])

# ---- vendor licence ----------------------------------------------------------------------
VEND = []
for p in sorted((ROOT / "data").rglob("*")):
    if p.is_file() and p.suffix in (".parquet", ".csv"):
        rel = str(p.relative_to(ROOT))
        if rel not in TRACKED:
            continue
        VEND.append(rel)
add("vendor", item="tracked_data_files", value=len(VEND))
add("vendor", item="etf_and_index_series", value=sum(1 for v in VEND
                                                     if "/raw/etf/" in v
                                                     or "/raw/index/" in v),
    note="price and total-return history sourced through yfinance from Yahoo Finance, "
         "whose terms permit personal use and do not grant redistribution rights. "
         "REDISTRIBUTION IS NOT ESTABLISHED as permitted and the question is reported "
         "rather than answered here")
add("vendor", item="cboe_vx_settles", value=sum(1 for v in VEND if "/raw/vx/" in v
                                                or "vx-" in v),
    note="Cboe VX futures daily settlement, published by Cboe on its own site. The terms "
         "attach to the publisher rather than to a purchase and the question is reported "
         "rather than answered here")
add("vendor", item="issuer_nav", value=sum(1 for v in VEND if "/raw/nav/" in v
                                           or "nav-" in v),
    note="ProShares issuer net asset value for UVXY and SVXY, taken from the issuer's "
         "own published record")
add("vendor", item="rates", value=sum(1 for v in VEND if "/raw/rates/" in v),
    note="DTB3 from the Federal Reserve H.15 release, which is United States government "
         "work and carries no redistribution restriction")
add("vendor", item="verdict", value="OPEN",
    note="no vendor licence has been read against these artifacts inside this project, "
         "so whether every tracked series may be redistributed is not established. The "
         "question is reported and not answered, and it bears on the publication "
         "decision rather than on any measurement")

# ---- gate A -------------------------------------------------------------------------------
halt = len(secret_hits) > 0
add("gate_A", item="credentials_or_keys_found", value=len(secret_hits))
add("gate_A", item="verdict", value="HALT" if halt else "PROCEED",
    note="a secret in git history is not removed by deleting the file, so the session "
         "halts before anything else runs" if halt else
         "no credential or key pattern matched in any tracked text file")

fn = ["table", "item", "file", "line", "value", "n_files", "n_files_total", "tracked",
      "note"]
with open(OUT / "publication-audit.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote publication-audit.csv, {len(rows)} rows")
print(f"tracked files {len(TRACKED)}, above 10 MB {len(big)}")
print(f"credential hits {len(secret_hits)}, identifier hits {len(ident_hits)}")
for name in sorted({h[0] for h in ident_hits}):
    print(f"  {name}: {sum(1 for h in ident_hits if h[0]==name)} hits across "
          f"{len({h[1] for h in ident_hits if h[0]==name})} files")
print(f"GATE A {'HALT' if halt else 'PROCEED'}")
sys.exit(1 if halt else 0)
