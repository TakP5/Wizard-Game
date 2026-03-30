import pygame
import sys
import os
import math
import random
import levels # Import your level data file

pygame.init()

# ================= PATHS =================
BASE_DIR = "C:\\PythonProjects"
IMG_DIR = os.path.join(BASE_DIR, "picture")

def load_img(name, size=(32, 42)):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (255,0,255), surf.get_rect(), 2)
        return surf
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

# ================= SETTINGS =================
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arctic & Rocky Metroidvania")
clock = pygame.time.Clock()

# ================= GLOBALS & FX =================
screen_shake = 0
hit_flash = 0
boss_flash = 0
current_room = 0
current_level_idx = 0
all_level_data = levels.get_levels()

def camera_offset():
    global screen_shake
    if screen_shake > 0:
        return random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)
    return 0, 0

# ================= LOAD SPRITES =================
wizard_run = [load_img(f"Wizard-{i}.png") for i in range(4)]
wizard_idle = [wizard_run[0], wizard_run[1]]
wizard_jump = load_img("Wizardjumping.png")

# NEW: Loading your custom boss images
boss_img = load_img("eyeboss-1.png", (100, 100))
rock_boss_img = load_img("rockboss.png", (110, 110)) 

# ================= COLORS & SNOW =================
SNOW_COLOR = (240, 250, 255)
FLASH, HEALTH_COLOR, BOSS_COLOR, BULLET_COLOR = (255,255,255), (200,60,60), (255,0,0), (0,150,255)
snow = [{"x":random.randint(0,WIDTH),"y":random.randint(0,HEIGHT),"s":random.randint(1,3)} for _ in range(120)]

def draw_background(sky_color, theme):
    screen.fill(sky_color)
    mountain_color = (max(0, sky_color[0]-20), max(0, sky_color[1]-20), max(0, sky_color[2]-20))
    for x in range(-80, WIDTH+80, 160): 
        pygame.draw.polygon(screen, mountain_color, [(x,440),(x+80,260),(x+160,440)])
    
    if theme == "arctic":
        for p in snow:
            pygame.draw.circle(screen, SNOW_COLOR, (p["x"], p["y"]), p["s"])
            p["y"] += p["s"]
            if p["y"] > HEIGHT: p["y"], p["x"] = -5, random.randint(0, WIDTH)

# ================= CLASSES =================
class Bullet:
    def __init__(self, x, y, dx, dy, color, size=8):
        self.rect = pygame.Rect(x, y, size, size)
        self.dx, self.dy, self.color = dx, dy, color
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

class Enemy: 
    def __init__(self, x, theme):
        self.rect = pygame.Rect(x, 410, 32, 32)
        self.vy = -10
        self.theme = theme
    def update(self, player, gravity):
        self.vy += gravity
        self.rect.y += self.vy
        if self.rect.bottom >= 440:
            self.rect.bottom = 440
            self.vy = -12 if self.theme == "arctic" else -8
            
        if self.rect.colliderect(player.rect) and not player.is_invincible:
            player.health -= 5
            player.is_invincible, player.last_hit_time = True, pygame.time.get_ticks()
    
    def draw(self, screen, offset):
        color = (40, 200, 40) if self.theme == "arctic" else (110, 100, 90)
        pygame.draw.rect(screen, color, self.rect.move(offset))
        if self.theme == "rocky": 
             pygame.draw.line(screen, (50,50,50), (self.rect.x+offset[0], self.rect.y+offset[1]), (self.rect.x+offset[0]+10, self.rect.y+offset[1]+10))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 300, 32, 42)
        self.vx, self.vy = 0, 0
        self.speed, self.jump_power = 4, 14
        self.on_ground, self.facing = False, 1
        self.anim_timer, self.frame = 0, 0
        self.health, self.bullets = 100, []
        self.is_invincible, self.last_hit_time = False, 0

    def update(self, platforms, gravity, current_time):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_a]: self.vx, self.facing = -self.speed, -1
        if keys[pygame.K_d]: self.vx, self.facing = self.speed, 1
        if keys[pygame.K_SPACE] and self.on_ground: self.vy, self.on_ground = -self.jump_power, False

        self.vy += gravity
        self.rect.x += self.vx
        self.rect.y += self.vy

        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0: self.rect.bottom, self.vy, self.on_ground = p.top, 0, True
                elif self.vy < 0: self.rect.top, self.vy = p.bottom, 0

        for b in self.bullets[:]:
            b.update()
            if not screen.get_rect().colliderect(b.rect): self.bullets.remove(b)
        
        if self.is_invincible and current_time - self.last_hit_time > 1000: self.is_invincible = False
        self.anim_timer += 1
        if self.anim_timer > 8: self.anim_timer, self.frame = 0, (self.frame + 1) % 4

    def shoot(self, target):
        bx, by = self.rect.center
        mx, my = target
        dist = math.hypot(mx-bx, my-by) or 1
        self.bullets.append(Bullet(bx, by, ((mx-bx)/dist)*15, ((my-by)/dist)*15, BULLET_COLOR))

    def draw(self, offset):
        if self.is_invincible and (pygame.time.get_ticks() // 100) % 2 == 0: return
        img = wizard_jump if not self.on_ground else (wizard_run[self.frame] if self.vx else wizard_idle[self.frame%2])
        if self.facing == -1: img = pygame.transform.flip(img, True, False)
        if hit_flash > 0:
            img = img.copy()
            img.fill(FLASH, special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(img, (self.rect.x+offset[0], self.rect.y+offset[1]))
        for b in self.bullets: pygame.draw.rect(screen, b.color, b.rect.move(offset))

class Boss:
    def __init__(self, theme):
        self.rect = pygame.Rect(520, 200, 100, 100)
        self.theme = theme
        self.max_health = 100 if theme == "arctic" else 150 
        self.health, self.timer, self.bullets = self.max_health, 0, []
        # Checks theme to pick the right image
        self.img = boss_img if theme == "arctic" else rock_boss_img

    def update(self, player):
        self.timer += 1
        self.rect.x += int(math.sin(self.timer*0.03)*3)
        self.rect.y += int(math.cos(self.timer*0.02)*2)
        if self.timer % 60 == 0:
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery) or 1
            dx, dy = (player.rect.centerx - self.rect.centerx) / dist, (player.rect.centery - self.rect.centery) / dist
            
            b_size = 8 if self.theme == "arctic" else 20
            b_color = BOSS_COLOR if self.theme == "arctic" else (120, 110, 100)
            self.bullets.append(Bullet(self.rect.centerx, self.rect.centery, dx*4, dy*4, b_color, b_size))
            
        for b in self.bullets[:]:
            b.update()
            if not screen.get_rect().colliderect(b.rect): self.bullets.remove(b)

# ================= HELPER FUNCTIONS =================
def setup_level(index):
    data = all_level_data[index]
    new_enemies = {r_id: [Enemy(x, data["theme"]) for x in x_list] for r_id, x_list in data["slimes"].items()}
    return data, new_enemies, Boss(data["theme"])

# ================= INITIALIZATION =================
player = Player()
level_data, slimes, boss = setup_level(current_level_idx)
game_over = False
victory = False

# ================= GAME LOOP =================
running = True
while running:
    current_time = pygame.time.get_ticks()
    clock.tick(60)
    
    sky_color = level_data["sky_color"]
    ice_color = level_data["ice_color"]
    gravity = level_data["gravity_mod"]
    theme = level_data["theme"]
    rooms = level_data["rooms"]

    draw_background(sky_color, theme)

    if screen_shake > 0: screen_shake -= 1
    if hit_flash > 0: hit_flash -= 1
    if boss_flash > 0: boss_flash -= 1
    offset = camera_offset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over or victory: pygame.quit(); sys.exit()
            elif event.button == 1: player.shoot(pygame.mouse.get_pos())

    if not game_over and not victory:
        player.update(rooms[current_room], gravity, current_time)
        
        if player.rect.x > WIDTH:
            if current_room < len(rooms) - 1: current_room += 1; player.rect.x = 10
            else: player.rect.x = WIDTH - player.rect.width
        elif player.rect.x < 0:
            if current_room > 0: current_room -= 1; player.rect.x = WIDTH - 40
            else: player.rect.x = 0

        if current_room in slimes:
            for s in slimes[current_room][:]:
                s.update(player, gravity)
                for b in player.bullets[:]:
                    if s.rect.colliderect(b.rect):
                        slimes[current_room].remove(s)
                        player.bullets.remove(b)

        if current_room == len(rooms) - 1:
            if boss.health > 0:
                boss.update(player)
                if player.rect.colliderect(boss.rect) and not player.is_invincible:
                    player.health -= 10
                    player.is_invincible, player.last_hit_time, hit_flash, screen_shake = True, current_time, 5, 8
                for b in boss.bullets[:]:
                    if b.rect.colliderect(player.rect) and not player.is_invincible:
                        player.health -= 5; boss.bullets.remove(b)
                        player.is_invincible, player.last_hit_time, hit_flash = True, current_time, 5
                for b in player.bullets[:]:
                    if b.rect.colliderect(boss.rect):
                        boss.health -= 5; boss_flash = 5; player.bullets.remove(b)
            else:
                current_level_idx += 1
                if current_level_idx < len(all_level_data):
                    current_room = 0
                    level_data, slimes, boss = setup_level(current_level_idx)
                    player.rect.x, player.rect.y = 100, 300
                else: victory = True

        if player.health <= 0: game_over = True

    # --- DRAW ---
    for p in rooms[current_room]: pygame.draw.rect(screen, ice_color, p.move(offset))
    if current_room in slimes:
        for s in slimes[current_room]: s.draw(screen, offset)
    player.draw(offset)
    
    if current_room == len(rooms) - 1 and boss.health > 0:
        b_img = boss.img
        if boss_flash > 0:
            b_img = b_img.copy()
            b_img.fill(FLASH, special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(b_img, boss.rect.move(offset))
        for b in boss.bullets: pygame.draw.rect(screen, b.color, b.rect.move(offset))
        pygame.draw.rect(screen, (0, 200, 0), (200, 20, (boss.health/boss.max_health)*400, 20)) 
    
    if game_over or victory:
        font = pygame.font.SysFont("Arial", 50, bold=True)
        txt = font.render("VICTORY!" if victory else "GAME OVER", True, (255,255,255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

    pygame.draw.rect(screen, HEALTH_COLOR, (20, HEIGHT-30, player.health * 2, 10))
    pygame.display.flip()

pygame.quit()