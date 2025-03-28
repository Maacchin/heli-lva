# Plot da Vibração Espectral

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import scipy as sc
import plotly.express as px
from datetime import datetime
import json
#import helimod

# %% Colocar o seu caminho da pasta das medições aqui
path = "C:/Users/MartinR/Desktop/Projetos/heli-lva/Scripts/Medições/Dados_Viagem_100225"
os.chdir(path)
os.listdir()

# %% Funções
def read_json(path):
    dataframes = {}
    esc_counter = 1
    
    files = os.listdir(path)
    
    for file in files:
         path_file = os.path.join(path, file)
         with open(path_file, 'r') as file:
            data = json.load(file)
            
             #Verificar para os arquivos que tem o mesmo metadata da posição
             #para serem as múltiplas medições do mesmo
            
            x = data['x']
            y = data['y']
            z = data['z']
            time = data['time'][0]
            posição = data['spot']
            samplingRate = data['metadata']['samplingRate']
            tempo0 = data ['metadata']['startedAt']
            
            df = pd.DataFrame({
            'Time (s)': time,
            'Axial': x,
            'Horizontal': y,
            'Vertical': z,
            'SampRate': samplingRate,
            'Pos': posição,
            'Tempo0': tempo0
            })
        
            var_name = f'espectral{esc_counter}_data'
            dataframes[var_name] = df
            esc_counter += 1
            
    return dataframes

# %% Carregar informações espectrais in JSON

#Temporário
# Potencialmente usar um dicionário aqui para lidar com a grande quantidade de informações

# esc_counter = 1

# files = os.listdir(f'{path}/Espectrais')

# for file in files:
#     var_name = f'espectral{esc_counter}_data'
#     file_path = os.path.join(f'{path}\Espectrais', file)
    
#     globals()[var_name] = helimod.read_json(file_path)
#     esc_counter += 1
read_json(path)
    
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')


 # %% Calcular o RMS de cada um

# dyna1_data.at[0, 'RMS'] = helimod.rms(dyna1_data['Vertical'].to_numpy())
# dyna2_data.at[0, 'RMS'] = helimod.rms(dyna2_data['Vertical'].to_numpy())
# dyna3_data.at[0, 'RMS'] = helimod.rms(dyna3_data['Vertical'].to_numpy())
# dyna4_data.at[0, 'RMS'] = helimod.rms(dyna4_data['Vertical'].to_numpy())
# acc_data.at[0, 'RMS']   = helimod.rms(acc_data['Vertical'].to_numpy())

# # %% Suavização do Plot e Pré processamento

# helimod.filtragem_hanning(dyna1_data)
# helimod.filtragem_hanning(dyna2_data)
# helimod.filtragem_hanning(dyna3_data)
# helimod.filtragem_hanning(dyna4_data)
# helimod.filtragem_hanning(acc_data)

# helimod.filtragem_lowpass(dyna1_data, 300, 1000, 4)
# helimod.filtragem_lowpass(dyna2_data, 300, 1000, 4)
# helimod.filtragem_lowpass(dyna3_data, 300, 1000, 4)
# helimod.filtragem_lowpass(dyna4_data, 300, 1000, 4)
# helimod.filtragem_lowpass(acc_data, 300, 1000, 4)

# # %% FFT

# nfft = 10000
# helimod.fft_minha(dyna1_data, nfft)
# helimod.fft_minha(dyna2_data, nfft)
# helimod.fft_minha(dyna3_data, nfft)
# helimod.fft_minha(dyna4_data, nfft)
# helimod.fft_minha(acc_data, nfft)


# # %% Nivel de vibração

# helimod.nv_minha(dyna1_data, dyna1_data['FFT_Mag'])
# helimod.nv_minha(dyna2_data, dyna2_data['FFT_Mag'])
# helimod.nv_minha(dyna3_data, dyna3_data['FFT_Mag'])
# helimod.nv_minha(dyna4_data, dyna4_data['FFT_Mag'])
# helimod.nv_minha(acc_data, acc_data['FFT_Mag'])

# # %% Densidade Espectral Ruido Branco (PSD)

# helimod.psd_minha(dyna1_data, 6400, nfft)
# helimod.psd_minha(dyna2_data, 5040, nfft)
# helimod.psd_minha(dyna3_data, 5040, nfft)
# helimod.psd_minha(dyna4_data, 5040, nfft)
# helimod.psd_minha(acc_data, 6000, nfft)

# del(nfft)

# # %% Diferenciação dos Sinais para plottagem
# dyna1_data['Sinal'] = 'D1'
# dyna2_data['Sinal'] = 'D2'
# dyna3_data['Sinal'] = 'D3'
# dyna4_data['Sinal'] = 'D4'
# acc_data['Sinal']   = 'Acc'

# # %% Junção de todos os sinais em um DataFrame só no final
# All_data = pd.concat([dyna1_data, dyna2_data, dyna3_data, dyna4_data, acc_data], ignore_index=True)

# # %% Plot Histórico Temporal
# helimod.plot(All_data, ['Time (s)', 'Vertical_Lowpass'], 'Histórico Temporal', tipo='hf', salvar=False)

# # %% Plot FFT
# helimod.plot(All_data, ['FFT_Freqs', "FFT_Mag"], "FFT", tipo='fft', salvar=False, log_x=True)

# # %% Plot Nivel de Vibração
# helimod.plot(All_data, ['FFT_Freqs', "NV"], "NV", tipo='nv', salvar=False, log_x=True)

# # %% Plottar a Desnsidade Espectral
# helimod.plot(All_data, ['PSD_Freqs', 'PSD_Pxx'], "PSD", tipo='psd', salvar=False, log_x=True, log_y=True)