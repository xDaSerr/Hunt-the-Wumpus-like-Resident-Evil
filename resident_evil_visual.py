import pygame
import random
import sys
import os

pygame.init()

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
WIDTH, HEIGHT = 1280, 780
MAP_WIDTH = 900
PANEL_X = 920

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape from the Mansion")
clock = pygame.time.Clock()

ASSET_DIR = os.path.join("assets", "images")

try:
    win_img = pygame.image.load(os.path.join(ASSET_DIR, "win.jpg")).convert()
    win_img = pygame.transform.smoothscale(win_img, (220, 280))
    print("Imagen win cargada correctamente")
except Exception as e:
    win_img = None
    print("Error cargando win.jpg:", e)

try:
    lose_img = pygame.image.load(os.path.join(ASSET_DIR, "lose.jpg")).convert()
    lose_img = pygame.transform.smoothscale(lose_img, (220, 280))
    print("Imagen lose cargada correctamente")
except Exception as e:
    lose_img = None
    print("Error cargando lose.jpg:", e)


title_font = pygame.font.SysFont("consolas", 30, bold=True)
font = pygame.font.SysFont("consolas", 22)
small_font = pygame.font.SysFont("consolas", 18)

# Colores
BG = (10, 12, 16)
PANEL = (20, 24, 30)
ROOM_COLOR = (42, 48, 58)
ROOM_ADJ = (63, 72, 86)
ROOM_CURRENT = (86, 104, 128)
ROOM_HOVER = (95, 80, 80)
BORDER = (150, 160, 175)
TEXT = (230, 230, 230)
SUBTEXT = (170, 175, 185)
RED = (190, 65, 65)
GREEN = (60, 190, 120)
YELLOW = (220, 190, 80)
BLUE = (90, 150, 220)
HALL = (55, 60, 70)
PLAYER = (70, 220, 130)

# =========================================================
# MAPA Y LÓGICA BASE
# =========================================================
ROOMS = {
    1: [2, 5, 8],
    2: [1, 3, 10],
    3: [2, 4, 12],
    4: [3, 5, 14],
    5: [1, 4, 6],
    6: [5, 7, 15],
    7: [6, 8, 17],
    8: [1, 7, 9],
    9: [8, 10, 18],
    10: [2, 9, 11],
    11: [10, 12, 19],
    12: [3, 11, 13],
    13: [12, 14, 20],
    14: [4, 13, 15],
    15: [6, 14, 16],
    16: [15, 17, 20],
    17: [7, 16, 18],
    18: [9, 17, 19],
    19: [11, 18, 20],
    20: [13, 16, 19],
}

ROOM_NAMES = {
    1: "Vestíbulo", 2: "Comedor", 3: "Biblioteca", 4: "Galería",
    5: "Sala médica", 6: "Pasillo oeste", 7: "Vigilancia", 8: "Archivo",
    9: "Laboratorio A", 10: "Pasillo central", 11: "Depósito", 12: "Laboratorio B",
    13: "Contención", 14: "Generador", 15: "Dormitorio", 16: "Túnel",
    17: "Calderas", 18: "Quirófano", 19: "Cámara fría", 20: "Salida"
}

# Rectángulos del mapa (x, y, w, h)
ROOM_RECTS = {
    1: pygame.Rect(70, 70, 150, 90),
    2: pygame.Rect(280, 60, 150, 90),
    3: pygame.Rect(500, 60, 150, 90),
    4: pygame.Rect(700, 90, 150, 90),
    5: pygame.Rect(720, 240, 150, 90),
    6: pygame.Rect(690, 390, 150, 90),
    7: pygame.Rect(540, 520, 150, 90),
    8: pygame.Rect(330, 560, 150, 90),
    9: pygame.Rect(110, 520, 150, 90),
    10: pygame.Rect(40, 360, 160, 90),
    11: pygame.Rect(60, 220, 160, 90),
    12: pygame.Rect(260, 190, 150, 90),
    13: pygame.Rect(470, 200, 150, 90),
    14: pygame.Rect(560, 320, 150, 90),
    15: pygame.Rect(500, 410, 150, 90),
    16: pygame.Rect(340, 420, 150, 90),
    17: pygame.Rect(250, 320, 150, 90),
    18: pygame.Rect(250, 450, 150, 90),
    19: pygame.Rect(420, 540, 150, 90),
    20: pygame.Rect(640, 560, 150, 90),
}

def random_game():
    positions = random.sample(list(ROOMS.keys()), 6)
    return {
        "player": positions[0],
        "tyrant": positions[1],
        "dead_zones": [positions[2], positions[3]],
        "creatures": [positions[4], positions[5]],
        "ammo": 3,
        "mode": "move",   # move o shoot
        "message": "Presiona M para moverte o S para disparar.",
        "game_over": False,
        "win": False,
    }

def adjacent_hints(game):
    current = game["player"]
    adj = ROOMS[current]
    hints = []

    if game["tyrant"] in adj:
        hints.append("Escuchas una respiración monstruosa cerca.")
    if any(z in adj for z in game["dead_zones"]):
        hints.append("Sientes un aire helado y peligroso.")
    if any(c in adj for c in game["creatures"]):
        hints.append("Oyes pasos arrastrándose entre los pasillos.")

    return hints

def refresh_message(game):
    hints = adjacent_hints(game)
    if hints:
        game["message"] = " | ".join(hints)
    else:
        game["message"] = "Todo está demasiado silencioso."

def resolve_current_room(game):
    room = game["player"]

    if room == game["tyrant"]:
        game["message"] = "Entraste a la habitación del Tyrant. No sobreviviste."
        game["game_over"] = True
        game["win"] = False
        return

    if room in game["dead_zones"]:
        game["message"] = "La habitación era letal. Fin del juego."
        game["game_over"] = True
        game["win"] = False
        return

    if room in game["creatures"]:
        new_room = random.choice([r for r in ROOMS if r != room])
        game["player"] = new_room
        game["message"] = f"Una criatura te arrastró hacia {ROOM_NAMES[new_room]}."
        resolve_current_room(game)
        return

    refresh_message(game)

def tyrant_moves(game):
    if random.random() < 0.60:
        game["tyrant"] = random.choice(ROOMS[game["tyrant"]])
        if game["tyrant"] == game["player"]:
            game["message"] = "El Tyrant escuchó el disparo y llegó hasta ti."
            game["game_over"] = True
            game["win"] = False

def handle_room_click(game, clicked_room):
    if game["game_over"]:
        return

    current = game["player"]
    neighbors = ROOMS[current]

    if clicked_room not in neighbors:
        game["message"] = "Solo puedes interactuar con habitaciones conectadas."
        return

    if game["mode"] == "move":
        game["player"] = clicked_room
        resolve_current_room(game)

    elif game["mode"] == "shoot":
        if game["ammo"] <= 0:
            game["message"] = "Ya no tienes munición."
            return

        game["ammo"] -= 1

        if clicked_room == game["tyrant"]:
            game["message"] = "¡Disparo certero! Eliminaste al Tyrant."
            game["game_over"] = True
            game["win"] = True
            return

        game["message"] = "Fallaste el disparo. Algo enorme se movió..."
        tyrant_moves(game)

        if game["ammo"] == 0 and not game["game_over"]:
            game["message"] = "Te quedaste sin munición y el Tyrant sigue vivo."
            game["game_over"] = True
            game["win"] = False

# =========================================================
# DIBUJO
# =========================================================
def draw_text(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    screen.blit(surf, (x, y))

def wrap_text(text, font_obj, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if current == "" else current + " " + word
        if font_obj.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines

def center_of(rect):
    return rect.centerx, rect.centery

def draw_background():
    screen.fill(BG)

    # Líneas sutiles de fondo para que no se vea plano
    for y in range(0, HEIGHT, 24):
        pygame.draw.line(screen, (14, 17, 22), (0, y), (MAP_WIDTH, y), 1)

def draw_connections():
    drawn = set()
    for room, neighbors in ROOMS.items():
        x1, y1 = center_of(ROOM_RECTS[room])
        for n in neighbors:
            if (n, room) not in drawn:
                x2, y2 = center_of(ROOM_RECTS[n])
                pygame.draw.line(screen, HALL, (x1, y1), (x2, y2), 12)
                pygame.draw.line(screen, (85, 90, 100), (x1, y1), (x2, y2), 2)
                drawn.add((room, n))

def draw_room(room_id, game, mouse_pos):
    rect = ROOM_RECTS[room_id]
    current = game["player"]
    adjacent = ROOMS[current]

    color = ROOM_COLOR
    border = BORDER

    if room_id in adjacent:
        color = ROOM_ADJ

    if room_id == current:
        color = ROOM_CURRENT
        border = GREEN

    if rect.collidepoint(mouse_pos) and room_id in adjacent and not game["game_over"]:
        color = ROOM_HOVER

    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=12)

    # Número de habitación
    draw_text(str(room_id), small_font, SUBTEXT, rect.x + 8, rect.y + 6)

    # Nombre centrado
    name = ROOM_NAMES[room_id]
    label = small_font.render(name, True, TEXT)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)

    # Marca del jugador
    if room_id == current:
        pygame.draw.circle(screen, PLAYER, (rect.right - 20, rect.y + 20), 8)

    # Indicador de objetivo para disparar
    if game["mode"] == "shoot" and room_id in adjacent and not game["game_over"]:
        pygame.draw.rect(screen, RED, rect, width=3, border_radius=12)

def draw_map(game, mouse_pos):
    draw_connections()
    for room_id in ROOM_RECTS:
        draw_room(room_id, game, mouse_pos)

def draw_panel(game):
    pygame.draw.rect(screen, PANEL, (PANEL_X, 0, WIDTH - PANEL_X, HEIGHT))
    pygame.draw.line(screen, (50, 55, 65), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

    draw_text("ESCAPE FROM", title_font, TEXT, PANEL_X + 20, 20)
    draw_text("THE MANSION", title_font, TEXT, PANEL_X + 20, 55)

    draw_text("Ubicación actual", font, SUBTEXT, PANEL_X + 20, 125)
    draw_text(ROOM_NAMES[game["player"]], font, TEXT, PANEL_X + 20, 155)

    draw_text("Munición", font, SUBTEXT, PANEL_X + 20, 210)
    draw_text(str(game["ammo"]), font, YELLOW, PANEL_X + 20, 240)

    draw_text("Modo", font, SUBTEXT, PANEL_X + 20, 295)
    mode_text = "Mover" if game["mode"] == "move" else "Disparar"
    mode_color = BLUE if game["mode"] == "move" else RED
    draw_text(mode_text, font, mode_color, PANEL_X + 20, 325)

    draw_text("Habitaciones conectadas", font, SUBTEXT, PANEL_X + 20, 385)
    y = 420
    for n in ROOMS[game["player"]]:
        draw_text(f"{n}. {ROOM_NAMES[n]}", small_font, TEXT, PANEL_X + 20, y)
        y += 28

    draw_text("Estado / pistas", font, SUBTEXT, PANEL_X + 20, 530)
    lines = wrap_text(game["message"], small_font, 300)
    y = 565
    for line in lines[:5]:
        draw_text(line, small_font, TEXT, PANEL_X + 20, y)
        y += 24

    draw_text("Controles", font, SUBTEXT, PANEL_X + 20, 675)
    draw_text("M = mover", small_font, TEXT, PANEL_X + 20, 710)
    draw_text("S = disparar", small_font, TEXT, PANEL_X + 20, 735)
    draw_text("R = reiniciar", small_font, TEXT, PANEL_X + 150, 710)
    draw_text("ESC = salir", small_font, TEXT, PANEL_X + 150, 735)

def draw_game_over(game):
    if not game["game_over"]:
        return

    overlay = pygame.Surface((MAP_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(160, 160, 580, 360)
    pygame.draw.rect(screen, (18, 20, 24), box, border_radius=16)
    pygame.draw.rect(screen, BORDER, box, 2, border_radius=16)

    result = "MISIÓN COMPLETADA" if game["win"] else "MISIÓN FALLIDA"
    color = GREEN if game["win"] else RED

    msg = title_font.render(result, True, color)
    screen.blit(msg, msg.get_rect(center=(box.centerx, box.y + 35)))

    if game["win"]:
        if win_img is not None:
            img_rect = win_img.get_rect(center=(box.centerx, box.centery + 20))
            screen.blit(win_img, img_rect)
        else:
            fallback = font.render("No se encontró win.jpg", True, TEXT)
            screen.blit(fallback, fallback.get_rect(center=(box.centerx, box.centery + 10)))
    else:
        if lose_img is not None:
            img_rect = lose_img.get_rect(center=(box.centerx, box.centery + 20))
            screen.blit(lose_img, img_rect)
        else:
            fallback = font.render("No se encontró lose.jpg", True, TEXT)
            screen.blit(fallback, fallback.get_rect(center=(box.centerx, box.centery + 10)))

    restart = font.render("Presiona R para volver a jugar", True, TEXT)
    screen.blit(restart, restart.get_rect(center=(box.centerx, box.bottom - 25)))

def get_clicked_room(mouse_pos):
    for room_id, rect in ROOM_RECTS.items():
        if rect.collidepoint(mouse_pos):
            return room_id
    return None

# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    game = random_game()
    resolve_current_room(game)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m and not game["game_over"]:
                    game["mode"] = "move"
                    game["message"] = "Modo mover activado. Haz clic en una habitación conectada."
                elif event.key == pygame.K_s and not game["game_over"]:
                    game["mode"] = "shoot"
                    game["message"] = "Modo disparo activado. Haz clic en una habitación conectada."
                elif event.key == pygame.K_r:
                    game = random_game()
                    resolve_current_room(game)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = get_clicked_room(event.pos)
                if clicked is not None:
                    handle_room_click(game, clicked)

        draw_background()
        draw_map(game, mouse_pos)
        draw_panel(game)
        draw_game_over(game)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()