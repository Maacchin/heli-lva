# Comparação de Medições Acelerometro e dynaloggers

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import scipy as sc
import plotly.express as px
from datetime import datetime
import helimod # Módulo de funções comuns do projeto

# %% Colocar o seu caminho da pasta Medições aqui
path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts\Medições"
os.chdir(path)

# %% Carregar informação dos Dynaloggers e Acelerometro

dyna1_data = pd.read_csv('waveform_Pedal_090325-1343.csv', sep = ';')
dyna2_data = pd.read_csv('waveform_Motor_090325-1426.csv', sep = ';')
dyna3_data = pd.read_csv('waveform_Esquerdo_090325-1647.csv', sep = ';')
dyna4_data = pd.read_csv('waveform_Direito_090325-1420.csv', sep = ';')
acc_data = pd.read_csv('Accelerometer_wo_excitation_Test1.csv', sep = ';')

# %% Calcular o RMS de cada um
dyna1_data.at[0, 'RMS'] = helimod.rms(dyna1_data['Vertical'].to_numpy())
dyna2_data.at[0, 'RMS'] = helimod.rms(dyna2_data['Vertical'].to_numpy())
dyna3_data.at[0, 'RMS'] = helimod.rms(dyna3_data['Vertical'].to_numpy())
dyna4_data.at[0, 'RMS'] = helimod.rms(dyna4_data['Vertical'].to_numpy())
acc_data.at[0, 'RMS']   = helimod.rms(acc_data['Vertical'].to_numpy())

# %% Suavização do Plot e Pré processamento

helimod.filtragem_hanning(dyna1_data)
helimod.filtragem_hanning(dyna2_data)
helimod.filtragem_hanning(dyna3_data)
helimod.filtragem_hanning(dyna4_data)
helimod.filtragem_hanning(acc_data)

helimod.filtragem_lowpass(dyna1_data, 300, 1000, 4)
helimod.filtragem_lowpass(dyna2_data, 300, 1000, 4)
helimod.filtragem_lowpass(dyna3_data, 300, 1000, 4)
helimod.filtragem_lowpass(dyna4_data, 300, 1000, 4)
helimod.filtragem_lowpass(acc_data, 300, 1000, 4)

# %% FFT

nfft = 10000
helimod.fft_minha(dyna1_data, nfft)
helimod.fft_minha(dyna2_data, nfft)
helimod.fft_minha(dyna3_data, nfft)
helimod.fft_minha(dyna4_data, nfft)
helimod.fft_minha(acc_data, nfft)


# %% Nivel de vibração

helimod.nv_minha(dyna1_data, dyna1_data['FFT_Mag'])
helimod.nv_minha(dyna2_data, dyna2_data['FFT_Mag'])
helimod.nv_minha(dyna3_data, dyna3_data['FFT_Mag'])
helimod.nv_minha(dyna4_data, dyna4_data['FFT_Mag'])
helimod.nv_minha(acc_data, acc_data['FFT_Mag'])

# %% Densidade Espectral Ruido Branco (PSD)

helimod.psd_minha(dyna1_data, 6400, nfft)
helimod.psd_minha(dyna2_data, 5040, nfft)
helimod.psd_minha(dyna3_data, 5040, nfft)
helimod.psd_minha(dyna4_data, 5040, nfft)
helimod.psd_minha(acc_data, 6000, nfft)

del(nfft)

# %% Diferenciação dos Sinais para plottagem
dyna1_data['Sinal'] = 'D1'
dyna2_data['Sinal'] = 'D2'
dyna3_data['Sinal'] = 'D3'
dyna4_data['Sinal'] = 'D4'
acc_data['Sinal']   = 'Acc'

# %% Junção de todos os sinais em um DataFrame só no final
All_data = pd.concat([dyna1_data, dyna2_data, dyna3_data, dyna4_data, acc_data], ignore_index=True)

# %% Plot Histórico Temporal
helimod.plot(All_data, ['Time (s)', 'Vertical_Lowpass'], 'Histórico Temporal', tipo='hf', salvar=False)

# %% Plot FFT
helimod.plot(All_data, ['FFT_Freqs', "FFT_Mag"], "FFT", tipo='fft', salvar=False, log_x=True)

# %% Plot Nivel de Vibração
helimod.plot(All_data, ['FFT_Freqs', "NV"], "NV", tipo='nv', salvar=False, log_x=True)

# %% Plottar a Desnsidade Espectral
helimod.plot(All_data, ['PSD_Freqs', 'PSD_Pxx'], "PSD", tipo='psd', salvar=False, log_x=True, log_y=True)