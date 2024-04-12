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

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 100

def load_flipped_images(frames: List[arcade.AnimationKeyframe]) -> List[arcade.AnimationKeyframe]:
    flipped_frames = []
    for frame in frames:
        clean_filename = frame.texture.name.split('.png')[0]+".png"
        flipped_frame = arcade.AnimationKeyframe(
            frame.tile_id,
            frame.duration, 
            arcade.load_texture(clean_filename, flipped_horizontally = True) #clean filename
        )
        flipped_frames.append(flipped_frame)
    return flipped_frames

class Enemy(arcade.AnimatedTimeBasedSprite):
    def __init__(self, filename, **kwargs): #5.19 #original ===self, name_folder, name_file):
        super().__init__()
        self.change_x = ENEMY_MOVEMENT_SPEED
        self.flipped_frames = self.frames[:]
        self.unflipped_frames = load_flipped_images(self.frames)

    def update(self, delta_time: float= 1/60):
        print("left boundary ", self.properties['left_boundary'])
        print("right boundary ", self.properties['right_boundary'])
        # Update enemy position
        if self.center_x >= self.properties['right_boundry']:
            self.change_x = -ENEMY_MOVEMENT_SPEED
        if self.center_y >= self.properties['left_boundry']:
            self.change_y = ENEMY_MOVEMENT_SPEED
        self.update_animation()
        super().update()
    
    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0:
            self.frames = self.flipped_frames
            print(self.frames)
        else:
            self.frames = self.unflipped_frames
            print(self.frames)
        super().update_animation()