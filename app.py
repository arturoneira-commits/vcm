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

# Inicializar Estado de Sesión para persistir datos completos de los archivos
if 'df_bd' not in st.session_state:
    try:
        df_bd = pd.read_excel('BD Innovacion.xlsx', sheet_name='Hoja1')
        df_bd.columns = [c.strip() for c in df_bd.columns]
        st.session_state.df_bd = df_bd
    except Exception:
        st.session_state.df_bd = pd.DataFrame(columns=['ID', 'Facultad', 'Escuela', 'Categoria', 'Iniciativa', 'Estado', 'Estudiantes'])

# Cargar archivos de Incubadoras conservando múltiples hojas si es posible
if 'xls_inc_data' not in st.session_state:
    try:
        xls_inc = pd.ExcelFile('reporte_general_INC (2).xlsx')
        st.session_state.xls_inc_sheets = xls_inc.sheet_names
        # Guardamos todas las hojas en un diccionario de DataFrames
        st.session_state.dict_inc = {sh: pd.read_excel('reporte_general_INC (2).xlsx', sheet_name=sh) for sh in xls_inc.sheet_names}
        for sh in st.session_state.dict_inc:
            st.session_state.dict_inc[sh].columns = [c.strip() for c in st.session_state.dict_inc[sh].columns]
    except Exception:
        st.session_state.xls_inc_sheets = []
        st.session_state.dict_inc = {}

if 'xls_pac_data' not in st.session_state:
    try:
        xls_pac = pd.ExcelFile('Proyectos_PAC.xlsx')
        st.session_state.xls_pac_sheets = xls_pac.sheet_names
        st.session_state.dict_pac = {sh: pd.read_excel('Proyectos_PAC.xlsx', sheet_name=sh) for sh in xls_pac.sheet_names}
        for sh in st.session_state.dict_pac:
            st.session_state.dict_pac[sh].columns = [c.strip() for c in st.session_state.dict_pac[sh].columns]
    except Exception:
        st.session_state.xls_pac_sheets = []
        st.session_state.dict_pac = {}

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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Iniciativas", len(df_bd))
        col2.metric("En Ejecución", len(df_bd[df_bd['Estado'].str.lower() == 'en ejecución']) if 'Estado' in df_bd.columns else 0)
        col3.metric("Finalizados", len(df_bd[df_bd['Estado'].str.lower() == 'finalizado']) if 'Estado' in df_bd.columns else 0)
        col4.metric("Estudiantes Totales", int(df_bd['Estudiantes'].sum()) if 'Estudiantes' in df_bd.columns else 0)
        
        st.markdown("---")
        st.subheader("📋 Detalle de Iniciativas de Innovación")
        st.dataframe(df_bd, use_container_width=True)

    elif dataset_choice == "Reporte General Incubadoras":
        st.subheader("📊 Indicadores Clave - Incubadoras")
        dict_inc = st.session_state.get('dict_inc', {})
        hoja_activa = st.selectbox("Seleccionar hoja a visualizar:", list(dict_inc.keys()) if dict_inc else ["Sin datos"])
        if hoja_activa in dict_inc:
            df_view = dict_inc[hoja_activa]
            col1, col2 = st.columns(2)
            col1.metric("Total Registros", len(df_view))
            st.markdown("---")
            st.dataframe(df_view, use_container_width=True)

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC")
        dict_pac = st.session_state.get('dict_pac', {})
        hoja_activa_pac = st.selectbox("Seleccionar hoja a visualizar:", list(dict_pac.keys()) if dict_pac else ["Sin datos"])
        if hoja_activa_pac in dict_pac:
            df_view_pac = dict_pac[hoja_activa_pac]
            col1, col2 = st.columns(2)
            col1.metric("Total Registros", len(df_view_pac))
            st.markdown("---")
            st.dataframe(df_view_pac, use_container_width=True)

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS (MATCH FACULTAD <-> CÓDIGO DE PROYECTO)
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios y Cruce por Código de Proyecto")
    st.markdown("Vinculación de la hoja **Organizaciones** con la hoja principal de proyectos usando el **código de proyecto** para obtener la facultad correspondiente.")
    
    tipo_fuente = st.radio("Seleccionar archivo origen:", ["Reporte General Incubadoras", "Proyectos PAC"], horizontal=True)
    st.markdown("---")
    
    dict_actual = st.session_state.get('dict_inc', {}) if tipo_fuente == "Reporte General Incubadoras" else st.session_state.get('dict_pac', {})
    
    if 'Organizaciones' in dict_actual:
        df_org = dict_actual['Organizaciones'].copy()
        
        # Encontrar la hoja principal (cualquier hoja distinta de Organizaciones)
        hojas_principales = [h for h in dict_actual.keys() if h != 'Organizaciones']
        
        if hojas_principales:
            # Seleccionar la primera hoja principal disponible como base de proyectos
            nombre_hoja_ppal = hojas_principales[0]
            df_ppal = dict_actual[nombre_hoja_ppal].copy()
            
            st.info(f"💡 Realizando match entre la hoja **Organizaciones** y la hoja principal **{nombre_hoja_ppal}**.")
            
            # Detectar columna de organización
            cols_org_lower = {c.lower(): c for c in df_org.columns}
            col_org_name = cols_org_lower.get('organización', cols_org_lower.get('organizacion', None))
            
            # Detectar columna de código de proyecto en ambas hojas
            col_codigo_org = next((c for c in df_org.columns if 'código' in c.lower() or 'codigo' in c.lower() or 'id' in c.lower() or 'proyecto' in c.lower()), None)
            
            cols_ppal_lower = {c.lower(): c for c in df_ppal.columns}
            col_codigo_ppal = next((c for c in df_ppal.columns if 'código' in c.lower() or 'codigo' in c.lower() or 'id' in c.lower() or 'proyecto' in c.lower()), None)
            col_fac_ppal = next((c for c in df_ppal.columns if 'facultad' in c.lower()), None)
            col_tipo_ppal = next((c for c in df_ppal.columns if 'tipo' in c.lower() or 'ambito' in c.lower() or 'iniciativa' in c.lower()), None)
            
            if col_org_name and col_codigo_org and col_codigo_ppal:
                # Hacer el merge (match) usando el código de proyecto
                df_merged = pd.merge(
                    df_org, 
                    df_ppal[[col_codigo_ppal] + ([col_fac_ppal] if col_fac_ppal else []) + ([col_tipo_ppal] if col_tipo_ppal else [])], 
                    left_on=col_codigo_org, 
                    right_on=col_codigo_ppal, 
                    how='left',
                    suffixes=('', '_ppal')
                )
                
                # Definir qué columna usar para la facultad tras el merge
                col_fac_final = col_fac_ppal if col_fac_ppal and col_fac_ppal in df_merged.columns else next((c for c in df_merged.columns if 'facultad' in c.lower()), None)
                col_tipo_final = col_tipo_ppal if col_tipo_ppal and col_tipo_ppal in df_merged.columns else next((c for c in df_merged.columns if 'tipo' in c.lower()), None)
                
                # Agrupar por organización
                socios_agrupados = df_merged.groupby(col_org_name).agg(
                    total_proyectos=(col_org_name, 'count'),
                    codigos_proyectos=(col_codigo_org, lambda x: ", ".join(x.dropna().astype(str).unique())),
                    facultades=(col_fac_final, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_fac_final else (col_org_name, lambda x: "No disponible"),
                    tipos=(col_tipo_final, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_tipo_final else (col_org_name, lambda x: "No disponible")
                ).reset_index()
                
                # Renderizar en tarjetas visuales
                cols = st.columns(2)
                for idx, row in socios_agrupados.iterrows():
                    with cols[idx % 2]:
                        st.markdown(f"""
                            <div class="socio-card">
                                <div class="socio-title">🏢 {row[col_org_name]}</div>
                                <div class="socio-detail"><b>Total Proyectos / Códigos:</b> {row['total_proyectos']} ({row['codigos_proyectos']})</div>
                                <div class="socio-detail"><b>Facultad (Match):</b> {row['facultades']}</div>
                                <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No se pudieron identificar automáticamente las columnas de enlace (código de proyecto u organización) para hacer el match.")
        else:
            st.warning("La estructura del archivo necesita al menos una hoja adicional además de 'Organizaciones' para cruzar los datos del proyecto.")
    else:
        st.warning(f"El archivo seleccionado no contiene la hoja 'Organizaciones'. Hojas disponibles: {list(dict_actual.keys())}")

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
            hoja_seleccionada = st.selectbox("Selecciona la hoja a procesar:", xls_subido.sheet_names)
            df_nuevo = pd.read_excel(uploaded_file, sheet_name=hoja_seleccionada)
            df_nuevo.columns = [c.strip() for c in df_nuevo.columns]
            
            st.write("### Vista previa del archivo subido:")
            st.dataframe(df_nuevo.head())
            
            if st.button("Guardar Cambios"):
                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = df_nuevo
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.dict_inc[hoja_seleccionada] = df_nuevo
                else:
                    st.session_state.dict_pac[hoja_seleccionada] = df_nuevo
                st.success("¡Base de datos actualizada correctamente!")
                    
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
