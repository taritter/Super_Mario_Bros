"""
Platformer Template
"""
import arcade

# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2.5
TILE_SCALING = 2.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the player is sprinting
SPRINTING = 0
WALKING = 1

# Constants to track if the player is small or large
SMALL = 0
LARGE = 1

# Constants to track if the player has the fire powerup
POWERUP = 0
POWERUP = 1

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
PLAYER_SPRINT_SPEED = 8
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 18

PLAYER_START_X = SPRITE_PIXEL_SIZE * CHARACTER_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 2

LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLAYER = "Player"

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "resources/sprites/"

        # Load textures for idle standing
        self.small_idle_texture_pair = load_texture_pair(f"{main_path}mario_small_idle.png")

        # Load textures for walking
        self.small_jump_texture_pair = load_texture_pair(f"{main_path}mario_small_jump.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(1, 4):
            texture = load_texture_pair(f"{main_path}mario_small_walk_{i}.png")
            self.walk_textures.append(texture)

        # Set the initial texture
        self.texture = self.small_idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

        self.update_counter = 0

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        # Only change if the player is touching the ground
        if self.change_y == 0:
            if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
                self.character_face_direction = LEFT_FACING
            elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
                self.character_face_direction = RIGHT_FACING

        # Jumping animation
        if self.change_y != 0:
            self.texture = self.small_jump_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.small_idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        if self.update_counter >= 5:
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
            self.update_counter = 0
        
        self.update_counter += 1



class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, resizable=True)

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None


        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False
        self.sprint_key_down = False

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Name of map file to load
        map_name = "resources/demo_background.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_BACKGROUND: {
                "use_spatial_hash": True,
            },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set wall List
        self.wall_list = self.tile_map.sprite_lists["Platforms"]

        # Set background image
        self.background_list = self.tile_map.sprite_lists["Background"]

        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 48
        self.player_sprite.center_y = 48
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # --- Other stuff
        # Create the 'physics engine'
        walls = [self.wall_list, ]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=walls
        )

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Draw our Scene
        # Note, if you a want pixelated look, add pixelated=True to the parameters

        # Calculate the drawing position for the background sprite
        background_draw_x = 128 * TILE_SCALING
        background_draw_y = 120 * TILE_SCALING # Align top of sprite with top of screen

        # Set the position of the background sprite before drawing
        self.background_list[0].set_position(background_draw_x, background_draw_y)

        #self.background_list.draw(pixelated=True)
        #self.wall_list.draw(pixelated=True)
        self.scene.draw(pixelated=True)
        

        #self.scene.draw()


    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0

        if self.left_key_down and not self.right_key_down:
            if self.sprint_key_down:
                self.player_sprite.change_x = -PLAYER_SPRINT_SPEED
            else:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_key_down and not self.left_key_down:
            if self.sprint_key_down:
                self.player_sprite.change_x = PLAYER_SPRINT_SPEED
            else:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.update_player_speed()

        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.update_player_speed()

        # Sprint
        elif key == arcade.key.J:
            self.sprint_key_down = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
            self.update_player_speed()
        elif key == arcade.key.J:
            self.sprint_key_down = False
            self.update_player_speed()

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_BACKGROUND, LAYER_NAME_PLATFORMS, LAYER_NAME_PLAYER]
        )




def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()