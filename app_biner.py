import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulasi Fasa Peritektek", layout="wide")

st.title("🧪 Aplikasi Interaktif Diagram Fasa: Pembentukan Senyawa Baru C (Sistem Peritektek)")
st.markdown("""
Aplikasi ini dimodifikasi total mengikuti diagram fasa peritektek terbaru kamu. 
Dukung fitur **Click-to-Move**! Kamu bisa **mengklik langsung area mana saja di dalam grafik** atau menggeser slider di sidebar untuk memindahkan titik kondisi fasa secara instan.
""")

# --- MODEL MATEMATIS DIAGRAM FASA PERITEKTEK ---
# TA = 800, TP = 550, TB_murni = 750, TB_garis = 350
# X_PA = 0.3, X_C = 0.5, X_PB = 0.7
def get_phase_info(x, t):
    # Batas Garis Liquidus
    if x <= 0.3:
        t_liq = 800 - (800 - 550) * (x / 0.3)**1.5
        if t > t_liq:
            return "L (Cairan)", "1 Fase (Cairan Homogen)"
        elif t > 550:
            return "L + A(s) (Cairan + Padat A)", "2 Fase (L + A_solid)"
    elif x >= 0.7:
        t_liq = 550 + (750 - 550) * ((x - 0.7) / 0.3)**1.5
        if t > t_liq:
            return "L (Cairan)", "1 Fase (Cairan Homogen)"
        elif t > 550:
            return "L + B(s) (Cairan + Padat B)", "2 Fase (L + B_solid)"
    else:
        if t > 550:
            return "L (Cairan)", "1 Fase (Cairan Homogen)"

    # Batas daerah di bawah suhu peritektek TP = 550
    # Model baji/wedge untuk Senyawa Baru C(s) di sekitar X = 0.5
    factor = max(0.0, min(1.0, (550 - t) / (550 - 150)))
    left_wedge = 0.5 - 0.03 * factor
    right_wedge = 0.5 + 0.03 * factor

    if x <= 0.3:
        return "A(s) (Padat A)", "Fase Padat A murni"
    elif x < left_wedge:
        return "A(s) + C(s) (Padat A + Senyawa C)", "2 Fase Padat (A + C)"
    elif x <= right_wedge:
        return "C(s) (Senyawa Baru C)", "Fase Senyawa Baru C"
    elif x < 0.7:
        return "B(s) + C(s) (Padat B + Senyawa C)", "2 Fase Padat (B + C)"
    else:
        return "B(s) (Padat B)", "Fase Padat B murni"

# Pembuatan kurva halus untuk garis liquidus
x_left = np.linspace(0, 0.3, 50)
y_left = [800 - (800 - 550) * (x / 0.3)**1.5 for x in x_left]
x_right = np.linspace(0.7, 1.0, 50)
y_right = [550 + (750 - 550) * ((x - 0.7) / 0.3)**1.5 for x in x_right]

# --- MANAJEMEN STATE (KLIK & SLIDER SINKRON) ---
if "comp_B" not in st.session_state:
    st.session_state.comp_B = 0.4
if "temp" not in st.session_state:
    st.session_state.temp = 650

if "phase_chart" in st.session_state and st.session_state.phase_chart:
    points = st.session_state.phase_chart.get("selection", {}).get("points", [])
    if points:
        st.session_state.comp_B = max(0.0, min(1.0, round(points[0]["x"], 2)))
        st.session_state.temp = max(150, min(950, int(points[0]["y"])))

# --- SIDEBAR KONTROL ---
st.sidebar.header("🕹️ Kontrol Simulasi")
mode = st.sidebar.radio("Mode Kontrol:", ["Manual (Klik Grafik / Slider)", "Animasi Pendinginan"])

if mode == "Manual (Klik Grafik / Slider)":
    comp_B = st.sidebar.slider("Komposisi Fraksi Mol B", 0.0, 1.0, value=st.session_state.comp_B, step=0.01)
    temp = st.sidebar.slider("Suhu / Temperatur (°C)", 150, 950, value=st.session_state.temp, step=5)
    st.session_state.comp_B = comp_B
    st.session_state.temp = temp
else:
    comp_B = st.sidebar.slider("Tentukan Komposisi B", 0.0, 1.0, value=st.session_state.comp_B, step=0.01)
    st.session_state.comp_B = comp_B
    if st.sidebar.button("▶️ Jalankan Animasi Pendinginan"):
        placeholder = st.empty()
        for t in np.linspace(900, 200, 60):
            p_txt, p_det = get_phase_info(st.session_state.comp_B, t)
            with placeholder.container():
                st.metric("Status Sistem", p_txt, delta=f"Suhu: {t:.1f} °C")
                # Gambar grafik animasi disederhanakan
                fig_anim = go.Figure()
                fig_anim.add_trace(go.Scatter(x=x_left, y=y_left, mode='lines', line=dict(color='blue', width=3), showlegend=False))
                fig_anim.add_trace(go.Scatter(x=x_right, y=y_right, mode='lines', line=dict(color='green', width=3), showlegend=False))
                fig_anim.add_trace(go.Scatter(x=[0.3, 0.7], y=[550, 550], mode='lines', line=dict(color='red', dash='dash'), showlegend=False))
                fig_anim.add_trace(go.Scatter(x=[st.session_state.comp_B], y=[t], mode='markers', marker=dict(color='gold', size=15, line=dict(color='black', width=2)), showlegend=False))
                fig_anim.update_layout(xaxis=dict(range=[0,1]), yaxis=dict(range=[150, 950]), height=500)
                st.plotly_chart(fig_anim, use_container_width=True, key=f"anim_{t}")
            time.sleep(0.06)
        st.stop()

# --- DISPLAY UTAMA MANUAL ---
phase_text, phase_detail = get_phase_info(st.session_state.comp_B, st.session_state.temp)

col1, col2, col3 = st.columns(3)
col1.metric("Komposisi (Fraksi Mol B)", f"{st.session_state.comp_B:.2f}")
col2.metric("Suhu (T)", f"{st.session_state.temp} °C")
col3.metric("Daerah Fasa", phase_text)

fig = go.Figure()

# 0. GRID TRANSPARAN UNTUK DETEKSI KLIK
x_m, y_m = np.meshgrid(np.linspace(0, 1, 35), np.linspace(150, 950, 35))
fig.add_trace(go.Scatter(x=x_m.flatten(), y=y_m.flatten(), mode='markers', marker=dict(color='rgba(0,0,0,0)', size=5), showlegend=False, hoverinfo='skip'))

# 1. WARNAI DAERAH FASA (Mewakili visual indah seperti DIAGRAM BARU.jpeg)
# Cairan L (Biru Muda)
fig.add_trace(go.Scatter(x=[0, 0.3, 0.7, 1, 1, 0], y=[800, 550, 550, 750, 950, 950], fill='toself', fillcolor='rgba(173, 216, 230, 0.3)', line=dict(width=0), mode='lines', showlegend=False, hoverinfo='skip'))
# L + A(s) (Hijau Kebiruan)
fig.add_trace(go.Scatter(x=list(x_left)+[0], y=list(y_left)+[550], fill='toself', fillcolor='rgba(144, 238, 144, 0.2)', line=dict(width=0), mode='lines', showlegend=False, hoverinfo='skip'))
# L + B(s) (Hijau Muda)
fig.add_trace(go.Scatter(x=[0.7]+list(x_right)+[0.7], y=[550]+list(y_right)+[550], fill='toself', fillcolor='rgba(144, 238, 144, 0.3)', line=dict(width=0), mode='lines', showlegend=False, hoverinfo='skip'))
# Senyawa C(s) (Ungu)
fig.add_trace(go.Scatter(x=[0.5, 0.47, 0.53], y=[550, 150, 150], fill='toself', fillcolor='rgba(147, 112, 219, 0.3)', line=dict(width=0), mode='lines', showlegend=False, hoverinfo='skip'))

# 2. GARIS UTAMA DIAGRAM
fig.add_trace(go.Scatter(x=x_left, y=y_left, mode='lines', name='Liquidus A', line=dict(color='blue', width=3)))
fig.add_trace(go.Scatter(x=x_right, y=y_right, mode='lines', name='Liquidus B', line=dict(color='green', width=3)))
fig.add_trace(go.Scatter(x=[0.3, 0.7], y=[550, 550], mode='lines', name='Suhu Peritektek (Tp)', line=dict(color='red', dash='dash', width=2.5)))

# Garis Batas Vertikal & Horisontal Internal
fig.add_trace(go.Scatter(x=[0.3, 0.3], y=[150, 550], mode='lines', line=dict(color='black', dash='dot'), showlegend=False))
fig.add_trace(go.Scatter(x=[0.7, 0.7], y=[150, 550], mode='lines', line=dict(color='black', dash='dot'), showlegend=False))
fig.add_trace(go.Scatter(x=[0.5, 0.5], y=[550, 550], mode='markers', name='Titik P (Peritektek)', marker=dict(color='purple', size=10, symbol='diamond')))
fig.add_trace(go.Scatter(x=[0, 0.3], y=[350, 350], mode='lines', line=dict(color='blue', dash='dash'), showlegend=False)) # Garis TB di kiri bawah sesuai gambar buku

# 3. TITIK TRACKER KONDISI SEKARANG
fig.add_trace(go.Scatter(
    x=[st.session_state.comp_B], y=[st.session_state.temp], mode='markers+text', name='Titik Sistem',
    marker=dict(color='gold', size=16, line=dict(color='black', width=2.5)),
    text=[f"<b>{phase_detail}</b>"], textposition="top center"
))

# 4. ANNOTATION / LABEL TEKS PERSIS SEPERTI GAMBAR BUKU
fig.add_annotation(x=0.5, y=750, text="<b>L</b>", showarrow=False, font=dict(size=16))
fig.add_annotation(x=0.12, y=620, text="<b>L + A(s)</b>", showarrow=False, font=dict(size=12))
fig.add_annotation(x=0.85, y=620, text="<b>L + B(s)</b>", showarrow=False, font=dict(size=12))
fig.add_annotation(x=0.15, y=380, text="<b>A(s)</b>", showarrow=False, font=dict(size=14))
fig.add_annotation(x=0.38, y=350, text="<b>A(s) + C(s)</b>", showarrow=False, font=dict(size=12))
fig.add_annotation(x=0.5, y=280, text="<b>C(s)</b><br><span style='size:10px;'>Senyawa baru</span>", showarrow=False, font=dict(size=12, color="purple"))
fig.add_annotation(x=0.61, y=350, text="<b>B(s) + C(s)</b>", showarrow=False, font=dict(size=12))
fig.add_annotation(x=0.85, y=350, text="<b>B(s)</b>", showarrow=False, font=dict(size=14))

# Penanda Titik Sumbu Utama
fig.add_annotation(x=0.3, y=570, text="<b>PA</b>", showarrow=False)
fig.add_annotation(x=0.5, y=570, text="<b>P</b>", showarrow=False)
fig.add_annotation(x=0.7, y=570, text="<b>PB</b>", showarrow=False)

# 5. ATUR LAYOUT (Sintaks Baru Bebas Dari ValueError)
fig.update_layout(
    xaxis=dict(title=dict(text='<b>Komposisi (fraksi mol B →)</b>', font=dict(color='black', size=14)), range=[0, 1], gridcolor='lightgray'),
    yaxis=dict(title=dict(text='<b>Suhu / Temperatur (T)</b>', font=dict(color='black', size=14)), range=[150, 950], gridcolor='lightgray'),
    height=600, plot_bgcolor='white', font=dict(color="black", size=12),
    clickmode='event+select'
)

st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="phase_chart")
