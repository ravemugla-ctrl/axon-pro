import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
from fpdf import FPDF

# --- 1. AYARLAR VE GÜVENLİK ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"
DB_URL = os.environ.get("DATABASE_URL")
ADMIN_USER = "admin"
ADMIN_PASSWORD = "axon-pro-2026"

if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DB_URL) if DB_URL else None

st.set_page_config(page_title="AXON PRO | Enterprise Vault", layout="wide")

# Oturum Durumu
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# URL Parametresi
is_portal = st.query_params.get("mode") == "portal"

# --- DB VE PDF FONKSİYONLARI ---
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
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT COUNT(*), SUM(record_count) FROM data_vault")).fetchone()
                return res[0] or 0, res[1] or 0
        except: return 0, 0
    return 0, 0

init_db()

# --- GÖRÜNÜM 1: PORTAL (DIŞA AÇIK) ---
if is_portal:
    st.title("🛡️ AXON PRO - Veri Ortaklığı Portalı")
    with st.container(border=True):
        p_cat = st.selectbox("Kategori:", ["Tüketici", "Turizm", "Lojistik"])
        u_file = st.file_uploader("Dosya Yükle", type=["csv", "xlsx"])
        if u_file and st.checkbox("Şartları Kabul Ediyorum"):
            df = pd.read_csv(u_file) if u_file.name.endswith('.csv') else pd.read_excel(u_file)
            if st.button("Havuza Gönder"):
                save_to_vault(p_cat, len(df), len(df)*0.15)
                st.success("Veri başarıyla kilitlendi!")

# --- GÖRÜNÜM 2: YÖNETİM (ŞİFRELİ) ---
else:
    if not st.session_state['logged_in']:
        st.title("🛡️ AXON PRO - Kaptan Köşkü")
        with st.form("Login"):
            u, p = st.text_input("Kullanıcı"), st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap") and u == ADMIN_USER and p == ADMIN_PASSWORD:
                st.session_state['logged_in'] = True
                st.rerun()
            elif u: st.error("Hatalı Giriş!")
    else:
        # --- ANA PANEL BURADAN BAŞLIYOR ---
        st.sidebar.title("🛠️ AXON Yönetim")
        if st.sidebar.button("Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.title("🛡️ AXON PRO - Enterprise Dashboard")
        f_count, r_count = get_vault_stats()
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Arşiv", f"{f_count} Dosya")
        c2.metric("Havuz Hacmi", f"{r_count:,} Satır")
        c3.metric("Güvenlik", "🔐 SQL Secure")
        
        st.markdown("---")
        
        # Dosya Yükleme ve Ajanlar (ESKİ PANELİN GERİ DÖNÜŞÜ)
        up = st.file_uploader("📂 Analiz İçin Dosya Seçin", type=["csv", "xlsx"])
        if up:
            df = pd.read_csv(up) if up.name.endswith('.csv') else pd.read_excel(up)
            st.plotly_chart(px.pie(df.head(10), names=df.columns[0], hole=.4, template="plotly_dark"), use_container_width=True)
            
            if st.button("🚀 Müzakereyi Başlat"):
                tabs = st.tabs(["💰 Satış", "⚖️ Hukuk", "📈 Analiz"])
                def call_groq(prompt):
                    h = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=h, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                    return res.json()['choices'][0]['message']['content']
                
                with st.status("Ajanlar çalışıyor..."):
                    tabs[0].write(call_groq(f"{len(df)} satır veri için satış teklifi hazırla."))
                    tabs[1].write(call_groq("Bu veri için gizlilik sözleşmesi yaz."))
                    tabs[2].write("Veri havuzu pazar analizi tamamlandı.")
