# Comparação de Medições Acelerometro e dynaloggers

# Limpeza e Refatoração

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


def nv(fft_magnitude):
    nv_vibração = []
    
    fft_magnitude_ms = fft_magnitude * 10
    valor_ref = pow(10, -5)
    
    for i in range(0, len(fft_magnitude_ms)):
       a = fft_magnitude_ms[i] / valor_ref
       nv_vibração.append(20 * np.log10(a))
                       
    return nv_vibração


def fft_minha(input_data):
    signal = input_data['Vertical'].values
    fft_esc = np.fft.fft(signal)
    
    # Sampling rate (Algo de errado aqui, testando)
    #sampling_rate = 1 /  (input_data['Time (s)'][1] - input_data['Time (s)'][0])
    sampling_rate = 6400
    
    # Frequências
    freqs = np.fft.fftfreq(len(signal), d=1/sampling_rate)
    
    # Escalamento
    tamanho_metade = len(input_data['Time (s)']) //2
    fft_esc_escalado = []
    for i in range(0, len(fft_esc)):
        fft_esc_escalado.append(fft_esc[i] / tamanho_metade)
        
    # Magnitude
    fft_magnitude = np.abs(fft_esc_escalado[:len(fft_esc_escalado)//2])
    fft_magnitude = fft_magnitude[1:]
    

    freqs = freqs[:len(freqs)//2]
    freqs = freqs[1:]
    
    #fft_dataframe = pd.DataFrame({'X':freqs, 'Y': fft_magnitude})
    return freqs, fft_magnitude, fft_esc_escalado

# %% Mudar para o CWD (Current Working directory) correto
path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts"
#path = r"/home/martinaise/Projetos/heli-lva/Scripts"
os.chdir(path)
os.listdir()

# %% Carregar informação dos Dynaloggers e Acelerometro
dyna1_data = pd.read_csv('Medições/waveform_Pedal_090325-1343.csv', sep=';')
dyna2_data = pd.read_csv('Medições/waveform_Direito_090325-1420.csv', sep=';')
dyna3_data = pd.read_csv('Medições/waveform_Motor_090325-1426.csv', sep=';')
dyna4_data = pd.read_csv('Medições/waveform_Esquerdo_090325-1647.csv', sep=';')

acc_data = pd.read_csv('Medições/Accelerometer_wo_excitation_Test1.csv', sep=';', header=0)
# Limpando colunas vazias
acc_data = acc_data.loc[:, ~acc_data.columns.str.contains('^Unnamed')]
# Removendo espaço em branco dos headers
acc_data = acc_data.rename(columns=lambda x: x.strip())

# Removendo medições extras
#acc_data = acc_data.drop(['X1', 'Y1', 'Z1'], axis='columns')

# Colocando no mesmo formato dos dynaloggers
#acc_data = acc_data.rename(columns={"Time": "Time (s)", "X": "Axial", "Y": "Horizontal", "Z": "Vertical"})


# %% Calcular o RMS de cada um
dyna1_data.at[0, 'RMS'] = rms(dyna1_data['Vertical'].to_numpy())
dyna2_data.at[0, 'RMS'] = rms(dyna2_data['Vertical'].to_numpy())
dyna3_data.at[0, 'RMS'] = rms(dyna3_data['Vertical'].to_numpy())
dyna4_data.at[0, 'RMS'] = rms(dyna4_data['Vertical'].to_numpy())
acc_data.at[0, 'RMS']   = rms(acc_data['Vertical'].to_numpy())


# %% Suavização do Plot e Pré processamento

# Tentar Hamming

# Parametros do filtro (Lowpass)
cutoff_freq = 100 # Frequência de corte em Hz
fs = 1000 # Taxa de amostragem em Hz
nyq = 0.5 * fs
order = 4 # Ordem do filtro
normal_cutoff = cutoff_freq / nyq
b,a = sc.signal.butter(order, normal_cutoff, btype='lowpass')

# Aplicação do filtro
dyna1_data['Vertical_filtrado'] = sc.signal.filtfilt(b, a, dyna1_data['Vertical'])
dyna2_data['Vertical_filtrado'] = sc.signal.filtfilt(b, a, dyna2_data['Vertical'])
dyna3_data['Vertical_filtrado'] = sc.signal.filtfilt(b, a, dyna3_data['Vertical'])
dyna4_data['Vertical_filtrado'] = sc.signal.filtfilt(b, a, dyna4_data['Vertical'])
acc_data['Vertical_filtrado']   = sc.signal.filtfilt(b, a, acc_data['Vertical'])


# Diferenciação dos Sinais
dyna1_data['Sinal'] = 'D1'
dyna2_data['Sinal'] = 'D2'
dyna3_data['Sinal'] = 'D3'
dyna4_data['Sinal'] = 'D4'
acc_data['Sinal']   = 'Acc'

# Junção de todos os sinais em um DataFrame só
dynaAll_data = pd.concat([dyna1_data, dyna2_data, dyna3_data, dyna4_data, acc_data], ignore_index=True)

# %% Histórico Temporal de todos os dynaloggers e acelerômetro
fig = px.line(dynaAll_data, x='Time (s)', y="Vertical_filtrado", color="Sinal", title="Histórico temporal")
fig_sem_filtro = px.line(dynaAll_data, x='Time (s)', y="Vertical", color="Sinal", title="Histórico temporal Não Filtrado")

# Formatação do gráfico
fig.update_layout(
     xaxis=dict(showgrid=True), 
     yaxis=dict(showgrid=True)
)

# Display
fig.show(renderer='browser')
fig_sem_filtro.show(renderer='browser')

# Salvar
figure_name = datetime.now()
figure_name = figure_name.strftime("Plot %d-%m-%Y %Hh-%Mm-%Ss")
fig.write_html(f"Plots\{figure_name}.html")
fig.write_image(f"Plots\{figure_name}.png")


# %% Limpeza de variáveis
del(a)
del(b)
del(cutoff_freq)
del(fig)
del(fig_sem_filtro)
del(figure_name)
del(fs)
del(normal_cutoff)
del(nyq)
del(order)
del(dynaAll_data)

# %% FFT

# Tentar construir função que constroi esses dataframes automaticamente depois

fft_dyna1_freq, fft_dyna1_mag, fft_dyna1_espec = fft_minha(dyna1_data)
fft_dyna2_freq, fft_dyna2_mag, fft_dyna2_espec = fft_minha(dyna2_data)
fft_dyna3_freq, fft_dyna3_mag, fft_dyna3_espec = fft_minha(dyna3_data)
fft_dyna4_freq, fft_dyna4_mag, fft_dyna4_espec = fft_minha(dyna4_data)
fft_acc_freq, fft_acc_mag, fft_acc_espec = fft_minha(acc_data)

fft_dyna1_df = pd.DataFrame({'Freqs': fft_dyna1_freq, 'Mag': fft_dyna1_mag })
fft_dyna2_df = pd.DataFrame({'Freqs': fft_dyna2_freq, 'Mag': fft_dyna2_mag })
fft_dyna3_df = pd.DataFrame({'Freqs': fft_dyna3_freq, 'Mag': fft_dyna3_mag })
fft_dyna4_df = pd.DataFrame({'Freqs': fft_dyna4_freq, 'Mag': fft_dyna4_mag })
fft_acc_df   = pd.DataFrame({'Freqs': fft_acc_freq, 'Mag': fft_acc_mag })

# Diferenciação dos Sinais
fft_dyna1_df['Sinal'] = 'D1'
fft_dyna2_df['Sinal'] = 'D2'
fft_dyna3_df['Sinal'] = 'D3'
fft_dyna4_df['Sinal'] = 'D4'
fft_acc_df['Sinal'] = 'Acc'

# Junção de todos os sinais em um DataFrame só
fft_all_data_df = pd.concat([fft_dyna1_df, fft_dyna2_df, fft_dyna3_df, fft_dyna4_df, fft_acc_df], ignore_index=True)

fig_fft= px.line(fft_all_data_df, x='Freqs', y='Mag', title="FFT", color="Sinal", log_y=True)
fig_fft.show(renderer='browser')


# %% Plot Nivel de Vibração

# Tentar construir função que constroi esses dataframes automaticamente depois

dyna1_nv = nv(fft_dyna1_mag)
dyna2_nv = nv(fft_dyna2_mag)
dyna3_nv = nv(fft_dyna3_mag)
dyna4_nv = nv(fft_dyna4_mag)
acc_nv = nv(fft_acc_mag)

NVporFreq_dyna1 = pd.DataFrame({'Freqs': fft_dyna1_freq, 'NV': dyna1_nv })
NVporFreq_dyna2 = pd.DataFrame({'Freqs': fft_dyna2_freq, 'NV': dyna2_nv })
NVporFreq_dyna3 = pd.DataFrame({'Freqs': fft_dyna3_freq, 'NV': dyna3_nv })
NVporFreq_dyna4 = pd.DataFrame({'Freqs': fft_dyna4_freq, 'NV': dyna4_nv })
NVporFreq_acc   = pd.DataFrame({'Freqs': fft_acc_freq,   'NV': acc_nv })

# Diferenciação dos Sinais
NVporFreq_dyna1['Sinal'] = 'D1'
NVporFreq_dyna2['Sinal'] = 'D2'
NVporFreq_dyna3['Sinal'] = 'D3'
NVporFreq_dyna4['Sinal'] = 'D4'
NVporFreq_acc['Sinal']   = 'Acc'

NVporFreq_all = pd.concat([NVporFreq_dyna1, NVporFreq_dyna2, NVporFreq_dyna3, NVporFreq_dyna4, NVporFreq_acc ])

fig_vibr = px.line(NVporFreq_all, x='Freqs', y='NV', title='Nivel de Vibração', color="Sinal" , log_x=True)
fig_vibr.show(renderer='browser')

figure_name = datetime.now()
figure_name = figure_name.strftime("Plot(NV) %d-%m-%Y %Hh-%Mm-%Ss")
fig_vibr.write_html(f"Plots\{figure_name}.html")
fig_vibr.write_image(f"Plots\{figure_name}.png")

# %% Limpeza
del(dyna1_nv)
del(dyna2_nv)
del(dyna3_nv)
del(dyna4_nv)
del(acc_nv)

del(fft_dyna1_df)
del(fft_dyna2_df)
del(fft_dyna3_df)
del(fft_dyna4_df)
del(fft_acc_df)

del(fft_dyna1_mag)
del(fft_dyna2_mag)
del(fft_dyna3_mag)
del(fft_dyna4_mag)
del(fft_acc_mag)


del(fft_dyna1_freq)
del(fft_dyna2_freq)
del(fft_dyna3_freq)
del(fft_dyna4_freq)
del(fft_acc_freq)

del(fft_dyna1_espec)
del(fft_dyna2_espec)
del(fft_dyna3_espec)
del(fft_dyna4_espec)
del(fft_acc_espec)

del(fig_fft)
del(fig_vibr)
del(figure_name)

# %% Densidade Espectral Ruido Branco (PSD)
# Usar welch com scipy

fs = 6400
f, pxx = sc.signal.welch(dyna1_data['Vertical'], fs)

dyna1_data['PSD_Freqs'] = pd.Series(f)
dyna1_data['PSD_Pxx'] = pd.Series(pxx)

fig_psd = px.line(dyna1_data, x="PSD_Freqs", y="PSD_Pxx")
fig_psd.show(rednderer='browser')



# %% Densidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar a Desnsidade Espectral

import numpy as np
import pandas as pd
import scipy.signal as signal
import plotly.graph_objects as go

# Generate a sample signal (replace with your own vibration data)
fs = 1000  # Sampling frequency (samples per second)
t = np.arange(0, 10, 1/fs)  # Time vector (10 seconds)
# Example: signal with a 50 Hz component and some noise
vibration_signal = 0.5 * np.sin(2 * np.pi * 50 * t) + np.random.randn(len(t))

# Compute the Power Spectral Density (PSD) using the Welch method
f, Pxx = signal.welch(vibration_signal, fs, nperseg=1024)



# Plot the PSD using Plotly
fig = go.Figure()

# Plot the PSD
fig.add_trace(go.Scatter(x=f, y=Pxx, mode='lines', name='PSD'))
fig.update_layout(
    title="Power Spectral Density (PSD) via Welch's Method",
    xaxis_title="Frequency (Hz)",
    yaxis_title="Power Spectral Density (dB/Hz)",
    template="plotly_dark"
)

fig.show(renderer='browser')


