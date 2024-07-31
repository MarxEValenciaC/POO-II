import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import folium
from folium.plugins import HeatMap
import webbrowser

# Rutas absolutas de las carpetas donde están los archivos
CARPETA_DATOS_educingres = r"D:\university\semestre 3\Programacion Orientada a Objetos 2\datos para el proyecto\datos app\educingres"

# Función para cargar los datos desde los archivos CSV
def cargar_datos(anio):
    try:
        ruta_csv_educingres = os.path.join(CARPETA_DATOS_educingres, f"Dataset{anio}.csv")
        if not os.path.isfile(ruta_csv_educingres):
            messagebox.showerror("Error", f"Archivo CSV para el año {anio} no encontrado en la ruta {ruta_csv_educingres}.")
            return None
        
        df_educingres = pd.read_csv(ruta_csv_educingres)
        if df_educingres.empty:
            messagebox.showerror("Error", f"No hay datos en el archivo CSV para el año {anio}.")
            return None
        
        print(f"Datos cargados para el año {anio}:")
        print(df_educingres.head())
        return df_educingres
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar datos para el año {anio}: {e}")
        return None

# Función para mostrar el mapa de calor y las barras estadísticas
def mostrar_visualizaciones(anio):
    df_educingres = cargar_datos(anio)
    if df_educingres is not None:
        # Crear y mostrar gráficos en la ventana principal
        mostrar_graficos(df_educingres, anio)

        # Filtrar filas con valores NaN en LATITUD y LONGITUD
        df_educingres = df_educingres.dropna(subset=['LATITUD', 'LONGITUD', 'P301A', 'E2'])
        print(f"Datos después de eliminar NaN para el mapa de calor:")
        print(df_educingres[['LATITUD', 'LONGITUD', 'P301A', 'E2']].head())

        # Crear un solo mapa de folium con dos capas
        mapa = folium.Map(location=[-9.19, -75.0152], zoom_start=6)

        # Mapa de calor de Educación
        heat_data_educ = [[row['LATITUD'], row['LONGITUD'], row['P301A']] for index, row in df_educingres.iterrows()]
        HeatMap(heat_data_educ, name="Mapa de Calor Educación", min_opacity=0.2, gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 1: 'red'}).add_to(mapa)

        # Mapa de calor de Ingresos
        heat_data_ingres = [[row['LATITUD'], row['LONGITUD'], row['E2']] for index, row in df_educingres.iterrows()]
        HeatMap(heat_data_ingres, name="Mapa de Calor Ingresos", min_opacity=0.2, gradient={0.2: 'purple', 0.4: 'magenta', 0.6: 'orange', 1: 'red'}).add_to(mapa)

        # Añadir control de capas
        folium.LayerControl().add_to(mapa)

        # Añadir título general
        title_html = '''
                     <h3 align="center" style="font-size:20px"><b>Educación en el Perú según Ingresos</b></h3>
                     '''
        mapa.get_root().html.add_child(folium.Element(title_html))

        # Guardar el mapa como un archivo HTML
        mapa_path = os.path.join(CARPETA_DATOS_educingres, f"mapa_{anio}.html")
        mapa.save(mapa_path)
        abrir_html_en_navegador(mapa_path)

def abrir_html_en_navegador(mapa_path):
    try:
        webbrowser.open_new_tab(mapa_path)  # Abrir el archivo HTML en una nueva pestaña del navegador
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo HTML en el navegador: {e}")

def mostrar_graficos(df_educingres, anio):
    # Verificar que las columnas necesarias existen y son numéricas
    required_columns = ['P207', 'P310E3', 'P301A', 'E2', 'LATITUD', 'LONGITUD']
    for col in required_columns:
        if col not in df_educingres.columns:
            messagebox.showerror("Error", f"La columna {col} no se encuentra en el conjunto de datos.")
            return
        if col not in ['P207', 'P310E3'] and not pd.api.types.is_numeric_dtype(df_educingres[col]):
            messagebox.showerror("Error", f"La columna {col} no contiene datos numéricos.")
            return

    # Llenar NaN en P310E3 con 'Desconocido' o eliminar esas filas
    df_educingres['P310E3'] = df_educingres['P310E3'].fillna('Desconocido')

    # Asegurar que P207 y P310E3 sean de tipo 'category'
    df_educingres['P207'] = df_educingres['P207'].astype('category')
    df_educingres['P310E3'] = df_educingres['P310E3'].astype('category')

    # Verificar si hay valores nulos en P207 después del filtrado
    if df_educingres['P207'].isnull().any():
        df_educingres = df_educingres.dropna(subset=['P207'])

    # Crear gráficos solo si hay datos suficientes
    if df_educingres.empty:
        messagebox.showerror("Error", "No hay datos disponibles para crear los gráficos.")
        return

    # Conteo por sexo y región
    conteo_sexo_region = df_educingres.groupby(['P207', 'P310E3'], observed=True).size().unstack(fill_value=0)

    # Mostrar gráficos en la ventana principal
    fig, ax = plt.subplots(2, 2, figsize=(15, 10))

    # Gráfico de barras apiladas por sexo y región
    if not conteo_sexo_region.empty:
        conteo_sexo_region.T.plot(kind='bar', stacked=True, ax=ax[0, 0], color=['#66b3ff', '#ff9999'])
        ax[0, 0].set_title(f"Distribución por Sexo y Región {anio}")
        ax[0, 0].set_xlabel("Región")
        ax[0, 0].set_ylabel("Cantidad")
        ax[0, 0].legend(["Varón", "Mujer"], title="Sexo")
    else:
        ax[0, 0].text(0.5, 0.5, "No hay datos suficientes para el gráfico de barras.", ha='center', va='center')

    # Gráfico de pastel basado en df_educingres
    conteo_sexo = df_educingres['P207'].value_counts()
    etiquetas = ['Varón', 'Mujer']
    ax[0, 1].pie(conteo_sexo, labels=etiquetas, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#ff9999'])
    ax[0, 1].set_title(f"Distribución por Sexo {anio}")

    # Gráfico de líneas basado en df_educingres
    df_educingres['E2'].plot(kind='line', ax=ax[1, 0], label='E2 (Ingresos)')
    df_educingres['P301A'].plot(kind='line', ax=ax[1, 0], label='P301A (Educación)')
    ax[1, 0].set_title(f"Gráfico de Líneas Educación e Ingresos {anio}")
    ax[1, 0].legend()

    # Gráfico adicional que muestra la relación entre educación e ingresos
    sns.scatterplot(x='E2', y='P301A', data=df_educingres, ax=ax[1, 1])
    ax[1, 1].set_title(f"Relación entre Ingresos y Educación {anio}")
    ax[1, 1].set_xlabel("Ingresos (E2)")
    ax[1, 1].set_ylabel("Educación (P301A)")

    # Guardar las visualizaciones como una imagen
    ruta_imagen = os.path.join(CARPETA_DATOS_educingres, "visualizacion.png")
    plt.savefig(ruta_imagen)
    plt.close(fig)

    # Mostrar la imagen en la interfaz de Tkinter
    mostrar_imagen_en_tkinter(ruta_imagen)

def mostrar_imagen_en_tkinter(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    imagen = ImageTk.PhotoImage(imagen)
    label_imagen.config(image=imagen)
    label_imagen.image = imagen

# Ventana principal
root = tk.Tk()
root.title("Análisis de Datos")
root.geometry("1200x800")

# El frame para los botones
frame_botones = tk.Frame(root)
frame_botones.pack(pady=20)

# Los botones con colores llamativos
boton_2016 = tk.Button(frame_botones, text="2016", command=lambda: mostrar_visualizaciones(2016),
                       bg="#ff9999", fg="white", font=("Arial", 12, "bold"))
boton_2016.pack(side=tk.LEFT, padx=10, pady=10)

boton_2017 = tk.Button(frame_botones, text="2017", command=lambda: mostrar_visualizaciones(2017),
                       bg="#ff9999", fg="white", font=("Arial", 12, "bold"))
boton_2017.pack(side=tk.LEFT, padx=10, pady=10)

boton_2018 = tk.Button(frame_botones, text="2018", command=lambda: mostrar_visualizaciones(2018),
                       bg="#ff9999", fg="white", font=("Arial", 12, "bold"))
boton_2018.pack(side=tk.LEFT, padx=10, pady=10)

boton_2019 = tk.Button(frame_botones, text="2019", command=lambda: mostrar_visualizaciones(2019),
                       bg="#ff9999", fg="white", font=("Arial", 12, "bold"))
boton_2019.pack(side=tk.LEFT, padx=10, pady=10)

boton_2020 = tk.Button(frame_botones, text="2020", command=lambda: mostrar_visualizaciones(2020),
                       bg="#ff9999", fg="white", font=("Arial", 12, "bold"))
boton_2020.pack(side=tk.LEFT, padx=10, pady=10)

boton_2021 = tk.Button(frame_botones, text="2021", command=lambda: mostrar_visualizaciones(2021),
                       bg="#99ccff", fg="white", font=("Arial", 12, "bold"))
boton_2021.pack(side=tk.LEFT, padx=10, pady=10)

boton_2022 = tk.Button(frame_botones, text="2022", command=lambda: mostrar_visualizaciones(2022),
                       bg="#99ff99", fg="white", font=("Arial", 12, "bold"))
boton_2022.pack(side=tk.LEFT, padx=10, pady=10)

# Canvas para añadir el scroll
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Un scrollbar vertical
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configurar el canvas para usar el scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Frame dentro del canvas
frame_contenido = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_contenido, anchor="nw")

# El label para mostrar la imagen dentro del frame
label_imagen = tk.Label(frame_contenido)
label_imagen.pack()

# El bucle principal de la aplicación
root.mainloop()
 