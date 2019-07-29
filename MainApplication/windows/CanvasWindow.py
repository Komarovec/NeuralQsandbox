import random
random.seed(5)

import kivy
kivy.require('1.0.7')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen

#Custom classes
from windows.Simulation import Simulation
from windows.CanvasHandler import CanvasHandler

#Widgets
class GameWidget(Widget):
    scaleFactor = NumericProperty(120)

    def __init__(self, game, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.game = game

class ToolBar(GameWidget):
    def __init__(self, manager, game, **kwargs):
        super(ToolBar, self).__init__(game, **kwargs)
        self.manager = manager

class StateBar(GameWidget):
    pass

#Main class
class CanvasWindow(Screen):
    def __init__(self, **kwargs):
        super(CanvasWindow, self).__init__(**kwargs)

    def on_enter(self):
        self.game = CanvasHandler()
        self.toolbar = ToolBar(self.manager, self.game)
        self.statebar = StateBar(self.game)

        self.game.size_hint = 1,1
        self.game.pos = 0,0

        self.add_widget(self.game, 10)
        self.add_widget(self.statebar)
        self.add_widget(self.toolbar)

        self.simulation = Simulation(self.game)

        self.game.init(self)
        self.game.start(self.simulation)

    def on_leave(self):
        self.game.stop()
        self.remove_widget(self.game)

    def reset(self):
        self.remove_widget(self.game)
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,0
        self.add_widget(self.game, 10)
        self.game.init()
        self.game.start()