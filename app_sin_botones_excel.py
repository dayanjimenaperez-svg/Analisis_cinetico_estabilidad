import streamlit as st

import pandas as pd

import numpy as np

import plotly.graph_objects as go



from groq import Groq


# Recuperar y limpiar la clave API

api_key = str(st.secrets["GROQ_API_KEY"]).strip()



# Verificar que la clave no tenga caracteres extraños

try:

    api_key.encode("ascii")

except UnicodeEncodeError:

    st.error(

        "La clave API contiene caracteres no válidos. "

        "Revisa secrets.toml."

    )

    st.stop()



client = Groq(api_key=api_key)



# ==================================================

# FUNCION GENERAL PARA CALCULAR TIEMPOS CINETICOS

# ==================================================



def calcular_tiempos_caracteristicos(k, orden, C0):



    if k <= 0 or C0 <= 0:

        raise ValueError("k y C0 deben ser positivos.")



    fracciones = {

        "t50": 0.50,

        "t98": 0.98,

        "t95": 0.95,

        "t90": 0.90

    }



    tiempos = {}



    for nombre, fraccion in fracciones.items():



        if orden == "Orden cero":



            tiempo = C0 * (1 - fraccion) / k



        elif orden in ["Orden uno", "Primer orden"]:



            tiempo = -np.log(fraccion) / k



        elif orden in ["Orden dos", "Segundo orden"]:



            tiempo = (1 / fraccion - 1) / (k * C0)



        else:

            raise ValueError("Orden cinético no reconocido.")



        tiempos[nombre] = float(tiempo)



    return tiempos



# ==================================================

# CONFIGURACION GENERAL

# ==================================================



st.set_page_config(

    page_title="Análisis cinético y estabilidad",

    page_icon="🧪",

    layout="wide"

)


# ==================================================
# ESTILO UNIFORME DE BOTONES EN COLOR GRIS
# ==================================================
st.markdown("""
<style>
.stButton > button,
.stDownloadButton > button,
div[data-testid="stFileUploader"] button {
    background-color: #E0E0E0 !important;
    color: #333333 !important;
    border: 1px solid #BDBDBD !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
div[data-testid="stFileUploader"] button:hover {
    background-color: #CFCFCF !important;
    color: #222222 !important;
    border-color: #AFAFAF !important;
}

.stButton > button:focus,
.stDownloadButton > button:focus {
    box-shadow: 0 0 0 0.15rem rgba(120, 120, 120, 0.25) !important;
}
</style>
""", unsafe_allow_html=True)


# ==================================================

# DISEÑO DE TODA LA PAGINA - ROSADO PASTEL

# ==================================================



# ==================================================
# DISEÑO ESTÁNDAR DE STREAMLIT (SIN TEMA ROSADO)
# ==================================================


st.title("🧪 ANÁLISIS CINÉTICO Y ESTABILIDAD")



st.markdown(

    "### 1. Determinación automática del orden cinético"

)



st.write(

    "Ingrese los datos experimentales de tiempo y concentración. "

    "El programa evaluará los ordenes cero, uno y dos mediante "

    "el método integral."

)



# ==================================================

# SELECCION DE UNIDADES

# ==================================================



st.divider()

st.subheader("Unidades de medición")



unidades_tiempo = {

    "Segundos (s)": 1,

    "Minutos (min)": 60,

    "Horas (h)": 3600,

    "Días (d)": 86400,

    "Semanas (sem)": 604800

}



# Factores expresados en mg/L

unidades_concentración = {

    "g/L": 1000,

    "mg/L": 1,

    "ug/L": 0.001,

    "mg/mL": 1000,

    "ug/mL": 1,

    "g/mL": 1000000,

    "kg/m3": 1000

}



col1, col2 = st.columns(2)



with col1:



    st.markdown("**UNIDADES DE TIEMPO**")



    unidad_t_entrada = st.selectbox(

        "Unidad original del tiempo",

        list(unidades_tiempo.keys()),

        index=3

    )



    unidad_t = st.selectbox(

        "Convertir tiempo a",

        list(unidades_tiempo.keys()),

        index=3

    )



with col2:



    st.markdown("**UNIDADES DE CONCENTRACIÓN**")



    unidad_c_entrada = st.selectbox(

        "Unidad original de concentración",

        list(unidades_concentración.keys()),

        index=1

    )



    unidad_c = st.selectbox(

        "Convertir concentración a",

        list(unidades_concentración.keys()),

        index=1

    )





# ==================================================

# INGRESO DE DATOS EXPERIMENTALES

# ==================================================



st.divider()

st.subheader("Datos experimentales")



st.info(

    "Puedes modificar los datos de ejemplo, agregar filas "

    "o eliminar las que no necesites."

)



datos_iniciales = pd.DataFrame({

    "Tiempo": [0.000, 1.000, 2.000, 3.000, 4.000],

    "Concentración": [100.000, 82.000, 67.000, 55.000, 45.000]

}).astype({

    "Tiempo": "float64",

    "Concentración": "float64"

})



datos_para_editor_cinetica = datos_iniciales

datos_editados = st.data_editor(

    datos_para_editor_cinetica,

    num_rows="dynamic",

    use_container_width=True,

    key="editor_tabla_experimental",

    column_config={



        "Tiempo": st.column_config.NumberColumn(

            "Tiempo",

            format="%.4f",

            step=0.0001

        ),



        "Concentración": st.column_config.NumberColumn(

            "Concentración",

            format="%.4f",

            step=0.0001

        )

    }

)





# ==================================================

# ANALISIS CINETICO

# ==================================================



if st.button("ANALIZAR ORDEN CINÉTICO", type="secondary"):
    st.session_state["ejecutar_analisis_cinetico"] = True

if st.session_state.get("ejecutar_analisis_cinetico", False):



    # Recuperar los datos de la tabla editable

    datos = datos_editados.copy()



    # Eliminar solamente las filas completamente vacias

    datos = datos.dropna(

        subset=["Tiempo", "Concentración"],

        how="all"

    ).copy()



    # Reiniciar los indices

    datos = datos.reset_index(drop=True)



    # Convertir los datos a valores numericos

    datos["Tiempo"] = pd.to_numeric(

        datos["Tiempo"],

        errors="coerce"

    )



    datos["Concentración"] = pd.to_numeric(

        datos["Concentración"],

        errors="coerce"

    )



    # ==================================================

    # VALIDACION DE DATOS

    # ==================================================



    if datos.empty:



        st.error(

            "Debes ingresar datos experimentales."

        )



    elif datos.isna().any().any():



        st.error(

            "Hay celdas vacías o valores no numéricos. "

            "Revisa la tabla experimental."

        )



    elif (

        not np.isfinite(datos["Tiempo"]).all()

        or not np.isfinite(datos["Concentración"]).all()

    ):



        st.error(

            "Los datos deben ser valores finitos."

        )



    elif len(datos) < 3:



        st.error(

            "Se necesitan al menos tres datos experimentales."

        )



    elif (datos["Concentración"] <= 0).any():



        valores_invalidos = datos.loc[

            datos["Concentración"] <= 0,

            ["Tiempo", "Concentración"]

        ]



        st.error(

            "Hay concentraciones iguales o menores que cero."

        )



        st.dataframe(

            valores_invalidos,

            use_container_width=True

        )



        st.warning(

            "Todas las concentraciones deben ser positivas "

            "para calcular el logaritmo natural."

        )



    elif datos["Tiempo"].nunique() < 3:



        st.error(

            "Se necesitan al menos tres tiempos diferentes."

        )



    else:



        # ==================================================

        # ORGANIZACION DE LOS DATOS

        # ==================================================



        datos = datos.sort_values(

            "Tiempo"

        )



        t_original = datos["Tiempo"].to_numpy(

            dtype=float

        )



        c_original = datos["Concentración"].to_numpy(

            dtype=float

        )



        # ==================================================

        # CONVERSION AUTOMATICA DE UNIDADES

        # ==================================================



        t = (

            t_original

            * unidades_tiempo[unidad_t_entrada]

            / unidades_tiempo[unidad_t]

        )



        c = (

            c_original

            * unidades_concentración[unidad_c_entrada]

            / unidades_concentración[unidad_c]

        )



        # Comprobar que las conversiones sean validas

        if (

            not np.isfinite(t).all()

            or not np.isfinite(c).all()

            or (c <= 0).any()

        ):



            st.error(

                "Error durante la conversión de unidades. "

                "Revisa los valores ingresados."

            )



        else:



            st.success(

                "Datos validados y unidades convertidas correctamente."

            )



            st.write(

                "### Datos después de la conversión"

            )



            tabla_convertida = pd.DataFrame({



                f"Tiempo ({unidad_t})": t,



                f"Concentración ({unidad_c})": c



            })



            st.dataframe(

                tabla_convertida.style.format("{:.4f}"),

                use_container_width=True

            )



            # ==================================================

            # REGRESIONES DEL METODO INTEGRAL

            # ==================================================



            modelos = [



                {

                    "orden": "Orden cero",

                    "transformación": "C",

                    "y": c,

                    "signo": -1

                },



                {

                    "orden": "Orden uno",

                    "transformación": "ln(C)",

                    "y": np.log(c),

                    "signo": -1

                },



                {

                    "orden": "Orden dos",

                    "transformación": "1/C",

                    "y": 1 / c,

                    "signo": 1

                }



            ]



            resultados = []



            for modelo in modelos:



                y = modelo["y"]



                # Regresion lineal

                pendiente, intercepto = np.polyfit(

                    t,

                    y,

                    1

                )



                # Prediccion del modelo

                prediccion = (

                    pendiente * t + intercepto

                )



                # Suma de cuadrados residuales

                ss_res = np.sum(

                    (y - prediccion) ** 2

                )



                # Suma total de cuadrados

                ss_tot = np.sum(

                    (y - np.mean(y)) ** 2

                )



                # Coeficiente de determinacion

                r2 = (

                    1 - ss_res / ss_tot

                    if ss_tot > 0

                    else np.nan

                )



                # Constante cinetica

                k = modelo["signo"] * pendiente



                resultados.append({



                    "Orden": modelo["orden"],



                    "Transformación": modelo["transformación"],



                    "Pendiente": pendiente,



                    "Intercepto": intercepto,



                    "k": k,



                    "R2": r2,



                    "y": y,



                    "prediccion": prediccion



                })



            # ==================================================

            # TABLA COMPARATIVA DE RESULTADOS

            # ==================================================



            st.divider()



            st.subheader(

                "2. Resultados de las regresiones"

            )



            resumen = pd.DataFrame([



                {

                    "Orden": m["Orden"],



                    "Transformación": m["Transformación"],



                    "Pendiente": m["Pendiente"],



                    "Intercepto": m["Intercepto"],



                    "Constante k": m["k"],



                    "R2": m["R2"]



                }



                for m in resultados



            ])



            st.dataframe(

                resumen.style.format({



                    "Pendiente": "{:.4f}",



                    "Intercepto": "{:.4f}",



                    "Constante k": "{:.4g}",



                    "R2": "{:.4f}"



                }),

                use_container_width=True

            )





            # ==================================================

            # GRÁFICAS DE LOS TRES MODELOS

            # ==================================================



            st.divider()



            st.subheader(

                "3. Gráficas de los modelos cinéticos"

            )



            for m in resultados:



                fig = go.Figure()



                # Datos experimentales

                fig.add_trace(

                    go.Scatter(

                        x=t,

                        y=m["y"],

                        mode="lines+markers",

                        name="Datos experimentales"

                    )

                )



                # Regresión lineal

                fig.add_trace(

                    go.Scatter(

                        x=t,

                        y=m["prediccion"],

                        mode="lines",

                        name="Regresión lineal"

                    )

                )



                # Configuración de la gráfica

                fig.update_layout(

                    title=(

                        f'{m["Orden"]}<br>'

                        f'R² = {m["R2"]:.4f}'

                    ),

                    xaxis_title=f"Tiempo ({unidad_t})",

                    yaxis_title=m["Transformación"],

                    template="plotly_white",

                    height=450,

                    annotations=[

                        dict(

                            x=0.02,

                            y=0.98,

                            xref="paper",

                            yref="paper",

                            xanchor="left",

                            yanchor="top",

                            text=(

                                f'Pendiente = {m["Pendiente"]:.6g}<br>'

                                f'Intercepto = {m["Intercepto"]:.6g}<br>'

                                f'R² = {m["R2"]:.6f}'

                            ),

                            showarrow=False,

                            bgcolor="rgba(255,255,255,0.85)",

                            bordercolor="#808080",

                            borderwidth=1

                        )

                    ]

                )



                st.plotly_chart(

                    fig,

                    use_container_width=True

                )





            # ==================================================

            
        # ==================================================
        # SELECCIÓN DEL MEJOR MODELO
        # ==================================================

        st.divider()
        st.subheader("4. Orden cinético seleccionado")

        validos = [
            m for m in resultados
            if (
                np.isfinite(m["R2"])
                and np.isfinite(m["k"])
                and m["k"] > 0
            )
        ]

        if not validos:
            st.warning(
                "No se encontró un modelo con R2 válido "
                "y constante cinética positiva."
            )
        else:
            mejor = max(validos, key=lambda m: m["R2"])

            # Unidades de la constante cinética
            if mejor["Orden"] == "Orden cero":
                unidad_k = f"{unidad_c}/{unidad_t}"
            elif mejor["Orden"] == "Orden uno":
                unidad_k = f"1/{unidad_t}"
            else:
                unidad_k = f"1/({unidad_c}·{unidad_t})"

            st.success(
                f"El orden cinético seleccionado es: {mejor['Orden']}"
            )
            st.metric("Coeficiente R2", f"{mejor['R2']:.4f}")
            st.write(f"**Modelo:** {mejor['Transformación']}")
            st.write(
                f"**Ecuación:** y = {mejor['Pendiente']:.4f}t "
                f"+ {mejor['Intercepto']:.4f}"
            )

            # ==================================================
            # CÁLCULO DE k, t50, t98, t95 y t90
            # ==================================================

            st.divider()
            st.subheader("5. Constante cinética y tiempos característicos")

            # c ya está convertido a la unidad de concentración seleccionada
            # y ordenado de acuerdo con el tiempo.
            C0 = float(c[0])
            k_calculada = float(mejor["k"])

            st.session_state["orden_cinetico_detectado"] = mejor["Orden"]
            st.session_state["R2_cinetico"] = float(mejor["R2"])
            st.session_state["k_cinetica"] = k_calculada
            st.session_state["C0_cinetica"] = C0
            st.session_state["unidad_k_cinetica"] = unidad_k
            st.session_state["unidad_t_cinetica"] = unidad_t
            st.session_state["unidad_c_cinetica"] = unidad_c
            st.session_state["modelos_cineticos"] = resumen.to_dict(
                orient="records"
            )

            if k_calculada <= 0 or C0 <= 0:
                st.error(
                    "No es posible calcular los tiempos. "
                    "La constante k y C0 deben ser positivas."
                )
            else:
                tiempos = calcular_tiempos_caracteristicos(
                    k_calculada, mejor["Orden"], C0
                )

                st.markdown("### Tiempos calculados")
                columnas = st.columns(4)

                for columna, (nombre, valor) in zip(columnas, tiempos.items()):
                    with columna:
                        st.metric(nombre, f"{valor:.4f} {unidad_t}")

                tabla_tiempos = pd.DataFrame({
                    "Parámetro": [
                        "Constante cinética k", "t50", "t98", "t95", "t90"
                    ],
                    "Resultado": [
                        k_calculada,
                        tiempos["t50"],
                        tiempos["t98"],
                        tiempos["t95"],
                        tiempos["t90"]
                    ],
                    "Unidad": [
                        unidad_k, unidad_t, unidad_t, unidad_t, unidad_t
                    ]
                })

                st.markdown("### Resumen de resultados cinéticos")
                st.dataframe(
                    tabla_tiempos.style.format({"Resultado": "{:.4g}"}),
                    use_container_width=True
                )

                csv_tiempos = tabla_tiempos.to_csv(
                    index=False
                ).encode("utf-8-sig")

                st.download_button(
                    "Descargar tiempos característicos",
                    data=csv_tiempos,
                    file_name="tiempos_caracteristicos.csv",
                    mime="text/csv",
                    key="descargar_tiempos_caracteristicos"
                )


# MODULO 2: ANALISIS DE ARRHENIUS

# ==================================================



st.divider()



st.title("🌡️ ANÁLISIS DE ARRHENIUS")



st.markdown("""

### 6. Determinación de la energía de activación



Ingrese las constantes cinéticas obtenidas a diferentes

temperaturas para determinar los parámetros de Arrhenius.

""")





st.write(

    "Ingresa las constantes cinéticas (k) obtenidas "

    "a diferentes temperaturas para calcular la energía "

    "de activación y el factor preexponencial."

)



# ------------------------------------------------------------

# 1. ECUACIONES

# ------------------------------------------------------------



st.subheader("Ecuaciones utilizadas")



st.latex(r"k = A e^{-\frac{E_a}{RT}}")



st.write("Ecuación linealizada:")



st.latex(

    r"\ln(k) = -\frac{E_a}{R}\left(\frac{1}{T}\right) + \ln(A)"

)



st.write(

    "Donde la pendiente corresponde a -Ea/R "

    "y el intercepto corresponde a ln(A)."

)



# ------------------------------------------------------------

# 2. INGRESO DE DATOS

# ------------------------------------------------------------



st.subheader("Ingreso de datos experimentales")



unidad_temperatura = st.selectbox(

    "Unidad de temperatura:",

    ["°C", "K"],

    key="unidad_temp_arrhenius"

)



datos_iniciales = pd.DataFrame({

    "Temperatura": [20.0, 30.0, 40.0],

    "k": [0.010, 0.020, 0.040]

})



datos_para_editor_arrhenius = datos_iniciales

datos_arrhenius = st.data_editor(

    datos_para_editor_arrhenius,

    num_rows="dynamic",

    use_container_width=True,

    key="editor_tabla_arrhenius"

)



st.caption(

    "Puedes modificar los valores de ejemplo, agregar filas "

    "o eliminar datos. Todas las constantes k deben ser positivas "

    "y estar expresadas en las mismas unidades."

)



# ------------------------------------------------------------

# 3. CÁLCULOS

# ------------------------------------------------------------



if st.button("CALCULAR ENERGÍA DE ACTIVACIÓN",

             key="calcular_arrhenius"):
    st.session_state["ejecutar_arrhenius"] = True

if st.session_state.get("ejecutar_arrhenius", False):



    datos = datos_arrhenius.copy()



    # Convertir los datos a valores numéricos

    datos["Temperatura"] = pd.to_numeric(

        datos["Temperatura"], errors="coerce"

    )



    datos["k"] = pd.to_numeric(

        datos["k"], errors="coerce"

    )



    # Eliminar filas vacías

    datos = datos.dropna(subset=["Temperatura", "k"])



    # Validaciones

    if len(datos) < 3:



        st.error(

            "Debes ingresar al menos tres pares de datos "

            "de temperatura y constante cinética."

        )



    elif not np.isfinite(datos[["Temperatura", "k"]].to_numpy()).all():



        st.error("Los datos deben ser valores numéricos finitos.")



    elif (datos["k"] <= 0).any():



        st.error("Todas las constantes cinéticas k deben ser positivas.")



    else:



        # ----------------------------------------------------

        # 4. CONVERSIÓN DE TEMPERATURA

        # ----------------------------------------------------



        if unidad_temperatura == "°C":

            temperatura_K = datos["Temperatura"] + 273.15

        else:

            temperatura_K = datos["Temperatura"]



        if (temperatura_K <= 0).any():



            st.error(

                "La temperatura en Kelvin debe ser mayor que cero."

            )



        elif temperatura_K.nunique() < 3:



            st.error(

                "Debes ingresar al menos tres temperaturas diferentes."

            )



        else:



            # ------------------------------------------------

            # 5. CÁLCULO DE 1/T Y LN(K)

            # ------------------------------------------------



            datos["Temperatura (K)"] = temperatura_K

            datos["1/T (K⁻¹)"] = 1 / temperatura_K

            datos["ln(k)"] = np.log(datos["k"])



            # ------------------------------------------------

            # 6. REGRESIÓN LINEAL

            # ------------------------------------------------



            x = datos["1/T (K⁻¹)"].to_numpy()

            y = datos["ln(k)"].to_numpy()



            pendiente, intercepto = np.polyfit(x, y, 1)



            y_estimado = pendiente * x + intercepto



            # Cálculo de R²

            ss_res = np.sum((y - y_estimado) ** 2)

            ss_tot = np.sum((y - np.mean(y)) ** 2)



            if ss_tot == 0:

                R2 = 0

            else:

                R2 = 1 - (ss_res / ss_tot)



            # ------------------------------------------------

            # 7. ENERGÍA DE ACTIVACIÓN Y FACTOR A

            # ------------------------------------------------



            R_ARRHENIUS = 8.314462618



            # Ea = -pendiente * R

            Ea = -pendiente * R_ARRHENIUS



            # A = e elevado al intercepto

            with np.errstate(over="ignore", under="ignore"):

                A = np.exp(intercepto)



            # Validar resultados

            if not np.isfinite(Ea) or not np.isfinite(A) or A <= 0:



                st.error(

                    "No fue posible calcular resultados válidos. "

                    "Revisa los valores experimentales."

                )



            else:

                st.session_state["Ea_arrhenius"] = Ea

                st.session_state["A_arrhenius"] = A

                st.session_state["R2_arrhenius"] = R2

                st.session_state["pendiente_arrhenius"] = float(pendiente)

                st.session_state["intercepto_arrhenius"] = float(intercepto)

                st.session_state["tabla_arrhenius_ia"] = datos[

    [

        "Temperatura (K)",

        "k",

        "1/T (K⁻¹)",

        "ln(k)"

    ]

].to_dict(orient="records")

                # --------------------------------------------

                # 8. TABLA DE RESULTADOS

                # --------------------------------------------



                st.subheader("Resultados experimentales")



                tabla_resultados = datos[

                    [

                        "Temperatura",

                        "Temperatura (K)",

                        "k",

                        "1/T (K⁻¹)",

                        "ln(k)"

                    ]

                ].copy()



                tabla_mostrar = tabla_resultados.copy()



                tabla_mostrar["Temperatura"] = (

                    tabla_mostrar["Temperatura"].map(lambda v: f"{v:.4f}")

                )



                tabla_mostrar["Temperatura (K)"] = (

                    tabla_mostrar["Temperatura (K)"].map(lambda v: f"{v:.4f}")

                )



                tabla_mostrar["k"] = (

                    tabla_mostrar["k"].map(lambda v: f"{v:.4e}")

                )



                tabla_mostrar["1/T (K⁻¹)"] = (

                    tabla_mostrar["1/T (K⁻¹)"].map(lambda v: f"{v:.8f}")

                )



                tabla_mostrar["ln(k)"] = (

                    tabla_mostrar["ln(k)"].map(lambda v: f"{v:.4f}")

                )



                st.dataframe(

                    tabla_mostrar,

                    use_container_width=True,

                    hide_index=True

                )



                # --------------------------------------------

                # 9. GRÁFICA DE ARRHENIUS

                # --------------------------------------------



                st.subheader("Gráfica de Arrhenius")



                x_linea = np.linspace(min(x), max(x), 100)

                y_linea = pendiente * x_linea + intercepto



                fig_arrhenius = go.Figure()



                fig_arrhenius.add_trace(

                    go.Scatter(

                        x=x,

                        y=y,

                        mode="lines+markers",

                        name="Datos experimentales",

                        marker=dict(size=10)

                    )

                )



                fig_arrhenius.add_trace(

                    go.Scatter(

                        x=x_linea,

                        y=y_linea,

                        mode="lines",

                        name="Regresión lineal"

                    )

                )



                fig_arrhenius.update_layout(

                    title="Gráfica de Arrhenius",

                    xaxis_title="1/T (K⁻¹)",

                    yaxis_title="ln(k)",

                    template="plotly_white"

                )



                st.plotly_chart(

                    fig_arrhenius,

                    use_container_width=True

                )



                # --------------------------------------------

                # 10. RESULTADOS CINÉTICOS

                # --------------------------------------------



                st.subheader("Parámetros cinéticos")



                col1, col2 = st.columns(2)



                with col1:

                    st.metric(

                        "Energía de activación (Ea)",

                        f"{Ea / 1000:.4f} kJ/mol"

                    )



                with col2:

                    st.metric(

                        "Factor preexponencial (A)",

                        f"{A:.4e}"

                    )



                col3, col4, col5 = st.columns(3)



                with col3:

                    st.metric("Pendiente", f"{pendiente:.4f}")



                with col4:

                    st.metric("Intercepto", f"{intercepto:.4f}")



                with col5:

                    st.metric("R²", f"{R2:.4f}")



                # --------------------------------------------

                # 11. ECUACIÓN LINEALIZADA

                # --------------------------------------------



                st.subheader("Ecuación linealizada obtenida")



                st.latex(

                    rf"\ln(k) = ({pendiente:.6f})"

                    rf"\left(\frac{{1}}{{T}}\right)"

                    rf" + ({intercepto:.6f})"

                )



                st.write(

                    f"**Energía de activación:** "

                    f"{Ea / 1000:.4f} kJ/mol"

                )



                st.write(

                    f"**Factor preexponencial:** {A:.4e}"

                )





                # ==================================================

                # DESCARGA DE RESULTADOS

                # ==================================================



                st.divider()



                st.subheader(

                    "11. Exportar resultados de Arrhenius"

                )



                csv_A = tabla_resultados.to_csv(

                    index=False

                ).encode("utf-8-sig")



                st.download_button(

                    "Descargar resultados de Arrhenius",

                    data=csv_A,

                    file_name="resultados_arrhenius.csv",

                    mime="text/csv",

                    key="descargar_arrhenius"

                )

# ============================================================

# PREDICCIÓN DE K Y CAMBIOS EN TIEMPOS DE VIDA ÚTIL

# ============================================================



st.divider()



st.header("PREDICCIÓN DE ESTABILIDAD A DIFERENTES TEMPERATURAS")



st.write(

    "Esta herramienta permite estimar cómo cambia la constante "

    "cinética y los tiempos de degradación del producto cuando "

    "se modifica la temperatura."

)



# ------------------------------------------------------------

# 1. VERIFICAR DATOS DE ARRHENIUS

# ------------------------------------------------------------



if (

    "Ea_arrhenius" not in st.session_state

    or "A_arrhenius" not in st.session_state

):



    st.warning(

        "Primero debes ejecutar el análisis de Arrhenius "

        "para obtener la energía de activación y el factor A."

    )



else:



    Ea_pred = st.session_state["Ea_arrhenius"]

    A_pred = st.session_state["A_arrhenius"]

    R_pred = 8.314462618



    # --------------------------------------------------------

    # 2. INGRESO DE TEMPERATURAS

    # --------------------------------------------------------



    st.subheader("Temperaturas de evaluación")



    unidad_pred = st.selectbox(

        "Unidad de temperatura:",

        ["°C", "K"],

        key="unidad_prediccion"

    )



    temperaturas_iniciales = pd.DataFrame({

        "Temperatura": [20.0, 30.0, 40.0, 50.0, 60.0]

    })



    temperaturas = st.data_editor(

    temperaturas_iniciales,

    num_rows="dynamic",

    use_container_width=True,

    key="tabla_temperaturas_prediccion"

)

# Concentración inicial tomada del análisis cinético

C0_inicial = float(

    st.session_state.get("C0_cinetica", 100.0)

)



unidad_c_pred = st.session_state.get(

    "unidad_c_cinetica",

    "unidad de concentración"

)



C0_pred = st.number_input(

    f"Concentración inicial (C₀) en {unidad_c_pred}:",

    min_value=0.000001,

    value=max(C0_inicial, 0.000001),

    step=1.0,

    key="concentracion_prediccion"

)



# Recuperar el orden detectado automáticamente



orden_detectado = st.session_state.get(

    "orden_cinetico_detectado"

)



if orden_detectado is None:



    st.warning(

        "Primero debes realizar el análisis cinético "

        "para identificar el orden de reacción."

    )



    orden_pred = None



else:



    orden_pred = orden_detectado



    st.success(

        f"Orden cinético utilizado en la predicción: {orden_pred}"

    )





    # --------------------------------------------------------

    # 4. BOTÓN DE CÁLCULO

    # --------------------------------------------------------



if st.button(

"CALCULAR PREDICCIÓN DE ESTABILIDAD",

key="boton_prediccion_estabilidad",

disabled=orden_pred is None

):
    st.session_state["ejecutar_prediccion_estabilidad"] = True

if st.session_state.get("ejecutar_prediccion_estabilidad", False) and orden_pred is not None:

            # ------------------------------------------------

            # 5. CONVERSIÓN A KELVIN

            # ------------------------------------------------



            if unidad_pred == "°C":



                temperaturas["Temperatura (K)"] = (

                    temperaturas["Temperatura"] + 273.15

                )



            else:



                temperaturas["Temperatura (K)"] = (

                    temperaturas["Temperatura"]

                )



            if (temperaturas["Temperatura (K)"] <= 0).any():



                st.error(

                    "Todas las temperaturas deben ser mayores "

                    "que cero Kelvin."

                )



            elif C0_pred <= 0:





                st.error(

                    "La concentración inicial debe ser positiva."

                )



            else:



                # --------------------------------------------

                # 6. PREDICCIÓN DE LA CONSTANTE CINÉTICA

                # --------------------------------------------



                resultados_pred = []



                for _, fila in temperaturas.iterrows():



                    T = fila["Temperatura (K)"]



                    k_pred = A_pred * np.exp(

                        -Ea_pred / (R_pred * T)

                    )



                    if not np.isfinite(k_pred) or k_pred <= 0:

                        continue



                    # ----------------------------------------

                    # 7. CÁLCULO DE TIEMPOS DE VIDA ÚTIL

                    # ----------------------------------------



                    tiempos_pred = calcular_tiempos_caracteristicos(

                    k_pred,

                    orden_pred,

                    C0_pred

)



                    t50 = tiempos_pred["t50"]

                    t98 = tiempos_pred["t98"]

                    t95 = tiempos_pred["t95"]

                    t90 = tiempos_pred["t90"]

                    resultados_pred.append({
                        "Temperatura (°C)": (
                            float(fila["Temperatura"])
                            if unidad_pred == "°C"
                            else float(T - 273.15)
                        ),
                        "Temperatura (K)": float(T),
                        "k estimada": float(k_pred),
                        "t50": float(t50),
                        "t98": float(t98),
                        "t95": float(t95),
                        "t90": float(t90)
                    })



                # --------------------------------------------

                # 8. MOSTRAR RESULTADOS

                # --------------------------------------------



                if len(resultados_pred) == 0:



                    st.error(

                        "No fue posible obtener resultados válidos."

                    )



                else:



                    tabla_pred = pd.DataFrame(resultados_pred)

                    # Guardar resultados para que no desaparezcan al actualizar la página

                    st.session_state["predicciones_ia"] = tabla_pred.to_dict(

    orient="records"

)



                    st.session_state["orden_ia"] = orden_pred

                    st.session_state["Ea_ia"] = Ea_pred

                    st.session_state["A_ia"] = A_pred

                    st.session_state["C0_ia"] = C0_pred



                    st.subheader(

                        "Resultados de predicción de estabilidad"

                    )



                    tabla_pred_mostrar = tabla_pred.copy()



                    for columna in tabla_pred_mostrar.columns:



                        tabla_pred_mostrar[columna] = (

                            tabla_pred_mostrar[columna].map(

                                lambda v: f"{v:.4e}"

                                if columna == "k estimada"

                                else f"{v:.4f}"

                            )

                        )



                    st.dataframe(

                        tabla_pred_mostrar,

                        use_container_width=True,

                        hide_index=True

                    )



                    st.caption(

                        "Los tiempos se expresan en las unidades "

                        "de tiempo correspondientes a la constante "

                        "cinética ingresada en el análisis."

                    )



                    # ----------------------------------------

                    # 9. GRÁFICA DE CONSTANTE CINÉTICA

                    # ----------------------------------------



                    st.subheader(

                        "Comportamiento de k según la temperatura"

                    )



                    fig_k = go.Figure()



                    fig_k.add_trace(

                        go.Scatter(

                            x=tabla_pred["Temperatura (°C)"],

                            y=tabla_pred["k estimada"],

                            mode="lines+markers",

                            name="k estimada"

                        )

                    )



                    fig_k.update_layout(

                        xaxis_title="Temperatura (°C)",

                        yaxis_title="Constante cinética (k)",

                        template="plotly_white"

                    )



                    st.plotly_chart(

                        fig_k,

                        use_container_width=True

                    )





                    # ----------------------------------------

                    # 7. EXPORTAR PREDICCIONES

                    # ----------------------------------------



                    st.subheader(

                        "Descargar predicciones"

                    )



                    csv_pred = tabla_pred.to_csv(

                        index=False

                    ).encode("utf-8-sig")



                    st.download_button(

                        label="Descargar predicciones (CSV)",

                        data=csv_pred,

                        file_name="predicciones_estabilidad.csv",

                        mime="text/csv",

                        key="descargar_predicciones"

                    )





# ==================================================

# 8. ANÁLISIS INTELIGENTE MEDIANTE IA

# ==================================================



if "predicciones_ia" in st.session_state:



    st.divider()

    st.subheader("✨ Análisis inteligente mediante IA")



    st.write(

        "La inteligencia artificial interpretará los resultados "

        "cinéticos y las predicciones de estabilidad."

    )



    if st.button(

        "✨ GENERAR CONCLUSIONES CON IA",

        key="boton_analisis_ia"

    ):



        with st.spinner(

            "La IA está analizando los resultados..."

        ):



            try:



                # ------------------------------------------

                # 1. RECUPERAR LAS PREDICCIONES

                # ------------------------------------------



                tabla_ia = pd.DataFrame(

                    st.session_state["predicciones_ia"]

                )



                datos_resultados = tabla_ia.to_string(

                    index=False

                )



                # ------------------------------------------

                # 2. RECUPERAR RESULTADOS CINÉTICOS

                # ------------------------------------------



                orden = st.session_state.get(

                    "orden_ia",

                    st.session_state.get(

                        "orden_cinetico_detectado",

                        "No disponible"

                    )

                )



                Ea = st.session_state.get("Ea_ia")

                A = st.session_state.get("A_ia")

                C0 = st.session_state.get("C0_ia")



                k_cinetica = st.session_state.get(

                    "k_cinetica",

                    "No disponible"

                )



                R2_cinetico = st.session_state.get(

                    "R2_cinetico",

                    "No disponible"

                )



                modelos_cineticos = st.session_state.get(

                    "modelos_cineticos",

                    []

                )



                tabla_modelos_ia = pd.DataFrame(

                    modelos_cineticos

                )



                # ------------------------------------------

                # 3. RECUPERAR RESULTADOS DE ARRHENIUS

                # ------------------------------------------



                R2_arrhenius = st.session_state.get(

                    "R2_arrhenius",

                    "No disponible"

                )



                pendiente_arrhenius = st.session_state.get(

                    "pendiente_arrhenius",

                    "No disponible"

                )



                intercepto_arrhenius = st.session_state.get(

                    "intercepto_arrhenius",

                    "No disponible"

                )



                tabla_arrhenius_ia = pd.DataFrame(

                    st.session_state.get(

                        "tabla_arrhenius_ia",

                        []

                    )

                )



                # ------------------------------------------

                # 4. RECUPERAR UNIDADES

                # ------------------------------------------



                unidad_k = st.session_state.get(

                    "unidad_k_cinetica",

                    "No especificada"

                )



                unidad_t = st.session_state.get(

                    "unidad_t_cinetica",

                    "No especificada"

                )



                unidad_c = st.session_state.get(

                    "unidad_c_cinetica",

                    "No especificada"

                )



                # ------------------------------------------

                # 5. PREPARAR INFORMACIÓN PARA LA IA

                # ------------------------------------------



                tabla_modelos_texto = (

                    tabla_modelos_ia.to_string(index=False)

                    if not tabla_modelos_ia.empty

                    else "No disponible"

                )



                tabla_arrhenius_texto = (

                    tabla_arrhenius_ia.to_string(index=False)

                    if not tabla_arrhenius_ia.empty

                    else "No disponible"

                )



                Ea_texto = (

                    f"{float(Ea) / 1000:.6f} kJ/mol"

                    if isinstance(Ea, (int, float, np.number))

                    else "No disponible"

                )



                A_texto = (

                    f"{float(A):.8e}"

                    if isinstance(A, (int, float, np.number))

                    else "No disponible"

                )



                # ------------------------------------------

                # 6. PROMPT CIENTÍFICO

                # ------------------------------------------



                prompt = f"""

Actúa como un especialista en cinética química,

estabilidad farmacéutica y análisis de datos.



Elabora un INFORME CIENTÍFICO utilizando exclusivamente

los resultados proporcionados por la aplicación.



No inventes datos ni modifiques los resultados calculados.



==================================================

1. RESULTADOS DEL ANÁLISIS CINÉTICO

==================================================



Orden de reacción seleccionado:

{orden}



R2 del modelo seleccionado:

{R2_cinetico}



Comparación de modelos cinéticos:

{tabla_modelos_texto}



Constante cinética experimental:

{k_cinetica}



Unidades de k:

{unidad_k}



Unidades de concentración:

{unidad_c}



Unidades de tiempo:

{unidad_t}



==================================================

2. RESULTADOS DE ARRHENIUS

==================================================



Energía de activación:

{Ea_texto}



Factor preexponencial:

{A_texto}



R2 de Arrhenius:

{R2_arrhenius}



Pendiente:

{pendiente_arrhenius}



Intercepto:

{intercepto_arrhenius}



Datos experimentales:

{tabla_arrhenius_texto}



==================================================

3. PREDICCIÓN DE ESTABILIDAD

==================================================



Orden cinético utilizado:

{orden}



Concentración inicial:

{C0} {unidad_c}



Resultados de las predicciones:

{datos_resultados}



==================================================

4. INSTRUCCIONES CIENTÍFICAS OBLIGATORIAS

==================================================



A. ORDEN CINÉTICO:



- Explica por qué fue seleccionado el orden de reacción.

- Compara los R2 de orden cero, uno y dos e identifica

  cuál presenta el mejor ajuste.

- Presenta la diferencia de R2 entre los dos mejores

  modelos como criterio de decisión. Si esa diferencia es

  menor de 0.01, indica que la decisión no es concluyente.

- No uses la expresión "estadísticamente significativo":

  no se realizó ninguna prueba estadística.

- No afirmes que un R2 alto demuestra por sí solo

  la validez absoluta del mecanismo.

- Recuerda que los R2 corresponden a variables

  transformadas diferentes y deben interpretarse

  con precaución.



B. ENERGÍA DE ACTIVACIÓN:



- Interpreta la energía de activación calculada y su

  relación con la sensibilidad térmica, apoyándote en

  cómo cambian k y los tiempos (columnas tx/tx(ref))

  en los resultados proporcionados.

- No clasifiques la Ea como baja, moderada o alta.

- No cites rangos típicos ni valores de la literatura:

  no fueron proporcionados.

- No inventes mecanismos de degradación (por ejemplo,

  oxidación o hidrólisis).



C. CONSTANTE CINÉTICA Y ARRHENIUS:



- Explica cómo cambia k con la temperatura usando solo

  los valores de la tabla proporcionada.

- Interpreta la pendiente (igual a -Ea/R) y el

  intercepto (igual a ln A).

- Explica el significado del R2 de Arrhenius como

  medida del ajuste lineal de ln(k) frente a 1/T.

  Advierte que, con pocas temperaturas ensayadas, el

  ajuste tiene pocos grados de libertad (con tres

  temperaturas, solo uno). No digas que describe la

  dependencia térmica "con precisión".

- Recuerda que A tiene las mismas unidades que k.

- No confundas las unidades de k entre órdenes cinéticos.



D. TIEMPOS CARACTERÍSTICOS:



IMPORTANTE: t50, t98, t95 y t90 representan

el tiempo necesario para conservar, respectivamente,

el 50 %, 98 %, 95 % y 90 % de la concentración inicial.



Por tanto:

- t50: 50 % de concentración restante.

- t98: 98 % de concentración restante.

- t95: 95 % de concentración restante.

- t90: 90 % de concentración restante.



No interpretes t98 como 98 % de degradación.



La relación cronológica esperada es:



t98 < t95 < t90 < t50



para una degradación con k positiva y bajo estas

definiciones de porcentaje restante.



- Compara los cuatro tiempos y explica cómo cambian

  al aumentar la temperatura.

- Con C0 fija, todos los tiempos son proporcionales a 1/k.

  Por eso los cocientes entre ellos (por ejemplo t50/t90)

  no cambian con la temperatura: no afirmes que la

  diferencia relativa entre tiempos aumenta o disminuye.

  Solo la diferencia absoluta se reduce al subir la

  temperatura, porque todos los tiempos se acortan.

- Describe el efecto térmico con las columnas tx/tx(ref).

- No definas umbrales de temperatura (por ejemplo,

  "por encima de X °C la estabilidad cae bruscamente"):

  el modelo de Arrhenius es continuo.

- Si encuentras valores que contradicen estas relaciones,

  informa de la inconsistencia.



E. ESTABILIDAD:



- Explica el efecto de la temperatura sobre la estabilidad.

- Identifica las temperaturas con mayor y menor estabilidad

  utilizando los resultados proporcionados.

- No presentes los tiempos calculados como una vida útil

  oficialmente establecida.

- Explica que t90 puede utilizarse como referencia

  cuando el criterio aplicable sea conservar al menos

  el 90 % de la concentración inicial.

- No recomiendes envases, protección contra la luz o la

  humedad ni medidas de almacenamiento específicas que no

  se deriven directamente de los datos proporcionados.



F. REVISIÓN DE CALIDAD:



- Detecta valores negativos, nulos o no válidos.

- Identifica posibles inconsistencias entre unidades.

- Comprueba el comportamiento de k con la temperatura.

- Señala si la energía de activación o el ajuste requieren

  revisión.

- Si la k experimental no es compatible con las k de

  Arrhenius y no se indicó la temperatura del ensayo,

  indica que la coherencia entre ambas no puede verificarse.

- Diferencia los datos experimentales de las predicciones.

  Señala como extrapolación toda temperatura marcada con

  "Sí" en la columna Extrapolación.



==================================================

5. ESTRUCTURA DEL INFORME

==================================================



Redacta las conclusiones con estos apartados:



1. Determinación e interpretación del orden cinético.

2. Interpretación de la energía de activación.

3. Comportamiento de k con la temperatura.

4. Análisis comparativo de t50, t98, t95 y t90.

5. Efecto de la temperatura sobre la estabilidad.

6. Limitaciones del análisis.

7. Conclusiones generales y recomendaciones.



Condiciones por apartado:

- Apartado 6: incluye solo limitaciones verificables con

  los datos proporcionados (número de puntos, extrapolación,

  un único orden cinético supuesto, consistencia de unidades).

  No enumeres factores que no se midieron (humedad, luz, pH)

  como si fueran hallazgos.

- Apartado 7: las recomendaciones se limitan a ampliar el

  número de temperaturas y réplicas, validar las predicciones

  con estudios reales y confirmar el criterio de aceptación

  aplicable.



==================================================

6. REGLAS DE REDACCIÓN

==================================================



- Escribe en español académico y científico.

- Utiliza lenguaje técnico, pero comprensible.

- Explica los resultados, no te limites a repetir tablas.

- Utiliza exclusivamente los valores proporcionados:

  no calcules valores nuevos y no inventes temperaturas,

  unidades ni concentraciones.

- No menciones medicamentos específicos; usa "el producto"

  en lugar de "fármaco".

- No afirmes que un producto es estable o inestable

  sin considerar los criterios de aceptación aplicables.

- Si faltan datos, indícalo expresamente.

- No presentes conclusiones contradictorias.

- Adapta todo el informe al orden cinético detectado.

- Las conclusiones deben corresponder a los resultados

  actuales y no a análisis anteriores.

- Escribe las fórmulas en texto plano, por ejemplo

  k = A * exp(-Ea / (R * T)). No uses corchetes ni LaTeX.

- Máximo 700 palabras. Termina siempre con una frase

  completa; si falta espacio, resume.

  - No asignes ninguna temperatura a la k experimental: la temperatura del ensayo no fue indicada.
- Son extrapolaciones SOLO las temperaturas marcadas "Sí" en la columna Extrapolación.
- Las columnas tx/tx(ref) son idénticas para t50, t98, t95 y t90: no afirmes que la reducción relativa difiere entre tiempos.
- No uses "sensibilidad moderada", "alta" ni "baja".
- Usa "tiempo para conservar x %" en lugar de "tiempo de retención".
No uses sensibilidad moderada, alta ni baja” y “no cites ningún cociente distinto de los de HECHOS VERIFICADOS

"""



                # ------------------------------------------

                # 7. GENERAR INFORME CON IA

                # ------------------------------------------



                respuesta_ia = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[

                        {

                            "role": "system",

                            "content": (

                                "Eres un especialista en cinética "

                                "química, estabilidad farmacéutica "

                                "y análisis de datos. Redactas "

                                "informes científicos rigurosos."

                            )

                        },

                        {

                            "role": "user",

                            "content": prompt

                        }

                    ],

                    temperature=0.2,
                    max_completion_tokens=6000,
                    reasoning_effort="low",
                    include_reasoning=False,
                    stream=False
                )

                # Extraer el texto y diagnosticar respuestas vacías.
                if not respuesta_ia.choices:
                    raise RuntimeError("Groq devolvió una respuesta sin opciones (choices).")

                eleccion = respuesta_ia.choices[0]
                mensaje = eleccion.message
                informe_ia = mensaje.content

                # Normalizar respuestas que puedan venir como texto vacío o espacios.
                if isinstance(informe_ia, str):
                    informe_ia = informe_ia.strip()

                if informe_ia:
                    st.session_state["informe_conclusiones_ia"] = informe_ia
                    st.success("¡Conclusiones generadas correctamente!")
                else:
                    motivo = getattr(eleccion, "finish_reason", None)
                    uso = getattr(respuesta_ia, "usage", None)
                    st.warning(
                        "Groq respondió, pero no entregó texto en el campo content. "
                        f"Motivo de finalización: {motivo or 'no informado'}. "
                        "Vuelve a intentarlo; si persiste, comparte este diagnóstico."
                    )
                    if uso is not None:
                        st.caption(f"Diagnóstico de uso de tokens: {uso}")
                    st.caption(
                        "La solicitud se configuró con razonamiento de bajo esfuerzo "
                        "y 6000 tokens máximos para dejar más espacio al informe."
                    )



            except Exception as error:



                st.error(

                    f"Error al generar las conclusiones: {error}"

                )



                st.write("Detalles técnicos del error:")

                st.exception(error)





    # Mantener el informe visible en cada rerun de Streamlit.
    if st.session_state.get("informe_conclusiones_ia"):
        st.markdown("### Informe de estabilidad")
        st.markdown(st.session_state["informe_conclusiones_ia"])


# ==================================================

# INFORMACION FINAL

# ==================================================



st.divider()



with st.expander("Ecuaciones utilizadas"):



    st.markdown("""

    **Orden cero**



    C = C0 - k0·t



    **Orden uno**



    ln(C) = ln(C0) - k1·t



    **Orden dos**



    1/C = 1/C0 + k2·t



    La selección del modelo se realiza comparando

    los coeficientes de determinación R2.

    """)



st.caption(

    "Análisis cinético mediante el método integral. "

    "Las conversiones de concentración corresponden "

    "a unidades de masa por volumen."

)