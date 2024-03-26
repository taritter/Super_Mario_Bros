import arcade
from load_textures import load_texture_pair

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants to check if the enemy is sliding
NOT_SLIDING = 0
SLIDING = 1

# Constants to track if the enemy is small or large
SMALL = 0
LARGE = 1

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 4
ENEMY_SPRINT_SPEED = 8
ENEMY_ACCELERATION = 0.2
ENEMY_FRICTION = 0.35
ENEMY_JUMP_SPEED = 18

class Enemy(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        # Used for image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.character_face_direction = RIGHT_FACING

        main_path = f":resources:images/animated_characters/{name_folder}/{name_file}"

        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

#class Enemy(Entity):
    #def __init__(self, name_folder, name_file):

        # Setup parent class
        #super().__init__(name_folder, name_file)


class GoombaEnemy(Enemy):
    def __init__(self):

        # Set up parent class
        super().__init__("goomba", "goomba") #or uper().__init__(name_folder, name_file)


#class ZombieEnemy(Enemy):
    #def __init__(self):

        # Set up parent class
        #super().__init__("zombie", "zombie")