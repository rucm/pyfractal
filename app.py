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


def resourcePath():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))


class FractalParam(object):
    fractal_type = 'julia'
    xmin = -1.5
    xmax = 1.5
    ymin = -1.5
    ymax = 1.5
    cx = -0.3
    cy = -0.63
    image_size = 800
    steps = 256
    scale = 1.0


class FractalModel(object):
    default_param = FractalParam()
    param = FractalParam()
    data = None

    def reset(self):
        import copy
        self.param = copy.deepcopy(self.default_param)

    def calculate(self):
        if self.param.fractal_type == 'julia':
            _, _, self.data = fractal.julia_set(
                self.param.xmin, self.param.xmax, self.ymin, self.ymax,
                self.param.cx, self.param.cy,
                self.param.image_size, self.param.steps)
        elif self.param.fractal_type == 'mandelbrot':
            _, _, self.data = fractal.mandelbrot_set(
                self.param.xmin, self.param.xmax, self.ymin, self.ymax,
                self.param.image_size, self.param.steps)


class ViewPanel(BoxLayout):
    scene = ObjectProperty(None)

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
        print('{}, {}'.format(x, y))


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
        start = time.time()
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
        elapsed_time = time.time() - start
        self.processing_time.param = elapsed_time

    def save(self):
        Clock.schedule_once(lambda dt: self.parent.save())


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

    def save(self):
        if self.control_panel.data is None:
            return
        elif self.color_panel.palette is None:
            return
        image = fractal.create_image(
            self.control_panel.data,
            self.color_panel.palette)
        fractal_type = self.control_panel.fractal_type
        filename = '{}.png'.format(fractal_type)
        index = 1
        while os.path.isfile(filename):
            filename = filename.split('.')
            filename[0] = '{}({})'.format(fractal_type, index)
            filename = '.'.join(filename)
            index += 1
        image.save(filename, 'PNG')


class FractalViewerApp(App):

    def build(self):
        self.icon = 'fractal.png'
        return FractalViewer()


if __name__ == '__main__':
    from kivy.config import Config
    import kivy.resources
    Config.set('graphics', 'width', 1080)
    Config.set('graphics', 'height', 720)
    kivy.resources.resource_add_path(resourcePath())
    FractalViewerApp().run()
