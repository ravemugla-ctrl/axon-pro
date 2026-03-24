import streamlit as st
import pandas as pd
import numpy as np
import os
from crewai import Agent, Task, Crew

# --- 1. AYARLAR ---
SAVED_GROQ_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="AXON Enterprise | Veri Borsası", layout="wide")

st.title("🛡️ AXON Enterprise")
st.subheader("Veri Egemenliği ve Mikro-Lisanslama Motoru")
st.markdown("---")

# --- 2. SOL PANEL ---
with st.sidebar:
    st.header("⚙️ Yönetim")
    st.success("✅ Sistem Erişimi Aktif")
    target_company = st.selectbox("Alıcı Kurum:", ["OpenAI", "Google DeepMind", "Meta AI", "Anthropic"])
    data_category = st.selectbox("Veri Kategorisi:", ["Tüketici Alışkanlıkları", "Finansal Hareketler", "Sağlık ve Fitness", "Konum Geçmişi"])
    urgency = st.slider("Veri Tazeliği (Gün):", 1, 30, 7)

# --- 3. VERİ YÜKLEME ALANI (YENİ!) ---
st.markdown("### 📥 Veri Havuzuna Girdi Sağla")
uploaded_file = st.file_uploader("Pazarlanacak veri dosyasını seçin (CSV veya Excel)", type=["csv", "xlsx"])

record_count = 0
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    record_count = len(df)
    st.info(f"📁 Dosya başarıyla yüklendi: **{record_count} satır** veri tespit edildi.")
    st.dataframe(df.head(3)) # İlk 3 satırı önizleme olarak göster

# --- 4. DİNAMİK METRİKLER ---
base_prices = {"Tüketici Alışkanlıkları": 0.15, "Finansal Hareketler": 0.45, "Sağlık ve Fitness": 0.75, "Konum Geçmişi": 0.30}
unit_price = base_prices[data_category] * (1 + (30 - urgency) / 100)
total_valuation = record_count * unit_price

c1, c2, c3 = st.columns(3)
c1.metric("Birim Fiyat", f"{unit_price:.2f} USD")
c2.metric("Toplam Tahmini Değer", f"{total_valuation:.2f} USD")
c3.metric("Veri Hacmi", f"{record_count} Satır")

# --- 5. PAZARLIK MOTORU ---
st.markdown("---")
if st.button(f"{target_company} ile Satış Görüşmesini Başlat"):
    if record_count == 0:
        st.warning("Pazarlık için önce bir veri dosyası yüklemelisiniz!")
    else:
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
        os.environ["OPENAI_API_KEY"] = SAVED_GROQ_KEY

        with st.status("Ajanlar lisanslama protokolü üzerinde çalışıyor...", expanded=True) as status:
            # AJANLAR
            shield = Agent(role='Güvenlik Mimarı', goal='Veriyi anonimleştir.', backstory='PII temizleme uzmanı.', verbose=True)
            broker = Agent(role='Müzakereci', goal=f'{target_company} firmasından bu {record_count} satır için {total_valuation:.2f} USD ödeme onayı al.', backstory='Veri borsacısı.', verbose=True)
            
            # GÖREVLER
            t1 = Task(description=f"Yüklenen {record_count} satır veriyi denetle ve güvenlik onayı ver.", agent=shield, expected_output="Güvenlik Sertifikası.")
            t2 = Task(description=f"{target_company} ile toplam {total_valuation:.2f} USD üzerinden lisanslama anlaşmasını mühürle.", agent=broker, expected_output="Finansal Onay Belgesi.")
            
            crew = Crew(agents=[shield, broker], tasks=[t1, t2])
            result = crew.kickoff()
            status.update(label="Satış Başarıyla Kapatıldı!", state="complete", expanded=False)

        st.success(f"**Tebrikler!** {target_company} verinizi lisansladı.")
        st.write(result)

st.caption("AXON v1.5 | Enterprise Data Union")
