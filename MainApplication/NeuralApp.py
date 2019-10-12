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
from kivy.uix.settings import SettingsWithSidebar
from kivy.config import ConfigParser

from windows.CanvasWindow import CanvasWindow
from config import ai_settings_json, game_settings_json

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

#Window classes
class MainMenuWindow(Screen):
    pass

#KV files import
Builder.load_file("templates/mainmenu.kv")
Builder.load_file("templates/canvas.kv")

#Screen manager
sm = ScreenManager()
screens = [MainMenuWindow(name="mainmenu"), CanvasWindow(name="canvas")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "mainmenu"

#Main class
class NeuralApp(App):
    def build(self):
        self.settings_cls = SettingsWithSidebar
        return sm

    def build_config(self, config):
        config.setdefaults("Game", {
            "boolraycasts": False,
            "numraycasts": 3,
            "angleraycasts": 35
        })

        config.setdefaults("AI", {
            "learn_type": "DQN",
            "network_type": "Sequential",
        })

        config.setdefaults("DQN", {
            "dqn_discount_factor": 0.95,
            "dqn_exploration_max": 1,
            "dqn_exploration_min": 0.01,
            "dqn_exploration_decay": 0.995,
            "dqn_batch_size": 20,
            "dqn_experience_type": "ER",
        })

        config.setdefaults("SGA", {
            "sga_mutation_rate": 0.01,
            "sga_population_size": 30,
        })

    def build_settings(self, settings):
        settings.add_json_panel("AI panel", self.config, data=ai_settings_json)
        settings.add_json_panel("Game panel", self.config, data=game_settings_json)

    def on_config_change(self, config, section, key, value):
        pass

if __name__ == '__main__':
    NeuralApp().run()