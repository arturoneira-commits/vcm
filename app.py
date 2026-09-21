import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="Dirección General de Vinculación con el Medio - UNIACC", layout="wide", page_icon=None)

# Control de autenticación en session_state
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Estilos CSS personalizados para reducir el espacio superior y ajustar componentes
css_toolbar_oculta = "header {visibility: hidden;}" if not st.session_state.is_admin else "header {visibility: visible;}"

st.markdown(f"""
    <style>
    {css_toolbar_oculta}
    .main {{ background-color: #f8fafc; }}
    .stApp {{ background-color: #f8fafc; }}
    
    /* Reducir el espacio superior predeterminado de Streamlit */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }}
    
    .stMetric {{ background-color: #ffffff; padding: 18px; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
    .socio-card {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #004b87;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }}
    .socio-title {{
        font-size: 18px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 10px;
    }}
    .socio-detail {{
        font-size: 14px;
        color: #475569;
        margin-bottom: 6px;
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
# FUNCIÓN AUXILIAR PARA ESTILOS PROFESIONALES EN PLOTLY (TIPO POWER BI - TORTA)
# -------------------------------------------------------------
def aplicar_estilo_powerbi_pie(fig, titulo=""):
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=15, color="#1e293b", family="Segoe UI, sans-serif"),
            x=0.5,
            xanchor='center',
            y=0.95
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", color="#334155", size=12),
        margin=dict(t=60, b=30, l=20, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=13,
            font_family="Segoe UI, sans-serif"
        )
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+value',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    return fig

# -------------------------------------------------------------
# CARGA ESTÁTICA DESDE ARCHIVOS EN LA RAIZ
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

# 2. Cargar Incubadoras
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
        
        if 'Organizaciones' in dict_inc and hoja_inc in dict_inc:
            df_orgs_raw = dict_inc['Organizaciones']
            valid_ids = dict_inc[hoja_inc]['ID'].dropna().tolist()
            df_orgs_filtradas = df_orgs_raw[df_orgs_raw['ID'].isin(valid_ids)].copy()
            
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
    st.markdown("### Dirección General de Vinculación con el Medio")
    st.markdown("#### Reporte de proyectos 2026 - Resumen General por Iniciativa")
    st.markdown("##### UNIACC")
    st.markdown("---")

    # Cálculos Globales
    tot_pac = df_pac['ID'].nunique() if ('ID' in df_pac.columns and not df_pac.empty) else len(df_pac)
    hoja_inc_nombre = 'Incubadoras' if 'Incubadoras' in dict_inc else (list(dict_inc.keys())[0] if dict_inc else None)
    tot_inc = len(dict_inc[hoja_inc_nombre]) if hoja_inc_nombre and hoja_inc_nombre in dict_inc else 0
    tot_bd = len(df_bd) if not df_bd.empty else 0

    # Gráfico de tortas general de iniciativas en lugar de las 3 tarjetas de métricas
    df_resumen_global = pd.DataFrame({
        'Iniciativa': ['Proyectos PAC', 'Proyectos Incubadoras', 'Iniciativas Innovación'],
        'Cantidad': [tot_pac, tot_inc, tot_bd]
    })

    fig_global = px.pie(
        df_resumen_global, names='Iniciativa', values='Cantidad',
        hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_global = aplicar_estilo_powerbi_pie(fig_global, "Distribución General por Tipo de Iniciativa")
    
    # Mostramos el gráfico centrado
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        st.plotly_chart(fig_global, use_container_width=True)

    st.markdown("---")
    st.markdown("##### Filtrar Vista de Gráficos por Iniciativa")

    # Pestañas de iniciativa (La primera pestaña es "Todos" y será el foco principal por defecto)
    tab_todos, tab_pac, tab_inc, tab_inn = st.tabs(["Todos", "PAC", "Incubadoras", "Innovación"])

    # --- PESTAÑA: TODOS (Muestra los 3 gráficos lado a lado) ---
    with tab_todos:
        st.subheader("Distribución Porcentual de Proyectos por Facultad (Todas las Iniciativas)")
        col_g1, col_g2, col_g3 = st.columns(3)

        with col_g1:
            st.markdown("##### Proyectos PAC")
            if not df_pac.empty and 'FACULTAD LÍDER' in df_pac.columns:
                df_p_pac = df_pac.drop_duplicates(subset=['ID']) if 'ID' in df_pac.columns else df_pac
                df_fac_pac = df_p_pac['FACULTAD LÍDER'].value_counts().reset_index()
                df_fac_pac.columns = ['Facultad', 'Cantidad']
                
                fig_pac = px.pie(
                    df_fac_pac, names='Facultad', values='Cantidad',
                    hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pac = aplicar_estilo_powerbi_pie(fig_pac, "PAC por Facultad")
                st.plotly_chart(fig_pac, use_container_width=True)
            else:
                st.info("Sin datos PAC disponibles.")

        with col_g2:
            st.markdown("##### Incubadoras")
            if dict_inc and hoja_inc_nombre in dict_inc:
                df_inc_activa = dict_inc[hoja_inc_nombre]
                col_fac_inc = next((c for c in df_inc_activa.columns if 'facultad' in c.lower()), None)
                if col_fac_inc:
                    df_fac_inc = df_inc_activa[col_fac_inc].value_counts().reset_index()
                    df_fac_inc.columns = ['Facultad', 'Cantidad']
                    
                    fig_inc = px.pie(
                        df_fac_inc, names='Facultad', values='Cantidad',
                        hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_inc = aplicar_estilo_powerbi_pie(fig_inc, "Incubadoras por Facultad")
                    st.plotly_chart(fig_inc, use_container_width=True)
                else:
                    st.info("Columna de facultad no encontrada.")
            else:
                st.info("Sin datos de Incubadoras.")

        with col_g3:
            st.markdown("##### BD Innovación")
            if not df_bd.empty:
                col_fac_bd = next((c for c in df_bd.columns if 'facultad' in c.lower()), None)
                if col_fac_bd:
                    df_fac_bd = df_bd[col_fac_bd].value_counts().reset_index()
                    df_fac_bd.columns = ['Facultad', 'Cantidad']
                    
                    fig_bd = px.pie(
                        df_fac_bd, names='Facultad', values='Cantidad',
                        hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_bd = aplicar_estilo_powerbi_pie(fig_bd, "Innovación por Facultad")
                    st.plotly_chart(fig_bd, use_container_width=True)
                else:
                    st.info("Columna de facultad no encontrada.")
            else:
                st.info("Sin datos de Innovación.")

    # --- PESTAÑA: PAC ---
    with tab_pac:
        st.subheader("Distribución Detallada - Proyectos PAC por Facultad")
        if not df_pac.empty and 'FACULTAD LÍDER' in df_pac.columns:
            df_p_pac = df_pac.drop_duplicates(subset=['ID']) if 'ID' in df_pac.columns else df_pac
            df_fac_pac = df_p_pac['FACULTAD LÍDER'].value_counts().reset_index()
            df_fac_pac.columns = ['Facultad', 'Cantidad']
            
            fig_pac = px.pie(
                df_fac_pac, names='Facultad', values='Cantidad',
                hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pac = aplicar_estilo_powerbi_pie(fig_pac, "Participación Proyectos PAC por Facultad")
            st.plotly_chart(fig_pac, use_container_width=True)
        else:
            st.info("Sin datos PAC disponibles.")

    # --- PESTAÑA: INCUBADORAS ---
    with tab_inc:
        st.subheader("Distribución Detallada - Incubadoras por Facultad")
        if dict_inc and hoja_inc_nombre in dict_inc:
            df_inc_activa = dict_inc[hoja_inc_nombre]
            col_fac_inc = next((c for c in df_inc_activa.columns if 'facultad' in c.lower()), None)
            if col_fac_inc:
                df_fac_inc = df_inc_activa[col_fac_inc].value_counts().reset_index()
                df_fac_inc.columns = ['Facultad', 'Cantidad']
                
                fig_inc = px.pie(
                    df_fac_inc, names='Facultad', values='Cantidad',
                    hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_inc = aplicar_estilo_powerbi_pie(fig_inc, "Participación Incubadoras por Facultad")
                st.plotly_chart(fig_inc, use_container_width=True)
            else:
                st.info("Columna de facultad no encontrada.")
        else:
            st.info("Sin datos de Incubadoras.")

    # --- PESTAÑA: INNOVACIÓN ---
    with tab_inn:
        st.subheader("Distribución Detallada - BD Innovación por Facultad")
        if not df_bd.empty:
            col_fac_bd = next((c for c in df_bd.columns if 'facultad' in c.lower()), None)
            if col_fac_bd:
                df_fac_bd = df_bd[col_fac_bd].value_counts().reset_index()
                df_fac_bd.columns = ['Facultad', 'Cantidad']
                
                fig_bd = px.pie(
                    df_fac_bd, names='Facultad', values='Cantidad',
                    hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_bd = aplicar_estilo_powerbi_pie(fig_bd, "Participación BD Innovación por Facultad")
                st.plotly_chart(fig_bd, use_container_width=True)
            else:
                st.info("Columna de facultad no encontrada.")
        else:
            st.info("Sin datos de Innovación.")

    st.markdown("---")
    st.markdown("### Tablas de Detalle General")
    tab1, tab2, tab3 = st.tabs(["Proyectos PAC", "Incubadoras", "BD Innovación"])
    with tab1:
        st.dataframe(df_pac, use_container_width=True)
    with tab2:
        if dict_inc and hoja_inc_nombre in dict_inc:
            st.dataframe(dict_inc[hoja_inc_nombre], use_container_width=True)
    with tab3:
        st.dataframe(df_bd, use_container_width=True)

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS
# -------------------------------------------------------------
elif app_mode == "Socios Comunitarios":
    st.markdown("### Dirección General de Vinculación con el Medio")
    st.markdown("#### Reporte de proyectos 2026")
    st.markdown("##### UNIACC")
    st.markdown("---")
    
    st.title("Red de Socios Comunitarios")
    st.markdown("Extracción directa de organizaciones y facultades, incluyendo el nombre del proyecto asociado.")
    
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
                df_grafico, x='Cantidad de Entidades', y='Facultad', orientation='h',
                text='Cantidad de Entidades', color='Cantidad de Entidades', color_continuous_scale='Blues'
            )
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
