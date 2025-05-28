from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
import time

app = Ursina()
player_enabled = True
p_key_held = False
original_world = []
world_size = 20  # x та y
world_depth = 5  # z

grass_texture = load_texture('assets/grass_block2.png')
stone_texture = load_texture('assets/stone_block2.png')
wood_texture = load_texture('assets/wood_block.png')
brick_texture = load_texture('assets/brick_block.png')
dirt_texture = load_texture('assets/dirt_block.png')
sky_texture = load_texture('assets/skybox.png')
arm_texture = load_texture('assets/arm_texture2.png')
punch_sound = Audio('assets/punch_sound', loop=False, autoplay=False)
block_pick = 1

window.fps_counter.enabled = True
window.exit_button.visible = True

def show_popup(text):
    global popup_text # дозволяє використати змінну поза функцією
    popup_text = Text(text=text, origin=(0, 0), scale=2, color=color.black)
    popup_text.x = -popup_text.width / 2
    popup_text.y = -popup_text.height / 2

def hide_popup():
    global popup_text
    destroy(popup_text) # видаляє текст 

def reset_game():
    show_popup("Світ перезавантажено")
    for voxel in scene.entities:
        if isinstance(voxel, Voxel): # перевіряє чи е об'єкт екземпляром для вказаного класу
            voxel.disable()
    for x, y, z, texture in original_world: # список усіх блоків, які мають бути в початковому світі
        Voxel(position=(x, y, z), texture=texture)
    player.position = (12, 4, 12) # позиція гравція за замовченням
    invoke(hide_popup, delay=4) # функція заклик, спилваюче вікно зникає через 4 секунди

def toggle_player_visibility(): 
    global player_enabled
    player_enabled = not player_enabled
    player.enabled = player_enabled # перемикає видиміть гравця "відключає його від руки"

def update(): # функція що виконується автоматично на кожному кадрі для реалізації інтерактивності
    global block_pick
    global p_key_held

    if player.y < -10:
        reset_game() # перезавантаження світу якщо гравець впав нижче ніж на 10 боків вниз

    if held_keys['r']:
        reset_game()

    if held_keys['p'] and not p_key_held: # запобігання багаторазовому спрацюванню 
        toggle_player_visibility() # гравець зникає та з'являється
        p_key_held = True
    elif not held_keys['p'] and p_key_held:
        p_key_held = False

    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.active()
    else:
        hand.passive()

    if held_keys['1']: block_pick = 1
    if held_keys['2']: block_pick = 2
    if held_keys['3']: block_pick = 3
    if held_keys['4']: block_pick = 4
    if held_keys['5']: block_pick = 5

class Voxel(Button): # кожен блок (voxel) успадковується і поводить себе як кнопка
    def __init__(self, position=(0, 0, 0), texture=grass_texture): # метод, що викликається під час створення нового об'єкту
        super().__init__( # викликаємо конструктор батьківського класу
            parent=scene, # додавання блоку до сцени
            position=position,
            model='assets/block',
            origin_y=0.5, # центр об'єкта припіднятий вгору, шоб стояв на землі
            texture=texture,
            color=color.color(0, 0, 1),
            scale=0.5
        )
        self.default_color = self.color

    def on_mouse_enter(self): # зміна кольору блоку при наведені мишкою
        self.color = color.color(19, 0.03, 0.7)

    def on_mouse_exit(self): # повернення кольору
        self.color = self.default_color

    def input(self, key): # обробка натискань клавіш
        if key == 'escape':
            application.quit()

        if self.hovered: # виконання тільки, якщо миша наведена на блок
            if key == 'right mouse down':
                punch_sound.play()
                pos = self.position + mouse.normal
                if block_pick == 1: Voxel(position=pos, texture=grass_texture)
                if block_pick == 2: Voxel(position=pos, texture=stone_texture)
                if block_pick == 3: Voxel(position=pos, texture=brick_texture)
                if block_pick == 4: Voxel(position=pos, texture=dirt_texture)
                if block_pick == 5: Voxel(position=pos, texture=wood_texture)

            if key == 'left mouse down':
                punch_sound.play()
                destroy(self)

class NonInteractiveButton(Button): # клас, що успадковує властивості кнопки. виглядає як кнопка, але з мишею не взаємодіє
    def __init__(self, **kwargs): # конструктор класу. Все, що передадуть (color) — автоматично піде в Button
        super().__init__(**kwargs) # створення звичайної кнопки
        self.highlight_color = self.color # явно зберігаємо колір, щоб уникнути зміни підсвітки
        self.collision = False # кнопка не реагує на натискання чи наведенян 

class TableUI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui) # TableUI стає частиною 2D UI, який видно поверх 3D-сцени

        cell_size = 0.08
        spacing = 0.02
        textures = [
            "assets/grass3d.png", "assets/Stone3d.png",
            "assets/Brick3d.png", "assets/Dirt3d.png",
            "assets/plank3d.png"
        ]

        self.cells = [] # створення кнопок, до яких в подальшому можна звертатися
        for i in range(9):
            if i <= 4: # створення текстур за кнопками від 0 до 4 (у комірках)
                cell = NonInteractiveButton(
                    parent=self,
                    model='quad',
                    color=color.rgba(1, 1, 1, 0.9),
                    texture=textures[i],
                    border=0.02,
                    scale=(cell_size, cell_size),
                    origin=(-0.5, 0),
                    position=(-0.43 + i * (cell_size + spacing), -0.42)
                )
            else:
                cell = NonInteractiveButton( # порожні слоти (комірки), що не знадобилися
                    parent=self,
                    model='quad',
                    border=0.02,
                    scale=(cell_size, cell_size),
                    origin=(-0.5, 0),
                    position=(-0.43 + i * (cell_size + spacing), -0.42)
                )
            text_entity = Text(
                parent=self,
                text=str(i + 1),
                scale=1,
                position=(cell.x + 0.02, cell.y + 0.03),
                origin=(-0.5, 0),
                background=True
            )
            self.cells.append(cell) # зберігаємо посилання на всі кнопки

class Sky(Entity):
    def __init__(self):
        super().__init__(
            parent=scene,
            model='sphere',
            texture=sky_texture,
            scale=150,
            double_sided=True # вмикає видимість сфери зсередини світу
        )

class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='assets/arm',
            texture=arm_texture,
            scale=0.2,
            rotation=Vec3(150, -10, 0),
            position=Vec2(0.4, -0.6)
        )

    def active(self): # активація руки гравця
        self.position = Vec2(0.3, -0.5)

    def passive(self): # повернення руки гравця
        self.position = Vec2(0.4, -0.6)

# Створення світу
for z in range(world_size):
    for x in range(world_size):
        for y in range(world_depth): 
            if y == 4:
                voxel = Voxel(position=(x, y, z), texture=grass_texture)
                original_world.append((x, y, z, grass_texture))
            elif y == 0:
                voxel = Voxel(position=(x, y, z), texture=stone_texture)
                original_world.append((x, y, z, stone_texture))
            else:
                voxel = Voxel(position=(x, y, z), texture=dirt_texture)
                original_world.append((x, y, z, dirt_texture))

player = FirstPersonController(position=(12, 15, 12)) # створення гравця з видом від першої особи
table = TableUI() 
sky = Sky()
hand = Hand()
window.fullscreen = True
app.run()
