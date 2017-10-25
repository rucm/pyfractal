from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.app import ObjectProperty
import numpy as np
import fractal


class MainScreen(GridLayout):
    display = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _, _, data = fractal.julia_set(
            -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 2000, 512
        )
        palette = fractal.create_palette()
        data = fractal.min_max_normalize(data, 0, 255).astype(np.uint8)
        image = fractal.create_image(data, palette)
        texture = Texture.create(size=image.size)
        texture.blit_buffer(image.tobytes())
        texture.flip_vertical()

        image.save('julia.png', 'PNG')
        print(self.display.size)

        with self.display.canvas:
            Rectangle(
                texture=texture,
                pos=self.display.pos,
                size=self.display.size)


class SetGraph(GridLayout):
    view = ObjectProperty(None)

    def click(self):
        data = []
        for i in range(256):
            data.append((
                i,
                fractal.Easing.Calc('InCirc', i, 256, 255, 0)))
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = data
        self.view.add_plot(plot)


class FractalViewerApp(App):
    pass


if __name__ == '__main__':
    import kivy.garden
    kivy.garden.garden_system_dir = 'garden'
    from kivy.config import Config
    from kivy.garden.graph import Graph, MeshLinePlot
    Config.set('graphics', 'width', 1024)
    Config.set('graphics', 'height', 768)
    FractalViewerApp().run()
