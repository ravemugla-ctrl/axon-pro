import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px

# --- 1. AYARLAR ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"

st.set_page_config(page_title="AXON PRO | Negotiation Suite", layout="wide")

# Tasarım
st.markdown("""<style>.stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }</style>""", unsafe_allow_html=True)

st.title("🛡️ AXON PRO - Enterprise Negotiation Suite")
st.markdown("---")

# --- 2. YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Operasyon Merkezi")
    target_company = st.selectbox("🎯 Alıcı Kurum:", ["OpenAI", "Google", "Meta AI", "Anthropic", "Tesla AI"])
    data_category = st.selectbox("📊 Veri Tipi:", ["Tüketici Davranışı", "Finansal Trendler", "Lojistik/Konum", "Sağlık"])
    neg_style = st.radio("🤝 Tarz:", ["Agresif", "Dengeli", "Hızlı Satış"])
    st.divider()
    st.success("✅ Ajanlar Hazır")

# --- 3. VERİ YÜKLEME ---
uploaded_file = st.file_uploader("📂 Veri Setini Yükleyin", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Dosya Okuma
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Analiz Panel
        c1, c2 = st.columns([1, 2])
        record_count = len(df)
        u_price = 0.22 if neg_style == "Agresif" else 0.15
        total_val = record_count * u_price
        
        with c1:
            st.metric("Satır Sayısı", f"{record_count:,}")
            st.metric("Tahmini Değer", f"${total_val:,.2f}")
        
        with c2:
            fig = px.pie(df.head(10), names=df.columns[0], hole=.4, template="plotly_dark")
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- 4. AJANLAR ---
        if st.button(f"🚀 {target_company} Masasına Otur"):
            tabs = st.tabs(["💰 Satış", "⚖️ Hukuk", "📈 Analiz"])
            
            def call_groq(p):
                try:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    h = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                    data = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": p}]
                    }
                    r = requests.post(url, headers=h, json=data)
                    return r.json()['choices'][0]['message']['content']
                except:
                    return "Bağlantı hatası oluştu."

            with st.status("Ajanlar müzakere ediyor..."):
                with tabs[0]:
                    st.write(call_groq(f"{target_company} için {record_count} satır {data_category} verisini {total_val}$ fiyata satacak teklif yaz. Tarz: {neg_style}"))
                with tabs[1]:
                    st.write(call_groq(f"{data_category} verisi için {target_company} ile yapılacak kısa bir gizlilik sözleşmesi yaz."))
                with tabs[2]:
                    st.write(call_groq(f"{data_category} verisinin pazardaki değerini analiz et."))
    except Exception as e:
        st.error(f"Hata: {e}")

st.caption("AXON Enterprise v3.0 | Göcek / Muğla")
