from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import math
import plotly.graph_objs as go
from scipy import stats
from scipy.stats import chi2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    graphJSON = None
    resultados = {}

    if request.method == 'POST':
        # Leer archivo CSV
        file = request.files['file']
        if file:
            datos = pd.read_csv(file)
            datos.columns = datos.columns.str.strip().str.lower()

            if 'x' not in datos.columns or 'y' not in datos.columns:
                return render_template('index.html', error="El CSV debe tener columnas 'x' y 'y'.")

            x = datos['x'].astype(str).str.replace(',', '.').astype(float).values
            y = datos['y'].astype(str).str.replace(',', '.').astype(float).values

            # Parámetros
            porcentaje_error = float(request.form['error']) / 100
            sigma = int(request.form['sigma'])

            err_x = x * porcentaje_error
            err_y = y * porcentaje_error

            # Constantes
            semivida_238 = 4_468_000_000
            semivida_235 = 703_800_000
            lamda238 = math.log(2) / semivida_238
            lamda235 = math.log(2) / semivida_235

            # Curva Concordia
            tiempos_ma = np.linspace(0, 4500, 500)
            tiempos = tiempos_ma * 1_000_000
            relacion_206_238 = np.exp(lamda238 * tiempos) - 1
            relacion_207_235 = np.exp(lamda235 * tiempos) - 1

            # Ajuste lineal
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

            # Error edad
            error_relativo = np.mean(err_y / (1 + y))
            incertidumbre_edad_anos = (1 / lamda238) * error_relativo
            incertidumbre_edad_ma = incertidumbre_edad_anos / 1_000_000

            resultados = {
                "edad": f"{edad_ma:.2f}",
                "incertidumbre": f"{incertidumbre_edad_ma:.2f}",
                "mswd": f"{mswd:.2f}",
                "pvalor": f"{p_valor:.3f}"
            }

            # Crear la gráfica
            fig = go.Figure()

            # Curva Concordia
            fig.add_trace(go.Scatter(x=relacion_207_235, y=relacion_206_238, mode='lines', name='Curva Concordia'))

            # Datos experimentales
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Datos experimentales'))

            # Línea de ajuste
            x_fit = np.linspace(min(x), max(x), 100)
            y_fit = slope * x_fit + intercept
            fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name='Ajuste lineal', line=dict(dash='dash')))

            fig.update_layout(
                title="Curva de Concordia U-Pb",
                xaxis_title="207Pb/235U",
                yaxis_title="206Pb/238U",
                hovermode='closest'
            )

            graphJSON = fig.to_json()

    return render_template('index.html', graphJSON=graphJSON, resultados=resultados)

if __name__ == '__main__':
    app.run(debug=True)
