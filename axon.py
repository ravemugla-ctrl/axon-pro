import streamlit as st
import pandas as pd
import os
import requests
from sqlalchemy import create_engine, text
from datetime import datetime

# --- 1. AYARLAR VE GÜVENLİK ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"
DB_URL = os.environ.get("DATABASE_URL")

# --- KAPTAN KÖŞKÜ ŞİFRELERİ (Burayı değiştirebilirsin) ---
ADMIN_USER = "admin"
ADMIN_PASSWORD = "axon-pro-2026" # <--- Burası senin anahtarın!

if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DB_URL) if DB_URL else None

st.set_page_config(page_title="AXON PRO | Secure Vault", layout="wide")

# --- OTURUM YÖNETİMİ ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# URL Parametresi Kontrolü
is_portal = st.query_params.get("mode") == "portal"

# --- DB FONKSİYONLARI ---
def init_db():
    if engine:
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS data_vault (id SERIAL, category TEXT, record_count INTEGER, valuation FLOAT, upload_time TIMESTAMP)"))
            conn.commit()

def save_to_vault(cat, count, val):
    if engine:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO data_vault (category, record_count, valuation, upload_time) VALUES (:cat, :count, :val, :time)"),
                         {"cat": cat, "count": count, "val": val, "time": datetime.now()})
            conn.commit()

def get_vault_stats():
    if engine:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT COUNT(*), SUM(record_count) FROM data_vault")).fetchone()
            return res[0] or 0, res[1] or 0
    return 0, 0

init_db()

# --- GÖRÜNÜM 1: VERİ TOPLAMA PORTALI (DIŞA AÇIK) ---
if is_portal:
    st.title("🛡️ AXON PRO - Veri Ortaklığı Portalı")
    st.info("Verilerinizi güvenli havuzumuza ekleyerek pazar değerini öğrenin.")
    
    with st.container(border=True):
        p_cat = st.selectbox("Kategori:", ["Tüketici", "Turizm", "Finans", "Lojistik"])
        u_file = st.file_uploader("Dosya Yükle", type=["csv", "xlsx"])
        agreed = st.checkbox("Anonim işleme ve lisanslama şartlarını kabul ediyorum.")
        
        if u_file and agreed:
            df = pd.read_csv(u_file) if u_file.name.endswith('.csv') else pd.read_excel(u_file)
            count = len(df)
            val = count * 0.15
            if st.button("Havuza Gönder"):
                save_to_vault(p_cat, count, val)
                st.success(f"Başarıyla kaydedildi! Tahmini Değer: ${val:,.2f}")

# --- GÖRÜNÜM 2: YÖNETİCİ GİRİŞİ VE PANEL ---
else:
    if not st.session_state['logged_in']:
        # GİRİŞ EKRANI
        st.title("🛡️ AXON PRO - Kaptan Köşkü")
        with st.form("Login Form"):
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Sisteme Giriş Yap")
            
            if submit:
                if user == ADMIN_USER and pw == ADMIN_PASSWORD:
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    else:
        # YÖNETİM PANELİ (Giriş Başarılıysa)
        st.sidebar.title("🛠️ AXON Yönetim")
        if st.sidebar.button("Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.title("🛡️ AXON PRO - Enterprise Dashboard")
        
        total_files, total_rows = get_vault_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Arşiv", f"{total_files} Dosya")
        c2.metric("Havuz Hacmi", f"{total_rows:,} Satır")
        c3.metric("Güvenlik", "🔐 Kilitli")
        
        st.markdown("---")
        st.subheader("🤖 Müzakere Masası")
        # Buraya senin eski müzakere kodun gelecek...
        st.info("Kaptan, sistem şu an senin kontrolünde. Verileri analiz edebilir ve ajanları çalıştırabilirsin.")
