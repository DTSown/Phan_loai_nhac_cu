
import os, uuid, glob
from collections import Counter
from flask import Flask, request, render_template, send_file, abort
from features import *
from search import Engine, W
from viz import fig_wave_mel, fig_zscore, to_b64

app = Flask(__name__); eng = Engine()
UP = "uploads"; os.makedirs(UP, exist_ok=True)
QFILES = {}                                    # token -> đường dẫn file query

def list_samples(per_class=8):
    out = []
    for kind in ("seen", "unseen"):
        for cls in sorted(glob.glob(f"query/{kind}/*")):
            fs = sorted(f for f in glob.glob(cls + "/*") if f.lower().endswith(".wav"))[:per_class]
            out += [(f"{kind}/{os.path.basename(cls)}/{os.path.basename(f)}", f) for f in fs]
    return out
SAMPLES = list_samples()

@app.route("/", methods=["GET", "POST"])
def index():
    ctx = dict(samples=[s[0] for s in SAMPLES])
    if request.method == "POST":
        path, qname = None, None
        f = request.files.get("audio")
        if f and f.filename:
            ext = os.path.splitext(f.filename)[1] or ".wav"
            path = os.path.join(UP, uuid.uuid4().hex + ext); f.save(path); qname = f.filename
        elif request.form.get("sample"):
            d = dict(SAMPLES)
            if request.form["sample"] in d: path = d[request.form["sample"]]; qname = request.form["sample"]
        if path:
            try:
                y = load_audio(path); feats = extract(y); v = to_vector(feats)
            except Exception as e:
                ctx["error"] = f"Không đọc được file: {e}"; return render_template("index.html", **ctx)
            results, q = eng.query_vec(v, k=5)
            token = uuid.uuid4().hex; QFILES[token] = path
            rows = list(zip(SPEC_NAMES, feats["spec"])) + list(zip(TEMP_NAMES, feats["temp"]))
            ctx.update(qname=qname, token=token, results=results, W=W, dur=len(y) / SR,
                       img1=to_b64(fig_wave_mel(y)),
                       img2=to_b64(fig_zscore(q, eng.Z[results[0]["idx"]], "Top-1")),
                       feat_rows=[(n, round(float(x), 5)) for n, x in rows],
                       votes=Counter(r["label"] for r in results).most_common())
    return render_template("index.html", **ctx)

@app.route("/audio/<int:i>")
def audio(i):
    p = eng.path_by_id.get(i)
    if not p: abort(404)
    return send_file(os.path.abspath(p))

@app.route("/query_audio/<token>")
def query_audio(token):
    p = QFILES.get(token)
    if not p: abort(404)
    return send_file(os.path.abspath(p))

if __name__ == "__main__":
    app.run(debug=False)
