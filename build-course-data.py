#!/usr/bin/env python3
"""Scan the repo and generate course-data.js for the course website (index.html).

Run from the repo root any time content is added or removed:
    python3 build-course-data.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = "2026/units"

# icon, track, round, description — keyed by unit number
UNIT_META = {
    "01": ("📝", "Foundations", 1, "Write competition-grade technical documents — Markdown syntax, LaTeX math, tables, and clean solution write-ups."),
    "02": ("📐", "Foundations", 1, "Linear algebra, probability, calculus, and convex optimization — the mathematical engine behind every model."),
    "03": ("🐍", "Foundations", 1, "Advanced Python, NumPy vectorization and broadcasting, pandas, and plotting for AI workflows."),
    "04": ("📈", "ML & PyTorch", 1, "Regression, classification, kernels, bias–variance, and model evaluation built from first principles."),
    "05": ("🔍", "ML & PyTorch", 1, "Clustering, dimensionality reduction, and discovering structure in data without labels."),
    "06": ("🔥", "ML & PyTorch", 1, "Tensors, autograd, modules, and building complete training loops in PyTorch."),
    "07": ("🧠", "Deep Learning & Advanced", 1, "MLPs, backpropagation by hand, CNNs, batch norm, dropout, and modern architectures."),
    "08": ("💬", "Deep Learning & Advanced", 2, "Tokenization, word embeddings, encoder & decoder transformers, and fine-tuning language models."),
    "09": ("⚡", "Deep Learning & Advanced", 2, "Attention from scratch — self-attention through multi-head, GQA, MLA, and KV caches."),
    "10": ("🎨", "Deep Learning & Advanced", 2, "Object detection, autoencoders, VAEs, GANs, diffusion models, CLIP, and adversarial attacks."),
    "11": ("🕸️", "Deep Learning & Advanced", 2, "Message passing, graph convolutions, and learning on graph-structured data."),
    "12": ("🏆", "Deep Learning & Advanced", 2, "Competition strategy and advanced integration — pulling every unit together."),
}

TRACKS = ["Foundations", "ML & PyTorch", "Deep Learning & Advanced"]

ACRONYMS = {
    "ai": "AI", "ml": "ML", "nlp": "NLP", "cnn": "CNN", "cnns": "CNNs",
    "mlp": "MLP", "mlps": "MLPs", "gqa": "GQA", "mla": "MLA", "kv": "KV",
    "svd": "SVD", "pca": "PCA", "vae": "VAE", "gan": "GAN", "gans": "GANs",
    "clip": "CLIP", "bert": "BERT", "gpt": "GPT", "ner": "NER", "bpe": "BPE",
    "knn": "k-NN", "svm": "SVM", "resnet": "ResNet", "pinn": "PINN",
    "vit": "ViT", "unet": "U-Net", "glove": "GloVe", "pytorch": "PyTorch",
    "numpy": "NumPy", "usaaio": "USAAIO", "og": "OG", "csv": "CSV",
    "na": "NA", "aio": "AIO", "gnn": "GNN", "gnns": "GNNs", "mha": "MHA",
    "latex": "LaTeX", "sklearn": "scikit-learn", "dbscan": "DBSCAN",
}

SMALL_WORDS = {"for", "in", "of", "and", "the", "on", "with", "to", "by", "vs", "a", "an"}


def titleize(slug):
    words = re.split(r"[-_ ]+", slug.strip())
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if lw in ACRONYMS:
            out.append(ACRONYMS[lw])
        elif i > 0 and lw in SMALL_WORDS:
            out.append(lw)
        else:
            out.append(w[:1].upper() + w[1:] if w else w)
    return " ".join(out)


def read_minutes(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except OSError:
        return None
    words = len(text.split())
    return max(1, round(words / 200))


def md_files(rel_dir):
    abs_dir = os.path.join(ROOT, rel_dir)
    if not os.path.isdir(abs_dir):
        return []
    return sorted(n for n in os.listdir(abs_dir) if n.endswith(".md"))


def nb_files(rel_dir):
    abs_dir = os.path.join(ROOT, rel_dir)
    if not os.path.isdir(abs_dir):
        return []
    return sorted(n for n in os.listdir(abs_dir) if n.endswith(".ipynb"))


def build_units():
    units = []
    for folder in sorted(os.listdir(os.path.join(ROOT, UNITS_DIR))):
        m = re.match(r"^(\d+)-(.+)$", folder)
        if not m:
            continue
        num, raw_title = m.group(1), m.group(2)
        icon, track, rnd, desc = UNIT_META.get(num, ("📘", "Deep Learning & Advanced", 2, ""))
        base = f"{UNITS_DIR}/{folder}"

        lessons = []
        for name in md_files(f"{base}/study-guide"):
            lm = re.match(r"^(\d+)-(.+)\.md$", name)
            if not lm:
                continue
            path = f"{base}/study-guide/{name}"
            lessons.append({
                "num": lm.group(1),
                "title": titleize(lm.group(2)),
                "path": path,
                "minutes": read_minutes(path),
            })

        exercises = []
        for name in md_files(f"{base}/exercises"):
            em = re.match(r"^(\d+)-(.+?)(?:-exercises)?\.md$", name)
            if not em:
                continue
            path = f"{base}/exercises/{name}"
            exercises.append({
                "num": em.group(1),
                "title": titleize(em.group(2)),
                "path": path,
                "minutes": read_minutes(path),
            })

        assignments = []
        for name in nb_files(f"{base}/assignments"):
            am = re.match(r"^assignment-(\d+)-(.+)\.ipynb$", name)
            if not am:
                continue
            assignments.append({
                "num": am.group(1),
                "title": titleize(am.group(2)),
                "path": f"{base}/assignments/{name}",
            })

        readme = f"{base}/README.md"
        cheat = f"{base}/cheat-sheet.md"
        units.append({
            "num": num,
            "slug": num,
            "title": titleize(raw_title),
            "icon": icon,
            "track": track,
            "round": rnd,
            "desc": desc,
            "dir": base,
            "readme": readme if os.path.isfile(os.path.join(ROOT, readme)) else None,
            "cheatsheet": cheat if os.path.isfile(os.path.join(ROOT, cheat)) else None,
            "lessons": lessons,
            "exercises": exercises,
            "assignments": assignments,
        })
    return units


def build_practice():
    base = "2026/practice/round-1-sample-variations"
    abs_dir = os.path.join(ROOT, base)
    problems = {}
    for name in sorted(os.listdir(abs_dir)):
        m = re.match(r"^problem-(\d+)-variations(?:-(.+?))?\.(md|ipynb)$", name)
        if not m:
            continue
        num, extra, ext = m.groups()
        p = problems.setdefault(num, {"num": num, "topic": titleize(extra) if extra else None})
        p["md" if ext == "md" else "nb"] = f"{base}/{name}"
    readme = f"{base}/README.md"
    return {
        "readme": readme if os.path.isfile(os.path.join(ROOT, readme)) else None,
        "problems": [problems[k] for k in sorted(problems)],
    }


def build_archive():
    base = "2025/notebooks"
    items = []
    for name in nb_files(base):
        m = re.match(r"^(\d+[ab]?)-(.+)\.ipynb$", name)
        if not m:
            continue
        items.append({"num": m.group(1), "title": titleize(m.group(2)), "path": f"{base}/{name}"})
    return items


VIEWABLE = {".md", ".ipynb", ".pdf", ".py", ".txt", ".csv", ".toml"}
SKIP_DIRS = {".git", ".ipynb_checkpoints", "__pycache__", "images", ".claude"}


def walk(rel_dir):
    abs_dir = os.path.join(ROOT, rel_dir)
    entries = []
    try:
        names = sorted(os.listdir(abs_dir))
    except FileNotFoundError:
        return entries
    files = [n for n in names if os.path.isfile(os.path.join(abs_dir, n))
             and os.path.splitext(n)[1].lower() in VIEWABLE]
    dirs = [n for n in names if os.path.isdir(os.path.join(abs_dir, n)) and n not in SKIP_DIRS]
    for name in sorted(files, key=lambda n: (n != "README.md", n.lower())):
        entries.append({"label": titleize(os.path.splitext(name)[0]), "type": "file",
                        "ext": os.path.splitext(name)[1][1:], "path": f"{rel_dir}/{name}"})
    for name in dirs:
        children = walk(f"{rel_dir}/{name}")
        if children:
            entries.append({"label": titleize(name), "type": "dir", "children": children})
    return entries


data = {
    "tracks": TRACKS,
    "units": build_units(),
    "practice": build_practice(),
    "archive": build_archive(),
    "official": walk("usaaio-official"),
    "round2prep": "2026/round-2-prep.md",
    "unitsReadme": "2026/units/README.md",
}

out = os.path.join(ROOT, "course-data.js")
with open(out, "w") as f:
    f.write("window.COURSE = ")
    json.dump(data, f, indent=1)
    f.write(";\n")

n_lessons = sum(len(u["lessons"]) for u in data["units"])
n_ex = sum(len(u["exercises"]) for u in data["units"])
n_as = sum(len(u["assignments"]) for u in data["units"])
print(f"Wrote course-data.js: {len(data['units'])} units, {n_lessons} lessons, "
      f"{n_ex} exercise sets, {n_as} assignments, {len(data['practice']['problems'])} practice problems")
