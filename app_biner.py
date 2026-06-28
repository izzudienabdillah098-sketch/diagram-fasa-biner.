import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulasi Fasa Biner Eutektik", layout="wide")

st.title("🧪 Aplikasi Interaktif Diagram Fasa Biner: Sistem Eutektik Sederhana")
st.markdown("""
Aplikasi ini direnovasi total mengikuti gambar acuan baru: **Sistem Dua Komponen yang Larut Sempurna pada Fase Cair dan Tidak Saling Larut pada Fase Padat**.
Kamu bisa **mengklik langsung area mana saja di dalam grafik** atau menggeser slider di sidebar untuk memindahkan titik kondisi fasa secara instan.
""")

# --- MODEL MATEMATIS DIAGRAM FASA EUTEKTIK SEDERHANA ---
# Titik Eutektik diatur pada X_B = 0.5 dan T = 400°C
# Titik leleh murni Komponen A = 800°C, Komponen B = 700°C
def get_liquidus(x):
    if x <= 0.5:
        return 800 - 400 * (x / 0.5)**1.5
    else:
        return 700 - 300 * ((1.0 - x) / 0.5)**1.5

def get_phase_info(x, t):
    t_liq = get_liquidus(x)
    if t > t_liq:
        return "Fase Cair (L)", "1 Fase (Cair)"
    
    t_eutectic = 400.0
    if t > t_eutectic:
        if x <= 0.5:
            return "Padat α + Cair", "2 Fase (Padat α + Cair)"
        else:
            return "Padat β + Cair", "2 Fase (Padat β + Cair)"
    else:
        return "Dua fase padat terpisah (α + β)", "Fase Padat Campuran (α + β)"

x_grid = np.linspace(0, 1, 300)
y_liquidus = [get_liquidus(x) for x in x_grid]

# --- MANAJEMEN STATE (SINKRONISASI KLIK & SLIDER) ---
if "comp_B" not in st.session_state:
    st.session_state.comp_B = 0.3
if "temp" not in st.session_state:
    st.session_state.temp = 600

# Deteksi jika ada koordinat grafik yang diklik oleh user
if "phase_chart" in st.session_state and st.session_state.phase_chart:
    points = st.session_state.phase_chart.get("selection", {}).get("points", [])
    if points:
        st.session_state.comp_B = max(0.0, min(1.0, round(points[0]["x"], 2)))
        st.session_state.temp = max(150, min(1050, int(points[0]["y"])))

# --- KONTROL SIDEBAR ---
st.sidebar.header("🕹️ Kontrol Simulasi Video")
mode = st.sidebar.radio("Pilih Mode Kontrol:", ["Manual (Eksplorasi / Klik Grafik)", "Animasi Pendinginan Campuran"])

if mode == "Manual (Eksplorasi / Klik Grafik)":
    comp_B = st.sidebar.slider("Komposisi Komponen B (X_B)", 0.0, 1.0, value=st.session_state.comp_B, step=0.01)
    temp = st.sidebar.slider("Temperatur Sistem (°C)", 150, 1050, value=st.session_state.temp, step=5)
    st.session_state.comp_B = comp_B
    st.session_state.temp = temp
    
elif mode == "Animasi Pendinginan Campuran":
    comp_B = st.sidebar.slider("Tentukan Komposisi Tetap B (X_B)", 0.0, 1.0, value=st.session_state.comp_B, step=0.01)
    st.session_state.comp_B = comp_B
    start_btn = st.sidebar.button("▶️ Jalankan Animasi Pendinginan")
    
    if start_btn:
        temp_range = np.linspace(950, 250, 70)
        placeholder = st.empty()
        
        for t in temp_range:
            phase_text, phase_detail = get_phase_info(st.session_state.comp_B, t)
            with placeholder.container():
                st.metric(label="Status Sistem Saat Ini", value=phase_text, delta=f"Suhu: {t:.1f} °C | X_B: {st.session_state.comp_B:.2f}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_grid, y=y_liquidus, mode='lines', name='Garis Liquidus', line=dict(color='darkred', width=3)))
                fig.add_trace(go.Scatter(x=[0, 1.0], y=[400, 400], mode='lines', name='Garis Temperatur Eutektik (Te)', line=dict(color='purple', dash='dash', width=2)))
                fig.add_trace(go.Scatter(x=[0.5], y=[400], mode='markers', name='Titik Eutektik', marker=dict(color='black', size=12, symbol='circle')))
                fig.add_trace(go.Scatter(x=[st.session_state.comp_B], y=[t], mode='markers', marker=dict(color='gold', size=15, line=dict(color='black', width=2)), name='Titik Sistem'))
                
                fig.update_layout(
                    xaxis=dict(title='Komposisi Fraksi Mol B (X_B)', range=[0, 1]), 
                    yaxis=dict(title='Temperatur (°C)', range=[150, 1050]), 
                    height=550, font=dict(color="black", size=12)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"anim_{t}")
            time.sleep(0.08)
        st.success("Pendinginan Selesai! Zat telah membeku sempurna.")
        st.stop()

# --- DISPLAY UTAMA MANUAL MODE ---
phase_text, phase_detail = get_phase_info(st.session_state.comp_B, st.session_state.temp)

col1, col2, col3 = st.columns(3)
col1.metric("Komposisi (X_B)", f"{st.session_state.comp_B:.2f}")
col2.metric("Temperatur (T)", f"{st.session_state.temp} °C")
col3.metric("Keadaan Fase", phase_text)

fig = go.Figure()

# 0. MESH GRID TRANSPARAN UNTUK FITUR KLIK
x_mesh, y_mesh = np.meshgrid(np.linspace(0, 1, 40), np.linspace(150, 1050, 40))
fig.add_trace(go.Scatter(
    x=x_mesh.flatten(), y=y_mesh.flatten(), mode='markers',
    marker=dict(color='rgba(0,0,0,0)', size=6),
    showlegend=False, hoverinfo='skip', name='ClickGrid'
))

# 1. Garis-Garis Utama Diagram Sesuai Gambar uu.jpeg
fig.add_trace(go.Scatter(x=x_grid, y=y_liquidus, mode='lines', name='Garis Liquidus', line=dict(color='darkred', width=3)))
fig.add_trace(go.Scatter(x=[0, 1.0], y=[400, 400], mode='lines', name='Garis Solidus (Te)', line=dict(color='black', dash='dash', width=2)))
fig.add_trace(go.Scatter(x=[0.5], y=[400], mode='markers', name='Titik Eutektik', marker=dict(color='black', size=12, symbol='circle')))

# 2. Titik Tracker Penunjuk Posisi
fig.add_trace(go.Scatter(
    x=[st.session_state.comp_B], y=[st.session_state.temp], mode='markers+text', name='Titik Kondisi',
    marker=dict(color='gold', size=16, symbol='circle', line=dict(color='black', width=2)),
    text=[f"<b>{phase_detail}</b>"], textposition="top right"
))

# 3. Label Teks Area Grafik (Bahasa Indonesia & Hitam Pekat Sesuai Gambar Buku)
fig.add_annotation(x=0.5, y=750, text="<b>Fase Cair (L)</b>", showarrow=False, font=dict(size=14))
fig.add_annotation(x=0.18, y=480, text="<b>Padat α + Cair</b>", showarrow=False, font=dict(size=13))
fig.add_annotation(x=0.82, y=460, text="<b>Padat β + Cair</b>", showarrow=False, font=dict(size=13))
fig.add_annotation(x=0.5, y=280, text="<b>Dua fase padat terpisah (α + β)</b>", showarrow=False, font=dict(size=14))
fig.add_annotation(x=0.5, y=430, text="<b>Titik Eutektik</b>", showarrow=True, arrowhead=2, ax=0, ay=-40, font=dict(size=12))

# Penanda Komponen Murni di Ujung Sumbu X bawah
fig.add_annotation(x=0.01, y=170, text="<b>A</b>", showarrow=False, font=dict(size=15, color="blue"))
fig.add_annotation(x=0.99, y=170, text="<b>B</b>", showarrow=False, font=dict(size=15, color="blue"))

# Tampilan Grafik Global (Tulisan Hitam Bersih)
fig.update_layout(
    xaxis=dict(title='Komposisi Campuran (Fraksi Mol B -> X_B)', range=[0, 1], gridcolor='lightgray'),
    yaxis=dict(title='Temperatur / Suhu (°C)', range=[150, 1050], gridcolor='lightgray'),
    height=600, plot_bgcolor='white',
    font=dict(color="black", size=12),
    clickmode='event+select'
)

st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="phase_chart")
