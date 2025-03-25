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


# %% Funções
def read_data(path, name=None):
    '''
    Função para ler automaticamente os dados .csv de uma pasta de medições
    onde olha pelos nomes waveform para medições dynalogger e para os nomes
    acc para medições sQuadriga

    Parameters
    ----------
    path : string
        Caminho da pasta de medições.

    Returns
    -------
    dataframes : Dict
        Retorna dicionário com todos DataFrames.

    '''    
    
    # Lê os arquivos de um diretório
    files = os.listdir(f"{path}/Medições")
    
    # Contadores para nome dinâmico
    dyna_counter = 1
    acc_counter = 1
    
    # Dicionário vazio para segurar os DataFrames
    dataframes = {}
    
    # Loopar pelos nomes e verificar se contem 'waveform' e 'acc'
    for file in files:  
        if "waveform" in file.lower():
            print(f"Found waveform in: {file}")
            
            # Ler arquivo com CSV usando ; como separador
            file_path = os.path.join(f"{path}/Medições", file)
            df = pd.read_csv(file_path, sep = ';')
            
            # Limpeza de espaços
            df.rename(columns=lambda x: x.strip(), inplace=True)
            
            var_name = f"dyna{dyna_counter}_data"
            dataframes[var_name] = df
            
            dyna_counter += 1
            
        elif "acc" in file.lower():
            print(f"Found acc in: {file}")
            
            # Ler arquivo com CSV usando ; como separador
            file_path = os.path.join(f"{path}/Medições", file)
            df = pd.read_csv(file_path, sep = ';')
            
            # Limpeza de espaços
            df.rename(columns=lambda x: x.strip(), inplace=True)
            
            var_name = f"acc{acc_counter}_data"
            dataframes[var_name] = df
            
            acc_counter += 1
    
    return dataframes

def fig_name(tipo=None):
    
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
    
    return figure_name

def rms(array):
    '''
    Cálculo simples do Root Mean Square usando numpy
    '''
    return(np.sqrt(np.mean(array**2)))

def filtragem_hanning(df, eixo='Vertical'):
    
    # Incorreto (WIP)
    
    window = np.hanning(len(df[eixo]))
    
    df[f"{eixo}_Filtrado"] = df[eixo] * window
    
    
def filtragem_passabaixa(df, eixo='Vertical'):
    # Parametros do filtro (Lowpass)
    cutoff_freq = 300 # Frequência de corte em Hz
    fs = 1000 # Taxa de amostragem em Hz
    nyq = 0.5 * fs
    order = 4 # Ordem do filtro
    normal_cutoff = cutoff_freq / nyq
    b,a = sc.signal.butter(order, normal_cutoff, btype='lowpass')
    
    df[f"{eixo}_Filtrado"] = sc.signal.filtfilt(b, a, df[eixo])

    

def plot(df, salvar=False):
    '''
    Faz o Plot do Histórico temporal e 
    opcionalmente salva a figura na pasta /Plots, a função espera
    um DataFrame com as colunas "Time (s)" e "Vertical"
    '''
    
    fig = px.line(df, x='Freqs', y='Mags', title="FFT", color="Sinal", log_y=True)
    fig.show(renderer='browser')
    
    if salvar:
        figure_name = fig_name('fft')
        fig.write_html(f"Plots\{figure_name}.html")
        fig.write_image(f"Plots\{figure_name}.png")

def fft_minha(input_data, nfft, eixo='Vertical'):
    '''

    Parameters
    ----------
    input_data : DataFrame
        DataFrame que possui os valores para ser feito a FFT.
    nfft : int
        Número para discretização da FFT. Define a quantidade de pontos
        a serem tomados no cálculo
    eixo : str
        Eixo a ser feito a fft, default = 'Vertical'

    Returns
    -------
    fft_df : DataFrame
        Retorna um DataFrame com as colunas de Frequências e Magnitudes.

    '''
    
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
    fft_df = pd.DataFrame({'Freqs':freqs, 'Mag': fft_magnitude})
    return fft_df

def plot_fft(df, salvar=False):
    '''
    Faz o plot da FFT e opcionalmente salva a figura na pasta /Plots, a função espera
    um DataFrame com as colunas "Freqs" e "Mags"
    '''
    
    fig = px.line(df, x='Freqs', y='Mags', title="FFT", color="Sinal", log_y=True)
    fig.show(renderer='browser')
    
    if salvar:
        figure_name = fig_name('fft')
        fig.write_html(f"Plots\{figure_name}.html")
        fig.write_image(f"Plots\{figure_name}.png")


def nv_minha(fft_magnitude):
    nv_vibração = []
    
    fft_magnitude_ms = fft_magnitude * 10
    valor_ref = pow(10, -5)
    
    for i in range(0, len(fft_magnitude_ms)):
       a = fft_magnitude_ms[i] / valor_ref
       nv_vibração.append(20 * np.log10(a))
                       
    return nv_vibração

def nv_plot(df, salvar=False):
    '''
    Faz o plot do Nível de Vibração e opcionalmente salva a figura 
    na pasta /Plots, a função espera um DataFrame com as colunas "Freqs" e "NV"

    '''
    fig = px.line(df, x='Freqs', y='NV', title="NV", color="Sinal", log_y=True)
    fig.show(renderer='browser')
    
    if salvar:
        figure_name = fig_name('nv')
        fig.write_html(f"Plots\{figure_name}.html")
        fig.write_image(f"Plots\{figure_name}.png")
    
def psd_minha():
    pass

def psd_plot():
    pass
# %% Opções do Pandas
# Para poder ver todas as colunas do DataFrame
pd.set_option('display.max_columns', None) 

# %% Mudar para o CWD (Current Working directory) correto
path = r"C:\Users\MartinR\Desktop\Projetos\heli-lva\Scripts"
#path = r"/home/martinaise/Projetos/heli-lva/Scripts"
os.chdir(path)
os.listdir()



# %% Carregar informação dos Dynaloggers e Acelerometro

dfs = read_data(path)

# Pegamos o que queremos das medições
dyna1_data = dfs.get('dyna1_data')
dyna2_data = dfs.get('dyna2_data')
dyna3_data = dfs.get('dyna3_data')
dyna4_data = dfs.get('dyna4_data')
acc_data   = dfs.get('acc2_data')

# Joga o resto fora
del(dfs)

# %% Calcular o RMS de cada um
dyna1_data.at[0, 'RMS'] = rms(dyna1_data['Vertical'].to_numpy())
dyna2_data.at[0, 'RMS'] = rms(dyna2_data['Vertical'].to_numpy())
dyna3_data.at[0, 'RMS'] = rms(dyna3_data['Vertical'].to_numpy())
dyna4_data.at[0, 'RMS'] = rms(dyna4_data['Vertical'].to_numpy())
acc_data.at[0, 'RMS']   = rms(acc_data['Vertical'].to_numpy())


# %% Suavização do Plot e Pré processamento

#filtragem_hanning(dyna4_data)
filtragem_passabaixa(dyna4_data)

# %%
fig1 = px.line(dyna4_data, x = "Time (s)", y = "Vertical")
fig2 = px.line(dyna4_data, x="Time (s)", y= "Vertical_Filtrado")
fig1.show(renderer='browser')
fig2.show(renderer='browser')



# %%


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


# %% FFT

# Tentar construir função que constroi esses dataframes automaticamente depois

nfft = 50

fft_dyna1_df = fft_minha(dyna1_data, nfft)
fft_dyna2_df = fft_minha(dyna2_data, nfft)
fft_dyna3_df = fft_minha(dyna3_data, nfft)
fft_dyna4_df = fft_minha(dyna4_data, nfft)
fft_acc_df = fft_minha(acc_data, nfft)

#fft_dyna1_df = pd.DataFrame({'Freqs': fft_dyna1_freq, 'Mag': fft_dyna1_mag })
#fft_dyna2_df = pd.DataFrame({'Freqs': fft_dyna2_freq, 'Mag': fft_dyna2_mag })
#fft_dyna3_df = pd.DataFrame({'Freqs': fft_dyna3_freq, 'Mag': fft_dyna3_mag })
##fft_dyna4_df = pd.DataFrame({'Freqs': fft_dyna4_freq, 'Mag': fft_dyna4_mag })
#fft_acc_df   = pd.DataFrame({'Freqs': fft_acc_freq, 'Mag': fft_acc_mag })

# Diferenciação dos Sinais
fft_dyna1_df['Sinal'] = 'D1'
fft_dyna2_df['Sinal'] = 'D2'
fft_dyna3_df['Sinal'] = 'D3'
fft_dyna4_df['Sinal'] = 'D4'
fft_acc_df['Sinal'] = 'Acc'

# Junção de todos os sinais em um DataFrame só
fft_all_data_df = pd.concat([fft_dyna1_df, fft_dyna2_df, fft_dyna3_df, fft_dyna4_df, fft_acc_df], ignore_index=True)




# %% Plot Nivel de Vibração

# Tentar construir função que constroi esses dataframes automaticamente depois

dyna1_nv = nv(fft_dyna1_df['Mag'])
dyna2_nv = nv(fft_dyna2_df['Mag'])
dyna3_nv = nv(fft_dyna3_df['Mag'])
dyna4_nv = nv(fft_dyna4_df['Mag'])
acc_nv = nv(fft_acc_df['Mag'])

NVporFreq_dyna1 = pd.DataFrame({'Freqs': fft_dyna1_df['Freqs'], 'NV': dyna1_nv })
NVporFreq_dyna2 = pd.DataFrame({'Freqs': fft_dyna2_df['Freqs'], 'NV': dyna2_nv })
NVporFreq_dyna3 = pd.DataFrame({'Freqs': fft_dyna3_df['Freqs'], 'NV': dyna3_nv })
NVporFreq_dyna4 = pd.DataFrame({'Freqs': fft_dyna4_df['Freqs'], 'NV': dyna4_nv })
NVporFreq_acc   = pd.DataFrame({'Freqs': fft_acc_df['Freqs'],   'NV': acc_nv })

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