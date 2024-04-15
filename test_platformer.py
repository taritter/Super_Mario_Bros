"""
Platformer Template
"""
import arcade

import time
import launch
from enemy import Koopa
import random
from mario import Mario
import json
from mystery_box import Mystery_Box
from coin import Coin
from mushroom import Mushroom

# --- Constants
SCREEN_TITLE = "Platformer"

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 600
DEFAULT_FONT_SIZE = 25
INTRO_FRAME_COUNT = 175
SCORE_FRAME_COUNT = 20

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 2.5
TILE_SCALING = 2.5
SPRITE_PIXEL_SIZE = 16
KOOPA_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * TILE_SCALING
NUMBER_OF_COINS = 3

# The gravity that is used by the physics engine
GRAVITY = 0.8

PLAYER_START_X = SPRITE_PIXEL_SIZE * CHARACTER_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 2

LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_PLATFORMS_BREAKABLE = "Platform_Breakable"
LAYER_NAME_MYSTERY_ITEM = "Mystery_Item"
LAYER_NAME_MYSTERY_COIN = "Mystery_Coin"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_FLAG = "Flag"
LAYER_NAME_GOOMBA = "Goomba"
LAYER_NAME_KOOPA = "Koopa"
LAYER_NAME_TELEPORT_EVENT = "Teleport"
LAYER_NAME_DOOR = "Next_Level_Door"
LAYER_NAME_FLAG_BOTTOM = "Flag_Bottom"
LAYER_NAME_MUSHROOM = "Mushroom"

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


        # for level ending
        
        self.mario_door = False
        
        self.mario_flag = False

        self.mario_flag_bottom = False

        self.last_level = False

        self.add_to_score = False

        self.quest_bool = False

        self.no_lives = False

        self.squish_counter = 0

        self.add_num = 0

        # Our physics engine
        self.physics_engine = None

        self.background_list = []

        self.player_list = []
        
        self.goomba_list = []

        self.koopa_list = []

        self.shell_list = []
        
        # -- sounds --
        self.jump_sound = arcade.load_sound("resources/sounds/jump_sound.wav")

        self.coin_sound = arcade.load_sound("resources/sounds/smw_coin.wav")

        self.break_sound = arcade.load_sound("resources/sounds/Break.wav")

        self.bump_sound = arcade.load_sound("resources/sounds/bump.wav")
        
        self.squish_sound = arcade.load_sound("resources/sounds/Squish.wav")

        self.powerup_sound = arcade.load_sound("resources/sounds/powerup.wav")

        self.death_sound = arcade.load_sound("resources/sounds/death.wav")

        self.clear_sound = arcade.load_sound("resources/sounds/clear.wav")

        self.music = arcade.load_sound("resources/sounds/music.wav")
        

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
        self.grab_shell = False

        # different levels
        self.stages = ["1-1", "1-2", "1-3"]
        self.stage_num = self.stages.index(self.stage)
        self.mario_world = self.stages[self.stage_num]
        self.success_map = False

        # background color
        arcade.set_background_color(arcade.color.BLACK)

        # background imags
        
        self.stagestart = arcade.load_texture("resources/backgrounds/supermariostagestart.png")

        self.quest_over = arcade.load_texture("resources/backgrounds/quest_over.png")

        self.timeUp = arcade.load_texture("resources/backgrounds/timeupMario.png")

        self.game_over = arcade.load_texture("resources/backgrounds/game_over.png")


    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        
        # Store the save file, as the player has either died or gotten to
        # a new stage        
        self.save()
        
        self.do_update = False
        self.stage_intro = True
        self.is_defeated = False
        self.end_of_level = False

        # for level ending
        
        self.mario_door = False
        
        self.mario_flag = False

        self.mario_flag_bottom = False

        self.last_level = False
        
        self.do_update = True

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

        # Initialize the set for handling when blocks are nudged
        self.nudged_blocks_list_set = ([],[],[],[],[])
                
        # Reset the frame counter
        self.frame_counter = 0

        # Name of map file to load
        # Can modify this by replacing instances of '1-1' with self.stage
        map_name =  self.next_world()  #"resources/backgrounds/1-1/world_1-1.json" #
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
            LAYER_NAME_GOOMBA: {
                "use_spatial_hash": False,
            },
            LAYER_NAME_KOOPA: {
                "use_spatial_hash": False,
                "custom_class": Koopa
            },
            LAYER_NAME_MUSHROOM: {
                "use_spatial_hash": False,
                "hit_box_algorithm": "None",
                "custom_class": Mushroom
            },
            LAYER_NAME_DOOR: {
                "use_spatial_hash": True,
            },
            LAYER_NAME_FLAG_BOTTOM: {
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
        self.mystery_item_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_ITEM]
        self.mystery_coin_list = self.tile_map.sprite_lists[LAYER_NAME_MYSTERY_COIN]
        
        self.goomba_list = self.tile_map.sprite_lists[LAYER_NAME_GOOMBA]
        self.koopa_list = self.tile_map.sprite_lists[LAYER_NAME_KOOPA]
        
        # Set coins
        self.coin_list = self.tile_map.sprite_lists[LAYER_NAME_COINS]

        # flag tiles
        self.flag_list = self.tile_map.sprite_lists[LAYER_NAME_FLAG]
        self.flag_bottom_list = self.tile_map.sprite_lists[LAYER_NAME_FLAG_BOTTOM]

        # Powerups
        self.mushroom_list = self.tile_map.sprite_lists[LAYER_NAME_MUSHROOM]
        
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
        
        self.scene[LAYER_NAME_GOOMBA]
        self.scene[LAYER_NAME_KOOPA]

        # --- Other stuff
        # Create the 'physics engine'
        walls = [self.platform_list, self.platform_breakable_list, self.mystery_item_list, self.mystery_coin_list]
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.mario, gravity_constant=GRAVITY, walls=walls, platforms=[self.goomba_list, self.koopa_list]
        )
        self.physics_engine_list = []

        self.music_ref = arcade.play_sound(self.music, volume=0.5)
        
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

        if self.timer <= 0:
            arcade.draw_lrwh_rectangle_textured(0, 0,
                                                SCREEN_WIDTH, SCREEN_HEIGHT,
                                                self.timeUp)
            
        elif self.no_lives:
            # no more lives
            arcade.draw_lrwh_rectangle_textured(0, 0,
                                                SCREEN_WIDTH, SCREEN_HEIGHT,
                                                self.game_over)
        
        
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
        
        if self.add_to_score:
            self.frame_counter += 1
            arcade.draw_text(str(self.add_num),
                         self.mario.center_x - 275,
                         self.mario.center_y,
                         arcade.color.WHITE,
                         20,
                         width=SCREEN_WIDTH,
                         align="center",
                         font_name="Kenney Pixel")
            if self.frame_counter > SCORE_FRAME_COUNT:
                self.add_to_score = False
                self.frame_counter = 0        

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
            if self.physics_engine.can_jump:
                arcade.play_sound(self.jump_sound, volume=0.05)
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


        # Grab Shell if big
        elif key == arcade.key.G:
            self.grab_shell = True


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
        
        if self.is_defeated:
            # Only want to shift the guy up and down, then call setup when
            # he's below the screen
            self.frame_counter += 1
            
            # Pause for around 20 frames
            if self.frame_counter > 20:
                # Go up for 20 frames, and then go down
                self.defeated.center_y += (40 - self.frame_counter) / 2           
                
                # Once below the map, reset
                if self.defeated.center_y < -25:
                    self.setup()
                
            return # Early return
        
        # Make sure that we are supposed to be doing updates
        if self.do_update:
            """Movement and game logic"""
            if self.mario.center_x < self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2:
                self.mario.center_x = self.screen_center_x + SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2
                self.mario.change_x = 0
            
            
            self.frame_counter += 1
            if self.frame_counter > 30:
                self.timer -= 1
                self.frame_counter = 0
            
            
            # Player dies if they fall below the world or run out of time
            if self.mario.center_y < -SPRITE_PIXEL_SIZE or self.timer <= 0:
                self.player_die()
            
            self.scene.update([LAYER_NAME_GOOMBA])
            self.scene.update([LAYER_NAME_KOOPA])
            self.scene.update([LAYER_NAME_MUSHROOM])
                
        
            # Player movement and physics engine
            self.mario.update_movement(self.left_key_down, self.right_key_down, self.jump_key_down, self.sprint_key_down, self.physics_engine)
            self.physics_engine.update()
            for engine in self.physics_engine_list:
                engine.update()
                

            if self.stage_num == 3:
                self.last_level = True

            if self.lives <= 0:
                self.no_lives = True

            # Update Animations
            if not self.mario_flag:
                self.scene.update_animation(delta_time,
                                            [LAYER_NAME_PLAYER,
                                             LAYER_NAME_MYSTERY_COIN,
                                             LAYER_NAME_MYSTERY_ITEM,
                                             LAYER_NAME_COINS,
                                             LAYER_NAME_GOOMBA,
                                             LAYER_NAME_KOOPA,
                                             LAYER_NAME_MUSHROOM])

            else:
                self.scene.update_animation(
                    delta_time, [LAYER_NAME_MYSTERY_COIN, LAYER_NAME_MYSTERY_ITEM, LAYER_NAME_COINS, LAYER_NAME_GOOMBA, LAYER_NAME_KOOPA, LAYER_NAME_MUSHROOM]
                )

                self.scene.update_animation(delta_time,
                                            [LAYER_NAME_MYSTERY_COIN,
                                             LAYER_NAME_MYSTERY_ITEM,
                                             LAYER_NAME_COINS])
            # Position the camera
            self.center_camera_to_player()


            # if get to flagpole
            if arcade.check_for_collision_with_list(self.mario, self.flag_list):
                self.mario_flag = True

            else:

                self.mario_flag = False

            # to slide down the flag
            if self.mario_flag and not self.mario_flag_bottom:
                self.mario.slidedown_flag()
                if arcade.check_for_collision_with_list(self.mario, self.flag_bottom_list):
                    self.mario.texture = self.mario.slide_textures[1]
                    self.mario.center_x = self.mario.center_x + SPRITE_PIXEL_SIZE
                    time.sleep(0.5)
                    self.mario_door = True
                    self.mario_flag_bottom = True

            # run to door
            if self.mario_door:
                self.flag_animation()

            self.door_hit = arcade.check_for_collision_with_list(self.mario, self.door)

            if self.door_hit and not self.last_level:
                self.mario.visible = False
            elif not self.door_hit and self.last_level:
                self.quest_bool = True

                
                
            # See if the coin is hitting a platform
            coin_hit_list = arcade.check_for_collision_with_list(self.mario, self.coin_list)
            

            for coin in coin_hit_list:
                self.coin_count += 1
                
                if self.coin_count > 99:
                    self.lives += 1
                    self.coin_count = 0
                
                # Remove the coin
                coin.remove_from_sprite_lists()
                # Play a sound
                arcade.play_sound(self.coin_sound, volume = 2)
                
                
            # Need for both breaking blocks and pipes above/below mario
            self.height_multiplier = int(self.mario.power > 0) + 1
             
            # Proof of concept of hitting the above block:

            """---- this is for KOOPA mario collision -----
            if koopa jumped on turns into shell that mario can collect"""

            # Define the range of x-coordinates
            x_range = range(int(self.mario.center_x) - 16, int(self.mario.center_x) + 17)  # Extend range by 1 to include both end points

            
            # Iterate over each x-coordinate in the range
            for x in x_range:
                new_sprite = False
                # Call get_sprites_at_point for each x-coordinate
                koopa_hit_list = arcade.get_sprites_at_point((x, self.mario.center_y - self.height_multiplier * KOOPA_PIXEL_SIZE * CHARACTER_SCALING / 2 - 2), self.koopa_list)
                for koopa in koopa_hit_list:
                   if self.mario.can_take_damage:
                        walls = [self.platform_list, self.platform_breakable_list, self.mystery_item_list, self.mystery_coin_list]
                        self.physics_engine_list.append(arcade.PhysicsEnginePlatformer(koopa, gravity_constant=GRAVITY, walls=walls))
                        self.frame_counter = 0
                        self.update_score(100)
                        arcade.play_sound(self.squish_sound)
                        enemy_position = koopa.position
                        # creates a new enemy object with the shell instead
                        koopa.remove_from_sprite_lists()
                        k_shell = arcade.Sprite("resources/sprites/koopa_shell.png", CHARACTER_SCALING)
                        k_shell.boundary_left = koopa.boundary_left
                        k_shell.boundary_right = koopa.boundary_right

                        offset_distance = 30
                        if self.mario.change_x >= 0 and not new_sprite:
                            k_shell.position = (self.mario.center_x + offset_distance, self.mario.center_y - 80)
                        elif self.mario.change_x < 0 and not new_sprite:
                            k_shell.position = (self.mario.center_x - offset_distance, self.mario.center_y - 80)

                    k_shell.change_x = 3
                    self.koopa_list.append(k_shell)
                    if k_shell in self.koopa_list:
                        new_sprite = True
                    if self.mario.collides_with_sprite(k_shell):    
                        self.mario.change_y = 3
                        k_shell.remove_from_sprite_lists()
                    # Check for collision with other koopas in the list
                    for koopa in self.koopa_list:
                        if k_shell.collides_with_sprite(koopa) and k_shell != koopa:
                            print("collision with koopa")
                            koopa.remove_from_sprite_lists()
                    for goomba in self.goomba_list:
                        if k_shell.collides_with_sprite(goomba):
                            goomba.change_y = -3
                            #goomba.remove_from_sprite_lists()

            

            """---- this is for GOOMBA collision ----
            if goomba is jumped on changes to squished image"""


            # Define the range of x-coordinates
            x_range = range(int(self.mario.center_x) - 16, int(self.mario.center_x) + 17)  # Extend range by 1 to include both end points
            
            # Iterate over each x-coordinate in the range
            for x in x_range:
                is_squished = False
                # Call get_sprites_at_point for each x-coordinate
                goomba_hit_list = arcade.get_sprites_at_point((x, self.mario.center_y - self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 - 2), self.goomba_list)
                if self.mario.can_take_damage:
                    for goomba in goomba_hit_list:
                        walls = [self.platform_list, self.platform_breakable_list, self.mystery_item_list, self.mystery_coin_list]
                        self.physics_engine_list.append(arcade.PhysicsEnginePlatformer(goomba, gravity_constant=GRAVITY, walls=walls))
                        self.update_score(100)
                        arcade.play_sound(self.squish_sound)
                        # make a animation that displays score
                        enemy_position = goomba.position
                        goomba.remove_from_sprite_lists()
                        squished = arcade.Sprite("resources/sprites/goomba_squish.png", CHARACTER_SCALING)
                        
                        squished.position = enemy_position
                        if self.mario.power == 0 and not is_squished:
                            squished.center_y = self.mario.center_y - 50
                            self.goomba_list.append(squished)
                        elif self.mario.power == 1 and not is_squished:
                            squished.center_y = self.mario.center_y - 70
                            self.goomba_list.append(squished)
                        self.squish_counter += 1
                        if self.squish_counter >= 2:
                            squished.remove_from_sprite_lists()
                            self.squish_counter = 0

                        
            #mushroom kills mario- todo: fix this so jumping on top doesn't kill mario
            mario_glist = arcade.check_for_collision_with_list(self.mario, self.goomba_list) #change ot enemy_hit_list?
            mario_klist = arcade.check_for_collision_with_list(self.mario, self.koopa_list)
            #check if there is anything in the list, if not, 
            if self.mario.can_take_damage:
                print("Damage possible")
                if (mario_glist or mario_klist) and self.mario.power == 0:
                    self.player_die()
                elif (mario_glist or mario_klist) and self.mario.power == 1:
                    self.mario.prev_power()
            else:
                print("INVINCIBLE")
            
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
                    arcade.play_sound(self.break_sound)
                
                else:
                    # This means Mario is small, bump the block!
                    self.nudged_blocks_list_set[4].append(block)
                    arcade.play_sound(self.bump_sound)
                    # Play a sound (change to nudging sound)
                    # arcade.play_sound(self.coin_sound)

            # Git the block list for the left side of mario's head
            mystery_coin_hit_list = arcade.get_sprites_at_point((self.mario.center_x - 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.mystery_coin_list)
            
            # Add to that list the blocks on the right side of mario's head
            mystery_coin_hit_list.extend(arcade.get_sprites_at_point((self.mario.center_x + 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.mystery_coin_list))
            
            # Turn that list into a set to eliminate duplicate values
            mystery_coin_hit_list = set(mystery_coin_hit_list)

            for block in mystery_coin_hit_list:
                if not block.is_hit:
                    self.coin_count += 1
                    block.is_hit = True
                    arcade.play_sound(self.coin_sound, volume = 2)

            # Get the block list for the left side of mario's head
            mystery_item_hit_list = arcade.get_sprites_at_point((self.mario.center_x - 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.mystery_item_list)
            
            # Add to that list the blocks on the right side of mario's head
            mystery_item_hit_list.extend(arcade.get_sprites_at_point((self.mario.center_x + 0.7 * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2, self.mario.center_y + self.height_multiplier * SPRITE_PIXEL_SIZE * CHARACTER_SCALING / 2 + 1), self.mystery_item_list))
            
            # Turn that list into a set to eliminate duplicate values
            mystery_item_hit_list = set(mystery_item_hit_list)

            for box in mystery_item_hit_list:
                if not box.is_hit:
                    box.is_hit = True
                    for shroom in self.mushroom_list:
                        if box.collides_with_sprite(shroom) and not shroom.is_hit: 
                            shroom.is_hit = True
                            walls = [self.platform_list, self.platform_breakable_list, self.mystery_item_list, self.mystery_coin_list]
                            self.physics_engine_list.append(arcade.PhysicsEnginePlatformer(shroom, gravity_constant=GRAVITY, walls=walls))
            
            
            # See if the mario collected a mushroom powerur
            mushroom_hit_list = arcade.check_for_collision_with_list(self.mario, self.mushroom_list)
            
            for shroom in mushroom_hit_list:
                self.mario.next_power()

                # Remove the mushroom
                shroom.remove_from_sprite_lists()

                # Play a sound
                arcade.play_sound(self.powerup_sound, volume = 2)

            self.nudge_blocks()

        else:
            # Only update the animation for Mario
            if not self.mario_flag:
                # Only update the animation for Mario
                self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER])
                self.do_update = not self.mario.is_growing
    
    def update_score(self, score):
        self.score += score
        self.add_num = score
        self.add_to_score = True
        
        
    def is_sprite_on_screen(self, sprite):
        if 0 <= sprite.center_x <= SCREEN_WIDTH and 0 <= sprite.center_y <= SCREEN_HEIGHT:
            return True
        else:
            return False

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
        self.end_of_level = True

        if arcade.Sound.is_playing(self.music_ref, self.music_ref):
            arcade.stop_sound(self.music_ref)
            arcade.play_sound(self.clear_sound)


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
        map_name = f"resources/backgrounds/{self.mario_world}/world_{self.mario_world}.tmx"
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
        
        # Can't die twice in a row
        if self.is_defeated:
            return
        
        self.frame_counter = 0
        self.is_defeated = True
        
        arcade.stop_sound(self.music_ref)

        if not self.end_of_level:
            self.lives -= 1
            arcade.stop_sound(self.music_ref)
            arcade.play_sound(self.death_sound)
        
        
        self.defeated = arcade.Sprite("resources/sprites/mario_defeated.png", CHARACTER_SCALING)
        
        self.defeated.position = self.mario.position
        
        # Make the player invisible
        self.mario.visible = False
        # Add the defeated mario to coins list (bit of a hack to cut down on number of lists)
        self.coin_list.append(self.defeated)
        
        
        # Set the timer and position to be safe, so it is not called again
        self.timer = 10
        self.mario.set_position(0, -2*SCREEN_HEIGHT)
        


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