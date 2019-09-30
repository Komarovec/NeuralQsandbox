import cffi
import pymunk
from objs.GameObjects import StaticGameObject
from objs.Car import Car
from objs.kivyObjs import paintObject

import tkinter as tk
from tkinter import filedialog

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

from keras.models import model_from_json

import pickle
import sys, os

class levelPopup():
    def __init__(self, text):
            content = BoxLayout(orientation="vertical")
            popup = Popup(title="WIP POPUP!! THIS WILL BE REPLACED", content=content, size_hint=(None,None), size=(400,300))

            content.add_widget(Label(text=text))
            content.add_widget(Button(text="Close", on_press=popup.dismiss, size_hint=(1, 0.2)))
            popup.open()

class IENetwork():
    @classmethod
    def exportNetwork(self, model, structure):
        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\networks"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        file_path = filedialog.asksaveasfilename(initialdir = pathname,title = "Save neural network")

        if(file_path != ""):
            model_json = model.to_json()
            with open(file_path, "w") as json_file:
                json_file.write(model_json)

            levelPopup("Neural network exported!")

    @classmethod
    def importNetwork(self):
        pass

class IELevel():
    @classmethod
    def exportLevel(self, simulation):     
        if(simulation.canvasWindow.state == "game"):
            levelPopup("Exporting while in-game is not supported!\nPlease switch to Editor")
            return

        simulation.canvasWindow.stopDrawing()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\levels"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(initialdir = pathname,title = "Save level")

        if(file_path != ""):
            cars = []
            space = simulation.space
            for shape in space.shapes:
                if(isinstance(shape, Car)):
                    cars.append(shape)

                simulation.canvasWindow.canvas.remove(shape.ky)
                shape.ky = None

            simulation.removeCallbacks()
            for car in cars:
                simulation.space.remove(car.body, car)

            space_copy = simulation.space.copy()

            simulation.addCallbacks()
            for car in cars:
                simulation.space.add(car.body, car)

            with open(file_path, "wb") as f:
                pickle.dump(space_copy, f, pickle.HIGHEST_PROTOCOL)

            for shape in space.shapes:
                paintObject(shape, simulation.canvasWindow)

            levelPopup("Level exported!")

        simulation.canvasWindow.startDrawing()

    @classmethod
    def importLevel(self, simulation):
        if(simulation.canvasWindow.state == "game"):
            levelPopup("Importing while in-game is not supported!\nPlease switch to Editor")
            return

        simulation.canvasWindow.stopDrawing()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\levels"   
        if not os.path.exists(pathname):
            os.makedirs(pathname) 

        #Create filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir = pathname,title = "Load level")

        if(file_path != ""):
            space = simulation.space

            simulation.deleteSpace()

            with open(file_path, "rb") as f:
                loaded_space = pickle.load(f)

            simulation.loadSpace(loaded_space)

            for shape in simulation.space.shapes:
                paintObject(shape, simulation.canvasWindow)

            simulation.canvasWindow.startDrawing()

            levelPopup("Level imported!")
        
        
