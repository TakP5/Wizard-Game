import pygame
import sys
import os
import math
import random
import levels

pygame.init()

# ================= PATHS =================
BASE_DIR = "C:\\PythonProjects"
IMG_DIR = os.path.join(BASE_DIR, "picture")

def load_img(name, size=(32, 42)):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        # Fallback if file is missing
        surf = pygame.Surface(size if size else (32, 42), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 100, 0), surf.get_rect(), 2)
        return surf
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            return pygame.transform.scale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (32, 42), pygame.SRCALPHA)
        return surf

# ================= SETTINGS =================
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Inkwell Isle Metroidvania")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
score_font = pygame.font.SysFont("Courier New", 24, bold=True)

# ================= COLORS =================
SNOW_COLOR = (240, 250, 255)
FLASH, HEALTH_COLOR, BOSS_COLOR = (255,255,255), (200,60,60), (255,0,0)
LASER_COLOR = (0, 255, 255) 
OCEAN_BLUE, SAND_COLOR, GRASS_COLOR, PATH_COLOR = (30, 80, 150), (240, 210, 150), (80, 160, 80), (180, 150, 100)
LAVA_GLOW = (255, 100, 0)

vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(0, 200, 4):
    alpha = int((i/200)**2 * 160)
    pygame.draw.rect(vignette, (0,0,0, alpha), (0,0, WIDTH, HEIGHT), 200-i)

# ================= GLOBALS =================
screen_shake = 0
hit_flash = 0
boss_flash = 0
current_room = 0
current_level_idx = 0
player_score = 0
laser_damage_mult = 1.0 
all_level_data = levels.get_levels()
god_mode = False 

def camera_offset():
    global screen_shake
    if screen_shake > 0:
        return random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)
    return 0, 0

# ================= OVERWORLD CLASSES =================
class MapPlayer:
    def __init__(self):
        self.base_img = load_img("MapPlayer.png", (32, 32))
        self.rect = pygame.Rect(WIDTH//2, HEIGHT//2, 32, 32)
        self.speed = 4
        self.facing = -1 

    def update(self):
        keys = pygame.key.get_pressed()
        vx, vy = 0, 0
        if keys[pygame.K_a]: 
            vx = -self.speed
            self.facing = -1
        if keys[pygame.K_d]: 
            vx = self.speed
            self.facing = 1 
        if keys[pygame.K_w]: vy = -self.speed
        if keys[pygame.K_s]: vy = self.speed
        
        self.rect.x += vx
        self.rect.y += vy
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        img = self.base_img
        if self.facing == 1:
            img = pygame.transform.flip(self.base_img, True, False)
        screen.blit(img, self.rect)

class WorldMap:
    def __init__(self):
        self.player = MapPlayer()
        self.locations = [
            (pygame.Rect(180, 160, 80, 80), 0, "Frozen Outskirts", "IceArea.png"),
            (pygame.Rect(560, 260, 80, 80), 1, "Granite Grotto", "Cave.png"),
            (pygame.Rect(380, 320, 80, 80), 2, "Molten Maw", "Lava.png"),
            (pygame.Rect(380, 100, 60, 60), 88, "The Merchant", "Merchant.png")
        ]
        self.location_images = [load_img(loc[3], (loc[0].width, loc[0].height)) for loc in self.locations]
        self.selected_id = None
        self.island_pts = []
        cx, cy = WIDTH//2, HEIGHT//2
        for i in range(0, 360, 10):
            rad = math.radians(i)
            dist = 300 + math.sin(rad * 4) * 30 + math.cos(rad * 7) * 20
            self.island_pts.append((cx + math.cos(rad)*dist, cy + math.sin(rad)*dist))

    def update(self):
        self.player.update()
        self.selected_id = None
        for loc in self.locations:
            if self.player.rect.colliderect(loc[0]):
                self.selected_id = loc[1]
                return True
        return False

    def draw(self):
        screen.fill(OCEAN_BLUE)
        pygame.draw.polygon(screen, SAND_COLOR, self.island_pts)
        grass_pts = [(p[0], p[1]-5) for p in self.island_pts]
        pygame.draw.polygon(screen, GRASS_COLOR, grass_pts)
        
        p_ice, p_cave, p_merch, p_lava = self.locations[0][0].center, self.locations[1][0].center, self.locations[3][0].center, self.locations[2][0].center
        pygame.draw.line(screen, PATH_COLOR, p_ice, p_cave, 12)
        pygame.draw.line(screen, PATH_COLOR, p_cave, p_lava, 12)
        pygame.draw.line(screen, PATH_COLOR, p_merch, p_ice, 8)
        
        for i, loc in enumerate(self.locations): 
            screen.blit(self.location_images[i], loc[0])
        self.player.draw()
        
        if self.selected_id is not None:
            name = next(loc[2] for loc in self.locations if loc[1] == self.selected_id)
            verb = "Shop" if self.selected_id == 88 else "Enter"
            prompt = font.render(f"Press E to {verb} {name}", True, (255, 255, 255))
            tr = prompt.get_rect(center=(WIDTH//2, HEIGHT - 80))
            pygame.draw.rect(screen, (0,0,0, 180), tr.inflate(20, 10))
            pygame.draw.rect(screen, (255, 215, 0), tr.inflate(20, 10), 2)
            screen.blit(prompt, tr)
        screen.blit(vignette, (0,0))

# ================= SIDE-SCROLLING CLASSES =================
class Bullet: 
    def __init__(self, x, y, dx, dy, color, damage, size=8, gravity=0):
        self.rect = pygame.Rect(x, y, size, size)
        self.dx, self.dy, self.color, self.damage = dx, dy, color, damage
        self.gravity = gravity

    def update(self):
        self.dy += self.gravity
        self.rect.x += self.dx
        self.rect.y += self.dy

class Enemy:
    def __init__(self, x, theme):
        self.rect = pygame.Rect(x, 410, 40, 40)
        self.vy, self.theme = -10, theme
        self.state, self.timer, self.chase_speed, self.chase_dir = "normal", 0, 6, 0
        self.health = 15
        
        # --- ASSET LOADING ---
        if theme == "arctic":
            img_name = "Slime.png"
        elif theme == "lava":
            img_name = "FrogMonster.png"
            self.health = 40
        else:
            img_name = "Rock.png"
            
        self.image = load_img(img_name, (40, 40))

    def update(self, player, gravity):
        self.timer += 1
        if self.state == "normal":
            self.vy += gravity
            self.rect.y += self.vy
            if self.rect.bottom >= 440:
                self.rect.bottom, self.vy = 440, -12 if self.theme == "arctic" else -8
            if self.timer > 35:
                self.state, self.timer = "chase", 0
                self.chase_dir = 1 if player.rect.centerx > self.rect.centerx else -1
        elif self.state == "chase":
            self.rect.x += self.chase_dir * self.chase_speed
            self.vy += gravity
            self.rect.y += self.vy
            if self.rect.bottom >= 440: self.rect.bottom, self.vy = 440, 0
            if self.timer > 60: self.state, self.timer = "normal", 0
        
        if self.rect.colliderect(player.rect) and not player.is_invincible:
            player.take_damage(10 if self.theme != "lava" else 20)
        
        if player.laser_active:
            if self.rect.clipline(player.rect.center, player.laser_end):
                self.health -= (0.5 * laser_damage_mult) if not god_mode else 5

    def draw(self, screen, offset):
        screen.blit(self.image, self.rect.move(offset))
        pygame.draw.rect(screen, (0,0,0), (self.rect.x+offset[0], self.rect.y+offset[1]-10, 40, 5))
        pygame.draw.rect(screen, (0,255,0), (self.rect.x+offset[0], self.rect.y+offset[1]-10, (max(0, self.health)/15)*40, 5))

class Player:
    def __init__(self):
        self.wizard_run = [load_img(f"Wizard-{i}.png", (32, 42)) for i in range(4)]
        self.wizard_idle = [self.wizard_run[0], self.wizard_run[1]]
        self.wizard_jump = load_img("Wizardjumping.png", (32, 42))
        self.rect = pygame.Rect(100, 300, 32, 42)
        self.vx, self.vy, self.speed, self.jump_power = 0, 0, 5, 14
        self.on_ground, self.facing, self.anim_timer, self.frame = False, 1, 0, 0
        self.max_health = 150
        self.health, self.is_invincible, self.last_hit_time = self.max_health, False, 0
        self.laser_active = False
        self.laser_end = (0,0)

    def reset(self):
        self.health, self.is_invincible = self.max_health, False
        self.rect.x, self.rect.y = 100, 300

    def take_damage(self, amt):
        global hit_flash, screen_shake
        if not self.is_invincible:
            self.health -= (0 if god_mode else amt)
            self.is_invincible, self.last_hit_time = True, pygame.time.get_ticks()
            hit_flash, screen_shake = 5, 12

    def update(self, platforms, hazards, gravity, current_time):
        keys = pygame.key.get_pressed()
        m_buttons = pygame.mouse.get_pressed()
        self.vx = 0
        if keys[pygame.K_a]: self.vx, self.facing = -self.speed, -1
        if keys[pygame.K_d]: self.vx, self.facing = self.speed, 1
        if keys[pygame.K_SPACE] and self.on_ground: self.vy, self.on_ground = -self.jump_power, False
        if m_buttons[0]:
            self.laser_active = True
            self.laser_end = pygame.mouse.get_pos()
        else:
            self.laser_active = False
        self.vy += gravity
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.y > HEIGHT: self.take_damage(20); self.rect.x, self.rect.y = 100, 100
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0: self.rect.bottom, self.vy, self.on_ground = p.top, 0, True
                elif self.vy < 0: self.rect.top, self.vy = p.bottom, 0
        for h in hazards:
            if self.rect.colliderect(h) and not self.is_invincible: self.take_damage(15); self.vy = -8
        if self.is_invincible and current_time - self.last_hit_time > 1000: self.is_invincible = False
        self.anim_timer += 1
        if self.anim_timer > 8: self.anim_timer, self.frame = 0, (self.frame + 1) % 4

    def draw(self, offset):
        if self.laser_active:
            start = (self.rect.centerx + offset[0], self.rect.centery + offset[1])
            end = (self.laser_end[0] , self.laser_end[1])
            pygame.draw.line(screen, LASER_COLOR, start, end, 6)
            pygame.draw.line(screen, (255, 255, 255), start, end, 2)
        if self.is_invincible and (pygame.time.get_ticks() // 100) % 2 == 0: return
        img = self.wizard_jump if not self.on_ground else (self.wizard_run[self.frame] if self.vx else self.wizard_idle[self.frame%2])
        if self.facing == -1: img = pygame.transform.flip(img, True, False)
        if hit_flash > 0: img = img.copy(); img.fill(FLASH, special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(img, (self.rect.x+offset[0], self.rect.y+offset[1]))

class Boss:
    def __init__(self, theme):
        self.rect = pygame.Rect(520, 200, 120, 120)
        self.theme = theme
        
        # --- HARDER HP & ASSETS ---
        if theme == "arctic": 
            self.max_health = 250
            img_name = "eyeboss-1.png"
        elif theme == "lava": 
            self.max_health = 1200 # Toughest boss
            img_name = "LavaBoss.png"
        else: 
            self.max_health = 750
            img_name = "rockboss.png"
            
        self.health, self.bullets = self.max_health, []
        self.img = load_img(img_name, (120, 120))
        self.state, self.state_timer = "shoot", 0

    def update(self, player):
        self.state_timer += 1
        is_enraged = self.health < (self.max_health / 2)
        
        # CONTACT DAMAGE (Punish closeness)
        if self.rect.colliderect(player.rect) and not player.is_invincible:
            player.take_damage(20 if self.theme == "lava" else 15)

        if player.laser_active:
            if self.rect.clipline(player.rect.center, player.laser_end):
                self.health -= (0.8 * laser_damage_mult) if not god_mode else 10
                global boss_flash
                if self.state_timer % 5 == 0: boss_flash = 2

        if self.state == "shoot":
            # Floating movement
            self.rect.x += int(math.sin(self.state_timer*0.06)*6)
            self.rect.y += int(math.cos(self.state_timer*0.05)*4)
            
            # Fire rates get faster when enraged
            base_rate = 25 if self.theme == "arctic" else 15
            fire_rate = base_rate if not is_enraged else (base_rate // 2)
            
            if self.state_timer % fire_rate == 0: 
                if self.theme == "lava":
                    # VOLCANO ATTACK: Fireballs that rain down
                    for _ in range(2 if not is_enraged else 4):
                        vx = random.uniform(-7, 7)
                        vy = random.uniform(-15, -9)
                        self.bullets.append(Bullet(self.rect.centerx, self.rect.centery, vx, vy, LAVA_GLOW, 15, 16, 0.4))
                else:
                    # Aimed shots
                    angle_to_player = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
                    angles = [-0.3, 0, 0.3]
                    if is_enraged: angles = [-0.6, -0.3, 0, 0.3, 0.6]
                    for a in angles:
                        bx, by = math.cos(angle_to_player + a), math.sin(angle_to_player + a)
                        self.bullets.append(Bullet(self.rect.centerx, self.rect.centery, bx*8.5, by*8.5, BOSS_COLOR, 10, 12))
            
            if self.state_timer > 120: self.state, self.state_timer = "chase", 0

        elif self.state == "chase":
            # Aggressive following
            speed = 11 if not is_enraged else 16
            dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery) or 1
            self.rect.x += int(((player.rect.centerx - self.rect.centerx) / dist) * speed) 
            self.rect.y += int(((player.rect.centery - self.rect.centery) / dist) * speed)
            
            if self.state_timer > 90: self.state, self.state_timer = "shoot", 0

        for b in self.bullets[:]:
            b.update()
            if b.rect.y > HEIGHT + 100 or b.rect.x < -100 or b.rect.x > WIDTH + 100: self.bullets.remove(b)

class PlatformingManager:
    def __init__(self, player_ref):
        self.player = player_ref
        self.active, self.complete = False, False
        self.level_data = None
        self.slimes = {}
        self.boss = None

    def load_level(self, index):
        global current_room, current_level_idx
        current_level_idx = index
        current_room = 0
        self.level_data = all_level_data[current_level_idx]
        theme = self.level_data["theme"]
        self.slimes = {r_id: [Enemy(x, theme) for x in x_list] for r_id, x_list in self.level_data.get("slimes", {}).items()}
        self.boss = Boss(theme)
        self.player.reset()
        self.active, self.complete = True, False

    def update(self, current_time):
        global current_room, player_score
        rooms = self.level_data["rooms"]
        grav = self.level_data["gravity_mod"]
        if self.level_data["theme"] not in ["arctic", "lava"]: grav += 0.2
            
        self.player.update(rooms[current_room], self.level_data.get("hazards", {}).get(current_room, []), grav, current_time)
        
        if self.player.rect.x > WIDTH:
            if current_room < len(rooms) - 1: current_room += 1; self.player.rect.x = 10
            else: self.active = False 
        elif self.player.rect.x < 0:
            if current_room > 0: current_room -= 1; self.player.rect.x = WIDTH - 40
            else: self.active = False 
        if current_room in self.slimes:
            for s in self.slimes[current_room][:]:
                s.update(self.player, grav)
                if s.health <= 0: self.slimes[current_room].remove(s); player_score += 1 
        if self.boss and current_room == len(rooms) - 1:
            if self.boss.health > 0:
                self.boss.update(self.player)
                for b in self.boss.bullets[:]:
                    if b.rect.colliderect(self.player.rect) and not self.player.is_invincible:
                        self.player.take_damage(b.damage); self.boss.bullets.remove(b)
            else: 
                if not self.complete: player_score += 15 
                self.complete, self.active = True, False
        if self.player.health <= 0: self.active = False

    def draw(self, offset):
        screen.fill(self.level_data["sky_color"])
        for p in self.level_data["rooms"][current_room]: pygame.draw.rect(screen, self.level_data["ice_color"], p.move(offset))
        
        hazards = self.level_data.get("hazards", {}).get(current_room, [])
        for h in hazards: pygame.draw.rect(screen, (255, 50, 0), h.move(offset))

        if current_room in self.slimes:
            for s in self.slimes[current_room]: s.draw(screen, offset)
        self.player.draw(offset)
        if self.boss and current_room == len(self.level_data["rooms"]) - 1 and self.boss.health > 0:
            img = self.boss.img.copy()
            if boss_flash > 0: img.fill(FLASH, special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(img, self.boss.rect.move(offset))
            for b in self.boss.bullets: pygame.draw.rect(screen, b.color, b.rect.move(offset))
            pygame.draw.rect(screen, (50, 50, 50), (200, 20, 400, 20))
            pygame.draw.rect(screen, (255, 0, 0), (200, 20, (max(0, self.boss.health)/self.boss.max_health)*400, 20)) 
        screen.blit(vignette, (0,0))

# ================= SHOP LOGIC =================
class Shop:
    def __init__(self):
        self.is_open = False
        self.buttons = [
            {"rect": pygame.Rect(250, 180, 300, 50), "cost": 10, "type": "health", "label": "+20 Max HP"},
            {"rect": pygame.Rect(250, 250, 300, 50), "cost": 20, "type": "damage", "label": "+20% Laser Damage"}
        ]

    def update(self, player):
        global player_score, laser_damage_mult
        m_pos = pygame.mouse.get_pos()
        m_click = pygame.mouse.get_pressed()
        
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.is_open = False
            pygame.time.delay(150)
            
        if m_click[0]:
            for btn in self.buttons:
                if btn["rect"].collidepoint(m_pos) and player_score >= btn["cost"]:
                    player_score -= btn["cost"]
                    if btn["type"] == "health":
                        player.max_health += 20
                        player.health = player.max_health
                    elif btn["type"] == "damage":
                        laser_damage_mult += 0.2
                    pygame.time.delay(250)

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 210))
        screen.blit(overlay, (0,0))
        title = score_font.render("--- MERCHANT SHOP ---", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        for btn in self.buttons:
            color = (60, 160, 60) if player_score >= btn["cost"] else (160, 60, 60)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), btn["rect"], 2, border_radius=5)
            txt = font.render(f"{btn['label']} ({btn['cost']} pts)", True, (255, 255, 255))
            screen.blit(txt, (btn["rect"].centerx - txt.get_width()//2, btn["rect"].centery - txt.get_height()//2))
        
        instr = font.render("Press ESC to Close", True, (200, 200, 200))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 350))

# ================= MAIN LOOP =================
player_shared = Player()
overworld = WorldMap()
platformer = PlatformingManager(player_shared)
merchant_shop = Shop()
game_state, game_over, victory = "OVERWORLD", False, False

running = True
while running:
    current_time = pygame.time.get_ticks()
    clock.tick(60)
    offset = camera_offset()
    if screen_shake > 0: screen_shake -= 1
    if hit_flash > 0: hit_flash -= 1
    if boss_flash > 0: boss_flash -= 1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_5: god_mode = not god_mode
            if game_state == "OVERWORLD" and not (game_over or victory) and not merchant_shop.is_open:
                if event.key == pygame.K_e and overworld.selected_id is not None:
                    if overworld.selected_id == 88:
                        merchant_shop.is_open = True
                    else: 
                        platformer.load_level(overworld.selected_id)
                        game_state = "PLATFORMING"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over or victory: running = False
    
    if game_state == "OVERWORLD":
        overworld.update()
        overworld.draw()
        if merchant_shop.is_open:
            merchant_shop.update(player_shared)
            merchant_shop.draw()
    else:
        platformer.update(current_time)
        platformer.draw(offset)
        if not platformer.active:
            if player_shared.health <= 0: game_over = True
            elif platformer.complete and current_level_idx == len(all_level_data) - 1: victory = True
            game_state = "OVERWORLD"
    
    if game_state == "PLATFORMING":
        bar_width = (player_shared.health / player_shared.max_health) * 200
        pygame.draw.rect(screen, (50,50,50), (20, HEIGHT-30, 200, 10))
        pygame.draw.rect(screen, HEALTH_COLOR, (20, HEIGHT-30, max(0, bar_width), 10))

    score_txt = score_font.render(f"POINTS: {player_score}", True, (255, 215, 0))
    screen.blit(score_txt, (WIDTH - score_txt.get_width() - 20, HEIGHT - 40))
    
    if game_over:
        txt = font.render("GAME OVER - Click to Exit", True, (255,255,255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
    if victory:
        txt = font.render("VICTORY! Isle Completed - Click to Exit", True, (255, 215, 0))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        
    pygame.display.flip()

pygame.quit()
sys.exit()
