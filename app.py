import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="Dashboard de Proyectos e Innovación", layout="wide", page_icon="📊")

# Estilos CSS personalizados para tarjetas de socios
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .socio-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #2e7d32;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .socio-title {
        font-size: 18px;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 10px;
    }
    .socio-detail {
        font-size: 14px;
        color: #4b5563;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estados en session_state
if 'df_bd' not in st.session_state:
    st.session_state.df_bd = pd.DataFrame()
if 'dict_inc' not in st.session_state:
    st.session_state.dict_inc = {}
if 'dict_pac' not in st.session_state:
    st.session_state.dict_pac = {}

archivos_en_raiz = os.listdir('.') if os.path.exists('.') else []

# 1. Cargar BD Innovación
if len(st.session_state.df_bd) == 0:
    try:
        bd_files = [f for f in archivos_en_raiz if 'INNOVACION' in f.upper() and f.endswith('.xlsx')]
        if bd_files:
            st.session_state.df_bd = pd.read_excel(bd_files[0], sheet_name=0)
            st.session_state.df_bd.columns = [str(c).strip() for c in st.session_state.df_bd.columns]
    except Exception:
        pass

# 2. Cargar Incubadoras
if not st.session_state.dict_inc:
    try:
        inc_files = [f for f in archivos_en_raiz if 'INC' in f.upper() and f.endswith('.xlsx')]
        if inc_files:
            file_inc = inc_files[0]
            xls_inc = pd.ExcelFile(file_inc)
            dict_inc = {sh: pd.read_excel(file_inc, sheet_name=sh) for sh in xls_inc.sheet_names}
            for sh in dict_inc:
                dict_inc[sh].columns = [str(c).strip() for c in dict_inc[sh].columns]
            if 'Incubadoras' in dict_inc and 'ESTADO DEL PROYECTO' in dict_inc['Incubadoras'].columns:
                dict_inc['Incubadoras'] = dict_inc['Incubadoras'][
                    ~dict_inc['Incubadoras']['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
                ]
            st.session_state.dict_inc = dict_inc
    except Exception:
        pass

# 3. Cargar Proyectos PAC (Filtrando estrictamente Borrador y Cancelada)
if not st.session_state.dict_pac:
    try:
        pac_files = [f for f in archivos_en_raiz if 'PAC' in f.upper() and f.endswith('.xlsx')]
        if not pac_files:
            pac_files = [f for f in archivos_en_raiz if f.endswith('.xlsx') and f not in inc_files]

        if pac_files:
            file_pac = pac_files[0]
            xls_pac = pd.ExcelFile(file_pac)
            dict_pac = {sh: pd.read_excel(file_pac, sheet_name=sh) for sh in xls_pac.sheet_names}
            for sh in dict_pac:
                dict_pac[sh].columns = [str(c).strip() for c in dict_pac[sh].columns]
            
            # Ubicar la hoja de Proyectos
            hoja_proyectos = 'Proyectos' if 'Proyectos' in dict_pac else list(dict_pac.keys())[0]
            
            if hoja_proyectos in dict_pac and 'ESTADO DEL PROYECTO' in dict_pac[hoja_proyectos].columns:
                df_proy_pac = dict_pac[hoja_proyectos]
                # EXCLUSIÓN ESTRICTA DE BORRADOR Y CANCELADA
                df_proy_limpio = df_proy_pac[
                    ~df_proy_pac['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
                ].copy()
                dict_pac[hoja_proyectos] = df_proy_limpio
                
                ids_validos = df_proy_limpio['ID'].dropna().tolist() if 'ID' in df_proy_limpio.columns else []
                if ids_validos:
                    for sh in dict_pac:
                        if sh != hoja_proyectos and 'ID' in dict_pac[sh].columns:
                            dict_pac[sh] = dict_pac[sh][dict_pac[sh]['ID'].isin(ids_validos)]
                            
            st.session_state.dict_pac = dict_pac
    except Exception as e:
        pass

# Sidebar: Navegación Principal
st.sidebar.header("🎛️ Panel de Control")
app_mode = st.sidebar.selectbox(
    "Navegación", 
    ["📊 Dashboard Principal", "🤝 Socios Comunitarios", "📁 Subir y Gestionar Nueva Información"]
)

# -------------------------------------------------------------
# OPCIÓN 1: DASHBOARD PRINCIPAL
# -------------------------------------------------------------
if app_mode == "📊 Dashboard Principal":
    dataset_choice = st.sidebar.radio("Seleccionar Base de Datos:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    
    st.title("🚀 Dashboard de Iniciativas e Incubación de Proyectos")

    if dataset_choice == "BD Innovación":
        df_bd = st.session_state.df_bd
        st.subheader("📊 Indicadores Clave - BD Innovación")
        if not df_bd.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Iniciativas", len(df_bd))
            col2.metric("En Ejecución", len(df_bd[df_bd['Estado'].str.lower() == 'en ejecución']) if 'Estado' in df_bd.columns else 0)
            col3.metric("Finalizados", len(df_bd[df_bd['Estado'].str.lower() == 'finalizado']) if 'Estado' in df_bd.columns else 0)
            col4.metric("Estudiantes Totales", int(df_bd['Estudiantes'].sum()) if 'Estudiantes' in df_bd.columns else 0)
            st.markdown("---")
            st.dataframe(df_bd, use_container_width=True)
        else:
            st.info("No hay datos cargados para BD Innovación.")

    elif dataset_choice == "Reporte General Incubadoras":
        st.subheader("📊 Indicadores Clave - Incubadoras (Sin Borradores ni Canceladas)")
        dict_inc = st.session_state.get('dict_inc', {})
        if dict_inc:
            hoja_activa = st.selectbox("Seleccionar hoja a visualizar:", list(dict_inc.keys()))
            st.dataframe(dict_inc[hoja_activa], use_container_width=True)
        else:
            st.info("No hay datos cargados para Incubadoras.")

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC (Sin Borradores ni Canceladas)")
        dict_pac = st.session_state.get('dict_pac', {})
        hoja_proyectos = 'Proyectos' if 'Proyectos' in dict_pac else (list(dict_pac.keys())[0] if dict_pac else None)
        
        if hoja_proyectos and hoja_proyectos in dict_pac:
            df_proyectos_pac = dict_pac[hoja_proyectos]
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Proyectos PAC Válidos", len(df_proyectos_pac))
            col2.metric("Estudiantes Participantes", int(df_proyectos_pac['ESTUDIANTES PARTICIPANTES'].sum()) if 'ESTUDIANTES PARTICIPANTES' in df_proyectos_pac.columns else 0)
            col3.metric("Beneficiarios Totales", int(df_proyectos_pac['BENEFICIARIOS'].sum()) if 'BENEFICIARIOS' in df_proyectos_pac.columns else 0)
            
            st.markdown("---")
            st.subheader("📈 Cantidad de Proyectos PAC por Facultad Líder")
            if 'FACULTAD LÍDER' in df_proyectos_pac.columns:
                df_fac_pac = df_proyectos_pac['FACULTAD LÍDER'].value_counts().reset_index()
                df_fac_pac.columns = ['Facultad', 'Cantidad de Proyectos']
                df_fac_pac = df_fac_pac.sort_values(by='Cantidad de Proyectos', ascending=True)
                
                if not df_fac_pac.empty:
                    fig_pac = px.bar(
                        df_fac_pac,
                        x='Cantidad de Proyectos',
                        y='Facultad',
                        orientation='h',
                        title="Proyectos PAC Activos por Facultad Líder",
                        text='Cantidad de Proyectos',
                        color='Cantidad de Proyectos',
                        color_continuous_scale='Blues'
                    )
                    fig_pac.update_layout(xaxis_title="Número de Proyectos", yaxis_title="Facultad")
                    st.plotly_chart(fig_pac, use_container_width=True)
            
            st.markdown("---")
            hoja_activa_pac = st.selectbox("Seleccionar hoja de detalle PAC a visualizar:", list(dict_pac.keys()))
            st.dataframe(dict_pac[hoja_activa_pac], use_container_width=True)
        else:
            st.info("No se encontró el archivo de Proyectos PAC en el repositorio.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios y Gráfico de Facultades")
    st.markdown("Cruce automatizado entre la hoja **Organizaciones** y la hoja principal **Proyectos** (filtrando borradores y canceladas).")
    
    tipo_fuente = st.radio("Seleccionar archivo origen:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    dict_actual = st.session_state.get('dict_pac', {}) if tipo_fuente == "Proyectos PAC" else st.session_state.get('dict_inc', {})
    
    if 'Organizaciones' in dict_actual:
        df_org = dict_actual['Organizaciones'].copy()
        hoja_ppal_nombre = 'Proyectos' if 'Proyectos' in dict_actual else list(dict_actual.keys())[0]
        df_ppal = dict_actual[hoja_ppal_nombre].copy()
        
        df_org = df_org.dropna(subset=['ORGANIZACIÓN']) if 'ORGANIZACIÓN' in df_org.columns else df_org
        
        if not df_org.empty and 'ID' in df_org.columns and 'ID' in df_ppal.columns:
            df_merged = pd.merge(
                df_org,
                df_ppal[['ID', 'FACULTAD LÍDER', 'TIPO DE INICIATIVA'] if 'FACULTAD LÍDER' in df_ppal.columns else ['ID']],
                on='ID',
                how='left',
                suffixes=('', '_ppal')
            )
            
            st.subheader("📈 Distribución de Socios Comunitarios por Facultad")
            if 'FACULTAD LÍDER' in df_merged.columns and 'ORGANIZACIÓN' in df_merged.columns:
                df_grafico = df_merged.dropna(subset=['FACULTAD LÍDER', 'ORGANIZACIÓN']).groupby('FACULTAD LÍDER')['ORGANIZACIÓN'].nunique().reset_index()
                df_grafico.columns = ['Facultad', 'Cantidad de Socios']
                df_grafico = df_grafico.sort_values(by='Cantidad de Socios', ascending=True)
                
                if not df_grafico.empty:
                    fig = px.bar(
                        df_grafico, 
                        x='Cantidad de Socios', 
                        y='Facultad', 
                        orientation='h',
                        title=f"Cantidad de Socios Comunitarios Únicos por Facultad ({tipo_fuente})",
                        text='Cantidad de Socios',
                        color='Cantidad de Socios',
                        color_continuous_scale='Greens'
                    )
                    fig.update_layout(xaxis_title="Cantidad de Socios Comunitarios", yaxis_title="Facultad Líder")
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🏢 Detalle por Socio Comunitario")
            
            socios_agrupados = df_merged.groupby('ORGANIZACIÓN').agg(
                total_convenios=('ORGANIZACIÓN', 'count'),
                codigos_ids=('ID', lambda x: ", ".join(x.dropna().astype(str).unique())),
                facultades=('FACULTAD LÍDER', lambda x: ", ".join(x.dropna().astype(str).unique())) if 'FACULTAD LÍDER' in df_merged.columns else ('ID', lambda x: "N/A"),
                tipos=('TIPO DE INICIATIVA', lambda x: ", ".join(x.dropna().astype(str).unique())) if 'TIPO DE INICIATIVA' in df_merged.columns else ('ID', lambda x: "N/A")
            ).reset_index()
            
            cols = st.columns(2)
            for idx, row in socios_agrupados.iterrows():
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="socio-card">
                            <div class="socio-title">🏢 {row['ORGANIZACIÓN']}</div>
                            <div class="socio-detail"><b>Cantidad de Proyectos / Convenios:</b> {row['total_convenios']} (IDs: {row['codigos_ids']})</div>
                            <div class="socio-detail"><b>Facultad Involucrada:</b> {row['facultades']}</div>
                            <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No se encontró coincidencia por ID entre Organizaciones y Proyectos.")
    else:
        st.info(f"El archivo seleccionado no contiene una hoja 'Organizaciones'.")

# -------------------------------------------------------------
# OPCIÓN 3: SUBIR Y GESTIONAR NUEVA INFORMACIÓN
# -------------------------------------------------------------
else:
    st.title("📂 Gestión, Limpieza y Actualización de Archivos")
    st.markdown("Sube nuevos archivos Excel para actualizar las bases de datos del sistema.")

    dataset_choice = st.sidebar.radio("Seleccionar Base de Datos a Actualizar:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    uploaded_file = st.file_uploader("Selecciona un archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            xls_subido = pd.ExcelFile(uploaded_file)
            st.success(f"¡Archivo detectado! Hojas disponibles: {xls_subido.sheet_names}")
            
            if st.button("Procesar y Guardar con Limpieza Automática"):
                dict_cargado = {sh: pd.read_excel(uploaded_file, sheet_name=sh) for sh in xls_subido.sheet_names}
                for sh in dict_cargado:
                    dict_cargado[sh].columns = [str(c).strip() for c in dict_cargado[sh].columns]
                
                hoja_p = 'Proyectos' if 'Proyectos' in dict_cargado else list(dict_cargado.keys())[0]
                if hoja_p in dict_cargado and 'ESTADO DEL PROYECTO' in dict_cargado[hoja_p].columns:
                    df_p = dict_cargado[hoja_p]
                    # Aplicar exclusión de Borrador y Cancelada
                    df_p = df_p[~df_p['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])].copy()
                    dict_cargado[hoja_p] = df_p
                    ids_val = df_p['ID'].dropna().tolist() if 'ID' in df_p.columns else []
                    if ids_val:
                        for sh in dict_cargado:
                            if sh != hoja_p and 'ID' in dict_cargado[sh].columns:
                                dict_cargado[sh] = dict_cargado[sh][dict_cargado[sh]['ID'].isin(ids_val)]

                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = list(dict_cargado.values())[0]
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.dict_inc = dict_cargado
                else:
                    st.session_state.dict_pac = dict_cargado
                    
                st.success("¡Base de datos procesada y guardada filtrando Borradores y Canceladas!")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
