import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. AYARLAR VE GÜVENLİK ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"
DATA_POOL_FILE = "MASTER_DATA_POOL.csv"

st.set_page_config(page_title="AXON PRO | Data Vault", layout="wide")

# Tasarım
st.markdown("""<style>.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }</style>""", unsafe_allow_html=True)

# --- VERİ HAVUZU FONKSİYONLARI ---
def save_to_pool(new_df, category):
    new_df['upload_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_df['category'] = category
    if os.path.exists(DATA_POOL_FILE):
        pool_df = pd.read_csv(DATA_POOL_FILE)
        updated_pool = pd.concat([pool_df, new_df], ignore_index=True)
        updated_pool.to_csv(DATA_POOL_FILE, index=False)
    else:
        new_df.to_csv(DATA_POOL_FILE, index=False)

def get_pool_stats():
    if os.path.exists(DATA_POOL_FILE):
        pool_df = pd.read_csv(DATA_POOL_FILE)
        return len(pool_df), pool_df['category'].nunique()
    return 0, 0

# --- 2. ANA PANEL ---
st.title("🛡️ AXON PRO - Enterprise Data Vault")
st.markdown("---")

# Havuz İstatistikleri
total_rows, total_cats = get_pool_stats()
m1, m2, m3 = st.columns(3)
m1.metric("Toplam Havuz Hacmi", f"{total_rows:,} Satır")
m2.metric("Aktif Veri Kategorileri", total_cats)
m3.metric("Sistem Durumu", "💾 Arşivleme Aktif")

# --- 3. YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Operasyon Merkezi")
    target_company = st.selectbox("🎯 Alıcı Kurum:", ["OpenAI", "Google", "Meta AI", "Anthropic", "Tesla AI"])
    data_category = st.selectbox("📊 Veri Tipi:", ["Tüketici Davranışı", "Finansal Trendler", "Lojistik/Konum", "Sağlık"])
    neg_style = st.radio("🤝 Tarz:", ["Agresif", "Dengeli", "Hızlı Satış"])
    st.divider()
    if st.checkbox("📜 Rıza Metnini Okudum ve Kabul Ediyorum"):
        st.info("Kullanıcı verisinin anonimleştirilerek havuzda saklanmasına izin verildi.")

# --- 4. VERİ YÜKLEME ---
uploaded_file = st.file_uploader("📂 Yeni Veri Setini Havuza Ekleyin", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        # Havuza Kaydet Butonu
        if st.button("📥 Veriyi Analiz Et ve Havuza Arşivle"):
            save_to_pool(df, data_category)
            st.success("✅ Veri başarıyla MASTER havuzuna eklendi!")
            
            # Analiz ve Pazarlık
            record_count = len(df)
            u_price = 0.22 if neg_style == "Agresif" else 0.15
            total_val = record_count * u_price
            
            tabs = st.tabs(["💰 Satış Stratejisi", "⚖️ Hukuki Taslak", "📊 Havuz Analizi"])
            
            def call_groq(p):
                h = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=h, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": p}]})
                return res.json()['choices'][0]['message']['content']

            with st.status("Ajanlar müzakere ediyor..."):
                s_txt = call_groq(f"{target_company} için {record_count} satır veriyi {total_val}$ fiyata satacak teklif yaz.")
                l_txt = call_groq(f"Bu verinin {target_company} firmasına lisanslanması için rıza metni ve gizlilik sözleşmesi hazırla.")
                
                tabs[0].write(s_txt)
                tabs[1].write(l_txt)
                with tabs[2]:
                    fig = px.bar(df.head(20), template="plotly_dark")
                    st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Hata: {e}")

st.caption("AXON v4.0 | Göcek Vault Operations")
