import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px

# --- 1. GÜVENLİ ANAHTAR ERİŞİMİ ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"

st.set_page_config(page_title="AXON PRO | Negotiation Suite", layout="wide", initial_sidebar_state="expanded")

# --- ÖZEL STİL (Yacht & Tech Karbon Görünüm) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2563eb; color: white; }
    </style>
    """, unsafe_allow_name_allowed=True)

st.title("🛡️ AXON PRO - Enterprise Negotiation Suite")
st.markdown("---")

# --- 2. SOL YÖNETİM PANELİ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=100)
    st.header("⚙️ Operasyon Merkezi")
    target_company = st.selectbox("🎯 Alıcı Kurum:", ["OpenAI", "Google DeepMind", "Meta AI", "Anthropic", "Tesla AI"])
    data_category = st.selectbox("📊 Veri Tipi:", ["Tüketici Davranışı", "Finansal Trendler", "Lojistik/Konum", "Sağlık Metrikleri"])
    negotiation_style = st.radio("🤝 Müzakere Tarzı:", ["Agresif (Yüksek Fiyat)", "Dengeli", "Hızlı Satış"])
    st.divider()
    st.success("✅ Ajanlar Göreve Hazır")

# --- 3. VERİ YÜKLEME VE ANALİZ ---
uploaded_file = st.file_uploader("📂 Pazarlanacak Veri Setini Yükleyin", type=["csv", "xlsx"])

if uploaded_file:
    # Veri Okuma
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📋 Veri Özeti")
            record_count = len(df)
            unit_price = 0.22 if negotiation_style == "Agresif (Yüksek Fiyat)" else 0.15
            total_valuation = record_count * unit_price
            
            st.metric("Satır Sayısı", f"{record_count:,}")
            st.metric("Tahmini Değer", f"${total_valuation:,.2f}")
            st.metric("Veri Kalite Skoru", "94/100")

        with col2:
            st.subheader("📉 Veri Dağılım Grafiği")
            # Rastgele bir sütun seçip basit bir analiz yapalım
            fig = px.pie(df.head(10), names=df.columns[0], hole=.4, template="plotly_dark")
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # --- 4. ÇOKLU AJAN MÜZAKERE MASASI ---
        if st.button(f"🚀 {target_company} Masasına Otur"):
            
            tabs = st.tabs(["💰 Satış Stratejisi", "⚖️ Hukuki Taslak", "📈 Pazar Analizi"])
            
            def ask_agent(prompt):
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": "Sen AXON PRO platformunun uzman bir yapay zeka ajanısın."},
                                 {"role": "user", "content": prompt}]
                }
                return requests.post(url, headers=headers, json=payload).json()['choices'][0]['message']['content']

            with st.status("Ajanlar {target_company} ile gizli oturumda...", expanded=True) as status:
                
                with tabs[0]:
                    st.markdown("### 🏹 Satış Uzmanı Raporu")
                    res1 = ask_agent(f"{target_company} için {record_count} satırlık {data_category} verisini {total_valuation}$ fiyatla satacak profesyonel ve ikna edici bir teklif yaz. Tarz: {negotiation_style}")
                    st.write(res1)
                
                with tabs[1]:
                    st.markdown("### ⚖️ Hukuk Müşaviri Taslağı")
                    res2 = ask_agent(f"{data_category} verisinin {target_company} firmasına mikro-lisanslanması için kısa, profesyonel bir gizlilik ve kullanım sözleşmesi taslağı hazırla.")
                    st.write(res2)
                
                with tabs[2]:
                    st.markdown("### 📉 Pazar Analisti Görüşü")
                    res3 = ask_agent(f"{data_category} verisinin 2026 pazarındaki güncel değerini analiz et. {total_valuation}$ fiyatı pazar standartlarına uygun mu?")
                    st.write(res3)
                
                status.update(label="✅ Müzakere Dosyası Hazır!", state="complete")

st.caption(f"AXON Enterprise v3.0 | 2026 Stealth Mode | Location: Göcek / Muğla")
