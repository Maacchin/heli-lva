# Comparação de Medições Acelerometro e dynaloggers

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import scipy as sc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


# %% Opções do Pandas

# Para poder ver todas as colunas do DataFrame
pd.set_option('display.max_columns', None) 

# %% Funções
def rms(array):
    return(np.sqrt(np.mean(array**2)))

# %% Mudar para o CWD (Current Working directory) correto
path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts"
os.chdir(path)
os.listdir()

# %% Carregar informação dos Dynaloggers e Acelerometro
dyna1_data = pd.read_csv('Medições/waveform_Pedal_090325-1326.csv', sep=';')
dyna2_data = pd.read_csv('Medições/waveform_Direito_090325-1417.csv', sep=';')
dyna3_data = pd.read_csv('Medições/waveform_Motor_090325-1423.csv', sep=';')
dyna4_data = pd.read_csv('Medições/waveform_Esquerdo_090325-1643.csv', sep=';')

acc_data = pd.read_csv('Medições/accelerometer_356A45.csv', sep=';', header=0)
# Limpando colunas vazias
acc_data = acc_data.loc[:, ~acc_data.columns.str.contains('^Unnamed')]
# Removendo espaço em branco dos headers
acc_data = acc_data.rename(columns=lambda x: x.strip())


# %% Calcular o RMS de cada um
dyna1_data.at[0, 'RMS'] = rms(dyna1_data['Vertical'].to_numpy())
dyna2_data.at[0, 'RMS'] = rms(dyna2_data['Vertical'].to_numpy())
dyna3_data.at[0, 'RMS'] = rms(dyna3_data['Vertical'].to_numpy())
dyna4_data.at[0, 'RMS'] = rms(dyna4_data['Vertical'].to_numpy())
acc_data.at[0, 'RMS'] = rms(acc_data['Z'].to_numpy())


# %% Suavização do Plot e Pré processamento

# Parametros do filtro (Lowpass)
cutoff_freq = 100 # Cuttof frequency in Hz
fs = 1000 # Sampling rate in Hz
nyq = 0.5 * fs
order = 4 
normal_cutoff = cutoff_freq / nyq
b,a = sc.signal.butter(order, normal_cutoff, btype='lowpass')


# Temporário, perguntar para vini sobre
dyna1_data['Vertical_Suave'] = dyna1_data['Vertical'].rolling(window=50, center = True).mean()
dyna2_data['Vertical_Suave'] = dyna2_data['Vertical'].rolling(window=50, center = True).mean()
dyna3_data['Vertical_Suave'] = dyna3_data['Vertical'].rolling(window=50, center = True).mean()
dyna4_data['Vertical_Suave'] = dyna4_data['Vertical'].rolling(window=50, center = True).mean()

# %%

t = dyna1_data['Time (s)']
acc = dyna1_data['Vertical']

filtered_data = sc.signal.filtfilt(b, a, acc)

sinal = pd.DataFrame({ 'Time':t, 'Acc':acc })
sinal['Data'] = 'A'

sinal_filtrado = pd.DataFrame({ 'Time':t, 'Acc':filtered_data })
sinal_filtrado['Data'] = 'B'

all_signal = pd.concat([sinal, sinal_filtrado], ignore_index=True)

fig = px.line(all_signal, x="Time", y="Acc", color='Data')
fig.show(renderer='browser')




# %% Hamming

# Diferenciação dos Sinais
dyna1_data['Sinal'] = 'S1'
dyna2_data['Sinal'] = 'S2'
dyna3_data['Sinal'] = 'S3'
dyna4_data['Sinal'] = 'S4'

# Junção de todos os sinais em um DataFrame só
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

# Salvar
figure_name = datetime.now()
figure_name = figure_name.strftime("Plot %d-%m-%Y %Hh-%Mm-%Ss")
fig.write_html(f"Plots\{figure_name}.html")
fig.write_image(f"Plots\{figure_name}.png")



# %% FFT de Tudo
signal = dyna1_data['Vertical'].values
fft_signal = np.fft.fft(signal)

# 1. Sampling Rate
sampling_rate = 1 / (dyna1_data['Time (s)'][1] - dyna1_data['Time (s)'][0])

freqs = np.fft.fftfreq(len(signal), d=1/sampling_rate)

fft_magnitude = np.abs(fft_signal[:len(fft_signal)//2])
freqs = freqs[:len(freqs//2)]

fft_dataframe = pd.DataFrame({'X':freqs, 'Y': fft_magnitude})

fig_fft= px.line(fft_dataframe, title="A")
fig_fft.show(renderer='browser')

# 2. Perform the FFT and get the magnitude
# 3. Only keep the positive frequencies (FFT is symmetric)


# %% Nivel de Vibração

# %% Densidade Espectral Ruido Branco (PSD)

# Usar welch com scipy

# %% Densidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar o espectro (Frequência) (CÓDIGO TEMPORÁRIO)


# %% Plottar a Desnsidade Espectral

# %% Caixa de areia


