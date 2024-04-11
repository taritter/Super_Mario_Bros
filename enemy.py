import arcade
from load_textures import load_texture_pair

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the enemy is small or large
SMALL = 0
LARGE = 1

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 5

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

        """self,
        filename: str = None,
        scale: float = 1,
        image_x: float = 0,
        image_y: float = 0,
        image_width: float = 0,
        image_height: float = 0,
        center_x: float = 0,
        center_y: float = 0,
        _repeat_count_x=1,  # Unused
        _repeat_count_y=1,  # Unused
        flipped_horizontally: bool = False,
        flipped_vertically: bool = False,
        flipped_diagonally: bool = False,
        hit_box_algorithm: str = 'Simple',
        hit_box_detail: float = 4.5,
        texture: arcade.texture.Texture = None,
        angle: float = 0

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        main_path = "resources/sprites/"

        # Load textures for walking
        self.walk_textures = []
        for i in range(1, 3):  # Iterating from 1 to 2 (inclusive)
            texture = load_texture_pair(f"{main_path}goomba_{i}.png")
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.walk_textures[0]  # Using the first texture

        # Hit box will be set based on the first image used
        self.hit_box = self.texture.hit_box_points

        # Initialize movement variables
        self.change_x = ENEMY_MOVEMENT_SPEED
        self.change_y = 0"""

    def update(self, delta_time: float= 1/60):
        # Update enemy position
        if self.flipped_frames is None:
            self.unflipped_frames = self.frames[:]
            self.flipped_frames = load_flipped_images(self.frames) #fix this to texture set?
        if self.center_x >= self.properties['right_boundry']:
            self.change_x = -ENEMY_MOVEMENT_SPEED
        if self.center_y >= self.properties['left_boundry']:
            self.change_y = ENEMY_MOVEMENT_SPEED
        self.update_animation()
        super().update()
    
    def update_animation(self, delta_time: float = 1/60):
        if self.change_x < 0:
            self.frames = self.flipped_frames
        else:
            self.frames = self.unflipped_frames
        super().update_animation()

        #self.center_x += self.change_x
        #self.center_y += self.change_y


        # # Check if the enemy has reached the end of the platform, then change direction
        # if self.boundary_right and self.right > self.boundary_right:
        #     self.change_x = -ENEMY_MOVEMENT_SPEED
        # elif self.boundary_left and self.left < self.boundary_left:
        #     self.change_x = ENEMY_MOVEMENT_SPEED

        # # Update the texture based on direction
        # if self.change_x > 0:  # Moving right
        #     self.texture = self.walk_textures[0][0]  # Right-facing texture
        # elif self.change_x < 0:  # Moving left
        #     self.texture = self.walk_textures[0][1]  # Left-facing texture

class GoombaEnemy(Enemy):
   def __init__(self):
        super().__init__("sprites", "goomba_1.png")  # Initialize with goomba sprite folder and file name
