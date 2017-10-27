from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
import fractal


def resourcePath():
    import os
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))


class Display(BoxLayout):

    def create_data(self):
        _, _, self.data = fractal.julia_set(
            -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 800, 800
        )
        palette = fractal.create_palette()
        self.update_image(palette)

    def update_image(self, palette):
        image = fractal.create_image(self.data, palette)
        self.scene.texture = Texture.create(size=image.size)
        self.scene.texture.blit_buffer(image.tobytes())
        self.scene.texture.flip_vertical()


class ColorContent(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = fractal.Easing.MethodList()

    def to_dict(self):
        result = {
            'range': [self.begin, self.end],
            'easing': self.easing
        }
        return result

    def change_easing(self, value):
        if value == 'Fixed':
            self.end_slider.disabled = True
        else:
            self.end_slider.disabled = False
        self.easing = value
        self.parent.update()

    def change_begin(self, value):
        self.begin = value
        self.parent.update()

    def change_end(self, value):
        self.end = value
        self.parent.update()


class ColorPanel(BoxLayout):
    hue = ObjectProperty(None)
    saturation = ObjectProperty(None)
    brightness = ObjectProperty(None)
    palette_image = ObjectProperty(None)

    def update(self):
        self.palette = fractal.create_palette({
            'hue': self.hue.to_dict(),
            'saturation': self.saturation.to_dict(),
            'brightness': self.brightness.to_dict()
        })
        image = fractal.image_of_palette(self.palette)
        self.palette_image.texture = Texture.create(size=image.size)
        self.palette_image.texture.blit_buffer(image.tobytes())
        self.palette_image.texture.flip_vertical()
        Clock.schedule_once(lambda dt: self.parent.update_image())

    def apply(self):
        self.parent.update_image()


class MainScreen(GridLayout):
    display = ObjectProperty(None)
    color_panel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.display.create_data()

    def update_image(self):
        self.display.update_image(self.color_panel.palette)


class FractalViewerApp(App):

    def build(self):
        return MainScreen()


if __name__ == '__main__':
    from kivy.config import Config
    import kivy.resources
    Config.set('graphics', 'width', 1280)
    Config.set('graphics', 'height', 720)
    kivy.resources.resource_add_path(resourcePath())
    FractalViewerApp().run()
