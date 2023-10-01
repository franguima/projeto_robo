import cv2, pytesseract, threading, re, serial, time, json, requests, logging, os, sys, signal, sys

class Terminal():
    def iniciar():
        try:
            if len(sys.argv) == 2:
                if sys.argv[1] == '/start':
                    if not os.path.exists(nome_arquivo_PID):
                        logger.info('PROCESSO CARREGADO NA MEMÓRIA')
                        ManipularPID.salvar_PID()
                        # Montar objeto que manipula o Arduino ; logger.info('CONTROLADOR ARDUINO CARREGADO NA MEMÓRIA')
                        # Montar o objeto que manipula o BOT do Telegram ; logger.info('SERVIDOR BOT CARREGADO NA MEMÓRIA')
                        # Iniciar os objetos

                    else:
                        PID = ManipularPID.obter_PID()
                        print('O programa já está em execução!')
                        print(f'O PID do programa é: {PID}.')
                        sys.exit(1)

                elif sys.argv[1] == '/stop':
                    if os.path.exists(nome_arquivo_PID):
                        logger.info('PROCESSO REMOVIDO DA MEMÓRIA PELO USUÁRIO')
                        MatarProcesso.agora()
                        sys.exit()
                    
                    else:
                        print('O programa não está em execução.')
                        sys.exit(1)
                
                elif sys.argv[1] == '/?':
                    print('Opções disponíveis:')
                    print('/start - Iniciar o programa')
                    print('/stop - Finalizar o programa')
                    print('/? - Exibir opções disponíveis')
                    sys.exit()

                else:
                    print('Parêmetros incorretos.')
                    print('DICA: nome_aplicacao.py < /start | /stop | /? >')
                    sys.exit(1)
            else:
                print('Parêmetros incorretos.')
                print('DICA: nome_aplicacao.py < /start | /stop | /? >')
                sys.exit(1)

        except OSError as e:
            logger.critical(f'Os parametros que foram passados estão incorretos: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            os.remove(nome_arquivo_PID)
            sys.exit(1)

        except Exception as e:
            logger.critical(f'Ocorreu um erro inesperado durante a leitura do terminal: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            os.remove(nome_arquivo_PID)
            sys.exit(1)

class CriarLogger():
    def __init__(self):
        self.logger = logging.getLogger(nome_arquivo_LOG)
        self.logger.setLevel(logging.INFO)
        # Manipulador do arquivo
        manipulador_arquivo = logging.FileHandler(nome_arquivo_LOG)
        manipulador_arquivo.setLevel(logging.INFO)
        # Manipulador do terminal
        manipulador_terminal = logging.StreamHandler()
        manipulador_terminal.setLevel(logging.INFO)
        # Configurando o formato do Log
        log_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        manipulador_arquivo.setFormatter(log_format) # Define o formato do log no manipulador do arquivo
        manipulador_terminal.setFormatter(log_format) # Define o formato do log no manipulador do terminal
        # Adicionando os manipuladores Log
        self.logger.addHandler(manipulador_arquivo) # Adiciona o manipulador do arquivo ao logger
        self.logger.addHandler(manipulador_terminal) # Adiciona o manipulador do arquivo ao logger

    def info(self, mensagem):
        self.logger.info(mensagem)

    def warning(self, mensagem):
        self.logger.warning(mensagem)

    def error(self, mensagem):
        self.logger.error(mensagem)
    
    def critical(self, mensagem):
        self.logger.critical(mensagem)

class ManipularPID():
    @staticmethod
    def salvar_PID():
        try:
            with open(nome_arquivo_PID, 'w') as descritor:
                PID = str(os.getpid())
                descritor.write(PID)
                
        except PermissionError as e:
            logger.critical(f'Sem permissão de escrita para criar o arquivo que conterá o PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)

        except IOError as e:
            logger.critical(f'Erro de I/O durante a escrita do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)
        
        except OSError as e:
            logger.critical(f'Possível erro no sistema de arquivos durante a escrita do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)
        
        except IsADirectoryError as e:
            logger.critical(f'Tentativa de escrita do LOG em um diretório: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)
        
        except ProcessLookupError as e:
            logger.critical(f'Erro ao tentar obter o PID do processo: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)

        except Exception as e:
            logger.critical(f'Ocorreu um erro inesperado durante a criação do arquivo do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            #os.remove(nome_arquivo_PID)
            sys.exit(1)

    @staticmethod
    def obter_PID():
        try:
            with open(nome_arquivo_PID, 'r') as descritor:
                PID = int(descritor.read())
                return PID
            
        except FileNotFoundError as e:
            logger.critical(f'O arquivo contendo o PID não foi encontrado: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

        except PermissionError as e:
            logger.critical(f'Sem permissão de leitura no diretório para abrir o arquivo contendo o PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

        except IOError as e:
            logger.critical(f'Erro de I/O durante a obtenção do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

        except OSError as e:
            logger.critical(f'Possível erro no sistema de arquivos durante a obtenção do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

        except ValueError as e:
            logger.critical(f'Erro durante a conversão do valor contido no arquivo PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

        except Exception as e:
            logger.critical(f'Ocorreu um erro inesperado durante a obtenção do PID: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)

class MatarProcesso():
    @staticmethod
    def agora():
        try:
            PID = ManipularPID.obter_PID()
            os.kill(PID, signal.SIGTERM)
            os.remove(nome_arquivo_PID)
            sys.exit(1)

        except ProcessLookupError as e:
            logger.critical(f'Erro ao finalizar o servidor devido ao PID fornecido ser inválio: {e}')
            logger.info('APLICAÇÃO REMOVIDA DA MEMÓRIA DEVIDO A UM ERRO CRÍTICO')
            sys.exit(1)
            
################################################################################
# Ainda falta transformar o resto do código para POO e deixá-lo mais robusto   # 
################################################################################

# Paciência

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
    combinacao = re.findall(padrao, texto) # Faz a combação da string buscada com o texto obtido da imagem
    print(combinacao)

    if len(combinacao) != 0:
        if tempo:= re.findall(r'\d+', combinacao[0]):
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


# Variáveis Globais
'''BOT = '' 
url_requisicao = f'https://api.telegram.org/bot{BOT}/getUpdates'
url_resposta = f'https://api.telegram.org/bot{BOT}/sendMessage'
status = {'status': 'em andamento', 'tempo': None, 'movimento': None} # Dicionário que contém o status da opereção
adm = 'brobotico' ; senha = 'adm.brobo' ; ip_camera = '192.168.0.101' # Variáveis para conexão remota com a câmera
url = f'rtsp://{adm}:{senha}@{ip_camera}/stream1' # URL de conexão com a câmera

movimentos = {'Movimento 01': [0, 6, 8], 'Movimento 02': [2, 8, 6], 'Movimento 03': [8, 2, 0], 'Movimento 04': [0, 6, 2],
              'Movimento 05': [2, 6, 8], 'Movimento 06': [0, 6, 8, 5, 4], 'Movimento 07': [0, 6, 8, 2, 1, 4]}

porta_arduino = serial.Serial('COM4', 9600) # Definando a porta da comunicação com o arduino
offset = 0 
tempo_inicio = time.time()
usuario = pegar_usuario()
arduino = threading.Thread(target=controlar_arduino)
bot = threading.Thread(target=bot_telegram)
arduino.start() ; bot.start()''' # Iniciando o sistema e o bot

nome_arquivo_PID = sys.argv[0].replace('.py', '.pid') # Preparando o nome para salvar o arquivo PID
nome_arquivo_LOG = sys.argv[0].replace('.py', '.log') # Preparando o nome para salvar o arquivo LOG
logger = CriarLogger()
Terminal.iniciar() # Iniciando o processo
