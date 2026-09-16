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
        df_inc = pd.read_excel('reporte_general_INC (2).xlsx', sheet_name='Incubadoras')
        df_inc.columns = [c.strip() for c in df_inc.columns]
        df_inc = df_inc[df_inc['ESTADO DEL PROYECTO'] != 'Borrador'].copy()
        st.session_state.df_inc = df_inc
    except Exception:
        st.session_state.df_inc = pd.DataFrame(columns=['ID', 'PROYECTO', 'ESTADO DEL PROYECTO', 'FACULTAD LÍDER'])

if 'df_pac' not in st.session_state:
    try:
        # Intentar cargar si existe un archivo PAC local, si no, crear vacío
        df_pac = pd.read_excel('Proyectos_PAC.xlsx')
        df_pac.columns = [c.strip() for c in df_pac.columns]
        st.session_state.df_pac = df_pac
    except Exception:
        st.session_state.df_pac = pd.DataFrame(columns=['ID', 'Proyecto PAC', 'Socio Comunitario', 'Facultad', 'Tipo de Iniciativa'])

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
        col1.metric("Proyectos Válidos", len(df_inc))
        col2.metric("Estudiantes", int(df_inc['ESTUDIANTES PARTICIPANTES'].sum()) if 'ESTUDIANTES PARTICIPANTES' in df_inc.columns else 0)
        col3.metric("Beneficiarios", int(df_inc['BENEFICIARIOS'].sum()) if 'BENEFICIARIOS' in df_inc.columns else 0)
        col4.metric("Recursos ($)", f"${df_inc['RECURSOS APROBADOS'].sum():,.0f}" if 'RECURSOS APROBADOS' in df_inc.columns else 0)
        
        st.markdown("---")
        st.subheader("📋 Detalle de Proyectos de Incubación")
        st.dataframe(df_inc, use_container_width=True)

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC")
        if len(df_pac) > 0:
            st.metric("Total Proyectos PAC", len(df_pac))
            st.markdown("---")
            st.dataframe(df_pac, use_container_width=True)
        else:
            st.info("Aún no hay registros cargados para Proyectos PAC. Sube un archivo desde la sección de gestión.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS (CON SELECTOR MANUAL DE COLUMNAS)
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios")
    st.markdown("Visualización detallada de los socios comunitarios agrupados por iniciativas.")
    
    tipo_socio = st.radio("Seleccionar origen de socios:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    df_actual = st.session_state.df_pac if tipo_socio == "Proyectos PAC" else st.session_state.df_inc
    
    if len(df_actual) > 0:
        st.write(f"**columnas detectadas en la base de datos de {tipo_socio}:**")
        columnas_disponibles = list(df_actual.columns)
        
        # Permitir al usuario elegir qué columna representa qué, para asegurar que funcione perfectamente
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            col_socio = st.selectbox("Columna de Socio Comunitario:", columnas_disponibles, index=0 if len(columnas_disponibles)>0 else 0)
        with col_c2:
            col_fac = st.selectbox("Columna de Facultad:", columnas_disponibles, index=min(1, len(columnas_disponibles)-1))
        with col_c3:
            col_tipo = st.selectbox("Columna de Tipo/Ámbito:", columnas_disponibles, index=min(2, len(columnas_disponibles)-1))
            
        st.markdown("---")
        
        # Agrupación basada en la selección manual del usuario
        try:
            socios_agrupados = df_actual.groupby(col_socio).agg(
                total_proyectos=(df_actual.columns[0], 'count'),
                facultades=(col_fac, lambda x: ", ".join(x.dropna().astype(str).unique())),
                tipos=(col_tipo, lambda x: ", ".join(x.dropna().astype(str).unique()))
            ).reset_index()
            
            # Renderizar tarjetas
            cols = st.columns(2)
            for idx, row in socios_agrupados.iterrows():
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="socio-card">
                            <div class="socio-title">🏢 {row[col_socio]}</div>
                            <div class="socio-detail"><b>Cantidad de Proyectos / Convenios:</b> {row['total_proyectos']}</div>
                            <div class="socio-detail"><b>Facultades Involucradas:</b> {row['facultades']}</div>
                            <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al agrupar los datos: {e}")
    else:
        st.warning(f"No hay datos cargados para {tipo_socio}. Sube un archivo Excel desde la sección de gestión.")

# -------------------------------------------------------------
# OPCIÓN 3: SUBIR Y GESTIONAR NUEVA INFORMACIÓN
# -------------------------------------------------------------
else:
    st.title("📂 Gestión, Limpieza y Actualización de Archivos")
    st.markdown("Sube nuevos archivos Excel para analizarlos, limpiarlos automáticamente y actualizar las bases de datos.")

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
            
            st.subheader("⚙️ Método de Actualización")
            accion = st.radio("¿Qué deseas hacer con esta información?", ["Reemplazar la base de datos existente", "Agregar (Concatenar) a la base de datos existente"])
            
            if st.button("Aplicar Cambios en el Sistema"):
                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = df_nuevo if accion == "Reemplazar la base de datos existente" else pd.concat([st.session_state.df_bd, df_nuevo], ignore_index=True)
                    st.success("¡Base de datos 'BD Innovación' actualizada correctamente!")
                    
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.df_inc = df_nuevo if accion == "Reemplazar la base de datos existente" else pd.concat([st.session_state.df_inc, df_nuevo], ignore_index=True)
                    st.success("¡Base de datos 'Reporte General Incubadoras' actualizada correctamente!")
                    
                else: # Proyectos PAC
                    st.session_state.df_pac = df_nuevo if accion == "Reemplazar la base de datos existente" else pd.concat([st.session_state.df_pac, df_nuevo], ignore_index=True)
                    st.success("¡Base de datos 'Proyectos PAC' actualizada correctamente!")
                    
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
