"""
Platformer Template
"""
import arcade

import time
import launch
import random
from mario import Mario
import json
from enemy import Enemy
from mystery_box import Mystery_Box
from coin import Coin

# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
DEFAULT_FONT_SIZE = 25
INTRO_FRAME_COUNT = 150

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
LAYER_NAME_ENEMIES = "enemies"
LAYER_NAME_TELEPORT_EVENT = "Teleport"
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
        
        self.enemy_list = []
        
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
        self.down_key_down = False
        self.sprint_key_down = False

        # different levels
        self.stages = {1: "1-1", 2: "1-2", 3: "1-3", 4: "1-4", 5: "2-1", 6: "2-2", 7: "2-3", 8: "2-4"}
        self.stage_num = 1
        self.mario_world = self.stages[self.stage_num]
        self.success_map = False

        # background color
        arcade.set_background_color(arcade.color.BLACK)
        
        self.stagestart = arcade.load_texture("resources/backgrounds/supermariostagestart.png")

        

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        
        # Store the save file, as the player has either died or gotten to
        # a new stage        
        self.save()
        
        self.do_update = False
        self.stage_intro = True
        
        self.timer = 300
        self.frame_counter = 0
        
        # Reset the 'center' of the screen to 0
        self.screen_center_x = 0
        self.screen_center_y = 0
        
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)
        
        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)
        
    def setup_part_2(self):
        
        self.do_update = True
        # Initialize the set for handling when blocks are nudged
        self.nudged_blocks_list_set = ([],[],[],[],[])
                
        # Reset the frame counter
        self.frame_counter = 0

        # Name of map file to load
        # Can modify this by replacing instances of '1-1' with self.stage
        map_name = "resources/backgrounds/1-1/world_1-1.json" #self.next_world()  #"resources/backgrounds/1-1/world_1-1_pipe_test.json" #
        # Layer specific options are defined based on Layer names in a dictionary
        # Doing this will make the SpriteList for the platforms layer
        # use spatial hashing for detection.
        layer_options = {

            LAYER_NAME_TELEPORT_EVENT: {
                "use_spatial_hash": True,
                },
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
            LAYER_NAME_ENEMIES: {
                "use_spatial_hash": True,
                "enemies": {
                    "custom_class": Enemy
                },
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
        
        self.enemy_list = self.tile_map.sprite_lists[LAYER_NAME_ENEMIES]
        
        # Set coins
        self.coin_list = self.tile_map.sprite_lists[LAYER_NAME_COINS]

        # flag tiles
        self.flag_list = self.tile_map.sprite_lists[LAYER_NAME_FLAG]
        
        # teleport locations
        full_teleport_list = self.tile_map.object_lists[LAYER_NAME_TELEPORT_EVENT]
        
        self.teleport_enter_list = []
        self.teleport_exit_list = []
        
        for teleporter in full_teleport_list:
            if "enter" in teleporter.name:
                self.teleport_enter_list.append(teleporter)
            else:
                self.teleport_exit_list.append(teleporter)
        
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
        
        self.success_map = False


    def on_draw(self):
        """Render the screen."""
        # Clear the screen to the background color
        self.clear()
        
        # Activate our Camera
        self.camera.use()
        
        if self.stage_intro:
            
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.stagestart)
            
            draw_string = f"WORLD  {self.stage}\n\n\t\t{self.lives}"
            
            self.draw_text()
            
            arcade.draw_text(draw_string,
                             self.screen_center_x,
                             self.screen_center_y + SCREEN_HEIGHT/2 + 3*DEFAULT_FONT_SIZE,
                             arcade.color.WHITE,
                             DEFAULT_FONT_SIZE * 1.5,
                             multiline = True,
                             width=SCREEN_WIDTH,
                             align="center",
                             font_name="Kenney Pixel")
            
            return
        
        
        # Draw our Scene
        # Draw the platforms
        self.scene.draw(pixelated=True)
        # Draw the player
        self.mario.draw(pixelated=True)
        
        self.draw_text()
        
    def draw_text(self):
        # Draw the text last, so it goes on top
        # Have to squeeze everything into one text draw, otherwise major lag
        draw_string = f"MARIO \t\t COINS \t\t WORLD \t\t TIME \n{self.score:06d}  \t\t {self.coin_count:02d} \t\t\t   {self.mario_world} \t\t {self.timer:03d}"
        
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
        if self.stage_intro:
            return
        
        # Jump
        if key == arcade.key.UP or key == arcade.key.W:
            self.jump_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            # Prevents the user from double jumping
            self.jump_key_down = False
            arcade.play_sound(self.jump_sound)
            self.enter_pipe("up")
            
        # Left
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            
            self.enter_pipe("left")
            
        # Right
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            
            self.enter_pipe("right")
            
        # Down
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_key_down = True
            
            self.enter_pipe("down")
            
        # Sprint
        elif key == arcade.key.J:
            self.sprint_key_down = True
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            
        # Reset
        elif key == arcade.key.ESCAPE:
            self.player_die()


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_key_down = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_key_down = False
        elif key == arcade.key.J:
            self.sprint_key_down = False


    def enter_pipe(self, direction):
        "Called for each directional key press, check if there is a pipe to enter, and enter it"
        # Pipe Collision
        for teleporter in self.teleport_enter_list:
            if direction in teleporter.name:
                if direction in ["up","down"]:
                    # TODO: fix vertical checks
                    # Need horizontal checks
                    right_of_pipe = self.mario.center_x > teleporter.shape[0][0] * TILE_SCALING
                    left_of_pipe = self.mario.center_x < teleporter.shape[2][0] * TILE_SCALING
                     
                    if direction == "down":
                        height_check_below = self.mario.center_y - self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 5
                        in_pipe_vertical_zone = height_check_below < SCREEN_HEIGHT + teleporter.shape[0][1] * TILE_SCALING
                    else:
                        # direction will be "up"
                        height_check_above = self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 5
                        in_pipe_vertical_zone = height_check_above > SCREEN_HEIGHT + teleporter.shape[2][1] * TILE_SCALING
                        
                    
                    if right_of_pipe and left_of_pipe and in_pipe_vertical_zone:
                        # All conditions met, go throught the pipe
                        self.exit_pipe(teleporter.name[:2])
                        return
                 
                elif direction in ["right","left"]:
                    # Need vertical checks
                    above_pipe = self.mario.center_y > SCREEN_HEIGHT + teleporter.shape[2][1] * TILE_SCALING
                    below_pipe = self.mario.center_y < SCREEN_HEIGHT + teleporter.shape[0][1] * TILE_SCALING
                    
                    # Check to see that the 'activator' pixel is within the left/right bounds
                    if direction == "left":
                        right_of_pipe = self.mario.center_x - SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 5 > teleporter.shape[0][0] * TILE_SCALING
                        left_of_pipe = self.mario.center_x - SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 5 < teleporter.shape[2][0] * TILE_SCALING
                        
                    else:
                        right_of_pipe = self.mario.center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 5 > teleporter.shape[0][0] * TILE_SCALING
                        left_of_pipe = self.mario.center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 5 < teleporter.shape[2][0] * TILE_SCALING
                     
                    if above_pipe and below_pipe and right_of_pipe and left_of_pipe:
                        self.exit_pipe(teleporter.name[:2])
                        return
                     
            
    def exit_pipe(self, teleport_id):
        # TODO: refigure to set the camera so that mario is on the far left
        # Find output pipe position
        for teleporter_output in self.teleport_exit_list:
            # If the identifier characters are present, thats the pair
            if teleport_id in teleporter_output.name:
                # Note, in actuality one version would be needed for each direction
                # as with enter_pipe
                # However, in the interest of time, I won't do that
                
                self.mario.center_x = teleporter_output.shape[2][0] * TILE_SCALING
                self.mario.center_y = SCREEN_HEIGHT + teleporter_output.shape[0][1] * TILE_SCALING
                
                self.screen_center_x = 0
                self.screen_center_y = 0
                # self.camera.move_to((self.screen_center_x, self.screen_center_y))
        

    def center_camera_to_player(self):
        if (self.mario.center_x - (self.camera.viewport_width / 3)) > self.screen_center_x:
            self.screen_center_x = self.mario.center_x - (self.camera.viewport_width / 3)

        # Don't let camera travel past 0
        if self.screen_center_x < 0:
            self.screen_center_x = 0

        player_centered = self.screen_center_x, self.screen_center_y

        self.camera.move_to(player_centered)

    def on_update(self, delta_time):

        # Only display the intro during the intro
        if self.stage_intro:
            self.frame_counter += 1
            
            if self.frame_counter == INTRO_FRAME_COUNT or self.success_map:
                self.stage_intro = False
                self.setup_part_2()
                
            return # Early return
        
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
            if self.mario.center_y < -SPRITE_PIXEL_SIZE:# or self.timer <= 0:
                self.player_die()
            

            # Player movement and physics engine
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            self.physics_engine.update()

            # Update Animations
            if not self.mario_flag:

                self.scene.update_animation(delta_time,
                                            [LAYER_NAME_PLAYER,
                                             LAYER_NAME_MYSTERY_COIN,
                                             LAYER_NAME_MYSTERY_ITEM,
                                             LAYER_NAME_COINS,
                                             LAYER_NAME_ENEMIES])

            else:

                self.scene.update_animation(delta_time,
                                            [LAYER_NAME_MYSTERY_COIN,
                                             LAYER_NAME_MYSTERY_ITEM,
                                             LAYER_NAME_COINS])
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
                
                if self.coin_count > 99:
                    self.lives += 1
                    self.coin_count = 0
                
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.coin_sound)
                
                
            # Need for both breaking blocks and pipes above/below mario
            self.height_multiplier = int(self.mario.power > 0) + 1
             
            # Proof of concept of hitting the above block:
            # Testing with breakable blocks first

            self.height_multiplier = int(self.mario.power > 0) + 1

            """--- this is for enemy mario collision"""

            # Define the range of x-coordinates
            x_range = range(int(self.mario.center_x) - 16, int(self.mario.center_x) + 17)  # Extend range by 1 to include both end points

            # Iterate over each x-coordinate in the range
            for x in x_range:
                # Call get_sprites_at_point for each x-coordinate
                enemy_hit_list = arcade.get_sprites_at_point((x, self.mario.center_y - self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 2), self.enemy_list)
                for enemy in enemy_hit_list:
                    #todo: at the position where the enemy was, put in the new sprite #get_sprite_at_point
                    enemy.remove_from_sprite_lists()

            #mushroom kills mario- todo: fix this so jumping on top doesn't kill mario
            mario_list = arcade.check_for_collision_with_list(self.mario, self.enemy_list) #change ot enemy_hit_list?
            #check if there is anything in the list, if not, 
            if mario_list:
                self.player_die()
            
            
            # Note that the multiplier for getting either side of mario's head (0.7)
            # Is just barely smaller than it needs to be - it is possible to
            # hit the block without it being added to the hit list
            # However, increasing the value to 0.75 is just barely too much,
            # and it is possible to hit a block from the side
            
            
            # Git the block list for the left side of mario's head
            block_hit_list = arcade.get_sprites_at_point((self.mario.center_x - 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.platform_breakable_list)
            
            # Add to that list the blocks on the right side of mario's head
            block_hit_list.extend(arcade.get_sprites_at_point((self.mario.center_x + 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.platform_breakable_list))
            
            # Turn that list into a set to eliminate duplicate values
            block_hit_list = set(block_hit_list)
            # Later, add a requisite that the mario must be big
            for block in block_hit_list:
                # Perhaps change this to a call to a function that activates some block_break
                # event at the position of each broken block
                # Remove the block
                if self.mario.power > 0:
                    block.remove_from_sprite_lists()
                    # Play a sound (change to breaking sound)
                    # arcade.play_sound(self.coin_sound)
                
                else:
                    # This means Mario is small, bump the block!
                    self.nudged_blocks_list_set[4].append(block)
                    # Play a sound (change to nudging sound)
                    # arcade.play_sound(self.coin_sound)
            
            
            self.nudge_blocks()

        else:
            # Only update the animation for Mario
            if not self.mario_flag:
                # Only update the animation for Mario
                self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER])
                self.do_update = not self.mario.is_growing

    def nudge_blocks(self):
        # On every few frames, allow the nudged blocks to move
        if self.frame_counter % 3 == 0:
            temp_nudged_blocks_list_set = ([],[],[],[],[])
            for list_id, nudged_block_list in enumerate(self.nudged_blocks_list_set):
                for block in nudged_block_list:
                    # Add the index of the list the block is in, centered around
                    # the middle list (by subtracting the length less 1, over 2)
                    # This achieves the effect of going up and down in equal amounts
                    # The multiplication gives a larger magnitude to the effect
                    block.center_y += (list_id - 2) * 2
                    
                    # If the block is not in the final (lowest)
                    if list_id-1 >= 0:
                        # Put the block in a lower list
                        temp_nudged_blocks_list_set[list_id-1].append(block)
                    # Otherwise, do not put the block back in any nudging list
                    
                self.nudged_blocks_list_set = temp_nudged_blocks_list_set
    
    def flag_animation(self):
        if self.mario.center_y > SPRITE_PIXEL_SIZE * TILE_SCALING * 4:
            self.mario.slidedown_flag()
        else:
            if not arcade.check_for_collision_with_list(self.mario, self.door):
                self.mario.walk_to_door()
            else:
                self.mario_door = False
                self.stage_num += 1
                self.next_world()
                self.setup_part_2()


    def next_world(self):
        # Name of map file to load
        self.mario_world = self.stages[self.stage_num]
        print("stage is: ", self.mario_world)
        map_name = f"resources/backgrounds/{self.mario_world}/world_{self.mario_world}.tmj"
        self.success_map = True
        self.stage = self.mario_world
        return map_name        
        
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
        
        # Set the timer and position to be safe, so it is not called again
        self.timer = 10
        self.mario.set_position(0, 2*SCREEN_HEIGHT)
        
        # For later, give a game over screen if lives reduced to zero (>0 can be infinite)
        # Ideally, also reset the save file to a default version (save_0.json)
        if self.lives == 0:
            pass
        
        
        # Reset the stage
        self.setup()


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