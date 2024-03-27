"""
Platformer Template
"""
import arcade
import math
import launch
import random
from mario import Mario
from enemy import Enemy
from enemy import GoombaEnemy
import json
from mystery_box import Mystery_Box
from coin import Coin
from load_textures import load_texture_pair


# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
DEFAULT_FONT_SIZE = 25

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2.5
TILE_SCALING = 2.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING
NUMBER_OF_COINS = 3

# The gravity that is used by the physics engine
GRAVITY = 0.8

PLAYER_START_X = SPRITE_PIXEL_SIZE * CHARACTER_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 2

LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PLATFORMS_BREAKABLE = "Platform_Breakable"
LAYER_NAME_PLATFORMS_COINS = "Platform_Coin"
LAYER_NAME_PLATFORMS_ITEM = "Platform_Item"
LAYER_NAME_MYSTERY_ITEM = "Mystery_Item"
LAYER_NAME_MYSTERY_COIN = "Mystery_Coin"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Goomba"

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT,
                         SCREEN_TITLE, resizable=False)

        # Put saved stuff here
        save_name = "1"
        self.save_path = f"resources/save_data/save_{save_name}.json"
        save_file = open(self.save_path)
        save_data = json.load(save_file)
        
        self.score = save_data['score']
        self.coin_count = save_data['coin_count']
        self.lives = save_data['lives']
        self.stage = save_data['stage']
        
        save_file.close()

        # Our TileMap Object
        self.tile_map = None

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.mario = None

        # Our physics engine
        self.physics_engine = None

        self.background_list = []

        self.player_list = []

        self.enemy_list = []

        self.coin_sound = arcade.load_sound("resources/sounds/smw_coin.wav")

        # A Camera that can be used for scrolling the screen
        self.camera = None

        self.screen_center_x = 0
        self.screen_center_y = 0

        # What key is pressed down?
        self.left_key_down = False
        self.right_key_down = False
        self.jump_key_down = False
        self.sprint_key_down = False

        # background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        
        # Set a timer
        self.timer = 300
        
        # Reset the 'center' of the screen to 0
        self.screen_center_x = 0
        self.screen_center_y = 0
        
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        # Can modify this by replacing instances of '1-1' with self.stage
        map_name = "resources/backgrounds/1-1/world_1-1.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_PLATFORMS_BREAKABLE: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_PLATFORMS_COINS: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_PLATFORMS_ITEM: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_MYSTERY_ITEM: {
                "use_spatial_hash": True,
                "custom_class": Mystery_Box,
            },
            LAYER_NAME_MYSTERY_COIN: {
                "use_spatial_hash": True,
                "custom_class": Mystery_Box,
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True,
                "custom_class": Coin,
            },
            LAYER_NAME_BACKGROUND: {
                "use_spatial_hash": True,
            },
            # LAYER_NAME_ENEMIES: {
            #     "use_spatial_hash": True,
            #     "custom_class": GoombaEnemy,
            # },
        }

        # Read in the tiled map
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order.
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set platforms
        self.platform_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS]
        self.platform_breakable_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_BREAKABLE]
        self.platform_coin_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_COINS]
        self.platform_item_list = self.tile_map.sprite_lists[LAYER_NAME_PLATFORMS_ITEM]
        self.mystery_item_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_ITEM]
        self.mystery_coin_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_COIN]
        self.enemy_list = self.tile_map.sprite_lists[LAYER_NAME_ENEMIES]

        # Set coins
        self.coin_list = self.tile_map.sprite_lists[LAYER_NAME_COINS]

        # Set background image
        self.background_list = self.tile_map.sprite_lists[LAYER_NAME_BACKGROUND]

        # Set the position of the background

        # Calculate the drawing position for the background sprite
        background_draw_x = self.tile_map.width*GRID_PIXEL_SIZE / 2
        background_draw_y = self.tile_map.height*GRID_PIXEL_SIZE / 2 # Align top of sprite with top of screen
        self.background_list[0].set_position(background_draw_x, background_draw_y)

        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

        # -- Enemies
        # for my_object in enemies_layer:
        #     cartesian = self.tile_map.get_cartesian(
        #         my_object.shape[0], my_object.shape[1]
        #     )

        #     #todo: enemy_type== "goomba" might not work!!
        #     #enemy_type = my_object.properties["type"]
        #     #if enemy_type == "goomba":
        #         #enemy = GoombaEnemy()
        #     #elif enemy_type == "zombie":
        #         #enemy = ZombieEnemy()
        #     #else:
        #         #raise Exception(f"Unknown enemy type {enemy_type}.")
            
        #     goomba = GoombaEnemy()
        #     # Set the initial position of the Goomba
        #     goomba.center_x = 55  # Set the x-coordinate according to your game's layout
        #     goomba.center_y = 48  # Set the y-coordinate according to your game's layout
        #     # Add the Goomba to the appropriate sprite list
        #     self.scene.add_sprite(LAYER_NAME_ENEMIES, goomba)

        #     '''
        #     enemy.center_x = math.floor(
        #         cartesian[0] * TILE_SCALING * self.tile_map.tile_width
        #     )
        #     enemy.center_y = math.floor(
        #         (cartesian[1] + 1) * (self.tile_map.tile_height * TILE_SCALING)
        #     )
        #     '''
        #     self.scene.add_sprite(LAYER_NAME_ENEMIES, goomba)

        # Set up the player, specifically placing it at these coordinates.
        self.mario = Mario(CHARACTER_SCALING)
        self.mario.center_x = 48
        self.mario.center_y = 48
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.mario)

        # --- Other stuff
        # Create the 'physics engine'
        walls = [self.platform_list, self.platform_breakable_list, self.platform_item_list, self.mystery_item_list, self.mystery_coin_list]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.mario, gravity_constant=GRAVITY, walls=walls
        )


    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Activate our Camera
        self.camera.use()

        # Draw our Scene
        # Draw the platforms
        self.scene.draw(pixelated=True)

        #Todo: Draw the goombas

        # Draw the player
        self.mario.draw(pixelated=True)
        
        # Draw the text last, so it goes on top
        # Have to squeeze everything into one text draw, otherwise major lag
        draw_string = f"MARIO \t\t COINS \t\t WORLD \t\t TIME \n{self.score:06d}  \t\t {self.coin_count:02d} \t\t\t   {self.stage} \t\t {self.timer:03d}"
        
        arcade.draw_text(draw_string,
                         self.screen_center_x + SCREEN_WIDTH / 10,
                         SCREEN_HEIGHT - 2 * DEFAULT_FONT_SIZE,
                         arcade.color.WHITE,
                         DEFAULT_FONT_SIZE,
                         multiline = True,
                         width=SCREEN_WIDTH,
                         align="left",
                         font_name="Kenney Pixel")
        
    

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            self.jump_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            # Prevents the user from double jumping
            self.jump_key_down = False
        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
        # Sprint
        elif key == arcade.key.J:
            self.sprint_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
        elif key == arcade.key.J:
            self.sprint_key_down = False

    def center_camera_to_player(self):
        if (self.mario.center_x - (self.camera.viewport_width / 3)) > self.screen_center_x:
            self.screen_center_x = self.mario.center_x - (self.camera.viewport_width / 3)

        # Don't let camera travel past 0
        if self.screen_center_x < 0:
            self.screen_center_x = 0

        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):
        """Movement and game logic"""
        if self.mario.center_x < self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2:
            self.mario.center_x = self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2
            self.mario.change_x = 0
        
        # Player dies if they fall below the world or run out of time
        if self.mario.center_y < -SPRITE_PIXEL_SIZE or self.timer <= 0:
            self.player_die()
        
        

        # Player movement and physics engine
        self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
        self.physics_engine.update()

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_PLAYER, LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS, LAYER_NAME_ENEMIES]
        )

        # Position the camera
        self.center_camera_to_player()

        # See if the coin is hitting a platform
        coin_hit_list = arcade.check_for_collision_with_list(self.mario, self.coin_list)

        for coin in coin_hit_list:
            self.coin_count += 1
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.coin_sound)


        #  Goomba movement put logic here
        enemy_hit_list = arcade.check_for_collision_with_list(self.mario, self.enemy_list)

        for enemy in enemy_hit_list:
            enemy.remove_from_sprite_lists()

        
        
    def save(self):
        save_file = open(self.save_path, "w")
        save_data = {
            'score' : self.score,
            'coin_count' : self.coin_count,
            'lives' : self.lives,
            'stage' : self.stage
        }
        json.dump(save_data, save_file)        
        save_file.close()
        
    def player_die(self):
        self.lives -= 1
        # Can likely put these at the start of setup:
            # self.save() 
            # Give a death screen
        
        # Reset the stage

        self.setup()
        
        # For later, give a game over screen if lives reduced to zero (>0 can be infinite)
        # Ideally, also reset the save file to a default version (save_0.json)
        if self.lives == 0:
            pass


def main():
    """Main function"""
    # window = MyGame()
    # window.setup()
    # arcade.run()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = launch.Title_Screen()
    window.show_view(start_view)
    arcade.run()
    # arcade.close_window()


if __name__ == "__main__":
    main()