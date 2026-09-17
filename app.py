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

# Inicializar estados
if 'df_bd' not in st.session_state:
    st.session_state.df_bd = pd.DataFrame()
if 'dict_inc' not in st.session_state:
    st.session_state.dict_inc = {}
if 'dict_pac' not in st.session_state:
    st.session_state.dict_pac = {}

# Carga automática y flexible de archivos Excel en la raíz del repositorio
archivos_en_raiz = os.listdir('.')

# 1. Cargar BD Innovación
try:
    bd_files = [f for f in archivos_en_raiz if 'INNOVACION' in f.upper() and f.endswith('.xlsx')]
    if bd_files and len(st.session_state.df_bd) == 0:
        st.session_state.df_bd = pd.read_excel(bd_files[0], sheet_name=0)
        st.session_state.df_bd.columns = [str(c).strip() for c in st.session_state.df_bd.columns]
except Exception:
    pass

# 2. Cargar Incubadoras
try:
    inc_files = [f for f in archivos_en_raiz if 'INC' in f.upper() and f.endswith('.xlsx')]
    if inc_files and not st.session_state.dict_inc:
        file_inc = inc_files[0]
        xls_inc = pd.ExcelFile(file_inc)
        dict_inc = {sh: pd.read_excel(file_inc, sheet_name=sh) for sh in xls_inc.sheet_names}
        for sh in dict_inc:
            dict_inc[sh].columns = [str(c).strip() for c in dict_inc[sh].columns]
        if 'Incubadoras' in dict_inc and 'ESTADO DEL PROYECTO' in dict_inc['Incubadoras'].columns:
            dict_inc['Incubadoras'] = dict_inc['Incubadoras'][dict_inc['Incubadoras']['ESTADO DEL PROYECTO'] != 'Borrador']
        st.session_state.dict_inc = dict_inc
except Exception:
    pass

# 3. Cargar Proyectos PAC (Detecta 'Libro3', 'PAC' o cualquier excel con múltiples hojas)
try:
    pac_files = [f for f in archivos_en_raiz if ('PAC' in f.upper() or 'LIBRO3' in f.upper()) and f.endswith('.xlsx')]
    if not pac_files:
        # Si no encuentra por nombre, busca cualquier excel que tenga más de 1 hoja (como Libro3 o reporte PAC)
        for f in archivos_en_raiz:
            if f.endswith('.xlsx') and f not in inc_files and f not in bd_files:
                try:
                    if len(pd.ExcelFile(f).sheet_names) > 1:
                        pac_files.append(f)
                        break
                except:
                    pass

    if pac_files and not st.session_state.dict_pac:
        file_pac = pac_files[0]
        xls_pac = pd.ExcelFile(file_pac)
        dict_pac = {sh: pd.read_excel(file_pac, sheet_name=sh) for sh in xls_pac.sheet_names}
        for sh in dict_pac:
            dict_pac[sh].columns = [str(c).strip() for c in dict_pac[sh].columns]
        
        # Mapear nombres de hojas estándar si vienen como Hoja1 / Hoja2
        if 'Hoja1' in dict_pac and 'Proyectos' not in dict_pac:
            dict_pac['Proyectos'] = dict_pac.pop('Hoja1')
        if 'Hoja2' in dict_pac and 'Organizaciones' not in dict_pac:
            dict_pac['Organizaciones'] = dict_pac.pop('Hoja2')
            
        # Limpieza automática: Excluir proyectos en estado 'Borrador'
        if 'Proyectos' in dict_pac and 'ESTADO DEL PROYECTO' in dict_pac['Proyectos'].columns:
            df_proy_pac = dict_pac['Proyectos']
            df_proy_limpio = df_proy_pac[df_proy_pac['ESTADO DEL PROYECTO'].astype(str).str.lower() != 'borrador'].copy()
            dict_pac['Proyectos'] = df_proy_limpio
            
            ids_validos = df_proy_limpio['ID'].dropna().tolist() if 'ID' in df_proy_limpio.columns else []
            if ids_validos:
                for sh in dict_pac:
                    if sh != 'Proyectos' and 'ID' in dict_pac[sh].columns:
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
            st.info("No se encontró el archivo de BD Innovación.")

    elif dataset_choice == "Reporte General Incubadoras":
        st.subheader("📊 Indicadores Clave - Incubadoras (Sin Borradores)")
        dict_inc = st.session_state.get('dict_inc', {})
        if dict_inc:
            hoja_activa = st.selectbox("Seleccionar hoja a visualizar:", list(dict_inc.keys()))
            st.dataframe(dict_inc[hoja_activa], use_container_width=True)
        else:
            st.info("No se encontró el archivo de Incubadoras.")

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC (Sin Borradores)")
        dict_pac = st.session_state.get('dict_pac', {})
        
        if 'Proyectos' in dict_pac:
            df_proyectos_pac = dict_pac['Proyectos']
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Proyectos PAC", len(df_proyectos_pac))
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
                        title="Proyectos PAC por Facultad Líder",
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
            st.info("No se detectó ningún archivo Excel de Proyectos PAC en el repositorio. Súbelo a la raíz de tu GitHub.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios y Gráfico de Facultades")
    st.markdown("Cruce automatizado entre la hoja **Organizaciones** y la hoja principal **Proyectos**.")
    
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
    st.markdown("Sube nuevos archivos Excel para actualizar las bases de datos.")

    dataset_choice = st.sidebar.radio("Seleccionar Base de Datos a Actualizar:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    uploaded_file = st.file_uploader("Selecciona un archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            xls_subido = pd.ExcelFile(uploaded_file)
            hoja_seleccionada = st.selectbox("Selecciona la hoja a procesar:", xls_subido.sheet_names)
            df_nuevo = pd.read_excel(uploaded_file, sheet_name=hoja_seleccionada)
            df_nuevo.columns = [str(c).strip() for c in df_nuevo.columns]
            
            st.write("### Vista previa:")
            st.dataframe(df_nuevo.head())
            
            if st.button("Guardar Cambios"):
                if dataset_choice == "BD Innovación":
                    st.session_state.df_bd = df_nuevo
                elif dataset_choice == "Reporte General Incubadoras":
                    st.session_state.dict_inc[hoja_seleccionada] = df_nuevo
                else:
                    st.session_state.dict_pac[hoja_seleccionada] = df_nuevo
                st.success("¡Base de datos actualizada!")
        except Exception as e:
            st.error(f"Error: {e}")
