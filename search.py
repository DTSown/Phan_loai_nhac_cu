"""BƯỚC 4: bộ máy tìm kiếm (chuẩn hóa z-score, cosine theo nhóm, cộng có trọng số)."""
import sqlite3, numpy as np
from features import *

W = {"mfcc": .35, "dmfcc": .10, "spec": .20, "contrast": .15, "temp": .20}
SL = group_slices()

class Engine:
    def __init__(self, db="perc.db"):
        con = sqlite3.connect(db)
        rows = con.execute("""SELECT a.id,a.filename,a.path,a.label,f.vec
                              FROM audio a JOIN feature f ON a.id=f.audio_id ORDER BY a.id""").fetchall()
        m, s = con.execute("SELECT mean,std FROM scaler WHERE name='z'").fetchone()
        con.close()
        self.meta = [dict(id=r[0], file=r[1], path=r[2], label=r[3]) for r in rows]
        self.path_by_id = {m_["id"]: m_["path"] for m_ in self.meta}
        self.X = np.stack([np.frombuffer(r[4], dtype=np.float32) for r in rows])
        self.mu = np.frombuffer(m, dtype=np.float32); self.sd = np.frombuffer(s, dtype=np.float32)
        self.Z = (self.X - self.mu) / self.sd

    @staticmethod
    def _cos(Z, q):
        return (Z @ q) / (np.linalg.norm(Z, axis=1) * np.linalg.norm(q) + 1e-9)

    def query_vec(self, raw_vec, k=5, weights=None):
        w = weights or W
        q = (raw_vec - self.mu) / self.sd
        per_group = {g: self._cos(self.Z[:, SL[g]], q[SL[g]]) for g in GROUPS}
        score = sum(w[g] * per_group[g] for g in GROUPS)
        idx = np.argsort(-score)[:k]
        res = [{"rank": r + 1, "idx": int(i), "id": self.meta[i]["id"], "file": self.meta[i]["file"],
                "label": self.meta[i]["label"], "score": float(score[i]),
                "groups": {g: float(per_group[g][i]) for g in GROUPS}} for r, i in enumerate(idx)]
        return res, q
