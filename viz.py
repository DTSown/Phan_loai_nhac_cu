"""Vẽ các hình minh họa kết quả trung gian (bước 4b)."""
import io, base64, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, librosa, librosa.display
from features import SR, group_slices

def fig_wave_mel(y):
    fig, ax = plt.subplots(2, 1, figsize=(8, 5.4), constrained_layout=True)

    # Waveform: cùng một thang biên độ [-1, 1] cho mọi truy vấn.
    t = np.arange(len(y)) / SR
    ax[0].plot(t, y, color="#183b5b", lw=0.75, alpha=0.9)
    ax[0].axhline(0, color="#6b7280", lw=0.8, ls="--", alpha=0.75)
    ax[0].set_xlim(0, max(t[-1], 1 / SR))
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].set_title("Waveform (dạng sóng)", loc="left", fontsize=11, fontweight="bold")
    ax[0].set_xlabel("Thời gian (s)")
    ax[0].set_ylabel("Biên độ chuẩn hóa")
    ax[0].grid(axis="x", color="#d1d5db", lw=0.5, alpha=0.65)

    # Mel-spectrogram: năng lượng dB cố định từ -80 đến 0 dB.
    M = librosa.power_to_db(
        librosa.feature.melspectrogram(y=y, sr=SR, n_mels=128, fmax=SR / 2),
        ref=np.max,
        top_db=80,
    )
    image = librosa.display.specshow(
        M, sr=SR, x_axis="time", y_axis="mel", cmap="magma",
        vmin=-80, vmax=0, ax=ax[1]
    )
    ax[1].set_title("Mel-spectrogram", loc="left", fontsize=11, fontweight="bold")
    ax[1].set_xlabel("Thời gian (s)")
    ax[1].set_ylabel("Tần số (Hz, thang Mel)")
    mel_ticks = [64, 256, 1000, 4000, 8000]
    ax[1].set_yticks(mel_ticks)
    ax[1].set_yticklabels(["64", "256", "1k", "4k", "8k"])
    colorbar = fig.colorbar(image, ax=ax[1], pad=0.02, format="%+2.0f dB")
    colorbar.set_label("Cường độ (dB)")
    return fig

def fig_zscore(q, ref=None, ref_name="Top-1"):
    fig, ax = plt.subplots(figsize=(10, 4.25), constrained_layout=True)
    x = np.arange(len(q))
    slices = group_slices()
    group_labels = {
        "mfcc": "MFCC (40)", "dmfcc": "ΔMFCC (20)", "spec": "Phổ (12)",
        "contrast": "Contrast (7)", "temp": "Thời gian (4)",
    }

    # Nền xen kẽ và vạch biên giúp đọc đúng 5 nhóm trong vector 83 chiều.
    span_colors = ["#f7f7f7", "#edf3f8"]
    for i, (g, s) in enumerate(slices.items()):
        ax.axvspan(s.start - 0.5, s.stop - 0.5, color=span_colors[i % 2], zorder=0)
        if s.start:
            ax.axvline(s.start - 0.5, color="#9ca3af", lw=0.8, zorder=1)
        label_y = 0.97 if g != "temp" else 0.88
        ax.text((s.start + s.stop - 1) / 2, label_y, group_labels[g],
                transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=8, color="#374151")

    ax.bar(x, q, width=0.78, color="#8db9dd", edgecolor="none", label="Query", zorder=2)
    if ref is not None:
        ax.plot(x, ref, color="#a33a3a", marker="o", lw=1.1, ms=2.4,
                label=ref_name, zorder=3)
        qn, rn = np.linalg.norm(q), np.linalg.norm(ref)
        cosine = float(np.dot(q, ref) / (qn * rn + 1e-12))
        corr = float(np.corrcoef(q, ref)[0, 1]) if np.std(q) and np.std(ref) else 0.0
        ax.text(0.99, 0.04, f"Tương quan r = {corr:.3f}\nCosine = {cosine:.3f}",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
                bbox=dict(facecolor="white", edgecolor="#b8b8b8", boxstyle="square,pad=0.35"))

    ax.axhline(0, color="#4b5563", lw=0.7)
    ax.set_xlim(-0.8, len(q) - 0.2)
    ax.set_ylim(-3, 3)
    ax.set_yticks(np.arange(-3, 4, 1))
    ax.set_xlabel("Chỉ số đặc trưng (0–82)")
    ax.set_ylabel("Z-score")
    ax.set_title("So sánh vector đặc trưng chuẩn hóa", loc="left", fontsize=11, fontweight="bold")
    ax.grid(axis="y", color="#d1d5db", lw=0.5, alpha=0.7, zorder=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2,
              fontsize=8, frameon=False)
    return fig

def to_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=80); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()
