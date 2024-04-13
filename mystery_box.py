import arcade

class Mystery_Box(arcade.Sprite):
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

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = scale

        # --- Load Textures ---
        main_path = "resources/sprites/"

        self.box_textures = []
        for i in range(1, 6):
            texture = arcade.load_texture(f"{main_path}mystery_{i}.png")
            self.box_textures.append(texture)

        # Set the initial texture
        self.texture = self.box_textures[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

        self.is_hit = False

        self.update_counter = 0

    def update_animation(self, delta_time: float = 1 / 60):
        
        if not self.is_hit:
            if self.update_counter >= 5 and self.update_counter <= 15:
                if self.cur_texture == 0:
                    self.update_counter += 1
                    return
                self.cur_texture += 1
                if self.cur_texture > 3:
                    self.cur_texture = 0
                self.texture = self.box_textures[self.cur_texture]
                self.update_counter = 0
            elif self.update_counter > 15:
                self.cur_texture += 1
                if self.cur_texture > 3:
                    self.cur_texture = 0
                self.texture = self.box_textures[self.cur_texture]
                self.update_counter = 0
        else:
            self.cur_texture = 4
            self.texture = self.box_textures[self.cur_texture]
        
        # Update our counter
        self.update_counter += 1