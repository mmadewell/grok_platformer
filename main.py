import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Platformer Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRIGHT_RED = (255, 50, 50)
BRIGHT_GREEN = (50, 255, 50)
BRIGHT_BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)

# 3D math functions
def rotate_x(point, angle):
    y = point[1] * math.cos(angle) - point[2] * math.sin(angle)
    z = point[1] * math.sin(angle) + point[2] * math.cos(angle)
    return [point[0], y, z]

def rotate_y(point, angle):
    x = point[0] * math.cos(angle) + point[2] * math.sin(angle)
    z = -point[0] * math.sin(angle) + point[2] * math.cos(angle)
    return [x, point[1], z]

def translate(point, dx, dy, dz):
    return [point[0] + dx, point[1] + dy, point[2] + dz]

def project(point, camera_z):
    z_factor = camera_z - point[2]
    if z_factor < 0.1: z_factor = 0.1
    factor = 200 / z_factor
    x = point[0] * factor + WIDTH // 2
    y = -point[1] * factor + HEIGHT // 2
    return [x, y]

def get_face_depth(vertices, face_indices):
    return sum(vertices[i][2] for i in face_indices) / len(face_indices)

# Player (a smaller cube)
player_size = 0.25
player_vertices = [
    [-player_size, -player_size, -player_size], [player_size, -player_size, -player_size],
    [player_size, player_size, -player_size], [-player_size, player_size, -player_size],
    [-player_size, -player_size, player_size], [player_size, -player_size, player_size],
    [player_size, player_size, player_size], [-player_size, player_size, player_size]
]
player_faces = [
    ([0, 1, 2, 3], BRIGHT_RED), ([4, 5, 6, 7], BRIGHT_GREEN), ([0, 1, 5, 4], BRIGHT_BLUE),
    ([2, 3, 7, 6], YELLOW), ([0, 3, 7, 4], WHITE), ([1, 2, 6, 5], GRAY)
]
player_pos = [0, -0.65, 0]  # On first platform
player_velocity = [0, 0, 0]
gravity = 0.02
jump_strength = 0.5
on_ground = False
last_platform = None
just_landed = False
prev_velocity_y = 0  # Track previous Y velocity

# Platform class
class Platform:
    def __init__(self, x, y, z, width, depth):
        self.pos = [x, y, z]
        self.width = width
        self.depth = depth
        h = 0.2
        self.vertices = [
            [x - width/2, y - h/2, z - depth/2], [x + width/2, y - h/2, z - depth/2],
            [x + width/2, y + h/2, z - depth/2], [x - width/2, y + h/2, z - depth/2],
            [x - width/2, y - h/2, z + depth/2], [x + width/2, y - h/2, z + depth/2],
            [x + width/2, y + h/2, z + depth/2], [x - width/2, y + h/2, z + depth/2]
        ]
        self.faces = [
            ([0, 1, 2, 3], GRAY), ([4, 5, 6, 7], GRAY), ([0, 1, 5, 4], GRAY),
            ([2, 3, 7, 6], BRIGHT_GREEN), ([0, 3, 7, 4], GRAY), ([1, 2, 6, 5], GRAY)
        ]

# Game setup
platforms = [
    Platform(0, -1, 0, 3, 3),  # Starting platform
    Platform(2, -0.5, 0, 3, 3)  # Second platform
]
camera_z = 1
score = 0
font = pygame.font.SysFont(None, 48)

def spawn_platform(last_platform):
    max_horizontal = 5
    max_vertical = 6
    x = last_platform.pos[0] + random.uniform(-max_horizontal, max_horizontal)
    y = last_platform.pos[1] + random.uniform(0.5, max_vertical)
    z = last_platform.pos[2] + random.uniform(-max_horizontal, max_horizontal)
    return Platform(x, y, z, random.uniform(2, 4), random.uniform(2, 4))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and on_ground:
        player_velocity[1] = jump_strength
        on_ground = False
        just_landed = False
        print("Jump detected")

    move_speed = 0.1
    if keys[pygame.K_a]: player_velocity[0] = -move_speed
    if keys[pygame.K_d]: player_velocity[0] = move_speed
    if not (keys[pygame.K_a] or keys[pygame.K_d]): player_velocity[0] *= 0.9

    # Physics
    player_velocity[1] -= gravity
    player_pos[0] += player_velocity[0]
    player_pos[1] += player_velocity[1]
    player_pos[2] += player_velocity[2]

    # Collision detection
    on_ground = False
    current_platform = None
    for platform in platforms:
        px, py, pz = player_pos
        plat_x, plat_y, plat_z = platform.pos
        within_bounds = (abs(px - plat_x) < platform.width/2 + player_size and
                         abs(pz - plat_z) < platform.depth/2 + player_size and
                         py - player_size <= plat_y + 0.5 and
                         py - player_size >= plat_y - 0.5)
        if within_bounds:
            print(f"Collision detected with platform at {platform.pos}")
            if prev_velocity_y < 0 and player_velocity[1] <= 0:  # New landing
                just_landed = True
            if player_velocity[1] <= 0:  # On ground or landing
                player_pos[1] = plat_y + 0.1 + player_size
                player_velocity[1] = 0
            on_ground = True
            current_platform = platform
        else:
            print(f"No collision with platform at {platform.pos}, player at {player_pos}")

    # Check for new platform landing
    if (just_landed and current_platform and current_platform != last_platform and 
        current_platform != platforms[0]):
        score += 1
        platforms.pop(0)
        platforms.append(spawn_platform(platforms[-1]))
        just_landed = False
    last_platform = current_platform if on_ground else None
    prev_velocity_y = player_velocity[1]  # Update previous velocity

    # Game over condition
    if player_pos[1] < -10:
        running = False

    # Camera follows player
    camera_pos = [player_pos[0], player_pos[1], player_pos[2] + camera_z]

    # Clear screen
    screen.fill((50, 50, 150))

    # Transform and render all objects
    all_objects = [(player_vertices, player_faces, player_pos)] + \
                  [(p.vertices, p.faces, p.pos) for p in platforms]
    render_list = []
    for vertices, faces, pos in all_objects:
        transformed_vertices = []
        for v in vertices:
            v_world = translate(v, pos[0], pos[1], pos[2])
            v_trans = translate(v_world, -camera_pos[0], -camera_pos[1], -camera_pos[2])
            transformed_vertices.append(v_trans)
        projected_points = [project(v, camera_z) for v in transformed_vertices]
        for face_indices, color in faces:
            depth = get_face_depth(transformed_vertices, face_indices)
            face_points = [projected_points[i] for i in face_indices]
            render_list.append((depth, face_points, color))

    # Sort and draw
    render_list.sort(reverse=True)
    for _, face_points, color in render_list:
        pygame.draw.polygon(screen, color, face_points)

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Game over screen
game_over_text = font.render(f"Game Over! Score: {score}", True, WHITE)
screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))
pygame.display.flip()
pygame.time.wait(2000)
pygame.quit()