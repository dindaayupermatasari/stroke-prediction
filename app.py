import streamlit as st
import numpy as np
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# ⚠️ HARUS PALING ATAS — TANPA APAPUN SEBELUM INI
# ==================================================
st.set_page_config(
    page_title="Dashboard Prediksi Penyakit Stroke",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# BARU BOLEH STREAMLIT COMMAND LAIN
# ==================================================
@st.cache_resource
def load_model():
    return joblib.load("models/stroke_model.pkl")


model = load_model()

# Header
st.title("Aplikasi Prediksi Risiko Stroke")

# Sidebar for menu
st.sidebar.header("Menu")
menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "Home",
        "Prediksi Risiko Stroke",
        "History Data Pasien",
        "Statistik Penyakit Stroke",
    ],
)

# Halaman Home
if menu == "Home":
    st.subheader("Selamat Datang di Aplikasi Prediksi Risiko Stroke")
    st.markdown(
        """
        Aplikasi ini dirancang untuk membantu Anda memahami risiko stroke berdasarkan data kesehatan Anda. 
        Dengan menggunakan model prediksi, aplikasi ini dapat memberikan wawasan tentang kemungkinan risiko stroke 
        yang mungkin Anda hadapi.
        """
    )
    st.image("images/stroke_image.jpg", use_column_width=True)


# Dummy Data for Patient History
if "history_data" not in st.session_state:
    st.session_state.history_data = pd.DataFrame(
        columns=[
            "Nama",
            "Tanggal Pemeriksaan",
            "Umur",
            "Jenis Kelamin",
            "Hipertensi",
            "Penyakit Jantung",
            "BMI",
            "Glukosa Darah",
            "Status Merokok",
            "Hasil Prediksi",
        ]
    )


# Medical Action Recommendations
def rekomendasi_tindakan(risk):
    if risk == 1:
        return """
        1. Segera lakukan pemeriksaan lanjutan seperti CT Scan atau MRI untuk mendeteksi potensi stroke.
        2. Pemantauan tekanan darah secara rutin untuk mencegah hipertensi yang dapat memperburuk kondisi.
        3. Diet rendah garam dan lemak, serta peningkatan aktivitas fisik untuk mengurangi risiko.
        4. Pengobatan untuk menurunkan kadar glukosa darah dan kontrol kolesterol.
        5. Konsultasi dengan ahli jantung jika ada riwayat penyakit jantung.
        """
    else:
        return """
        1. Menjaga pola hidup sehat dengan pola makan yang seimbang dan olahraga teratur.
        2. Pemantauan kesehatan secara berkala untuk mencegah potensi risiko di masa depan.
        3. Pengurangan stres dan perubahan gaya hidup untuk mendukung kesehatan jangka panjang.
        """


# Patient Data Input Form
if menu == "Prediksi Risiko Stroke":
    st.subheader("Form Input Data Pasien")
    age = st.slider("Umur (tahun)", 0, 120, 35)
    gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    hypertension = st.selectbox("Riwayat Hipertensi", ["Tidak", "Ya"])
    heart_disease = st.selectbox("Riwayat Penyakit Jantung", ["Tidak", "Ya"])
    ever_married = st.selectbox("Pernah Menikah?", ["Tidak", "Ya"])
    work_type = st.selectbox(
        "Tipe Pekerjaan",
        ["Private", "Self-employed", "Government Job", "Children", "Never Worked"],
    )
    residence_type = st.selectbox("Tipe Tempat Tinggal", ["Urban", "Rural"])
    avg_glucose_level = st.slider("Rata-rata Glukosa Darah (mg/dL)", 0.0, 300.0, 120.0)
    bmi = st.slider("BMI (Body Mass Index)", 0.0, 50.0, 22.0)
    smoking_status = st.selectbox(
        "Status Merokok", ["Tidak Merokok", "Merokok", "Mantan Perokok"]
    )

    # Encode the inputs
    gender = 1 if gender == "Perempuan" else 0
    hypertension = 1 if hypertension == "Ya" else 0
    heart_disease = 1 if heart_disease == "Ya" else 0
    ever_married = 1 if ever_married == "Ya" else 0
    work_type_dict = {
        "Private": 1,
        "Self-employed": 2,
        "Government Job": 3,
        "Children": 4,
        "Never Worked": 5,
    }
    work_type = work_type_dict[work_type]
    residence_type = 1 if residence_type == "Urban" else 0
    smoking_status_dict = {
        "Tidak Merokok": 0,
        "Merokok": 1,
        "Mantan Perokok": 2,
    }
    smoking_status = smoking_status_dict[smoking_status]

    input_data = pd.DataFrame(
        [
            [
                gender,
                age,
                hypertension,
                heart_disease,
                ever_married,
                work_type,
                residence_type,
                avg_glucose_level,
                bmi,
                smoking_status,
            ]
        ],
        columns=[
            "gender",
            "age",
            "hypertension",
            "heart_disease",
            "ever_married",
            "work_type",
            "residence_type",
            "avg_glucose_level",
            "bmi",
            "smoking_status",
        ],
    )

    # Predict and recommend
    if "prediction" not in st.session_state:
        st.session_state.prediction = None

    if st.button("Prediksi Risiko Stroke"):
        st.session_state.prediction = model.predict(input_data)

        if st.session_state.prediction is not None:
            if st.session_state.prediction[0] == 1:
                st.error("Hasil: Berisiko Stroke")
                st.subheader("Rekomendasi Tindakan Medis:")
                st.markdown(rekomendasi_tindakan(1))
            else:
                st.success("Hasil: Tidak Berisiko Stroke")
                st.subheader("Rekomendasi Tindakan Medis:")
                st.markdown(rekomendasi_tindakan(0))

    if st.button("Simpan Data ke History"):
        if st.session_state.prediction is None:
            st.warning("Silakan lakukan prediksi terlebih dahulu.")
        else:
            new_data = {
                "Nama": "Pasien Baru",
                "Tanggal Pemeriksaan": pd.Timestamp.now().date(),
                "Umur": age,
                "Jenis Kelamin": "Perempuan" if gender == 1 else "Laki-laki",
                "Hipertensi": "Ya" if hypertension == 1 else "Tidak",
                "Penyakit Jantung": "Ya" if heart_disease == 1 else "Tidak",
                "BMI": bmi,
                "Glukosa Darah": avg_glucose_level,
                "Status Merokok": list(smoking_status_dict.keys())[smoking_status],
                "Hasil Prediksi": (
                    "Berisiko"
                    if st.session_state.prediction[0] == 1
                    else "Tidak Berisiko"
                ),
            }

            st.session_state.history_data = pd.concat(
                [st.session_state.history_data, pd.DataFrame([new_data])],
                ignore_index=True,
            )
            st.success("Data berhasil disimpan ke history.")


# History Data and Stroke Statistics Menu
elif menu == "History Data Pasien":
    st.subheader("History Data Pasien")
    st.dataframe(st.session_state.history_data)

    # Statistik Sederhana
    st.markdown("### Statistik Data History Pasien")
    if not st.session_state.history_data.empty:
        stat_umur = st.session_state.history_data["Umur"].mean()
        jumlah_berisiko = st.session_state.history_data[
            st.session_state.history_data["Hasil Prediksi"] == "Berisiko"
        ].shape[0]
        jumlah_tidak_berisiko = st.session_state.history_data[
            st.session_state.history_data["Hasil Prediksi"] == "Tidak Berisiko"
        ].shape[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Rata-rata Umur", f"{stat_umur:.1f} tahun")
        col2.metric("Pasien Berisiko", jumlah_berisiko)
        col3.metric("Pasien Tidak Berisiko", jumlah_tidak_berisiko)

        # Insight dari Data
        st.markdown("### Insight dari Data Pasien")
        st.markdown(
            """
            - **Pasien dengan risiko stroke**: Kebanyakan berada di kelompok usia lebih tua.
            - **BMI tinggi**: Perlu perhatian khusus untuk pasien dengan BMI di atas normal (≥25).
            - **Faktor glukosa darah dan hipertensi**: Terlihat menjadi faktor signifikan dalam prediksi risiko.
            """
        )
    else:
        st.warning("Belum ada data history pasien.")

if menu == "Statistik Penyakit Stroke":
    st.title("Statistik Kasus Stroke di Indonesia")
    st.markdown(
        """
        Berikut ini adalah statistik kasus penyakit stroke yang ada di Indonesia, dari sini Anda dapat melihat insight dari perkembangan data penyakit stroke, 
        termasuk distribusi faktor risiko, tren jumlah kasus, dan analisis korelasi antar faktor.
        """
    )

    # Data Dummy
    statistik_data = pd.DataFrame(
        {
            "Kategori": [
                "Hipertensi",
                "Merokok",
                "Kolesterol Tinggi",
                "Gaya Hidup Sedentary",
            ],
            "Persentase": [40, 25, 20, 15],
            "Jumlah Kasus": [400, 250, 200, 150],
        }
    )

    tahun_data = pd.DataFrame(
        {
            "Tahun": [2018, 2019, 2020, 2021, 2022],
            "Jumlah Kasus": [700, 800, 850, 900, 1000],
        }
    )

    korelasi_data = pd.DataFrame(
        {
            "Hipertensi": [1, 0.6, 0.4, 0.3],
            "Merokok": [0.6, 1, 0.5, 0.2],
            "Kolesterol Tinggi": [0.4, 0.5, 1, 0.4],
            "Gaya Hidup Sedentary": [0.3, 0.2, 0.4, 1],
        },
        index=["Hipertensi", "Merokok", "Kolesterol Tinggi", "Gaya Hidup Sedentary"],
    )

    # Overview Metrics
    st.markdown("### Overview Statistik")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Kasus Stroke", "1000", "50% ↑ dari tahun lalu")
    col2.metric("Rata-rata Umur", "58 tahun", "-2 tahun ↓")
    col3.metric("Hipertensi", "40%", "Stabil")
    col4.metric("Perokok Aktif", "25%", "Naik 5%")

    # Baris Visualisasi 1
    st.markdown("### Analisis Distribusi dan Jumlah Kasus")
    col_a, col_b = st.columns(2)

    with col_a:
        # Distribusi Faktor Risiko (Pie Chart)
        fig1 = px.pie(
            statistik_data,
            names="Kategori",
            values="Persentase",
            title="Distribusi Faktor Risiko",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        st.plotly_chart(fig1, use_column_width=True)

    # Bar Chart
    with col_b:
        fig2 = px.bar(
            statistik_data,
            x="Kategori",
            y="Jumlah Kasus",
            title="Jumlah Kasus Berdasarkan Faktor Risiko",
            color="Kategori",
            color_discrete_sequence=px.colors.sequential.RdBu,
        )
        st.plotly_chart(fig2, use_column_width=True)

    st.markdown("### Tren dan Korelasi Faktor Risiko")
    col_c, col_d = st.columns(2)

    # Line Chart
    with col_c:
        fig3 = px.line(
            tahun_data,
            x="Tahun",
            y="Jumlah Kasus",
            title="Tren Jumlah Kasus Per Tahun",
            markers=True,
            line_shape="linear",
            color_discrete_sequence=px.colors.sequential.RdBu[1:4],
        )
        st.plotly_chart(fig3, use_column_width=True)

    # Heatmap
    with col_d:
        fig4 = go.Figure(
            data=go.Heatmap(
                z=korelasi_data.values,
                x=korelasi_data.columns,
                y=korelasi_data.index,
                colorscale="RdBu",
                colorbar=dict(title="Korelasi"),
            )
        )
        fig4.update_layout(title="Korelasi Antar Faktor Risiko", title_x=0.5)
        st.plotly_chart(fig4, use_column_width=True)

    # Insight Section
    st.markdown("### Insight")
    st.markdown(
        """
        - **Hipertensi** memiliki korelasi tertinggi dengan faktor risiko lainnya.
        - Faktor **Merokok** juga cukup signifikan dalam meningkatkan risiko stroke.
        - Jumlah kasus stroke mengalami peningkatan setiap tahun.
        """
    )
