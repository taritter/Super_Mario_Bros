import arcade 
import test_platformer as main
import arcade.gui

SCREEN_TITLE = "Launch"
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

class Title_Screen(arcade.View):
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        self.ui = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.widgets.UIBoxLayout(space_between=20)

        one_player = arcade.gui.UIFlatButton(text="1 PLAYER GAME", width=150)
        two_player = arcade.gui.UIFlatButton(text="2 PLAYER GAME", width=150)

        self.v_box.add(one_player)
        self.v_box.add(two_player)


    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        #self.clear()
        arcade.draw_text("Start Game", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")


    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        arcade.close_window()


        game_view = main.MyGame()
        game_view.setup()
        arcade.set_window(game_view)
        arcade.run()
