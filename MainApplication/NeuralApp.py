"""
Basic menu system for NS2

Denis Kurka - 11.7.2019
"""

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen

#Window classes
class MainMenuWindow(Screen):
    pass

#Screen manager
kv = Builder.load_file("templates/neural.kv")
sm = ScreenManager()
screens = [MainMenuWindow(name="mainmenu")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "mainmenu"

#Main class
class NeuralApp(App):
    def build(self):
        return sm

if __name__ == '__main__':
    NeuralApp().run()