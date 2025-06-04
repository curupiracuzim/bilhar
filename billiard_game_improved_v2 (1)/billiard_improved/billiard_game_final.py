# [Previous imports and constants remain the same]

class JogoBilhar:
    def __init__(self, largura, altura):
        # [Previous initialization code remains the same]
        
        # Add tracking for balls pocketed in current shot
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None
        
    def reiniciar(self):
        # [Previous reset code remains the same]
        
        # Reset shot tracking
        self.bolas_encacapadas_na_tacada = []
        self.ultima_bola_encacapada_na_tacada = None
        
    def dar_tacada(self):
        """Aplica a força na bola branca."""
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
        """Lógica quando uma bola é encaçapada."""
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
        """Verifica se o turno deve ser trocado após as bolas pararem."""
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
        """Atualiza o estado do jogo."""
        # [Previous update code remains the same]

        if self.estado == JOGO:
            if not self.tacada_iniciada:
                # Verificar troca de turno apenas quando as bolas param
                if self.todas_paradas and not self.bola_branca_encacapada:
                    self.verificar_troca_turno()

        # [Rest of the update method remains the same]

# [Rest of the code remains the same]