import pygame
import sys
import math
import random
import os
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
LARGURA, ALTURA = 1024, 768  # Increased resolution
LARGURA_MESA = 800
ALTURA_MESA = 400
RAIO_BOLA = 15
RAIO_BURACO = 20

# Enhanced colors with better contrast
COR_MESA = (0, 80, 0)
COR_BORDA = (60, 30, 0)
COR_BRANCA = (255, 255, 255)
COR_PRETA = (0, 0, 0)
COR_TEXTO = (240, 240, 240)
COR_FUNDO = (20, 20, 20)
COR_BOTAO = (40, 40, 40)
COR_BOTAO_HOVER = (60, 60, 60)
COR_VERMELHA = (255, 0, 0)
COR_AMARELA = (255, 255, 0)
COR_AZUL = (0, 0, 255)
COR_LARANJA = (255, 165, 0)
COR_VERDE = (0, 128, 0)
COR_ROXA = (128, 0, 128)
COR_MARROM = (139, 69, 19)
COR_JOGADOR1 = (0, 0, 255)
COR_JOGADOR2 = (255, 0, 0)
COR_MIRA = (255, 255, 255, 150)

# Game states
MENU = 0
JOGO = 1
PAUSA = 2
REPOSICIONAR = 3
FIM_JOGO = 4
ANIMACAO_TACOS = 5

# Physics constants
VELOCIDADE_MIN = 0.2
FORCA_MAX = 15.0
ATRITO = 0.99
FADE_SPEED = 5
ANIM_TACOS_DELAY = 3000
ANIM_TACOS_SPEED = 4
TACO_RECUO_MAX = 30

# Initialize audio
audio_enabled = False
try:
    pygame.mixer.init()
    audio_enabled = True
    print("Mixer de áudio inicializado com sucesso.")
except pygame.error as e:
    print(f"Erro ao inicializar o mixer de áudio: {e}. O jogo continuará sem som.")

# Initialize fonts with better quality
pygame.font.init()
try:
    fonte_principal = pygame.font.Font(None, 32)
    fonte_titulo = pygame.font.Font(None, 64)
    fonte_pequena = pygame.font.Font(None, 24)
    fonte_media = pygame.font.Font(None, 36)
    fonte_grande = pygame.font.Font(None, 48)
except:
    print("Erro ao carregar fontes. Usando fontes do sistema.")
    fonte_principal = pygame.font.SysFont(None, 32)
    fonte_titulo = pygame.font.SysFont(None, 64)
    fonte_pequena = pygame.font.SysFont(None, 24)
    fonte_media = pygame.font.SysFont(None, 36)
    fonte_grande = pygame.font.SysFont(None, 48)

# Screen setup with antialiasing
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Ultimate Billiards 2025")

[Previous classes and methods remain unchanged until JogoBilhar class]

class JogoBilhar:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.estado = MENU
        self.fade_alpha = 0
        self.fading_in = True
        self.fading_out = False
        self.proximo_estado = JOGO
        
        # Add tracking for balls pocketed in current shot
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None
        
        # [Rest of initialization code remains the same]

    def reiniciar(self):
        # [Previous reset code remains the same]
        
        # Reset shot tracking
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None
        
        # [Rest of reset code remains the same]

    def dar_tacada(self):
        if not self.bola_branca.na_mesa:
            print("Não é possível tacar, bola branca fora da mesa.")
            return

        # Reset shot tracking when new shot starts
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None

        forca_aplicada = self.forca_tacada
        self.bola_branca.vx = math.cos(self.angulo_tacada) * forca_aplicada
        self.bola_branca.vy = math.sin(self.angulo_tacada) * forca_aplicada
        self.forca_tacada = 0.0
        self.todas_paradas = False
        self.tacada_iniciada = False

        if audio_enabled and self.sons_tacada:
            som_tacada = random.choice([s for s in self.sons_tacada if s])
            if som_tacada:
                volume = min(1.0, 0.2 + 0.8 * (forca_aplicada / FORCA_MAX))
                som_tacada.set_volume(volume)
                som_tacada.play()

    def bola_encacapada(self, bola):
        print(f"Bola {bola.numero} ({"Listrada" if bola.listrada else "Lisa" if bola.numero != 0 else "Branca"}) foi encaçapada.")
        
        # Track ball for this shot
        if bola.numero != 0:  # Don't track cue ball
            self.bolas_encacapadas_na_tacada.append(bola.numero)
            self.ultima_bola_encacapada_na_tacada = bola.numero

        if audio_enabled and self.som_encacapar:
            self.som_encacapar.play()

        if bola == self.bola_branca:
            self.bola_branca_encacapada = True
            self.mensagem = "Falta! Bola branca encaçapada."
            self.tempo_mensagem = 120
            self.trocar_jogador()
            self.estado = REPOSICIONAR
            return

        # [Rest of the bola_encacapada method remains the same]

    def verificar_troca_turno(self):
        if not self.todas_paradas or self.tacada_iniciada or self.bola_branca_encacapada:
            return

        # Se nenhuma bola foi encaçapada nesta tacada
        if not self.bolas_encacapadas_na_tacada:
            self.trocar_jogador()
            return

        # Verifica se a última bola encaçapada era do tipo correto
        if self.ultima_bola_encacapada_na_tacada is not None:
            bola_obj = next((b for b in self.bolas if b.numero == self.ultima_bola_encacapada_na_tacada), None)
            if bola_obj:
                tipo_bola_encacapada = "listradas" if bola_obj.listrada else "lisas"
                tipo_jogador_atual = self.jogador1_tipo if self.jogador_atual == 1 else self.jogador2_tipo
                
                # Se os tipos não correspondem ou o tipo ainda não foi definido
                if tipo_jogador_atual is None or tipo_jogador_atual != tipo_bola_encacapada:
                    self.trocar_jogador()

        # Reset shot tracking
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None

    def atualizar(self):
        if self.estado == JOGO:
            if not self.tacada_iniciada:
                # Verificar troca de turno apenas quando as bolas param
                if self.todas_paradas and not self.bola_branca_encacapada:
                    self.verificar_troca_turno()

        # [Rest of the update method remains the same]

[Rest of the code remains unchanged]