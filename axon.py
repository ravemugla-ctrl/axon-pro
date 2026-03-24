import streamlit as st
import pandas as pd
import os
import requests

# --- 1. AYARLAR ---
SAVED_GROQ_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="AXON PRO | Veri Borsası", layout="wide")

st.title("🛡️ AXON PRO")
st.subheader("Veri Egemenliği ve Mikro-Lisanslama Platformu")
st.markdown("---")

# --- 2. SOL PANEL ---
with st.sidebar:
    st.header("⚙️ Yönetim")
    st.success("✅ Sistem Erişimi Aktif")
    target_company = st.selectbox("Alıcı Kurum:", ["OpenAI", "Google DeepMind", "Meta AI", "Anthropic"])
    data_category = st.selectbox("Veri Kategorisi:", ["Tüketici Alışkanlıkları", "Finansal Hareketler", "Sağlık", "Konum"])

# --- 3. VERİ YÜKLEME ---
uploaded_file = st.file_uploader("Pazarlanacak veri dosyasını seçin", type=["csv", "xlsx"])

record_count = 0
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    record_count = len(df)
    st.info(f"📁 {record_count} satır veri tespit edildi.")

# --- 4. DİNAMİK METRİKLER ---
unit_price = 0.18
total_valuation = record_count * unit_price

c1, c2, c3 = st.columns(3)
c1.metric("Birim Fiyat", f"{unit_price} USD")
c2.metric("Toplam Değer", f"{total_valuation:.2f} USD")
c3.metric("Veri Hacmi", f"{record_count} Satır")

# --- 5. LİTE AJAN MOTORU ---
if st.button(f"{target_company} ile Müzakereyi Başlat"):
    if record_count == 0:
        st.warning("Lütfen önce bir dosya yükleyin.")
    else:
        with st.status("AXON Ajanları müzakereye başlıyor...", expanded=True):
            # Groq API'ye doğrudan istek atıyoruz (Ağır kütüphane gerektirmez)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Sen bir veri borsası uzmanısın. {target_company} firmasına {record_count} satır {data_category} verisini {total_valuation} dolara satmak için profesyonel bir teklif hazırla."}]
            }
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()['choices'][0]['message']['content']
            
        st.success("✅ Pazarlık Tamamlandı!")
        st.write(result)

st.caption("AXON v2.0 | Render Cloud Edition")
