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
        if 'ID' not in df_bd.columns or df_bd['ID'].isnull().all():
            df_bd['ID'] = [f"INN2025{str(i+1).zfill(3)}" for i in range(len(df_bd))]
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
        st.session_state.df_inc = pd.DataFrame(columns=['ID', 'PROYECTO', 'ESTADO DEL PROYECTO', 'FACULTAD LÍDER', 'SOCIO COMUNITARIO'])

if 'df_pac' not in st.session_state:
    st.session_state.df_pac = pd.DataFrame({
        'ID': ['PAC001', 'PAC002', 'PAC003', 'PAC004'],
        'Proyecto PAC': ['EcoBarrio', 'Alfabetización Digital', 'Salud Comunitaria', 'Huertas Urbanas'],
        'Socio Comunitario': ['Municipalidad de Santiago', 'Fundación Tejiendo Redes', 'Cesfam San Luis', 'Vecinos Unidos'],
        'Facultad': ['Ingeniería', 'Ciencias Sociales', 'Medicina', 'Arquitectura'],
        'Convenios': [2, 1, 3, 1],
        'Tipo de Iniciativa': ['Innovación Social', 'Capacitación', 'Atención en Salud', 'Medio Ambiente'],
        'Estudiantes': [15, 10, 20, 12]
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
        c1, c2 = st.columns(2)
        with c1:
            if 'Estado' in df_bd.columns:
                fig_estado = px.pie(df_bd, names='Estado', title="Distribución por Estado", hole=0.4)
                st.plotly_chart(fig_estado, use_container_width=True)
        with c2:
            if 'Facultad' in df_bd.columns:
                fig_fac = px.bar(df_bd['Facultad'].value_counts().reset_index(), x='count', y='Facultad', orientation='h', title="Iniciativas por Facultad")
                st.plotly_chart(fig_fac, use_container_width=True)
            
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
        c1, c2 = st.columns(2)
        with c1:
            if 'ESTADO DEL PROYECTO' in df_inc.columns:
                fig_est = px.pie(df_inc, names='ESTADO DEL PROYECTO', title="Estado de Proyectos", hole=0.4)
                st.plotly_chart(fig_est, use_container_width=True)
        with c2:
            if 'ÁMBITO DE ACCIÓN' in df_inc.columns:
                fig_amb = px.bar(df_inc['ÁMBITO DE ACCIÓN'].value_counts().reset_index(), x='count', y='ÁMBITO DE ACCIÓN', orientation='h', title="Ámbito de Acción")
                st.plotly_chart(fig_amb, use_container_width=True)
            
        st.subheader("📋 Detalle de Proyectos de Incubación")
        st.dataframe(df_inc, use_container_width=True)

    else: # Proyectos PAC
        st.subheader("📊 Indicadores Clave - Proyectos PAC")
        if len(df_pac) > 0:
            col1, col2 = st.columns(2)
            col1.metric("Total Proyectos PAC", len(df_pac))
            col2.metric("Estudiantes Totales", int(df_pac['Estudiantes'].sum()) if 'Estudiantes' in df_pac.columns else 0)
            
            st.markdown("---")
            st.dataframe(df_pac, use_container_width=True)
        else:
            st.info("Aún no hay registros cargados para Proyectos PAC.")

# -------------------------------------------------------------
# OPCIÓN 2: SOCIOS COMUNITARIOS (MENÚ PRINCIPAL)
# -------------------------------------------------------------
elif app_mode == "🤝 Socios Comunitarios":
    st.title("🤝 Red de Socios Comunitarios")
    st.markdown("Visualización detallada de los socios comunitarios agrupados por iniciativas PAC e Incubadoras.")
    
    # Selector de qué socio comunitario visualizar
    tipo_socio = st.radio("Seleccionar origen de socios:", ["Proyectos PAC", "Reporte General Incubadoras"], horizontal=True)
    st.markdown("---")
    
    if tipo_socio == "Proyectos PAC":
        df_pac = st.session_state.df_pac
        if len(df_pac) > 0:
            col_socio_pac = next((c for c in df_pac.columns if 'socio' in c.lower()), 'Socio Comunitario')
            col_fac_pac = next((c for c in df_pac.columns if 'facultad' in c.lower()), 'Facultad')
            col_tipo_pac = next((c for c in df_pac.columns if 'tipo' in c.lower()), 'Tipo de Iniciativa')
            col_convenios = 'Convenios' if 'Convenios' in df_pac.columns else None
            
            if col_socio_pac in df_pac.columns:
                socios_agrupados = df_pac.groupby(col_socio_pac).agg(
                    cant_convenios=(col_convenios, 'sum') if col_convenios else (col_socio_pac, 'count'),
                    facultades=(col_fac_pac, lambda x: ", ".join(x.dropna().unique())) if col_fac_pac in df_pac.columns else ('ID', lambda x: "N/A"),
                    tipos=(col_tipo_pac, lambda x: ", ".join(x.dropna().unique())) if col_tipo_pac in df_pac.columns else ('ID', lambda x: "N/A")
                ).reset_index()
                
                cols = st.columns(2)
                for idx, row in socios_agrupados.iterrows():
                    with cols[idx % 2]:
                        st.markdown(f"""
                            <div class="socio-card">
                                <div class="socio-title">🏢 {row[col_socio_pac]}</div>
                                <div class="socio-detail"><b>Cantidad de Convenios / Proyectos:</b> {row['cant_convenios']}</div>
                                <div class="socio-detail"><b>Facultades Involucradas:</b> {row['facultades']}</div>
                                <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No hay registros disponibles para Proyectos PAC.")
            
    else: # Incubadoras
        df_inc = st.session_state.df_inc
        col_socio_inc = next((c for c in df_inc.columns if 'socio' in c.lower() or 'comunitario' in c.lower()), None)
        col_facultad_inc = next((c for c in df_inc.columns if 'facultad' in c.lower()), None)
        col_tipo_inc = next((c for c in df_inc.columns if 'tipo' in c.lower() or 'ambito' in c.lower()), None)
        
        if col_socio_inc:
            socios_inc = df_inc.groupby(col_socio_inc).agg(
                total_proyectos=('PROYECTO' if 'PROYECTO' in df_inc.columns else df_inc.columns[0], 'count'),
                facultades=(col_facultad_inc, lambda x: ", ".join(x.dropna().unique())) if col_facultad_inc else ('PROYECTO', lambda x: "N/A"),
                tipos=(col_tipo_inc, lambda x: ", ".join(x.dropna().unique())) if col_tipo_inc else ('PROYECTO', lambda x: "N/A")
            ).reset_index()
            
            cols = st.columns(2)
            for idx, row in socios_inc.iterrows():
                with cols[idx % 2]:
                    st.markdown(f"""
                        <div class="socio-card">
                            <div class="socio-title">🏢 {row[col_socio_inc]}</div>
                            <div class="socio-detail"><b>Cantidad de Proyectos / Convenios:</b> {row['total_proyectos']}</div>
                            <div class="socio-detail"><b>Facultades Involucradas:</b> {row['facultades']}</div>
                            <div class="socio-detail"><b>Tipo de Iniciativa:</b> {row['tipos']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No se encontró una columna explícita de 'Socio Comunitario' en la base de datos de Incubadoras.")

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
            
            st.subheader("🧹 Reglas de Limpieza Automática")
            limpiar_borrador = st.checkbox("Eliminar automáticamente registros en estado 'Borrador'", value=True)
            
            if limpiar_borrador:
                col_estado = next((c for c in df_nuevo.columns if 'estado' in c.lower()), None)
                if col_estado:
                    antes = len(df_nuevo)
                    df_nuevo = df_nuevo[df_nuevo[col_estado].astype(str).str.lower() != 'borrador'].copy()
                    despues = len(df_nuevo)
                    st.success(f"Se eliminaron {antes - despues} registros en estado 'Borrador'.")
                else:
                    st.warning("No se detectó una columna explícita de 'estado' para filtrar borradores.")

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
