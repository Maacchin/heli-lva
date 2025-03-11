# Comparação de Medições Acelerometro e dynaloggers

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# %% Opções do Pandas

# Para poder ver todas as colunas do DataFrame
pd.set_option('display.max_columns', None) 

# %% Funções
def rms(array):
    return(np.sqrt(np.mean(np.square(array))))

# %% Mudar para o CWD (Current Working directory) correto
path = "C:\\Users\MartinR\\Desktop\\Projetos\\heli-lva\\Scripts"
os.chdir(path)
os.listdir()

# %% Carregar informação dos Dynaloggers e Acelerometro
dyna1_data = pd.read_csv('waveform_Pedal_090325-1326.csv', sep=';')
dyna2_data = pd.read_csv('waveform_Direito_090325-1417.csv', sep=';')
dyna3_data = pd.read_csv('waveform_Motor_090325-1423.csv', sep=';')
dyna4_data = pd.read_csv('waveform_Esquerdo_090325-1643.csv', sep=';')

acc_data = pd.read_csv('accelerometer_356A45.csv', sep=';', header=0)
# Limpando colunas vazias
acc_data = acc_data.loc[:, ~acc_data.columns.str.contains('^Unnamed')]
# Removendo espaço em branco dos headers
acc_data = acc_data.rename(columns=lambda x: x.strip())


# %% Calcular o RMS de cada um
dyna1_rms = rms(dyna1_data['Vertical'].to_numpy())
dyna2_rms = rms(dyna2_data['Vertical'].to_numpy())
dyna3_rms = rms(dyna3_data['Vertical'].to_numpy())
dyna4_rms = rms(dyna4_data['Vertical'].to_numpy())
acc_rms = rms(acc_data['Z'].to_numpy())


# %% Plottar Cada Dynalogger no tempo
fig = go.Figure(
    data=[go.Bar(y=[2, 1, 3])],
    layout_title_text="A Figure Displayed with fig.show()"
)
fig.show(renderer='browser')
fig.write_html("Plots/teste.html")
fig.write_image("Plots/teste.png")


# %% FFT de Tudo

# %% Nivel de Vibração

# %% Densidade Espectral Ruido Branco (PSD)

# %% Densidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar o espectro (Frequência)

# %% Plottar a Desnsidade Espectral
