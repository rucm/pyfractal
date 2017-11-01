import fractal


class FractalModel(object):

    def __init__(self):
        self.reset_param()
        self.create_data()
        self.create_palette()

    def reset_param(self):
        self.fractal_type = 'julia'
        self.x_range = [-1.5, 1.5]
        self.y_range = [-1.5, 1.5]
        self.center_pos = [0.0, 0.0]
        self.constant = [-0.3, -0.63]
        self.size = 800
        self.steps = 256
        self.zoom = 1.0
        self.hue = {'easing': 'OutExp', 'range': [0.2, 1.0]}
        self.saturation = {'easing': 'OutExp', 'range': [1.0, 0.0]}
        self.brightness = {'easing': 'Fixed', 'range': [1.0, 1.0]}

    def set_fractal_type(self, fractal_type):
        self.fractal_type = fractal_type

    def get_center_from_normalized(self, x, y):
        dif_x = self.x_range[1] - self.x_range[0]
        dif_y = self.y_range[1] - self.y_range[0]
        x = x * dif_x + self.x_range[0]
        y = y * dif_y + self.y_range[0]
        return [x, y]

    def set_center_pos(self, x, y):
        self.center_pos = [x, y]

    def set_constant(self, x, y):
        self.constant = [x, y]

    def set_size(self, size):
        self.size = size

    def set_steps(self, steps):
        self.steps = steps

    def set_zoom(self, zoom):
        self.zoom = zoom

    def set_hue(self, easing, begin, end):
        self.hue['easing'] = easing
        self.hue['range'] = [begin, end]

    def set_saturation(self, easing, begin, end):
        self.saturation['easing'] = easing
        self.saturation['range'] = [begin, end]

    def set_brightness(self, easing, begin, end):
        self.brightness['easing'] = easing
        self.brightness['range'] = [begin, end]

    def create_data(self):
        x, y = self.center_pos[0], self.center_pos[1]
        x_range = [-1.5 / self.zoom + x, 1.5 / self.zoom + x]
        y_range = [-1.5 / self.zoom + y, 1.5 / self.zoom + y]
        if self.fractal_type == 'julia':
            _, _, self.data = fractal.julia_set(
                *x_range,
                *y_range,
                *self.constant,
                self.size, self.steps,
            )
        elif self.fractal_type == 'mandelbrot':
            _, _, self.data = fractal.mandelbrot_set(
                *x_range,
                *y_range,
                self.size, self.steps
            )
        self.x_range = x_range
        self.y_range = y_range

    def create_palette(self):
        self.palette = fractal.create_palette({
            'hue': self.hue,
            'saturation': self.saturation,
            'brightness': self.brightness
        })

    def to_image(self):
        return fractal.create_image(self.data, self.palette)

    def to_palette_image(self):
        return fractal.image_of_palette(self.palette)


if __name__ == '__main__':
    model = FractalModel()
    model.create_data()
    model.create_palette()
    image = model.to_image()
    image.save('test.png')
