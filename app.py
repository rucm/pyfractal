from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color
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

    rect_size = 0.0
    rect = None
    center = [0.0, 0.0]

    def set_image(self, image):
        self.scene.texture = Texture.create(size=image.size)
        self.scene.texture.blit_buffer(image.tobytes())
        self.scene.texture.flip_vertical()

    def touch_down(self, touch):
        self.center = touch.pos
        if not self.collide_point(*self.center) or touch.button != 'left':
            return
        with self.canvas:
            Color(0.0, 0.5, 1.0, 0.3)
            self.rect = Rectangle(size=(0, 0), pos=self.center)

    def touch_move(self, touch):
        if touch.button != 'left' or self.rect is None:
            return
        pos = touch.pos
        dif = pos[0] - self.center[0]
        self.rect.pos = (self.center[0] - dif, self.center[1] - dif)
        self.rect_size = dif * 2
        self.rect.size = (self.rect_size, self.rect_size)

    def touch_up(self, touch):
        if touch.button != 'left' or self.rect is None:
            return
        self.canvas.remove(self.rect)
        self.rect = None
        zoom = self.rect_size / self.scene.norm_image_size[0]
        zoom = zoom if zoom > 0.0 else 1.0
        x, y = self.center[0], self.center[1]
        x = (x - self.scene.offset_x) / self.scene.norm_image_size[0]
        y = 1 - (y - self.scene.offset_y) / self.scene.norm_image_size[1]
        self.ctrl.set_new_area(x, y, 1.0 / zoom)


class ColorPanel(BoxLayout):
    ctrl = ObjectProperty()

    def set_palette(self, image):
        self.palette_image.texture = Texture.create(size=image.size)
        self.palette_image.texture.blit_buffer(image.tobytes())
        self.palette_image.texture.flip_vertical()

    def set_param(self, model):
        pass

    def set_hue(self, hue):
        self.hue.easing = hue['easing']
        self.hue.begin = hue['range'][0]
        self.hue.end = hue['range'][1]

    def set_saturation(self, saturation):
        self.saturation.easing = saturation['easing']
        self.saturation.begin = saturation['range'][0]
        self.saturation.end = saturation['range'][1]

    def set_brightness(self, brightness):
        self.brightness.easing = brightness['easing']
        self.brightness.begin = brightness['range'][0]
        self.brightness.end = brightness['range'][1]


class FractalPanel(BoxLayout):
    ctrl = ObjectProperty()

    def set_processing_time(self, t):
        self.processing_time.param = t

    def set_param(self, model):
        self.fractal_type = model.fractal_type
        self.center_pos.param = model.center_pos
        self.constant.param = model.constant
        self.image_size.param = model.size
        self.steps.param = model.steps
        self.zoom.param = model.zoom


class FractalViewer(BoxLayout):
    model = FractalModel()
    calc_ready = False

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
        self.fractal_panel.set_param(self.model)
        # self.color_panel.set_hue(self.model.hue)
        # self.color_panel.set_saturation(self.model.saturation)
        # self.color_panel.set_brightness(self.model.brightness)
        self.calc_ready = True

    def update_color(self):
        if not self.calc_ready:
            return
        self.model.hue = self.color_panel.hue
        self.model.saturation = self.color_panel.saturation
        self.model.brightness = self.color_panel.brightness
        print('test')
        # self.model.set_hue(
        #     self.color_panel.hue.easing,
        #     self.color_panel.hue.begin,
        #     self.color_panel.hue.end
        # )
        # self.model.set_saturation(
        #     self.color_panel.saturation.easing,
        #     self.color_panel.saturation.begin,
        #     self.color_panel.saturation.end
        # )
        # self.model.set_brightness(
        #     self.color_panel.brightness.easing,
        #     self.color_panel.brightness.begin,
        #     self.color_panel.brightness.end
        # )
        self.model.create_palette()
        self.view_panel.set_image(self.model.to_image())
        self.color_panel.set_palette(self.model.to_palette_image())

    def set_new_area(self, x, y, zoom):
        center = self.model.get_center_from_normalized(x, y)
        self.fractal_panel.zoom.param = self.model.zoom * zoom
        self.fractal_panel.center_pos.param = center

    def calculate(self):
        if not self.calc_ready:
            return
        start = time.time()
        self.model.set_fractal_type(self.fractal_panel.fractal_type)
        self.model.set_center_pos(*self.fractal_panel.center_pos.param)
        self.model.set_constant(*self.fractal_panel.constant.param)
        self.model.set_size(self.fractal_panel.image_size.param)
        self.model.set_steps(self.fractal_panel.steps.param)
        self.model.set_zoom(self.fractal_panel.zoom.param)
        self.model.create_data()
        elapsed_time = time.time() - start
        self.view_panel.set_image(self.model.to_image())
        self.fractal_panel.set_processing_time(elapsed_time)

    def save(self):
        filename = self.model.fractal_type
        index = 1
        while os.path.isfile('{}.png'.format(filename)):
            filename = '{}({})'.format(self.model.fractal_type, index)
            index += 1
        image = self.model.to_image()
        image.save('{}.png'.format(filename))


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
