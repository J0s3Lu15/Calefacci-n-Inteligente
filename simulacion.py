import pygame
import pickle
import numpy as np

with open('calefaccion_q_table.pkl', 'rb') as f:
    q_table = pickle.load(f)

pygame.init()
screen = pygame.display.set_mode((600, 450))
pygame.display.set_caption("Calefacción Inteligente")
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

house_sprite = pygame.image.load("casa.png").convert_alpha()
house_sprite = pygame.transform.scale(house_sprite, (300, 300))

# Variables del sistema térmico
T_in = 15.0
display_T_in = T_in
T_out = 0.0
T_set = 21.0

C = 8.0
R = 10.0
dt = 5.0
max_heat_step = 10.0
T_margin = 1.0

running = True

# Discretización
T_in_bins  = np.linspace(-20, 40, 30)
T_out_bins = np.linspace(-20, 40, 30)
T_set_bins = np.linspace(-10, 40, 11)

# Variables del cielo
clouds = [{
    "x": np.random.randint(0, 600),
    "y": np.random.randint(0, 120),
    "speed": np.random.uniform(0.3, 0.8)
} for _ in range(6)]

raindrops = [{
    "x": np.random.randint(0, 600),
    "y": np.random.randint(-300, 0),
    "speed": np.random.uniform(4, 8)
} for _ in range(60)]

snowflakes = [{
    "x": np.random.randint(0, 600),
    "y": np.random.randint(0, 150)
} for _ in range(50)]

lightning_active = False
lightning_timer = 0

# Dibujar cielo
def draw_sky(screen, T_out):
    global lightning_active, lightning_timer

    # COLOR DEL CIELO
    if T_out < 0:
        t_norm = np.clip(T_out / -10, 0, 1)
        color_min = np.array([50, 50, 50])
        color_max = np.array([0, 0, 0])
        sky_color = (color_min * (1 - t_norm) + color_max * t_norm).astype(int)
    elif 0 <= T_out < 19:
        t_norm = T_out / 19
        color_min = np.array([50, 50, 50])
        color_max = np.array([135, 206, 235])
        sky_color = (color_min * (1 - t_norm) + color_max * t_norm).astype(int)
    elif 19 <= T_out <= 36:
        t_norm = (T_out - 19) / (36 - 19)
        color_min = np.array([135, 206, 235])
        color_max = np.array([255, 200, 100])
        sky_color = (color_min * (1 - t_norm) + color_max * t_norm).astype(int)
    else:
        sky_color = (255, 200, 100)

    screen.fill(tuple(sky_color))

    # SOL
    if T_out >= 17:
        pygame.draw.circle(screen, (255, 255, 0), (500, 100), 40)

    # NUBES
    if T_out < 22:
        for cloud in clouds:
            cloud["x"] += cloud["speed"] * 1.2

            if cloud["x"] > 650:
                cloud["x"] = -100
                cloud["y"] = np.random.randint(0, 130)

            cx, cy = int(cloud["x"]), int(cloud["y"])
            color = (230, 230, 230)

            pygame.draw.ellipse(screen, color, (cx, cy, 60, 35))
            pygame.draw.ellipse(screen, color, (cx + 20, cy - 10, 70, 45))
            pygame.draw.ellipse(screen, color, (cx - 15, cy + 5, 55, 30))

    # LLUVIA
    if -5 <= T_out <= 5:
        for drop in raindrops:
            drop["x"] += 1.5
            drop["y"] += drop["speed"]

            if drop["y"] > 160:
                drop["y"] = np.random.randint(-200, 0)
                drop["x"] = np.random.randint(0, 600)

            pygame.draw.line(screen, (180,180,255), (drop["x"], drop["y"]),
                             (drop["x"] - 2, drop["y"] + 6), 2)

    # NIEVE
    if T_out < -5:
        for flake in snowflakes:
            flake["y"] += 1.5
            flake["x"] += 0.3

            if flake["y"] > 160:
                flake["y"] = np.random.randint(0, 20)
                flake["x"] = np.random.randint(0, 600)

            pygame.draw.circle(screen, (255,255,255), (int(flake["x"]), int(flake["y"])), 3)

    # RELÁMPAGOS
    lightning_probability = 0

    if -5 <= T_out <= 0:
        lightning_probability = 0.05
    elif 0 < T_out <= 5:
        lightning_probability = 0.01
    else:
        lightning_probability = 0

    if lightning_probability > 0:
        if not lightning_active and np.random.random() < lightning_probability:
            lightning_active = True
            lightning_timer = np.random.randint(4, 8)

    if lightning_active:
        points = [
            (450, 0),
            (460, 40),
            (430, 80),
            (470, 120),
            (440, 160)
        ]
        pygame.draw.lines(screen, (255, 255, 255), False, points, 4)

        lightning_timer -= 1
        if lightning_timer <= 0:
            lightning_active = False

# Dibujar casa
def draw_house(screen, heat_power):
    house_pos = (0,150)
    w, h = house_sprite.get_size()

    temp_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    # color ventanas
    if heat_power > 0:
        window_color = (255, 255, 0, 180)  # calor
    elif heat_power < 0:
        window_color = (100, 100, 255, 180)  # frío
    else:
        window_color = (0, 0, 0, 0)

    ventana1 = pygame.Rect(80,150,40,80)
    ventana2 = pygame.Rect(180,150,40,80)
    ventana3 = pygame.Rect(130, 90,50,50)

    pygame.draw.rect(temp_surface, window_color, ventana1)
    pygame.draw.rect(temp_surface, window_color, ventana2)
    pygame.draw.rect(temp_surface, window_color, ventana3)

    temp_surface.blit(house_sprite, (0,0))
    screen.blit(temp_surface, house_pos)

# Dibujar información
def draw_info(screen, T_in, T_out, T_set, heat_power, heater_status, consumption):
    bg = screen.get_at((0,0))[:3]
    text_color = (0,0,0) if np.mean(bg) > 150 else (255,255,255)

    lines = [
        f"Temp. interna: {T_in:.2f} °C",
        f"Temp. exterior: {T_out:.2f} °C",
        f"Temp. deseada: {T_set:.2f} °C",
        f"Otorgando: {heater_status}",
        f"Consumo: {consumption:.4f} kWh",
        "↑↓ Temp. Exterior",
        "←→ Temp. Deseada"
    ]

    for i, t in enumerate(lines):
        txt = font.render(t, True, text_color)
        screen.blit(txt, (350, 250 + i*25))

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP:    T_out += 1
            if ev.key == pygame.K_DOWN:  T_out -= 1
            if ev.key == pygame.K_RIGHT: T_set += 1
            if ev.key == pygame.K_LEFT:  T_set -= 1

    s_in  = np.digitize(T_in, T_in_bins)
    s_out = np.digitize(T_out, T_out_bins)
    s_set = np.digitize(T_set, T_set_bins)

    action = np.argmax(q_table[s_in, s_out, s_set, :])

    if action == 1:
        heat_power = np.clip(T_set - T_in, -max_heat_step, max_heat_step)
    else:
        heat_power = 0.0

    heat_loss = (T_out - T_in) / R
    T_in += (dt / C) * (heat_loss + heat_power)

    # suavizado visual
    display_T_in = display_T_in*0.2 + T_in*0.8

    # consumo
    KW_PER_UNIT = 0.3 #0.3 kw por poder de calor o frio
    heat_power_kw = abs(heat_power) * KW_PER_UNIT
    consumption = abs(heat_power_kw) * dt / 3600.0

    # estado calefacción
    if heat_power > 0:
        heater_status = "Calor"
    elif heat_power < 0:
        heater_status = "Frío"
    else:
        heater_status = "Apagado"

    # render
    draw_sky(screen, T_out)
    draw_house(screen, heat_power)
    draw_info(screen, display_T_in, T_out, T_set, heat_power, heater_status, consumption)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
