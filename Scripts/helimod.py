# Funções
import os
import pandas as pd
import numpy as np
import scipy as sc
import plotly.express as px
from datetime import datetime
import json

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

def rms(array):
    '''
    Cálculo simples do Root Mean Square usando numpy
    '''
    return(np.sqrt(np.mean(array**2)))

def plot(df, eixos, title, tipo, salvar=False, log_x=False, log_y=False):
    '''
    Função genérica para plottar dados com o plotly.express
    
    df: DataFrame a ser plotado
    
    eixos: Um vetor contendo 2 eixos em strings ex: ['Time (s)', 'Vertical']
    
    tipo: O tipo do plot para nomear o arquivo se salvar, opções possíveis ->
    ['ht', 'nv', 'fft', 'psd']
    
    salvar: booleano que controla o salvamento da imagem ou não
    
    log_x, log_y: booleanos que habilitam ou desabilitam o eixo log
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
    
def filtragem_lowpass(df, cutoff_freq, fs, order, eixo='Vertical'):
    '''
    Função para aplicar filtragem lowpass no DataFrame
    
    df: DataFrame a ser filtrado
    
    cutoff_freq: Frequência de corte
    
    fs: Frequência de amostragem
    
    order: Ordem do filtro
    '''
    
    # Parametros do filtro (Lowpass)
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    
    b,a = sc.signal.butter(order, normal_cutoff, btype='lowpass')
    df[f"{eixo}_Lowpass"] = sc.signal.filtfilt(b, a, df[eixo])

def fft_minha(df, nfft, eixo='Vertical'):
    '''
    Função para calcular fft
    
    df: DataFrame a ser calculado
    
    nfft: Número inteiro para discretização da FFT
    
    eixo: Qual eixo vai ser feito o cálculo
    
    '''
    signal = df[eixo].values
    fft_esc = np.fft.fft(signal, nfft)
    
    # Sampling rate (Algo de errado aqui, testando)
    sampling_rate = 1 /  (df['Time (s)'][1] - df['Time (s)'][0])
    
    # Frequências
    freqs = np.fft.fftfreq(nfft , d=1/sampling_rate)
    
    # Escalamento
    tamanho_metade = len(df['Time (s)']) //2
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
    df['FFT_Freqs'] = pd.Series(freqs)
    df['FFT_Mag'] = pd.Series(fft_magnitude)

def nv_minha(df,fft_magnitude):
    '''
    Função simples para calcular o Nível de Vibração de um DataFrame
    
    df: DataFrame a ser calculado
    
    fft_magnitude: a magnitude da FFT anteriormente feita
    '''
    
    nv_vibração = []
    
    fft_magnitude_ms = fft_magnitude * 10
    valor_ref = pow(10, -5)
    
    for i in range(0, len(fft_magnitude_ms)):
       a = fft_magnitude_ms[i] / valor_ref
       nv_vibração.append(20 * np.log10(a))
                       
    df['NV'] = pd.Series(nv_vibração)

def psd_minha(df, fs, nfft):
    '''
    Função simples para cálculo do Power Spectral Density (PSD) usando o método
    de welch
    
    df: DataFrame a ser calculado
    
    fs: Frequência de Amostragem
    
    nfft: Número para discretização
    
    '''
    
    n = np.floor(len(df)/8)
    f, pxx = sc.signal.welch(df['Vertical'], fs=fs, nperseg=n, nfft=nfft, detrend=False)
    
    df['PSD_Freqs'] = pd.Series(f)
    df['PSD_Pxx']   = pd.Series(pxx)
