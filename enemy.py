import arcade
from load_textures import load_texture_pair

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the enemy is small or large
SMALL = 0
LARGE = 1

# Movement speed of enemy, in pixels per frame
ENEMY_MOVEMENT_SPEED = 4

class Enemy(arcade.Sprite):
    def __init__(self, name_folder, name_file):
        super().__init__()

        # Default to facing right
        self.facing_direction = RIGHT_FACING

        main_path = "resources/sprites/"

        # Load textures for walking
        self.walk_textures = []
        for i in range(1, 3):  # Iterating from 1 to 2 (inclusive)
            texture = load_texture_pair(f"{main_path}goomba_{i}.png")
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.walk_textures[0][0]  # Using the first texture

        # Hit box will be set based on the first image used
        self.hit_box = self.texture.hit_box_points

        # Initialize movement variables
        self.change_x = ENEMY_MOVEMENT_SPEED
        self.change_y = 0

    def update(self):
        # Update enemy position
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check if the enemy has reached the end of the platform, then change direction
        if self.boundary_right and self.right > self.boundary_right:
            self.change_x = -ENEMY_MOVEMENT_SPEED
        elif self.boundary_left and self.left < self.boundary_left:
            self.change_x = ENEMY_MOVEMENT_SPEED

        # Update the texture based on direction
        if self.change_x > 0:  # Moving right
            self.texture = self.walk_textures[0][0]  # Right-facing texture
        elif self.change_x < 0:  # Moving left
            self.texture = self.walk_textures[0][1]  # Left-facing texture

class GoombaEnemy(Enemy):
    def __init__(self):
        super().__init__("sprites", "goomba_1.png")  # Initialize with goomba sprite folder and file name
