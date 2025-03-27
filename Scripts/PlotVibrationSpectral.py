# Plot da Vibração Espectral

# %% Bibliotecas
import os
import pandas as pd
import numpy as np
import scipy as sc
import plotly.express as px
from datetime import datetime
import json

# %% Funções

def read_json(nome):
    with open(nome, 'r') as file:
        data = json.load(file)
        
        # Verificar para os arquivos que tem o mesmo metadata da posição
        # para serem as múltiplas medições do mesmo
        
        x = data['x']
        y = data['y']
        z = data['z']
        time = data['time'][0]
        posição = data['spot']
        samplingRate = data['metadata']['samplingRate']
        
    df = pd.DataFrame({
        'Time (s)': time,
        'Axial': x,
        'Horizontal': y,
        'Vertical': z,
        'SampRate': samplingRate,
        'Pos': posição
        })
    
    return df

def clear_df(df):
    # Não tenho certeza se funciona
    df.rename(columns=lambda x: x.strip(), inplace=True)

def rms(array):
    '''
    Cálculo simples do Root Mean Square usando numpy
    '''
    return(np.sqrt(np.mean(array**2)))

def plot(df, eixos, title, tipo, salvar=False, log_x=False, log_y=False):
    '''
    Função genérica para plottar dados com o plotly.express
    '''
    fig = px.line(df, x=eixos[0], y=eixos[1], title=title, color="Sinal", 
                  log_x=log_x, log_y=log_y)
    
    fig.show(renderer='browser')
    
    if salvar == True:
        figure_name = datetime.now()
        match tipo:
            case "ht":
                figure_name = figure_name.strftime("Plot(HT) %d-%m-%Y %Hh-%Mm-%Ss")    
            case "nv":
                figure_name = figure_name.strftime("Plot(NV) %d-%m-%Y %Hh-%Mm-%Ss")
            case "fft":
                figure_name = figure_name.strftime("Plot(FFT) %d-%m-%Y %Hh-%Mm-%Ss")
            case "psd":
                figure_name = figure_name.strftime("Plot(PSD) %d-%m-%Y %Hh-%Mm-%Ss")
            case _:
                figure_name = figure_name.strftime("Plot %d-%m-%Y %Hh-%Mm-%Ss")
        fig.write_html(f"Plots/{figure_name}.html")
        fig.write_image(f"Plots/{figure_name}.png")

def filtragem_hanning(df, eixo='Vertical'):
    '''
    Função para aplicar filtragem de hanning no DataFrame
    '''
    window = np.hanning(len(df[eixo]))
    df[f"{eixo}_Hanning"] = df[eixo] * window
    
def filtragem_lowpass(df, eixo='Vertical'):
    '''
    Função para aplicar filtragem lowpass no DataFrame
    '''
    # Parametros do filtro (Lowpass)
    cutoff_freq = 300 # Frequência de corte em Hz
    fs = 1000 # Taxa de amostragem em Hz
    nyq = 0.5 * fs
    order = 4 # Ordem do filtro
    normal_cutoff = cutoff_freq / nyq
    b,a = sc.signal.butter(order, normal_cutoff, btype='lowpass')
    df[f"{eixo}_Lowpass"] = sc.signal.filtfilt(b, a, df[eixo])

def fft_minha(input_data, nfft, eixo='Vertical'):

    signal = input_data[eixo].values
    fft_esc = np.fft.fft(signal, nfft)
    
    # Sampling rate (Algo de errado aqui, testando)
    sampling_rate = 1 /  (input_data['Time (s)'][1] - input_data['Time (s)'][0])
    
    # Frequências
    freqs = np.fft.fftfreq(nfft , d=1/sampling_rate)
    
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
    # Retorna o dataframe montado
    #fft_df = pd.DataFrame({'Freqs':freqs, 'Mag': fft_magnitude})
    #return fft_df
    input_data['FFT_Freqs'] = pd.Series(freqs)
    input_data['FFT_Mag'] = pd.Series(fft_magnitude)

def nv_minha(df,fft_magnitude):
    nv_vibração = []
    
    fft_magnitude_ms = fft_magnitude * 10
    valor_ref = pow(10, -5)
    
    for i in range(0, len(fft_magnitude_ms)):
       a = fft_magnitude_ms[i] / valor_ref
       nv_vibração.append(20 * np.log10(a))
                       
    df['NV'] = pd.Series(nv_vibração)

def psd_minha(df, fs, nfft):
    n = np.floor(len(df)/8)
    f, pxx = sc.signal.welch(df['Vertical'], fs=fs, nperseg=n, nfft=nfft, detrend=False)
    
    df['PSD_Freqs'] = pd.Series(f)
    df['PSD_Pxx']   = pd.Series(pxx)

# %% Mudar para o CWD (Current Working directory) correto
path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts\Medições\Dados_Viagem_100225"
#path = r"/home/martinaise/Projetos/heli-lva/Scripts/Medições"
os.chdir(path)
os.listdir()

# %% Carregar informações espectrais in JSON

#Temporário
# Potencialmente usar um dicionário aqui para lidar com a grande quantidade de informações

esc_counter = 1

files = os.listdir(f'{path}/Espectrais')

for file in files:
    var_name = f'espectral{esc_counter}_data'
    file_path = os.path.join(f'{path}\Espectrais', file)
    
    globals()[var_name] = read_json(file_path)
    esc_counter += 1
    
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')
#dyna1 = read_json('SeatTrackL-Traveling-100225-07h05m36s.json')


# %%

#dyna1_data = pd.read_csv('waveform_Pedal_090325-1343.csv', sep = ';')
#dyna2_data = pd.read_csv('waveform_Motor_090325-1426.csv', sep = ';')
#dyna3_data = pd.read_csv('waveform_Esquerdo_090325-1647.csv', sep = ';')
#dyna4_data = pd.read_csv('waveform_Direito_090325-1420.csv', sep = ';')
#acc_data = pd.read_csv('Accelerometer_wo_excitation_Test1.csv', sep = ';')

# %% Calcular o RMS de cada um
#dyna1_data.at[0, 'RMS'] = rms(dyna1_data['Vertical'].to_numpy())
#dyna2_data.at[0, 'RMS'] = rms(dyna2_data['Vertical'].to_numpy())
#dyna3_data.at[0, 'RMS'] = rms(dyna3_data['Vertical'].to_numpy())
#dyna4_data.at[0, 'RMS'] = rms(dyna4_data['Vertical'].to_numpy())
#acc_data.at[0, 'RMS']   = rms(acc_data['Vertical'].to_numpy())

# %% Suavização do Plot e Pré processamento

#filtragem_hanning(dyna1_data)
#filtragem_hanning(dyna2_data)
#filtragem_hanning(dyna3_data)
#filtragem_hanning(dyna4_data)
#filtragem_hanning(acc_data)

#filtragem_lowpass(dyna1_data)
#filtragem_lowpass(dyna2_data)
#filtragem_lowpass(dyna3_data)
#filtragem_lowpass(dyna4_data)
#filtragem_lowpass(acc_data)

# %% FFT

#nfft = 10000
#fft_minha(dyna1_data, nfft)
#fft_minha(dyna2_data, nfft)
#fft_minha(dyna3_data, nfft)
#fft_minha(dyna4_data, nfft)
#fft_minha(acc_data, nfft)


# %% Nivel de vibração

#nv_minha(dyna1_data, dyna1_data['FFT_Mag'])
#nv_minha(dyna2_data, dyna2_data['FFT_Mag'])
#nv_minha(dyna3_data, dyna3_data['FFT_Mag'])
#nv_minha(dyna4_data, dyna4_data['FFT_Mag'])
#nv_minha(acc_data, acc_data['FFT_Mag'])

# %% Densidade Espectral Ruido Branco (PSD)

#psd_minha(dyna1_data, 6400, nfft)
#psd_minha(dyna2_data, 5040, nfft)
#psd_minha(dyna3_data, 5040, nfft)
#psd_minha(dyna4_data, 5040, nfft)
#psd_minha(acc_data, 6000, nfft)

#del(nfft)

# %% Diferenciação dos Sinais para plottagem
#dyna1_data['Sinal'] = 'D1'
#dyna2_data['Sinal'] = 'D2'
#dyna3_data['Sinal'] = 'D3'
#dyna4_data['Sinal'] = 'D4'
#acc_data['Sinal']   = 'Acc'

# %% Junção de todos os sinais em um DataFrame só no final
#All_data = pd.concat([dyna1_data, dyna2_data, dyna3_data, dyna4_data, acc_data], ignore_index=True)

# %% Plot Histórico Temporal
#plot(All_data, ['Time (s)', 'Vertical_Lowpass'], 'Histórico Temporal', tipo='hf', salvar=False)

# %% Plot FFT
#plot(All_data, ['FFT_Freqs', "FFT_Mag"], "FFT", tipo='fft', salvar=False, log_x=True)

# %% Plot Nivel de Vibração
#plot(All_data, ['FFT_Freqs', "NV"], "NV", tipo='nv', salvar=False, log_x=True)

# %% Plottar a Desnsidade Espectral
#plot(All_data, ['PSD_Freqs', 'PSD_Pxx'], "PSD", tipo='psd', salvar=False, log_x=True, log_y=True)