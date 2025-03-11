# Comparação Medições Acelerometro e dynaloggers

# %% Bibliotecas
import os
import pandas as pd

# %% Muda para o CWD (Current Working directory) correto
path = "C:\\Users\MartinR\\Desktop\\Projetos\\heli-lva\\Scripts"
os.chdir(path)
os.listdir()

# %% Carregar informação dos Dynaloggers e Acelerometro
data_dyna1 = pd.read_csv('waveform_Pedal_090325-1326.csv', sep=';')
data_dyna2 = pd.read_csv('waveform_Direito_090325-1417.csv', sep=';')
data_dyna3 = pd.read_csv('waveform_Motor_090325-1423.csv', sep=';')
data_dyna4 = pd.read_csv('waveform_Esquerdo_090325-1643.csv', sep=';')

data_acc = pd.read_csv('accelerometer_356A45.csv', sep=';')


# %% Calcular o RMS de cada um

# %% Plottar Cada Dynalogger no tempo

# %% FFT de Tudo

# %% Nivel de Vibração

# %% Densidade Espectral Ruido Branco (PSD)

# %% Desndidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar o espectro (Frequência)

# %% Plottar a Desnsidade Espectral
