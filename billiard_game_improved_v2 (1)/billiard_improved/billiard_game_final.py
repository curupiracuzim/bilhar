# Jogo de Bilhar Aprimorado com cenário de bar, sons e gráficos melhorados
# Versão corrigida com física de colisão melhorada, sons sincronizados, física de buracos corrigida, formação triangular padrão, ajuste de taco e mira assistida/barra de força

import pygame
import sys
import math
import random
import os

# Inicialização do Pygame
pygame.init()
audio_enabled = False
try:
    pygame.mixer.init()
    audio_enabled = True
    print("Mixer de áudio inicializado com sucesso.")
except pygame.error as e:
    print(f"Erro ao inicializar o mixer de áudio: {e}. O jogo continuará sem som.")

# Constantes
LARGURA, ALTURA = 800, 600
LARGURA_MESA = 700
ALTURA_MESA = 350
RAIO_BOLA = 15
RAIO_BURACO = 20
COR_MESA = (0, 100, 0)
COR_BORDA = (50, 25, 0)
COR_BRANCA = (255, 255, 255)
COR_PRETA = (0, 0, 0)
COR_VERMELHA = (255, 0, 0)
COR_AMARELA = (255, 255, 0)
COR_AZUL = (0, 0, 255)
COR_LARANJA = (255, 165, 0)
COR_VERDE = (0, 128, 0)
COR_ROXA = (128, 0, 128)
COR_MARROM = (139, 69, 19)
COR_TEXTO = (255, 255, 255)
COR_FUNDO = (20, 20, 20)
COR_BOTAO = (100, 100, 100)
COR_BOTAO_HOVER = (150, 150, 150)
COR_JOGADOR1 = (0, 0, 255)
COR_JOGADOR2 = (255, 0, 0)
COR_MIRA = (255, 255, 255, 150) # Cor da linha de mira (com transparência)
VELOCIDADE_MIN = 0.2  # Velocidade mínima antes de parar
FORCA_MAX = 15.0  # Força máxima da tacada
ATRITO = 0.99  # Coeficiente de atrito

# Estados do jogo
MENU = 0
JOGO = 1
PAUSA = 2
REPOSICIONAR = 3
FIM_JOGO = 4

# Configurações de fonte
pygame.font.init()
fonte_pequena = pygame.font.SysFont("Arial", 16)
fonte_media = pygame.font.SysFont("Arial", 24)
fonte_grande = pygame.font.SysFont("Arial", 36)

# Configuração da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Bilhar com Cenário de Bar")

# Carregar imagens
def carregar_imagem(nome_arquivo, tamanho=None):
    try:
        # Tenta carregar do diretório atual primeiro
        caminho_atual = os.path.join(os.getcwd(), nome_arquivo)
        if os.path.exists(caminho_atual):
            caminho = caminho_atual
        else:
            # Se não encontrar, tenta carregar do diretório do script
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)
        
        imagem = pygame.image.load(caminho).convert_alpha()
        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)
        print(f"Imagem {nome_arquivo} carregada de: {caminho}")
        return imagem
    except Exception as e:
        print(f"Erro ao carregar imagem {nome_arquivo}: {e}")
        # Criar uma superfície de placeholder
        surf = pygame.Surface((100, 100) if tamanho is None else tamanho, pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 1)
        texto_erro = fonte_pequena.render("Erro", True, (255, 0, 255))
        surf.blit(texto_erro, (5, 5))
        return surf

# Carregar sons
def carregar_som(nome_arquivo):
    if not audio_enabled:
        return None
    try:
        # Tenta carregar do diretório atual primeiro
        caminho_atual = os.path.join(os.getcwd(), nome_arquivo)
        if os.path.exists(caminho_atual):
            caminho = caminho_atual
        else:
            # Se não encontrar, tenta carregar do diretório do script
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)
            
        som = pygame.mixer.Sound(caminho)
        # Ajustar volume para baixo
        som.set_volume(0.3)
        print(f"Som {nome_arquivo} carregado de: {caminho}")
        return som
    except Exception as e:
        print(f"Erro ao carregar som {nome_arquivo}: {e}")
        return None

# Carregar música
def carregar_musica(nome_arquivo):
    if not audio_enabled:
        return
    try:
        # Tenta carregar do diretório atual primeiro
        caminho_atual = os.path.join(os.getcwd(), nome_arquivo)
        if os.path.exists(caminho_atual):
            caminho = caminho_atual
        else:
            # Se não encontrar, tenta carregar do diretório do script
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_arquivo)
            
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # -1 para tocar em loop infinito
        print(f"Música {nome_arquivo} carregada com sucesso de: {caminho}")
    except Exception as e:
        print(f"Erro ao carregar música {nome_arquivo}: {e}")

# Classe para as bolas de bilhar
class Bola:
    def __init__(self, x, y, cor, listrada=False, numero=0):
        self.x = x
        self.y = y
        self.cor = cor
        self.vx = 0
        self.vy = 0
        self.raio = RAIO_BOLA
        self.listrada = listrada
        self.numero = numero
        self.na_mesa = True
        self.massa = 1.0  # Massa da bola para cálculos de física
        self.encacapada_anim = 0 # Contador para animação de encaçapamento
    
    def mover(self):
        if not self.na_mesa:
            return
        self.x += self.vx
        self.y += self.vy
        self.vx *= ATRITO
        self.vy *= ATRITO
        
        # Se a velocidade for muito baixa, para a bola
        if abs(self.vx) < VELOCIDADE_MIN and abs(self.vy) < VELOCIDADE_MIN:
            self.vx = 0
            self.vy = 0
    
    def colisao_parede(self, x_min, y_min, x_max, y_max):
        """Verifica e resolve colisão da bola com as paredes da mesa."""
        if not self.na_mesa:
            return
        # Colisão com as paredes
        if self.x - self.raio < x_min:
            self.x = x_min + self.raio
            self.vx = -self.vx * 0.8
        elif self.x + self.raio > x_max:
            self.x = x_max - self.raio
            self.vx = -self.vx * 0.8
        
        if self.y - self.raio < y_min:
            self.y = y_min + self.raio
            self.vy = -self.vy * 0.8
        elif self.y + self.raio > y_max:
            self.y = y_max - self.raio
            self.vy = -self.vy * 0.8
    
    def colisao_buraco(self, buracos):
        """Verifica se a bola caiu em um dos buracos."""
        if not self.na_mesa:
            return False
        for buraco in buracos:
            dx = self.x - buraco[0]
            dy = self.y - buraco[1]
            distancia = math.sqrt(dx*dx + dy*dy)
            
            # Se o centro da bola estiver dentro do raio do buraco, ela cai
            if distancia < RAIO_BURACO:
                self.na_mesa = False
                self.encacapada_anim = 10 # Inicia animação de queda
                return True
        return False
    
    def colisao_bola(self, outra_bola):
        """Verifica e resolve colisão entre esta bola e outra bola."""
        if not outra_bola.na_mesa or not self.na_mesa:
            return False
            
        dx = self.x - outra_bola.x
        dy = self.y - outra_bola.y
        distancia = math.sqrt(dx*dx + dy*dy)
        
        if distancia < self.raio + outra_bola.raio:
            # Evitar divisão por zero
            if distancia == 0:
                distancia = 0.001
                
            # Normalizar o vetor de colisão
            nx = dx / distancia
            ny = dy / distancia
            
            # Calcular velocidade relativa ao longo da normal
            vx_rel = self.vx - outra_bola.vx
            vy_rel = self.vy - outra_bola.vy
            vel_normal = vx_rel * nx + vy_rel * ny
            
            # Se as bolas estão se afastando, não fazer nada
            if vel_normal > 0:
                return False
                
            # Calcular impulso (conservação de momento e energia)
            e = 0.9  # Coeficiente de restituição (elasticidade)
            j = -(1 + e) * vel_normal
            j /= (1 / self.massa) + (1 / outra_bola.massa)
            
            # Aplicar impulso
            self.vx += (j * nx) / self.massa
            self.vy += (j * ny) / self.massa
            outra_bola.vx -= (j * nx) / outra_bola.massa
            outra_bola.vy -= (j * ny) / outra_bola.massa
            
            # Corrigir sobreposição (importante para evitar bolas presas)
            penetracao = (self.raio + outra_bola.raio - distancia) * 0.5
            self.x += nx * penetracao
            self.y += ny * penetracao
            outra_bola.x -= nx * penetracao
            outra_bola.y -= ny * penetracao
            
            return True
        return False
    
    def desenhar(self, tela):
        if not self.na_mesa and self.encacapada_anim <= 0:
            return
        
        # Animação de encaçapamento (diminuir raio)
        raio_atual = self.raio
        if self.encacapada_anim > 0:
            raio_atual = int(self.raio * (self.encacapada_anim / 10.0))
            self.encacapada_anim -= 1
            if self.encacapada_anim <= 0:
                self.na_mesa = False # Garante que a bola não seja mais desenhada após a animação
                return # Não desenha mais nada após a animação

        # Desenhar a bola com efeito 3D (sombra e brilho)
        # Sombra
        pygame.draw.circle(tela, (self.cor[0]//2, self.cor[1]//2, self.cor[2]//2), 
                          (int(self.x+2), int(self.y+2)), raio_atual)
        
        # Bola principal
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), raio_atual)
        
        # Brilho
        if raio_atual > 0:
            brilho_raio = raio_atual // 3
            brilho_pos = (int(self.x - raio_atual//3), int(self.y - raio_atual//3))
            pygame.draw.circle(tela, (min(self.cor[0]+50, 255), min(self.cor[1]+50, 255), min(self.cor[2]+50, 255)), 
                              brilho_pos, brilho_raio)
        
        # Se for listrada, desenhar uma faixa branca
        if self.listrada and raio_atual > 8:
            pygame.draw.circle(tela, COR_BRANCA, (int(self.x), int(self.y)), raio_atual - 5)
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), raio_atual - 8)
        
        # Desenhar o número da bola
        if self.numero > 0 and raio_atual > 5:
            # Ajustar tamanho da fonte com base no raio atual
            tamanho_fonte = max(1, int(fonte_pequena.get_height() * (raio_atual / self.raio)))
            fonte_num = pygame.font.SysFont("Arial", tamanho_fonte)
            texto = fonte_num.render(str(self.numero), True, COR_BRANCA if self.cor == COR_PRETA else COR_PRETA)
            tela.blit(texto, (self.x - texto.get_width() // 2, self.y - texto.get_height() // 2))

# Função para desenhar linha pontilhada
def desenhar_linha_pontilhada(surf, color, start_pos, end_pos, width=1, dash_length=5):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if (x1 == x2 and y1 == y2): return

    dx = x2 - x1
    dy = y2 - y1
    distance = math.hypot(dx, dy)
    dx /= distance
    dy /= distance

    for i in range(0, int(distance / (2 * dl)), 1):
        start = (x1 + dx * i * 2 * dl, y1 + dy * i * 2 * dl)
        end = (x1 + dx * (i * 2 * dl + dl), y1 + dy * (i * 2 * dl + dl))
        pygame.draw.line(surf, color, start, end, width)

# Classe para o jogo de bilhar
class JogoBilhar:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.estado = MENU
        
        # Carregar sons
        self.sons_tacada = [
            carregar_som("forceful-hit-sound.mp3"),
            carregar_som("bonk_BEtiM8g.mp3"),
            carregar_som("metal-pipe-go-bonk.mp3")
        ]
        
        # Carregar sons de acerto
        self.sons_acerto = [
            carregar_som("pai-de-familia-delicia-cara.mp3"),
            carregar_som("yuri22-niceeeeee-krl.mp3")
        ]
        
        self.som_sequencia = carregar_som("metal-pipe-go-bonk.mp3")  # Som para 3 acertos seguidos
        self.som_encacapar = carregar_som("bonk_BEtiM8g.mp3") # Som para bola encaçapada (usando bonk por enquanto)
        if self.som_encacapar: self.som_encacapar.set_volume(0.4)
        
        # Carregar música de fundo
        carregar_musica("Promotech.mp3")
        
        # Carregar imagens
        try:
            self.chao_bar = carregar_imagem("image.png", (LARGURA, ALTURA))
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
            self.chao_bar = None
        
        self.reiniciar()
    
    def reiniciar(self):
        # Configuração da mesa
        self.x_mesa = (self.largura - LARGURA_MESA) // 2
        self.y_mesa = (self.altura - ALTURA_MESA) // 2
        
        # Buracos (caçapas)
        self.buracos = [
            (self.x_mesa, self.y_mesa),  # Superior esquerdo
            (self.x_mesa + LARGURA_MESA // 2, self.y_mesa - 5),  # Superior central
            (self.x_mesa + LARGURA_MESA, self.y_mesa),  # Superior direito
            (self.x_mesa, self.y_mesa + ALTURA_MESA),  # Inferior esquerdo
            (self.x_mesa + LARGURA_MESA // 2, self.y_mesa + ALTURA_MESA + 5),  # Inferior central
            (self.x_mesa + LARGURA_MESA, self.y_mesa + ALTURA_MESA)  # Inferior direito
        ]
        
        # Inicializar bolas
        self.bolas = []
        
        # Bola branca
        self.bola_branca = Bola(self.x_mesa + LARGURA_MESA // 4, self.y_mesa + ALTURA_MESA // 2, COR_BRANCA, numero=0)
        self.bolas.append(self.bola_branca)
        
        # Posição inicial do triângulo de bolas (Foot Spot)
        x_foot_spot = self.x_mesa + LARGURA_MESA * 3 // 4
        y_foot_spot = self.y_mesa + ALTURA_MESA // 2
        
        # Definir as bolas (1 a 15)
        bolas_numeradas = []
        cores_bolas = {
            1: COR_AMARELA, 2: COR_AZUL, 3: COR_VERMELHA, 4: COR_ROXA, 5: COR_LARANJA,
            6: COR_VERDE, 7: COR_MARROM, 8: COR_PRETA, 9: COR_AMARELA, 10: COR_AZUL,
            11: COR_VERMELHA, 12: COR_ROXA, 13: COR_LARANJA, 14: COR_VERDE, 15: COR_MARROM
        }
        for i in range(1, 16):
            listrada = i > 8
            bolas_numeradas.append(Bola(0, 0, cores_bolas[i], listrada, i))
        
        # Embaralhar as bolas (exceto a 8)
        bola_8 = next(b for b in bolas_numeradas if b.numero == 8)
        bolas_numeradas.remove(bola_8)
        random.shuffle(bolas_numeradas)
        
        # Posicionar as bolas no triângulo
        bolas_triangulo = [None] * 15
        bolas_triangulo[0] = bolas_numeradas.pop(0) # Bola da ponta
        bolas_triangulo[4] = bola_8 # Bola 8 no centro da 3ª linha
        
        # Garantir que os cantos traseiros tenham uma lisa e uma listrada
        bola_canto1 = bolas_numeradas.pop(random.randrange(len(bolas_numeradas)))
        bola_canto2 = None
        for i in range(len(bolas_numeradas) - 1, -1, -1):
            if bolas_numeradas[i].listrada != bola_canto1.listrada:
                bola_canto2 = bolas_numeradas.pop(i)
                break
        if bola_canto2 is None: # Caso raro de não encontrar oposta, pega qualquer uma
             bola_canto2 = bolas_numeradas.pop(0)
             
        bolas_triangulo[10] = bola_canto1 # Canto inferior esquerdo
        bolas_triangulo[14] = bola_canto2 # Canto inferior direito
        
        # Preencher o restante do triângulo com as bolas embaralhadas
        idx_restante = 0
        for i in range(15):
            if bolas_triangulo[i] is None:
                bolas_triangulo[i] = bolas_numeradas[idx_restante]
                idx_restante += 1
        
        # Calcular posições do triângulo
        espacamento_x = RAIO_BOLA * 2 * math.sqrt(3) / 2 # Distância horizontal entre centros
        espacamento_y = RAIO_BOLA * 2 * 0.5 # Metade da distância vertical
        
        idx_bola = 0
        for linha in range(5):
            for col in range(linha + 1):
                x = x_foot_spot + linha * espacamento_x
                y = y_foot_spot + (col * 2 - linha) * (RAIO_BOLA + 1) # +1 para pequeno espaço
                
                bola_atual = bolas_triangulo[idx_bola]
                bola_atual.x = x
                bola_atual.y = y
                self.bolas.append(bola_atual)
                idx_bola += 1
        
        # Variáveis de controle
        self.jogador_atual = 1
        self.pontos_jogador1 = 0
        self.pontos_jogador2 = 0
        self.tacada_iniciada = False
        self.forca_tacada = 0
        self.angulo_tacada = 0
        self.todas_paradas = True
        self.mensagem = "Jogador 1, sua vez!"
        self.tempo_mensagem = 0
        self.bola_branca_encacapada = False
        self.ultima_bola_encacapada = None
        self.jogador1_tipo = None  # "lisas" ou "listradas"
        self.jogador2_tipo = None
        self.bola_8_encacapada = False
        self.vencedor = None
        
        # Contador de acertos consecutivos
        self.acertos_consecutivos_j1 = 0
        self.acertos_consecutivos_j2 = 0
        
        # Variável para controlar colisões recentes (evitar sons repetidos)
        self.ultima_colisao = 0
        self.tempo_entre_colisoes = 10  # frames entre colisões para tocar som
    
    def atualizar(self):
        """Atualiza o estado do jogo a cada frame (movimento, colisões, regras)."""
        if self.estado == JOGO:
            # Verificar se todas as bolas estão paradas
            self.todas_paradas = all(bola.vx == 0 and bola.vy == 0 for bola in self.bolas if bola.na_mesa)
            
            # Mover as bolas
            for bola in self.bolas:
                bola.mover()
            
            # Verificar colisões e encaçapamentos
            bola_encacapada_nesta_jogada = False
            for _ in range(5): # Iterar algumas vezes para resolver colisões múltiplas
                colisao_ocorreu = False
                for i in range(len(self.bolas)):
                    # Verificar colisão com buraco ANTES da parede
                    if self.bolas[i].na_mesa and self.bolas[i].colisao_buraco(self.buracos):
                        bola_encacapada_nesta_jogada = True
                        if audio_enabled and self.som_encacapar: self.som_encacapar.play()
                        # Lógica de pontuação e fim de jogo (movida para depois do loop de física)
                        continue # Bola já caiu, não precisa checar parede/outras bolas
                    
                    # Verificar colisão com parede
                    self.bolas[i].colisao_parede(self.x_mesa, self.y_mesa, 
                                                self.x_mesa + LARGURA_MESA, 
                                                self.y_mesa + ALTURA_MESA)
                    
                    # Verificar colisões entre bolas
                    for j in range(i + 1, len(self.bolas)):
                        if self.bolas[i].colisao_bola(self.bolas[j]):
                            colisao_ocorreu = True
                            
                            # Tocar som de colisão se a bola branca estiver envolvida
                            if (self.bolas[i] == self.bola_branca or self.bolas[j] == self.bola_branca) and self.ultima_colisao <= 0:
                                self.ultima_colisao = self.tempo_entre_colisoes
                                
                                # Tocar som de acerto quando a bola branca colide com outra
                                if self.sons_acerto and any(som is not None for som in self.sons_acerto):
                                    sons_disponiveis = [som for som in self.sons_acerto if som is not None]
                                    if audio_enabled and sons_disponiveis:
                                        random.choice(sons_disponiveis).play()
                if not colisao_ocorreu: # Se não houve mais colisões, sair do loop de física
                    break
            
            # Decrementar contador de colisão
            if self.ultima_colisao > 0:
                self.ultima_colisao -= 1
            
            # Processar bolas encaçapadas APÓS o loop de física
            bola_valida_encacapada = False
            for bola in self.bolas:
                if not bola.na_mesa and bola.encacapada_anim > 0: # Processar apenas as recém-encaçapadas
                    if bola == self.bola_branca:
                        self.bola_branca_encacapada = True
                        self.mensagem = "Falta: Bola Branca Encaçapada!"
                        self.tempo_mensagem = 180
                        if self.jogador_atual == 1: self.acertos_consecutivos_j1 = 0
                        else: self.acertos_consecutivos_j2 = 0
                    elif bola.numero == 8:
                        self.bola_8_encacapada = True
                    else:
                        self.ultima_bola_encacapada = bola # Guarda a última bola colorida encaçapada
                        # Atribuir pontos e verificar tipo
                        if self.jogador1_tipo is None:
                            self.jogador1_tipo = "lisas" if not bola.listrada else "listradas"
                            self.jogador2_tipo = "listradas" if self.jogador1_tipo == "lisas" else "lisas"
                            self.pontos_jogador1 += 1
                            self.acertos_consecutivos_j1 += 1
                            bola_valida_encacapada = True
                            self.mensagem = f"Jogador 1: {self.jogador1_tipo.capitalize()}, Jogador 2: {self.jogador2_tipo.capitalize()}"
                            self.tempo_mensagem = 180
                        else:
                            bola_do_jogador1 = (self.jogador1_tipo == "lisas" and not bola.listrada) or \
                                              (self.jogador1_tipo == "listradas" and bola.listrada)
                            
                            if (self.jogador_atual == 1 and bola_do_jogador1) or \
                               (self.jogador_atual == 2 and not bola_do_jogador1):
                                bola_valida_encacapada = True
                                if self.jogador_atual == 1:
                                    self.pontos_jogador1 += 1
                                    self.acertos_consecutivos_j1 += 1
                                    self.acertos_consecutivos_j2 = 0
                                    if self.acertos_consecutivos_j1 == 3 and self.som_sequencia:
                                        self.som_sequencia.play()
                                        self.mensagem = "Jogador 1: SEQUÊNCIA DE 3 ACERTOS!"
                                        self.tempo_mensagem = 180
                                else:
                                    self.pontos_jogador2 += 1
                                    self.acertos_consecutivos_j2 += 1
                                    self.acertos_consecutivos_j1 = 0
                                    if self.acertos_consecutivos_j2 == 3 and self.som_sequencia:
                                        self.som_sequencia.play()
                                        self.mensagem = "Jogador 2: SEQUÊNCIA DE 3 ACERTOS!"
                                        self.tempo_mensagem = 180
                            else:
                                # Encaçapou bola do adversário (falta)
                                if self.jogador_atual == 1: self.pontos_jogador2 += 1; self.acertos_consecutivos_j1 = 0
                                else: self.pontos_jogador1 += 1; self.acertos_consecutivos_j2 = 0
                                # Não troca de jogador ainda, espera todas pararem
            
            # Verificar condições de fim de jogo
            if self.bola_8_encacapada:
                jogador_ganhou = False
                if self.jogador_atual == 1 and self.pontos_jogador1 >= 7:
                    jogador_ganhou = True
                elif self.jogador_atual == 2 and self.pontos_jogador2 >= 7:
                     jogador_ganhou = True
                
                if jogador_ganhou:
                    self.vencedor = self.jogador_atual
                    self.mensagem = f"Jogador {self.vencedor} Venceu!"
                else:
                    self.vencedor = 3 - self.jogador_atual # O outro jogador ganha
                    self.mensagem = f"Falta: Bola 8 Encaçapada Ilegalmente! Jogador {self.vencedor} Venceu!"
                
                self.tempo_mensagem = 300 # Mostrar mensagem por mais tempo
                self.estado = FIM_JOGO
                return
            
            # Verificar se todas as bolas pararam para trocar jogador ou reposicionar branca
            if self.todas_paradas:
                if self.bola_branca_encacapada:
                    # Não reposiciona imediatamente, muda para o estado REPOSICIONAR
                    # A bola branca continua fora da mesa (na_mesa = False)
                    self.jogador_atual = 3 - self.jogador_atual # Troca de jogador
                    self.mensagem = f"Jogador {self.jogador_atual}: Posicione a bola branca atrás da linha."
                    self.tempo_mensagem = 180
                    self.estado = REPOSICIONAR
                    # A bola branca será colocada na mesa pelo jogador no estado REPOSICIONAR
                elif not bola_valida_encacapada and not self.tacada_iniciada: # Se não encaçapou bola válida, troca jogador
                    self.jogador_atual = 3 - self.jogador_atual
                    self.mensagem = f"Jogador {self.jogador_atual}, sua vez!"
                    self.tempo_mensagem = 120
                    # Resetar contadores de acertos consecutivos
                    if self.jogador_atual == 1: self.acertos_consecutivos_j2 = 0
                    else: self.acertos_consecutivos_j1 = 0
                
                # Resetar a última bola encaçapada
                self.ultima_bola_encacapada = None
            
            # Atualizar tempo da mensagem
            if self.tempo_mensagem > 0:
                self.tempo_mensagem -= 1
    
    def desenhar(self, tela):
        """Desenha todos os elementos do jogo na tela."""
        # Desenhar fundo (cenário de bar)
        if self.chao_bar:
            tela.blit(self.chao_bar, (0, 0))
        else:
            tela.fill(COR_FUNDO)
        
        # Desenhar a mesa com efeito 3D
        # Borda externa (sombra)
        pygame.draw.rect(tela, (30, 15, 0), (self.x_mesa - 25, self.y_mesa - 25, 
                                          LARGURA_MESA + 50, ALTURA_MESA + 50))
        # Borda principal
        pygame.draw.rect(tela, COR_BORDA, (self.x_mesa - 20, self.y_mesa - 20, 
                                          LARGURA_MESA + 40, ALTURA_MESA + 40))
        # Mesa
        pygame.draw.rect(tela, COR_MESA, (self.x_mesa, self.y_mesa, 
                                         LARGURA_MESA, ALTURA_MESA))
        
        # Desenhar os buracos com efeito 3D
        for buraco in self.buracos:
            # Sombra do buraco
            pygame.draw.circle(tela, (0, 0, 0, 128), 
                              (buraco[0]+2, buraco[1]+2), RAIO_BURACO+2)
            # Buraco
            pygame.draw.circle(tela, COR_PRETA, buraco, RAIO_BURACO)
            # Profundidade do buraco (círculo interno mais escuro)
            pygame.draw.circle(tela, (0, 0, 0), buraco, RAIO_BURACO-5)
        
        # Desenhar as bolas
        for bola in self.bolas:
            bola.desenhar(tela)
        
        # Desenhar o taco e mira quando todas as bolas estão paradas
        if self.todas_paradas and not self.bola_branca_encacapada and self.estado == JOGO:
            # Calcular a posição do taco
            angulo_rad = math.radians(self.angulo_tacada)
            x_taco = self.bola_branca.x - math.cos(angulo_rad) * (50 + self.forca_tacada * 5)
            y_taco = self.bola_branca.y - math.sin(angulo_rad) * (50 + self.forca_tacada * 5)
            x_ponta = self.bola_branca.x - math.cos(angulo_rad) * 30
            y_ponta = self.bola_branca.y - math.sin(angulo_rad) * 30
            
            # Desenhar linha de mira pontilhada
            x_mira_fim = self.bola_branca.x + math.cos(angulo_rad) * LARGURA_MESA # Linha longa
            y_mira_fim = self.bola_branca.y + math.sin(angulo_rad) * LARGURA_MESA
            desenhar_linha_pontilhada(tela, COR_MIRA, (self.bola_branca.x, self.bola_branca.y), (x_mira_fim, y_mira_fim), width=2, dash_length=10)
            
            # Desenhar o taco com efeito 3D
            # Sombra do taco
            pygame.draw.line(tela, (100, 50, 0), 
                            (x_taco+2, y_taco+2), (x_ponta+2, y_ponta+2), 7)
            # Taco principal
            pygame.draw.line(tela, (180, 100, 50), (x_taco, y_taco), (x_ponta, y_ponta), 5)
            # Ponta do taco
            pygame.draw.line(tela, (220, 220, 220), 
                            (x_ponta - math.cos(angulo_rad) * 5, y_ponta - math.sin(angulo_rad) * 5), 
                            (x_ponta, y_ponta), 5)
            
            # Desenhar indicador de força (barra visual aprimorada)
            if self.tacada_iniciada:
                # Barra de força no canto inferior esquerdo
                barra_x = 20
                barra_y = ALTURA - 40
                barra_largura = 200
                barra_altura = 20
                
                # Fundo da barra
                pygame.draw.rect(tela, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura), border_radius=5)
                # Preenchimento da barra (cor muda com a força)
                forca_percent = self.forca_tacada / FORCA_MAX
                cor_forca = (int(255 * forca_percent), int(255 * (1 - forca_percent)), 0)
                largura_preenchimento = barra_largura * forca_percent
                pygame.draw.rect(tela, cor_forca, (barra_x, barra_y, largura_preenchimento, barra_altura), border_radius=5)
                # Contorno da barra
                pygame.draw.rect(tela, COR_TEXTO, (barra_x, barra_y, barra_largura, barra_altura), 1, border_radius=5)
                
                # Texto de força
                texto_forca = fonte_pequena.render(f"Força: {int(forca_percent * 100)}%", True, COR_TEXTO)
                tela.blit(texto_forca, (barra_x + barra_largura + 10, barra_y))
        
        # Desenhar placar no topo da tela
        texto_placar = fonte_media.render(f"Jogador 1: {self.pontos_jogador1}   Jogador 2: {self.pontos_jogador2}", True, COR_TEXTO)
        tela.blit(texto_placar, (self.largura // 2 - texto_placar.get_width() // 2, 10))
        
        # Desenhar indicador de jogador atual
        if self.jogador1_tipo:
            texto_j1 = fonte_pequena.render(f"J1: {self.jogador1_tipo}", True, COR_JOGADOR1)
            texto_j2 = fonte_pequena.render(f"J2: {self.jogador2_tipo}", True, COR_JOGADOR2)
            tela.blit(texto_j1, (20, 10))
            tela.blit(texto_j2, (self.largura - 20 - texto_j2.get_width(), 10))
        
        # Desenhar mensagem temporária
        if self.tempo_mensagem > 0:
            texto_msg = fonte_media.render(self.mensagem, True, COR_TEXTO)
            tela.blit(texto_msg, (self.largura // 2 - texto_msg.get_width() // 2, 40))
        
        # Desenhar instruções no canto superior direito
        instrucoes = [
            "Mouse: Mirar",
            "Clique: Iniciar tacada",
            "Arraste: Ajustar força",
            "ESC: Pausar",
            "R: Reiniciar"
        ]
        
        # Fundo semi-transparente para as instruções
        s = pygame.Surface((200, 100), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        tela.blit(s, (self.largura - 210, 10))
        
        y_offset = 15
        for instrucao in instrucoes:
            texto = fonte_pequena.render(instrucao, True, COR_TEXTO)
            tela.blit(texto, (self.largura - 200, y_offset))
            y_offset += 20
        
        # Desenhar telas específicas
        if self.estado == MENU:
            self.desenhar_menu(tela)
        elif self.estado == PAUSA:
            self.desenhar_pausa(tela)
        elif self.estado == REPOSICIONAR:
            self.desenhar_reposicionar(tela)
        elif self.estado == FIM_JOGO:
            self.desenhar_fim_jogo(tela)
    
    def desenhar_menu(self, tela):
        # Fundo semi-transparente
        s = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        tela.blit(s, (0, 0))
        
        # Título
        texto_titulo = fonte_grande.render("Jogo de Bilhar", True, COR_TEXTO)
        tela.blit(texto_titulo, (self.largura // 2 - texto_titulo.get_width() // 2, 100))
        
        # Botão de iniciar
        mouse_pos = pygame.mouse.get_pos()
        botao_iniciar = pygame.Rect(self.largura // 2 - 100, 250, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_iniciar.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_iniciar)
        texto_iniciar = fonte_media.render("Iniciar Jogo", True, COR_TEXTO)
        tela.blit(texto_iniciar, (self.largura // 2 - texto_iniciar.get_width() // 2, 265))
        
        # Botão de sair
        botao_sair = pygame.Rect(self.largura // 2 - 100, 320, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_sair.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_sair)
        texto_sair = fonte_media.render("Sair", True, COR_TEXTO)
        tela.blit(texto_sair, (self.largura // 2 - texto_sair.get_width() // 2, 335))
    
    def desenhar_pausa(self, tela):
        # Fundo semi-transparente
        s = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        tela.blit(s, (0, 0))
        
        # Título
        texto_titulo = fonte_grande.render("Jogo Pausado", True, COR_TEXTO)
        tela.blit(texto_titulo, (self.largura // 2 - texto_titulo.get_width() // 2, 100))
        
        # Botões
        mouse_pos = pygame.mouse.get_pos()
        
        # Botão de continuar
        botao_continuar = pygame.Rect(self.largura // 2 - 100, 200, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_continuar.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_continuar)
        texto_continuar = fonte_media.render("Continuar", True, COR_TEXTO)
        tela.blit(texto_continuar, (self.largura // 2 - texto_continuar.get_width() // 2, 215))
        
        # Botão de reiniciar
        botao_reiniciar = pygame.Rect(self.largura // 2 - 100, 270, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_reiniciar.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_reiniciar)
        texto_reiniciar = fonte_media.render("Reiniciar", True, COR_TEXTO)
        tela.blit(texto_reiniciar, (self.largura // 2 - texto_reiniciar.get_width() // 2, 285))
        
        # Botão de menu
        botao_menu = pygame.Rect(self.largura // 2 - 100, 340, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_menu.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_menu)
        texto_menu = fonte_media.render("Menu Principal", True, COR_TEXTO)
        tela.blit(texto_menu, (self.largura // 2 - texto_menu.get_width() // 2, 355))
    
    def desenhar_reposicionar(self, tela):
        # Fundo semi-transparente
        s = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        tela.blit(s, (0, 0))
        
        # Mensagem
        texto = fonte_media.render("Posicione a bola branca e clique para confirmar", True, COR_TEXTO)
        tela.blit(texto, (self.largura // 2 - texto.get_width() // 2, 50))
        
        # Desenhar a bola branca na posição do mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Verificar se a posição é válida (dentro da mesa e não sobre outras bolas)
        posicao_valida = (
            self.x_mesa + 20 < mouse_pos[0] < self.x_mesa + LARGURA_MESA - 20 and
            self.y_mesa + 20 < mouse_pos[1] < self.y_mesa + ALTURA_MESA - 20
        )
        
        # Verificar colisão com outras bolas
        for bola in self.bolas:
            if bola != self.bola_branca and bola.na_mesa:
                dx = mouse_pos[0] - bola.x
                dy = mouse_pos[1] - bola.y
                distancia = math.sqrt(dx*dx + dy*dy)
                if distancia < 2 * RAIO_BOLA:
                    posicao_valida = False
                    break
        
        # Atualizar posição da bola branca
        self.bola_branca.x = mouse_pos[0]
        self.bola_branca.y = mouse_pos[1]
        
        # Desenhar indicador de posição válida/inválida
        cor_indicador = (0, 255, 0, 128) if posicao_valida else (255, 0, 0, 128)
        s = pygame.Surface((2 * RAIO_BOLA, 2 * RAIO_BOLA), pygame.SRCALPHA)
        pygame.draw.circle(s, cor_indicador, (RAIO_BOLA, RAIO_BOLA), RAIO_BOLA)
        tela.blit(s, (mouse_pos[0] - RAIO_BOLA, mouse_pos[1] - RAIO_BOLA))
    
    def desenhar_fim_jogo(self, tela):
        # Fundo semi-transparente
        s = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        tela.blit(s, (0, 0))
        
        # Mensagem de fim de jogo
        texto_fim = fonte_grande.render(f"Jogador {self.vencedor} venceu!", True, COR_TEXTO)
        tela.blit(texto_fim, (self.largura // 2 - texto_fim.get_width() // 2, 150))
        
        # Botões
        mouse_pos = pygame.mouse.get_pos()
        
        # Botão de reiniciar
        botao_reiniciar = pygame.Rect(self.largura // 2 - 100, 250, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_reiniciar.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_reiniciar)
        texto_reiniciar = fonte_media.render("Jogar Novamente", True, COR_TEXTO)
        tela.blit(texto_reiniciar, (self.largura // 2 - texto_reiniciar.get_width() // 2, 265))
        
        # Botão de menu
        botao_menu = pygame.Rect(self.largura // 2 - 100, 320, 200, 50)
        cor_botao = COR_BOTAO_HOVER if botao_menu.collidepoint(mouse_pos) else COR_BOTAO
        
        pygame.draw.rect(tela, cor_botao, botao_menu)
        texto_menu = fonte_media.render("Menu Principal", True, COR_TEXTO)
        tela.blit(texto_menu, (self.largura // 2 - texto_menu.get_width() // 2, 335))
    
    def processar_eventos(self, evento):
        if evento.type == pygame.QUIT:
            return False
        
        # Processar eventos de teclado
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.estado == JOGO:
                    self.estado = PAUSA
                elif self.estado == PAUSA:
                    self.estado = JOGO
            elif evento.key == pygame.K_r:
                self.reiniciar()
                self.estado = JOGO
        
        # Processar eventos de mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.estado == MENU:
                # Botão de iniciar
                botao_iniciar = pygame.Rect(self.largura // 2 - 100, 250, 200, 50)
                if botao_iniciar.collidepoint(mouse_pos):
                    self.reiniciar()
                    self.estado = JOGO
                
                # Botão de sair
                botao_sair = pygame.Rect(self.largura // 2 - 100, 320, 200, 50)
                if botao_sair.collidepoint(mouse_pos):
                    return False
            
            elif self.estado == PAUSA:
                # Botão de continuar
                botao_continuar = pygame.Rect(self.largura // 2 - 100, 200, 200, 50)
                if botao_continuar.collidepoint(mouse_pos):
                    self.estado = JOGO
                
                # Botão de reiniciar
                botao_reiniciar = pygame.Rect(self.largura // 2 - 100, 270, 200, 50)
                if botao_reiniciar.collidepoint(mouse_pos):
                    self.reiniciar()
                    self.estado = JOGO
                
                # Botão de menu
                botao_menu = pygame.Rect(self.largura // 2 - 100, 340, 200, 50)
                if botao_menu.collidepoint(mouse_pos):
                    self.estado = MENU
            
            elif self.estado == FIM_JOGO:
                # Botão de reiniciar
                botao_reiniciar = pygame.Rect(self.largura // 2 - 100, 250, 200, 50)
                if botao_reiniciar.collidepoint(mouse_pos):
                    self.reiniciar()
                    self.estado = JOGO
                
                # Botão de menu
                botao_menu = pygame.Rect(self.largura // 2 - 100, 320, 200, 50)
                if botao_menu.collidepoint(mouse_pos):
                    self.estado = MENU
            
            elif self.estado == REPOSICIONAR:
                # Verificar se a posição é válida
                posicao_valida = (
                    self.x_mesa + 20 < mouse_pos[0] < self.x_mesa + LARGURA_MESA - 20 and
                    self.y_mesa + 20 < mouse_pos[1] < self.y_mesa + ALTURA_MESA - 20
                )
                
                # Verificar colisão com outras bolas
                for bola in self.bolas:
                    if bola != self.bola_branca and bola.na_mesa:
                        dx = mouse_pos[0] - bola.x
                        dy = mouse_pos[1] - bola.y
                        distancia = math.sqrt(dx*dx + dy*dy)
                        if distancia < 2 * RAIO_BOLA:
                            posicao_valida = False
                            break
                
                if posicao_valida:
                    self.bola_branca.x = mouse_pos[0]
                    self.bola_branca.y = mouse_pos[1]
                    self.estado = JOGO
            
            elif self.estado == JOGO and self.todas_paradas:
                # Iniciar tacada
                self.tacada_iniciada = True
                self.forca_tacada = 0
        
        if evento.type == pygame.MOUSEBUTTONUP:
            if self.estado == JOGO and self.tacada_iniciada:
                # Finalizar tacada
                angulo_rad = math.radians(self.angulo_tacada)
                self.bola_branca.vx = math.cos(angulo_rad) * self.forca_tacada
                self.bola_branca.vy = math.sin(angulo_rad) * self.forca_tacada
                self.tacada_iniciada = False
                
                # Tocar som de tacada aleatório
                if self.sons_tacada and any(som is not None for som in self.sons_tacada):
                    sons_disponiveis = [som for som in self.sons_tacada if som is not None]
                    if sons_disponiveis:
                        random.choice(sons_disponiveis).play()
        
        if evento.type == pygame.MOUSEMOTION:
            if self.estado == JOGO:
                mouse_pos = pygame.mouse.get_pos()
                
                # Ajustar ângulo da tacada sempre que o mouse se move
                dx = self.bola_branca.x - mouse_pos[0]
                dy = self.bola_branca.y - mouse_pos[1]
                self.angulo_tacada = math.degrees(math.atan2(dy, dx))
                
                # Ajustar força da tacada APENAS se o botão estiver pressionado
                if self.tacada_iniciada:
                    distancia = math.sqrt(dx*dx + dy*dy)
                    self.forca_tacada = min(distancia / 10, FORCA_MAX)
        
        return True

# Função principal
def main():
    clock = pygame.time.Clock()
    jogo = JogoBilhar(LARGURA, ALTURA)
    
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            rodando = jogo.processar_eventos(evento)
        
        jogo.atualizar()
        jogo.desenhar(tela)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
