import cffi
import pymunk
from objs.GameObjects import StaticGameObject
from objs.Car import Car
from objs.CarAI import CarAI
from objs.kivyObjs import paintObject

import tkinter as tk
from tkinter import filedialog

from keras.models import load_model

from windows.PopNot import InfoPopup
import windows.PopNot as PN

import tensorflow as tf

import pickle
import sys, os

class IENetwork():
    NETWORK_TYPES = [("Hierarchical Data Format (*.h5)","*.h5")]

    @classmethod
    def exportNetwork(self, model, simulation):
        # Check if model exists
        if(model == None):
            InfoPopup("No model loaded!")
            return

        # Create filedialog
        root = tk.Tk()
        root.withdraw()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/networks"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        file_path = filedialog.asksaveasfilename(initialdir = pathname, title = "Save neural network", defaultextension=".h5", filetypes=self.NETWORK_TYPES)

        if(file_path != ""):
            simulation.canvasWindow.stopDrawing()
            simulation.endPhysicsThread()

            # Try exporting model
            try:
                model.save(file_path)
            # If exception occured print something
            except:
                InfoPopup("Something went wrong!", "Network export", PN.DANGER_ICON)
            # If everything went ok
            else:
                InfoPopup("Neural network\nsuccessfully exported!", "Network export", PN.INFO_ICON)

            simulation.startPhysicsThread()
            simulation.canvasWindow.startDrawing()

    @classmethod
    def importNetwork(self, simulation):
        # Create filedialog
        root = tk.Tk()
        root.withdraw()

        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/networks"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        file_path = filedialog.askopenfilename(initialdir = pathname, title = "Load neural network", defaultextension=".h5", filetypes=self.NETWORK_TYPES)

        if(file_path != ""):
            simulation.canvasWindow.stopDrawing()
            simulation.endPhysicsThread()

            model = None
            # Try importing model
            try:
                graph = tf.get_default_graph()
                with graph.as_default():
                    model = load_model(file_path)
            # If exception occured print something
            except:
                InfoPopup("Something went wrong!", "Network import", PN.DANGER_ICON)
            # If everything went ok
            else:
                InfoPopup("Neural network\nsuccessfully imported!", "Network import", PN.INFO_ICON)
            
            simulation.startPhysicsThread()
            simulation.canvasWindow.startDrawing()    
            return model


class IELevel():
    LEVEL_TYPES = [("Pickled level (*.lvl)","*.lvl")]

    @classmethod
    def exportLevel(self, simulation):     
        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/levels"
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        # Create filedialog
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(initialdir = pathname,title = "Save level", defaultextension=".lvl", filetypes=self.LEVEL_TYPES)

        if(file_path != ""):
            simulation.canvasWindow.stopDrawing()
            simulation.endPhysicsThread()

            cars = []
            space = simulation.space
            for shape in space.shapes:
                if(isinstance(shape, Car)):
                    cars.append(shape)

                simulation.canvasWindow.canvas.remove(shape.ky)
                shape.ky = None

            for car in cars:
                simulation.space.remove(car.body, car)

            simulation.removeCallbacks()
            space_copy = simulation.space.copy()
            simulation.addCallbacks()

            for car in cars:
                simulation.space.add(car.body, car)

            # Try exporting level
            try:
                with open(file_path, "wb") as f:
                    pickle.dump(space_copy, f, pickle.HIGHEST_PROTOCOL)
            # If exception occured print something
            except:
                InfoPopup("Something went wrong!", "Level export", PN.DANGER_ICON)
            # If everything went ok
            else:
                for shape in space.shapes:
                    paintObject(shape, simulation.canvasWindow)
                InfoPopup("Level successfully exported!", "Level export", PN.INFO_ICON)

            simulation.startPhysicsThread()
            simulation.canvasWindow.startDrawing()

    @classmethod
    def importLevel(self, simulation):
        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"/levels"   
        if not os.path.exists(pathname):
            os.makedirs(pathname) 

        # Create filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(initialdir = pathname,title = "Load level", defaultextension=".lvl", filetypes=self.LEVEL_TYPES)

        if(file_path != ""):
            # Try importing level
            try:
                with open(file_path, "rb") as f:
                    loaded_space = pickle.load(f)
                # print("DEBUG: External space loaded")
            # If exception occured print something
            except:
                InfoPopup("Something went wrong!", "Level import", PN.DANGER_ICON)
            # If everything went ok
            else:
                simulation.deleteSpace()
                simulation.space.add_post_step_callback(simulation.loadSpace, loaded_space)

                InfoPopup("Level successfully imported!", "Level import", PN.INFO_ICON)

    @classmethod
    def exportLevelSilent(self, simulation, path):
        if(path != ""):
            simulation.canvasWindow.stopDrawing()
            simulation.endPhysicsThread()

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
                if(isinstance(car, CarAI)):
                    car.deleteRaycasts(simulation)

            space_copy = simulation.space.copy()

            simulation.addCallbacks()
            for car in cars:
                simulation.space.add(car.body, car)
                if(isinstance(car, CarAI)):
                    car.loadRaycasts(simulation)

            # Try exporting level
            try:
                with open(path, "wb") as f:
                    pickle.dump(space_copy, f, pickle.HIGHEST_PROTOCOL)

            # If exception occured print something
            except:
                InfoPopup("Something went wrong!", "Level export", PN.DANGER_ICON)
                simulation.startPhysicsThread()
                simulation.canvasWindow.startDrawing()
                return False
            
            # If everything went ok
            else:
                for shape in space.shapes:
                    paintObject(shape, simulation.canvasWindow)
                InfoPopup("Level successfully exported!", "Level export", PN.INFO_ICON)
                simulation.startPhysicsThread()
                simulation.canvasWindow.startDrawing()
                return True
        else:
            return False

    @classmethod
    def importLevelSilent(self, simulation, path):
        if(path != ""):
            loaded_space = None

            try: # Try importing level
                with open(path, "rb") as f:
                    loaded_space = pickle.load(f)
            except: # If exception occured print something
                simulation.startPhysicsThread()
                simulation.canvasWindow.startDrawing()
                return False
            else: # If everything went ok
                simulation.deleteSpace()
                simulation.space.add_post_step_callback(simulation.loadSpace, loaded_space)
                
            return True
        else:
            return False
        
        
        
