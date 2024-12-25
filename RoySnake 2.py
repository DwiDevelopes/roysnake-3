import pygame
import time
import random
import asyncio

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
width = 700
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('RoySnake 2')
logo = pygame.image.load('RoySnakeZero.ico')
pygame.display.set_icon(logo)

# Warna
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# Ukuran ular
snake_block = 10

# Gambar kepala dan badan ular
head_img1 = pygame.image.load('head.png')  # Gambar karakter 1
head_img2 = pygame.image.load('head2.png')  # Gambar karakter 2
body_img = pygame.image.load('body.png')
enemy_img = pygame.image.load('enemy.png')  # Gambar musuh
background_image2 = pygame.image.load('background1.jpg')
background_image3 = pygame.image.load('background2.jpg')
background_image1 = pygame.image.load('background.jpg')

# Memuat suara
eat_sound = pygame.mixer.Sound('eat_sound.wav')
game_over_sound = pygame.mixer.Sound('game_over.wav')
pygame.mixer.music.load('background.mp3')
pygame.mixer.music.play(-1)

# Fungsi untuk menggambar ular
def draw_snake(snake_list, head_img):
    for x in range(len(snake_list)):
        if x == 0:
            screen.blit(head_img, (snake_list[x][0], snake_list[x][1]))
        else:
            screen.blit(body_img, (snake_list[x][0], snake_list[x][1]))

# Fungsi untuk menggambar musuh
def draw_enemies(enemies):
    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

# Fungsi untuk menampilkan teks
def display_message(msg, color, x, y):
    font_style = pygame.font.SysFont(None, 50)
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [x, y])

# Fungsi untuk menggambar tombol
def draw_button(msg, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    
    display_message(msg, white, x + 20, y + 10)

# Fungsi untuk menampilkan menu tingkat kesulitan
def difficulty_menu(start_game, head_img):
    while True:
        screen.fill(black)
        screen.blit(background_image3, (0, 0))
        for i in range(1, 7):
            draw_button(f"Level {i}", 200, 150 + (i - 1) * 60, 200, 50, green, red, lambda level=i: start_game(level, head_img))

        draw_button("Back to Menu", 200, 150 + 10 * 60, 200, 50, green, red, menu)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

# Fungsi untuk menampilkan menu utama
async def menu():
    while True:
        screen.fill(black)
        screen.blit(background_image3, (0, 0))
        title_image = pygame.image.load("RoySnake2.png")
        title_image = pygame.transform.scale(title_image, (400, 200))
        screen.blit(title_image, (width // 2 - title_image.get_width() // 2, height // 5 - 100))
        
        draw_button("Start", 260, 260, 200, 60, green, red, character_selection)
        draw_button("Select", 260, 350, 200, 60, green, red, character_selection)
        draw_button("Quit", 260, 440, 200, 60, green, red, pygame.quit)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        await asyncio.sleep(0)
# Fungsi untuk pemilihan karakter
def character_selection():
    global head_img1, head_img2
    while True:
        screen.fill(black)
        screen.blit(background_image1, (0, 0))
        display_message("Select Your Character", white, width / 4, height / 5)
        
        draw_button("Character 1", 200, 250, 200, 50, green, red, lambda: difficulty_menu(game_loop, head_img1))
        draw_button("Character 2", 200, 320, 200, 50, green, red, lambda: difficulty_menu(game_loop, head_img2))
        draw_button("Back to Menu", 200, 390, 200, 50, green, red, menu)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

# Fungsi untuk menggambar rintangan
def draw_obstacles(obstacles):
    for obstacle in obstacles:
        pygame.draw.rect(screen, blue, [obstacle[0], obstacle[1], snake_block, snake_block])

# Fungsi untuk memeriksa tabrakan
def check_collision(snake_head, obstacles):
    for obstacle in obstacles:
        if snake_head[0] == obstacle[0] and snake_head[1] == obstacle[1]:
            return True
    return False

# Fungsi untuk memeriksa tabrakan dengan musuh
def check_enemy_collision(snake_head, enemies):
    for enemy in enemies:
        if snake_head[0] == enemy[0] and snake_head[1] == enemy[1]:
            return True
    return False

# Fungsi untuk memindahkan musuh
def move_enemies(enemies, snake_head):
    for i in range(len(enemies)):
        if enemies[i][0] < snake_head[0]:
            enemies[i][0] += snake_block // 2
        elif enemies[i][0] > snake_head[0]:
            enemies[i][0] -= snake_block // 2

        if enemies[i][1] < snake_head[1]:
            enemies[i][1] += snake_block // 2
        elif enemies[i][1] > snake_head[1]:
            enemies[i][1] -= snake_block // 2

def game_loop(level, head_img):
    global snake_speed
    game_over = False
    game_close = False
    score = 0  # Initialize score

    # Set kecepatan dan rintangan berdasarkan level
    snake_speed = 10 + level * 2

    x1 = width / 2
    y1 = height / 2

    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    # Rintangan
    obstacles = []
    num_obstacles = level
    for _ in range(num_obstacles):
        obstacle_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        obstacle_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
        obstacles.append((obstacle_x, obstacle_y))

    # Musuh
    enemies = []
    for _ in range(2):  # Menambahkan musuh
        enemy_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        enemy_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
        enemies.append([enemy_x, enemy_y])  # Musuh disimpan sebagai list agar bisa diubah

    while not game_over:

        while game_close:
            screen.fill(black)
            screen.blit(background_image1, (0, 0))
            title_image = pygame.image.load("GameOver.png")
            title_image = pygame.transform.scale(title_image, (400, 200))
            screen.blit(title_image, (width // 2 - title_image.get_width() // 2, height // 7 - 100))
            display_message(f"Score: {score}", white, width / 2.8, height / 3.5)
            draw_button("Select", 220, 215, 228, 50, green, blue, lambda: character_selection())
            draw_button("Restart", 220, 315, 228, 50, green, blue, lambda: difficulty_menu(game_loop, head_img))
            draw_button("Menu", 220, 415, 228, 50, green, blue, menu)
            draw_button("Exit", 220, 515, 228, 50, green, red, pygame.quit)
            
            pygame.display.update()
            game_over_sound.play()  # Memutar suara game over

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop(level, head_img)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        
        # Gambar latar belakang
        screen.blit(background_image2, (0, 0))

        pygame.draw.rect(screen, white, [foodx, foody, snake_block, snake_block])
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(snake_list, head_img)
        draw_obstacles(obstacles)
        draw_enemies(enemies)

        move_enemies(enemies, snake_head)

        # Cek tabrakan dengan rintangan dan musuh
        if check_collision(snake_head, obstacles) or check_enemy_collision(snake_head, enemies):
            game_close = True

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            snake_length += 1
            score += 1  # Increment score
            eat_sound.play()  # Memutar suara saat memakan makanan

        pygame.time.Clock().tick(snake_speed)

    pygame.quit()
    quit()

asyncio.run(menu())  # Menjalankan menu utama
