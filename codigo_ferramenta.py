import cv2, pytesseract, threading, re, serial, time, json, requests

# Um "Log" bastante arcaico, mas apenas para marcar que precisa de um Log mais robusto
def gravar_arquivo(): 
    with open('StatusDaOperacao.json', 'w') as descritor:
        json.dump(status, descritor)

# Uma camada de pseudo-proteção, para que o bot responda apenas para o usuário correto
def pegar_usuario(): 
    with open('usuario.txt', 'r') as descritor:
        usuario = int(descritor.read())

    return usuario

# Captura a imagem e faz um breve tratamento
def tratar_imagem():
    camera = cv2.VideoCapture(url) # Obtém um vínculo com a câmera
    _, imagem = camera.read() # Captura a imagem
    #imagem = cv2.imread('imagem2.jpeg')
    #imagem_blur = cv2.blur(imagem, (1,1))
    #imagem_mediana = cv2.medianBlur(imagem, 3)
    imagem_gaussiana = cv2.GaussianBlur(imagem, (3, 3), 0) # Trata a imagem
    camera.release() # Libera o recusso
    return imagem_gaussiana

# Verifica se a tela foi desbloqueada
def desbloqueio_de_tela(imagem):
    texto = pytesseract.image_to_string(imagem, config='--psm 1').lower() # Pega o texto da imagem
    print(texto)
    falha_inicial = 'padrão incorreto' # Padrão exibido nas primeiras tentativas
    falha_tempo = 'tentar novamente em \d+' # Padrão com os tempos de espera
    padrao = fr'{falha_inicial}|{falha_tempo}' # Monta a string para tentar fazer a cabnação de um ou outra
    combnacao = re.findall(padrao, texto) # Faz a combação da string buscada com o texto obtido da imagem
    print(combnacao)

    if len(combnacao) != 0:
        if tempo:= re.findall(r'\d+', combnacao[0]):
            return int(tempo[0]) # Retorna o tempo caso as tentativas tenha excedido o mínimo
        
        else:
            return False # Retorna falso caso ainda esteja nas primeiras tentativas
        
    return True # Retorna verdadeiro caso não tenha obtido nehuma combnação (no estágio atual supõe-se que foi sucesso)

# Envia os comando ao arduino
def controlar_arduino(): 
    global indice
    resultado = 0
    for indice, movimento in movimentos.items(): # Percorre o dicipnário que contém os movimentos
        if resultado == True and isinstance(resultado, bool): # Se o resultado for o boleano True quer dizer que o processo finalizou
            enviar_status() # Envia o status de finalizado para o usuário
            break

        elif resultado: # Se o resultado for um número o processo é interrompido pelo valor desse número e depois retomado
            time.sleep(resultado)
            comando = json.dumps({
                'controle': True,
                'lista': movimento
            })

            porta_arduino.write(comando.encode() + b'\n') # Enviando o comando para o arduino

        else: # Se não foi nenhum dos outros casos quer dizer que é False, então faz o processo "simplificado"
            comando = json.dumps({
                'controle': False,
                'lista': movimento
            })

            porta_arduino.write(comando.encode() + b'\n') # Enviando o comando para o arduino

        time.sleep(10) # Espera o arduino trabalhar
        resultado = desbloqueio_de_tela(tratar_imagem()) # Verifica a tela do dispositivo

# Envia o status da operação quando ela for finalizada
def enviar_status():
    tempo_atual = time.time()
    tempo_total = (tempo_atual - tempo_inicio) / 60
    status['status'] = 'Finalizado'
    status['tempo'] = tempo_total
    status['movimento'] = indice
    texto = f'O status atual é: {status["status"]} em {tempo_total:.2f} minutos. O padrão de bloqueio é o {indice}.'
    dados_resposta = {
    'chat_id':usuario,
    'text': texto
    }
    resposta = requests.post(url_resposta, json=dados_resposta)

# Exibe o status da opração quando usuário solicitar
def exibir_status():
    tempo_atual = time.time()
    tempo_total = (tempo_atual - tempo_inicio) / 60
    texto = f'O status atual é: {status["status"]} há {tempo_total:.2f} minutos. Atualmente executando o {indice}.'
    dados_resposta = {
    'chat_id':usuario,
    'text': texto
    }
    resposta = requests.post(url_resposta, json=dados_resposta)

# Bot do usuário
def bot_telegram():
    global offset
    while True:
        requisicao = requests.get(url_requisicao, params={'offset':offset}).json()

        if requisicao['ok']:
            for atualizacao in requisicao['result']:
                if atualizacao['message']['from']['id'] == usuario:
                    print('mensagem recebida', atualizacao['message']['text'])
                    if atualizacao['message']['text'] == '/s':
                        exibir_status()
                offset = atualizacao['update_id'] + 1

        else:
            print('Falha na solicitação das mensagens do bot do Telegram.')


# Variáveis
BOT = '' 
url_requisicao = f'https://api.telegram.org/bot{BOT}/getUpdates'
url_resposta = f'https://api.telegram.org/bot{BOT}/sendMessage'
status = {'status': 'em andamento', 'tempo': None, 'movimento': None} # Dicionário que contém o status da opereção
adm = 'brobotico' ; senha = 'adm.brobo' ; ip_camera = '192.168.0.101' # Variáveis para conexão remota com a câmera
url = f'rtsp://{adm}:{senha}@{ip_camera}/stream1' # URL de conexão com a câmera

movimentos = {'Movimento 01': [0, 6, 8], 'Movimento 02': [2, 8, 6], 'Movimento 03': [8, 2, 0], 'Movimento 04': [0, 6, 2],
              'Movimento 05': [2, 6, 8], 'Movimento 06': [0, 6, 8, 5, 4], 'Movimento 07': [0, 6, 8, 2, 1, 4]}


status = {'status': 'Em andamento', 'movimento': ''}
porta_arduino = serial.Serial('COM4', 9600) # Definando a porta da comunicação com o arduino
offset = 0 
tempo_inicio = time.time()
usuario = pegar_usuario()
arduino = threading.Thread(target=controlar_arduino)
bot = threading.Thread(target=bot_telegram)
arduino.start() ; bot.start() # Iniciando o sistema e o bot