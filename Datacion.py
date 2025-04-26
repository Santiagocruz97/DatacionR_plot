import pandas as pd
import math

# Datos de los sistemas isotópicos
data = {
    "Sistema Isotópico": ["40K-40Ar", "40K-40Ca", "87Rb-87Sr", "147Sm-143Nd", "238U-206Pb", "235U-207Pb", "176Lu-176Hf", "187Re-187Os", "14C-14N"],
    "Reacción": [
        "40K → 40Ar",
        "40K → 40Ca",
        "87Rb → 87Sr",
        "147Sm → 143Nd",
        "238U → 206Pb",
        "235U → 207Pb",
        "176Lu → 176Hf",
        "187Re → 187Os",
        "14C → 14N"
    ],
    "Semivida (años)": [
        1_248_000_000,
        1_248_000_000,
        48_800_000_000,
        106_000_000_000,
        4_468_000_000,
        703_800_000,
        37_800_000_000,
        41_600_000_000,
        5_730
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

# Crear la tabla
tabla = pd.DataFrame(data)

# Mostrar la tabla
print(tabla)

# Función para seleccionar sistema
def seleccion_sistema(l):
    if l == "40K-40Ar":
        semivida = 1_248_000_000
    elif l == "40K-40Ca":
        semivida = 1_248_000_000
    elif l == "87Rb-87Sr":
        semivida = 48_800_000_000
    elif l == "147Sm-143Nd":
        semivida = 106_000_000_000
    elif l == "238U-206Pb":
        semivida = 4_468_000_000
    elif l == "235U-207Pb":
        semivida = 703_800_000
    elif l == "176Lu-176Hf":
        semivida = 37_800_000_000
    elif l == "187Re-187Os":
        semivida = 41_600_000_000
    elif l == "14C-14N":
        semivida = 5_730
    else:
        semivida = None  # Si ponen algo incorrecto
    return semivida

# Pedir el sistema
l = input("\nSeleccione el sistema que va a usar (ej: 40K-40Ar): ")
semivida = seleccion_sistema(l)

# Verificar que sea válido
if semivida is not None:
    # Calcular la constante de decaimiento λ
    lamda = math.log(2) / semivida
    print(f"\nSemivida del sistema: {semivida} años")
    print(f"Constante de decaimiento λ (a⁻¹): {lamda:.10f}")

    # Pedir valores de n y h
    try:
        n = float(input("\nIngrese la cantidad de átomos padre restantes (n): "))
        h = float(input("Ingrese la cantidad de átomos hijo formados (h): "))

        # Calcular el logaritmo natural
        razon = n / (n + h)
        ln = math.log(razon)
        print(f"\nValor de ln(n/(n+h)): {ln}")

        # Calcular edad t en años
        t = (-1 / lamda) * ln

        # Convertir a millones de años (Ma)
        t_ma = t / 1_000_000

        print(f"\nLa edad calculada es: {t_ma:.2f} Ma")

    except ValueError:
        print("\nError: n y h deben ser números positivos y no nulos.")
else:
    print("\nSistema seleccionado inválido.")

