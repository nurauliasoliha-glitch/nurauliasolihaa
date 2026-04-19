import os
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Coffee QC — Deteksi Cacat Biji Kopi",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background-color: #0f0d0b; color: #f0e6d0; }

section[data-testid="stSidebar"] {
    background-color: #1a1713 !important;
    border-right: 1px solid #2e2920;
}
section[data-testid="stSidebar"] * { color: #f0e6d0 !important; }

.hero-title {
    font-family: 'Fraunces', serif;
    font-size: 2.6rem; font-weight: 900;
    background: linear-gradient(135deg, #c9a84c 0%, #f5d78e 50%, #c9a84c 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -0.03em; margin-bottom: 0;
}
.hero-sub {
    color: #9e9080; font-size: 0.82rem;
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1.5rem;
}
.stat-grid { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1rem 0; }
.stat-card {
    flex: 1; min-width: 100px;
    background: #1a1713; border: 1px solid #2e2920;
    border-radius: 10px; padding: 1.1rem 1rem; text-align: center;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
}
.stat-total::before      { background: #c9a84c; }
.stat-normal::before     { background: #22c55e; }
.stat-broken::before     { background: #ef4444; }
.stat-scorching::before  { background: #f97316; }
.stat-underdevelop::before { background: #a855f7; }
.stat-count {
    font-family: 'Fraunces', serif;
    font-size: 2.4rem; font-weight: 700; line-height: 1;
}
.stat-total   .stat-count { color: #c9a84c; }
.stat-normal  .stat-count { color: #22c55e; }
.stat-broken  .stat-count { color: #ef4444; }
.stat-scorching .stat-count { color: #f97316; }
.stat-underdevelop .stat-count { color: #a855f7; }
.stat-label {
    font-size: 0.67rem; text-transform: uppercase;
    letter-spacing: 0.1em; color: #9e9080;
    margin-top: 0.3rem; font-family: 'DM Mono', monospace;
}
.tag {
    display: inline-block; padding: 0.2rem 0.65rem;
    border-radius: 20px; font-size: 0.75rem; font-weight: 500;
}
.tag-normal      { background: rgba(34,197,94,0.15);  color: #22c55e; }
.tag-broken      { background: rgba(239,68,68,0.15);  color: #ef4444; }
.tag-scorching   { background: rgba(249,115,22,0.15); color: #f97316; }
.tag-underdevelop { background: rgba(168,85,247,0.15); color: #a855f7; }
.det-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.det-table th {
    padding: 0.6rem 1rem; text-align: left;
    font-family: 'DM Mono', monospace; font-size: 0.67rem;
    color: #9e9080; letter-spacing: 0.1em; text-transform: uppercase;
    border-bottom: 1px solid #2e2920; background: #1a1713;
}
.det-table td {
    padding: 0.55rem 1rem;
    border-bottom: 1px solid rgba(46,41,32,0.5); color: #f0e6d0;
}
.det-table tr:hover td { background: rgba(201,168,76,0.03); }
.det-table tr:last-child td { border-bottom: none; }
.mono { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #9e9080; }
.info-box {
    background: #1a1713; border: 1px solid #2e2920;
    border-left: 3px solid #c9a84c; border-radius: 8px;
    padding: 0.85rem 1.1rem; margin-bottom: 1rem;
    font-size: 0.82rem; color: #9e9080; line-height: 1.6;
}
.info-box b { color: #c9a84c; }
.warn-box {
    background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.3);
    border-radius: 8px; padding: 0.85rem 1.1rem;
    font-size: 0.82rem; color: #f87171; margin-bottom: 0.8rem;
}
hr { border-color: #2e2920 !important; }
#MainMenu, footer { visibility: hidden; }
.stButton > button {
    background: linear-gradient(135deg, #c9a84c 0%, #a87c2e 100%) !important;
    color: #0f0d0b !important; font-weight: 700 !important;
    border: none !important; width: 100% !important;
    padding: 0.7rem !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.04em !important; font-size: 0.9rem !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(201,168,76,0.35) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: #1a1713 !important; color: #c9a84c !important;
    border: 1px solid #c9a84c !important; width: 100% !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
CLASSES = ['normal', 'broken', 'scorching', 'underdevelop']
CLASS_COLORS_RGB = {
    'normal':       (34,  197,  94),
    'broken':       (239,  68,  68),
    'scorching':    (249, 115,  22),
    'underdevelop': (168,  85, 247),
}
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# ─────────────────────────────────────────────────────────────
# MODEL LOADING (cached agar tidak reload terus)
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_yolov8():
    try:
        from ultralytics import YOLO
        path = os.path.join(MODEL_DIR, 'best.pt')
        if not os.path.exists(path):
            return None, f"❌ File tidak ditemukan: models/best.pt"
        model = YOLO(path)
        return model, None
    except ImportError:
        return None, "❌ Library 'ultralytics' belum terinstall. Jalankan: pip install ultralytics"
    except Exception as e:
        return None, f"❌ Gagal load YOLOv8: {e}"

@st.cache_resource(show_spinner=False)
def load_faster_rcnn():
    try:
        import torch
        from torchvision.models.detection import fasterrcnn_resnet50_fpn
        from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
        path = os.path.join(MODEL_DIR, 'faster_rcnn_kopi_best.pth')
        if not os.path.exists(path):
            return None, f"❌ File tidak ditemukan: models/faster_rcnn_kopi_best.pth"
        num_classes = len(CLASSES) + 1
        model = fasterrcnn_resnet50_fpn(weights=None, num_classes=num_classes)
        in_feat = model.roi_heads.box_predictor.cls_score.in_features
        from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
        model.roi_heads.box_predictor = FastRCNNPredictor(in_feat, num_classes)
        ckpt = torch.load(path, map_location='cpu')
        state = (ckpt.get('model_state_dict') or ckpt.get('state_dict') or ckpt)
        model.load_state_dict(state)
        model.eval()
        return model, None
    except ImportError:
        return None, "❌ Library 'torchvision' belum terinstall. Jalankan: pip install torchvision"
    except Exception as e:
        return None, f"❌ Gagal load Faster R-CNN: {e}"

@st.cache_resource(show_spinner=False)
def load_ssd():
    try:
        import torch
        from torchvision.models.detection import ssd300_vgg16
        path = os.path.join(MODEL_DIR, 'ssd_kopi_best.pth')
        if not os.path.exists(path):
            return None, f"❌ File tidak ditemukan: models/ssd_kopi_best.pth"
        num_classes = len(CLASSES) + 1
        model = ssd300_vgg16(weights=None, num_classes=num_classes)
        ckpt = torch.load(path, map_location='cpu')
        state = (ckpt.get('model_state_dict') or ckpt.get('state_dict') or ckpt)
        model.load_state_dict(state)
        model.eval()
        return model, None
    except ImportError:
        return None, "❌ Library 'torchvision' belum terinstall. Jalankan: pip install torchvision"
    except Exception as e:
        return None, f"❌ Gagal load SSD: {e}"

# ─────────────────────────────────────────────────────────────
# INFERENCE
# ─────────────────────────────────────────────────────────────
def run_yolov8(image_pil, conf):
    model, err = load_yolov8()
    if err:
        return None, err
    results = model(image_pil, conf=conf)[0]
    detections = []
    for box in results.boxes:
        cls_idx  = int(box.cls.item())
        conf_val = float(box.conf.item())
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls_name = CLASSES[cls_idx] if cls_idx < len(CLASSES) else f"class_{cls_idx}"
        detections.append({
            'class': cls_name,
            'confidence': round(conf_val, 3),
            'bbox': [round(x1), round(y1), round(x2), round(y2)]
        })
    return detections, None

def run_faster_rcnn(image_pil, conf):
    import torch
    import torchvision.transforms.functional as F
    model, err = load_faster_rcnn()
    if err:
        return None, err
    tensor = F.to_tensor(image_pil.convert('RGB'))
    with torch.no_grad():
        outputs = model([tensor])[0]
    detections = []
    for i in range(len(outputs['scores'])):
        score = float(outputs['scores'][i].item())
        if score < conf:
            continue
        label = int(outputs['labels'][i].item())
        x1, y1, x2, y2 = outputs['boxes'][i].tolist()
        cls_name = CLASSES[label - 1] if 1 <= label <= len(CLASSES) else f"class_{label}"
        detections.append({
            'class': cls_name,
            'confidence': round(score, 3),
            'bbox': [round(x1), round(y1), round(x2), round(y2)]
        })
    return detections, None

def run_ssd(image_pil, conf):
    import torch
    import torchvision.transforms.functional as F
    model, err = load_ssd()
    if err:
        return None, err
    orig_w, orig_h = image_pil.size
    img300  = image_pil.convert('RGB').resize((300, 300))
    tensor  = F.to_tensor(img300)
    sx, sy  = orig_w / 300, orig_h / 300
    with torch.no_grad():
        outputs = model([tensor])[0]
    detections = []
    for i in range(len(outputs['scores'])):
        score = float(outputs['scores'][i].item())
        if score < conf:
            continue
        label = int(outputs['labels'][i].item())
        x1, y1, x2, y2 = outputs['boxes'][i].tolist()
        cls_name = CLASSES[label - 1] if 1 <= label <= len(CLASSES) else f"class_{label}"
        detections.append({
            'class': cls_name,
            'confidence': round(score, 3),
            'bbox': [round(x1*sx), round(y1*sy), round(x2*sx), round(y2*sy)]
        })
    return detections, None

def run_inference(model_name, image_pil, conf):
    if model_name == 'YOLOv8':
        return run_yolov8(image_pil, conf)
    elif model_name == 'Faster R-CNN':
        return run_faster_rcnn(image_pil, conf)
    elif model_name == 'SSD':
        return run_ssd(image_pil, conf)
    return None, "Model tidak dikenali"

# ─────────────────────────────────────────────────────────────
# DRAW BOUNDING BOXES
# ─────────────────────────────────────────────────────────────
def draw_boxes(image_pil, detections):
    img  = image_pil.convert('RGB').copy()
    draw = ImageDraw.Draw(img)
    try:
        # Coba load font — fallback ke default jika tidak ada
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, 14)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    for det in detections:
        cls  = det['class']
        conf = det['confidence']
        x1, y1, x2, y2 = det['bbox']
        color = CLASS_COLORS_RGB.get(cls, (255, 255, 0))
        # Kotak tebal
        for t in range(3):
            draw.rectangle([x1-t, y1-t, x2+t, y2+t], outline=color)
        # Label
        label     = f"{cls} {conf:.2f}"
        text_bbox = draw.textbbox((x1, y1 - 18), label, font=font)
        draw.rectangle([text_bbox[0]-2, text_bbox[1]-2,
                        text_bbox[2]+2, text_bbox[3]+2], fill=color)
        draw.text((x1, y1 - 18), label, fill=(255, 255, 255), font=font)
    return img

def count_classes(detections):
    counts = {c: 0 for c in CLASSES}
    for det in detections:
        if det['class'] in counts:
            counts[det['class']] += 1
    counts['total'] = sum(counts[c] for c in CLASSES)
    return counts

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.3rem 0 1.5rem'>
      <div style='font-family:Fraunces,serif;font-size:1.75rem;font-weight:900;
                  background:linear-gradient(135deg,#c9a84c,#f5d78e,#c9a84c);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;letter-spacing:-0.03em'>☕ Coffee QC</div>
      <div style='color:#9e9080;font-size:0.7rem;letter-spacing:0.1em;
                  text-transform:uppercase;margin-top:0.2rem'>
        Deteksi Cacat Biji Kopi
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Pilih Model ──
    st.markdown("""<div style='font-size:0.67rem;letter-spacing:0.14em;
        text-transform:uppercase;color:#8a6f2e;font-family:DM Mono,monospace;
        margin-bottom:0.5rem'>Pilih Model</div>""", unsafe_allow_html=True)

    model_choice = st.selectbox(
        "Model", ["YOLOv8", "Faster R-CNN", "SSD"],
        label_visibility="collapsed"
    )

    info = {
        "YOLOv8":       ("⚡", "Real-time · Tercepat", "best.pt"),
        "Faster R-CNN": ("🔍", "Akurasi Tinggi · ResNet50", "faster_rcnn_kopi_best.pth"),
        "SSD":          ("📦", "Single Shot · VGG16", "ssd_kopi_best.pth"),
    }
    icon, desc, fname = info[model_choice]
    st.markdown(f"""
    <div class='info-box'>
      {icon} <b>{model_choice}</b><br>
      {desc}<br>
      <span style='font-family:DM Mono,monospace;font-size:0.75rem;color:#8a6f2e'>{fname}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Confidence ──
    st.markdown("""<div style='font-size:0.67rem;letter-spacing:0.14em;
        text-transform:uppercase;color:#8a6f2e;font-family:DM Mono,monospace;
        margin-bottom:0.5rem'>Confidence Threshold</div>""", unsafe_allow_html=True)

    conf_threshold = st.slider(
        "conf", min_value=0.05, max_value=0.95,
        value=0.25, step=0.05, label_visibility="collapsed"
    )
    st.markdown(
        f"<div style='font-family:DM Mono,monospace;font-size:0.85rem;"
        f"color:#c9a84c;text-align:right;margin-top:-0.5rem'>{conf_threshold:.2f}</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ── Legenda Kelas ──
    st.markdown("""<div style='font-size:0.67rem;letter-spacing:0.14em;
        text-transform:uppercase;color:#8a6f2e;font-family:DM Mono,monospace;
        margin-bottom:0.7rem'>Kelas Defek</div>""", unsafe_allow_html=True)

    legend = [
        ("normal",       "#22c55e", "Biji sehat"),
        ("broken",       "#ef4444", "Retak / pecah"),
        ("scorching",    "#f97316", "Gosong / terbakar"),
        ("underdevelop", "#a855f7", "Kurang matang"),
    ]
    for cls, color, keterangan in legend:
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:0.6rem;
                    margin-bottom:0.45rem;font-size:0.82rem'>
          <div style='width:10px;height:10px;border-radius:50%;
                      background:{color};flex-shrink:0'></div>
          <span><b style='color:{color}'>{cls.capitalize()}</b>
            <span style='color:#9e9080'> — {keterangan}</span>
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Status Model ──
    st.markdown("""<div style='font-size:0.67rem;letter-spacing:0.14em;
        text-transform:uppercase;color:#8a6f2e;font-family:DM Mono,monospace;
        margin-bottom:0.6rem'>Status Model</div>""", unsafe_allow_html=True)

    model_files = {
        "YOLOv8":       "best.pt",
        "Faster R-CNN": "faster_rcnn_kopi_best.pth",
        "SSD":          "ssd_kopi_best.pth",
    }
    for mname, fname in model_files.items():
        path   = os.path.join(MODEL_DIR, fname)
        exists = os.path.exists(path)
        dot    = "🟢" if exists else "🔴"
        color  = "#9e9080" if exists else "#f87171"
        label  = "Siap" if exists else "Tidak ditemukan"
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;
                    align-items:center;font-size:0.78rem;margin-bottom:0.3rem'>
          <span>{dot} {mname}</span>
          <span style='color:{color};font-family:DM Mono,monospace;
                        font-size:0.7rem'>{label}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin-top:0.8rem;font-size:0.72rem;color:#9e9080;
                font-family:DM Mono,monospace;text-align:center'>
      Taruh model di folder:<br>
      <code style='color:#c9a84c'>models/</code>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">☕ Coffee Quality Control</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Sistem Deteksi Cacat Biji Kopi · 4 Kelas · 3 Model Deep Learning</div>',
    unsafe_allow_html=True
)

# ── Upload ──
uploaded = st.file_uploader(
    "📁 Upload gambar biji kopi (JPG, PNG, WEBP)",
    type=["jpg", "jpeg", "png", "webp"]
)

st.markdown("---")

if not uploaded:
    st.markdown("""
    <div style='background:#1a1713;border:2px dashed #2e2920;border-radius:14px;
                padding:4rem 2rem;text-align:center;margin-top:0.5rem'>
      <div style='font-size:4rem;margin-bottom:1rem;opacity:0.25'>☕</div>
      <div style='color:#9e9080;font-size:0.9rem'>
        Upload gambar biji kopi untuk memulai deteksi
      </div>
      <div style='color:#8a6f2e;font-size:0.78rem;margin-top:0.4rem'>
        Mendukung JPG · PNG · WEBP
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    image_pil = Image.open(uploaded).convert("RGB")

    col_orig, col_result = st.columns(2, gap="large")

    with col_orig:
        st.markdown("**📷 Gambar Asli**")
        st.image(image_pil, use_container_width=True)
        run_btn = st.button(f"🔍  Deteksi dengan {model_choice}")

    result_placeholder = col_result.empty()
    with result_placeholder.container():
        st.markdown("**🎯 Hasil Deteksi**")
        st.markdown("""
        <div style='background:#1a1713;border:1px solid #2e2920;border-radius:10px;
                    min-height:280px;display:flex;align-items:center;
                    justify-content:center;color:#9e9080;font-size:0.85rem'>
          Tekan tombol Deteksi →
        </div>""", unsafe_allow_html=True)

    stats_placeholder = st.empty()
    table_placeholder = st.empty()

    if run_btn:
        with st.spinner(f"Menjalankan {model_choice}… Harap tunggu"):
            detections, err = run_inference(model_choice, image_pil, conf_threshold)

        if err:
            st.markdown(f"<div class='warn-box'>⚠️ {err}</div>", unsafe_allow_html=True)
        else:
            # ── Gambar hasil ──
            result_img = draw_boxes(image_pil, detections)
            with result_placeholder.container():
                st.markdown("**🎯 Hasil Deteksi**")
                st.image(result_img, use_container_width=True)
                buf = io.BytesIO()
                result_img.save(buf, format="JPEG", quality=92)
                st.download_button(
                    "⬇️ Download Hasil Deteksi",
                    data=buf.getvalue(),
                    file_name=f"coffee_qc_{model_choice.lower().replace(' ','_')}.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )

            counts = count_classes(detections)
            total  = len(detections)

            # ── Stat Cards ──
            stats_placeholder.markdown(f"""
            <div class="stat-grid">
              <div class="stat-card stat-total">
                <div class="stat-count">{total}</div>
                <div class="stat-label">Total</div>
              </div>
              <div class="stat-card stat-normal">
                <div class="stat-count">{counts['normal']}</div>
                <div class="stat-label">Normal</div>
              </div>
              <div class="stat-card stat-broken">
                <div class="stat-count">{counts['broken']}</div>
                <div class="stat-label">Broken</div>
              </div>
              <div class="stat-card stat-scorching">
                <div class="stat-count">{counts['scorching']}</div>
                <div class="stat-label">Scorching</div>
              </div>
              <div class="stat-card stat-underdevelop">
                <div class="stat-count">{counts['underdevelop']}</div>
                <div class="stat-label">Underdevelop</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Tabel Deteksi ──
            with table_placeholder.container():
                st.markdown("---")
                st.markdown(
                    f"**📋 Detail Deteksi** — `{model_choice}` · **{total}** objek terdeteksi"
                )

                if total == 0:
                    st.markdown("""
                    <div style='text-align:center;padding:2.5rem;
                                color:#9e9080;font-size:0.85rem;
                                background:#1a1713;border:1px solid #2e2920;
                                border-radius:10px'>
                      Tidak ada objek terdeteksi.<br>
                      Coba turunkan <b style='color:#c9a84c'>Confidence Threshold</b> di sidebar.
                    </div>""", unsafe_allow_html=True)
                else:
                    bar_colors = {
                        'normal':       '#22c55e',
                        'broken':       '#ef4444',
                        'scorching':    '#f97316',
                        'underdevelop': '#a855f7',
                    }
                    rows = ""
                    for i, det in enumerate(detections):
                        cls   = det['class']
                        pct   = int(det['confidence'] * 100)
                        bbox  = det['bbox']
                        bc    = bar_colors.get(cls, '#c9a84c')
                        rows += f"""
                        <tr>
                          <td style='color:#9e9080'>{i+1}</td>
                          <td><span class="tag tag-{cls}">{cls}</span></td>
                          <td>
                            <div style='display:flex;align-items:center;gap:0.6rem'>
                              <div style='width:80px;height:4px;background:#2e2920;
                                          border-radius:2px;overflow:hidden'>
                                <div style='width:{pct}%;height:100%;
                                            background:{bc};border-radius:2px'></div>
                              </div>
                              <span class='mono'>{pct}%</span>
                            </div>
                          </td>
                          <td class='mono'>[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]</td>
                        </tr>"""

                    st.markdown(f"""
                    <table class="det-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Kelas</th>
                          <th>Confidence</th>
                          <th>Bounding Box (x1,y1,x2,y2)</th>
                        </tr>
                      </thead>
                      <tbody>{rows}</tbody>
                    </table>
                    """, unsafe_allow_html=True)
