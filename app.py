from kivy.app import App


class FractalViewerApp(App):
    pass


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'width', 1024)
    Config.set('graphics', 'height', 768)
    FractalViewerApp().run()
