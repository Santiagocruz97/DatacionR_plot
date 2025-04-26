import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.patches import Ellipse
from scipy import stats

# 1. Constantes U-Pb
semivida_238 = 4_468_000_000  # años
semivida_235 = 703_800_000    # años

lamda238 = math.log(2) / semivida_238
lamda235 = math.log(2) / semivida_235

# Crear tiempos para la Concordia
tiempos_ma = np.linspace(0, 4500, 500)  # en millones de años
tiempos = tiempos_ma * 1_000_000  # en años

# Relaciones teóricas Concordia
relacion_206_238 = np.exp(lamda238 * tiempos) - 1
relacion_207_235 = np.exp(lamda235 * tiempos) - 1

# 2. Cargar los datos
datos = pd.read_csv('datos_muestras.csv')  # nombre que estás usando ahora

x = datos['Pb207_Pb235'].values
y = datos['Pb206_Pb238'].values
err_x = datos['Pb207_Pb235'].values
err_y = datos['Pb206_Pb238'].values

# 3. Ajuste lineal y MSWD
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

y_pred = slope * x + intercept

residuos = y - y_pred
n = len(x)
mswd = np.sum(residuos**2) / (n - 2)

# 4. Edad promedio de la muestra
promedio_206_238 = np.mean(y)
edad_anos = (1/lamda238) * math.log(1 + promedio_206_238)
edad_ma = edad_anos / 1_000_000

# 5. Calcular incertidumbre de la edad promedio (propagación de error)
error_relativo = np.mean(err_y / (1 + y))  # simplificación del error relativo
incertidumbre_edad_anos = (1/lamda238) * error_relativo
incertidumbre_edad_ma = incertidumbre_edad_anos / 1_000_000  # convertir a millones de años

# 6. Graficar TODO
fig, ax = plt.subplots(figsize=(12, 10))

# Curva Concordia
ax.plot(relacion_207_235, relacion_206_238, color='blue', label="Curva de Concordia")

# Etiquetas de edades estándar
edades_etiquetas = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
for edad in edades_etiquetas:
    t = edad * 1_000_000  # años
    x_edad = np.exp(lamda235 * t) - 1
    y_edad = np.exp(lamda238 * t) - 1
    ax.scatter(x_edad, y_edad, color='red', zorder=5)
    ax.text(x_edad, y_edad + 0.01, f"{edad} Ma", fontsize=9, ha='center', va='bottom')

# Datos experimentales con elipses
for i in range(len(x)):
    elipse = Ellipse((x[i], y[i]), width=err_x[i]*2, height=err_y[i]*2,
                     angle=0, edgecolor='red', facecolor='none', lw=1)
    ax.add_patch(elipse)
    ax.scatter(x[i], y[i], color='green', s=30)

# Línea de ajuste
#x_fit = np.linspace(min(x), max(x), 100)
#y_fit = slope * x_fit + intercept
#ax.plot(x_fit, y_fit, color='red', linestyle='--', label=f'Ajuste lineal')

# Título profesional
ax.set_title(
    f"Curva de Concordia U-Pb\n"
    f"MSWD = {mswd:.3f} | Edad promedio = {edad_ma:.1f} ± {incertidumbre_edad_ma:.1f} Ma",
    fontsize=14
)

# Configurar ejes
ax.set_xlabel(r'$^{207}$Pb/$^{235}$U', fontsize=12)
ax.set_ylabel(r'$^{206}$Pb/$^{238}$U', fontsize=12)
ax.grid(True)
ax.legend()
plt.show()
