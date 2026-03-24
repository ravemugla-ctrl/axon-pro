import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime

# --- 1. AYARLAR VE VERİTABANI BAĞLANTISI ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"
DB_URL = os.environ.get("DATABASE_URL")

# SQLAlchemy motorunu kur (Render'da 'postgres://' kısmını 'postgresql://' olarak düzeltmemiz gerekebilir)
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URL) if DB_URL else None

st.set_page_config(page_title="AXON PRO | Vault v5", layout="wide")

# --- VERİTABANI TABLO OLUŞTURMA ---
def init_db():
    if engine:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_vault (
                    id SERIAL PRIMARY KEY,
                    category TEXT,
                    record_count INTEGER,
                    valuation FLOAT,
                    upload_time TIMESTAMP,
                    raw_preview TEXT
                )
            """))
            conn.commit()

# --- VERİYİ KASAYA KAYDETME ---
def save_to_vault(cat, count, val, preview):
    if engine:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO data_vault (category, record_count, valuation, upload_time, raw_preview)
                VALUES (:cat, :count, :val, :time, :preview)
            """), {"cat": cat, "count": count, "val": val, "time": datetime.now(), "preview": str(preview)})
            conn.commit()

# --- İSTATİSTİKLERİ ÇEKME ---
def get_vault_stats():
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT COUNT(*), SUM(record_count) FROM data_vault")).fetchone()
                return res[0] or 0, res[1] or 0
        except:
            return 0, 0
    return 0, 0

# Başlat
init_db()

# --- 2. ANA PANEL ---
st.title("🛡️ AXON PRO - Enterprise Data Vault v5")
st.markdown("---")

total_files, total_rows = get_vault_stats()
m1, m2, m3 = st.columns(3)
m1.metric("Toplam Arşivlenen Dosya", total_files)
m2.metric("Toplam Havuz Hacmi (Satır)", f"{total_rows:,}")
m3.metric("Kasa Durumu", "🔐 SQL Secure")

# --- 3. YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Operasyon Merkezi")
    target_company = st.selectbox("🎯 Alıcı Kurum:", ["OpenAI", "Google", "Meta AI", "Anthropic", "Tesla AI"])
    data_category = st.selectbox("📊 Veri Tipi:", ["Tüketici Davranışı", "Finansal Trendler", "Lojistik/Konum", "Sağlık"])
    neg_style = st.radio("🤝 Tarz:", ["Agresif", "Dengeli", "Hızlı Satış"])
    st.divider()
    st.success("✅ Veritabanı Bağlantısı Aktif")

# --- 4. VERİ YÜKLEME ---
uploaded_file = st.file_uploader("📂 Yeni Veriyi Kasaya Kilitleyin", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        record_count = len(df)
        u_price = 0.22 if neg_style == "Agresif" else 0.15
        total_val = record_count * u_price
        
        if st.button("📥 Analiz Et ve Veritabanına Yaz"):
            # Veritabanına Kaydet
            save_to_vault(data_category, record_count, total_val, df.columns.tolist())
            st.balloons()
            st.success("✨ Veri başarıyla PostgreSQL Çelik Kasasına kilitlendi!")
            
            # Ajan Müzakeresi
            tabs = st.tabs(["💰 Satış", "⚖️ Hukuk", "📈 Analiz"])
            def call_groq(p):
                h = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=h, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": p}]})
                return res.json()['choices'][0]['message']['content']

            with st.status("Ajanlar müzakere ediyor..."):
                s_txt = call_groq(f"{target_company} için {record_count} satır veriyi {total_val}$ fiyata satacak teklif yaz.")
                tabs[0].write(s_txt)
                tabs[1].write("Hukuki taslak hazırlandı (Database Logged).")
                tabs[2].write(f"Pazar analizi: {data_category} verisi için {target_company} masasında güçlü bir pozisyon alındı.")

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")

st.caption("AXON v5.0 | SQL Protected | Location: Göcek / Muğla")
