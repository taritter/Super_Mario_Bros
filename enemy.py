import arcade
from load_textures import load_texture_pair

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the enemy is small or large
SMALL = 0
LARGE = 1

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 100

def load_flipped_images(frames: list[arcade.AnimationKeyframe]) -> list[arcade.AnimationKeyframe]:
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
        self.flipped_frames= None
        self.unflipped_frames = None

    def update(self, delta_time: float= 1/60):
        # Update enemy position
        if self.flipped_frames is None:
            self.unflipped_frames = self.frames[:]
            self.flipped_frames = load_flipped_images(self.frames) #fix this to texture set?
        if self.center_x >= self.properties['right_boundary']:
            self.change_x = -ENEMY_MOVEMENT_SPEED
        if self.center_x <= self.properties['left_boundary']:
            self.change_x = ENEMY_MOVEMENT_SPEED
        self.update_animation()
        super().update()
    
    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0:
            self.frames = self.flipped_frames
        else:
            self.frames = self.unflipped_frames
        super().update_animation()
