from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
import time
import os
import sys
import fractal
from models import FractalModel


def resourcePath():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))


class ViewPanel(BoxLayout):
    ctrl = ObjectProperty()
    scene = ObjectProperty()

    def set_image(self, image):
        self.scene.texture = Texture.create(size=image.size)
        self.scene.texture.blit_buffer(image.tobytes())
        self.scene.texture.flip_vertical()

    def touch_down(self, touch):
        x, y = touch.pos[0], touch.pos[1]
        if not self.collide_point(x, y) or touch.button != 'left':
            return
        x = (x - self.scene.offset_x) / self.scene.norm_image_size[0]
        y = 1 - (y - self.scene.offset_y) / self.scene.norm_image_size[1]
        self.ctrl.set_center(x, y)


class ColorPanel(BoxLayout):
    ctrl = ObjectProperty()

    def set_palette(self, image):
        self.palette_image.texture = Texture.create(size=image.size)
        self.palette_image.texture.blit_buffer(image.tobytes())
        self.palette_image.texture.flip_vertical()


class FractalPanel(BoxLayout):
    ctrl = ObjectProperty()

    def set_processing_time(self, t):
        self.processing_time.param = t

    def set_mag_rate(self, mr):
        self.mag_rate.param = mr


class FractalViewer(BoxLayout):
    model = FractalModel()
    disabled_calc = True

    view_panel = ObjectProperty()
    fractal_panel = ObjectProperty()
    color_panel = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view_panel.ctrl = self
        self.fractal_panel.ctrl = self
        self.color_panel.ctrl = self
        self.initialize()
        self.update_color()
        self.calculate()

    def initialize(self):
        self.fractal_panel.center_pos.param_x = self.model.center_pos[0]
        self.fractal_panel.center_pos.param_y = self.model.center_pos[1]
        self.fractal_panel.constant.param_x = self.model.constant[0]
        self.fractal_panel.constant.param_y = self.model.constant[1]
        self.fractal_panel.image_size.param = self.model.size
        self.fractal_panel.steps.param = self.model.steps
        self.fractal_panel.zoom_rate.param = self.model.zoom
        self.fractal_panel.mag_rate.param = self.model.mag_rate

        self.color_panel.hue.easing = self.model.hue['easing']
        self.color_panel.hue.begin = self.model.hue['range'][0]
        self.color_panel.hue.end = self.model.hue['range'][1]
        self.color_panel.saturation.easing = self.model.saturation['easing']
        self.color_panel.saturation.begin = self.model.saturation['range'][0]
        self.color_panel.saturation.end = self.model.saturation['range'][1]
        self.color_panel.brightness.easing = self.model.brightness['easing']
        self.color_panel.brightness.begin = self.model.brightness['range'][0]
        self.color_panel.brightness.end = self.model.brightness['range'][1]
        self.disabled_calc = False

    def update_color(self):
        if self.disabled_calc:
            return
        self.model.set_hue(
            self.color_panel.hue.easing,
            self.color_panel.hue.begin,
            self.color_panel.hue.end
        )
        self.model.set_saturation(
            self.color_panel.saturation.easing,
            self.color_panel.saturation.begin,
            self.color_panel.saturation.end
        )
        self.model.set_brightness(
            self.color_panel.brightness.easing,
            self.color_panel.brightness.begin,
            self.color_panel.brightness.end
        )
        self.model.create_palette()
        self.view_panel.set_image(self.model.to_image())
        self.color_panel.set_palette(self.model.to_palette_image())

    def set_center(self, x, y):
        x, y = self.model.get_center_from_normalized(x, y)
        self.fractal_panel.center_pos.param_x = x
        self.fractal_panel.center_pos.param_y = y

    def calculate(self):
        if self.disabled_calc:
            return
        start = time.time()
        self.model.set_fractal_type(self.fractal_panel.fractal_type)
        x = self.fractal_panel.center_pos.param_x
        y = self.fractal_panel.center_pos.param_y
        self.model.set_center_pos(x, y)
        x = self.fractal_panel.constant.param_x
        y = self.fractal_panel.constant.param_y
        self.model.set_constant(x, y)
        self.model.set_size(self.fractal_panel.image_size.param)
        self.model.set_steps(self.fractal_panel.steps.param)
        self.model.set_zoom(self.fractal_panel.zoom_rate.param)
        self.model.create_data()
        elapsed_time = time.time() - start
        self.view_panel.set_image(self.model.to_image())
        self.fractal_panel.set_processing_time(elapsed_time)
        self.fractal_panel.set_mag_rate(self.model.mag_rate)

    def save(self):
        fractal_type = self.model.fractal_type
        filename = '{}.png'.format(fractal_type)
        index = 1
        while os.path.isfile(filename):
            filename = filename.split('.')
            filename[0] = '{}({})'.format(fractal_type, index)
            filename = '.'.join(filename)
            index += 1
        image = self.model.to_image()
        image.save(filename)


class FractalViewerApp(App):

    def build(self):
        self.icon = 'fractal.png'
        return FractalViewer()


if __name__ == '__main__':
    from kivy.config import Config
    import kivy.resources
    Config.set('graphics', 'width', 1080)
    Config.set('graphics', 'height', 720)
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    kivy.resources.resource_add_path(resourcePath())
    FractalViewerApp().run()
