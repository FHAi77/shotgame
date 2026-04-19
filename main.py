import pygame
import random
import sys
import math
import json
import os
from enum import Enum
from datetime import datetime

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
DARK_BLUE = (10, 10, 40)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("太空防卫战")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 36)
small_font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("arial", 60)

def get_chinese_font(size):
    available_fonts = pygame.font.get_fonts()
    
    font_candidates = [
        "arialunicode",
        "stheiti",
        "hiraginosansgb",
        "songti",
        "heiti",
        "pingfang",
        "microsoftyahei",
        "simhei",
        "simsun",
        "wenquanyi",
        "noto sans cjk",
        "source han sans",
        "applegothic"
    ]
    
    for candidate in font_candidates:
        for font_name in available_fonts:
            if candidate in font_name.lower():
                try:
                    f = pygame.font.SysFont(font_name, size)
                    test_surface = f.render("测试中文字体", True, WHITE)
                    if test_surface.get_width() > 50:
                        return f
                except:
                    continue
    
    for font_name in available_fonts:
        try:
            f = pygame.font.SysFont(font_name, size)
            test_surface = f.render("测试中文字体", True, WHITE)
            if test_surface.get_width() > 50:
                return f
        except:
            continue
    
    return pygame.font.SysFont(None, size)

chinese_font = get_chinese_font(32)
chinese_small_font = get_chinese_font(20)

SCORES_FILE = "highscores.json"
MAX_HIGH_SCORES = 10


def load_high_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_high_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def add_high_score(score):
    scores = load_high_scores()
    entry = {
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    scores.append(entry)
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:MAX_HIGH_SCORES]
    save_high_scores(scores)
    return scores


def get_rank_color(rank):
    if rank == 0:
        return GOLD
    elif rank == 1:
        return SILVER
    elif rank == 2:
        return BRONZE
    return WHITE


def create_player_sprite():
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    
    body_points = [
        (24, 0),
        (28, 20),
        (40, 35),
        (32, 32),
        (28, 40),
        (24, 35),
        (20, 40),
        (16, 32),
        (8, 35),
        (20, 20),
    ]
    pygame.draw.polygon(surface, (100, 150, 255), body_points)
    pygame.draw.polygon(surface, (200, 220, 255), body_points, 2)
    
    cockpit_points = [
        (24, 8),
        (26, 18),
        (24, 22),
        (22, 18),
    ]
    pygame.draw.polygon(surface, CYAN, cockpit_points)
    
    pygame.draw.ellipse(surface, ORANGE, (18, 38, 5, 8))
    pygame.draw.ellipse(surface, ORANGE, (25, 38, 5, 8))
    
    return surface


def create_enemy_basic_sprite():
    surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    
    body_points = [
        (20, 5),
        (30, 15),
        (35, 25),
        (28, 30),
        (20, 38),
        (12, 30),
        (5, 25),
        (10, 15),
    ]
    pygame.draw.polygon(surface, (200, 50, 50), body_points)
    pygame.draw.polygon(surface, (255, 100, 100), body_points, 2)
    
    pygame.draw.circle(surface, (255, 0, 0), (20, 18), 6)
    pygame.draw.circle(surface, (150, 0, 0), (20, 18), 3)
    
    return surface


def create_enemy_elite_sprite():
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    
    body_points = [
        (24, 2),
        (36, 12),
        (44, 24),
        (36, 36),
        (24, 46),
        (12, 36),
        (4, 24),
        (12, 12),
    ]
    pygame.draw.polygon(surface, (150, 0, 150), body_points)
    pygame.draw.polygon(surface, (255, 100, 255), body_points, 3)
    
    pygame.draw.circle(surface, (255, 0, 255), (24, 15), 8)
    pygame.draw.circle(surface, (150, 0, 150), (24, 15), 4)
    pygame.draw.circle(surface, (255, 0, 255), (16, 20), 4)
    pygame.draw.circle(surface, (255, 0, 255), (32, 20), 4)
    
    return surface


def create_bullet_sprite():
    surface = pygame.Surface((8, 20), pygame.SRCALPHA)
    
    pygame.draw.ellipse(surface, (255, 255, 200), (2, 0, 4, 20))
    pygame.draw.ellipse(surface, YELLOW, (3, 2, 2, 16))
    
    return surface


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._create_sounds()
    
    def _create_sounds(self):
        self.sounds['shoot'] = self._generate_tone(880, 0.1, volume=0.3)
        self.sounds['explosion'] = self._generate_explosion(volume=0.4)
        self.sounds['hit'] = self._generate_tone(440, 0.05, volume=0.2)
        self.sounds['gameover'] = self._generate_descending_tone(volume=0.5)
    
    def _generate_tone(self, frequency, duration, volume=0.5):
        sample_rate = 44100
        samples = int(sample_rate * duration)
        
        buf = bytearray()
        for i in range(samples):
            t = i / sample_rate
            envelope = 1.0 - (i / samples)
            value = int(127 + 127 * math.sin(2 * math.pi * frequency * t) * envelope * volume)
            buf.append(value)
            buf.append(value)
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound
    
    def _generate_explosion(self, volume=0.5):
        sample_rate = 44100
        duration = 0.3
        samples = int(sample_rate * duration)
        
        buf = bytearray()
        for i in range(samples):
            envelope = 1.0 - (i / samples) ** 0.5
            value = int(127 + 127 * (random.random() * 2 - 1) * envelope * volume)
            buf.append(value)
            buf.append(value)
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound
    
    def _generate_descending_tone(self, volume=0.5):
        sample_rate = 44100
        duration = 1.0
        samples = int(sample_rate * duration)
        
        buf = bytearray()
        for i in range(samples):
            t = i / sample_rate
            freq = 440 * (1 - t * 0.8)
            envelope = 1.0 - (i / samples)
            value = int(127 + 127 * math.sin(2 * math.pi * freq * t) * envelope * volume)
            buf.append(value)
            buf.append(value)
        
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(volume)
        return sound
    
    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()


class Particle:
    def __init__(self, x, y, color, speed, life):
        self.x = x
        self.y = y
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.color = color
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)
        self.active = True
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, int(self.size * 0.95))
        if self.life <= 0:
            self.active = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class Star:
    def __init__(self):
        self.reset()
        self.y = random.randint(0, SCREEN_HEIGHT)
    
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -5
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 3)
        self.brightness = random.randint(100, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.reset()
    
    def draw(self, surface):
        color = (self.brightness, self.brightness, 255)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    HIGH_SCORES = 5


class Bullet:
    def __init__(self, x, y, sprite):
        self.sprite = sprite
        self.rect = self.sprite.get_rect(center=(x, y))
        self.speed = 10
        self.active = True

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.active = False

    def draw(self, surface):
        surface.blit(self.sprite, self.rect)


class Player:
    def __init__(self, sprite, bullet_sprite):
        self.sprite = sprite
        self.bullet_sprite = bullet_sprite
        self.rect = self.sprite.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.speed = 6
        self.health = 1
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_delay = 12
        self.engine_particles = []

    def move(self, dx, dy):
        if dx != 0 and dy != 0:
            factor = self.speed / 1.414
            self.rect.x += dx * factor
            self.rect.y += dy * factor
        else:
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_sprite)
            self.bullets.append(bullet)
            self.shoot_cooldown = self.shoot_delay
            return True
        return False

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # BUG: 引擎粒子在玩家死亡后仍持续生成
        if self.health > 0 and random.random() < 0.7:
            self.engine_particles.append(Particle(
                self.rect.centerx + random.randint(-5, 5),
                self.rect.bottom - 5,
                ORANGE,
                2,
                random.randint(10, 20)
            ))
        
        for p in self.engine_particles[:]:
            p.update()
            if not p.active:
                self.engine_particles.remove(p)

    def draw(self, surface):
        for p in self.engine_particles:
            p.draw(surface)
        
        # BUG: 玩家死亡后仍显示飞船图像
        surface.blit(self.sprite, self.rect)

        for bullet in self.bullets:
            bullet.draw(surface)


class Enemy:
    def __init__(self, x, y, enemy_type, sprite):
        self.enemy_type = enemy_type
        self.sprite = sprite
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.active = True
        self.hit_flash = 0

        if enemy_type == "basic":
            self.health = 1
            self.speed = 2.5
            self.score = 10
        else:
            self.health = 2
            self.speed = 1.8
            self.score = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.active = False
        
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def take_damage(self):
        self.health -= 1
        self.hit_flash = 5
        if self.health <= 0:
            self.active = False
            return True
        return False

    def draw(self, surface):
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            flash_sprite = self.sprite.copy()
            flash_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(flash_sprite, self.rect)
        else:
            surface.blit(self.sprite, self.rect)


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.enemies = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 50
        self.stars = [Star() for _ in range(100)]
        self.particles = []
        self.sound_manager = SoundManager()
        self.score_saved = False
        self.high_scores = load_high_scores()
        
        self.player_sprite = create_player_sprite()
        self.enemy_basic_sprite = create_enemy_basic_sprite()
        self.enemy_elite_sprite = create_enemy_elite_sprite()
        self.bullet_sprite = create_bullet_sprite()

    def reset(self):
        self.player = Player(self.player_sprite, self.bullet_sprite)
        self.enemies = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.particles = []
        self.score_saved = False

    def spawn_enemy(self):
        sprite = self.enemy_basic_sprite
        enemy_type = "basic"
        
        if random.random() < 0.25:
            sprite = self.enemy_elite_sprite
            enemy_type = "elite"
        
        x = random.randint(0, SCREEN_WIDTH - sprite.get_width())
        enemy = Enemy(x, -50, enemy_type, sprite)
        self.enemies.append(enemy)

    def create_explosion(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(
                x, y, color,
                random.uniform(3, 8),
                random.randint(20, 40)
            ))

    def check_collisions(self):
        # BUG: 碰撞检测在玩家死亡后仍继续执行
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                self.create_explosion(self.player.rect.centerx, self.player.rect.centery, ORANGE, 30)
                self.create_explosion(enemy.rect.centerx, enemy.rect.centery, RED, 20)
                self.sound_manager.play('gameover')
                self.player.health = 0
                return

        # BUG: 子弹可以穿透多个敌机（移除了break）
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.active and enemy.active and bullet.rect.colliderect(enemy.rect):
                    bullet.active = False
                    self.sound_manager.play('hit')
                    if enemy.take_damage():
                        self.score += enemy.score
                        color = RED if enemy.enemy_type == "basic" else PURPLE
                        self.create_explosion(enemy.rect.centerx, enemy.rect.centery, color)
                        self.sound_manager.play('explosion')
                    # 移除了break，子弹可以继续击中其他敌机

    def update(self):
        if self.state != GameState.PLAYING:
            return

        self.player.update()

        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            # BUG: 难度增加过快，每帧都减少生成间隔
            self.enemy_spawn_delay -= 0.1

        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.active:
                self.enemies.remove(enemy)

        self.check_collisions()

        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
            if not self.score_saved:
                self.high_scores = add_high_score(self.score)
                self.score_saved = True

        for p in self.particles[:]:
            p.update()
            if not p.active:
                self.particles.remove(p)

    def draw_background(self, surface):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(5 + ratio * 15)
            g = int(5 + ratio * 10)
            b = int(20 + ratio * 30)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        for star in self.stars:
            if self.state == GameState.PLAYING:
                star.update()
            star.draw(surface)

    def draw_ui(self, surface):
        if self.state == GameState.PLAYING:
            score_text = chinese_small_font.render(f"得分: {self.score}", True, WHITE)
            surface.blit(score_text, (10, 10))
            
            diff_text = chinese_small_font.render(f"等级: {int(50 - self.enemy_spawn_delay) // 5 + 1}", True, YELLOW)
            surface.blit(diff_text, (10, 40))

        elif self.state == GameState.MENU:
            title = title_font.render("SPACE DEFENDER", True, CYAN)
            subtitle = chinese_small_font.render("保卫银河系，击退外星入侵！", True, GRAY)
            start_text = chinese_small_font.render("按 [空格键] 开始游戏", True, WHITE)
            scores_text = chinese_small_font.render("按 [H] 查看排行榜", True, YELLOW)
            controls_text = chinese_small_font.render("方向键/WASD: 移动  |  空格: 射击  |  P: 暂停", True, GRAY)
            quit_text = chinese_small_font.render("按 [ESC] 退出游戏", True, GRAY)

            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))
            surface.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 310))
            surface.blit(scores_text, (SCREEN_WIDTH // 2 - scores_text.get_width() // 2, 350))
            surface.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 410))
            surface.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 460))

        elif self.state == GameState.PAUSED:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))
            
            pause_text = title_font.render("PAUSED", True, YELLOW)
            continue_text = chinese_small_font.render("按 [P] 继续游戏", True, WHITE)

            surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
            surface.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 340))

        elif self.state == GameState.GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))
            
            over_text = title_font.render("GAME OVER", True, RED)
            score_text = chinese_small_font.render(f"最终得分: {self.score}", True, WHITE)
            restart_text = chinese_small_font.render("按 [R] 重新开始", True, GREEN)
            menu_text = chinese_small_font.render("按 [M] 返回主菜单", True, CYAN)
            scores_text = chinese_small_font.render("按 [H] 查看排行榜", True, YELLOW)

            surface.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, 180))
            surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 320))
            surface.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 360))
            surface.blit(scores_text, (SCREEN_WIDTH // 2 - scores_text.get_width() // 2, 400))

        elif self.state == GameState.HIGH_SCORES:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))
            
            title = title_font.render("HIGH SCORES", True, GOLD)
            surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 60))
            
            if not self.high_scores:
                no_score_text = chinese_small_font.render("暂无记录", True, GRAY)
                surface.blit(no_score_text, (SCREEN_WIDTH // 2 - no_score_text.get_width() // 2, 200))
            else:
                header_rank = chinese_small_font.render("排名", True, GRAY)
                header_score = chinese_small_font.render("得分", True, GRAY)
                header_date = chinese_small_font.render("日期", True, GRAY)
                
                surface.blit(header_rank, (200, 120))
                surface.blit(header_score, (350, 120))
                surface.blit(header_date, (480, 120))
                
                pygame.draw.line(surface, GRAY, (180, 145), (620, 145), 1)
                
                for i, entry in enumerate(self.high_scores[:10]):
                    y_pos = 160 + i * 35
                    rank_color = get_rank_color(i)
                    
                    rank_text = font.render(f"#{i + 1}", True, rank_color)
                    score_text = font.render(str(entry["score"]), True, WHITE)
                    date_text = small_font.render(entry["date"], True, GRAY)
                    
                    surface.blit(rank_text, (200, y_pos))
                    surface.blit(score_text, (350, y_pos))
                    surface.blit(date_text, (480, y_pos + 5))
            
            back_text = chinese_small_font.render("按 [M] 返回主菜单", True, CYAN)
            surface.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 530))

    def draw(self, surface):
        self.draw_background(surface)

        if self.state == GameState.PLAYING or self.state == GameState.PAUSED:
            if self.player:
                self.player.draw(surface)
            for enemy in self.enemies:
                enemy.draw(surface)
            
            for p in self.particles:
                p.draw(surface)

        self.draw_ui(surface)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_h:
                        self.high_scores = load_high_scores()
                        self.state = GameState.HIGH_SCORES

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_p:
                        self.state = GameState.PAUSED

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_h:
                        self.high_scores = load_high_scores()
                        self.state = GameState.HIGH_SCORES

                elif self.state == GameState.HIGH_SCORES:
                    if event.key == pygame.K_m:
                        self.state = GameState.MENU

        if self.state == GameState.PLAYING and self.player:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            self.player.move(dx, dy)

            if keys[pygame.K_SPACE]:
                if self.player.shoot():
                    self.sound_manager.play('shoot')

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
