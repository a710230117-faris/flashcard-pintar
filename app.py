import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from gtts import gTTS
import io
import random

# =========================
# Load model YOLO
# =========================
model = YOLO("yolov8n.pt")

# =========================
# Mapping nama objek
# =========================
nama_indo = {
    "apple": "apel", "banana": "pisang", "orange": "jeruk",
    "cat": "kucing", "dog": "anjing", "bird": "burung",
    "ball": "bola", "book": "buku", "bottle": "botol",
    "cup": "gelas", "person": "orang", "car": "mobil"
}

# =========================
# Teks ekspresif
# =========================
ekspresi = {
    "apel": ["Ini apel merah yang manis!", "Apel sehat bikin kuat!"],
    "pisang": ["Pisang lucu melengkung!", "Pisang enak dan mengenyangkan!"],
    "jeruk": ["Jeruk segar dan cerah!", "Jeruk vitamin C!"],
    "kucing": ["Meow! Kucing imut!", "Kucing suka tidur!"],
    "anjing": ["Woof! Anjing setia!", "Anjing senang bermain!"],
    "bola": ["Bola bulat seru!", "Ayo main bola!"],
    "mobil": ["Brum brum! Mobil jalan!", "Mobil cepat!"],
    "buku": ["Buku pintar!", "Ayo baca buku!"],
    "orang": ["Hello! Orang cerdas!", "Haii!! Orang pintar!"]
}

# =========================
# CSS Ramah Anak
# =========================
st.markdown("""
<style>
/* Warna background */
body {
    background-color: #FFF8DC;
}

/* Judul besar & cerah */
h1, h2, h3 {
    color: #FF4500;
    font-family: 'Comic Sans MS', cursive;
}

/* Card gambar */
.card {
    border: 5px solid #FFD700;
    border-radius: 20px;
    padding: 10px;
    background-color: #FFFACD;
    text-align: center;
    margin-bottom: 15px;
}

/* Tombol besar */
.stButton > button {
    font-size: 24px;
    padding: 10px 20px;
    border-radius: 15px;
    background-color: #00BFFF;
    color: white;
    font-weight: bold;
}

.stRadio > div {
    font-size: 24px;
    color: #FF69B4;
}
</style>
""", unsafe_allow_html=True)

# =========================
# UI Header
# =========================
st.title("🎨 Flashcard Pintar 👶📸")
st.markdown("Belajar mengenal benda dengan **kamera**, **gambar**, atau **tebak gambar**")

# =========================
# Sidebar Mode
# =========================
mode = st.sidebar.radio(
    "Pilih Mode",
    ["📸 Kamera Real-time", "🖼️ Flashcard Statis", "🧠 Tebak Gambar"]
)

# =========================
# MODE KAMERA
# =========================
if mode == "📸 Kamera Real-time":
    st.info("Arahkan kamera ke benda nyata")
    frame_box = st.image([])

    # Inisialisasi state kamera
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = True

    # Tombol toggle
    if st.sidebar.button("⏯️ Stop / Mulai Kamera"):
        st.session_state.camera_running = not st.session_state.camera_running
        if st.session_state.camera_running:
            st.success("Kamera dinyalakan ✅")
        else:
            st.warning("Kamera dimatikan ⛔")

    spoken = set()

    if st.session_state.camera_running:
        camera = cv2.VideoCapture(0)

        while camera.isOpened() and st.session_state.camera_running:
            ret, frame = camera.read()
            if not ret:
                st.error("Tidak dapat mengakses kamera")
                break

            results = model(frame)[0]

            for box in results.boxes.data.tolist():
                x1, y1, x2, y2, conf, cls = box
                if conf > 0.5:
                    label = results.names[int(cls)].lower()
                    if label in nama_indo:
                        nama = nama_indo[label]

                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)),
                                      (255, 0, 255), 4)
                        cv2.putText(frame, nama.upper(),
                                    (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                                    (255, 0, 255), 3)

                        if nama not in spoken:
                            teks = random.choice(ekspresi.get(nama, [f"Ini {nama}"]))
                            tts = gTTS(teks, lang="id")
                            audio = io.BytesIO()
                            tts.write_to_fp(audio)
                            audio.seek(0)
                            st.audio(audio, autoplay=True)
                            spoken.add(nama)

            frame_box.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        camera.release()
    else:
        st.info("Kamera tidak aktif. Tekan tombol ⏯️ Stop / Mulai Kamera untuk menyalakan kembali.")

# =========================
# MODE FLASHCARD STATIS
# =========================
elif mode == "🖼️ Flashcard Statis":
    st.info("Upload gambar flashcard")
    uploaded = st.file_uploader("Upload Gambar Flashcard", type=["jpg","jpeg","png"], key="flashcard")
    if uploaded:
        image = Image.open(uploaded)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(image)
        st.markdown('</div>', unsafe_allow_html=True)

        img_array = np.array(image)
        results = model(img_array)[0]
        detected = False
        for box in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = box
            if conf > 0.5:
                label = results.names[int(cls)].lower()
                if label in nama_indo:
                    detected = True
                    nama = nama_indo[label]
                    teks = random.choice(ekspresi.get(nama, [f"Ini {nama}"]))
                    st.success(f"🧠 Terdeteksi: {nama.upper()}")
                    tts = gTTS(teks, lang="id")
                    audio = io.BytesIO()
                    tts.write_to_fp(audio)
                    audio.seek(0)
                    st.audio(audio, autoplay=True)
        if not detected:
            st.warning("Tidak ada objek yang dikenali 😢")

# =========================
# MODE TEBAK GAMBAR
# =========================
elif mode == "🧠 Tebak Gambar":
    st.subheader("🧠 Tebak Gambar")
    st.info("Lihat gambarnya, lalu tebak nama bendanya ya 😊")

    uploaded = st.file_uploader(
        "Upload Gambar Tebakan",
        type=["jpg", "jpeg", "png"],
        key="tebak"
    )

    if uploaded:
        image = Image.open(uploaded)
        img_array = np.array(image)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(image, caption="Gambar Tebakan")
        st.markdown('</div>', unsafe_allow_html=True)

        results = model(img_array)[0]
        objek = None

        # Ambil 1 objek utama
        for box in results.boxes.data.tolist():
            conf = box[4]
            cls = int(box[5])
            if conf > 0.5:
                label = results.names[cls].lower()
                if label in nama_indo:
                    objek = nama_indo[label]
                    break

        if objek:
            st.markdown("### 🤔 Ini gambar apa ya?")

            # Buat key unik per gambar untuk session_state
            key_opsi = f"opsi_{uploaded.name}"

            # Simpan opsi di session_state agar tidak berubah
            if key_opsi not in st.session_state:
                pilihan = list(nama_indo.values())
                opsi = random.sample(pilihan, 3)
                if objek not in opsi:
                    opsi[random.randint(0, 2)] = objek
                random.shuffle(opsi)
                st.session_state[key_opsi] = opsi

            opsi = st.session_state[key_opsi]

            jawaban = st.radio("Pilih jawaban:", opsi, key=f"radio_{uploaded.name}")

            if st.button("✅ Jawab", key=f"btn_{uploaded.name}"):
                if jawaban == objek:
                    st.success("🎉 BENAR! Pintar sekali!")
                    teks = f"Hebat! Ini adalah {objek}. Kamu pintar sekali!"
                else:
                    st.error("❌ Belum tepat, coba lagi ya!")
                    teks = f"Belum tepat. Ini adalah {objek}. Yuk belajar lagi!"

                tts = gTTS(teks, lang="id")
                audio = io.BytesIO()
                tts.write_to_fp(audio)
                audio.seek(0)
                st.audio(audio, autoplay=True)

        else:
            st.warning("Objek belum dikenali, coba gambar lain ya 😊")