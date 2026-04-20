# ☕ Coffee QC — Deteksi Cacat Biji Kopi

Web app deteksi defek biji kopi menggunakan 3 model deep learning:
- **YOLOv8** (`best.pt`)
- **Faster R-CNN** (`faster_rcnn_kopi_best.pth`)
- **SSD** (`ssd_kopi_best.pth`)

4 kelas deteksi: `normal`, `broken`, `scorching`, `underdevelop`

---

## 📁 Struktur Folder

```
coffee-detector/
├── app.py                          ← Backend Flask
├── requirements.txt
├── static/
│   └── index.html                  ← Frontend web
└── models/
    ├── best.pt                     ← Salin model Anda ke sini
    ├── faster_rcnn_kopi_best.pth
    └── ssd_kopi_best.pth
```

---

## 🚀 Cara Menjalankan

### 1. Salin model ke folder `models/`
```bash
cp /path/to/best.pt models/
cp /path/to/faster_rcnn_kopi_best.pth models/
cp /path/to/ssd_kopi_best.pth models/
```

### 2. Buat virtual environment (disarankan)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **GPU (opsional):** Jika ingin menggunakan GPU NVIDIA, install PyTorch versi CUDA:
> ```
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
> ```

### 4. Jalankan server
```bash
python app.py
```

### 5. Buka browser
```
http://localhost:5000
```

---

## 🎯 Fitur

- Upload gambar biji kopi (JPG/PNG/WEBP)
- Pilih model: YOLOv8, Faster R-CNN, atau SSD
- Atur confidence threshold (slider)
- Tampil hasil deteksi dengan bounding box berwarna
- **Hitungan per kelas** (Normal / Broken / Scorching / Underdevelop)
- Tabel detail: kelas, confidence, koordinat bbox

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: ultralytics` | `pip install ultralytics` |
| Model tidak ter-load | Periksa nama file di folder `models/` |
| Error state_dict | Edit `app.py` bagian checkpoint loading sesuai format `.pth` Anda |
| Port 5000 sudah dipakai | Ganti `port=5000` di `app.py` menjadi `port=8080` |

---

## ⚠️ Catatan Format Model `.pth`

Jika model `.pth` Anda disimpan dengan format berbeda, edit bagian ini di `app.py`:

```python
# Opsi 1: state_dict langsung
model.load_state_dict(checkpoint)

# Opsi 2: dict dengan key 'model_state_dict'
model.load_state_dict(checkpoint['model_state_dict'])

# Opsi 3: dict dengan key 'state_dict'
model.load_state_dict(checkpoint['state_dict'])
```
