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

    def set_image(self, image):
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
        xmin = -1.5 / self.scale.param + self.center_position.param_x
        xmax = 1.5 / self.scale.param + self.center_position.param_x
        ymin = -1.5 / self.scale.param + self.center_position.param_y
        ymax = 1.5 / self.scale.param + self.center_position.param_y
        if self.fractal_type == 'julia':
            _, _, self.data = fractal.julia_set(
                xmin, xmax, ymin, ymax,
                self.constant.param_x, self.constant.param_y,
                self.image_size.param, self.steps.param)
        elif self.fractal_type == 'mandelbrot':
            _, _, self.data = fractal.mandelbrot_set(
                xmin, xmax, ymin, ymax,
                self.image_size.param, self.steps.param)
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
        self.control_panel.calculate()

    def update(self):
        if self.control_panel.data is None:
            return
        elif self.color_panel.palette is None:
            return
        image = fractal.create_image(
            self.control_panel.data,
            self.color_panel.palette)
        self.view_panel.set_image(image)


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
