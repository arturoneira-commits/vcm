import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================
# 1. CONFIGURACIÓN DE PÁGINA Y TEMATIZACIÓN INSTITUCIONAL
# =============================================================
st.set_page_config(
    page_title="Dirección General de Vinculación con el Medio - UNIACC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de estado de administración
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Ocultar barra superior / menú de edición para usuarios que NO son Admin
hide_top_bar_style = "" if st.session_state.is_admin else """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    </style>
"""

# CSS Personalizado Inspirado en Power BI / Dashboards Ejecutivos
st.markdown(f"""
    {hide_top_bar_style}
    <style>
    /* Estilos generales y fondo neutral moderno */
    .stApp {{
        background-color: #F3F4F6;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }}
    
    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 98% !important;
    }}
    
    /* Header Institucional */
    .header-container {{
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .header-title {{
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
    }}
    .header-subtitle {{
        font-size: 13px;
        color: #93C5FD;
        margin-top: 4px;
        font-weight: 500;
    }}
    
    /* Tarjetas KPI (Power BI Style) */
    .kpi-card {{
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }}
    .kpi-title {{
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 30px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1;
        margin-bottom: 6px;
    }}
    .kpi-subtext {{
        font-size: 11px;
        color: #2563EB;
        font-weight: 600;
    }}
    
    /* Tarjetas de Contenedores y Gráficos */
    .pbi-card {{
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }}
    
    /* Cards de Socios Comunitarios */
    .socio-card {{
        background-color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }}
    .socio-card:hover {{
        border-left-color: #1D4ED8;
        box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    }}
    .socio-title {{
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 8px;
    }}
    .socio-detail {{
        font-size: 13px;
        color: #475569;
        margin-bottom: 4px;
        line-height: 1.4;
    }}
    
    /* Badges y elementos secundarios */
    .admin-badge {{
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid #BFDBFE;
    }}
    
    /* Ajustes visuales para Pestañas Streamlit */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #E2E8F0;
        padding: 4px;
        border-radius: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 38px;
        white-space: pre;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #475569;
        background-color: transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #FFFFFF !important;
        color: #1E3A8A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# =============================================================
# 2. FUNCIONES DE FORMATO Y ESTILO PARA GRÁFICOS (POWER BI STYLE)
# =============================================================
PALETA_INSTITUCIONAL = ['#1E3A8A', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#CBD5E1']

def aplicar_estilo_powerbi_bar(fig, titulo=""):
    """Aplica formato profesional tipo Power BI a gráficos de barra."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=14, color="#0F172A", family="Segoe UI, sans-serif"),
            x=0.02, y=0.95
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", color="#475569", size=12),
        margin=dict(t=50, b=40, l=40, r=20),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            title=None
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            title=None,
            autorange="reversed"
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Segoe UI, sans-serif",
            font_color="#FFFFFF"
        )
    )
    fig.update_traces(
        marker_color="#2563EB",
        marker_line_width=0,
        textposition="outside",
        cliponaxis=False
    )
    return fig

def aplicar_estilo_powerbi_donut(fig, titulo=""):
    """Aplica formato profesional tipo Power BI a gráficos Donut."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(size=14, color="#0F172A", family="Segoe UI, sans-serif"),
            x=0.5, xanchor='center', y=0.95
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", color="#334155", size=11),
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF")
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+value',
        marker=dict(colors=PALETA_INSTITUCIONAL, line=dict(color='#FFFFFF', width=2))
    )
    return fig

# =============================================================
# 3. CARGA DE DATOS ESTÁTICA
# =============================================================
archivos_en_raiz = os.listdir('.') if os.path.exists('.') else []

# Cargar BD Innovación
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
            df_bd = df_bd_raw[~df_bd_raw['Estado'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])].copy()
        else:
            df_bd = df_bd_raw
    except Exception:
        pass

# Cargar Incubadoras
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
            dict_inc[hoja_inc] = dict_inc[hoja_inc][~dict_inc[hoja_inc]['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])]
        
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

# Cargar Proyectos PAC
df_pac = pd.DataFrame()
pac_file = 'reporte_general_PAC_limpio.xlsx' if os.path.exists('reporte_general_PAC_limpio.xlsx') else next((f for f in archivos_en_raiz if 'pac' in f.lower() and f.endswith('.xlsx')), None)
if pac_file:
    try:
        df_pac_raw = pd.read_excel(pac_file, sheet_name=0)
        df_pac_raw.columns = [str(c).strip() for c in df_pac_raw.columns]
        if 'ESTADO DEL PROYECTO' in df_pac_raw.columns:
            df_pac = df_pac_raw[~df_pac_raw['ESTADO DEL PROYECTO'].astype(str).str.lower().isin(['borrador', 'cancelada', 'cancelado'])].copy()
        else:
            df_pac = df_pac_raw
    except Exception:
        pass

# =============================================================
# 4. HEADER Y NAVEGACIÓN LATERAL
# =============================================================
st.markdown("""
    <div class="header-container">
        <div>
            <div class="header-title">Dirección General de Vinculación con el Medio</div>
            <div class="header-subtitle">Universidad UNIACC — Panel Institucional de Control y Gestión</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### Navegación")
opciones_menu = ["Dashboard Principal", "Socios Comunitarios"]

if st.session_state.is_admin:
    st.sidebar.markdown('<div class="admin-badge">Modo Administrador Activo</div>', unsafe_allow_html=True)
    opciones_menu.append("Gestión de Archivos")
    if st.sidebar.button("Cerrar Sesión Admin", use_container_width=True):
        st.session_state.is_admin = False
        st.rerun()
else:
    with st.sidebar.expander("Acceso Administrador"):
        password_input = st.text_input("Contraseña:", type="password")
        if st.button("Ingresar", use_container_width=True):
            if password_input == "admin123":
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")

app_mode = st.sidebar.radio("Ir a la sección:", opciones_menu)

# =============================================================
# 5. DASHBOARD PRINCIPAL
# =============================================================
if app_mode == "Dashboard Principal":
    # Cálculos globales
    tot_pac = df_pac['ID'].nunique() if ('ID' in df_pac.columns and not df_pac.empty) else len(df_pac)
    hoja_inc_nombre = 'Incubadoras' if 'Incubadoras' in dict_inc else (list(dict_inc.keys())[0] if dict_inc else None)
    tot_inc = len(dict_inc[hoja_inc_nombre]) if hoja_inc_nombre and hoja_inc_nombre in dict_inc else 0
    tot_bd = len(df_bd) if not df_bd.empty else 0
    tot_general = tot_pac + tot_inc + tot_bd

    # --- KPIs DE ENCABEZADO ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Iniciativas</div>
                <div class="kpi-value">{tot_general}</div>
                <div class="kpi-subtext">Consolidado Institucional</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Proyectos PAC</div>
                <div class="kpi-value">{tot_pac}</div>
                <div class="kpi-subtext">{(tot_pac/tot_general*100) if tot_general > 0 else 0:.1f}% del Total</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Incubadoras</div>
                <div class="kpi-value">{tot_inc}</div>
                <div class="kpi-subtext">{(tot_inc/tot_general*100) if tot_general > 0 else 0:.1f}% del Total</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">BD Innovación</div>
                <div class="kpi-value">{tot_bd}</div>
                <div class="kpi-subtext">{(tot_bd/tot_general*100) if tot_general > 0 else 0:.1f}% del Total</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FILTROS Y CONTENIDOS MULTI-PESTAÑA ---
    st.markdown("### Análisis por Iniciativa y Facultad")
    tab_todos, tab_pac, tab_inc, tab_inn = st.tabs(["Resumen Global", "Proyectos PAC", "Incubadoras", "Innovación"])

    # PESTAÑA: RESUMEN GLOBAL
    with tab_todos:
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.markdown('<div class="pbi-card">', unsafe_allow_html=True)
            df_resumen_global = pd.DataFrame({
                'Iniciativa': ['Proyectos PAC', 'Incubadoras', 'Innovación'],
                'Cantidad': [tot_pac, tot_inc, tot_bd]
            })
            fig_global = px.pie(
                df_resumen_global, names='Iniciativa', values='Cantidad', hole=0.55
            )
            fig_global = aplicar_estilo_powerbi_donut(fig_global, "Distribución de Iniciativas VcM")
            st.plotly_chart(fig_global, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_g2:
            st.markdown('<div class="pbi-card">', unsafe_allow_html=True)
            # Consolidado de facultades
            list_facs = []
            if not df_pac.empty and 'FACULTAD LÍDER' in df_pac.columns:
                list_facs.extend(df_pac['FACULTAD LÍDER'].dropna().tolist())
            if dict_inc and hoja_inc_nombre in dict_inc:
                col_f = next((c for c in dict_inc[hoja_inc_nombre].columns if 'facultad' in c.lower()), None)
                if col_f:
                    list_facs.extend(dict_inc[hoja_inc_nombre][col_f].dropna().tolist())
            if not df_bd.empty:
                col_f = next((c for c in df_bd.columns if 'facultad' in c.lower()), None)
                if col_f:
                    list_facs.extend(df_bd[col_f].dropna().tolist())
                    
            if list_facs:
                df_fac_tot = pd.Series(list_facs).value_counts().reset_index()
                df_fac_tot.columns = ['Facultad', 'Cantidad']
                fig_bar_tot = px.bar(df_fac_tot.head(7), x='Cantidad', y='Facultad', orientation='h', text='Cantidad')
                fig_bar_tot = aplicar_estilo_powerbi_bar(fig_bar_tot, "Top Facultades por N° de Iniciativas")
                st.plotly_chart(fig_bar_tot, use_container_width=True)
            else:
                st.info("Sin información suficiente de facultades.")
            st.markdown('</div>', unsafe_allow_html=True)

    # PESTAÑA: PAC
    with tab_pac:
        if not df_pac.empty and 'FACULTAD LÍDER' in df_pac.columns:
            df_p_pac = df_pac.drop_duplicates(subset=['ID']) if 'ID' in df_pac.columns else df_pac
            df_fac_pac = df_p_pac['FACULTAD LÍDER'].value_counts().reset_index()
            df_fac_pac.columns = ['Facultad', 'Cantidad']
            
            col_pac1, col_pac2 = st.columns([1, 1])
            with col_pac1:
                fig_pac_bar = px.bar(df_fac_pac, x='Cantidad', y='Facultad', orientation='h', text='Cantidad')
                fig_pac_bar = aplicar_estilo_powerbi_bar(fig_pac_bar, "Proyectos PAC por Facultad")
                st.plotly_chart(fig_pac_bar, use_container_width=True)
            with col_pac2:
                fig_pac_pie = px.pie(df_fac_pac, names='Facultad', values='Cantidad', hole=0.5)
                fig_pac_pie = aplicar_estilo_powerbi_donut(fig_pac_pie, "% Participación PAC por Facultad")
                st.plotly_chart(fig_pac_pie, use_container_width=True)
        else:
            st.info("No existen datos cargados para Proyectos PAC.")

    # PESTAÑA: INCUBADORAS
    with tab_inc:
        if dict_inc and hoja_inc_nombre in dict_inc:
            df_inc_activa = dict_inc[hoja_inc_nombre]
            col_fac_inc = next((c for c in df_inc_activa.columns if 'facultad' in c.lower()), None)
            if col_fac_inc:
                df_fac_inc = df_inc_activa[col_fac_inc].value_counts().reset_index()
                df_fac_inc.columns = ['Facultad', 'Cantidad']
                
                col_inc1, col_inc2 = st.columns([1, 1])
                with col_inc1:
                    fig_inc_bar = px.bar(df_fac_inc, x='Cantidad', y='Facultad', orientation='h', text='Cantidad')
                    fig_inc_bar = aplicar_estilo_powerbi_bar(fig_inc_bar, "Incubadoras por Facultad")
                    st.plotly_chart(fig_inc_bar, use_container_width=True)
                with col_inc2:
                    fig_inc_pie = px.pie(df_fac_inc, names='Facultad', values='Cantidad', hole=0.5)
                    fig_inc_pie = aplicar_estilo_powerbi_donut(fig_inc_pie, "% Participación Incubadoras por Facultad")
                    st.plotly_chart(fig_inc_pie, use_container_width=True)
            else:
                st.info("Columna de facultad no encontrada en datos de Incubadoras.")
        else:
            st.info("No existen datos cargados para Incubadoras.")

    # PESTAÑA: INNOVACIÓN
    with tab_inn:
        if not df_bd.empty:
            col_fac_bd = next((c for c in df_bd.columns if 'facultad' in c.lower()), None)
            if col_fac_bd:
                df_fac_bd = df_bd[col_fac_bd].value_counts().reset_index()
                df_fac_bd.columns = ['Facultad', 'Cantidad']
                
                col_bd1, col_bd2 = st.columns([1, 1])
                with col_bd1:
                    fig_bd_bar = px.bar(df_fac_bd, x='Cantidad', y='Facultad', orientation='h', text='Cantidad')
                    fig_bd_bar = aplicar_estilo_powerbi_bar(fig_bd_bar, "Innovación por Facultad")
                    st.plotly_chart(fig_bd_bar, use_container_width=True)
                with col_bd2:
                    fig_bd_pie = px.pie(df_fac_bd, names='Facultad', values='Cantidad', hole=0.5)
                    fig_bd_pie = aplicar_estilo_powerbi_donut(fig_bd_pie, "% Participación Innovación por Facultad")
                    st.plotly_chart(fig_bd_pie, use_container_width=True)
            else:
                st.info("Columna de facultad no encontrada en BD Innovación.")
        else:
            st.info("No existen datos cargados para BD Innovación.")

    # --- TABLAS DE DETALLE GENERAL ---
    st.markdown("---")
    st.markdown("### Explorador de Registros")
    det_tab1, det_tab2, det_tab3 = st.tabs(["Detalle PAC", "Detalle Incubadoras", "Detalle BD Innovación"])
    
    with det_tab1:
        st.dataframe(df_pac, use_container_width=True)
    with det_tab2:
        if dict_inc and hoja_inc_nombre in dict_inc:
            st.dataframe(dict_inc[hoja_inc_nombre], use_container_width=True)
    with det_tab3:
        st.dataframe(df_bd, use_container_width=True)

# =============================================================
# 6. SOCIOS COMUNITARIOS
# =============================================================
elif app_mode == "Socios Comunitarios":
    st.markdown("### Red de Socios Comunitarios")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtros de Socios")
    tipo_fuente = st.sidebar.radio("Seleccionar origen de datos:", ["Proyectos PAC", "Reporte General Incubadoras"])

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
    else:
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
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Organizaciones / Socios Comunitarios</div>
                    <div class="kpi-value">{total_socios}</div>
                    <div class="kpi-subtext">Entidades externas activas</div>
                </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Facultades Vinculadas</div>
                    <div class="kpi-value">{total_facultades}</div>
                    <div class="kpi-subtext">Cobertura Académica</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="pbi-card">', unsafe_allow_html=True)
        df_grafico = socios_agrupados.assign(facultades=socios_agrupados['facultades'].str.split(', ')).explode('facultades')
        df_grafico = df_grafico.groupby('facultades')['total_convenios'].sum().reset_index()
        df_grafico.columns = ['Facultad', 'Cantidad de Entidades']
        df_grafico = df_grafico.sort_values(by='Cantidad de Entidades', ascending=True)
        
        fig_socios = px.bar(df_grafico, x='Cantidad de Entidades', y='Facultad', orientation='h', text='Cantidad de Entidades')
        fig_socios = aplicar_estilo_powerbi_bar(fig_socios, "Distribución de Socios Comunitarios por Facultad")
        st.plotly_chart(fig_socios, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### Directorio de Socios Comunitarios")
        search_term = st.text_input("Buscar por nombre de organización:", "")
        
        df_mostrar = socios_agrupados.copy()
        if search_term:
            df_mostrar = df_mostrar[df_mostrar[col_org].str.contains(search_term, case=False, na=False)]

        cols = st.columns(2)
        for idx, row in df_mostrar.iterrows():
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="socio-card">
                        <div class="socio-title">{row[col_org]}</div>
                        <div class="socio-detail"><b>Proyectos Asociados:</b> {row['total_convenios']} (IDs: {row['codigos_ids']})</div>
                        <div class="socio-detail"><b>Facultad:</b> {row['facultades']}</div>
                        <div class="socio-detail"><b>Nombre Proyecto:</b> {row['nombres_proyectos']}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron socios comunitarios registrados para la fuente seleccionada.")

# =============================================================
# 7. GESTIÓN DE ARCHIVOS (SOLO ADMIN)
# =============================================================
elif app_mode == "Gestión de Archivos" and st.session_state.is_admin:
    st.markdown("### Administración y Carga de Archivos")
    
    st.markdown('<div class="pbi-card">', unsafe_allow_html=True)
    st.subheader("Eliminar Archivo Existente")
    archivos_excel_actuales = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if archivos_excel_actuales:
        archivo_a_borrar = st.selectbox("Selecciona archivo a eliminar:", archivos_excel_actuales)
        if st.button("Eliminar Archivo", type="primary"):
            try:
                os.remove(archivo_a_borrar)
                st.success(f"Archivo '{archivo_a_borrar}' eliminado exitosamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")
    else:
        st.info("No existen archivos Excel cargados actualmente.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="pbi-card">', unsafe_allow_html=True)
    st.subheader("Cargar Nuevo Archivo al Sistema")
    dataset_choice = st.selectbox("Selecciona destino de la base de datos:", ["BD Innovación", "Reporte General Incubadoras", "Proyectos PAC"])
    uploaded_file = st.file_uploader("Selecciona archivo (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        if st.button("Guardar Archivo"):
            try:
                if "Innovación" in dataset_choice:
                    nombre_guardado = "bd_innovacion.xlsx"
                elif "Incubadoras" in dataset_choice:
                    nombre_guardado = "reporte_general_incubadoras.xlsx"
                else:
                    nombre_guardado = "reporte_general_PAC_limpio.xlsx"
                
                with open(nombre_guardado, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"Archivo guardado como '{nombre_guardado}' correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar archivo: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
