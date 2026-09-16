import pandas as pd
import streamlit as st
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(page_title="Dashboard de Proyectos e Innovación", layout="wide", page_icon="📊")

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Inicializar Estado de Sesión para persistir datos modificados/subidos
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
        # Limpieza inicial automática de borradores
        df_inc = df_inc[df_inc['ESTADO DEL PROYECTO'] != 'Borrador'].copy()
        st.session_state.df_inc = df_inc
    except Exception:
        st.session_state.df_inc = pd.DataFrame(columns=['ID', 'PROYECTO', 'ESTADO DEL PROYECTO', 'FACULTAD LÍDER'])

# Sidebar: Navegación y Carga de Archivos
st.sidebar.header("🎛️ Panel de Control")
app_mode = st.sidebar.selectbox("Navegación", ["📊 Dashboard Principal", "📁 Subir y Gestionar Nueva Información"])

dataset_choice = st.sidebar.radio("Seleccionar Base de Datos:", ["BD Innovación", "Reporte General Incubadoras"])

if app_mode == "📁 Subir y Gestionar Nueva Información":
    st.title("📂 Gestión, Limpieza y Actualización de Archivos")
    st.markdown("Sube nuevos archivos Excel para analizarlos, limpiarlos automáticamente (eliminando estados preliminares como *Borrador*) y fusionarlos o reemplazar los datos actuales.")

    uploaded_file = st.file_uploader("Selecciona un archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # Vista previa del archivo subido
            xls_subido = pd.ExcelFile(uploaded_file)
            hoja_seleccionada = st.selectbox("Selecciona la hoja a procesar:", xls_subido.sheet_names)
            df_nuevo = pd.read_excel(uploaded_file, sheet_name=hoja_seleccionada)
            df_nuevo.columns = [c.strip() for c in df_nuevo.columns]
            
            st.write("### Vista previa del archivo subido:")
            st.dataframe(df_nuevo.head())
            
            # Opciones de limpieza automática
            st.subheader("🧹 Reglas de Limpieza Automática")
            limpiar_borrador = st.checkbox("Eliminar automáticamente registros en estado 'Borrador'", value=True)
            
            if limpiar_borrador:
                # Buscar columnas de estado comunes
                col_estado = next((c for c in df_nuevo.columns if 'estado' in c.lower()), None)
                if col_estado:
                    antes = len(df_nuevo)
                    df_nuevo = df_nuevo[df_nuevo[col_estado].astype(str).str.lower() != 'borrador'].copy()
                    despues = len(df_nuevo)
                    st.success(f"Se eliminaron {antes - despues} registros en estado 'Borrador'.")
                else:
                    st.warning("No se detectó una columna explícita de 'estado' para filtrar borradores.")

            # Opciones de almacenamiento
            st.subheader("⚙️ Método de Actualización")
            accion = st.radio("¿Qué deseas hacer con esta información?", ["Reemplazar la base de datos existente", "Agregar (Concatenar) a la base de datos existente"])
            
            if st.button("Aplicar Cambios en el Sistema"):
                if dataset_choice == "BD Innovación":
                    if accion == "Reemplazar la base de datos existente":
                        # Asegurar ID secuencial
                        if 'ID' not in df_nuevo.columns:
                            df_nuevo['ID'] = [f"INN2026{str(i+1).zfill(3)}" for i in range(len(df_nuevo))]
                        st.session_state.df_bd = df_nuevo
                    else:
                        if 'ID' not in df_nuevo.columns:
                            df_nuevo['ID'] = [f"INN2026{str(len(st.session_state.df_bd)+i+1).zfill(3)}" for i in range(len(df_nuevo))]
                        st.session_state.df_bd = pd.concat([st.session_state.df_bd, df_nuevo], ignore_index=True)
                    st.success("¡Base de datos 'BD Innovación' actualizada correctamente!")
                else:
                    if accion == "Reemplazar la base de datos existente":
                        st.session_state.df_inc = df_nuevo
                    else:
                        st.session_state.df_inc = pd.concat([st.session_state.df_inc, df_nuevo], ignore_index=True)
                    st.success("¡Base de datos 'Reporte General Incubadoras' actualizada correctamente!")
                    
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

else:
    # 📊 Dashboard Principal con los datos actuales en session_state
    df_bd = st.session_state.df_bd
    df_inc = st.session_state.df_inc

    st.title("🚀 Dashboard de Iniciativas e Incubación de Proyectos")
    st.markdown("Visualización en tiempo real de los datos activos limpios.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros Globales")

    if dataset_choice == "BD Innovación":
        if 'Facultad' in df_bd.columns:
            facultades = ['Todas'] + sorted(df_bd['Facultad'].dropna().unique().tolist())
            sel_facultad = st.sidebar.selectbox("Facultad", facultades)
        else:
            sel_facultad = 'Todas'
            
        if 'Estado' in df_bd.columns:
            estados = ['Todos'] + sorted(df_bd['Estado'].dropna().unique().tolist())
            sel_estado = st.sidebar.selectbox("Estado", estados)
        else:
            sel_estado = 'Todos'
        
        filtered_df = df_bd.copy()
        if sel_facultad != 'Todas' and 'Facultad' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Facultad'] == sel_facultad]
        if sel_estado != 'Todos' and 'Estado' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Estado'] == sel_estado]
            
        st.subheader("📊 Indicadores Clave - BD Innovación")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Iniciativas", len(filtered_df))
        col2.metric("En Ejecución", len(filtered_df[filtered_df['Estado'].str.lower() == 'en ejecución']) if 'Estado' in filtered_df.columns else 0)
        col3.metric("Finalizados", len(filtered_df[filtered_df['Estado'].str.lower() == 'finalizado']) if 'Estado' in filtered_df.columns else 0)
        col4.metric("Estudiantes Totales", int(filtered_df['Estudiantes'].sum()) if 'Estudiantes' in filtered_df.columns else 0)
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if 'Estado' in filtered_df.columns:
                fig_estado = px.pie(filtered_df, names='Estado', title="Distribución por Estado", hole=0.4)
                st.plotly_chart(fig_estado, use_container_width=True)
        with c2:
            if 'Facultad' in filtered_df.columns:
                fig_fac = px.bar(filtered_df['Facultad'].value_counts().reset_index(), x='count', y='Facultad', orientation='h', title="Iniciativas por Facultad")
                st.plotly_chart(fig_fac, use_container_width=True)
            
        st.subheader("📋 Detalle de Iniciativas de Innovación (IDs Secuenciales)")
        search_query = st.text_input("🔍 Buscar...", "")
        if search_query:
            filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
        st.dataframe(filtered_df, use_container_width=True)

    else:
        if 'FACULTAD LÍDER' in df_inc.columns:
            facultades = ['Todas'] + sorted(df_inc['FACULTAD LÍDER'].dropna().unique().tolist())
            sel_facultad = st.sidebar.selectbox("Facultad Líder", facultades)
        else:
            sel_facultad = 'Todas'
            
        if 'ESTADO DEL PROYECTO' in df_inc.columns:
            estados = ['Todos'] + sorted(df_inc['ESTADO DEL PROYECTO'].dropna().unique().tolist())
            sel_estado = st.sidebar.selectbox("Estado del Proyecto", estados)
        else:
            sel_estado = 'Todos'
        
        filtered_df = df_inc.copy()
        if sel_facultad != 'Todas' and 'FACULTAD LÍDER' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['FACULTAD LÍDER'] == sel_facultad]
        if sel_estado != 'Todos' and 'ESTADO DEL PROYECTO' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ESTADO DEL PROYECTO'] == sel_estado]
            
        st.subheader("📊 Indicadores Clave - Incubadoras")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Proyectos Válidos", len(filtered_df))
        col2.metric("Estudiantes", int(filtered_df['ESTUDIANTES PARTICIPANTES'].sum()) if 'ESTUDIANTES PARTICIPANTES' in filtered_df.columns else 0)
        col3.metric("Beneficiarios", int(filtered_df['BENEFICIARIOS'].sum()) if 'BENEFICIARIOS' in filtered_df.columns else 0)
        col4.metric("Recursos ($)", f"${filtered_df['RECURSOS APROBADOS'].sum():,.0f}" if 'RECURSOS APROBADOS' in filtered_df.columns else 0)
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if 'ESTADO DEL PROYECTO' in filtered_df.columns:
                fig_est = px.pie(filtered_df, names='ESTADO DEL PROYECTO', title="Estado de Proyectos", hole=0.4)
                st.plotly_chart(fig_est, use_container_width=True)
        with c2:
            if 'ÁMBITO DE ACCIÓN' in filtered_df.columns:
                fig_amb = px.bar(filtered_df['ÁMBITO DE ACCIÓN'].value_counts().reset_index(), x='count', y='ÁMBITO DE ACCIÓN', orientation='h', title="Ámbito de Acción")
                st.plotly_chart(fig_amb, use_container_width=True)
            
        st.subheader("📋 Detalle de Proyectos de Incubación")
        search_query = st.text_input("🔍 Buscar...", "")
        if search_query:
            filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
        st.dataframe(filtered_df, use_container_width=True)