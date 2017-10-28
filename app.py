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


class ViewPanel(BoxLayout):
    scene = ObjectProperty(None)

    def create_data(self):
        _, _, self.data = fractal.julia_set(
            -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 800, 256)
        palette = fractal.create_palette()
        self.apply_palette(palette)

    def set_data(self, data):
        self.data = data

    def apply_palette(self, palette):
        image = fractal.create_image(self.data, palette)
        self.scene.texture = Texture.create(size=image.size)
        self.scene.texture.blit_buffer(image.tobytes())
        self.scene.texture.flip_vertical()


class ColorPanel(BoxLayout):
    hue = ObjectProperty(None)
    saturation = ObjectProperty(None)
    brightness = ObjectProperty(None)
    palette_image = ObjectProperty(None)

    def update(self):
        self.palette = fractal.create_palette({
            'hue': {
                'range': [
                    self.hue.begin,
                    self.hue.end
                ],
                'easing': self.hue.easing
            },
            'saturation': {
                'range': [
                    self.saturation.begin,
                    self.saturation.end
                ],
                'easing': self.saturation.easing
            },
            'brightness': {
                'range': [
                    self.brightness.begin,
                    self.brightness.end
                ],
                'easing': self.brightness.easing
            }
        })
        image = fractal.image_of_palette(self.palette)
        self.palette_image.texture = Texture.create(size=image.size)
        self.palette_image.texture.blit_buffer(image.tobytes())
        self.palette_image.texture.flip_vertical()
        Clock.schedule_once(lambda dt: self.parent.update())


class ControlPanel(BoxLayout):

    def calculate(self):
        Clock.schedule_once(lambda dt: self.parent.update())

    def reset(self):
        Clock.schedule_once(lambda dt: self.parent.update())

    def save(self):
        Clock.schedule_once(lambda dt: self.parent.update())


class FractalViewer(BoxLayout):
    view_panel = ObjectProperty(None)
    control_panel = ObjectProperty(None)
    color_panel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view_panel.create_data()

    def update(self):
        self.view_panel.apply_palette(self.color_panel.palette)


class FractalViewerApp(App):

    def build(self):
        return FractalViewer()


if __name__ == '__main__':
    from kivy.config import Config
    import kivy.resources
    Config.set('graphics', 'width', 1080)
    Config.set('graphics', 'height', 720)
    kivy.resources.resource_add_path(resourcePath())
    FractalViewerApp().run()
