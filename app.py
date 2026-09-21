import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="Dashboard de Proyectos e Innovación", layout="wide", page_icon="📊")

# Estilos CSS personalizados para tarjetas
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
if 'df_pac' not in st.session_state:
    st.session_state.df_pac = pd.DataFrame()

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

# 2. Cargar Incubadoras (Filtrando Borrador y Cancelada)
if not st.session_state.dict_inc:
    try:
        inc_files = [f for f in archivos_en_raiz if 'INC' in f.upper() and f.endswith('.xlsx')]
        if inc_files:
            file_inc = inc_files[0]
            xls_inc = pd.ExcelFile(file_inc)
            dict_inc = {sh: pd.read_excel(file_inc, sheet_name=sh) for sh in xls_inc.sheet_names}
            for sh in dict_inc:
                dict_inc[sh].columns = [str(c).strip() for c in dict_inc[sh].columns]
            
            hoja_inc = 'Incubadoras' if 'Incubadoras' in dict_inc else list(dict_inc.keys())[0]
            if hoja_inc in dict_inc and 'ESTADO DEL PROYECTO' in dict_inc[hoja_inc].columns:
                dict_inc[hoja_inc] = dict_inc[hoja_inc][
                    ~dict_inc[hoja_inc]['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
                ]
            st.session_state.dict_inc = dict_inc
    except Exception:
        pass

# 3. Cargar Proyectos PAC (Desde reporte_general_PAC_limpio.xlsx, filtrando Borrador y Cancelada)
if st.session_state.df_pac.empty:
    try:
        pac_file = 'reporte_general_PAC_limpio.xlsx' if os.path.exists('reporte_general_PAC_limpio.xlsx') else next((f for f in archivos_en_raiz if 'PAC' in f.upper() and f.endswith('.xlsx')), None)
        
        if pac_file:
            df_pac_raw = pd.read_excel(pac_file, sheet_name=0)
            df_pac_raw.columns = [str(c).strip() for c in df_pac_raw.columns]
            
            if 'ESTADO DEL PROYECTO' in df_pac_raw.columns:
                df_pac_limpio = df_pac_raw[
                    ~df_pac_raw['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
                ].copy()
                st.session_state.df_pac = df_pac_limpio
            else:
                st.session_state.df_pac = df_pac_raw
    except Exception:
        pass

# Sidebar: Navegación Principal
st.sidebar.header("🎛️ Panel de Control")
app_mode = st.sidebar.selectbox(
    "Navegación", 
    [
        "📊 Dashboard Principal", 
        "🤝 Socios Comunitarios", 
        "📁 Gestión y Actualización de Archivos"
    ]
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
            st.subheader("📈 Cantidad de Iniciativas por Facultad (BD Innovación)")
            
            col_fac_bd = next((c for c in df_bd.columns if 'facultad' in c.lower()), None)
            if col_fac_bd:
                df_fac_bd = df_bd[col_fac_bd].value_counts().reset_index()
                df_fac_bd.columns = ['Facultad', 'Cantidad de Iniciativas']
                df_fac_bd = df_fac_bd.sort_values(by='Cantidad de Iniciativas', ascending=True)
                
                if not df_fac_bd.empty:
                    fig_bd = px.bar(
                        df_fac_bd,
                        x='Cantidad de Iniciativas',
                        y='Facultad',
                        orientation='h',
                        title="Iniciativas de Innovación por Facultad",
                        text='Cantidad de Iniciativas',
                        color='Cantidad de Iniciativas',
                        color_continuous_scale='Purples'
                    )
                    fig_bd.update_layout(xaxis_title="Número de Iniciativas", yaxis_title="Facultad")
                    st.plotly_chart(fig_bd, use_container_width=True)
            else:
                st.info("No se encontró una columna de facultad en BD Innovación.")

            st.markdown("---")
            st.subheader("📋 Detalle de Iniciativas de Innovación")
            st.dataframe(df_bd, use_container_width=True)
        else:
            st.info("No hay datos cargados para BD Innovación.")

    elif dataset_choice == "Reporte General Incubadoras":
        st.subheader("📊 Indicadores Clave - Incubadoras (Sin Borradores ni Canceladas)")
        dict_inc = st.session_state.get('dict_inc', {})
        
        if dict_inc:
            hoja_inc_nombre = 'Incubadoras' if 'Incubadoras' in dict_inc else list(dict_inc.keys())[0]
            df_inc_activa = dict_inc[hoja_inc_nombre]
            
            total_proyectos_inc = len(df_inc_activa)
            col_fac_inc = next((c for c in df_inc_activa.columns if 'facultad' in c.lower()), None)
            total_facultades_inc = df_inc_activa[col_fac_inc].nunique() if col_fac_inc else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("📁 Total de Proyectos (Incubadoras)", total_proyectos_inc)
            col_m2.metric("🏛️ Total de Facultades", total_facultades_inc)
            
            st.markdown("---")
            st.subheader("📈 Cantidad de Proyectos por Facultad Líder (Incubadoras)")
            
            if col_fac_inc:
                df_fac_inc = df_inc_activa[col_fac_inc].value_counts().reset_index()
                df_fac_inc.columns = ['Facultad', 'Cantidad de Proyectos']
                df_fac_inc = df_fac_inc.sort_values(by='Cantidad de Proyectos', ascending=True)
                
                if not df_fac_inc.empty:
                    fig_inc = px.bar(
                        df_fac_inc,
                        x='Cantidad de Proyectos',
                        y='Facultad',
                        orientation='h',
                        title="Proyectos de Incubación por Facultad Líder",
                        text='Cantidad de Proyectos',
                        color='Cantidad de Proyectos',
                        color_continuous_scale='Oranges'
                    )
                    fig_inc.update_layout(xaxis_title="Número de Proyectos", yaxis_title="Facultad")
                    st.plotly_chart(fig_inc, use_container_width=True)
            else:
                st.info("No se encontró una columna de facultad en esta hoja de Incubadoras.")

            st.markdown("---")
            st.subheader("📋 Detalle de Incubadoras")
            st.dataframe(df_inc_activa, use_container_width=True)
        else:
            st.info("No hay datos cargados para Incubadoras.")

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC (Sin Borradores ni Canceladas)")
        df_pac = st.session_state.get('df_pac', pd.DataFrame())
        
        if not df_pac.empty:
            # Si hay proyectos repetidos por ID o por organización, contamos proyectos únicos por ID
            total_proyectos_pac = df_pac['ID'].nunique() if 'ID' in df_pac.columns else len(df_pac)
            total_estudiantes = int(df_pac['ESTUDIANTES PARTICIPANTES'].sum()) if 'ESTUDIANTES PARTICIPANTES' in df_pac.columns else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Total Proyectos PAC Válidos", total_proyectos_pac)
            col2.metric("Estudiantes Participantes", total_estudiantes)
            
            st.markdown("---")
            st.subheader("📈 Cantidad de Proyectos PAC por Facultad Líder")
            if 'FACULTAD LÍDER' in df_pac.columns:
                # Agrupamos por ID y Facultad para contar cada proyecto una sola vez
                df_proyectos_unicos = df_pac.drop_duplicates(subset=['ID']) if 'ID' in df_pac.columns else df_pac
                df_fac_pac = df_proyectos_unicos['FACULTAD LÍDER'].value_counts().reset_index()
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
            st.subheader("📋 Detalle de Proyectos PAC")
            st.dataframe(df_pac, use_container_width=True)
        else:
            st.info("No se encontró el archivo 'reporte_general_PAC_limpio.xlsx' en el repositorio.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios")
    st.markdown("Extracción directa de organizaciones y facultades desde la nueva estructura (filtrando borradores y canceladas).")
    
    tipo_fuente = st.radio("Seleccionar archivo origen:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    if tipo_fuente == "Proyectos PAC":
        df_src = st.session_state.get('df_pac', pd.DataFrame())
    else:
        dict_inc = st.session_state.get('dict_inc', {})
        hoja_inc = 'Incubadoras' if 'Incubadoras' in dict_inc else (list(dict_inc.keys())[0] if dict_inc else None)
        df_src = dict_inc[hoja_inc] if hoja_inc else pd.DataFrame()
    
    if not df_src.empty:
        col_org = next((c for c in df_src.columns if 'organización' in c.lower() or 'organizacion' in c.lower()), 'ORGANIZACIÓN')
        col_fac = next((c for c in df_src.columns if 'facultad' in c.lower()), 'FACULTAD LÍDER')
        col_id = next((c for c in df_src.columns if 'id' in c.lower()), 'ID')
        col_tipo = next((c for c in df_src.columns if 'tipo' in c.lower() or 'iniciativa' in c.lower()), None)
        
        if col_org in df_src.columns and col_fac in df_src.columns:
            df_org_clean = df_src.dropna(subset=[col_org]).copy()
            
            total_socios = df_org_clean[col_org].nunique()
            total_facultades = df_org_clean[col_fac].nunique()
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("🏢 Total de Socios Comunitarios", total_socios)
            col_m2.metric("🏛️ Total de Facultades Vinculadas", total_facultades)
            
            st.markdown("---")
            st.subheader("📈 Distribución de Socios Comunitarios por Facultad")
            
            df_grafico = df_org_clean.dropna(subset=[col_fac, col_org]).groupby(col_fac)[col_org].nunique().reset_index()
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
            
            socios_agrupados = df_org_clean.groupby(col_org).agg(
                total_convenios=(col_org, 'count'),
                codigos_ids=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_id in df_org_clean.columns else (col_org, lambda x: "N/A"),
                facultades=(col_fac, lambda x: ", ".join(x.dropna().astype(str).unique())),
                tipos=(col_tipo, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_tipo else (col_org, lambda x: "N/A")
            ).reset_index()
            
            cols = st.columns(2)
            for idx, row in socios_agrupados.iterrows():
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="socio-card">
                            <div class="socio-title">🏢 {row[col_org]}</div>
                            <div class="socio-detail"><b>Cantidad de Proyectos / Convenios:</b> {row['total_convenios']} (IDs: {row['codigos_ids']})</div>
                            <div class="socio-detail"><b>Facultad Involucrada:</b> {row['facultades']}</div>
                            <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron las columnas de organización o facultad en los datos.")
    else:
        st.info("No hay datos cargados para la fuente seleccionada.")

# -------------------------------------------------------------
# OPCIÓN 3: GESTIÓN Y ACTUALIZACIÓN DE ARCHIVOS
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
                df_subido = pd.read_excel(uploaded_file, sheet_name=0)
                df_subido.columns = [str(c).strip() for c in df_subido.columns]
                
                if 'ESTADO DEL PROYECTO' in df_subido.columns:
                    df_subido = df_subido[~df_subido['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])].copy()

                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = df_subido
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.dict_inc = {xls_subido.sheet_names[0]: df_subido}
                else:
                    st.session_state.df_pac = df_subido
                    
                st.success("¡Base de datos procesada y guardada filtrando Borradores y Canceladas!")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
