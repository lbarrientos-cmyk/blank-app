# app.py — Demo visual de control de huerta (sin librerías extra)
import streamlit as st
from datetime import datetime, timedelta, time
import random

st.set_page_config(page_title="Huerta • Demo Visual", page_icon="🌿", layout="wide")

# ================== Mock mínimo de datos (solo visual) ==================
def generar_series_mock(horas=24, cada_min=10):
    ahora = datetime.now()
    n = (horas * 60) // cada_min
    tiempos = [ahora - timedelta(minutes=cada_min*(n - 1 - i)) for i in range(n)]
    # Señales simples y suaves
    temp = [round(21 + 2*random.random() + 1.5*random.uniform(-1, 1), 2) for _ in tiempos]
    hum_amb = [round(55 + 6*random.uniform(-1, 1), 1) for _ in tiempos]
    hum_suelo = [round(38 + 10*random.uniform(-1, 1), 1) for _ in tiempos]
    riego = [0]*n
    # Simular 2 riegos y su efecto
    for _ in range(2):
        i = random.randint(3, n-4)
        riego[i] = 1
        for k in range(i, min(i+4, n)):
            hum_suelo[k] = min(100.0, hum_suelo[k] + random.uniform(4, 8))
    return tiempos, temp, hum_amb, hum_suelo, riego

if "data" not in st.session_state:
    st.session_state.data = generar_series_mock()
if "cfg" not in st.session_state:
    st.session_state.cfg = {"auto": True, "umbral": 40.0, "h1": "07:30", "h2": "19:00", "dur": 30}
if "estado" not in st.session_state:
    st.session_state.estado = {"ultima": None, "activaciones_hoy": 0}

tiempos, temp, hum_amb, hum_suelo, riego = st.session_state.data

# ================== Encabezado ==================
l, m, r = st.columns([2,3,2])
with l:
    st.markdown("### 🌿 Huerta Automatizada — Demo Visual")
    st.caption("UI de monitoreo y control (solo front-end).")
with r:
    st.write("")

st.divider()

# ================== KPIs ==================
k1, k2, k3, k4 = st.columns(4)
k1.metric("Temperatura", f"{temp[-1]} °C")
k2.metric("Humedad ambiente", f"{hum_amb[-1]} %")
k3.metric("Humedad del suelo", f"{hum_suelo[-1]} %")
if st.session_state.estado["ultima"]:
    k4.metric("Último riego", st.session_state.estado["ultima"].strftime("%d/%m %H:%M"),
              f"{st.session_state.estado['activaciones_hoy']} hoy")
else:
    k4.metric("Último riego", "—")

st.caption("Datos simulados únicamente para diseño visual.")

# ================== Tabs ==================
tab_dash, tab_sens, tab_riego, tab_info = st.tabs(["Dashboard", "Sensores", "Riego", "Ajustes/Notas"])

with tab_dash:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Humedad del suelo (%)")
        st.line_chart({"Humedad suelo (%)": hum_suelo})
    with c2:
        st.subheader("Temperatura / Humedad ambiente")
        st.line_chart({
            "Temperatura (°C)": temp,
            "Humedad amb. (%)": hum_amb
        })

    st.subheader("Eventos de riego")
    st.bar_chart({"Riego (1=on)": riego})

with tab_sens:
    st.subheader("Lecturas recientes")
    horas = st.slider("Rango (horas)", 1, 72, 24)
    corte = datetime.now() - timedelta(hours=horas)

    # Construir una tabla simple (lista de dicts) sin pandas
    filas = []
    for t, T, Ha, Hs, R in zip(tiempos, temp, hum_amb, hum_suelo, riego):
        if t >= corte:
            filas.append({
                "Hora": t.strftime("%d/%m %H:%M"),
                "Temp (°C)": T,
                "Hum. amb (%)": Ha,
                "Hum. suelo (%)": Hs,
                "Riego": "Sí" if R == 1 else "No"
            })
    st.table(filas if filas else [{"Mensaje": "Sin datos en el rango seleccionado"}])

with tab_riego:
    st.subheader("Control de riego (simulado)")
    a, b = st.columns([1,2])

    with a:
        st.markdown("**Modo automático**")
        st.session_state.cfg["auto"] = st.toggle("Habilitar automático", value=st.session_state.cfg["auto"])
        st.session_state.cfg["umbral"] = st.number_input(
            "Umbral humedad suelo (%)", min_value=10.0, max_value=90.0,
            value=float(st.session_state.cfg["umbral"]), step=1.0
        )

        st.markdown("---")
        st.markdown("**Riego manual**")
        if st.button("Activar riego ahora", use_container_width=True):
            st.session_state.estado["ultima"] = datetime.now()
            st.session_state.estado["activaciones_hoy"] += 1
            # efecto visual inmediato en último punto
            hum_suelo[-1] = min(100.0, hum_suelo[-1] + 6.0)
            st.success("Riego activado (simulación visual).")

    with b:
        st.markdown("**Programación horaria**")
        h1 = st.time_input("Horario 1", value=time.fromisoformat(st.session_state.cfg["h1"]))
        h2 = st.time_input("Horario 2", value=time.fromisoformat(st.session_state.cfg["h2"]))
        dur = st.number_input("Duración (segundos)", min_value=5, max_value=600,
                              value=int(st.session_state.cfg["dur"]), step=5)

        if st.button("Guardar programación"):
            st.session_state.cfg["h1"] = h1.strftime("%H:%M")
            st.session_state.cfg["h2"] = h2.strftime("%H:%M")
            st.session_state.cfg["dur"] = int(dur)
            st.success("Programación guardada (memoria volátil).")

    st.info("Frontend puro: estos controles no llaman hardware ni APIs.")

with tab_info:
    st.subheader("Notas")
    st.markdown(
        """
- Este ejemplo evita **cualquier import extra** (solo `streamlit` y stdlib).
- Los gráficos usan listas; no se requiere `pandas`.
- Para conectar con tu backend, reemplazá las listas por lecturas desde API y
  accioná el riego con requests HTTP/MQTT según tu hardware.
        """
    )

st.divider()
st.caption("Huerta • Demo Visual en Streamlit (sin librerías externas).")
