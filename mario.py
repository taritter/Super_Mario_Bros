import arcade
from load_textures import load_texture_pair

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Constants used to track if the player is sprinting
WALKING = 0
SPRINTING = 1

# Constants to check if the player is sliding
NOT_SLIDING = 0
SLIDING = 1

# Constants to track if the player is small or large
SMALL = 0
LARGE = 1

# Constants to track if the player has the fire powerup
NO_POWERUP = 0
POWERUP = 1

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 4
PLAYER_SPRINT_SPEED = 8
PLAYER_ACCELERATION = 0.2
PLAYER_FRICTION = 0.35
PLAYER_JUMP_SPEED = 18

class Mario(arcade.Sprite):
    """Player Sprite"""

    def __init__(self, scale):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = scale

        # Track our state
        self.sprinting = WALKING
        self.sliding = NOT_SLIDING

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = "resources/sprites/"

        # Load textures for idle standing
        self.small_idle_texture_pair = load_texture_pair(f"{main_path}mario_small_idle.png")

        # Load textures for jumping
        self.small_jump_texture_pair = load_texture_pair(f"{main_path}mario_small_jump.png")

        # Load textures for sliding
        self.small_slide_texture_pair = load_texture_pair(f"{main_path}mario_small_slide.png")

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

    def update_movement(self, left_key_down, right_key_down, jump_key_down, sprint_key_down, physics_engine):
        # Jump if the up key is pressed
        if jump_key_down:
            if physics_engine.can_jump():
                self.change_y = PLAYER_JUMP_SPEED

        # Calculate speed based on the keys pressed
        if left_key_down and not right_key_down:
            if self.change_x > 0:
                self.sliding = SLIDING
            else:
                self.sliding = NOT_SLIDING
            if sprint_key_down:
                self.sprinting = SPRINTING
                if self.change_x > -PLAYER_SPRINT_SPEED:
                    if self.sliding:
                        self.change_x -= PLAYER_FRICTION
                    else:
                        self.change_x -= PLAYER_ACCELERATION
                elif self.change_x < PLAYER_SPRINT_SPEED:
                    self.change_x = -PLAYER_SPRINT_SPEED
            else:
                self.sprinting = WALKING
                if self.change_x > -PLAYER_MOVEMENT_SPEED:
                    if self.sliding:
                        self.change_x -= PLAYER_FRICTION
                    else:
                        self.change_x -= PLAYER_ACCELERATION
                elif self.change_x < -PLAYER_MOVEMENT_SPEED:
                    if self.change_x < -PLAYER_SPRINT_SPEED:
                        self.change_x = -PLAYER_SPRINT_SPEED
                    self.change_x += PLAYER_FRICTION
        elif right_key_down and not left_key_down:
            if self.change_x < 0:
                self.sliding = SLIDING
            else:
                self.sliding = NOT_SLIDING
            if sprint_key_down:
                self.sprinting = SPRINTING
                if self.change_x < PLAYER_SPRINT_SPEED:
                    if self.sliding:
                        self.change_x += PLAYER_FRICTION
                    else:
                        self.change_x += PLAYER_ACCELERATION
                elif self.change_x > PLAYER_SPRINT_SPEED:
                    self.change_x = PLAYER_SPRINT_SPEED
            else:
                self.sprinting = WALKING
                if self.change_x < PLAYER_MOVEMENT_SPEED:
                    if self.sliding:
                        self.change_x += PLAYER_FRICTION
                    else:
                        self.change_x += PLAYER_ACCELERATION
                elif self.change_x > PLAYER_MOVEMENT_SPEED:
                    if self.change_x > PLAYER_SPRINT_SPEED:
                        self.change_x = PLAYER_SPRINT_SPEED
                    self.change_x -= PLAYER_FRICTION
        elif self.change_x != 0:
            self.sprinting = WALKING
            self.sliding = NOT_SLIDING
            if self.change_x > 0:
                if self.change_x > PLAYER_FRICTION:
                    self.change_x -= PLAYER_FRICTION
                else:
                    self.change_x = 0
            elif self.change_x < 0:
                if self.change_x < -PLAYER_FRICTION:
                    self.change_x += PLAYER_FRICTION
                else:
                    self.change_x = 0

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

        if self.sliding == SLIDING:
            self.texture = self.small_slide_texture_pair[self.character_face_direction]
            return

        # Walking and sprinting animation
        if self.sprinting:
            if self.update_counter >= 3:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
                self.update_counter = 0
        else:
            if self.update_counter >= 5:
                self.cur_texture += 1
                if self.cur_texture > 2:
                    self.cur_texture = 0
                self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
                self.update_counter = 0
        
        # Update our counter
        self.update_counter += 1