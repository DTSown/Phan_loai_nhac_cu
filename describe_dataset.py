"""BƯỚC 1: mô tả đặc điểm giống/khác giữa các lớp nhạc cụ bằng thống kê từ CSDL."""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from search import Engine
from features import feature_names

eng = Engine()
df = pd.DataFrame(eng.X, columns=feature_names()); df["label"] = [m["label"] for m in eng.meta]
cols = ["centroid_mean", "bandwidth_mean", "rolloff_mean", "flatness_mean", "zcr_mean", "rms_mean",
        "attack_s", "decay_s", "temporal_centroid_s", "spectral_flux"]
summary = df.groupby("label")[cols].mean()
summary["n_files"] = df.groupby("label").size()
summary["duration_mean"] = pd.Series({k: np.mean([m["id"] for m in []] or [0]) for k in []}, dtype=float)
summary = summary.drop(columns="duration_mean")
print(summary.round(4).to_string())
summary.round(4).to_csv("class_summary.csv")

z = (summary[cols] - summary[cols].mean()) / (summary[cols].std() + 1e-9)
fig, ax = plt.subplots(figsize=(10, 0.45 * len(z) + 2))
im = ax.imshow(z.values, aspect="auto", cmap="coolwarm", vmin=-2.5, vmax=2.5)
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right")
ax.set_yticks(range(len(z))); ax.set_yticklabels(z.index)
fig.colorbar(im, label="z-score giữa các lớp"); ax.set_title("Đặc trưng trung bình theo lớp nhạc cụ")
fig.tight_layout(); fig.savefig("class_means.png", dpi=120)
print("Đã lưu class_summary.csv, class_means.png")
