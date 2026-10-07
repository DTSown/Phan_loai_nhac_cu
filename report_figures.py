
import sys, os, numpy as np, pandas as pd
from features import *
from search import Engine, W
from viz import fig_wave_mel, fig_zscore

path = sys.argv[1]; os.makedirs("figures", exist_ok=True)
eng = Engine(); y = load_audio(path); f = extract(y); v = to_vector(f)
res, q = eng.query_vec(v, 5)
base = os.path.splitext(os.path.basename(path))[0]

print("1) Độ dài sau tiền xử lý: %.3f s" % (len(y) / SR))
print("\n2) Đặc trưng thô (nhóm phổ + thời gian):")
for n, val in zip(SPEC_NAMES, f["spec"]): print(f"   {n:20s} {val:.5f}")
for n, val in zip(TEMP_NAMES, f["temp"]): print(f"   {n:20s} {val:.5f}")
print("\n3) Vector sau z-score: min=%.2f max=%.2f" % (q.min(), q.max()))
print("\n4) Top-5 (điểm từng nhóm và tổng):")
tab = pd.DataFrame([{"rank": r["rank"], "file": r["file"], "label": r["label"],
                     **{g: round(r["groups"][g], 3) for g in GROUPS}, "TONG": round(r["score"], 3)} for r in res])
print(tab.to_string(index=False)); tab.to_csv(f"figures/{base}_top5.csv", index=False)
print("\n   Trọng số:", W)

fig_wave_mel(y).savefig(f"figures/{base}_wave_mel.png", dpi=120)
fig_zscore(q, eng.Z[res[0]["idx"]], f"Top-1: {res[0]['file']}").savefig(f"figures/{base}_zscore.png", dpi=120)
print("\nĐã lưu hình vào figures/")
