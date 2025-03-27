clear all
clc
close all
%%1; Load sample data GPS from CSV file
Input_GPS_File_Name = 'C:\Users\tavin\Desktop\Mestrado\2_teste_automovel\GPS\Viagem_espectral\TracksForEspectral';
jj=7;
    [number]        = xlsread(Input_GPS_File_Name,['Espectral_',num2str(jj)]);   
    [~,~,raw]       = xlsread(Input_GPS_File_Name,['Espectral_',num2str(jj)]);   
    GPS.Longitude = number(:,1);
    GPS.Latitude  = number(:,2);    
    GPS.Velocidade= number(:,3);  
    GPS.Time      = datetime(string(raw(2:end,4)),'Format','dd/MM/yyyy HH:mm:ss',TimeZone="-03:00") ;% 'ConvertFrom','datenum', 'Format','HH:mm:ss');
   
    % figure(1)
    % plot(GPS.Time,GPS.Velocidade)
    % grid on
    % xlim([GPS.Time(1) GPS.Time(end)])

    clear jj Input_GPS_File_Name number raw
%% 2. Load sample Waveform data from JSON file 
Espectrais = ['SeatTrackL-Traveling-100225-07h05m36s.json';...
    'SeatTrackL-Traveling-100225-07h07m21s.json';...
    'SeatTrackL-Traveling-100225-07h08m44s.json';...
    'SeatTrackL-Traveling-100225-07h10m23s.json';...
    'SeatTrackL-Traveling-100225-07h11m56s.json';...
    'SeatTrackL-Traveling-100225-07h13m48s.json';...
    'SeatTrackL-Traveling-100225-07h15m14s.json';...
    'SeatTrackL-Traveling-100225-07h16m38s.json';...
    'SeatTrackL-Traveling-100225-07h18m14s.json';...
    'SeatTrackL-Traveling-100225-07h20m03s.json';...
    'SeatTrackL-Traveling-100225-07h21m29s.json';...
    'SeatTrackL-Traveling-100225-07h22m55s.json';...
    'SeatTrackL-Traveling-100225-07h24m29s.json';...
    'SeatTrackL-Traveling-100225-07h26m41s.json';...
    'SeatTrackL-Traveling-100225-07h28m08s.json';...
    'SeatTrackL-Traveling-100225-07h29m35s.json';...
    'SeatTrackL-Traveling-100225-07h31m13s.json';...
    'SeatTrackL-Traveling-100225-07h32m58s.json';...
    'SeatTrackL-Traveling-100225-07h34m25s.json';...
    'SeatTrackL-Traveling-100225-07h35m52s.json';...
    'SeatTrackL-Traveling-100225-07h37m25s.json';...
    'SeatTrackL-Traveling-100225-07h39m13s.json';...
    'SeatTrackL-Traveling-100225-07h40m37s.json';...
    'SeatTrackL-Traveling-100225-07h42m03s.json';...
    'SeatTrackL-Traveling-100225-07h43m40s.json';...
    'SeatTrackL-Traveling-100225-07h45m24s.json';...
    'SeatTrackL-Traveling-100225-07h46m38s.json';...
    'SeatTrackL-Traveling-100225-07h48m14s.json';...
    'SeatTrackL-Traveling-100225-07h49m47s.json';...
    'SeatTrackL-Traveling-100225-07h51m36s.json';...
    'SeatTrackL-Traveling-100225-07h53m03s.json';...
    'SeatTrackL-Traveling-100225-07h54m28s.json';...
    'SeatTrackL-Traveling-100225-07h56m00s.json'];

Local_Espectrais = 'C:\Users\tavin\Desktop\Mestrado\2_teste_automovel\WaveformData\espectrais100225\';
EspecSample = 0;            
    Inputs_File_Name = Espectrais;
    numfiles = size(Inputs_File_Name,1);
    for k = 1:numfiles
        EspecSample = EspecSample+1; 
        FileNameStored(EspecSample,:) = Inputs_File_Name(k,:);
        str = fileread(append(Local_Espectrais,Inputs_File_Name(k,:))); % dedicated for reading files as text 
        import(EspecSample) = jsondecode(str); % Using the jsondecode function to parse JSON from string
        clear str
        Espectral.startAt(EspecSample)      = datetime(import(EspecSample).metadata.startedAt/1000,'ConvertFrom','posixtime',TimeZone="-03:00");
        % Espectral.finishedAt(EspecSample)   = datetime(import(EspecSample).data{1,1}{4,1},'InputFormat','uuuu-MM-dd''T''HH:mm:ss.000Z',TimeZone="-03:00");
        Espectral.samples(EspecSample)      = length(import(EspecSample).x); % Number of samples
        Espectral.samplingRate(EspecSample) = import(EspecSample).metadata.samplingRate  ; % sample frequency, Hz
        Espectral.duration(EspecSample)     = import(EspecSample).time(end); % Period of mesurement, s
        Espectral.Acceleration.X_g{EspecSample} = import(EspecSample).x;
        Espectral.Acceleration.Y_g{EspecSample} = import(EspecSample).y;
        Espectral.Acceleration.Z_g{EspecSample} = import(EspecSample).z;
		 Espectral.time{EspecSample} = import(EspecSample).time' ;
       % Acceleration in SI and remove DC component   
	    WaveFormAcc.X{EspecSample} =9.8*(Espectral.Acceleration.X_g{EspecSample}-mean(Espectral.Acceleration.X_g{EspecSample}));
        WaveFormAcc.Y{EspecSample} = 9.8*(Espectral.Acceleration.Y_g{EspecSample}-mean(Espectral.Acceleration.Y_g{EspecSample}));
        WaveFormAcc.Z{EspecSample} = 9.8*(Espectral.Acceleration.Z_g{EspecSample}-mean(Espectral.Acceleration.Z_g{EspecSample}));
        
        Espectral.TimeHistory{EspecSample} = [ Espectral.time{EspecSample} WaveFormAcc.Z{EspecSample}];
    end
 clear Inputs_File_Name Local_Espectrais Espectrais numfiles import N_espectrais FileNameStored
       % Gerar os vetores de tempo e vibração dos Danyloggers
for k = 1:EspecSample
        Espectral.dt(k) = 1/Espectral.samplingRate(k);
        WaveFormTime{k} = datetime(Espectral.startAt(k)+ Espectral.dt(k)*seconds(0:Espectral.samples(k)-1),'Format','dd/MM/yyyy HH:mm:ss.SSSS');
end
		WaveFormTimeConc = [ WaveFormTime{1,1}'; WaveFormTime{1,2}'; WaveFormTime{1,3}'; WaveFormTime{1,4}'; WaveFormTime{1,5}'; WaveFormTime{1,6}'; WaveFormTime{1,7}'; WaveFormTime{1,8}'; WaveFormTime{1,9}'; WaveFormTime{1,10}'; WaveFormTime{1,11}'; WaveFormTime{1,12}'; WaveFormTime{1,13}'; WaveFormTime{1,14}'; WaveFormTime{1,15}'; WaveFormTime{1,16}'; WaveFormTime{1,17}'; WaveFormTime{1,18}'; WaveFormTime{1,19}'; WaveFormTime{1,20}'; WaveFormTime{1,21}'; WaveFormTime{1,22}'; WaveFormTime{1,23}'; WaveFormTime{1,24}'; WaveFormTime{1,25}'; WaveFormTime{1,26}' ;WaveFormTime{1,27}'; WaveFormTime{1,28}'; WaveFormTime{1,29}'; WaveFormTime{1,30}'; WaveFormTime{1,31}' ;WaveFormTime{1,32}'; WaveFormTime{1,33}'];
        WaveForAccConc.X = [ WaveFormAcc.X{1,1}; WaveFormAcc.X{1,2}; WaveFormAcc.X{1,3}; WaveFormAcc.X{1,4}; WaveFormAcc.X{1,5}; WaveFormAcc.X{1,6};  WaveFormAcc.X{1,7};WaveFormAcc.X{1,8}; WaveFormAcc.X{1,9}; WaveFormAcc.X{1,10}; WaveFormAcc.X{1,11};WaveFormAcc.X{1,12};WaveFormAcc.X{1,13};WaveFormAcc.X{1,14};WaveFormAcc.X{1,15};WaveFormAcc.X{1,16};WaveFormAcc.X{1,17};WaveFormAcc.X{1,18};WaveFormAcc.X{1,19};WaveFormAcc.X{1,20};WaveFormAcc.X{1,21};WaveFormAcc.X{1,22};WaveFormAcc.X{1,23};WaveFormAcc.X{1,24};WaveFormAcc.X{1,25};WaveFormAcc.X{1,26};WaveFormAcc.X{1,27};WaveFormAcc.X{1,28};WaveFormAcc.Y{1,29};WaveFormAcc.X{1,30};WaveFormAcc.X{1,31};WaveFormAcc.X{1,32};WaveFormAcc.X{1,33}];
        WaveForAccConc.Y = [ WaveFormAcc.Y{1,1}; WaveFormAcc.Y{1,2}; WaveFormAcc.Y{1,3}; WaveFormAcc.Y{1,4}; WaveFormAcc.Y{1,5}; WaveFormAcc.Y{1,6}; WaveFormAcc.Y{1,7}; WaveFormAcc.Y{1,8}; WaveFormAcc.Y{1,9}; WaveFormAcc.Y{1,10}; WaveFormAcc.Y{1,11};WaveFormAcc.Y{1,12};WaveFormAcc.Y{1,13};WaveFormAcc.Y{1,14};WaveFormAcc.Y{1,15};WaveFormAcc.Y{1,16};WaveFormAcc.Y{1,17};WaveFormAcc.Y{1,18};WaveFormAcc.Y{1,19};WaveFormAcc.Y{1,20};WaveFormAcc.Y{1,21};WaveFormAcc.Y{1,22};WaveFormAcc.Y{1,23};WaveFormAcc.Y{1,24};WaveFormAcc.Y{1,25};WaveFormAcc.Y{1,26};WaveFormAcc.Y{1,27};WaveFormAcc.Y{1,28};WaveFormAcc.Y{1,29};WaveFormAcc.Y{1,30};WaveFormAcc.Y{1,31};WaveFormAcc.Y{1,32};WaveFormAcc.Y{1,33}];
        WaveForAccConc.Z = [ WaveFormAcc.Z{1,1}; WaveFormAcc.Z{1,2}; WaveFormAcc.Z{1,3}; WaveFormAcc.Z{1,4}; WaveFormAcc.Z{1,5}; WaveFormAcc.Z{1,6}; WaveFormAcc.Z{1,7}; WaveFormAcc.Z{1,8}; WaveFormAcc.Z{1,9}; WaveFormAcc.Z{1,10}; WaveFormAcc.Z{1,11};WaveFormAcc.Z{1,12};WaveFormAcc.Z{1,13};WaveFormAcc.Z{1,14};WaveFormAcc.Z{1,15};WaveFormAcc.Z{1,16};WaveFormAcc.Z{1,17};WaveFormAcc.Z{1,18};WaveFormAcc.Z{1,19};WaveFormAcc.Z{1,20};WaveFormAcc.Z{1,21};WaveFormAcc.Z{1,22};WaveFormAcc.Z{1,23};WaveFormAcc.Z{1,24};WaveFormAcc.Z{1,25};WaveFormAcc.Z{1,26};WaveFormAcc.Z{1,27};WaveFormAcc.Z{1,28};WaveFormAcc.Z{1,29};WaveFormAcc.Z{1,30};WaveFormAcc.Z{1,31};WaveFormAcc.Z{1,32};WaveFormAcc.Z{1,33}];
        WaveFormAccRMS_Z = rms(WaveForAccConc.Z);

%% 3. Load sample data SQuadriga
squadriga_data = load('C:\Users\tavin\Desktop\Mestrado\2_teste_automovel\WaveformData_SQuadriga\viagem_100225.mat');
X = squadriga_data.x(:,1);
Y = squadriga_data.x(:,2);
Z = squadriga_data.x(:,3);
EspectralSQ.samplingRate = 6000;
N = size(X);
% Coloco + 3H pq ele ja tá em BR;
t0_squadriga = datetime('2025-02-10T 10:06:36.000Z','InputFormat','uuuu-MM-dd''T''HH:mm:ss.000Z',TimeZone="-03:00");
Time_SQuadriga = datetime(t0_squadriga + 1/EspectralSQ.samplingRate*seconds(0:N-1),'Format','dd/MM/yyyy HH:mm:ss.SSSS');
WaveFormAccRMS_SQ_Z = rms(Z);
%% 4. Time history plot with velocity and vibration Z      
        figure('Renderer', 'painters', 'Position', [300 200 1200 500]);
        t = tiledlayout(2,1,"TileSpacing","compact",Padding="tight");
        % plot Velocidade vs vibração
        ax1 = nexttile(1);
        plot(GPS.Time,GPS.Velocidade,'DisplayName','Velocity','Color','k');
        ylabel('Velocidade [km/h]','FontSize',10)
        % Limites dos eixos X de ambos plots(velocidade e acc)-----%
        t0 = WaveFormTimeConc(1)-seconds(36);
        tf = GPS.Time(end)+seconds(31);
        xlim([t0 tf]);
        xticks(t0 : minutes(1):tf); 
        xtickformat('HH:mm')
      %----------------------------------------------------------%
        ax1.XAxis.FontSize = 10;
        grid on
        title('Velocity and Seat Track Left Accelerations ')
        ax2 =nexttile(2);
        plot(Time_SQuadriga,Z,"-",'DisplayName','Z-dir SQuadriga','Color',[0 0 1])
        % hold on
        % plot(Time_SQuadriga,Y,"-",'DisplayName','Y-dir SQuadriga','Color',[0 1 0])
        % hold on
        % plot(Time_SQuadriga,X,"-",'DisplayName','X-dir SQuadriga','Color',[1 0 0])
        hold on
        plot(WaveFormTimeConc,WaveForAccConc.Z,"-",'DisplayName','Z-dir Dynaloggers','Color',[0 0.4470 0.7410])
        % hold on
        % plot(WaveFormTimeConc,WaveForAccConc.Y,"-",'DisplayName','Y-dir Dynaloggers','Color',[0.4660 0.6740 0.1880])
        % hold on 
        % plot(WaveFormTimeConc,WaveForAccConc.X,"-",'DisplayName','X-dir Dynaloggers','Color',[0.6350 0.0780 0.1840])
        y1 = yline(WaveFormAccRMS_Z,'--','RMS Dynalogger = '+string(WaveFormAccRMS_Z),'LineWidth',2,'Color',[1,1,0]);
        y2 = yline(WaveFormAccRMS_SQ_Z,'--','RMS SQuadriga= '+string(WaveFormAccRMS_SQ_Z),'LineWidth',2,'Color',[1,0,0]);
        ylabel('Acceleration [m/s^2]','FontSize',10) 
        % Toma apenas um eixo X como referencia para ambos os plots
        linkaxes(t.Children,'x')
        %-----------------------------------------------------------
        xlabel('Hour','FontSize',10)
        xtickformat('HH:mm')
        grid on
        xlim([t0 tf]);
        xticks(t0 : minutes(1) :tf);         
        legend('SQuadriga','Dynaloggers',"Location","north")
        ylim([-6 6])
       yl.LabelVerticalAlignment = 'top';
y2.LabelVerticalAlignment = 'bottom';

%% 5. Cria vetores de vibração do SQuadriga nos mesmos intantes dos Dynas
% Acha o index inicial e final do vetor do SQuadriga referente ao inicio e
% fim de uma medição do Dyna
index_2_i = find(Time_SQuadriga == '10/02/2025 07:07:21.0000'); index_2_f = find(Time_SQuadriga == '10/02/2025 07:07:43.6190');
WaveFormTimeSQ{1,2}  = Time_SQuadriga(index_2_i:index_2_f);
WaveFormAccSQ.X{1,2} = X(index_2_i:index_2_f);
WaveFormAccSQ.Y{1,2} = Y(index_2_i:index_2_f);
WaveFormAccSQ.Z{1,2} = Z(index_2_i:index_2_f);
TimeDummy= Time_SQuadriga(index_2_f) -Time_SQuadriga(index_2_i);
EspectralSQ.duration(2) = seconds(TimeDummy);
EspectralSQ.samples(2) = length(WaveFormAccSQ.X{1,2});

index_3_i = find(Time_SQuadriga == '10/02/2025 07:08:44.0000'); index_3_f = find(Time_SQuadriga == '10/02/2025 07:09:06.6190');
WaveFormTimeSQ{1,3}  = Time_SQuadriga(index_3_i:index_3_f);
WaveFormAccSQ.X{1,3} = X(index_3_i:index_3_f);
WaveFormAccSQ.Y{1,3} = Y(index_3_i:index_3_f);
WaveFormAccSQ.Z{1,3} = Z(index_3_i:index_3_f);
TimeDummy= Time_SQuadriga(index_3_f) -Time_SQuadriga(index_3_i);
EspectralSQ.duration(3) = seconds(TimeDummy);
EspectralSQ.samples(3) = length(WaveFormAccSQ.X{1,3});

index_4_i = find(Time_SQuadriga == '10/02/2025 07:10:23.0000'); index_4_f = find(Time_SQuadriga == '10/02/2025 07:10:45.6190');
WaveFormTimeSQ{1,4}  = Time_SQuadriga(index_4_i:index_4_f);
WaveFormAccSQ.X{1,4} = X(index_4_i:index_4_f);
WaveFormAccSQ.Y{1,4} = Y(index_4_i:index_4_f);
WaveFormAccSQ.Z{1,4} = Z(index_4_i:index_4_f);
TimeDummy= Time_SQuadriga(index_4_f) -Time_SQuadriga(index_4_i);
EspectralSQ.duration(4) = seconds(TimeDummy);
EspectralSQ.samples(4) = length(WaveFormAccSQ.X{1,4});

index_5_i = find(Time_SQuadriga == '10/02/2025 07:11:56.0000'); index_5_f = find(Time_SQuadriga == '10/02/2025 07:12:01.1200');
WaveFormTimeSQ{1,5}  = Time_SQuadriga(index_5_i:index_5_f);
WaveFormAccSQ.X{1,5} = X(index_5_i:index_5_f);
WaveFormAccSQ.Y{1,5} = Y(index_5_i:index_5_f);
WaveFormAccSQ.Z{1,5} = Z(index_5_i:index_5_f);
TimeDummy= Time_SQuadriga(index_5_f) -Time_SQuadriga(index_5_i);
EspectralSQ.duration(5) = seconds(TimeDummy);
EspectralSQ.samples(5) = length(WaveFormAccSQ.X{1,5});

index_6_i = find(Time_SQuadriga == '10/02/2025 07:13:48.0000'); index_6_f = find(Time_SQuadriga == ' 10/02/2025 07:14:10.6190');
WaveFormTimeSQ{1,6}  = Time_SQuadriga(index_6_i:index_6_f);
WaveFormAccSQ.X{1,6} = X(index_6_i:index_6_f);
WaveFormAccSQ.Y{1,6} = Y(index_6_i:index_6_f);
WaveFormAccSQ.Z{1,6} = Z(index_6_i:index_6_f);
TimeDummy= Time_SQuadriga(index_6_f) -Time_SQuadriga(index_6_i);
EspectralSQ.duration(6) = seconds(TimeDummy);
EspectralSQ.samples(6) = length(WaveFormAccSQ.X{1,6});

index_7_i = find(Time_SQuadriga == '10/02/2025 07:15:14.0000'); index_7_f = find(Time_SQuadriga == '10/02/2025 07:15:36.6190');
WaveFormTimeSQ{1,7}  = Time_SQuadriga(index_7_i:index_7_f);
WaveFormAccSQ.X{1,7} = X(index_7_i:index_7_f);
WaveFormAccSQ.Y{1,7} = Y(index_7_i:index_7_f);
WaveFormAccSQ.Z{1,7} = Z(index_7_i:index_7_f);
TimeDummy= Time_SQuadriga(index_7_f) -Time_SQuadriga(index_7_i);
EspectralSQ.duration(7) = seconds(TimeDummy);
EspectralSQ.samples(7) = length(WaveFormAccSQ.X{1,7});

index_8_i = find(Time_SQuadriga == '10/02/2025 07:16:38.0000'); index_8_f = find(Time_SQuadriga == '10/02/2025 07:17:00.6190');
WaveFormTimeSQ{1,8}  = Time_SQuadriga(index_8_i:index_8_f);
WaveFormAccSQ.X{1,8} = X(index_8_i:index_8_f);
WaveFormAccSQ.Y{1,8} = Y(index_8_i:index_8_f);
WaveFormAccSQ.Z{1,8} = Z(index_8_i:index_8_f);
TimeDummy= Time_SQuadriga(index_8_f) -Time_SQuadriga(index_8_i);
EspectralSQ.duration(8) = seconds(TimeDummy);
EspectralSQ.samples(8) = length(WaveFormAccSQ.X{1,8});

index_9_i = find(Time_SQuadriga == '10/02/2025 07:18:14.0000'); index_9_f = find(Time_SQuadriga == '10/02/2025 07:18:19.1200');
WaveFormTimeSQ{1,9}  = Time_SQuadriga(index_9_i:index_9_f);
WaveFormAccSQ.X{1,9} = X(index_9_i:index_9_f);
WaveFormAccSQ.Y{1,9} = Y(index_9_i:index_9_f);
WaveFormAccSQ.Z{1,9} = Z(index_9_i:index_9_f);
TimeDummy= Time_SQuadriga(index_9_f) -Time_SQuadriga(index_9_i);
EspectralSQ.duration(9) = seconds(TimeDummy);
EspectralSQ.samples(9) = length(WaveFormAccSQ.X{1,9});

index_10_i = find(Time_SQuadriga == '10/02/2025 07:20:03.0000'); index_10_f = find(Time_SQuadriga == '10/02/2025 07:20:25.6190');
WaveFormTimeSQ{1,10}  = Time_SQuadriga(index_10_i:index_10_f);
WaveFormAccSQ.X{1,10} = X(index_10_i:index_10_f);
WaveFormAccSQ.Y{1,10} = Y(index_10_i:index_10_f);
WaveFormAccSQ.Z{1,10} = Z(index_10_i:index_10_f);
TimeDummy= Time_SQuadriga(index_10_f) -Time_SQuadriga(index_10_i);
EspectralSQ.duration(10) = seconds(TimeDummy);
EspectralSQ.samples(10) = length(WaveFormAccSQ.X{1,10});

index_11_i = find(Time_SQuadriga == '10/02/2025 07:21:29.0000'); index_11_f = find(Time_SQuadriga == '10/02/2025 07:21:51.6190');
WaveFormTimeSQ{1,11}  = Time_SQuadriga(index_11_i:index_11_f);
WaveFormAccSQ.X{1,11} = X(index_11_i:index_11_f);
WaveFormAccSQ.Y{1,11} = Y(index_11_i:index_11_f);
WaveFormAccSQ.Z{1,11} = Z(index_11_i:index_11_f);
TimeDummy= Time_SQuadriga(index_11_f) -Time_SQuadriga(index_11_i);
EspectralSQ.duration(11) = seconds(TimeDummy);
EspectralSQ.samples(11) = length(WaveFormAccSQ.X{1,11});

index_12_i = find(Time_SQuadriga == '10/02/2025 07:22:55.0000'); index_12_f = find(Time_SQuadriga == '10/02/2025 07:23:17.6190');
WaveFormTimeSQ{1,12}  = Time_SQuadriga(index_12_i:index_12_f);
WaveFormAccSQ.X{1,12} = X(index_12_i:index_12_f);
WaveFormAccSQ.Y{1,12} = Y(index_12_i:index_12_f);
WaveFormAccSQ.Z{1,12} = Z(index_12_i:index_12_f);
TimeDummy= Time_SQuadriga(index_12_f) -Time_SQuadriga(index_12_i);
EspectralSQ.duration(12) = seconds(TimeDummy);
EspectralSQ.samples(12) = length(WaveFormAccSQ.X{1,12});

index_13_i = find(Time_SQuadriga == '10/02/2025 07:24:29.0000'); index_13_f = find(Time_SQuadriga == ' 10/02/2025 07:24:34.1200');
WaveFormTimeSQ{1,13}  = Time_SQuadriga(index_13_i:index_13_f);
WaveFormAccSQ.X{1,13} = X(index_13_i:index_13_f);
WaveFormAccSQ.Y{1,13} = Y(index_13_i:index_13_f);
WaveFormAccSQ.Z{1,13} = Z(index_13_i:index_13_f);
TimeDummy= Time_SQuadriga(index_13_f) -Time_SQuadriga(index_13_i);
EspectralSQ.duration(13) = seconds(TimeDummy);
EspectralSQ.samples(13) = length(WaveFormAccSQ.X{1,13});

index_14_i = find(Time_SQuadriga == '10/02/2025 07:26:41.0000'); index_14_f = find(Time_SQuadriga == '10/02/2025 07:27:03.6190');
WaveFormTimeSQ{1,14}  = Time_SQuadriga(index_14_i:index_14_f);
WaveFormAccSQ.X{1,14} = X(index_14_i:index_14_f);
WaveFormAccSQ.Y{1,14} = Y(index_14_i:index_14_f);
WaveFormAccSQ.Z{1,14} = Z(index_14_i:index_14_f);
TimeDummy= Time_SQuadriga(index_14_f) -Time_SQuadriga(index_14_i);
EspectralSQ.duration(14) = seconds(TimeDummy);
EspectralSQ.samples(14) = length(WaveFormAccSQ.X{1,14});

index_15_i = find(Time_SQuadriga == '10/02/2025 07:28:08.0000'); index_15_f = find(Time_SQuadriga == '10/02/2025 07:28:30.6190');
WaveFormTimeSQ{1,15}  = Time_SQuadriga(index_15_i:index_15_f);
WaveFormAccSQ.X{1,15} = X(index_15_i:index_15_f);
WaveFormAccSQ.Y{1,15} = Y(index_15_i:index_15_f);
WaveFormAccSQ.Z{1,15} = Z(index_15_i:index_15_f);
TimeDummy= Time_SQuadriga(index_15_f) -Time_SQuadriga(index_15_i);
EspectralSQ.duration(15) = seconds(TimeDummy);
EspectralSQ.samples(15) = length(WaveFormAccSQ.X{1,15});

index_16_i = find(Time_SQuadriga == '10/02/2025 07:29:35.0000'); index_16_f = find(Time_SQuadriga == '10/02/2025 07:29:57.6190');
WaveFormTimeSQ{1,16}  = Time_SQuadriga(index_16_i:index_16_f);
WaveFormAccSQ.X{1,16} = X(index_16_i:index_16_f);
WaveFormAccSQ.Y{1,16} = Y(index_16_i:index_16_f);
WaveFormAccSQ.Z{1,16} = Z(index_16_i:index_16_f);
TimeDummy= Time_SQuadriga(index_16_f) -Time_SQuadriga(index_16_i);
EspectralSQ.duration(16) = seconds(TimeDummy);
EspectralSQ.samples(16) = length(WaveFormAccSQ.X{1,16});

index_17_i = find(Time_SQuadriga == '10/02/2025 07:31:13.0000'); index_17_f = find(Time_SQuadriga == '10/02/2025 07:31:18.1200');
WaveFormTimeSQ{1,17}  = Time_SQuadriga(index_17_i:index_17_f);
WaveFormAccSQ.X{1,17} = X(index_17_i:index_17_f);
WaveFormAccSQ.Y{1,17} = Y(index_17_i:index_17_f);
WaveFormAccSQ.Z{1,17} = Z(index_17_i:index_17_f);
TimeDummy= Time_SQuadriga(index_17_f) -Time_SQuadriga(index_17_i);
EspectralSQ.duration(17) = seconds(TimeDummy);
EspectralSQ.samples(17) = length(WaveFormAccSQ.X{1,17});

index_18_i = find(Time_SQuadriga == '10/02/2025 07:32:58.0000'); index_18_f = find(Time_SQuadriga == '10/02/2025 07:33:20.6190');
WaveFormTimeSQ{1,18}  = Time_SQuadriga(index_18_i:index_18_f);
WaveFormAccSQ.X{1,18} = X(index_18_i:index_18_f);
WaveFormAccSQ.Y{1,18} = Y(index_18_i:index_18_f);
WaveFormAccSQ.Z{1,18} = Z(index_18_i:index_18_f);
TimeDummy= Time_SQuadriga(index_18_f) -Time_SQuadriga(index_18_i);
EspectralSQ.duration(18) = seconds(TimeDummy);
EspectralSQ.samples(18) = length(WaveFormAccSQ.X{1,18});

index_19_i = find(Time_SQuadriga == '10/02/2025 07:34:25.0000'); index_19_f = find(Time_SQuadriga == '10/02/2025 07:34:47.6190');
WaveFormTimeSQ{1,19}  = Time_SQuadriga(index_19_i:index_19_f);
WaveFormAccSQ.X{1,19} = X(index_19_i:index_19_f);
WaveFormAccSQ.Y{1,19} = Y(index_19_i:index_19_f);
WaveFormAccSQ.Z{1,19} = Z(index_19_i:index_19_f);
TimeDummy= Time_SQuadriga(index_19_f) -Time_SQuadriga(index_19_i);
EspectralSQ.duration(19) = seconds(TimeDummy);
EspectralSQ.samples(19) = length(WaveFormAccSQ.X{1,19});

index_20_i = find(Time_SQuadriga == '10/02/2025 07:35:52.0000'); index_20_f = find(Time_SQuadriga == '10/02/2025 07:36:14.6190');
WaveFormTimeSQ{1,20}  = Time_SQuadriga(index_20_i:index_20_f);
WaveFormAccSQ.X{1,20} = X(index_20_i:index_20_f);
WaveFormAccSQ.Y{1,20} = Y(index_20_i:index_20_f);
WaveFormAccSQ.Z{1,20} = Z(index_20_i:index_20_f);
TimeDummy= Time_SQuadriga(index_20_f) -Time_SQuadriga(index_20_i);
EspectralSQ.duration(20) = seconds(TimeDummy);
EspectralSQ.samples(20) = length(WaveFormAccSQ.X{1,20});

index_21_i = find(Time_SQuadriga == '10/02/2025 07:37:25.0000'); index_21_f = find(Time_SQuadriga == '10/02/2025 07:37:30.120');
WaveFormTimeSQ{1,21}  = Time_SQuadriga(index_21_i:index_21_f);
WaveFormAccSQ.X{1,21} = X(index_21_i:index_21_f);
WaveFormAccSQ.Y{1,21} = Y(index_21_i:index_21_f);
WaveFormAccSQ.Z{1,21} = Z(index_21_i:index_21_f);
TimeDummy= Time_SQuadriga(index_21_f) -Time_SQuadriga(index_21_i);
EspectralSQ.duration(21) = seconds(TimeDummy);
EspectralSQ.samples(21) = length(WaveFormAccSQ.X{1,21});

index_22_i = find(Time_SQuadriga == '10/02/2025 07:39:13.0000'); index_22_f = find(Time_SQuadriga == '10/02/2025 07:39:35.6190');
WaveFormTimeSQ{1,22}  = Time_SQuadriga(index_22_i:index_22_f);
WaveFormAccSQ.X{1,22} = X(index_22_i:index_22_f);
WaveFormAccSQ.Y{1,22} = Y(index_22_i:index_22_f);
WaveFormAccSQ.Z{1,22} = Z(index_22_i:index_22_f);
TimeDummy= Time_SQuadriga(index_22_f) -Time_SQuadriga(index_22_i);
EspectralSQ.duration(22) = seconds(TimeDummy);
EspectralSQ.samples(22) = length(WaveFormAccSQ.X{1,22});

index_23_i = find(Time_SQuadriga == '10/02/2025 07:40:37.0000'); index_23_f = find(Time_SQuadriga == '10/02/2025 07:40:59.6190');
WaveFormTimeSQ{1,23}  = Time_SQuadriga(index_23_i:index_23_f);
WaveFormAccSQ.X{1,23} = X(index_23_i:index_23_f);
WaveFormAccSQ.Y{1,23} = Y(index_23_i:index_23_f);
WaveFormAccSQ.Z{1,23} = Z(index_23_i:index_23_f);
TimeDummy= Time_SQuadriga(index_23_f) -Time_SQuadriga(index_23_i);
EspectralSQ.duration(23) = seconds(TimeDummy);
EspectralSQ.samples(23) = length(WaveFormAccSQ.X{1,23});

index_24_i = find(Time_SQuadriga == '10/02/2025 07:42:03.0000'); index_24_f = find(Time_SQuadriga == '10/02/2025 07:42:25.6190');
WaveFormTimeSQ{1,24}  = Time_SQuadriga(index_24_i:index_24_f);
WaveFormAccSQ.X{1,24} = X(index_24_i:index_24_f);
WaveFormAccSQ.Y{1,24} = Y(index_24_i:index_24_f);
WaveFormAccSQ.Z{1,24} = Z(index_24_i:index_24_f);
TimeDummy= Time_SQuadriga(index_24_f) -Time_SQuadriga(index_24_i);
EspectralSQ.duration(24) = seconds(TimeDummy);
EspectralSQ.samples(24) = length(WaveFormAccSQ.X{1,24});

index_25_i = find(Time_SQuadriga == '10/02/2025 07:43:40.0000'); index_25_f = find(Time_SQuadriga == '10/02/2025 07:43:45.1200');
WaveFormTimeSQ{1,25}  = Time_SQuadriga(index_25_i:index_25_f);
WaveFormAccSQ.X{1,25} = X(index_25_i:index_25_f);
WaveFormAccSQ.Y{1,25} = Y(index_25_i:index_25_f);
WaveFormAccSQ.Z{1,25} = Z(index_25_i:index_25_f);
TimeDummy= Time_SQuadriga(index_25_f) -Time_SQuadriga(index_25_i);
EspectralSQ.duration(25) = seconds(TimeDummy);
EspectralSQ.samples(25) = length(WaveFormAccSQ.X{1,25});

index_26_i = find(Time_SQuadriga == '10/02/2025 07:45:24.0000'); index_26_f = find(Time_SQuadriga == '10/02/2025 07:45:46.6190');
WaveFormTimeSQ{1,26}  = Time_SQuadriga(index_26_i:index_26_f);
WaveFormAccSQ.X{1,26} = X(index_26_i:index_26_f);
WaveFormAccSQ.Y{1,26} = Y(index_26_i:index_26_f);
WaveFormAccSQ.Z{1,26} = Z(index_26_i:index_26_f);
TimeDummy= Time_SQuadriga(index_26_f) -Time_SQuadriga(index_26_i);
EspectralSQ.duration(26) = seconds(TimeDummy);
EspectralSQ.samples(26) = length(WaveFormAccSQ.X{1,26});

index_27_i = find(Time_SQuadriga == '10/02/2025 07:46:48.0000'); index_27_f = find(Time_SQuadriga == '10/02/2025 07:47:10.6190');
WaveFormTimeSQ{1,27}  = Time_SQuadriga(index_27_i:index_27_f);
WaveFormAccSQ.X{1,27} = X(index_27_i:index_27_f);
WaveFormAccSQ.Y{1,27} = Y(index_27_i:index_27_f);
WaveFormAccSQ.Z{1,27} = Z(index_27_i:index_27_f);
TimeDummy= Time_SQuadriga(index_27_f) -Time_SQuadriga(index_27_i);
EspectralSQ.duration(27) = seconds(TimeDummy);
EspectralSQ.samples(27) = length(WaveFormAccSQ.X{1,27});

index_28_i = find(Time_SQuadriga == '10/02/2025 07:48:14.0000'); index_28_f = find(Time_SQuadriga == '10/02/2025 07:48:36.6190');
WaveFormTimeSQ{1,28}  = Time_SQuadriga(index_28_i:index_28_f);
WaveFormAccSQ.X{1,28} = X(index_28_i:index_28_f);
WaveFormAccSQ.Y{1,28} = Y(index_28_i:index_28_f);
WaveFormAccSQ.Z{1,28} = Z(index_28_i:index_28_f);
TimeDummy= Time_SQuadriga(index_28_f) -Time_SQuadriga(index_28_i);
EspectralSQ.duration(28) = seconds(TimeDummy);
EspectralSQ.samples(28) = length(WaveFormAccSQ.X{1,28});

index_29_i = find(Time_SQuadriga == '10/02/2025 07:49:47.0000'); index_29_f = find(Time_SQuadriga == '10/02/2025 07:49:52.1200');
WaveFormTimeSQ{1,29}  = Time_SQuadriga(index_29_i:index_29_f);
WaveFormAccSQ.X{1,29} = X(index_29_i:index_29_f);
WaveFormAccSQ.Y{1,29} = Y(index_29_i:index_29_f);
WaveFormAccSQ.Z{1,29} = Z(index_29_i:index_29_f);
TimeDummy= Time_SQuadriga(index_29_f) -Time_SQuadriga(index_29_i);
EspectralSQ.duration(29) = seconds(TimeDummy);
EspectralSQ.samples(29) = length(WaveFormAccSQ.X{1,29});

index_30_i = find(Time_SQuadriga == '10/02/2025 07:51:36.0000'); index_30_f = find(Time_SQuadriga == '10/02/2025 07:51:58.6190');
WaveFormTimeSQ{1,30}  = Time_SQuadriga(index_30_i:index_30_f);
WaveFormAccSQ.X{1,30} = X(index_30_i:index_30_f);
WaveFormAccSQ.Y{1,30} = Y(index_30_i:index_30_f);
WaveFormAccSQ.Z{1,30} = Z(index_30_i:index_30_f);
TimeDummy= Time_SQuadriga(index_30_f) -Time_SQuadriga(index_30_i);
EspectralSQ.duration(30) = seconds(TimeDummy);
EspectralSQ.samples(30) = length(WaveFormAccSQ.X{1,30});

index_31_i = find(Time_SQuadriga == '10/02/2025 07:53:03.0000'); index_31_f = find(Time_SQuadriga == '10/02/2025 07:53:25.6190');
WaveFormTimeSQ{1,31}  = Time_SQuadriga(index_31_i:index_31_f);
WaveFormAccSQ.X{1,31} = X(index_31_i:index_31_f);
WaveFormAccSQ.Y{1,31} = Y(index_31_i:index_31_f);
WaveFormAccSQ.Z{1,31} = Z(index_31_i:index_31_f);
TimeDummy= Time_SQuadriga(index_31_f) -Time_SQuadriga(index_31_i);
EspectralSQ.duration(31) = seconds(TimeDummy);
EspectralSQ.samples(31) = length(WaveFormAccSQ.X{1,31});

index_32_i = find(Time_SQuadriga == '10/02/2025 07:54:28.0000'); index_32_f = find(Time_SQuadriga == '10/02/2025 07:54:50.6190');
WaveFormTimeSQ{1,32}  = Time_SQuadriga(index_32_i:index_32_f);
WaveFormAccSQ.X{1,32} = X(index_32_i:index_32_f);
WaveFormAccSQ.Y{1,32} = Y(index_32_i:index_32_f);
WaveFormAccSQ.Z{1,32} = Z(index_32_i:index_32_f);
TimeDummy= Time_SQuadriga(index_32_f) -Time_SQuadriga(index_32_i);
EspectralSQ.duration(32) = seconds(TimeDummy);
EspectralSQ.samples(32) = length(WaveFormAccSQ.X{1,32});

index_33_i = find(Time_SQuadriga == '10/02/2025 07:56:00.0000'); index_33_f = find(Time_SQuadriga == '10/02/2025 07:56:05.1200');
WaveFormTimeSQ{1,33}  = Time_SQuadriga(index_33_i:index_33_f);
WaveFormAccSQ.X{1,33} = X(index_33_i:index_33_f);
WaveFormAccSQ.Y{1,33} = Y(index_33_i:index_33_f);
WaveFormAccSQ.Z{1,33} = Z(index_33_i:index_33_f);
TimeDummy= Time_SQuadriga(index_33_f) -Time_SQuadriga(index_33_i);
EspectralSQ.duration(33) = seconds(TimeDummy);
EspectralSQ.samples(33) = length(WaveFormAccSQ.X{1,33});
clear index_2_i index_2_f TimeDummy
% %% 6. Plota a comparacao Dyna vs SQuadriga no Tempo
%for k = 2:EspecSample
%figure(k)
%plot(WaveFormTimeSQ{1,k}, WaveFormAccSQ.Z{1,k},"-",'DisplayName','Z-dir SQuadriga','Color',[0 0 1])
%hold on 
%plot(WaveFormTime{1,k},WaveFormAcc.Z{1,k},"-",'DisplayName','Z-dir Dynaloggers','Color',[0 0.4470 0.7410])
%legend()
%grid on
%ylim([-5 5])
%ylabel('Acceleration [m/s^2]','FontSize',10) 
%title(['Seat Track Left | Z-direction. Amostra', ' ',num2str(k)])
%end

%% 7. Cria os vetores de espectros
for k = 2:EspecSample
       [Espectral.Spectrum.X{k},Espectral.Mag.X{k},Espectral.Pha.X{k},Espectral.freq{k}] = fftTimetoFreq2(WaveFormAcc.X{k},Espectral.duration(k),Espectral.samples(k));
       [Espectral.Spectrum.Y{k},Espectral.Mag.Y{k},Espectral.Pha.Y{k},Espectral.freq{k}] = fftTimetoFreq2(WaveFormAcc.Y{k},Espectral.duration(k),Espectral.samples(k));
       [Espectral.Spectrum.Z{k},Espectral.Mag.Z{k},Espectral.Pha.Z{k},Espectral.freq{k}] = fftTimetoFreq2(WaveFormAcc.Z{k},Espectral.duration(k),Espectral.samples(k));

       [EspectralSQ.Spectrum.X{k},EspectralSQ.Mag.X{k},EspectralSQ.Pha.X{k},EspectralSQ.freq{k}] = fftTimetoFreq2(WaveFormAccSQ.X{k},EspectralSQ.duration(k),EspectralSQ.samples(k));
       [EspectralSQ.Spectrum.Y{k},EspectralSQ.Mag.Y{k},EspectralSQ.Pha.Y{k},EspectralSQ.freq{k}] = fftTimetoFreq2(WaveFormAccSQ.Y{k},EspectralSQ.duration(k),EspectralSQ.samples(k));
       [EspectralSQ.Spectrum.Z{k},EspectralSQ.Mag.Z{k},EspectralSQ.Pha.Z{k},EspectralSQ.freq{k}] = fftTimetoFreq2(WaveFormAccSQ.Z{k},EspectralSQ.duration(k),EspectralSQ.samples(k));
 %% 8. Cria os vetores de PSD 
       nsc = floor(Espectral.samples(k)/40);
       nov = floor(nsc/2); % 50% de overlap
       nfft = max(256,2^nextpow2(nsc));
       [Espectral.PSD.X{k},Espectral.freq2{k}] = pwelch(WaveFormAcc.X{k}, hamming(nsc),nov, nfft, Espectral.samplingRate(k));
       [Espectral.PSD.Y{k},Espectral.freq2{k}] = pwelch(WaveFormAcc.Y{k}, hamming(nsc),nov, nfft, Espectral.samplingRate(k));
       [Espectral.PSD.Z{k},Espectral.freq2{k}] = pwelch(WaveFormAcc.Z{k}, hamming(nsc),nov, nfft, Espectral.samplingRate(k));

       [EspectralSQ.PSD.X{k},EspectralSQ.freq2{k}] = pwelch(WaveFormAccSQ.X{k}, hamming(nsc),nov,nfft, EspectralSQ.samplingRate);
       [EspectralSQ.PSD.Y{k},EspectralSQ.freq2{k}] = pwelch(WaveFormAccSQ.Y{k}, hamming(nsc),nov,nfft, EspectralSQ.samplingRate);
       [EspectralSQ.PSD.Z{k},EspectralSQ.freq2{k}] = pwelch(WaveFormAccSQ.Z{k}, hamming(nsc),nov,nfft, EspectralSQ.samplingRate);
       %% 9. Nivel de vibracao
       a_0 = 1e-5;
       Espectral.L_a.Z{k} = 20*log10(Espectral.Mag.Z{k}/a_0);
       EspectralSQ.L_a.Z{k} = 20*log10(EspectralSQ.Mag.Z{k}/a_0);

end
%% 8. Plota a comparacao Dyna vs SQuadriga na Frequencia 
Spectrum_ymax_seat=1;
Spectrum_ymin=1e-6;
Spectrum_xmax=3000; 
close all
for k = 2:EspecSample
            figure(23+k)
            subplot(2,1,1)
            semilogx(EspectralSQ.freq{k},EspectralSQ.L_a.Z{k},'DisplayName','Dynalogger','Color',[0 0 1])
            hold on
            semilogx(Espectral.freq{k},Espectral.L_a.Z{k},'DisplayName','Dynalogger','Color',[0 0.4470 0.7410])
            yline(46,'--','Vibration Level = 46 dB (2e-4 g)','LineWidth',1,'color', [0 0 0],'LabelHorizontalAlignment','left')
            xline(0.7,'--','0.7 Hz','LineWidth',1)
            xline(3,'--','3 Hz','LineWidth',1)
            xlabel('Freq [Hz]','FontSize',10)
            ylabel('Acceleration [dB]','FontSize',10)
            grid on
            xlim([0.1 3000])
            ylim([-30 100])
            title(['Vibration Level - Amostra', ' ',num2str(k)])
            legend('SQuadriga','Dynalogger')
            set(gcf,'position',[400,200,650,700])
            
            subplot(2,1,2)
            loglog(EspectralSQ.freq2{k},EspectralSQ.PSD.Z{k},'DisplayName','SQuadriga','Color',[0 0 1])
            % loglog(Espectral.freq2{k},Espectral.PSD.Z{k},'DisplayName','Dynalogger','Color',[0 0.4470 0.7410])
            hold on
            loglog(Espectral.freq2{k},Espectral.PSD.Z{k},'DisplayName','Dynalogger','Color',[0 0.4470 0.7410])
            xline(0.7,'--','0.7 Hz','LineWidth',1)
            xline(3,'--','3 Hz','LineWidth',1)
            yline((220e-6*10)^2,'--','Densidade de ruido (TcAs) = (220ug)^2','LineWidth',1,'color', [0 0 0])
            yline((75e-6*10)^2,'--','Desidade de ruido (HF+) = (75ug)^2','LineWidth',1,'color', [0 0 0])
            xlabel('Freq [Hz]','FontSize',10)
            ylabel('Acceleration [(m/s^2)^2/Hz]','FontSize',10)
            grid on
            xlim([0.1 3000])
            % ylim([Spectrum_ymin Spectrum_ymax_seat])
            title(['Power Spectral Density - Amostra', ' ',num2str(k)])
            legend('SQuadriga','Dynalogger')
            set(gcf,'position',[400,200,600,700])

            
end 
% clear  k EspecSample


%% Export Waveforms 
% Instantes = 0:Espectral.dt(1):numfiles*Espectral.duration(1)+(numfiles-1)*Espectral.dt(1);
 % save('C:\Users\tavin\Desktop\Mestrado\2_teste_automovel\Arduino_codes\heli-lva\test_fft_discretization\time_history\TEST',"Espectral.time{1,1}","WaveFormAcc.Z{1, 1} ","-v7.3")