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
from kivy.uix.settings import Settings
from kivy.uix.settings import SettingString
from kivy.uix.settings import InterfaceWithNoMenu
from kivy.config import ConfigParser

from windows.CanvasWindow import CanvasWindow
from windows.PopNot import ConfirmPopup, InfoPopup
import windows.PopNot as PN
from config import ai_settings_json, game_settings_json

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

import numpy as np

#Window classes
class MainMenuWindow(Screen):
    pass

#KV files import
Builder.load_file("templates/mainmenu.kv")
Builder.load_file("templates/canvas.kv")

#Screen manager
sm = ScreenManager()
mainMenu = MainMenuWindow(name="mainmenu")
canvasWindow = CanvasWindow(name="canvas")

sm.add_widget(mainMenu)
sm.add_widget(canvasWindow)

sm.current = "mainmenu"

#Settings classes
class ValidatedSettingsInterface(SettingsWithSidebar):  
    pass

class ValidatedSettings(Settings):
    def __init__(self, **kwargs):
        super(ValidatedSettings, self).__init__(**kwargs)
        self.register_type('multiplier', MultiplierValue)
        self.register_type('angle', AngleValue)
        self.register_type('raycasts', RaycastsValue)
        self.register_type('population', PopulationValue)
        self.register_type('batch', BatchValue)

    def add_kivy_panel(self):
        pass

"""
Custom datatypes
"""
#Validate percentage multipliers <0,1>
class MultiplierValue(SettingString):
    def __init__(self, **kwargs):
        super(MultiplierValue, self).__init__(**kwargs)

    def _validate(self, instance):
        self._dismiss()    # closes the popup

        #Clamp the value between <0,1>
        try:
            val = float(self.textinput.text)
            val = np.clip(val, 0, 1)
            self.value = str(val)
        except:
            return

#Validate angles
class AngleValue(SettingString):
    def __init__(self, **kwargs):
        super(AngleValue, self).__init__(**kwargs)

    def _validate(self, instance):
        self._dismiss()    # closes the popup

        #Clamp the value between <0,1>
        try:
            val = float(self.textinput.text)
            val = np.clip(val, 1, 180)
            self.value = str(val)
        except:
            return

#Validate raycasts
class RaycastsValue(SettingString):
    def __init__(self, **kwargs):
        super(RaycastsValue, self).__init__(**kwargs)

    def _validate(self, instance):
        self._dismiss()    # closes the popup

        #Clamp the value between <0,1>
        try:
            val = int(round(float(self.textinput.text)))
            val = np.clip(val, 1, 20)
            self.value = str(val)
        except:
            return

#Validate batch size DQN
class BatchValue(SettingString):
    def __init__(self, **kwargs):
        super(BatchValue, self).__init__(**kwargs)

    def _validate(self, instance):
        self._dismiss()    # closes the popup

        #Clamp the value between <0,1>
        try:
            val = int(round(float(self.textinput.text)))
            val = np.clip(val, 10, 100)
            self.value = str(val)
        except:
            return

#Validate population size SGA
class PopulationValue(SettingString):
    def __init__(self, **kwargs):
        super(PopulationValue, self).__init__(**kwargs)

    def _validate(self, instance):
        self._dismiss()    # closes the popup

        #Clamp the value between <0,1>
        try:
            val = int(round(float(self.textinput.text)))
            val = np.clip(val, 8, 50)
            self.value = str(val)
        except:
            return

#Main class
class NeuralApp(App):
    def build(self):
        self.settings_cls = ValidatedSettings
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

    #Config reset confirmed
    def config_reset_confirmed(self):
        config = self.config

        config.setall("Game", {
            "boolraycasts": False,
            "numraycasts": 3,
            "angleraycasts": 35
        })

        config.setall("AI", {
            "learn_type": "DQN",
            "network_type": "Sequential",
        })

        config.setall("DQN", {
            "dqn_discount_factor": 0.95,
            "dqn_exploration_max": 1,
            "dqn_exploration_min": 0.01,
            "dqn_exploration_decay": 0.995,
            "dqn_batch_size": 20,
            "dqn_experience_type": "ER",
        })

        config.setall("SGA", {
            "sga_mutation_rate": 0.01,
            "sga_population_size": 30,
        })

        config.write()

        self.stop()

    #Reset of config
    def config_reset(self):
        ConfirmPopup("Reset will result in application restart!\n Do you really wish to continue?", 
        "Config reset", self.config_reset_confirmed, PN.DANGER_ICON)

    #Exiting confirmed
    def exit_game_confirmed(self):
        sm.transition.direction = 'right'
        sm.current = 'mainmenu'

    #Called when exiting canvas
    def exit_game(self):
        ConfirmPopup("Exiting will erase your progress!\n Do you really wish to continue?", 
        "Game exit", self.exit_game_confirmed, PN.DANGER_ICON)


if __name__ == '__main__':
    NeuralApp().run()