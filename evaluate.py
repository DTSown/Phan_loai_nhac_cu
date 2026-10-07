
import os, glob, numpy as np, pandas as pd
from collections import Counter
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from features import *
from search import Engine, W

OUT = "evaluation_results"; os.makedirs(OUT, exist_ok=True)
eng = Engine(); SL = group_slices()
labels = np.array([m["label"] for m in eng.meta]); N = len(labels)
classes = sorted(set(labels))
Zn = {}
for g in GROUPS:
    Z = eng.Z[:, SL[g]]; Zn[g] = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9)

def run(weights, block=1000):
    p5, top1, ap, pred = [], [], [], []
    for s in range(0, N, block):
        e = min(N, s + block)
        S = sum(weights[g] * (Zn[g][s:e] @ Zn[g].T) for g in GROUPS if weights[g] > 0)
        S[np.arange(e - s), np.arange(s, e)] = -9          # loại chính nó
        order = np.argsort(-S, axis=1)[:, :-1]
        for r in range(e - s):
            rel = labels[order[r]] == labels[s + r]
            p5.append(rel[:5].mean()); top1.append(rel[0]); pred.append(labels[order[r][0]])
            ap.append((np.cumsum(rel)[rel] / (np.flatnonzero(rel) + 1)).mean() if rel.any() else 0)
    return {"P@5": np.mean(p5), "Top1": np.mean(top1), "mAP": np.mean(ap)}, np.array(p5), np.array(pred)

print("== Leave-one-out trên CSDL (%d file) ==" % N)
rows = {}
full, p5_full, pred_full = run(W); rows["Tất cả nhóm"] = full
for g in GROUPS:
    rows[f"Chỉ {g}"], _, _ = run({k: float(k == g) for k in GROUPS})
for g in GROUPS:
    w = {k: (0 if k == g else W[k]) for k in GROUPS}; t = sum(w.values())
    rows[f"Bỏ {g}"], _, _ = run({k: v / t for k, v in w.items()})
res = pd.DataFrame(rows).T.round(4); print(res.to_string()); res.to_csv(f"{OUT}/ablation.csv")

pc = pd.Series(p5_full).groupby(labels).mean().round(4)
print("\nP@5 theo lớp:\n", pc.to_string()); pc.to_csv(f"{OUT}/p5_per_class.csv")

class_index = {label: i for i, label in enumerate(classes)}
cm = np.zeros((len(classes), len(classes)), dtype=int)
np.add.at(cm, ([class_index[x] for x in labels],
               [class_index[x] for x in pred_full]), 1)
cmn = cm / cm.sum(1, keepdims=True)
pd.DataFrame(cm, index=classes, columns=classes).to_csv(f"{OUT}/confusion_matrix.csv")
fig, ax = plt.subplots(figsize=(8, 7)); im = ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(classes))); ax.set_xticklabels(classes, rotation=60, ha="right")
ax.set_yticks(range(len(classes))); ax.set_yticklabels(classes)
ax.set_xlabel("Nhãn của Top-1"); ax.set_ylabel("Nhãn thật"); fig.colorbar(im)
fig.tight_layout(); fig.savefig(f"{OUT}/confusion_matrix.png", dpi=120); plt.close(fig)
off = [(classes[i], classes[j], cm[i, j]) for i in range(len(classes)) for j in range(len(classes)) if i != j]
print("\nCác cặp hay bị nhầm nhất:")
for a, b, n in sorted(off, key=lambda t: -t[2])[:8]: print(f"  {a} -> {b}: {n}")

print("\n== Query ngoài CSDL ==")
def top5_of(path):
    y = load_audio(path); r, _ = eng.query_vec(to_vector(extract(y)), 5); return r
seen = sorted(glob.glob("query/seen/*/*.wav"))
if seen:
    p5s, t1s = [], []
    for p in seen:
        lab = os.path.basename(os.path.dirname(p)); r = top5_of(p)
        rel = [x["label"] == lab for x in r]; p5s.append(np.mean(rel)); t1s.append(rel[0])
    print(f"Query lớp đã có ({len(seen)} file): P@5={np.mean(p5s):.4f}  Top1={np.mean(t1s):.4f}")
unseen = sorted(glob.glob("query/unseen/*/*.wav"))
rep = []
for cls in sorted({os.path.basename(os.path.dirname(p)) for p in unseen}):
    cnt = Counter()
    fs = [p for p in unseen if os.path.basename(os.path.dirname(p)) == cls]
    for p in fs:
        for x in top5_of(p): cnt[x["label"]] += 1
    tot = sum(cnt.values())
    print(f"Lớp lạ '{cls}' ({len(fs)} file) - phân bố nhãn trong Top-5:")
    for k, v in cnt.most_common(5):
        print(f"   {k:15s} {100 * v / tot:5.1f}%"); rep.append((cls, k, v / tot))
if rep: pd.DataFrame(rep, columns=["lop_la", "nhan_giong_nhat", "ty_le"]).to_csv(f"{OUT}/unseen_distribution.csv", index=False)
print("\nKết quả lưu trong", OUT)
