

//Framework
#include <Arduino.h>

// Bibliotecas
#include <SoftwareSerial.h>             // Para o GPS
#include <TinyGPS.h>                    // Para o GPS
//#include <LiquidCrystal_I2C.h>          // Para o LCD
#include <SD.h>                         // Para o Cartão SD
#include <SPI.h>                        // Para o cartão SD
#include <Wire.h>

// Pinagem
#define PIN_TRIGGER 7    // Pino para trigger para o gateway
#define PIN_RX 2          // RX GPS
#define PIN_TX 3          // TX GPS
#define CS_PIN 10          // Pino cartão SD

// Variáveis globais para cartão SD
char GPS_file_name[32];
File dataFile;

// Init dos objetos
TinyGPS gps;
SoftwareSerial ss(2, 3); // RX, TX

// Variaveis globais para lógica GPS
bool newData = false; // Variável de controle para escrever apenas quando há informações válidas
int routePosition = 1;// Variável de controle e.g "Position 1,2,3,..."

// Variáveis globais para pulso Trigger
bool pulsing = false;                     // Variável de controle para lógica do pulso
unsigned long previousMillisTrigger = 0;  // Último momento que o pulso ocorreu
const long intervalTrigger = 300000;      // Intervalo de 5 min 
unsigned long pulseStartTime = 0;         // Tempo quando pulso começou
const long intervalPulse = 10000;           // Duração do pulso 10s

// -------------- Declaração de funções----------------
void initSD() {
  Serial.println("Inicializando cartão de SD...");
  pinMode(CS_PIN, OUTPUT);

  if (SD.begin()) {
    Serial.println("Cartão de SD pronto para uso");
  } else {
    Serial.println("Inicializão de SD falhou");
  }
}

 int getIndex(File nameFile) {
   int indexNumber;

   if (nameFile) {
     indexNumber = nameFile.parseInt();
     nameFile.close();
   }

     if (indexNumber == 0) {
       indexNumber = 0;
      }
   Serial.println("index found = "  + String(indexNumber));
 return indexNumber;
 }

int updateIndex(int indexNumber) {
  File indexFile;
  SD.remove("INDEX.txt");
  indexFile = SD.open("INDEX.txt", FILE_WRITE);
    if (indexFile) {
      indexNumber +=1;
       indexFile.print(indexNumber);
       indexFile.close();
       Serial.println("current index = ");
       Serial.println (indexNumber);
  } else {
    Serial.println("Não foi possivel abrir arquino INDEX");}
  return indexNumber;
}

void pulso(){
  // Verifica se 5 min passaram para o trigger
  unsigned long currentMillisTrigger = millis();

  if (currentMillisTrigger-previousMillisTrigger >= intervalTrigger){
    previousMillisTrigger = currentMillisTrigger;

    if (!pulsing){
      digitalWrite(PIN_TRIGGER,HIGH);
      pulsing = true;
      pulseStartTime = currentMillisTrigger;
    }
  }
  if(pulsing &&(currentMillisTrigger - pulseStartTime >=intervalPulse)){
    digitalWrite(PIN_TRIGGER,LOW);
    pulsing =false;
  }
  //Serial.print(currentMillisTrigger/1000);
}
//--------------Fim declaracao funçoes----------------------
// -------------Setup Section-------------------------------
void setup() {
  // Setup dos seriais com 9600 baunds
  Serial.begin(9600);
  // Software serial para RX e TX
  ss.begin(9600);
  
  // Verifica se Cartão de SD tá funcionando
  initSD();
  
  // Mostra o ultimo index para definir proximo data file
  File indexFile = SD.open("INDEX.txt", FILE_READ);
  int index_old = getIndex(indexFile);
  indexFile.close();  
  
  // Atualiza index
  int index_new = updateIndex(index_old);
  Serial.println("Terminou de atualizar o índice");
  
  // Monta o nome do arquivo a ser criado
  sprintf(GPS_file_name, "file_%d.csv", index_new);
  Serial.println(GPS_file_name);

Serial.println("Final da função setup");
} // Termina Setup Section ---------------------------

// -------------Loop Section-------------------------------
void loop() {
Serial.println("Rodando função loop");
// -- Processamento do GPS + Escrita dos dados no SD --

// For one second we parse GPS data and report some key values
for (unsigned long start = millis(); millis() - start < 1000;)
{
  while (ss.available()) {
    char c = ss.read();
    // Serial.write(c); // Para os dados raw
    if (gps.encode(c)) // Checando se formou uma sentença válida do GPS
      newData = true;
  }
}

Serial.println(newData ? "New GPS data received" : "No new GPS data");
  
if (newData) {
  float flat, flon, speed;
  unsigned long age;
  double altitude;
    
  // Abrir arquivo quando informações novas
  dataFile = SD.open(GPS_file_name, FILE_WRITE);

    if (dataFile) {
      pulso();
      //Serial.println("Tem arquivo no newData");

      // Dados básicos
      gps.f_get_position(&flat, &flon, &age);
      // if (line == 1) {
      //   line +=1;
      //   dataFile.print("Longitude,Latidute,Elevation,Time,Description");
      // } else{
      // LON
      dataFile.print(flon, 8);
      Serial.print("Longitude ->");
      Serial.println(flon);
      dataFile.print(",");
      // LAT
      dataFile.print(flat, 8);
      Serial.print("Latitude ->");
      Serial.println(flat);
      dataFile.print(",");
      // Elevation
      altitude = gps.altitude(); 
      altitude = altitude/100;
      dataFile.print(altitude);
      Serial.print("altitude(m)->");
      Serial.println(altitude);
      dataFile.print(",");
      // Speed
      speed = gps.f_speed_kmph();
      dataFile.print(speed, 8);
      dataFile.print(",");
      // Date/Time
      // To store the sprintf
      int year;
      byte month, day, hour, minute, second, hundredths;
      unsigned long age;
      gps.crack_datetime(&year, &month, &day, &hour, &minute, &second, &hundredths, &age);
      hour = hour - 3;
      char dataAtual[32];
      //Serial.println(year);
      //Serial.println(month);
      //Serial.println(day);
      //Serial.println(hour);
      //Serial.println(minute);
      sprintf(dataAtual, "%02d/%02d/%02d %02d:%02d:%02d ", day, month, year, hour, minute, second);
      dataFile.print(dataAtual);
      dataFile.print(",");
      Serial.println(dataAtual);
    
      // Description (Informação para os pontos da rota)
      dataFile.print("Position ");
      dataFile.print(routePosition);
      routePosition++;
      dataFile.print(",");

      // SAT (Não necessário no momento)
      //dataFile.print(gps.satellites());
      //dataFile.print(",");
      //Serial.print("SAT->");
      //Serial.print(gps.satellites());

      // PREC (Não necessário no momento)
      //dataFile.print(gps.hdop());
      //dataFile.print(",");

      dataFile.println();

    } else {
      Serial.println("Não tem arquivo no newData");
    }

    dataFile.close();

  } else {
    Serial.println("Sincronizando...");
  }

//pulso();
//}

}
