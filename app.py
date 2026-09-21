import matplotlib.pyplot as plt

# Datos extraídos del gráfico
facultades = [
    'Facultad de Psicología',
    'Facultad de Artes',
    'Facultad de Arquitectura y Diseño',
    'Facultad de Comunicaciones',
    'Facultad de Negocios y Tecnología',
    'Facultad de Ciencias Jurídicas y Sociales'
]

cantidades = [17, 13, 9, 8, 7, 5]

# Colores acordes a la paleta azul
colores = [
    '#1a365d',  # Azul oscuro
    '#2b6cb0',  # Azul medio
    '#3182ce',  # Azul estándar
    '#63b3ed',  # Azul claro
    '#90cdf4',  # Azul suave
    '#cbd5e0'   # Gris claro
]

# Crear figura
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(aspect="equal"))

# Crear gráfico de anillo
wedges, texts, autotexts = ax.pie(
    cantidades,
    labels=facultades,
    autopct=lambda pct: f"{pct:.1f}%",
    pctdistance=0.75,
    colors=colores,
    startangle=90,
    counterclock=False,
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
    rotatelabels=False
)

# Estilar los porcentajes dentro de las rebanadas
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_weight('bold')
    autotext.set_fontsize(9)

# Ajustar etiquetas para evitar solapamiento colocándolas en leyenda externa
ax.legend(
    wedges, 
    facultades,
    title="Facultades",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1)  # Mueve la leyenda completamente fuera del gráfico
)

plt.setp(autotexts, size=10, weight="bold")
plt.title("Distribución por Facultad", fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.show()
