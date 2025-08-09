from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import pandas as pd

df = pd.read_csv("Data/clean_data.csv")

# Separar variables
X = df[['m2_lote',  #x1
        'banos',    #x2
        'estacionamientos', #x3
        'recamaras',    #x4
        'jardin',   #x5
        'Distancia al parque (km)', #x6
        'Distancia a plaza (km)',   #x7
        'Distancia al centro de la ciudad (km)',    #x8
        'robo_de_vehiculo_automotor',   #x9
        'robo_a_negocio',   #x10
        'robo_casa_habitacion']]    #x11

y = df['precio']
X = sm.add_constant(X)

modelo = sm.OLS(y, X).fit()

# Resultados
print(modelo.summary())
