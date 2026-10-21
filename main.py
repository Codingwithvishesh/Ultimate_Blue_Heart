import pygame
import math
import random
import sys

# Pygame initialize
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 950, 950
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Slow-Reveal Cyberpunk Blue Heart Particle Engine")
clock = pygame.time.Clock()

# Heart Parametric Formula
def heart_formula(t, scale=17.5):
    x = 16 * (math.sin(t) ** 3)
    y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    return x * scale, y * scale

class Particle:
    def __init__(self, target_x, target_y, is_border=False, layer_dist=0.0):
        self.target_base_x = target_x
        self.target_base_y = target_y
        self.is_border = is_border
        self.layer_dist = layer_dist  # 0.0 (center) se 1.0 (outer border)

        # Particle reveal timing state (Center se outward wave me activate hoga)
        # Delay based on radial distance from core
        self.activation_threshold = self.layer_dist * 0.85 + random.uniform(0.0, 0.15)
        self.active = False
        self.progress = 0.0

        # Slow motion growth / flight speed
        self.speed = random.uniform(0.008, 0.018) if not is_border else random.uniform(0.012, 0.022)

        # Positions
        self.x = 0.0
        self.y = 0.0

        # Shimmer and Glow
        self.brightness = random.uniform(0.65, 1.0)
        self.size = random.uniform(1.2, 2.4) if not is_border else random.uniform(2.0, 3.2)
        self.jitter_seed = random.uniform(0, 500)

    def update(self, global_reveal_progress, pulse_scale, time_sec):
        # Activation check based on global reveal wave
        if not self.active:
            if global_reveal_progress >= self.activation_threshold:
                self.active = True

        if not self.active:
            return

        # Particle expansion with cubic ease-out for ultra smooth slow-motion
        if self.progress < 1.0:
            self.progress += self.speed
            # Cubic Ease Out: 1 - (1-t)^3
            ease = 1.0 - math.pow(1.0 - min(1.0, self.progress), 3)
        else:
            ease = 1.0

        # Dynamic target with pulsating heartbeat (heartbeat activates as it expands)
        effective_pulse = 1.0 + (pulse_scale - 1.0) * ease
        cur_target_x = self.target_base_x * effective_pulse
        cur_target_y = self.target_base_y * effective_pulse

        # Organic micro-shimmer / fluffy particle vibration
        jitter_amp = 1.6 if self.is_border else 0.8
        jitter_x = math.sin(time_sec * 6.0 + self.jitter_seed) * jitter_amp
        jitter_y = math.cos(time_sec * 6.0 + self.jitter_seed) * jitter_amp

        self.x = (cur_target_x * ease) + jitter_x
        self.y = (cur_target_y * ease) + jitter_y

    def draw(self, surface, center_x, center_y):
        if not self.active:
            return

        px = int(center_x + self.x)
        py = int(center_y + self.y)

        # Alpha & Color grading based on flight progress
        fade = min(1.0, self.progress * 1.5)

        if self.is_border:
            core_color = (int(210 * fade), int(250 * fade), int(255 * fade))
            glow_color = (0, int(220 * fade), int(255 * fade))
        else:
            b_val = int(255 * self.brightness * fade)
            g_val = int(150 * self.brightness * fade)
            core_color = (int(100 * fade), g_val, b_val)
            glow_color = (0, int(110 * fade), int(225 * fade))

        # Glowing outer halo and dense core
        if self.size > 2.0 and fade > 0.6:
            pygame.draw.circle(surface, glow_color, (px, py), int(self.size + 1.5))
        pygame.draw.circle(surface, core_color, (px, py), int(self.size))

def generate_heart_particles(num_particles=5000):
    particles = []

    # 1. Outer Border / Silhouette
    border_count = int(num_particles * 0.38)
    for _ in range(border_count):
        t = random.uniform(0, 2 * math.pi)
        hx, hy = heart_formula(t, scale=17.5)
        fuzz = random.gauss(0, 3.5)
        hx += fuzz * math.cos(t)
        hy += fuzz * math.sin(t)
        particles.append(Particle(hx, hy, is_border=True, layer_dist=1.0))

    # 2. Interior Dense Core & Volumetric Fill
    fill_count = num_particles - border_count
    for _ in range(fill_count):
        t = random.uniform(0, 2 * math.pi)
        hx, hy = heart_formula(t, scale=17.5)
        # Layer distance mapping for progressive wave reveal
        r = math.sqrt(random.uniform(0.005, 0.98))
        ix = hx * r
        iy = hy * r
        particles.append(Particle(ix, iy, is_border=False, layer_dist=r))

    return particles

particles = generate_heart_particles(5000)

running = True
paused = False
center_x, center_y = WIDTH // 2, HEIGHT // 2 - 25
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Global slow reveal progress (0.0 se 1.0 tak aage badhega)
global_reveal = 0.0
REVEAL_SPEED = 0.0018  # Ultra smooth slow reveal rate

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                particles = generate_heart_particles(5000)
                global_reveal = 0.0
            elif event.key == pygame.K_UP:
                REVEAL_SPEED = min(0.01, REVEAL_SPEED + 0.0005)
            elif event.key == pygame.K_DOWN:
                REVEAL_SPEED = max(0.0004, REVEAL_SPEED - 0.0005)

    time_sec = pygame.time.get_ticks() / 1000.0

    # 2. Heartbeat Rhythm (Lub-Dub Dual Pulse)
    beat = (math.sin(time_sec * 4.2) ** 63) * 0.11 + (math.sin(time_sec * 4.2 + 0.35) ** 63) * 0.05
    pulse_scale = 1.0 + beat

    if not paused:
        if global_reveal < 1.0:
            global_reveal = min(1.0, global_reveal + REVEAL_SPEED)

        for p in particles:
            p.update(global_reveal, pulse_scale, time_sec)

    # 3. Screen Rendering
    trail_surface.fill((3, 6, 16, 45))
    screen.blit(trail_surface, (0, 0))

    # Core Sparkle Fissure at Center (Gradually grows with reveal)
    fissure_len = int(140 * min(1.0, global_reveal * 1.5))
    if fissure_len > 10:
        pulse_core = int(4 + 2 * math.sin(time_sec * 8))
        pygame.draw.line(screen, (0, 180, 255), (center_x, center_y - fissure_len * 0.7), (center_x, center_y + fissure_len), 2)
        pygame.draw.line(screen, (220, 255, 255), (center_x, center_y - fissure_len * 0.4), (center_x, center_y + fissure_len * 0.6), 1)
        pygame.draw.circle(screen, (0, 240, 255), (center_x, center_y), pulse_core + 2)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), pulse_core)

    # Render All Active Particles
    for p in particles:
        p.draw(screen, center_x, center_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
