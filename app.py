import streamlit as st
import os
import re
import json
import random
from collections import Counter
from datetime import datetime


# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia - Pengembangan",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# KONFIGURASI DATABASE BARU
# =========================================================

FOLDER_DATABASE = "database_pengembangan"

FILE_ABSENSI = os.path.join(
    FOLDER_DATABASE,
    "absensi.json"
)

FILE_BOOKMARK = os.path.join(
    FOLDER_DATABASE,
    "bookmark.json"
)

FILE_NILAI = os.path.join(
    FOLDER_DATABASE,
    "nilai.json"
)


# =========================================================
# MEMBUAT FOLDER DATABASE
# =========================================================

if not os.path.exists(FOLDER_DATABASE):
    os.makedirs(FOLDER_DATABASE)


# =========================================================
# FUNGSI MEMBACA FILE TXT
# =========================================================

def baca_database():

    data = []

    for nama_file in os.listdir(FOLDER_DATABASE):

        if nama_file.lower().endswith(".txt"):

            lokasi = os.path.join(
                FOLDER_DATABASE,
                nama_file
            )

            try:

                with open(
                    lokasi,
                    "r",
                    encoding="utf-8"
                ) as file:

                    isi = file.read()

                data.append({
                    "nama_file": nama_file,
                    "isi": isi
                })

            except Exception as error:

                st.error(
                    f"Gagal membaca {nama_file}: {error}"
                )

    return data


# =========================================================
# FUNGSI JSON
# =========================================================

def baca_json(lokasi, default):

    if not os.path.exists(lokasi):
        return default

    try:

        with open(
            lokasi,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return default


def simpan_json(lokasi, data):

    with open(
        lokasi,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# MEMBERSIHKAN TEKS
# =========================================================

def bersihkan_teks(teks):

    teks = teks.lower()

    teks = re.sub(
        r"[^a-zA-ZÀ-ÿ0-9\s]",
        " ",
        teks
    )

    teks = re.sub(
        r"\s+",
        " ",
        teks
    )

    return teks.strip()


# =========================================================
# STOPWORDS
# =========================================================

STOPWORDS = {
    "yang",
    "dan",
    "di",
    "ke",
    "dari",
    "pada",
    "dengan",
    "untuk",
    "dalam",
    "adalah",
    "itu",
    "ini",
    "atau",
    "apa",
    "bagaimana",
    "mengapa",
    "sebutkan",
    "jelaskan",
    "tentang",
    "suatu",
    "sebuah",
    "secara",
    "merupakan",
    "dapat",
    "akan",
    "sebagai",
    "oleh",
    "lebih",
    "juga",
    "tidak",
    "tersebut"
}


# =========================================================
# KATA KUNCI
# =========================================================

def ambil_kata_kunci(pertanyaan):

    teks = bersihkan_teks(
        pertanyaan
    )

    kata = teks.split()

    return [
        item
        for item in kata
        if len(item) > 2
        and item not in STOPWORDS
    ]


# =========================================================
# HITUNG RELEVANSI
# =========================================================

def hitung_relevansi(
    pertanyaan,
    isi
):

    kata_kunci = ambil_kata_kunci(
        pertanyaan
    )

    if not kata_kunci:
        return 0

    teks_database = bersihkan_teks(
        isi
    )

    frekuensi = Counter(
        teks_database.split()
    )

    skor = 0

    for kata in kata_kunci:

        if kata in frekuensi:

            jumlah = frekuensi[kata]

            if jumlah > 10:
                jumlah = 10

            skor += jumlah

    pertanyaan_bersih = bersihkan_teks(
        pertanyaan
    )

    if pertanyaan_bersih in teks_database:
        skor += 20

    return skor


# =========================================================
# PENCARIAN MATERI
# =========================================================

def cari_materi(
    pertanyaan,
    database
):

    hasil = []

    for data in database:

        skor = hitung_relevansi(
            pertanyaan,
            data["isi"]
        )

        if skor > 0:

            hasil.append({
                "nama_file": data["nama_file"],
                "isi": data["isi"],
                "skor": skor
            })

    hasil.sort(
        key=lambda x: x["skor"],
        reverse=True
    )

    return hasil


# =========================================================
# POTONGAN MATERI
# =========================================================

def ambil_potongan_relevan(
    pertanyaan,
    isi,
    maksimal=1800
):

    kata_kunci = ambil_kata_kunci(
        pertanyaan
    )

    paragraf = re.split(
        r"\n\s*\n|\r\n",
        isi
    )

    hasil = []

    for p in paragraf:

        teks = bersihkan_teks(p)

        skor = sum(
            1
            for kata in kata_kunci
            if kata in teks
        )

        if skor > 0:

            hasil.append(
                (skor, p.strip())
            )

    hasil.sort(
        key=lambda x: x[0],
        reverse=True
    )

    jawaban = ""

    for skor, paragraf in hasil:

        if len(jawaban) + len(paragraf) <= maksimal:

            jawaban += (
                paragraf +
                "\n\n"
            )

    if not jawaban:

        jawaban = isi[:maksimal]

    return jawaban.strip()


# =========================================================
# INISIALISASI SESSION STATE
# =========================================================

if "nama_siswa" not in st.session_state:

    st.session_state.nama_siswa = ""


if "bookmark" not in st.session_state:

    st.session_state.bookmark = baca_json(
        FILE_BOOKMARK,
        []
    )


if "nilai" not in st.session_state:

    st.session_state.nilai = baca_json(
        FILE_NILAI,
        []
    )


if "absensi" not in st.session_state:

    st.session_state.absensi = baca_json(
        FILE_ABSENSI,
        []
    )


# =========================================================
# LOAD DATABASE
# =========================================================

database = baca_database()


# =========================================================
# HEADER
# =========================================================

st.title(
    "📚 AI Tutor Bahasa Indonesia"
)

st.subheader(
    "🚀 Versi Pengembangan"
)

st.write(
    "Platform pembelajaran Bahasa Indonesia "
    "dengan materi, tanya jawab, kuis, "
    "absensi, bookmark, dan evaluasi."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("👤 Identitas Siswa")

    nama = st.text_input(
        "Nama siswa",
        value=st.session_state.nama_siswa,
        placeholder="Masukkan nama Anda"
    )

    st.session_state.nama_siswa = nama

    st.divider()

    st.header("📂 Database")

    st.code(
        "database_pengembangan/"
    )

    st.write(
        f"Jumlah materi: **{len(database)}**"
    )

    st.write(
        f"Bookmark: **{len(st.session_state.bookmark)}**"
    )

    st.write(
        f"Riwayat nilai: **{len(st.session_state.nilai)}**"
    )


# =========================================================
# MENU UTAMA
# =========================================================

menu = st.tabs([
    "🏠 Beranda",
    "📖 Materi",
    "💬 Tanya Jawab",
    "📝 Kuis",
    "📅 Absensi",
    "🔖 Bookmark",
    "📊 Nilai"
])


# =========================================================
# TAB BERANDA
# =========================================================

with menu[0]:

    st.header(
        "👋 Selamat Datang di AI Tutor"
    )

    if st.session_state.nama_siswa:

        st.success(
            f"Halo, {st.session_state.nama_siswa}! "
            "Selamat belajar."
        )

    else:

        st.info(
            "Silakan masukkan nama Anda "
            "di bagian sidebar."
        )

    st.markdown("""
    ### 🎯 Fitur Pembelajaran

    **📖 Materi**
    
    Membaca materi Bahasa Indonesia
    yang tersedia dalam database.

    **💬 Tanya Jawab**
    
    Ajukan pertanyaan dan sistem akan
    mencari materi yang paling relevan.

    **📝 Kuis**
    
    Kerjakan soal dan lihat nilai Anda.

    **📅 Absensi**
    
    Catat kehadiran setiap kali belajar.

    **🔖 Bookmark**
    
    Simpan materi penting untuk dibaca kembali.

    **📊 Nilai**
    
    Lihat perkembangan hasil kuis.
    """)


# =========================================================
# TAB MATERI
# =========================================================

with menu[1]:

    st.header("📖 Materi Pembelajaran")

    if len(database) == 0:

        st.warning(
            "Belum ada materi dalam "
            "database_pengembangan."
        )

        st.info(
            "Tambahkan file TXT ke folder "
            "database_pengembangan."
        )

    else:

        pilihan = st.selectbox(
            "Pilih materi:",
            [
                data["nama_file"]
                for data in database
            ]
        )

        materi = next(
            data
            for data in database
            if data["nama_file"] == pilihan
        )

        st.subheader(
            pilihan.replace(
                ".txt",
                ""
            ).replace(
                "_",
                " "
            ).title()
        )

        st.write(
            materi["isi"]
        )

        st.divider()

        if st.button(
            "🔖 Simpan ke Bookmark",
            key="bookmark_materi"
        ):

            if pilihan not in st.session_state.bookmark:

                st.session_state.bookmark.append(
                    pilihan
                )

                simpan_json(
                    FILE_BOOKMARK,
                    st.session_state.bookmark
                )

                st.success(
                    "Materi berhasil disimpan."
                )

            else:

                st.info(
                    "Materi sudah ada di bookmark."
                )


# =========================================================
# TAB TANYA JAWAB
# =========================================================

with menu[2]:

    st.header("💬 Tanya Jawab")

    pertanyaan = st.text_area(
        "Apa yang ingin Anda tanyakan?",
        placeholder=(
            "Contoh: Apa yang dimaksud "
            "dengan teks rekon?"
        ),
        height=120
    )

    if st.button(
        "🔍 Cari Jawaban",
        key="tanya"
    ):

        if not pertanyaan.strip():

            st.warning(
                "Masukkan pertanyaan terlebih dahulu."
            )

        elif not database:

            st.error(
                "Database materi masih kosong."
            )

        else:

            hasil = cari_materi(
                pertanyaan,
                database
            )

            if hasil:

                utama = hasil[0]

                st.success(
                    "Materi yang relevan ditemukan."
                )

                st.subheader(
                    "💡 Jawaban"
                )

                jawaban = ambil_potongan_relevan(
                    pertanyaan,
                    utama["isi"]
                )

                st.info(jawaban)

                st.caption(
                    f"Sumber: {utama['nama_file']}"
                )

                if len(hasil) > 1:

                    st.subheader(
                        "📚 Materi Terkait"
                    )

                    for item in hasil[1:4]:

                        with st.expander(
                            item["nama_file"]
                        ):

                            st.write(
                                ambil_potongan_relevan(
                                    pertanyaan,
                                    item["isi"],
                                    800
                                )
                            )

            else:

                st.warning(
                    "Materi belum ditemukan."
                )


# =========================================================
# TAB KUIS
# =========================================================

with menu[3]:

    st.header("📝 Kuis Bahasa Indonesia")

    soal = [
        {
            "soal":
                "Apa tujuan utama teks rekon?",
            "pilihan": [
                "Menceritakan kembali suatu peristiwa",
                "Membuat sebuah iklan",
                "Menjelaskan cara memasak",
                "Menggambarkan sebuah benda"
            ],
            "jawaban":
                "Menceritakan kembali suatu peristiwa"
        },

        {
            "soal":
                "Bagian teks rekon yang berisi urutan kejadian disebut...",
            "pilihan": [
                "Orientasi",
                "Rangkaian peristiwa",
                "Judul",
                "Penutup"
            ],
            "jawaban":
                "Rangkaian peristiwa"
        },

        {
            "soal":
                "Teks rekon biasanya menceritakan...",
            "pilihan": [
                "Peristiwa yang telah terjadi",
                "Rencana masa depan",
                "Cara membuat sesuatu",
                "Pendapat seseorang"
            ],
            "jawaban":
                "Peristiwa yang telah terjadi"
        },

        {
            "soal":
                "Salah satu ciri teks rekon adalah...",
            "pilihan": [
                "Memuat urutan waktu",
                "Tidak memiliki peristiwa",
                "Selalu berupa dialog",
                "Tidak menggunakan kata kerja"
            ],
            "jawaban":
                "Memuat urutan waktu"
        },

        {
            "soal":
                "Kata seperti 'kemudian' dan 'setelah itu' menunjukkan...",
            "pilihan": [
                "Urutan waktu",
                "Tempat",
                "Tokoh",
                "Pendapat"
            ],
            "jawaban":
                "Urutan waktu"
        }
    ]

    st.write(
        "Kerjakan soal berikut."
    )

    jawaban_siswa = []

    for i, item in enumerate(soal):

        st.write(
            f"**{i + 1}. {item['soal']}**"
        )

        jawaban = st.radio(
            "Pilih jawaban:",
            item["pilihan"],
            key=f"soal_{i}"
        )

        jawaban_siswa.append(
            jawaban
        )

    if st.button(
        "✅ Selesai dan Nilai",
        key="nilai_kuis"
    ):

        benar = 0

        for i, item in enumerate(soal):

            if jawaban_siswa[i] == item["jawaban"]:

                benar += 1

        nilai = int(
            (benar / len(soal)) * 100
        )

        nama_siswa = (
            st.session_state.nama_siswa
            if st.session_state.nama_siswa
            else "Siswa"
        )

        data_nilai = {
            "nama": nama_siswa,
            "nilai": nilai,
            "benar": benar,
            "jumlah_soal": len(soal),
            "tanggal": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        }

        st.session_state.nilai.append(
            data_nilai
        )

        simpan_json(
            FILE_NILAI,
            st.session_state.nilai
        )

        st.divider()

        if nilai >= 80:

            st.success(
                f"🎉 Nilai Anda: {nilai}"
            )

        elif nilai >= 60:

            st.warning(
                f"👍 Nilai Anda: {nilai}. "
                "Terus berlatih!"
            )

        else:

            st.info(
                f"📚 Nilai Anda: {nilai}. "
                "Yuk pelajari kembali materinya."
            )

        st.write(
            f"Jawaban benar: "
            f"**{benar}/{len(soal)}**"
        )


# =========================================================
# TAB ABSENSI
# =========================================================

with menu[4]:

    st.header("📅 Absensi Belajar")

    nama_absen = st.text_input(
        "Nama siswa untuk absensi:",
        value=st.session_state.nama_siswa,
        key="nama_absen"
    )

    status = st.selectbox(
        "Status kehadiran:",
        [
            "Hadir",
            "Izin",
            "Tidak Hadir"
        ]
    )

    if st.button(
        "📌 Simpan Absensi"
    ):

        if not nama_absen.strip():

            st.warning(
                "Masukkan nama siswa."
            )

        else:

            data_absen = {
                "nama": nama_absen,
                "status": status,
                "tanggal": datetime.now().strftime(
                    "%d-%m-%Y"
                ),
                "waktu": datetime.now().strftime(
                    "%H:%M"
                )
            }

            st.session_state.absensi.append(
                data_absen
            )

            simpan_json(
                FILE_ABSENSI,
                st.session_state.absensi
            )

            st.success(
                "Absensi berhasil disimpan."
            )

    st.divider()

    st.subheader(
        "📋 Riwayat Absensi"
    )

    if st.session_state.absensi:

        st.dataframe(
            st.session_state.absensi,
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada data absensi."
        )


# =========================================================
# TAB BOOKMARK
# =========================================================

with menu[5]:

    st.header("🔖 Materi Bookmark")

    if not st.session_state.bookmark:

        st.info(
            "Belum ada materi yang disimpan."
        )

    else:

        for nama_file in (
            st.session_state.bookmark
        ):

            st.markdown(
                f"### 📖 {nama_file}"
            )

            materi = next(
                (
                    data
                    for data in database
                    if data["nama_file"] == nama_file
                ),
                None
            )

            if materi:

                with st.expander(
                    "Buka materi"
                ):

                    st.write(
                        materi["isi"]
                    )

            else:

                st.warning(
                    "Materi sudah tidak ditemukan."
                )


# =========================================================
# TAB NILAI
# =========================================================

with menu[6]:

    st.header("📊 Perkembangan Nilai")

    if not st.session_state.nilai:

        st.info(
            "Belum ada hasil kuis."
        )

    else:

        st.dataframe(
            st.session_state.nilai,
            use_container_width=True
        )

        nilai_list = [
            item["nilai"]
            for item in st.session_state.nilai
        ]

        rata_rata = sum(
            nilai_list
        ) / len(nilai_list)

        nilai_tertinggi = max(
            nilai_list
        )

        st.metric(
            "📈 Rata-rata Nilai",
            f"{rata_rata:.1f}"
        )

        st.metric(
            "🏆 Nilai Tertinggi",
            nilai_tertinggi
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Tutor Bahasa Indonesia "
    "| Versi Pengembangan "
    "| Python + Streamlit + TXT Knowledge Base"
)