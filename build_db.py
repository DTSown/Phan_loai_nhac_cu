
import sqlite3, glob, os, json, numpy as np
from joblib import Parallel, delayed
from features import *

def proc(path):
    try:
        y = load_audio(path)
        if np.max(np.abs(y)) < 1e-4: return None
        return path, len(y) / SR, extract(y)
    except Exception as e:
        print("Bỏ qua", path, e); return None

if __name__ == "__main__":                     # bắt buộc trên Windows
    paths = sorted(p for p in glob.glob("data/*/*") if p.lower().endswith(".wav"))
    print("Số file:", len(paths))
    results = [r for r in Parallel(n_jobs=-1, verbose=5)(delayed(proc)(p) for p in paths) if r]

    con = sqlite3.connect("perc.db"); c = con.cursor()
    c.executescript("""
    DROP TABLE IF EXISTS audio; DROP TABLE IF EXISTS feature; DROP TABLE IF EXISTS scaler;
    CREATE TABLE audio(id INTEGER PRIMARY KEY, filename TEXT, path TEXT, label TEXT, duration REAL);
    CREATE TABLE feature(audio_id INTEGER PRIMARY KEY REFERENCES audio(id),
        mfcc TEXT, dmfcc TEXT, spec TEXT, contrast TEXT, temp TEXT, vec BLOB);
    CREATE TABLE scaler(name TEXT PRIMARY KEY, mean BLOB, std BLOB);
    CREATE INDEX idx_label ON audio(label);
    """)
    vecs = []
    for path, dur, f in results:
        label = os.path.basename(os.path.dirname(path)); v = to_vector(f)
        c.execute("INSERT INTO audio(filename,path,label,duration) VALUES(?,?,?,?)",
                  (os.path.basename(path), path, label, dur))
        c.execute("INSERT INTO feature VALUES(?,?,?,?,?,?,?)",
                  (c.lastrowid, *[json.dumps(f[g].tolist()) for g in GROUPS], v.tobytes()))
        vecs.append(v)
    X = np.stack(vecs); mu, sd = X.mean(0), X.std(0) + 1e-9
    c.execute("INSERT INTO scaler VALUES('z',?,?)",
              (mu.astype(np.float32).tobytes(), sd.astype(np.float32).tobytes()))
    con.commit(); con.close()
    print("Xong:", X.shape, "| bị loại:", len(paths) - len(results))
