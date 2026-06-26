import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulasi Fasa Biner A2B3", layout="wide")

st.title("🧪 Aplikasi Interaktif Diagram Fasa Biner: Pembentukan Senyawa $A_2B_3$")
st.markdown("""
Aplikasi ini dibuat khusus untuk mendukung presentasi video mengenai **Sistem Dua Komponen yang Tidak Bercampur pada Fase Padat dan Membentuk Produk Baru ($A_2B_3$)**.
""")

# --- MODEL MATEMATIS DIAGRAM FASA BINER ---
def get_liquidus(x):
    if x < 0.3:
        return 800 - 300 * (x / 0.3)**2
    elif x < 0.6:
        return 900 - 400 * ((0.6 - x) / 0.3)**2
    elif x < 0.8:
        return 900 - 450 * ((x - 0.6) / 0.2)**2
    else:
        return 700 - 250 * ((1.0 - x) / 0.2)**2

def get_phase_info(x, t):
    t_liq = get_liquidus(x)
    
    if t > t_liq:
        return "Fase Cair (Larutan Homogen A + B)", "1 Fase (Cair)"
    
    if x < 0.6:
        t_sol = 500.0
        if t > t_sol:
            if x < 0.3:
                return "Cair + Padatan A murni", "2 Fase (Cair + Padat A)"
            else:
                return "Cair + Padatan Senyawa A₂B₃", "2 Fase (Cair + Padat A₂B₃)"
        else:
            return "Campuran Padat (Padat A + Padat A₂B₃)", "Fase Padat Campuran"
            
    else:
        t_sol = 450.0
        if t > t_sol:
            if x < 0.8:
                return "Cair + Padatan Senyawa A₂B₃", "2 Fase (Cair + Padat A₂B₃)"
            else:
                return "Cair + Padatan B murni", "2 Fase (Cair + Padat B)"
        else:
            return "Campuran Padat (Padat A₂B₃ + Padat B)", "Fase Padat Campuran"

x_grid = np.linspace(0, 1, 300)
y_liquidus = [get_liquidus(x) for x in x_grid]

# --- KONTROL SIDEBAR ---
st.sidebar.header("🕹️ Kontrol Simulasi Video")
mode = st.sidebar.radio("Pilih Mode Kontrol:", ["Manual (Eksplorasi)", "Animasi Pendinginan Campuran"])

if mode == "Manual (Eksplorasi)":
    comp_B = st.sidebar.slider("Komposisi Komponen B (X_B)", 0.0, 1.0, 0.4, 0.01)
    temp = st.sidebar.slider("Temperatur Sistem (°C)", 200, 1000, 600, 5)
    
elif mode == "Animasi Pendinginan Campuran":
    comp_B = st.sidebar.slider("Tentukan Komposisi Tetap B (X_B)", 0.0, 1.0, 0.4, 0.01)
    start_btn = st.sidebar.button("▶️ Jalankan Animasi Pendinginan")
    
    if start_btn:
        temp_range = np.linspace(950, 250, 70)
        placeholder = st.empty()
        
        for t in temp_range:
            phase_text, phase_detail = get_phase_info(comp_B, t)
            with placeholder.container():
                st.metric(label="Status Sistem Saat Ini", value=phase_text, delta=f"Suhu: {t:.1f} °C | X_B: {comp_B:.2f}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_grid, y=y_liquidus, mode='lines', name='Garis Liquidus', line=dict(color='red', width=3)))
                fig.add_trace(go.Scatter(x=[0, 0.6], y=[500, 500], mode='lines', name='Solidus Eutektik 1', line=dict(color='blue', dash='dash')))
                fig.add_trace(go.Scatter(x=[0.6, 1.0], y=[450, 450], mode='lines', name='Solidus Eutektik 2', line=dict(color='purple', dash='dash')))
                fig.add_trace(go.Scatter(x=[0.6, 0.6], y=[200, 900], mode='lines', name='Senyawa A₂B₃', line=dict(color='green', width=2)))
                
                fig.add_trace(go.Scatter(x=[comp_B], y=[t], mode='markers', marker=dict(color='gold', size=15, line=dict(color='black', width=2)), name='Titik Sistem'))
                fig.update_layout(xaxis=dict(title='Komposisi Fraksi Mol B (X_B)', range=[0, 1]), yaxis=dict(title='Temperatur (°C)', range=[200, 1050]), height=550)
                st.plotly_chart(fig, use_container_width=True)
            time.sleep(0.08)
        st.success("Pendinginan Selesai! Zat telah membeku sempurna.")
        st.stop()
    else:
        temp = 950

# --- DISPLAY UTAMA FOR MANUAL MODE ---
phase_text, phase_detail = get_phase_info(comp_B, temp)

col1, col2, col3 = st.columns(3)
col1.metric("Komposisi (X_B)", f"{comp_B:.2f}")
col2.metric("Temperatur (T)", f"{temp} °C")
col3.metric("Keadaan Fase", phase_text)

fig = go.Figure()

# 1. Garis Utama Diagram
fig.add_trace(go.Scatter(x=x_grid, y=y_liquidus, mode='lines', name='Garis Liquidus', line=dict(color='darkred', width=3)))
fig.add_trace(go.Scatter(x=[0, 0.6], y=[500, 500], mode='lines', name='Garis Solidus 1', line=dict(color='blue', dash='dash')))
fig.add_trace(go.Scatter(x=[0.6, 1.0], y=[450, 450], mode='lines', name='Garis Solidus 2', line=dict(color='purple', dash='dash')))
fig.add_trace(go.Scatter(x=[0.6, 0.6], y=[200, 900], mode='lines', name='Senyawa A₂B₃ (60% B)', line=dict(color='darkgreen', width=2.5)))

fig.add_trace(go.Scatter(x=[0.3, 0.8], y=[500, 450], mode='markers', name='Titik Eutektik', marker=dict(color='black', size=10, symbol='x')))
fig.add_trace(go.Scatter(x=[0.6], y=[900], mode='markers', name='Titik Leleh Kongruen', marker=dict(color='darkgreen', size=10, symbol='diamond')))

# 2. Titik Tracker (Teks diubah menjadi HITAM TEBAL)
fig.add_trace(go.Scatter(
    x=[comp_B], y=[temp], mode='markers+text', name='Titik Kondisi',
    marker=dict(color='gold', size=16, symbol='circle', line=dict(color='black', width=2)),
    text=[f"<b>{phase_detail}</b>"], textposition="top right",
    textfont=dict(color="black", size=13)  # <-- FIX WARNA TEKS TRACKER KUNING
))

# 3. Label Area Grafik (Semua diubah menjadi warna HITAM TEBAL)
fig.add_annotation(x=0.5, y=980, text="<b>FASE CAIR (LARUTAN HOMOGEN)</b>", showarrow=False, font=dict(size=14, color="black"))
fig.add_annotation(x=0.12, y=580, text="<b>Cair +<br>Padat A</b>", showarrow=False, font=dict(size=12, color="black"))
fig.add_annotation(x=0.43, y=620, text="<b>Cair +<br>Padat A₂B₃</b>", showarrow=False, font=dict(size=12, color="black"))
fig.add_annotation(x=0.72, y=600, text="<b>Cair +<br>Padat A₂B₃</b>", showarrow=False, font=dict(size=12, color="black"))
fig.add_annotation(x=0.90, y=550, text="<b>Cair +<br>Padat B</b>", showarrow=False, font=dict(size=12, color="black"))
fig.add_annotation(x=0.25, y=320, text="<b>PADAT A + PADAT A₂B₃</b>", showarrow=False, font=dict(size=13, color="black"))
fig.add_annotation(x=0.80, y=320, text="<b>PADAT A₂B₃ + PADAT B</b>", showarrow=False, font=dict(size=13, color="black"))

fig.update_layout(
    xaxis=dict(title='Komposisi Campuran (Fraksi Mol B -> X_B)', range=[0, 1], gridcolor='lightgray', titlefont=dict(color='black'), tickfont=dict(color='black')),
    yaxis=dict(title='Temperatur / Suhu (°C)', range=[150, 1050], gridcolor='lightgray', titlefont=dict(color='black'), tickfont=dict(color='black')),
    height=600, plot_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)
