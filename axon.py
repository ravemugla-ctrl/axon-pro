import streamlit as st
import pandas as pd
import os
import requests
from sqlalchemy import create_engine, text
from datetime import datetime

# --- 1. AYARLAR ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"
DB_URL = os.environ.get("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DB_URL) if DB_URL else None

st.set_page_config(page_title="AXON PRO | Data Vault", layout="wide")

# URL Parametresi Kontrolü (Yönetici mi, Kullanıcı mı?)
query_params = st.query_params
is_portal = query_params.get("mode") == "portal"

# --- DB FONKSİYONLARI ---
def init_db():
    if engine:
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS data_vault (id SERIAL, category TEXT, record_count INTEGER, valuation FLOAT, upload_time TIMESTAMP, raw_preview TEXT)"))
            conn.commit()

def save_to_vault(cat, count, val):
    if engine:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO data_vault (category, record_count, valuation, upload_time) VALUES (:cat, :count, :val, :time)"),
                         {"cat": cat, "count": count, "val": val, "time": datetime.now()})
            conn.commit()

init_db()

# --- GÖRÜNÜM 1: VERİ TOPLAMA PORTALI (DIŞA AÇIK) ---
if is_portal:
    st.title("🛡️ AXON PRO - Veri Ortaklığı Portalı")
    st.subheader("Verilerinizi Anonimleştirin, Gelir Paylaşımına Katılın")
    st.info("Yüklediğiniz veriler yapay zeka pazarında değerlendirilmek üzere güvenli havuzumuza eklenir.")
    
    with st.container(border=True):
        p_cat = st.selectbox("Veri Seti Kategorisi:", ["Tüketici Harcamaları", "Turizm/Konaklama", "Lojistik", "Ticaret"])
        u_file = st.file_uploader("Dosyanızı Seçin (CSV/XLSX)", type=["csv", "xlsx"])
        agreed = st.checkbox("Verilerimin anonim olarak işlenmesini ve havuza eklenmesini onaylıyorum.")
        
        if u_file and agreed:
            df = pd.read_csv(u_file) if u_file.name.endswith('.csv') else pd.read_excel(u_file)
            count = len(df)
            val = count * 0.15
            if st.button("Havuza Gönder ve Değerlemeyi Onayla"):
                save_to_vault(p_cat, count, val)
                st.success(f"Tebrikler! {count} satır veri başarıyla gönderildi. Tahmini Pazar Değeri: ${val:.2f}")

# --- GÖRÜNÜM 2: YÖNETİCİ PANELİ (SENİN EKRANIN) ---
else:
    st.title("🛡️ AXON PRO - Enterprise Vault v5.1")
    # Mevcut yönetim kodu buraya devam eder (Senin az önceki kodun)
    # ... (Kısalık adına burayı senin mevcut kodunla aynı düşün)
    st.write("Yönetim paneline hoş geldin Kaptan.")
    # İstatistikleri gösteren kısımlar vb...
