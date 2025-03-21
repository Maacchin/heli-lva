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
    
    # Sampling rate
    sampling_rate = 1 /  (input_data['Time (s)'][1] - input_data['Time (s)'][0])
    
    # Frequências
    freqs = np.fft.fftfreq(len(signal), d=1/sampling_rate)
    
    # Escalamento
    tamanho_metade = len(input_data['Time (s)']) /2
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
#path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts"
path = r"/home/martinaise/Projetos/heli-lva/Scripts"
os.chdir(path)
os.listdir()

# %% Carregar informação dos Dynaloggers e Acelerometro
dyna1_data = pd.read_csv('Medições/waveform_Pedal_090325-1343.csv', sep=';')
dyna2_data = pd.read_csv('Medições/waveform_Direito_090325-1420.csv', sep=';')
dyna3_data = pd.read_csv('Medições/waveform_Motor_090325-1426.csv', sep=';')
dyna4_data = pd.read_csv('Medições/waveform_Esquerdo_090325-1647.csv', sep=';')

acc_data = pd.read_csv('Medições/accelerometer_356A45.csv', sep=';', header=0)
# Limpando colunas vazias
acc_data = acc_data.loc[:, ~acc_data.columns.str.contains('^Unnamed')]
# Removendo espaço em branco dos headers
acc_data = acc_data.rename(columns=lambda x: x.strip())

# Removendo medições extras
acc_data = acc_data.drop(['X1', 'Y1', 'Z1'], axis='columns')

# Colocando no mesmo formato dos dynaloggers
acc_data = acc_data.rename(columns={"Time": "Time (s)", "X": "Axial", "Y": "Horizontal", "Z": "Vertical"})


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

# %% Plottar Cada Dynalogger no tempo (CÓDIGO TEMPORÁRIO)
fig = px.line(dynaAll_data, x='Time (s)', y="Vertical_filtrado", color="Sinal", title="Histórico temporal")

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


# %% Limpeza
del(a)
del(b)
del(cutoff_freq)
del(fig)
del(figure_name)
del(fs)
del(normal_cutoff)
del(nyq)
del(order)

# %% FFT
fft_dyna1_freq, fft_dyna1_mag, fft_dyna1_espec = fft_minha(dyna1_data)

fft_dyna1_df = pd.DataFrame({'Freqs': fft_dyna1_freq, 'Mag': fft_dyna1_mag })

fig_fft= px.line(fft_dyna1_df, x='Freqs', y='Mag', title="FFT", log_y=True)
fig_fft.show(renderer='browser')


# %% Plot Nivel de Vibração
dyna1_nv = nv(fft_dataframe['fft_magnitude'])

NVporFreq = pd.DataFrame({'Freqs': freqs, 'NV': dyna1_nv })

fig_vibr = px.line(NVporFreq, x='Freqs', y='NV', title='NV Dyna1', log_x=True)

fig_vibr.show(renderer='browser')

figure_name = datetime.now()
figure_name = figure_name.strftime("Plot(NV) %d-%m-%Y %Hh-%Mm-%Ss")
fig_vibr.write_html(f"Plots\{figure_name}.html")
fig_vibr.write_image(f"Plots\{figure_name}.png")

# %% Densidade Espectral Ruido Branco (PSD)
# Usar welch com scipy

# %% Densidade Espectral dos Dynaloggers e Accelerometro

# %% Plottar a Desnsidade Espectral



