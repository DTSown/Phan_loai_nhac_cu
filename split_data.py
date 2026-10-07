
import os, glob, random, shutil, argparse, hashlib

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default="raw_data")
ap.add_argument("--unseen", nargs="*", default=[], help="tên thư mục các lớp làm nhạc cụ lạ")
ap.add_argument("--ratio", type=float, default=0.05)
ap.add_argument("--seed", type=int, default=42)
a = ap.parse_args()
random.seed(a.seed)

if os.path.isdir("data") and os.listdir("data"):
    raise SystemExit("data/ đã có dữ liệu. Xóa data/ và query/ rồi chạy lại.")

for cls in sorted(os.listdir(a.raw)):
    src = os.path.join(a.raw, cls)
    if not os.path.isdir(src): continue
    files = sorted(f for f in glob.glob(os.path.join(src, "**", "*"), recursive=True)
                   if os.path.isfile(f) and f.lower().endswith(".wav"))
    if cls in a.unseen:
        dst = os.path.join("query", "unseen", cls); os.makedirs(dst, exist_ok=True)
        for f in files: shutil.copy(f, dst)
        print(f"{cls:15s} UNSEEN: {len(files)} file -> query/unseen")
        continue
    groups = {}
    for f in files:
        groups.setdefault(md5(f), []).append(f)
    groups = list(groups.values())
    random.shuffle(groups)
    n_q = max(1, int(len(files) * a.ratio))
    q, d = [], []
    for group in groups:
        (q if len(q) < n_q else d).extend(group)
    os.makedirs(os.path.join("query", "seen", cls), exist_ok=True)
    os.makedirs(os.path.join("data", cls), exist_ok=True)
    for f in q: shutil.copy(f, os.path.join("query", "seen", cls))
    for f in d: shutil.copy(f, os.path.join("data", cls))
    print(f"{cls:15s} data: {len(d)}  query: {len(q)}")
