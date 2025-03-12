# Comparação de Medições Acelerometro e dynaloggers

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# %% Opções do Pandas

# Para poder ver todas as colunas do DataFrame
pd.set_option('display.max_columns', None) 

# %% Funções
def rms(array):
    return(np.sqrt(np.mean(array**2)))

# %% Mudar para o CWD (Current Working directory) correto
#path = "/home/martinaise/Projetos/heli-lva/Scripts"
#os.chdir(path)
#os.listdir()

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


# %% Suavização do Plot e Pré processamento

dyna1_data['Vertical_Suave'] = dyna1_data['Vertical'].rolling(window=50, center = True).mean()
dyna2_data['Vertical_Suave'] = dyna2_data['Vertical'].rolling(window=50, center = True).mean()
dyna3_data['Vertical_Suave'] = dyna3_data['Vertical'].rolling(window=50, center = True).mean()
dyna4_data['Vertical_Suave'] = dyna4_data['Vertical'].rolling(window=50, center = True).mean()

dyna1_data['Sinal'] = 'S1'
dyna2_data['Sinal'] = 'S2'
dyna3_data['Sinal'] = 'S3'
dyna4_data['Sinal'] = 'S4'


dynaAll_data = pd.concat([dyna1_data, dyna2_data, dyna3_data, dyna4_data], ignore_index=True)


# %% Plottar Cada Dynalogger no tempo (CÓDIGO TEMPORÁRIO)



fig = px.line(dynaAll_data, x='Time (s)', y="Vertical_Suave", color="Sinal")


# Formatação do gráfico
fig.update_layout(
     xaxis=dict(showgrid=True), 
     yaxis=dict(showgrid=True)
)

# Display
fig.show(renderer='browser')
fig.write_html("Plots/Depois.html")
fig.write_image("Plots/Depois.png")



# %% FFT de Tudo

# %% Nivel de Vibração

# %% Densidade Espectral Ruido Branco (PSD)

# %% Densidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar o espectro (Frequência)

# %% Plottar a Desnsidade Espectral
