import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Ellipse
from scipy import stats
from scipy.stats import chi2
import csv

def limpiar_encabezados(datos):
    datos.columns = (
        datos.columns
        .str.strip()
        .str.replace("'", "", regex=False)
        .str.replace('"', '', regex=False)
        .str.replace(' ', '', regex=False)
        .str.lower()
    )
    return datos

def verificar_columnas(datos, columnas_requeridas):
    columnas_actuales = datos.columns.tolist()
    faltantes = [col for col in columnas_requeridas if col not in columnas_actuales]
    if faltantes:
        print(f"⚠️ Faltan las siguientes columnas en el CSV: {faltantes}")
        return False
    return True

def detectar_separador(ruta_csv):
    with open(ruta_csv, 'r', newline='', encoding='utf-8') as file:
        sample = file.read(1024)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter

def cargar_y_graficar():
    # Selección del archivo
    ruta_csv = filedialog.askopenfilename(
        title="Seleccione su archivo CSV",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    if not ruta_csv:
        print("No se seleccionó ningún archivo.")
        return

    # Detectar separador
    separador_detectado = detectar_separador(ruta_csv)
    print(f"Separador detectado: '{separador_detectado}'")

    # Cargar CSV
    datos = pd.read_csv(ruta_csv, sep=separador_detectado)
    datos = limpiar_encabezados(datos)

    columnas_requeridas = ['x', 'y']
    if not verificar_columnas(datos, columnas_requeridas):
        return

    x = datos['x'].astype(str).str.replace(',', '.').astype(float).values
    y = datos['y'].astype(str).str.replace(',', '.').astype(float).values

    porcentaje_error = 0.02
    err_x = x * porcentaje_error
    err_y = y * porcentaje_error
    nivel_sigma = 1  # 1σ

    semivida_238 = 4_468_000_000
    semivida_235 = 703_800_000
    lamda238 = math.log(2) / semivida_238
    lamda235 = math.log(2) / semivida_235

    tiempos_ma = np.linspace(0, 4500, 500)
    tiempos = tiempos_ma * 1_000_000
    relacion_206_238 = np.exp(lamda238 * tiempos) - 1
    relacion_207_235 = np.exp(lamda235 * tiempos) - 1

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    y_pred = slope * x + intercept

    residuos = y - y_pred
    n = len(x)
    mswd = np.sum((residuos / err_y) ** 2) / (n - 2)
    gl = n - 2
    p_valor = 1 - chi2.cdf(mswd * gl, gl)

    promedio_206_238 = np.mean(y)
    edad_anos = (1 / lamda238) * math.log(1 + promedio_206_238)
    edad_ma = edad_anos / 1_000_000
    error_relativo = np.mean(err_y / (1 + y))
    incertidumbre_edad_anos = (1 / lamda238) * error_relativo
    incertidumbre_edad_ma = incertidumbre_edad_anos / 1_000_000

    # 📈 Calcular automáticamente los límites de los ejes
    x_min = min(x) * 0.95
    x_max = max(x) * 1.05
    y_min = min(y) * 0.95
    y_max = max(y) * 1.05

    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 10))

    # Graficar Concordia
    ax.plot(relacion_207_235, relacion_206_238, color='blue', label="Curva de Concordia")

    # Etiquetas de edades
    edades_etiquetas = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
    for edad in edades_etiquetas:
        t = edad * 1_000_000
        x_edad = np.exp(lamda235 * t) - 1
        y_edad = np.exp(lamda238 * t) - 1
        ax.scatter(x_edad, y_edad, color='red', zorder=5)
        ax.text(x_edad, y_edad + 0.01, f"{edad} Ma", fontsize=9, ha='center', va='bottom')

    # Datos experimentales y elipses
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
        ax.scatter(x[i], y[i], color='green', s=30)

    # Línea de ajuste
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, color='red', linestyle='--', label='Ajuste lineal')

    ax.set_title(
        f"Curva de Concordia U-Pb\n"
        f"MSWD = {mswd:.3f} | p-valor = {p_valor:.3f}\n"
        f"Edad promedio = {edad_ma:.1f} ± {incertidumbre_edad_ma:.1f} Ma",
        fontsize=14
    )

    ax.set_xlabel(r'$^{207}$Pb/$^{235}$U', fontsize=12)
    ax.set_ylabel(r'$^{206}$Pb/$^{238}$U', fontsize=12)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.grid(True)
    ax.legend()
    plt.show()

# ----------------- Interfaz gráfica principal -----------------

ventana = tk.Tk()
ventana.title("Aplicación Concordia U-Pb")

# Título
titulo = tk.Label(ventana, text="Gráfica de Concordia U-Pb", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

# Instrucciones
instrucciones = tk.Label(ventana, text=(
    "Por favor asegúrese de que el archivo CSV tenga dos columnas:\n"
    "- 'x' para la relación 207Pb/235U\n"
    "- 'y' para la relación 206Pb/238U\n"
    "Separadas por coma (,) o punto y coma (;).\n"
    "No deben tener comillas en los encabezados."
), font=("Arial", 10), justify="center")
instrucciones.pack(padx=20, pady=10)

# Botón
boton_cargar = tk.Button(ventana, text="Cargar CSV y Graficar", command=cargar_y_graficar, width=30, height=2)
boton_cargar.pack(pady=20)

# Firma
firma = tk.Label(ventana, text="Desarrollado por Santiago Cruz", font=("Arial", 8), fg="gray")
firma.pack(pady=10)

ventana.mainloop()
