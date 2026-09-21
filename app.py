import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="Dirección General de Vinculación con el Medio - UNIACC", layout="wide", page_icon=None)

# Control de autenticación en session_state (debe ir antes de renderizar la UI para aplicar el CSS del header)
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Estilos CSS personalizados (Fondo blanco y tonos celeste/azul, sin iconos)
# Si NO es admin, ocultamos la barra superior de Streamlit (header con Share, GitHub, etc.)
css_toolbar_oculta = "header {visibility: hidden;}" if not st.session_state.is_admin else "header {visibility: visible;}"

st.markdown(f"""
    <style>
    {css_toolbar_oculta}
    .main {{ background-color: #ffffff; }}
    .stApp {{ background-color: #ffffff; }}
    .stMetric {{ background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
    .socio-card {{
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #0284c7;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }}
    .socio-title {{
        font-size: 18px;
        font-weight: bold;
        color: #0f172a;
        margin-bottom: 10px;
    }}
    .socio-detail {{
        font-size: 14px;
        color: #334155;
        margin-bottom: 5px;
    }}
    .admin-badge {{
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #bae6fd;
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# CARGA ESTÁTICA DESDE ARCHIVOS EN LA RAIZ (Persistente al refrescar)
# -------------------------------------------------------------
archivos_en_raiz = os.listdir('.') if os.path.exists('.') else []

# 1. Cargar BD Innovación
df_bd = pd.DataFrame()
bd_files = [f for f in archivos_en_raiz if 'innovacion' in f.lower() and f.endswith('.xlsx')]
if bd_files:
    try:
        file_bd = bd_files[0]
        xls_bd = pd.ExcelFile(file_bd)
        hoja_bd = 'Hoja1' if 'Hoja1' in xls_bd.sheet_names else xls_bd.sheet_names[0]
        df_bd_raw = pd.read_excel(file_bd, sheet_name=hoja_bd)
        df_bd_raw.columns = [str(c).strip() for c in df_bd_raw.columns]
        
        if 'Estado' in df_bd_raw.columns:
            df_bd = df_bd_raw[
                ~df_bd_raw['Estado'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
            ].copy()
        else:
            df_bd = df_bd_raw
    except Exception:
        pass

# 2. Cargar Incubadoras (Leyendo pestañas principales y hoja de Organizaciones)
dict_inc = {}
df_inc_orgs = pd.DataFrame()
inc_files = [f for f in archivos_en_raiz if 'inc' in f.lower() and f.endswith('.xlsx') and 'innovacion' not in f.lower()]
if inc_files:
    try:
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
        
        # Cargar y cruzar organizaciones de incubadoras si existe la pestaña
        if 'Organizaciones' in dict_inc and hoja_inc in dict_inc:
            df_orgs_raw = dict_inc['Organizaciones']
            valid_ids = dict_inc[hoja_inc]['ID'].dropna().tolist()
            df_orgs_filtradas = df_orgs_raw[df_orgs_raw['ID'].isin(valid_ids)].copy()
            
            # Buscamos columnas posibles para el nombre del proyecto en incubadoras
            col_nombre_inc = next((c for c in dict_inc[hoja_inc].columns if any(k in c.lower() for k in ['nombre', 'proyecto', 'iniciativa', 'titulo'])), 'ID')
            df_proyectos_info = dict_inc[hoja_inc][['ID', 'FACULTAD LÍDER', col_nombre_inc]].copy()
            df_proyectos_info.columns = ['ID', 'FACULTAD LÍDER', 'NOMBRE_PROYECTO']
            
            df_inc_orgs = pd.merge(df_orgs_filtradas, df_proyectos_info, on='ID', how='inner', suffixes=('', '_proj'))
    except Exception:
        pass

# 3. Cargar Proyectos PAC
df_pac = pd.DataFrame()
pac_file = 'reporte_general_PAC_limpio.xlsx' if os.path.exists('reporte_general_PAC_limpio.xlsx') else next((f for f in archivos_en_raiz if 'pac' in f.lower() and f.endswith('.xlsx')), None)
if pac_file:
    try:
        df_pac_raw = pd.read_excel(pac_file, sheet_name=0)
        df_pac_raw.columns = [str(c).strip() for c in df_pac_raw.columns]
        
        if 'ESTADO DEL PROYECTO' in df_pac_raw.columns:
            df_pac = df_pac_raw[
                ~df_pac_raw['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])
            ].copy()
        else:
            df_pac = df_pac_raw
    except Exception:
        pass

# -------------------------------------------------------------
# AUTENTICACIÓN Y PANEL DE CONTROL (SIDEBAR)
# -------------------------------------------------------------
st.sidebar.header("Navegación")

opciones_menu = ["Dashboard Principal", "Socios Comunitarios"]

if st.session_state.is_admin:
    st.sidebar.markdown('<div class="admin-badge">Modo Administrador Activo</div>', unsafe_allow_html=True)
    opciones_menu.append("Gestión y Actualización de Archivos")
    if st.sidebar.button("Cerrar Sesión de Admin"):
        st.session_state.is_admin = False
        st.rerun()
else:
    with st.sidebar.expander("Acceso Administrador"):
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("Ingresar"):
            if password_input == "admin123":
                st.session_state.is_admin = True
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

app_mode = st.sidebar.selectbox("Ir a:", opciones_menu)

# -------------------------------------------------------------
# OPCIÓN 1: DASHBOARD PRINCIPAL
# -------------------------------------------------------------
if app_mode == "Dashboard Principal":
    dataset_choice = st.sidebar.radio("Seleccionar Base de Datos:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    
    st.markdown("### Dirección General de Vinculación con el Medio")
    st.markdown("#### Reporte de proyectos 2026")
    st.markdown("##### UNIACC")
    st.markdown("---")

    if dataset_choice == "BD Innovación":
        st.subheader("Indicadores Clave - BD Innovación (Sin Canceladas)")
        if not df_bd.empty:
            total_iniciativas = len(df_bd)
            en_ejecucion = len(df_bd[df_bd['Estado'].str.lower() == 'en ejecución']) if 'Estado' in df_bd.columns else 0
            finalizados = len(df_bd[df_bd['Estado'].str.lower() == 'finalizado']) if 'Estado' in df_bd.columns else 0
            total_estudiantes = int(df_bd['Estudiantes'].sum()) if 'Estudiantes' in df_bd.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Iniciativas Válidas", total_iniciativas)
            col2.metric("En Ejecución", en_ejecucion)
            col3.metric("Finalizados", finalizados)
            col4.metric("Estudiantes Totales", total_estudiantes)
            
            st.markdown("---")
            st.subheader("Cantidad de Iniciativas por Facultad (BD Innovación)")
            
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
                        color_continuous_scale='Blues'
                    )
                    fig_bd.update_layout(xaxis_title="Número de Iniciativas", yaxis_title="Facultad", plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig_bd, use_container_width=True)
            else:
                st.info("No se encontró una columna de facultad en BD Innovación.")

            st.markdown("---")
            st.subheader("Detalle de Iniciativas de Innovación")
            st.dataframe(df_bd, use_container_width=True)
        else:
            st.info("No hay datos cargados para BD Innovación.")

    elif dataset_choice == "Reporte General Incubadoras":
        st.subheader("Indicadores Clave - Incubadoras (Sin Borradores ni Canceladas)")
        if dict_inc:
            hoja_inc_nombre = 'Incubadoras' if 'Incubadoras' in dict_inc else list(dict_inc.keys())[0]
            df_inc_activa = dict_inc[hoja_inc_nombre]
            
            total_proyectos_inc = len(df_inc_activa)
            col_fac_inc = next((c for c in df_inc_activa.columns if 'facultad' in c.lower()), None)
            total_facultades_inc = df_inc_activa[col_fac_inc].nunique() if col_fac_inc else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total de Proyectos (Incubadoras)", total_proyectos_inc)
            col_m2.metric("Total de Facultades", total_facultades_inc)
            
            st.markdown("---")
            st.subheader("Cantidad de Proyectos por Facultad Líder (Incubadoras)")
            
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
                        color_continuous_scale='Blues'
                    )
                    fig_inc.update_layout(xaxis_title="Número de Proyectos", yaxis_title="Facultad", plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig_inc, use_container_width=True)
            else:
                st.info("No se encontró una columna de facultad en esta hoja de Incubadoras.")

            st.markdown("---")
            st.subheader("Detalle de Incubadoras")
            st.dataframe(df_inc_activa, use_container_width=True)
        else:
            st.info("No hay datos cargados para Incubadoras.")

    else: # Proyectos PAC
        st.subheader("Indicadores Clave - Proyectos PAC (Sin Borradores ni Canceladas)")
        if not df_pac.empty:
            total_proyectos_pac = df_pac['ID'].nunique() if 'ID' in df_pac.columns else len(df_pac)
            total_estudiantes = int(df_pac['ESTUDIANTES PARTICIPANTES'].sum()) if 'ESTUDIANTES PARTICIPANTES' in df_pac.columns else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Total Proyectos PAC Válidos", total_proyectos_pac)
            col2.metric("Estudiantes Participantes", total_estudiantes)
            
            st.markdown("---")
            st.subheader("Cantidad de Proyectos PAC por Facultad Líder")
            if 'FACULTAD LÍDER' in df_pac.columns:
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
                    fig_pac.update_layout(xaxis_title="Número de Proyectos", yaxis_title="Facultad", plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig_pac, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Detalle de Proyectos PAC")
            st.dataframe(df_pac, use_container_width=True)
        else:
            st.info("No hay datos cargados para Proyectos PAC.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS
# -------------------------------------------------------------
elif app_mode == "Socios Comunitarios":
    st.markdown("### Dirección General de Vinculación con el Medio")
    st.markdown("#### Reporte de proyectos 2026")
    st.markdown("##### UNIACC")
    st.markdown("---")
    
    st.title("Red de Socios Comunitarios")
    st.markdown("Extracción directa de organizaciones y facultades desde las estructuras limpias.")
    
    tipo_fuente = st.radio("Seleccionar archivo origen:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    if tipo_fuente == "Proyectos PAC":
        df_src = df_pac
        col_org = next((c for c in df_src.columns if 'organización' in c.lower() or 'organizacion' in c.lower() or 'entidad' in c.lower()), None)
        col_fac = next((c for c in df_src.columns if 'facultad' in c.lower()), None)
        col_id = next((c for c in df_src.columns if 'id' in c.lower()), None)
        col_nom_proy = next((c for c in df_src.columns if any(k in c.lower() for k in ['nombre', 'proyecto', 'iniciativa', 'titulo'])), None)
        
        if not df_src.empty and col_org and col_fac:
            df_org_clean = df_src.dropna(subset=[col_org]).copy()
            socios_agrupados = df_org_clean.groupby(col_org).agg(
                total_convenios=(col_org, 'count'),
                codigos_ids=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_id else (col_org, lambda x: "N/A"),
                facultades=(col_fac, lambda x: ", ".join(x.dropna().astype(str).unique())),
                nombres_proyectos=(col_nom_proy, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_nom_proy else (col_org, lambda x: "N/A")
            ).reset_index()
        else:
            socios_agrupados = pd.DataFrame()

    else: # Reporte General Incubadoras
        df_src = df_inc_orgs
        if not df_src.empty:
            col_org = 'ORGANIZACIÓN'
            col_fac = 'FACULTAD LÍDER'
            col_id = 'ID'
            col_nom_proy = 'NOMBRE_PROYECTO' if 'NOMBRE_PROYECTO' in df_src.columns else 'ID'
            
            socios_agrupados = df_src.groupby(col_org).agg(
                total_convenios=(col_org, 'count'),
                codigos_ids=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())),
                facultades=(col_fac, lambda x: ", ".join(x.dropna().astype(str).unique())),
                nombres_proyectos=(col_nom_proy, lambda x: ", ".join(x.dropna().astype(str).unique()))
            ).reset_index()
        else:
            socios_agrupados = pd.DataFrame()

    if not socios_agrupados.empty:
        total_socios = len(socios_agrupados)
        total_facultades = socios_agrupados['facultades'].nunique()
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total de Entidades / Socios Comunitarios", total_socios)
        col_m2.metric("Total de Facultades Vinculadas", total_facultades)
        
        st.markdown("---")
        st.subheader("Distribución de Entidades por Facultad")
        
        df_grafico = socios_agrupados.assign(facultades=socios_agrupados['facultades'].str.split(', ')).explode('facultades')
        df_grafico = df_grafico.groupby('facultades')['total_convenios'].sum().reset_index()
        df_grafico.columns = ['Facultad', 'Cantidad de Entidades']
        df_grafico = df_grafico.sort_values(by='Cantidad de Entidades', ascending=True)
        
        if not df_grafico.empty:
            fig = px.bar(
                df_grafico, 
                x='Cantidad de Entidades', 
                y='Facultad', 
                orientation='h',
                title=f"Cantidad de Entidades / Socios por Facultad ({tipo_fuente})",
                text='Cantidad de Entidades',
                color='Cantidad de Entidades',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_title="Cantidad de Entidades", yaxis_title="Facultad", plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Detalle por Entidad / Socio Comunitario")
        
        cols = st.columns(2)
        for idx, row in socios_agrupados.iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="socio-card">
                        <div class="socio-title">{row[col_org]}</div>
                        <div class="socio-detail"><b>Registros / Proyectos:</b> {row['total_convenios']} (IDs: {row['codigos_ids']})</div>
                        <div class="socio-detail"><b>Facultad Involucrada:</b> {row['facultades']}</div>
                        <div class="socio-detail"><b>Nombre del Proyecto:</b> {row['nombres_proyectos']}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay datos de organizaciones disponibles para la fuente seleccionada.")

# -------------------------------------------------------------
# OPCIÓN 3: GESTIÓN, ELIMINACIÓN Y ACTUALIZACIÓN (SOLO ADMIN)
# -------------------------------------------------------------
elif app_mode == "Gestión y Actualización de Archivos" and st.session_state.is_admin:
    st.markdown("### Dirección General de Vinculación con el Medio")
    st.markdown("#### Reporte de proyectos 2026")
    st.markdown("##### UNIACC")
    st.markdown("---")
    
    st.title("Gestión, Limpieza y Actualización de Archivos")
    st.markdown("Administra los archivos almacenados estáticamente en el sistema.")

    st.subheader("Selector para Eliminar Archivos Existentes")
    archivos_excel_actuales = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if archivos_excel_actuales:
        archivo_a_borrar = st.selectbox("Selecciona el archivo que deseas eliminar para reemplazarlo:", archivos_excel_actuales)
        if st.button("Eliminar Archivo Seleccionado", type="primary"):
            try:
                os.remove(archivo_a_borrar)
                st.success(f"¡El archivo '{archivo_a_borrar}' ha sido eliminado correctamente! Recarga la página para ver los cambios.")
            except Exception as e:
                st.error(f"No se pudo eliminar el archivo: {e}")
    else:
        st.info("No hay archivos Excel en la raíz actualmente.")

    st.markdown("---")
    st.subheader("Subir Nuevo Archivo Estático")
    dataset_choice = st.selectbox("Destino de la base de datos:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    uploaded_file = st.file_uploader("Selecciona un nuevo archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        if st.button("Guardar Estáticamente en el Sistema"):
            try:
                if "Innovación" in dataset_choice:
                    nombre_guardado = "bd_innovacion.xlsx"
                elif "Incubadoras" in dataset_choice:
                    nombre_guardado = "reporte_general_incubadoras.xlsx"
                else:
                    nombre_guardado = "reporte_general_PAC_limpio.xlsx"
                
                with open(nombre_guardado, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"¡Archivo guardado estáticamente como '{nombre_guardado}'! La información ya es permanente y no se borrará al refrescar. Recarga la página.")
            except Exception as e:
                st.error(f"Error al guardar el archivo: {e}")
