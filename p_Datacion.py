import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import math

# ----------------- Datos -----------------

# Crear tabla de sistemas isotópicos
data = {
    "Sistema Isotópico": ["40K-40Ar", "40K-40Ca", "87Rb-87Sr", "147Sm-143Nd", "238U-206Pb", "235U-207Pb", "176Lu-176Hf", "187Re-187Os", "14C-14N"],
    "Semivida [años]": [
        1.248e9,
        1.248e9,
        4.88e10,
        1.06e11,
        4.468e9,
        7.038e8,
        3.78e10,
        4.16e10,
        5.73e3
    ],
    "Fuente": [
        "Steiger & Jäger (1977)",
        "Steiger & Jäger (1977)",
        "Steiger & Jäger (1977)",
        "Lugmair & Marti (1978)",
        "Jaffey et al. (1971)",
        "Jaffey et al. (1971)",
        "Söderlund et al. (2004)",
        "Smoliar et al. (1996)",
        "Radiocarbon community"
    ]
}
tabla_sistemas = pd.DataFrame(data)

# ----------------- Funciones -----------------

def seleccion_sistema(l):
    semividas = {
        "40K-40Ar": 1_248_000_000,
        "40K-40Ca": 1_248_000_000,
        "87Rb-87Sr": 48_800_000_000,
        "147Sm-143Nd": 106_000_000_000,
        "238U-206Pb": 4_468_000_000,
        "235U-207Pb": 703_800_000,
        "176Lu-176Hf": 37_800_000_000,
        "187Re-187Os": 41_600_000_000,
        "14C-14N": 5_730
    }
    return semividas.get(l, None)

def calcular_edad():
    sistema = variable_sistema.get()
    semivida = seleccion_sistema(sistema)

    if semivida is None:
        messagebox.showerror("Error", "Sistema seleccionado inválido.")
        return

    try:
        n = float(entrada_n.get())
        h = float(entrada_h.get())

        if n <= 0 or h < 0:
            raise ValueError

        lamda = math.log(2) / semivida
        razon = n / (n + h)
        ln = math.log(razon)
        t = (-1 / lamda) * ln
        t_ma = t / 1_000_000

        resultado_texto.set(
            f"📊 Resultado:\n\n"
            f"Semivida: {semivida:.2e} años\n"
            f"Constante λ: {lamda:.10f} a⁻¹\n"
            f"ln(n/(n+h)) = {ln:.5f}\n\n"
            f"🔴 Edad calculada: {t_ma:.2f} Ma 🔴"
        )

    except ValueError:
        messagebox.showerror("Error", "Ingrese valores válidos para n y h (positivos y numéricos).")

# ----------------- Interfaz gráfica -----------------

ventana = tk.Tk()
ventana.title("Cálculo de Edad Isotópica")
ventana.configure(bg="white")

# Título principal
titulo = tk.Label(ventana, text="Cálculo de Edad por Sistemas Isotópicos", font=("Arial", 18, "bold"), bg="white")
titulo.pack(pady=10)

# Imagen de átomo (opcional)
try:
    imagen_atomo = Image.open("atomo.png")  # Asegúrate que esté en tu carpeta
    imagen_atomo = imagen_atomo.resize((80, 80), Image.LANCZOS)
    imagen_atomo = ImageTk.PhotoImage(imagen_atomo)
    label_imagen = tk.Label(ventana, image=imagen_atomo, bg="white")
    label_imagen.pack(pady=5)
except:
    pass

# Tabla organizada
tabla_frame = tk.Frame(ventana, bg="white")
tabla_frame.pack(padx=10, pady=5)

tabla_label = tk.Label(tabla_frame, text="Sistemas disponibles:", font=("Arial", 12, "bold"), bg="white")
tabla_label.pack()

tabla_texto = tk.Text(tabla_frame, height=12, width=75, font=("Courier", 10), wrap=tk.NONE, bg="white")
tabla_texto.pack()

scroll_x = tk.Scrollbar(tabla_frame, orient=tk.HORIZONTAL, command=tabla_texto.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tabla_texto.configure(xscrollcommand=scroll_x.set)

# Mostrar tabla eliminando el índice
tabla_sin_indice = tabla_sistemas.to_string(index=False)
tabla_texto.insert(tk.END, tabla_sin_indice)
tabla_texto.config(state=tk.DISABLED)

# Explicación
explicacion = tk.Label(ventana, text=(
    "Seleccione el sistema isotópico, luego ingrese los átomos padre (n) e hijo (h).\n"
    "La edad se calculará automáticamente."
), font=("Arial", 10), bg="white", justify="center")
explicacion.pack(pady=10)

# Entrada de datos
frame_entradas = tk.Frame(ventana, bg="white")
frame_entradas.pack()

# Lista desplegable para sistema
tk.Label(frame_entradas, text="Sistema isotópico:", bg="white").grid(row=0, column=0, pady=5, padx=5)

variable_sistema = tk.StringVar(ventana)
variable_sistema.set("238U-206Pb")  # valor por defecto

opciones_sistemas = [
    "40K-40Ar", "40K-40Ca", "87Rb-87Sr", "147Sm-143Nd",
    "238U-206Pb", "235U-207Pb", "176Lu-176Hf", "187Re-187Os", "14C-14N"
]
desplegable_sistema = tk.OptionMenu(frame_entradas, variable_sistema, *opciones_sistemas)
desplegable_sistema.grid(row=0, column=1, pady=5, padx=5)

# Entradas de n y h
tk.Label(frame_entradas, text="Átomos padre (n):", bg="white").grid(row=1, column=0, pady=5, padx=5)
entrada_n = tk.Entry(frame_entradas)
entrada_n.grid(row=1, column=1, pady=5, padx=5)

tk.Label(frame_entradas, text="Átomos hijo (h):", bg="white").grid(row=2, column=0, pady=5, padx=5)
entrada_h = tk.Entry(frame_entradas)
entrada_h.grid(row=2, column=1, pady=5, padx=5)

# Botón de calcular
boton_calcular = tk.Button(ventana, text="Calcular Edad", command=calcular_edad, width=20, height=2, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
boton_calcular.pack(pady=15)

# Resultado
resultado_texto = tk.StringVar()
resultado_label = tk.Label(ventana, textvariable=resultado_texto, font=("Arial", 13, "bold"), fg="#d32f2f", bg="white", justify="center")
resultado_label.pack(pady=10)

# Firma
firma = tk.Label(ventana, text="Desarrollado por Santiago Cruz", font=("Arial", 8), fg="gray", bg="white")
firma.pack(pady=10)

ventana.mainloop()
