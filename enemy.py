import arcade
from load_textures import load_texture_pair
from typing import (
    List
)

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the enemy is small or large
SMALL = 0
LARGE = 1

CHARACTER_SCALING = 2.5

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 100

class Koopa(arcade.AnimatedTimeBasedSprite):
    def __init__(self, filename, **kwargs): #5.19 #original ===self, name_folder, name_file):
        super().__init__()
        self.change_x = ENEMY_MOVEMENT_SPEED
        self.scale = CHARACTER_SCALING
        self.r_texture1 = arcade.load_texture("resources/sprites/koopa_1.png", flipped_horizontally=False)
        self.r_texture2 = arcade.load_texture("resources/sprites/koopa_2.png", flipped_horizontally=False)
        self.l_texture1 = arcade.load_texture("resources/sprites/koopa_1.png", flipped_horizontally=True)
        self.l_texture2 = arcade.load_texture("resources/sprites/koopa_2.png", flipped_horizontally=True)

        self.l_frames = [arcade.AnimationKeyframe(0, 150, self.l_texture1), arcade.AnimationKeyframe(1, 150, self.l_texture2)]
        self.r_frames = [arcade.AnimationKeyframe(0, 150, self.r_texture1), arcade.AnimationKeyframe(1, 150, self.r_texture2)]

        self.hit = False
        if filename == "resources/sprites/koopa_shell.png":
            print("loading shells")
            self.shell = arcade.load_texture(filename)
            self.shell_frame = [arcade.AnimationKeyframe(0, 200, self.shell)]

        # Set initial texture
        self.texture = self.l_texture1
        self.hit_box = self.texture.hit_box_points

    
    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0 and not self.hit:
            self.frames = self.r_frames
        elif self.change_x > 0 and not self.hit:
            self.frames = self.l_frames
        
        super().update_animation()