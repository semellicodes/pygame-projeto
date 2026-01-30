import pygame
import random
import math

# Inicialização
pygame.init()
pygame.mixer.init()

# Configurações de Tela
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Configurações de Volume
MUSIC_VOL_NORMAL = 0.1  # Volume ambiente
MUSIC_VOL_LOW = 0.02    # Volume baixo durante efeitos

# Cores
SKY_BLUE = (135, 206, 235)
SKY_STORM = (70, 80, 100)
SUN_YELLOW = (255, 223, 0)
GRASS_GREEN = (76, 175, 80)
DARK_GREEN = (56, 142, 60)
RAIN_COLOR = (180, 180, 200)

BUILDING_COLORS = [
    (255, 107, 107), (255, 159, 64), (255, 206, 86), (75, 192, 192),
    (54, 162, 235), (153, 102, 255), (255, 99, 132), (100, 221, 23),
]

PANEL_BLUE = (30, 144, 255)
PANEL_DARK = (25, 118, 210)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHADOW = (0, 0, 0, 60)
BTN_MENU_COLOR = (120, 144, 156)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cidade Solar Inteligente")
clock = pygame.time.Clock()

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.life = 1.0

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= dt * 2

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * self.life)
            size = int(self.size * self.life)
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (int(self.x - size), int(self.y - size)))

class Building:
    def __init__(self, x, y, width, height, name, consumption, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.consumption = consumption
        self.color = color
        self.has_solar = False
        self.solar_generation = 0
        self.hover = False
        self.install_animation = 0

    def install_solar(self):
        if not self.has_solar:
            self.has_solar = True
            # Geração ajustada (Média de 23 por painel)
            self.solar_generation = 22 + random.randint(-2, 5)
            self.install_animation = 1.0
            return True
        return False

    def update(self, dt):
        if self.install_animation > 0:
            self.install_animation -= dt * 2

    def draw(self, surface):
        shadow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, SHADOW, (0, 0, self.rect.width + 10, self.rect.height + 10), border_radius=8)
        surface.blit(shadow_surf, (self.rect.x + 5, self.rect.y + 5))

        for i in range(self.rect.height):
            factor = 1 - (i / self.rect.height) * 0.3
            color = tuple(int(c * factor) for c in self.color)
            pygame.draw.rect(surface, color, (self.rect.x, self.rect.y + i, self.rect.width, 1))

        border_color = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(surface, border_color, self.rect, 4, border_radius=5)

        window_cols = 3
        window_rows = 5
        window_w = (self.rect.width - 20) // window_cols
        window_h = (self.rect.height - 30) // window_rows

        for row in range(window_rows):
            for col in range(window_cols):
                wx = self.rect.x + 10 + col * window_w
                wy = self.rect.y + 15 + row * window_h
                window_color = (255, 255, 200) if random.random() > 0.3 else (200, 220, 255)
                pygame.draw.rect(surface, window_color, (wx, wy, window_w - 5, window_h - 5), border_radius=2)
                pygame.draw.rect(surface, (100, 100, 100), (wx, wy, window_w - 5, window_h - 5), 1, border_radius=2)

        if self.hover and not self.has_solar:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, 80), (0, 0, self.rect.width, self.rect.height), border_radius=5)
            surface.blit(s, self.rect.topleft)

        if self.has_solar:
            panel_y = self.rect.y - 25
            panel_rect = pygame.Rect(self.rect.x + 5, panel_y, self.rect.width - 10, 22)
            if self.install_animation > 0:
                scale = 1 + self.install_animation * 0.3
                panel_rect.inflate_ip(int((scale - 1) * panel_rect.width), int((scale - 1) * panel_rect.height))

            shadow_panel = pygame.Surface((panel_rect.width + 4, panel_rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(shadow_panel, SHADOW, (0, 0, panel_rect.width + 4, panel_rect.height + 4), border_radius=4)
            surface.blit(shadow_panel, (panel_rect.x + 2, panel_rect.y + 2))

            pygame.draw.rect(surface, PANEL_DARK, panel_rect, border_radius=4)

            cell_w = (panel_rect.width - 8) // 5
            for i in range(5):
                cell_x = panel_rect.x + 4 + i * cell_w
                cell_rect = pygame.Rect(cell_x, panel_rect.y + 3, cell_w - 2, panel_rect.height - 6)
                pygame.draw.rect(surface, PANEL_BLUE, cell_rect, border_radius=2)
                highlight = pygame.Surface((cell_w - 2, 4), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255, 255, 255, 100), (0, 0, cell_w - 2, 4))
                surface.blit(highlight, (cell_x, panel_rect.y + 3))

            pygame.draw.rect(surface, PANEL_DARK, panel_rect, 2, border_radius=4)

        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, WHITE)
        text_bg = pygame.Surface((text.get_width() + 12, text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(text_bg, (*BLACK, 180), (0, 0, text.get_width() + 12, text.get_height() + 6), border_radius=8)
        text_x = self.rect.centerx - text.get_width()//2 - 6
        text_y = self.rect.bottom + 8
        surface.blit(text_bg, (text_x, text_y))
        surface.blit(text, (self.rect.centerx - text.get_width()//2, text_y + 3))

class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(70, 120)

    def update(self, dt):
        self.x += self.speed * dt * 30
        if self.x > WIDTH + 150:
            self.x = -150

    def draw(self, surface, storm=False):
        color = (160, 160, 180) if storm else (255, 255, 255)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, color, (int(self.x + self.size*0.7), int(self.y)), int(self.size*0.8))
        pygame.draw.circle(surface, color, (int(self.x + self.size*1.3), int(self.y)), int(self.size*0.7))
        pygame.draw.ellipse(surface, color, (self.x - self.size, self.y - self.size//2, self.size*3, self.size*1.2))

class Game:
    def __init__(self):
        self.state = "menu"
        self.level = 1
        self.clouds = [Cloud(random.randint(0, WIDTH), random.randint(50, 150), random.uniform(0.5, 1.5)) for _ in range(5)]
        self.particles = []

        # --- CARREGAMENTO DE EFEITOS SONOROS ---
        self.sfx_thunder = None
        self.sfx_victory = None
        self.sfx_defeat = None

        try:
            self.sfx_thunder = pygame.mixer.Sound("trovao.mp3")
            self.sfx_victory = pygame.mixer.Sound("vitoria.mp3")
            self.sfx_defeat = pygame.mixer.Sound("derrota.mp3")

            if self.sfx_thunder: self.sfx_thunder.set_volume(0.7)
            if self.sfx_victory: self.sfx_victory.set_volume(0.6)
            if self.sfx_defeat: self.sfx_defeat.set_volume(0.7)
        except pygame.error:
            print("Aviso: Alguns arquivos de som (trovao, vitoria ou derrota) não foram encontrados.")

        self.reset_level()

    def reset_level(self):
        # RESTAURA O VOLUME DA MÚSICA AO REINICIAR
        try: pygame.mixer.music.set_volume(MUSIC_VOL_NORMAL)
        except: pass

        # --- REAJUSTE DE DIFICULDADE (ENERGIA INICIAL) ---
        if self.level == 1:
            self.energy_total = 100 # Fácil
        elif self.level == 2:
            self.energy_total = 70  # Médio (Começa com 70% de bateria)
        elif self.level == 3:
            self.energy_total = 50  # Hardcore (Começa com 50% de bateria)

        self.time = 0
        self.sun_level = 1.0
        self.storm_active = False
        self.storm_timer = 0
        self.points = 0
        self.co2_avoided = 0
        self.panels_installed = 0
        self.energy_generated = 0
        self.particles = []
        self.raindrops = []
        self.lightning_flash = 0
        self.game_over_delay_timer = 0

        self.buildings = []
        if self.level == 1:
            self.create_level_1()
        elif self.level == 2:
            self.create_level_2()
        elif self.level == 3:
            self.create_level_3()

    def create_level_1(self):
        spacing = 250
        start_x = 150
        for i in range(3):
            self.buildings.append(Building(start_x + i * spacing, 420, 160, 200, f"Casa {i+1}", 3, BUILDING_COLORS[i]))
        self.target_time = 5 # 5 Segundos (Muito rápido para terminar)

    def create_level_2(self):
        spacing = 200
        start_x = 100
        names = ["Casa", "Escola", "Loja", "Mercado", "Hospital"]
        # --- AUMENTO DE CONSUMO PARA EXIGIR 3 PAINÉIS ---
        consumptions = [12, 11, 13, 12, 11]
        for i in range(5):
            self.buildings.append(Building(start_x + i * spacing, 400 + random.randint(-20, 20), 140, 210, names[i], consumptions[i], BUILDING_COLORS[i]))

        # --- TEMPO REDUZIDO PARA PRESSÃO ---
        self.target_time = 7 # Era 10s, agora 7s (Tempestade vem rápido)

    def create_level_3(self):
        spacing = 140
        start_x = 50
        names = ["Fábrica 1", "Indústria", "Usinagem", "Depósito", "DataCenter", "Metalúrgica", "Refinaria", "Complexo"]
        # Consumo aumentado para nível difícil
        consumptions = [6, 7, 8, 6, 9, 8, 9, 7]
        for i in range(8):
            self.buildings.append(Building(start_x + i * spacing, 390 + random.randint(-30, 30), 120, 220, names[i], consumptions[i], BUILDING_COLORS[i]))

        # --- TEMPO REDUZIDO AINDA MAIS ---
        self.target_time = 9 # Era 10s, agora 9s (Muito rápido para 8 prédios)

    def update_rain(self, dt):
        if not self.storm_active:
            self.raindrops = []
            return

        if random.random() < 0.8:
            x = random.randint(0, WIDTH)
            y = -10
            speed = random.uniform(400, 700)
            self.raindrops.append([x, y, speed])

        for drop in self.raindrops:
            drop[1] += drop[2] * dt
        self.raindrops = [d for d in self.raindrops if d[1] < HEIGHT]

    def update(self, dt):
        for cloud in self.clouds:
            cloud.update(dt)

        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)

        for building in self.buildings:
            building.update(dt)

        if self.lightning_flash > 0:
            self.lightning_flash -= dt * 5

        self.update_rain(dt)

        if self.state != "playing":
            return

        # LÓGICA DO JOGO
        if self.time < self.target_time:
            self.time += dt

            total_consumption = sum(b.consumption for b in self.buildings)
            total_generation = sum(b.solar_generation * self.sun_level for b in self.buildings if b.has_solar)

            net_energy = total_generation - total_consumption
            self.energy_total += net_energy * dt
            self.energy_generated += total_generation * dt
            self.co2_avoided += total_generation * dt * 0.5

            if net_energy > 0:
                self.points += dt * 10

            # --- CHECAGEM DE VITÓRIA IMEDIATA (SPEEDRUN) ---
            if self.panels_installed == len(self.buildings):
                # Bônus massivo pelo tempo que sobrou
                time_left = self.target_time - self.time
                self.points += time_left * 100
                self.time = self.target_time # Ajusta tempo visual para 100%

                self.state = "victory"
                try: pygame.mixer.music.set_volume(MUSIC_VOL_LOW)
                except: pass
                if self.sfx_victory: self.sfx_victory.play()
                return # Sai da função

            # GAME OVER: Falta de energia
            if self.energy_total <= 0:
                self.energy_total = 0
                self.state = "gameover"
                try: pygame.mixer.music.set_volume(MUSIC_VOL_LOW)
                except: pass
                if self.sfx_defeat: self.sfx_defeat.play()

        else:
            # O TEMPO ACABOU -> TEMPESTADE IMEDIATA
            if not self.storm_active:
                self.storm_active = True
                self.sun_level = 0.3
                self.game_over_delay_timer = 0
                try: pygame.mixer.music.set_volume(MUSIC_VOL_LOW)
                except: pass
                if self.sfx_thunder: self.sfx_thunder.play()

            self.game_over_delay_timer += dt

            # Se a tempestade durar 3 segundos, Game Over
            if self.game_over_delay_timer >= 3.0:
                self.state = "gameover"
                if self.sfx_defeat: self.sfx_defeat.play()

    def draw(self, surface):
        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "tutorial":
            self.draw_tutorial(surface)
        elif self.state == "playing":
            self.draw_game(surface)
        elif self.state == "gameover":
            self.draw_gameover(surface)
        elif self.state == "victory":
            self.draw_victory(surface)

    def draw_menu(self, surface):
        for y in range(HEIGHT):
            factor = y / HEIGHT
            color = tuple(int(SKY_BLUE[i] * (1 - factor * 0.3)) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        for cloud in self.clouds:
            cloud.draw(surface)

        sun_x, sun_y = WIDTH - 150, 100
        for i in range(12):
            angle = i * math.pi / 6
            end_x = sun_x + int(math.cos(angle) * 110)
            end_y = sun_y + int(math.sin(angle) * 110)
            pygame.draw.line(surface, SUN_YELLOW, (sun_x, sun_y), (end_x, end_y), 6)
        pygame.draw.circle(surface, SUN_YELLOW, (sun_x, sun_y), 70)
        pygame.draw.circle(surface, (255, 240, 100), (sun_x, sun_y), 63)

        title_panel = pygame.Surface((900, 400), pygame.SRCALPHA)
        pygame.draw.rect(title_panel, (255, 255, 255, 240), (0, 0, 900, 400), border_radius=30)
        surface.blit(title_panel, (WIDTH//2 - 450, 150))

        font_title = pygame.font.Font(None, 90)
        title = font_title.render("Cidade Solar Inteligente", True, (30, 144, 255))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 180))

        font_sub = pygame.font.Font(None, 42)
        subtitle = font_sub.render("Energia Limpa e Sustentabilidade", True, GRASS_GREEN)
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 270))

        font_normal = pygame.font.Font(None, 32)
        ods = font_normal.render("ODS 7: Energia Limpa | ODS 13: Ação Climática", True, (60, 60, 60))
        surface.blit(ods, (WIDTH//2 - ods.get_width()//2, 330))

        button_rect = pygame.Rect(WIDTH//2 - 180, 420, 360, 80)
        shadow_surf = pygame.Surface((button_rect.width + 10, button_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, button_rect.width + 10, button_rect.height + 10), border_radius=20)
        surface.blit(shadow_surf, (button_rect.x + 5, button_rect.y + 5))

        for i in range(button_rect.height):
            factor = i / button_rect.height
            color = tuple(int(GRASS_GREEN[j] * (1 - factor * 0.2)) for j in range(3))
            pygame.draw.rect(surface, color, (button_rect.x, button_rect.y + i, button_rect.width, 1))

        pygame.draw.rect(surface, DARK_GREEN, button_rect, 5, border_radius=20)
        play_text = pygame.font.Font(None, 56).render("JOGAR", True, WHITE)
        surface.blit(play_text, (WIDTH//2 - play_text.get_width()//2, button_rect.y + 20))

        instructions = [
            "Clique nos prédios para instalar painéis solares",
            "Mantenha a energia positiva para evitar apagão",
            "Cuidado com as tempestades!"
        ]
        y = 570
        for inst in instructions:
            text = font_normal.render(inst, True, (40, 40, 40))
            bg = pygame.Surface((text.get_width() + 30, text.get_height() + 20), pygame.SRCALPHA)
            pygame.draw.rect(bg, (255, 255, 255, 200), (0, 0, bg.get_width(), bg.get_height()), border_radius=15)
            surface.blit(bg, (WIDTH//2 - bg.get_width()//2, y - 10))
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 50

    def draw_tutorial(self, surface):
        for y in range(HEIGHT):
            factor = y / HEIGHT
            color = tuple(int(SKY_BLUE[i] * (1 - factor * 0.3)) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        # Painel de fundo
        panel = pygame.Surface((1100, 720), pygame.SRCALPHA) # Aumentei um pouco a largura do painel
        pygame.draw.rect(panel, (255, 255, 255, 250), (0, 0, 1100, 720), border_radius=30)
        surface.blit(panel, (WIDTH//2 - 550, 40))

        font_title = pygame.font.Font(None, 70)
        font_subtitle = pygame.font.Font(None, 36)
        font_normal = pygame.font.Font(None, 28) # Fonte um pouco maior
        font_small = pygame.font.Font(None, 24)  # Fonte um pouco maior

        title = font_title.render("Como Jogar?", True, (30, 144, 255))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        # Faixa do Objetivo
        objective_bg = pygame.Surface((1000, 50), pygame.SRCALPHA)
        pygame.draw.rect(objective_bg, (76, 175, 80, 40), (0, 0, 1000, 50), border_radius=15)
        surface.blit(objective_bg, (WIDTH//2 - 500, 120))

        objective = font_subtitle.render("OBJETIVO: Manter sua cidade iluminada com energia solar!", True, (76, 175, 80))
        surface.blit(objective, (WIDTH//2 - objective.get_width()//2, 132))

        instructions = [
            {
                "title": "CONSUMO DE ENERGIA",
                "desc": "Cada prédio da cidade consome energia constantemente.",
                "detail": "A barra de energia no topo mostra quanto você tem.",
                "color": (244, 67, 54)
            },
            {
                "title": "PAINÉIS SOLARES",
                "desc": "Clique com o mouse nos prédios para instalar painéis.",
                "detail": "Os painéis aparecem no teto e geram energia limpa!",
                "color": (30, 144, 255)
            },
            {
                "title": "GERAÇÃO DE ENERGIA",
                "desc": "Painéis produzem energia quando o sol está brilhando.",
                "detail": "Quanto mais painéis, mais energia sua cidade terá!",
                "color": (255, 193, 7)
            },
            {
                "title": "CUIDADO COM APAGÕES",
                "desc": "Se a energia chegar a ZERO, a cidade fica no escuro!",
                "detail": "Fique de olho na barra e instale painéis rápido.",
                "color": (156, 39, 176)
            },
            {
                "title": "TEMPESTADES",
                "desc": "Durante tempestades, a geração de energia cai muito.",
                "detail": "Instale painéis ANTES das tempestades aparecerem!",
                "color": (255, 152, 0)
            },
            {
                "title": "COMO VENCER",
                "desc": "Sobreviva até o tempo alvo de cada nível.",
                "detail": "Cada nível tem mais prédios e menos tempo!",
                "color": (76, 175, 80)
            }
        ]

        # --- LÓGICA DE DUAS COLUNAS ---
        start_y = 200
        col_width = 480 # Largura de cada coluna
        col_gap = 40    # Espaço entre colunas
        left_x = WIDTH//2 - 500
        right_x = WIDTH//2 + 20

        for i, inst in enumerate(instructions):
            # Define se vai desenhar na esquerda (0,1,2) ou direita (3,4,5)
            if i < 3:
                x = left_x
                y = start_y + (i * 140) # Espaçamento vertical
            else:
                x = right_x
                y = start_y + ((i-3) * 140)

            # Desenha o Bloco
            title_text = font_normal.render(inst["title"], True, inst["color"])
            surface.blit(title_text, (x, y))

            desc_text = font_small.render(inst["desc"], True, (40, 40, 40))
            surface.blit(desc_text, (x, y + 28))

            detail_text = font_small.render(inst["detail"], True, (100, 100, 100))
            surface.blit(detail_text, (x, y + 50))

        # Dica final
        tip_bg = pygame.Surface((1000, 40), pygame.SRCALPHA)
        pygame.draw.rect(tip_bg, (33, 150, 243, 40), (0, 0, 1000, 40), border_radius=15)
        surface.blit(tip_bg, (WIDTH//2 - 500, 630))

        tip = font_normal.render("DICA: Instale painéis em TODOS os prédios o mais rápido possível!", True, (33, 150, 243))
        surface.blit(tip, (WIDTH//2 - tip.get_width()//2, 640))

        # Botão Começar
        button_rect = pygame.Rect(WIDTH//2 - 150, 685, 300, 60)
        pygame.draw.rect(surface, GRASS_GREEN, button_rect, border_radius=15)
        pygame.draw.rect(surface, DARK_GREEN, button_rect, 4, border_radius=15)
        continue_text = font_subtitle.render("COMEÇAR!", True, WHITE)
        surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, 705))

    def draw_game(self, surface):
        if self.storm_active:
            for y in range(HEIGHT):
                factor = y / HEIGHT
                color = tuple(int(SKY_STORM[i] * (1 - factor * 0.2)) for i in range(3))
                pygame.draw.line(surface, color, (0, y), (WIDTH, y))

            for drop in self.raindrops:
                pygame.draw.line(surface, RAIN_COLOR, (drop[0], drop[1]), (drop[0], drop[1]+15), 2)

            if random.random() < 0.02:
                self.lightning_flash = 1.0
                x = random.randint(100, WIDTH - 100)
                points = [(x, 0)]
                y = 0
                for _ in range(6):
                    x += random.randint(-40, 40)
                    y += random.randint(50, 100)
                    points.append((x, y))
                pygame.draw.lines(surface, WHITE, False, points, 5)
                pygame.draw.lines(surface, (200, 200, 255), False, points, 2)
        else:
            for y in range(HEIGHT):
                factor = y / HEIGHT
                color = tuple(int(SKY_BLUE[i] * (1 - factor * 0.3)) for i in range(3))
                pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        for cloud in self.clouds:
            cloud.draw(surface, self.storm_active)

        if not self.storm_active:
            sun_x, sun_y = WIDTH - 120, 100
            sun_size = int(65 * self.sun_level)
            for i in range(12):
                angle = i * math.pi / 6 + self.time
                end_x = sun_x + int(math.cos(angle) * (sun_size + 35))
                end_y = sun_y + int(math.sin(angle) * (sun_size + 35))
                pygame.draw.line(surface, SUN_YELLOW, (sun_x, sun_y), (end_x, end_y), 5)

            pygame.draw.circle(surface, SUN_YELLOW, (sun_x, sun_y), sun_size)
            pygame.draw.circle(surface, (255, 240, 100), (sun_x, sun_y), sun_size - 5)

        grass_height = HEIGHT - 150
        for y in range(grass_height, HEIGHT):
            factor = (y - grass_height) / (HEIGHT - grass_height)
            color = tuple(int(GRASS_GREEN[i] * (1 - factor * 0.3)) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        for i in range(0, WIDTH, 20):
            blade_x = i + random.randint(-5, 5)
            blade_y = grass_height + random.randint(0, 30)
            pygame.draw.line(surface, DARK_GREEN, (blade_x, blade_y),
                           (blade_x + random.randint(-3, 3), blade_y - 15), 2)

        mouse_pos = pygame.mouse.get_pos()
        for building in self.buildings:
            building.hover = building.rect.collidepoint(mouse_pos) and not building.has_solar
            building.draw(surface)

        for particle in self.particles:
            particle.draw(surface)

        if self.lightning_flash > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(180 * self.lightning_flash)
            flash_surface.fill((255, 255, 255, alpha))
            surface.blit(flash_surface, (0,0))

        self.draw_hud(surface)

    def draw_hud(self, surface):
        font = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 26)

        hud_panel = pygame.Surface((380, 320), pygame.SRCALPHA)
        pygame.draw.rect(hud_panel, (255, 255, 255, 230), (0, 0, 380, 320), border_radius=20)
        surface.blit(hud_panel, (20, 20))

        bar_width = 340
        bar_height = 40
        bar_x, bar_y = 40, 40

        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), border_radius=20)
        energy_percent = max(0, min(1, self.energy_total / 100))
        energy_width = int(bar_width * energy_percent)

        if energy_percent > 0.5:
            color1, color2 = (76, 175, 80), (129, 199, 132)
        elif energy_percent > 0.25:
            color1, color2 = (255, 167, 38), (255, 202, 40)
        else:
            color1, color2 = (244, 67, 54), (239, 83, 80)

        for i in range(energy_width):
            factor = i / bar_width
            color = tuple(int(color1[j] + (color2[j] - color1[j]) * factor) for j in range(3))
            pygame.draw.rect(surface, color, (bar_x + i, bar_y, 1, bar_height))

        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=20)
        energy_text = font.render(f"Energia: {int(self.energy_total)}", True, (50, 50, 50))
        surface.blit(energy_text, (bar_x + 10, bar_y + 8))

        y_offset = 100
        info_items = [
            (f"Nível: {self.level}", (30, 144, 255)),
            (f"Tempo: {int(min(self.time, self.target_time))}s / {self.target_time}s", (100, 100, 100)),
            (f"Painéis: {self.panels_installed}", (255, 152, 0)),
            (f"Pontos: {int(self.points)}", (156, 39, 176)),
            (f"CO2: {int(self.co2_avoided)} kg", (76, 175, 80))
        ]

        for text_str, color in info_items:
            text = font_small.render(text_str, True, color)
            surface.blit(text, (40, y_offset))
            y_offset += 40

        if self.storm_active:
            alert_panel = pygame.Surface((300, 60), pygame.SRCALPHA)
            pygame.draw.rect(alert_panel, (255, 235, 59, 240), (0, 0, 300, 60), border_radius=15)
            surface.blit(alert_panel, (WIDTH//2 - 150, 20))
            storm_text = font.render("TEMPESTADE!", True, (198, 40, 40))
            surface.blit(storm_text, (WIDTH//2 - storm_text.get_width()//2, 35))

    def draw_gameover(self, surface):
        # --- FUNDO VERMELHO (DERROTA) ---
        for y in range(HEIGHT):
            factor = y / HEIGHT
            # Gradiente de Vermelho Escuro para Preto
            # R: 60->20, G: 0, B: 0
            r = int(60 * (1 - factor * 0.5))
            color = (r, 0, 0)
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        # Painel central
        panel = pygame.Surface((700, 550), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 0, 0, 200), (0, 0, 700, 550), border_radius=30)
        # Borda vermelha brilhante
        pygame.draw.rect(panel, (200, 50, 50), (0, 0, 700, 550), 3, border_radius=30)
        surface.blit(panel, (WIDTH//2 - 350, 120))

        font_title = pygame.font.Font(None, 90)
        font_normal = pygame.font.Font(None, 40)

        # Título em Vermelho Neon
        title = font_title.render("APAGÃO!", True, (255, 80, 80))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        if self.energy_total <= 0:
            msg = "Energia esgotada! Instale mais rápido!"
        else:
            msg = "Tempo esgotado! A tempestade venceu."

        subtitle = font_normal.render(msg, True, (255, 200, 200))
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 250))

        stats = [
            (f"Tempo: {int(self.target_time)}s", (255, 255, 255)),
            (f"Painéis: {self.panels_installed} / {len(self.buildings)}", (255, 150, 150)),
            (f"CO2: {int(self.co2_avoided)} kg", (255, 150, 150)),
            (f"Pontos: {int(self.points)}", (255, 150, 150))
        ]

        y = 330
        for stat, color in stats:
            text = font_normal.render(stat, True, color)
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 55

        # Botões VERMELHOS (Para manter o tema de alerta)
        button_rect = pygame.Rect(WIDTH//2 - 200, 540, 400, 60)
        pygame.draw.rect(surface, (200, 60, 60), button_rect, border_radius=15) # Vermelho botão
        pygame.draw.rect(surface, (150, 30, 30), button_rect, 4, border_radius=15) # Borda escura
        restart_text = font_normal.render("TENTAR NOVAMENTE", True, WHITE)
        surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 555))

        menu_rect = pygame.Rect(WIDTH//2 - 200, 620, 400, 60)
        pygame.draw.rect(surface, (100, 100, 100), menu_rect, border_radius=15) # Cinza para menu
        pygame.draw.rect(surface, (60, 60, 60), menu_rect, 4, border_radius=15)
        menu_text = font_normal.render("MENU INICIAL", True, WHITE)
        surface.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 635))

    def draw_victory(self, surface):
        # --- FUNDO VERDE/AZUL (VITÓRIA) ---
        for y in range(HEIGHT):
            factor = y / HEIGHT
            # Gradiente de Verde Limão para Verde Floresta
            r = int(100 * (1 - factor))
            g = int(200 + factor * 30) # Muito verde
            b = int(100 + factor * 100)
            color = (r, g, b)
            if y < 5: color = (255, 255, 255) # Brilho no topo
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))

        # Confetes coloridos
        for _ in range(40): # Mais confetes!
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            color = random.choice([(255, 255, 0), (255, 100, 100), (100, 255, 100), (100, 200, 255)])
            size = random.randint(4, 12)
            pygame.draw.circle(surface, color, (x, y), size)

        # Painel central (Branco com leve tom verde)
        panel_h = 680
        panel_y = (HEIGHT - panel_h) // 2
        panel = pygame.Surface((850, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (240, 255, 240, 240), (0, 0, 850, panel_h), border_radius=30)
        # Borda verde
        pygame.draw.rect(panel, (76, 175, 80), (0, 0, 850, panel_h), 4, border_radius=30)
        surface.blit(panel, (WIDTH//2 - 425, panel_y))

        font_title = pygame.font.Font(None, 80)
        font_normal = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)

        # Título Verde Escuro
        title = font_title.render("PARABÉNS!", True, (30, 100, 30))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, panel_y + 40))

        subtitle = font_normal.render("Você criou uma cidade sustentável!", True, (50, 150, 50))
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, panel_y + 110))

        stats = [
            (f"Painéis instalados: {self.panels_installed}", (0, 150, 0)), # Verde
            (f"Energia gerada: {int(self.energy_generated)} un.", (0, 120, 200)), # Azul
            (f"CO2 evitado: {int(self.co2_avoided)} kg", (0, 150, 0)), # Verde
            (f"Economia: {int((self.panels_installed / max(1, len(self.buildings))) * 100)}%", (200, 150, 0)), # Dourado
            (f"Pontos finais: {int(self.points)}", (255, 100, 0)) # Laranja
        ]

        y = panel_y + 170
        for stat, color in stats:
            text = font_normal.render(stat, True, color)
            # Fundo branco suave atrás do texto para ler melhor
            bg = pygame.Surface((text.get_width() + 40, text.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(bg, (255, 255, 255, 180), (0, 0, bg.get_width(), bg.get_height()), border_radius=10)

            surface.blit(bg, (WIDTH//2 - bg.get_width()//2, y - 5))
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 45

        tips_title = font_normal.render("Dicas para economizar energia:", True, (0, 100, 0))
        surface.blit(tips_title, (WIDTH//2 - tips_title.get_width()//2, y + 20))

        if self.level == 1:
            tips = ["- Desligue aparelhos da tomada quando não usar"]
        elif self.level == 2:
            tips = ["- Evite abrir geladeira desnecessariamente"]
        else:
            tips = ["- Limpe filtros de ar-condicionado regularmente"]

        y += 55
        for tip in tips:
            text = font_small.render(tip, True, (60, 60, 60))
            surface.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 30

        btn_y_start = panel_y + panel_h - 150

        # Botões VERDES (Tema de Sucesso)
        button_rect = pygame.Rect(WIDTH//2 - 200, btn_y_start, 400, 55)
        if self.level < 3:
            pygame.draw.rect(surface, (76, 175, 80), button_rect, border_radius=15) # Verde Clássico
            pygame.draw.rect(surface, (56, 142, 60), button_rect, 4, border_radius=15)
            next_text = font_normal.render("PRÓXIMO NÍVEL", True, WHITE)
        else:
            pygame.draw.rect(surface, (30, 144, 255), button_rect, border_radius=15) # Azul para zerar
            pygame.draw.rect(surface, (25, 118, 210), button_rect, 4, border_radius=15)
            next_text = font_normal.render("JOGAR NOVAMENTE", True, WHITE)
        surface.blit(next_text, (WIDTH//2 - next_text.get_width()//2, btn_y_start + 15))

        menu_rect = pygame.Rect(WIDTH//2 - 200, btn_y_start + 70, 400, 55)
        pygame.draw.rect(surface, (139, 195, 74), menu_rect, border_radius=15) # Verde mais claro
        pygame.draw.rect(surface, (104, 159, 56), menu_rect, 4, border_radius=15)
        menu_text = font_normal.render("MENU INICIAL", True, WHITE)
        surface.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, btn_y_start + 85))

    def handle_click(self, pos):
        if self.state == "menu":
            button_rect = pygame.Rect(WIDTH//2 - 180, 420, 360, 80)
            if button_rect.collidepoint(pos):
                self.state = "tutorial"
                self.level = 1

        elif self.state == "tutorial":
            button_rect = pygame.Rect(WIDTH//2 - 150, 710, 300, 60)
            if button_rect.collidepoint(pos):
                self.reset_level()
                self.state = "playing"

        elif self.state == "playing":
            for building in self.buildings:
                if building.rect.collidepoint(pos):
                    if building.install_solar():
                        self.panels_installed += 1
                        self.points += 50
                        for _ in range(15):
                            self.particles.append(Particle(building.rect.centerx, building.rect.top - 25, (30, 144, 255)))

        elif self.state == "gameover":
            button_rect = pygame.Rect(WIDTH//2 - 200, 540, 400, 60)
            if button_rect.collidepoint(pos):
                self.reset_level()
                self.state = "playing"

            menu_rect = pygame.Rect(WIDTH//2 - 200, 620, 400, 60)
            if menu_rect.collidepoint(pos):
                self.state = "menu"
                self.level = 1
                try: pygame.mixer.music.set_volume(MUSIC_VOL_NORMAL)
                except: pass

        elif self.state == "victory":
            panel_h = 680
            panel_y = (HEIGHT - panel_h) // 2
            btn_y_start = panel_y + panel_h - 150

            button_rect = pygame.Rect(WIDTH//2 - 200, btn_y_start, 400, 55)
            if button_rect.collidepoint(pos):
                if self.level < 3:
                    self.level += 1
                else:
                    self.level = 1
                self.reset_level()
                self.state = "playing"

            menu_rect = pygame.Rect(WIDTH//2 - 200, btn_y_start + 70, 400, 55)
            if menu_rect.collidepoint(pos):
                self.state = "menu"
                self.level = 1
                try: pygame.mixer.music.set_volume(MUSIC_VOL_NORMAL)
                except: pass

def main():
    try:
        pygame.mixer.music.load("musica.mp3")
        pygame.mixer.music.set_volume(MUSIC_VOL_NORMAL)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Nenhuma música encontrada. O jogo rodará sem som.")

    game = Game()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        game.update(dt)
        game.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
