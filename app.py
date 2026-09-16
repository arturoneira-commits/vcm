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

# Inicializar Estado de Sesión para persistir datos
if 'df_bd' not in st.session_state:
    try:
        df_bd = pd.read_excel('BD Innovacion.xlsx', sheet_name='Hoja1')
        df_bd.columns = [c.strip() for c in df_bd.columns]
        st.session_state.df_bd = df_bd
    except Exception:
        st.session_state.df_bd = pd.DataFrame(columns=['ID', 'Facultad', 'Escuela', 'Categoria', 'Iniciativa', 'Estado', 'Estudiantes'])

if 'df_inc' not in st.session_state:
    try:
        # Intentamos cargar la hoja Organizaciones si existe, si no la principal
        xls_inc = pd.ExcelFile('reporte_general_INC (2).xlsx')
        sheet_org = 'Organizaciones' if 'Organizaciones' in xls_inc.sheet_names else xls_inc.sheet_names[0]
        df_inc = pd.read_excel('reporte_general_INC (2).xlsx', sheet_name=sheet_org)
        df_inc.columns = [c.strip() for c in df_inc.columns]
        st.session_state.df_inc = df_inc
    except Exception:
        st.session_state.df_inc = pd.DataFrame(columns=['ID', 'organización', 'FACULTAD LÍDER'])

if 'df_pac' not in st.session_state:
    try:
        xls_pac = pd.ExcelFile('Proyectos_PAC.xlsx')
        sheet_org_pac = 'Organizaciones' if 'Organizaciones' in xls_pac.sheet_names else xls_pac.sheet_names[0]
        df_pac = pd.read_excel('Proyectos_PAC.xlsx', sheet_name=sheet_org_pac)
        df_pac.columns = [c.strip() for c in df_pac.columns]
        st.session_state.df_pac = df_pac
    except Exception:
        # Creamos un ejemplo si no hay archivo físico aún
        st.session_state.df_pac = pd.DataFrame({
            'ID': ['PAC001', 'PAC002', 'PAC003'],
            'organización': ['Municipalidad de Santiago', 'Fundación Tejiendo Redes', 'Cesfam San Luis'],
            'Facultad': ['Ingeniería', 'Ciencias Sociales', 'Medicina'],
            'Tipo de Iniciativa': ['Innovación Social', 'Capacitación', 'Atención en Salud']
        })

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
    
    df_bd = st.session_state.df_bd
    df_inc = st.session_state.df_inc
    df_pac = st.session_state.df_pac

    st.title("🚀 Dashboard de Iniciativas e Incubación de Proyectos")

    if dataset_choice == "BD Innovación":
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
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Registros en Organizaciones", len(df_inc))
        st.markdown("---")
        st.subheader("📋 Detalle de Organizaciones - Incubadoras")
        st.dataframe(df_inc, use_container_width=True)

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC")
        if len(df_pac) > 0:
            col1, col2 = st.columns(2)
            col1.metric("Total Registros", len(df_pac))
            st.markdown("---")
            st.dataframe(df_pac, use_container_width=True)
        else:
            st.info("Aún no hay registros cargados para Proyectos PAC.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS (USANDO LA HOJA ORGANIZACIONES)
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios")
    st.markdown("Información detallada de los socios comunitarios obtenida directamente desde la hoja **Organizaciones**.")
    
    tipo_socio = st.radio("Seleccionar origen:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    df_actual = st.session_state.df_pac if tipo_socio == "Proyectos PAC" else st.session_state.df_inc
    
    if len(df_actual) > 0:
        # Verificamos si existe la columna 'organización' (sin importar mayúsculas)
        cols_lower = {c.lower(): c for c in df_actual.columns}
        col_org_name = cols_lower.get('organización', cols_lower.get('organizacion', None))
        
        if col_org_name:
            # Buscamos columnas opcionales para facultad y tipo de iniciativa de forma inteligente
            col_fac = next((c for c in df_actual.columns if 'facultad' in c.lower()), None)
            col_tipo = next((c for c in df_actual.columns if 'tipo' in c.lower() or 'ambito' in c.lower() or 'iniciativa' in c.lower()), None)
            
            # Agrupamos por la organización
            socios_agrupados = df_actual.groupby(col_org_name).agg(
                cantidad_convenios=(col_org_name, 'count'),
                facultades=(col_fac, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_fac else (col_org_name, lambda x: "No especificado"),
                tipos=(col_tipo, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_tipo else (col_org_name, lambda x: "No especificado")
            ).reset_index()
            
            # Renderizar en tarjetas / recuadros
            cols = st.columns(2)
            for idx, row in socios_agrupados.iterrows():
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="socio-card">
                            <div class="socio-title">🏢 {row[col_org_name]}</div>
                            <div class="socio-detail"><b>Cantidad de Convenios / Registros:</b> {row['cantidad_convenios']}</div>
                            <div class="socio-detail"><b>Facultades Involucradas:</b> {row['facultades']}</div>
                            <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(f"No se encontró la columna 'organización' en la hoja de {tipo_socio}. Columnas disponibles: {list(df_actual.columns)}")
    else:
        st.info(f"No hay datos cargados para {tipo_socio}.")

# -------------------------------------------------------------
# OPCIÓN 3: SUBIR Y GESTIONAR NUEVA INFORMACIÓN
# -------------------------------------------------------------
else:
    st.title("📂 Gestión, Limpieza y Actualización de Archivos")
    st.markdown("Sube nuevos archivos Excel para analizarlos y actualizar las bases de datos.")

    dataset_choice = st.sidebar.radio("Seleccionar Base de Datos a Actualizar:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    uploaded_file = st.file_uploader("Selecciona un archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            xls_subido = pd.ExcelFile(uploaded_file)
            hoja_seleccionada = st.selectbox("Selecciona la hoja a procesar (ej. Organizaciones):", xls_subido.sheet_names)
            df_nuevo = pd.read_excel(uploaded_file, sheet_name=hoja_seleccionada)
            df_nuevo.columns = [c.strip() for c in df_nuevo.columns]
            
            st.write("### Vista previa del archivo subido:")
            st.dataframe(df_nuevo.head())
            
            if st.button("Guardar Cambios en el Sistema"):
                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = df_nuevo
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.df_inc = df_nuevo
                else:
                    st.session_state.df_pac = df_nuevo
                st.success("¡Base de datos actualizada correctamente!")
                    
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
