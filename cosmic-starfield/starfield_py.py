import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Starfield")
clock = pygame.time.Clock()

# Colors
DEEP_SPACE = (5, 8, 20)  # Very dark blue-black
WHITE = (255, 255, 255)
STAR_YELLOW = (255, 250, 200)
CONSTELLATION_LINE = (100, 120, 180, 80)  # Soft blue-ish with alpha

# Star class for appearing/disappearing stars
class TwinklingStar:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2.5)
        self.brightness = 0
        self.target_brightness = random.randint(150, 255)
        self.fade_speed = random.uniform(1, 3)
        self.state = 'appearing'  # appearing, visible, disappearing
        self.visible_time = random.uniform(2000, 6000)  # How long to stay visible
        self.appear_start = pygame.time.get_ticks()
        # Vary star colors slightly
        self.color_offset = random.randint(-20, 20)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.state == 'appearing':
            self.brightness += self.fade_speed
            if self.brightness >= self.target_brightness:
                self.brightness = self.target_brightness
                self.state = 'visible'
                self.visible_start = current_time
        
        elif self.state == 'visible':
            # Small twinkle while visible
            twinkle = random.uniform(-10, 10)
            self.brightness = max(0, min(255, self.target_brightness + twinkle))
            if current_time - self.visible_start >= self.visible_time:
                self.state = 'disappearing'
        
        elif self.state == 'disappearing':
            self.brightness -= self.fade_speed
            if self.brightness <= 0:
                self.brightness = 0
                # Respawn at new location
                self.x = random.randint(0, WIDTH)
                self.y = random.randint(0, HEIGHT)
                self.target_brightness = random.randint(150, 255)
                self.visible_time = random.uniform(2000, 6000)
                self.state = 'appearing'
    
    def draw(self, surface):
        if self.brightness <= 0:
            return
        b = int(max(0, min(255, self.brightness)))
        r = max(0, min(255, b + self.color_offset))
        g = max(0, min(255, b + self.color_offset - 5))
        b_color = max(0, min(255, b + self.color_offset - 55))
        color = (r, g, b_color)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

# Constellation class
class Constellation:
    def __init__(self):
        # Random center position
        center_x = random.randint(100, WIDTH - 100)
        center_y = random.randint(100, HEIGHT - 100)
        
        # Create 4-7 stars in constellation
        num_stars = random.randint(4, 7)
        self.stars = []
        
        for i in range(num_stars):
            angle = (i / num_stars) * 2 * math.pi + random.uniform(-0.5, 0.5)
            distance = random.randint(30, 80)
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            size = random.uniform(1.5, 3)
            self.stars.append({'x': x, 'y': y, 'size': size})
        
        # Create connections (lines between stars)
        self.connections = []
        for i in range(len(self.stars) - 1):
            if random.random() < 0.7:  # 70% chance of connection
                self.connections.append((i, i + 1))
        # Sometimes connect back to start
        if random.random() < 0.3 and len(self.stars) > 3:
            self.connections.append((len(self.stars) - 1, 0))
        
        # Shining properties
        self.alpha = 0
        self.shine_duration = random.uniform(6000, 12000)  # 6-12 seconds
        self.fade_in_duration = 1500
        self.fade_out_duration = 1500
        self.start_time = pygame.time.get_ticks()
        self.state = 'fade_in'  # fade_in, shine, fade_out, hidden
    
    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        
        if self.state == 'fade_in':
            self.alpha = min(255, (elapsed / self.fade_in_duration) * 255)
            if elapsed >= self.fade_in_duration:
                self.state = 'shine'
                self.shine_start = pygame.time.get_ticks()
        
        elif self.state == 'shine':
            shine_elapsed = pygame.time.get_ticks() - self.shine_start
            if shine_elapsed >= self.shine_duration:
                self.state = 'fade_out'
                self.fade_start = pygame.time.get_ticks()
        
        elif self.state == 'fade_out':
            fade_elapsed = pygame.time.get_ticks() - self.fade_start
            self.alpha = max(0, 255 - (fade_elapsed / self.fade_out_duration) * 255)
            if fade_elapsed >= self.fade_out_duration:
                self.state = 'hidden'
    
    def is_hidden(self):
        return self.state == 'hidden'
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
        
        # Draw connecting lines
        for conn in self.connections:
            start_star = self.stars[conn[0]]
            end_star = self.stars[conn[1]]
            
            # Create surface for alpha blending
            line_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            color = (100, 120, 180, int(self.alpha * 0.4))
            pygame.draw.line(line_surface, color, 
                           (int(start_star['x']), int(start_star['y'])),
                           (int(end_star['x']), int(end_star['y'])), 1)
            surface.blit(line_surface, (0, 0))
        
        # Draw stars
        for star in self.stars:
            star_surface = pygame.Surface((int(star['size'] * 2 + 4), 
                                          int(star['size'] * 2 + 4)), pygame.SRCALPHA)
            color = (255, 250, 220, int(self.alpha))
            pygame.draw.circle(star_surface, color, 
                             (int(star['size'] + 2), int(star['size'] + 2)), 
                             int(star['size']))
            # Add glow
            glow_color = (200, 210, 255, int(self.alpha * 0.3))
            pygame.draw.circle(star_surface, glow_color,
                             (int(star['size'] + 2), int(star['size'] + 2)),
                             int(star['size'] * 2))
            surface.blit(star_surface, 
                        (int(star['x'] - star['size'] - 2), 
                         int(star['y'] - star['size'] - 2)))

# Shooting star class
class ShootingStar:
    def __init__(self):
        if random.random() < 0.5:
            self.x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
            self.y = -10
        else:
            self.x = -10
            self.y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
        
        angle = random.uniform(0.4, 1.1)
        speed = random.uniform(10, 18)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.alpha = 255
        self.trail_length = 20
        self.trail = []
    
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 2
    
    def is_alive(self):
        return self.alpha > 0 and self.x < WIDTH + 100 and self.y < HEIGHT + 100
    
    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            trail_alpha = int((i / len(self.trail)) * self.alpha)
            trail_size = int(2 + 2 * (i / len(self.trail)))
            if trail_size < 1:
                trail_size = 1
            
            s = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, trail_alpha), 
                             (trail_size, trail_size), trail_size)
            surface.blit(s, (int(tx) - trail_size, int(ty) - trail_size))
        
        head_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(head_surface, (255, 255, 255, int(self.alpha)), (5, 5), 3)
        pygame.draw.circle(head_surface, (200, 220, 255, int(self.alpha * 0.5)), (5, 5), 5)
        surface.blit(head_surface, (int(self.x) - 5, int(self.y) - 5))

# Create background stars with varied density
twinkling_stars = [TwinklingStar() for _ in range(500)]

# Constellations
constellations = []
last_constellation = pygame.time.get_ticks()

# Shooting stars
shooting_stars = []
last_shooting_star = pygame.time.get_ticks()

# Main loop
running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    current_time = pygame.time.get_ticks()
    
    # Spawn constellations
    if current_time - last_constellation > random.randint(8000, 15000):
        if len([c for c in constellations if not c.is_hidden()]) < 3:
            constellations.append(Constellation())
            last_constellation = current_time
    
    # Remove hidden constellations
    constellations = [c for c in constellations if not c.is_hidden() or 
                     (pygame.time.get_ticks() - c.start_time) < 20000]
    
    # Spawn shooting stars
    if current_time - last_shooting_star > random.randint(2000, 5000):
        if len(shooting_stars) < 3:
            shooting_stars.append(ShootingStar())
            last_shooting_star = current_time
    
    # Update
    for star in twinkling_stars:
        star.update()
    
    for constellation in constellations:
        constellation.update()
    
    for shooting_star in shooting_stars[:]:
        shooting_star.update()
        if not shooting_star.is_alive():
            shooting_stars.remove(shooting_star)
    
    # Draw
    screen.fill(DEEP_SPACE)
    
    # Draw all twinkling stars
    for star in twinkling_stars:
        star.draw(screen)
    
    # Draw constellations
    for constellation in constellations:
        constellation.draw(screen)
    
    # Draw shooting stars
    for shooting_star in shooting_stars:
        shooting_star.draw(screen)
    
    pygame.display.flip()

pygame.quit()