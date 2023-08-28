#include <Servo.h>
#include <ArduinoJson.h>

// Definindo os Servos
Servo eixoX;
Servo eixoY;
Servo eixoZ;

// Definindo os Pinos
const int eixoXPin = 3;
const int eixoYPin = 5;
const int eixoZPin = 6;

// Angulos que os servos podem se mover
const int posicoes[9][3] = {
  {89, 151, 151}, {84, 152, 151}, {78, 149, 147},
  {91, 143, 145}, {84, 140, 140}, {77, 143, 145},
  {92, 135, 135}, {85, 136, 135}, {76, 134, 135}
};

// Movimentos para dar dois toques na tela para ativá-la
int ativar_tela[5][3] = {
  {85, 130, 160}, {85, 128, 127}, {85, 130, 160}, {85, 128, 127}, {85, 130, 160}
};

// Movimentos para exibir as trilhas de inserções dos padrões
int preparar_tela[3][3] ={
  {85, 128, 126}, {85, 150, 150}, {85, 130, 160}
};

// Função que move os Servos
void mover(int alvoX, int alvoY, int alvoZ) {
  //int alvoX = posicoes[posicao][0]; // Posição que o eixo X precisa ir
  //int alvoY = posicoes[posicao][1]; // Posição que o eixo Y precisa ir
  //int alvoZ = posicoes[posicao][2]; // Posição que o eixo Y precisa ir

  int posicaoAtualX = eixoX.read(); 
  int posicaoAtualY = eixoY.read();
  int posicaoAtualZ = eixoZ.read();

  if (posicaoAtualX == alvoX && posicaoAtualY == alvoY && posicaoAtualZ == alvoZ) { // Se a posiçao que os Servos precisam ir forem as atuais, não faz nada
    return; 
  }

  int passoX = (alvoX - posicaoAtualX) / abs(alvoX - posicaoAtualX); // Etapas que o eixo precisa percorrer (nagativas ou positivas)
  int passoY = (alvoY - posicaoAtualY) / abs(alvoY - posicaoAtualY); // Etapas que o eixo precisa percorrer (nagativas ou positivas)
  int passoZ = (alvoZ - posicaoAtualZ) / abs(alvoZ - posicaoAtualZ); // Etapas que o eixo precisa percorrer (nagativas ou positivas)
  
  while (posicaoAtualX != alvoX || posicaoAtualY != alvoY || posicaoAtualZ != alvoZ ) { // Movendo de fato os eixos

    if (posicaoAtualX != alvoX) { // Movendo eixo X
      posicaoAtualX += passoX;
      eixoX.write(posicaoAtualX);
    }

    if (posicaoAtualY != alvoY) { // Movendo eixo Y
      posicaoAtualY += passoY;
      eixoY.write(posicaoAtualY);
    }

    if (posicaoAtualZ != alvoZ) { // Movendo eixo Z
      posicaoAtualZ += passoZ;
      eixoZ.write(posicaoAtualZ);
    }

    delay(8); // Pausa para suavizar o movimetno
  }
  delay(5); // Pausa para suavizar o movimento
}

// Iniciando os Servos
void setup() {
  Serial.begin(9600); // Taxa da transmissão entre o arduino e o computador
  eixoX.attach(eixoXPin);
  eixoY.attach(eixoYPin);
  eixoZ.attach(eixoZPin);
  mover(85, 95, 130); // Indo para a posição inicial
  delay(100);
}

void loop() {
  if (Serial.available() > 0) { // Se tiver algo a ser recebido
    String comandoString = Serial.readStringUntil('\n');
    comandoString.trim();

    DynamicJsonDocument comando(90);
    deserializeJson(comando, comandoString);

    bool controle = comando["controle"];
    JsonArray movimentos = comando["lista"]; // Lista de "passos" do movimento atual
    int tamanhoMovimentos = movimentos.size(); // Descobrindo quantos passos terão que ser executados
    int tamanhoAtivacao = sizeof(ativar_tela) / sizeof(ativar_tela[0]);
    int tamanhoPreparacao = sizeof(preparar_tela) / sizeof(preparar_tela[0]);
    // int tamanho = sizeof(movimentos) / sizeof(movimentos[0]); // Tamanho da lista

    if (controle) {
      for (int i = 0; i < tamanhoAtivacao; i++) { // Pegando os valores da lista um por um para ativar a tela
        int eixoX = ativar_tela[i][0];
        int eixoY = ativar_tela[i][1];
        int eixoZ = ativar_tela[i][2];
        mover(eixoX, eixoY, eixoZ); // Movendo o braço
      }

      delay(500);

      for (int i = 0; i < tamanhoPreparacao; i++) { // Pegando os valores da lista um por um para exibir a trilha dos padrões
        int eixoX = preparar_tela[i][0];
        int eixoY = preparar_tela[i][1];
        int eixoZ = preparar_tela[i][2];
        mover(eixoX, eixoY, eixoZ); // Movendo o braço
      }
    }

    delay(500);

    for (int i = 0; i < tamanhoMovimentos; i++) { // Pegando os valores da lista um por um e executando os passos do movimento atual
      int posicao = movimentos[i];
      int eixoX = posicoes[posicao][0];
      int eixoY = posicoes[posicao][1];
      int eixoZ = posicoes[posicao][2];
      mover(eixoX, eixoY, eixoZ); // Movendo o braço
      delay(200);
    }

    delay(100);

    mover(85, 95, 130); // Voltando para a posição inicial
  }
}