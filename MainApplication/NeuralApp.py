"""
Basic menu system for NS2

Denis Kurka - 11.7.2019
"""

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.widget import Widget

class MainMenu(Widget):
    pass

class NeuralApp(App):
    kv_directory = 'templates'
    def build(self):
        return MainMenu()

if __name__ == '__main__':
    NeuralApp().run()