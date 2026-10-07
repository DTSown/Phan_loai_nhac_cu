"""Thống kê độ dài, sample rate, số kênh, số file mỗi lớp (dùng cho mô tả dữ liệu ở bước 1)."""
import os, sys, soundfile as sf, pandas as pd
root = sys.argv[1] if len(sys.argv) > 1 else "raw_data"
rows = []
errors = []
wav_paths = []
for dirpath, _, filenames in os.walk(root):
    for filename in filenames:
        if filename.lower().endswith(".wav"):
            wav_paths.append(os.path.join(dirpath, filename))
for p in wav_paths:
    try:
        i = sf.info(p)
        label = os.path.relpath(p, root).split(os.sep)[0]
        rows.append((label, i.duration, i.samplerate, i.channels, i.subtype))
    except Exception as e:
        errors.append((p, str(e)))
        print("LỖI:", p, e)
df = pd.DataFrame(rows, columns=["label", "dur", "sr", "ch", "subtype"])
print("Tổng số file:", len(df))
print("Số lớp:", df.label.nunique())
print(df.dur.describe().round(3))
print(df.groupby("label").dur.agg(["count", "mean", "min", "max"]).round(2))
print(df.sr.value_counts()); print(df.ch.value_counts()); print(df.subtype.value_counts())
print("File < 0.2 s:", (df.dur < 0.2).sum())
print("File lỗi đọc:", len(errors))
print("File WAV có đuôi không viết thường:", sum(not p.endswith(".wav") for p in wav_paths))
df.to_csv("dataset_info.csv", index=False)
