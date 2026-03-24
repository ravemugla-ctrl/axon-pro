import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
from fpdf import FPDF
import base64

# --- 1. GÜVENLİ ANAHTAR VE AYARLAR ---
SAVED_GROQ_KEY = os.environ.get("GROQ_API_KEY") or "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"

st.set_page_config(page_title="AXON PRO | Negotiation Suite", layout="wide")

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_pdf(target, cat, style, count, val, s_text, l_text, p_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "AXON ENTERPRISE - RESMI MUZAKERE RAPORU", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Alici Kurum: {target}", ln=True)
    pdf.cell(200, 10, f"Veri Kategorisi: {cat}", ln=True)
    pdf.cell(200, 10, f"Muzakere Tarzi: {style}", ln=True)
    pdf.cell(200, 10, f"Veri Hacmi: {count:,} Satir", ln=True)
    pdf.cell(200, 10, f"Toplam Degerleme: ${val:,.2f}", ln=True)
    pdf.ln(10)
    
    sections = [("SATIS TEKLIFI", s_text), ("HUKUKI TASLAK", l_text), ("PAZAR ANALIZI", p_text)]
    for title, text in sections:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, title, ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
    
    return pdf.output(dest="S").encode("latin-1")

st.title("🛡️ AXON PRO - Enterprise Negotiation Suite")
st.markdown("---")

# --- 2. YAN PANEL ---
with st.sidebar:
    st.header("⚙️ Operasyon Merkezi")
    target_company = st.selectbox("🎯 Alıcı Kurum:", ["OpenAI", "Google", "Meta AI", "Anthropic", "Tesla AI"])
    data_category = st.selectbox("📊 Veri Tipi:", ["Tüketici Davranışı", "Finansal Trendler", "Lojistik/Konum", "Sağlık"])
    neg_style = st.radio("🤝 Tarz:", ["Agresif", "Dengeli", "Hızlı Satış"])
    st.divider()
    st.success("✅ Ajanlar ve PDF Motoru Hazır")

# --- 3. VERİ YÜKLEME ---
uploaded_file = st.file_uploader("📂 Veri Setini Yükleyin", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        c1, c2 = st.columns([1, 2])
        record_count, u_price = len(df), (0.22 if neg_style == "Agresif" else 0.15)
        total_val = record_count * u_price
        
        with c1:
            st.metric("Satır Sayısı", f"{record_count:,}")
            st.metric("Tahmini Değer", f"${total_val:,.2f}")
        with c2:
            fig = px.pie(df.head(10), names=df.columns[0], hole=.4, template="plotly_dark")
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        if st.button(f"🚀 {target_company} Masasına Otur"):
            tabs = st.tabs(["💰 Satış", "⚖️ Hukuk", "📈 Analiz"])
            
            def call_groq(p):
                url = "https://api.groq.com/openai/v1/chat/completions"
                h = {"Authorization": f"Bearer {SAVED_GROQ_KEY}", "Content-Type": "application/json"}
                res = requests.post(url, headers=h, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": p}]})
                return res.json()['choices'][0]['message']['content']

            with st.status("Ajanlar müzakere ediyor..."):
                s_txt = call_groq(f"{target_company} için {record_count} satır {data_category} verisini {total_val}$ fiyata satacak teklif yaz.")
                l_txt = call_groq(f"{data_category} verisi için {target_company} ile gizlilik sözleşmesi yaz.")
                p_txt = call_groq(f"{data_category} verisinin pazar analizini yap.")
                
                tabs[0].write(s_txt)
                tabs[1].write(l_txt)
                tabs[2].write(p_txt)
                
                # --- PDF İNDİRME BUTONU ---
                pdf_data = create_pdf(target_company, data_category, neg_style, record_count, total_val, s_txt, l_txt, p_txt)
                st.download_button(label="📄 Muzakere Raporunu PDF Olarak Indir", data=pdf_data, file_name=f"AXON_{target_company}_Rapor.pdf", mime="application/pdf")
                
    except Exception as e:
        st.error(f"Hata: {e}")

st.caption("AXON v3.5 | Resmi Belge Üretim Modülü Aktif")
