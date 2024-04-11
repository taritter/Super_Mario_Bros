"""
Platformer Template
"""
import arcade
import time
import launch
import random
from mario import Mario
import json
from mystery_box import Mystery_Box
from coin import Coin

# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
DEFAULT_FONT_SIZE = 25

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
LAYER_NAME_FLAG = "Flag"
LAYER_NAME_DOOR = "Next_Level_Door"

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

        self.mario_door = False

        self.mario_flag = False

        # Our physics engine
        self.physics_engine = None

        self.background_list = []

        self.player_list = []

        # -- sounds --
        self.jump_sound = arcade.load_sound("resources/sounds/jump_sound.mp3")

        self.coin_sound = arcade.load_sound("resources/sounds/smw_coin.wav")

        self.timeUp = arcade.load_texture("resources/backgrounds/timeupMario.png")

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
        self.do_update = True

        # Set a timer
        self.timer = 300
        self.frame_counter = 0
        
        # Reset the 'center' of the screen to 0
        self.screen_center_x = 0
        self.screen_center_y = 0
        
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Name of map file to load
        self.stages = {1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "2-1", 6: "2-2", 7: "2-3", 8: "2-4"}
        self.stage_num = 1
        self.stage = self.stages[self.stage_num]
        map_name = f"resources/backgrounds/1-1/world_{self.stage}.json"

        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_BREAKABLE: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_COINS: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
            },
            LAYER_NAME_PLATFORMS_ITEM: {
                "use_spatial_hash": True,
                "hit_box_algorithm": "None",
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
            LAYER_NAME_FLAG: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_DOOR: {
                "use_spatial_hash": True,
            },
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

        # Set coins
        self.coin_list = self.tile_map.sprite_lists[LAYER_NAME_COINS]

        # flag tiles
        self.flag_list = self.tile_map.sprite_lists[LAYER_NAME_FLAG]

        # Set background image
        self.background_list = self.tile_map.sprite_lists[LAYER_NAME_BACKGROUND]

        # door tile
        self.door = self.tile_map.sprite_lists[LAYER_NAME_DOOR]

        # Set the position of the background

        # Calculate the drawing position for the background sprite
        background_draw_x = self.tile_map.width*GRID_PIXEL_SIZE / 2
        background_draw_y = self.tile_map.height*GRID_PIXEL_SIZE / 2 # Align top of sprite with top of screen
        self.background_list[0].set_position(background_draw_x, background_draw_y)

        self.end_of_map = self.tile_map.width * GRID_PIXEL_SIZE

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
        
        if self.timer <= 0:
            arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.timeUp)
    

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        # Make sure that we are supposed to be doing updates
        #if self.do_update:
        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            self.jump_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            # Prevents the user from double jumping
            self.jump_key_down = False
            arcade.play_sound(self.jump_sound)
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

        # Make sure that we are supposed to be doing updates
        if self.do_update:
            """Movement and game logic"""
            if self.mario.center_x < self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2:
                self.mario.center_x = self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2
                self.mario.change_x = 0
            
            
            self.frame_counter += 1
            if self.frame_counter > 20:
                self.timer -= 1
                self.frame_counter = 0
            
            
            # Player dies if they fall below the world or run out of time
            if self.mario.center_y < -SPRITE_PIXEL_SIZE:
                self.player_die()
                
        
            # Player movement and physics engine
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            self.physics_engine.update()

            # Update Animations
            if not self.mario_flag:
                self.scene.update_animation(
                    delta_time, [LAYER_NAME_PLAYER, LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS]
                )
            else:
                self.scene.update_animation(
                    delta_time, [LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS]
                )

            # Position the camera
            self.center_camera_to_player()


            # if get to flagpole
            if arcade.check_for_collision_with_list(self.mario, self.flag_list):
                # call animation method
                self.mario_flag = True
            else:
                self.mario_flag = False

            if self.mario_flag:
                self.mario.slidedown_flag()
                self.mario_door = True

            if self.mario_door:
                self.flag_animation()

            self.door_hit = arcade.check_for_collision_with_list(self.mario, self.door)

            if self.door_hit:
                self.mario.visible = False
                

            # See if the coin is hitting a platform
            coin_hit_list = arcade.check_for_collision_with_list(self.mario, self.coin_list)
            

            for coin in coin_hit_list:
                self.do_update = False
                if self.mario.power == 0:
                    self.mario.next_power()
                else:
                    self.mario.prev_power()
                self.coin_count += 1
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.coin_sound)
  
            # Proof of concept of hitting the above block:
            # Testing with breakable blocks first
            height_multiplier = int(self.mario.power > 0) + 1
            
            block_hit_list = arcade.get_sprites_at_point((self.mario.center_x, self.mario.center_y + height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.platform_breakable_list)

            # Later, add a requisite that the mario must be big
            for block in block_hit_list:
                # Perhaps change this to a call to a function that activates some block_break
                # event at the position of each broken block
                # Remove the block
                if self.mario.power > 0:
                    block.remove_from_sprite_lists()
                
                else:
                    # This means Mario is small, bump the block!
                    block.update = 0.1
                    pass
        else:
            if not self.mario_flag:
                # Only update the animation for Mario
                self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER])
                self.do_update = not self.mario.is_growing


    def flag_animation(self):
        if self.mario.center_y > SPRITE_PIXEL_SIZE * TILE_SCALING * 4:
            self.mario.slidedown_flag()
        else:
            if not arcade.check_for_collision_with_list(self.mario, self.door):
                self.mario.walk_to_door()
            else:
                self.mario_door = False


        
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