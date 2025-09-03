# akademik/face_detect.py
import base64, os, sys, threading
from typing import List, Dict, Tuple
import numpy as np
import cv2
from django.conf import settings
from insightface.app import FaceAnalysis

try:
    import onnxruntime as ort
except Exception:
    ort = None

MODEL_NAME = 'buffalo_l'
DET_SIZE = (640, 640)
THRESHOLD = 0.60  # sesuai permintaan

# Lokasi file hasil enroll (selaras dengan 1_enroll_faces.py)  # :contentReference[oaicite:2]{index=2}
EMB_PATH = os.path.join(settings.BASE_DIR, 'DataFace/face_embeddings.npy')
NAME_PATH = os.path.join(settings.BASE_DIR, 'DataFace/face_names.npy')

# Singleton + lock untuk cegah race-condition
_app = None
_embeddings = None
_names = None
_init_lock = threading.Lock()
_logged = False

def _pick_providers() -> Tuple[list, str]:
    note = "CPU"
    providers = ['CPUExecutionProvider']
    if ort is not None:
        try:
            av = set(ort.get_available_providers())
            if 'CUDAExecutionProvider' in av:
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                note = "GPU (CUDA)"
        except Exception:
            pass
    return providers, note

def _ensure_loaded():
    global _app, _embeddings, _names, _logged
    with _init_lock:
        if _app is None:
            providers, note = _pick_providers()
            # allowed_modules biar hanya load yang perlu (lebih ringan & stabil)
            _app = FaceAnalysis(name=MODEL_NAME, allowed_modules=['detection','recognition'], providers=providers)
            # PENTING: prepare sebelum dipakai agar self.input_size terisi
            _app.prepare(ctx_id=0, det_size=DET_SIZE)
            if not _logged:
                print(f"[face_detect] InsightFace '{MODEL_NAME}' ready. Backend: {note}. Providers={providers}", file=sys.stderr, flush=True)
                _logged = True

        if _embeddings is None or _names is None:
            if not (os.path.exists(EMB_PATH) and os.path.exists(NAME_PATH)):
                raise FileNotFoundError("face_embeddings.npy / face_names.npy tidak ditemukan. Jalankan enroll. :contentReference[oaicite:3]{index=3}")
            _embeddings = np.load(EMB_PATH)
            _names = np.load(NAME_PATH)
            if _embeddings.ndim == 1:
                _embeddings = _embeddings.reshape(1, -1)
            if not _logged:
                print(f"[face_detect] Embeddings loaded: {_embeddings.shape}, Names: {_names.shape}", file=sys.stderr, flush=True)
                _logged = True

def _decode_b64_image(data_url: str):
    if ',' in data_url: data_url = data_url.split(',', 1)[1]
    arr = np.frombuffer(base64.b64decode(data_url), np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def _to_conf(score: float, thr: float = THRESHOLD) -> float:
    if score <= thr: return 0.0
    return float(max(0.0, min(1.0, (score - thr) / (1.0 - thr))) * 100.0)

def _split_label_nisn_nama(label: str) -> Tuple[str, str]:
    # Format: NISNNama (10 digit awal = NISN, sisanya = Nama lengkap).  # :contentReference[oaicite:4]{index=4}
    label = str(label or "")
    if len(label) >= 10 and label[:10].isdigit():
        return label[:10], label[10:].strip() or label
    # fallback: cari blok 10 digit pertama
    digits = ''.join(ch for ch in label if ch.isdigit())
    if len(digits) >= 10:
        nisn = digits[:10]
        nama = label.replace(nisn, '').strip() or label
        return nisn, nama
    return label, label

def detect_from_base64(frame_b64: str) -> List[Dict]:
    _ensure_loaded()
    img = _decode_b64_image(frame_b64)
    if img is None or img.size == 0:
        return []

    # (opsional) enforce size minimum → kurangi error detector di frame ganjil
    if img.shape[0] < 64 or img.shape[1] < 64:
        return []

    faces = _app.get(img)  # sudah prepared → aman
    results = []
    if faces:
        for f in faces:
            emb = f.normed_embedding.astype(np.float32)
            sims = _embeddings @ emb
            best_idx = int(np.argmax(sims))
            score = float(sims[best_idx])
            if score >= THRESHOLD:
                raw_label = str(_names[best_idx])
                nisn, nama = _split_label_nisn_nama(raw_label)
                results.append({
                    'label': raw_label,
                    'nisn': nisn,
                    'nama': nama,
                    'confidence': round(_to_conf(score), 1),
                    'bbox': f.bbox.astype(int).tolist() if hasattr(f, 'bbox') else None
                })
    return results
