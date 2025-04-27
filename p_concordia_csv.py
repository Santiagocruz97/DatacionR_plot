import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy import stats
from scipy.stats import chi2
import csv

# Variables globales para guardar figura
fig = None
ax = None

# ----------------- Funciones -----------------

def detectar_separador(ruta_csv):
    with open(ruta_csv, 'r', newline='', encoding='utf-8') as file:
        sample = file.read(1024)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter

def verificar_columnas(datos, columnas_requeridas):
    columnas_actuales = datos.columns.tolist()
    faltantes = [col for col in columnas_requeridas if col not in columnas_actuales]
    if faltantes:
        print(f"⚠️ Faltan las siguientes columnas en el CSV: {faltantes}")
        return False
    return True

def cargar_y_graficar():
    global fig, ax

    ruta_csv = filedialog.askopenfilename(
        title="Seleccione su archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    if not ruta_csv:
        print("No se seleccionó ningún archivo.")
        return

    separador_detectado = detectar_separador(ruta_csv)
    print(f"Separador detectado: '{separador_detectado}'")

    datos = pd.read_csv(ruta_csv, sep=separador_detectado)

    columnas_requeridas = ['x', 'y']
    if not verificar_columnas(datos, columnas_requeridas):
        return

    try:
        x = datos['x'].astype(str).str.replace(',', '.').astype(float).values
        y = datos['y'].astype(str).str.replace(',', '.').astype(float).values

        porcentaje_error = float(entrada_error.get()) / 100
        nivel_sigma = int(variable_sigma.get())

        # Color y estilo de la línea de ajuste
        color_ajuste = color_var.get()
        estilo_ajuste = estilo_var.get()

        # Color de curva de concordia y puntos
        color_concordia = color_concordia_var.get()
        color_puntos = color_puntos_var.get()

        err_x = x * porcentaje_error
        err_y = y * porcentaje_error

        # Constantes U-Pb
        semivida_238 = 4_468_000_000  # años
        semivida_235 = 703_800_000    # años
        lamda238 = math.log(2) / semivida_238
        lamda235 = math.log(2) / semivida_235

        # Curva Concordia
        tiempos_ma = np.linspace(0, 4500, 500)
        tiempos = tiempos_ma * 1_000_000
        relacion_206_238 = np.exp(lamda238 * tiempos) - 1
        relacion_207_235 = np.exp(lamda235 * tiempos) - 1

        # Ajuste lineal para MSWD
        slope, intercept, r_value, p_value_reg, std_err = stats.linregress(x, y)
        y_pred = slope * x + intercept
        residuos = y - y_pred
        n = len(x)

        mswd = np.sum((residuos / err_y) ** 2) / (n - 2)
        gl = n - 2
        p_valor = 1 - chi2.cdf(mswd * gl, gl)

        # Edad promedio
        promedio_206_238 = np.mean(y)
        edad_anos = (1 / lamda238) * math.log(1 + promedio_206_238)
        edad_ma = edad_anos / 1_000_000

        # Error de la edad
        error_relativo = np.mean(err_y / (1 + y))
        incertidumbre_edad_anos = (1 / lamda238) * error_relativo
        incertidumbre_edad_ma = incertidumbre_edad_anos / 1_000_000

        # Gráfico
        fig, ax = plt.subplots(figsize=(12, 10))

        # Curva Concordia
        ax.plot(relacion_207_235, relacion_206_238, color=color_concordia, label="Curva de Concordia")

        # Etiquetas de edades sobre la Concordia
        edades_etiquetas = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
        for edad in edades_etiquetas:
            t = edad * 1_000_000
            x_edad = np.exp(lamda235 * t) - 1
            y_edad = np.exp(lamda238 * t) - 1
            ax.scatter(x_edad, y_edad, color='red', zorder=5)
            ax.text(x_edad, y_edad + 0.01, f"{edad} Ma", fontsize=8, ha='center', va='bottom')

        # Datos experimentales
        ax.scatter(x, y, color=color_puntos, label='Datos experimentales')

        # Elipses de error
        for i in range(len(x)):
            elipse = Ellipse(
                (x[i], y[i]),
                width=err_x[i]*2*nivel_sigma,
                height=err_y[i]*2*nivel_sigma,
                angle=0,
                edgecolor='red',
                facecolor='none',
                lw=1,
                alpha=0.5
            )
            ax.add_patch(elipse)

        # Línea de ajuste
        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, color=color_ajuste, linestyle=estilo_ajuste, label="Ajuste lineal")

        ax.set_xlim(min(x)*0.95, max(x)*1.05)
        ax.set_ylim(min(y)*0.95, max(y)*1.05)

        ax.set_xlabel(r'$^{207}$Pb/$^{235}$U')
        ax.set_ylabel(r'$^{206}$Pb/$^{238}$U')
        ax.set_title(
            f"Curva de Concordia + Datos\n"
            f"Edad promedio = {edad_ma:.1f} ± {incertidumbre_edad_ma:.1f} Ma\n"
            f"MSWD = {mswd:.3f} | p-valor = {p_valor:.3f}",
            fontsize=14
        )
        ax.grid(True)
        ax.legend()
        plt.show()

    except ValueError:
        messagebox.showerror("Error", "Verifique que los datos y los parámetros de error sean válidos.")

def guardar_grafica():
    if fig is not None:
        archivo = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[("PNG files", '*.png')])
        if archivo:
            fig.savefig(archivo, dpi=300)
            messagebox.showinfo("Guardado", "Gráfica guardada correctamente.")
    else:
        messagebox.showwarning("Advertencia", "No hay gráfica para guardar.")

# ----------------- Interfaz gráfica -----------------

ventana = tk.Tk()
ventana.title("Concordia U-Pb + Datos Experimentales")
ventana.configure(bg="white")

titulo = tk.Label(ventana, text="Curva de Concordia U-Pb con Datos CSV", font=("Arial", 18, "bold"), bg="white")
titulo.pack(pady=10)

try:
    imagen_atomo = Image.open("atomo.png")
    imagen_atomo = imagen_atomo.resize((80, 80), Image.LANCZOS)
    imagen_atomo = ImageTk.PhotoImage(imagen_atomo)
    label_imagen = tk.Label(ventana, image=imagen_atomo, bg="white")
    label_imagen.pack(pady=5)
except:
    pass

explicacion = tk.Label(ventana, text=(
    "Seleccione su CSV (x = 207Pb/235U, y = 206Pb/238U).\n"
    "Defina error relativo (%) y sigma.\n"
    "Elija color para la Concordia, los puntos y la línea de ajuste.\n"
    "Se calcularán automáticamente MSWD, p-valor, edad promedio."
), font=("Arial", 10), bg="white", justify="center")
explicacion.pack(pady=10)

frame_entradas = tk.Frame(ventana, bg="white")
frame_entradas.pack(pady=10)

tk.Label(frame_entradas, text="Error (%) relativo:", bg="white").grid(row=0, column=0, padx=10, pady=5)
entrada_error = tk.Entry(frame_entradas)
entrada_error.insert(0, "2")
entrada_error.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_entradas, text="Nivel sigma:", bg="white").grid(row=1, column=0, padx=10, pady=5)
variable_sigma = tk.StringVar(ventana)
variable_sigma.set("1")
desplegable_sigma = tk.OptionMenu(frame_entradas, variable_sigma, "1", "2", "3")
desplegable_sigma.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_entradas, text="Color Concordia:", bg="white").grid(row=2, column=0, padx=10, pady=5)
color_concordia_var = tk.StringVar(ventana)
color_concordia_var.set("blue")
color_concordia_menu = tk.OptionMenu(frame_entradas, color_concordia_var, "blue", "red", "green", "black", "orange")
color_concordia_menu.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_entradas, text="Color Puntos:", bg="white").grid(row=3, column=0, padx=10, pady=5)
color_puntos_var = tk.StringVar(ventana)
color_puntos_var.set("green")
color_puntos_menu = tk.OptionMenu(frame_entradas, color_puntos_var, "green", "red", "blue", "black", "orange")
color_puntos_menu.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame_entradas, text="Color Línea Ajuste:", bg="white").grid(row=4, column=0, padx=10, pady=5)
color_var = tk.StringVar(ventana)
color_var.set("black")
color_menu = tk.OptionMenu(frame_entradas, color_var, "black", "red", "blue", "green", "orange")
color_menu.grid(row=4, column=1, padx=10, pady=5)

tk.Label(frame_entradas, text="Estilo Línea Ajuste:", bg="white").grid(row=5, column=0, padx=10, pady=5)
estilo_var = tk.StringVar(ventana)
estilo_var.set("--")
estilo_menu = tk.OptionMenu(frame_entradas, estilo_var, "-", "--", "-.", ":")
estilo_menu.grid(row=5, column=1, padx=10, pady=5)

boton_cargar = tk.Button(ventana, text="Cargar CSV y Graficar", command=cargar_y_graficar,
                         width=25, height=2, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
boton_cargar.pack(pady=10)

boton_guardar = tk.Button(ventana, text="Guardar Gráfica como PNG", command=guardar_grafica,
                          width=25, height=2, bg="#2196F3", fg="white", font=("Arial", 11))
boton_guardar.pack(pady=10)

firma = tk.Label(ventana, text="Desarrollado por Santiago Cruz", font=("Arial", 8), fg="gray", bg="white")
firma.pack(pady=10)

ventana.mainloop()
