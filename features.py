
import numpy as np, librosa

SR, MAXDUR, HOP = 22050, 3.0, 512
MIN_LEN = int(SR * 0.25)                      # đủ > 9 frame cho delta
GROUPS = ["mfcc", "dmfcc", "spec", "contrast", "temp"]
DIMS = {"mfcc": 40, "dmfcc": 20, "spec": 12, "contrast": 7, "temp": 4}
SPEC_NAMES = ["centroid_mean", "centroid_std", "bandwidth_mean", "bandwidth_std",
              "rolloff_mean", "rolloff_std", "flatness_mean", "flatness_std",
              "zcr_mean", "zcr_std", "rms_mean", "rms_std"]
TEMP_NAMES = ["attack_s", "decay_s", "temporal_centroid_s", "spectral_flux"]

def feature_names():
    names = []
    for g in GROUPS:
        if g == "mfcc": names += [f"mfcc{i}_mean" for i in range(20)] + [f"mfcc{i}_std" for i in range(20)]
        elif g == "dmfcc": names += [f"dmfcc{i}_mean" for i in range(20)]
        elif g == "spec": names += SPEC_NAMES
        elif g == "contrast": names += [f"contrast{i}" for i in range(7)]
        else: names += TEMP_NAMES
    return names

def load_audio(path):
    y, _ = librosa.load(path, sr=SR, mono=True)
    y, _ = librosa.effects.trim(y, top_db=40)
    y = y[: int(SR * MAXDUR)]
    if len(y) < MIN_LEN:
        y = np.pad(y, (0, MIN_LEN - len(y)), mode="constant")
    return librosa.util.normalize(y)

def ms(x):                                     # mean + std theo thời gian
    return np.concatenate([x.mean(axis=1), x.std(axis=1)])

def extract(y):
    S = np.abs(librosa.stft(y, hop_length=HOP))
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, hop_length=HOP)
    dm = librosa.feature.delta(mfcc)

    cen = librosa.feature.spectral_centroid(S=S, sr=SR)
    bw = librosa.feature.spectral_bandwidth(S=S, sr=SR)
    ro = librosa.feature.spectral_rolloff(S=S, sr=SR)
    fl = librosa.feature.spectral_flatness(S=S)
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=HOP)
    rms = librosa.feature.rms(S=S)
    spec = np.concatenate([ms(f) for f in (cen, bw, ro, fl, zcr, rms)])
    contrast = librosa.feature.spectral_contrast(S=S, sr=SR).mean(axis=1)

    env = rms[0]
    pk = int(np.argmax(env)); peak = env[pk] + 1e-12
    t = np.arange(len(env)) * HOP / SR
    start = int(np.argmax(env >= 0.1 * peak))
    attack = t[pk] - t[start]
    after = np.where(env[pk:] < 0.1 * peak)[0]
    decay = (after[0] if len(after) else len(env) - pk) * HOP / SR
    tcent = (t * env).sum() / (env.sum() + 1e-9)
    flux = np.sqrt((np.diff(S, axis=1).clip(min=0) ** 2).sum(axis=0)).mean()
    temp = np.array([attack, decay, tcent, flux])

    return {"mfcc": ms(mfcc), "dmfcc": dm.mean(axis=1), "spec": spec,
            "contrast": contrast, "temp": temp}

def to_vector(d):
    return np.concatenate([d[g] for g in GROUPS]).astype(np.float32)

def group_slices():
    s, i = {}, 0
    for g in GROUPS:
        s[g] = slice(i, i + DIMS[g]); i += DIMS[g]
    return s
