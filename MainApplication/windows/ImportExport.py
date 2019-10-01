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

from keras.models import load_model

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
    NETWORK_TYPES = [("Hierarchical Data Format (*.h5)","*.h5")]

    @classmethod
    def exportNetwork(self, model):
        #Check if model exists
        if(model == None):
            levelPopup("No model loaded!")
            return

        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\networks"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        file_path = filedialog.asksaveasfilename(initialdir = pathname, title = "Save neural network", defaultextension=".h5", filetypes=self.NETWORK_TYPES)

        if(file_path != ""):
            #Try exporting model
            try:
                model.save(file_path)

            #If exception occured print something
            except:
                levelPopup("Something went wrong!")

            #If everything went ok
            else:
                levelPopup("Neural network exported!")

    @classmethod
    def importNetwork(self):
        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\networks"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        file_path = filedialog.askopenfilename(initialdir = pathname, title = "Load neural network", defaultextension=".h5", filetypes=self.NETWORK_TYPES)

        if(file_path != ""):
            #Try importing model
            try:
                model = load_model(file_path)

            #If exception occured print something
            except:
                levelPopup("Something went wrong!")

            #If everything went ok
            else:
                levelPopup("Neural network imported!")
                return model


class IELevel():
    LEVEL_TYPES = [("Pickled level (*.lvl)","*.lvl")]

    @classmethod
    def exportLevel(self, simulation):     
        simulation.canvasWindow.stopDrawing()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\levels"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(initialdir = pathname,title = "Save level", defaultextension=".lvl", filetypes=self.LEVEL_TYPES)

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

            #Try exporting level
            try:
                with open(file_path, "wb") as f:
                    pickle.dump(space_copy, f, pickle.HIGHEST_PROTOCOL)

            #If exception occured print something
            except:
                levelPopup("Something went wrong!")
            
            #If everything went ok
            else:
                for shape in space.shapes:
                    paintObject(shape, simulation.canvasWindow)
                levelPopup("Level exported!")


        simulation.canvasWindow.startDrawing()

    @classmethod
    def importLevel(self, simulation):
        simulation.canvasWindow.stopDrawing()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\\levels"   
        if not os.path.exists(pathname):
            os.makedirs(pathname) 

        #Create filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir = pathname,title = "Load level", defaultextension=".lvl", filetypes=self.LEVEL_TYPES)

        if(file_path != ""):
            space = simulation.space

            #Try importing level
            try:
                with open(file_path, "rb") as f:
                    loaded_space = pickle.load(f)

            #If exception occured print something
            except:
                levelPopup("Something went wrong!")

            #If everythin went ok
            else:
                simulation.deleteSpace()
                simulation.loadSpace(loaded_space)

                for shape in simulation.space.shapes:
                    paintObject(shape, simulation.canvasWindow)

                levelPopup("Level imported!")
            

            simulation.canvasWindow.startDrawing()
        
        
