import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from windows.GameWidgets import BGLabel, ActivationDropDown

from functools import partial
import re

from ai.models import DEFAULT_STRUCTURE

class ControlsWidget(BoxLayout):
    def __init__(self, addfun=None, resetfun=None, applyfun=None, **kwargs):
        super().__init__(orientation="vertical", size=(150,100), size_hint=(None, 1), padding=10,
            spacing=10, **kwargs)
 
        self.app = App.get_running_app()
        self.build()

        self.cancelBtn.bind(on_press=self.app.exit_layers)
        self.bindFun(addfun, resetfun, applyfun)

        self.bind(pos=self.draw)
        self.bind(size=self.draw)
        self.draw()

    def build(self):
        self.layerBtn = Button(text="Add layer", size_hint=(1, None), size=(50,50))
        self.resetBtn = Button(text="Reset", size_hint=(1, None), size=(50,50))
        self.cancelBtn = Button(text="Cancel", size_hint=(1, None), size=(50,50))
        self.applyBtn = Button(text="Apply", size_hint=(1, None), size=(50,50))

        self.add_widget(self.layerBtn)
        self.add_widget(self.resetBtn)
        self.add_widget(Label(text="", size_hint=(1, 1))) # Blank space
        self.add_widget(self.cancelBtn)
        self.add_widget(self.applyBtn)

    def draw(self, *args):
        if(self.canvas == None): return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=(.15,.15,.15,1))
            Rectangle(pos=self.pos, size=self.size)

    def bindFun(self, addfun=None, resetfun=None, applyfun=None):
        if(addfun != None):
            self.layerBtn.bind(on_press=addfun)
        if(resetfun != None):
            self.resetBtn.bind(on_press=resetfun)
        if(applyfun != None):
            self.applyBtn.bind(on_press=applyfun)

class DenseLayerWidget(BoxLayout):
    def __init__(self, num, remfun, units=128, activation="relu", **kwargs):
        super().__init__(orientation="horizontal", padding=10,spacing=10, size=(100,50), size_hint=(1, None), **kwargs)
        self.remfun = remfun

        # Default values
        self.units = units
        self.activation = activation

        # Regex
        self.pat = re.compile('^[0-9]*$')

        self.unitInput = TextInput(text=str(self.units))
        self.unitInput.bind(text=self.units_change)
        self.actiInput = Button(text=activation)
        self.dropdown = ActivationDropDown(func=self.activation_change)
        self.actiInput.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.actiInput, 'text', x))

        self.removeBtn = Button(text="Remove", size_hint=(None, 1), size=(100,100))
        self.removeBtn.bind(on_press=partial(remfun, self))

        self.numLabel = Label(text=str(num))
        
        self.add_widget(self.numLabel)
        self.add_widget(Label(text="Units: "))
        self.add_widget(self.unitInput)
        self.add_widget(Label(text="Activation: "))
        self.add_widget(self.actiInput)
        if(num == 0):
            self.add_widget(Label(text="Input", size_hint=(None, 1), size=(100,100)))
        else:
            self.add_widget(self.removeBtn)

        self.bind(pos=self.draw)
        self.bind(size=self.draw)
        self.draw()

    def draw(self, *args):
        if(self.canvas == None): return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=(.15,.15,.15,1))
            Rectangle(pos=self.pos, size=self.size)

    def num_change(self, num):
        self.numLabel.text = str(num)

    def activation_change(self, val):
        self.activation = val

    def units_change(self, obj, val, *_):
        if(self.pat.match(val) and val != ""):
            self.units = val
        else:
            self.unitInput.text = str(self.units)
        print(val)

    def remove(self):
        self.canvas.before.clear()

class LayersWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #(orientation="vertical", padding=10,spacing=10, **kwargs)
        self.app = App.get_running_app()

        self.allLayers = []
        
        self.layout = BoxLayout(orientation="vertical", size_hint_y=None, padding=10, spacing=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.sv = ScrollView(size_hint=(1, None), size=self.size, pos=self.pos)
        self.sv.add_widget(self.layout)
        self.add_widget(self.sv) 

    def save_structure(self, *_):
        structure = []
        for layer in self.allLayers:
            structure.append(["dense", {"units":int(layer.units), "activation":layer.activation}])

        self.app.nstructure = structure

    def load_structure(self, *_):
        self.remove_all_layers()
        structure = self.app.nstructure
        if(structure == None):
            structure = DEFAULT_STRUCTURE

        for i, layer in enumerate(structure):
            if(layer[0] == "dense"): # Dense class
                self.add_layer(units=layer[1]["units"], activation=layer[1]["activation"])

    def on_size(self, *_):
        if(self.canvas == None): return

        self.sv.size = self.size
        self.sv.pos = self.pos

    def add_layer(self, *_, units=128, activation="relu"):
        newLayer = DenseLayerWidget(self.allLayers.__len__(), remfun=self.remove_layer, units=units, activation=activation)
        self.layout.add_widget(newLayer)
        self.allLayers.append(newLayer)
    
    def remove_all_layers(self):
        for layer in self.allLayers:
            self.layout.remove_widget(layer)

        self.allLayers = []

    def remove_layer(self, obj, *_):
        self.allLayers.remove(obj)
        self.layout.remove_widget(obj)

        newList = []
        for i, layer in enumerate(self.allLayers):
            layer.num_change(i)
            newList.append(layer)
        self.allLayers = newList

class LayersWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mainLayout = None
        self.controls = ControlsWidget()
        self.layers = LayersWidget()

        self.controls.bindFun(addfun=self.layers.add_layer, 
                              resetfun=self.layers.load_structure, 
                              applyfun=self.layers.save_structure)

    # Entered the screen
    def on_enter(self):
        if(self.mainLayout == None):
            self.mainLayout = BoxLayout(orientation='horizontal')
            self.mainLayout.add_widget(self.controls)
            self.mainLayout.add_widget(self.createLayers())
            self.add_widget(self.mainLayout)
        self.layers.load_structure()

    def createLayers(self):
        layersLayout = BoxLayout(orientation='vertical')
        layersLayout.add_widget(BGLabel(text="Layers", size_hint=(1, None), size=(50,50)))
        layersLayout.add_widget(self.layers)
        return layersLayout






