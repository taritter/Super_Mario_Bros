import arcade

# Constant used for the pixel height of a tile
TILE_HEIGHT = 16

# Movement speed of mushroom, in pixels per frame
MUSHROOM_MOVEMENT_SPEED = 2

class Mushroom(arcade.Sprite):
    def __init__(
        self,
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
    ):

        # Set up parent class
        super().__init__(
            filename=filename,
            scale=scale,
            image_x=image_x,
            image_y=image_y,
            image_width=image_width,
            image_height=image_height,
            center_x=center_x,
            center_y=center_y,
        )

        self.is_hit = False
        self.in_box = True

        self.scale = scale
        
        self.out_of_box_y = 0

        self.update_counter = 0

        self.hit_box = self.texture.hit_box_points

        self.direction = 1

        self.prev_x = 0

    def update(self):
        if self.out_of_box_y == 0:
            self.out_of_box_y = self.center_y + self.scale * TILE_HEIGHT
            self.prev_x = self.center_x
        print(self.is_hit)
        print(self.center_y)
        print(self.out_of_box_y)
        print(self.change_x)
        print(self.boundary_right)
        if self.is_hit and self.in_box:
            self.change_y = self.scale * TILE_HEIGHT / 16
            if self.center_y >= self.out_of_box_y:
                self.center_y = self.out_of_box_y
                self.change_x = MUSHROOM_MOVEMENT_SPEED
                self.in_box = False
        elif not self.is_hit:
            self.change_x = 0
            self.change_y = 0
        else:
            if abs(self.center_x - self.prev_x) < 0.1:
                self.direction = self.direction * -1
            self.change_x = self.direction * MUSHROOM_MOVEMENT_SPEED
            self.prev_x = self.center_x
        
        self.update_counter += 1

        # Reset counter to prevent overflow
        if self.update_counter >= 1000:
            self.update_counter = 0