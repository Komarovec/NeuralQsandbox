import cffi
import pymunk
from objs.GameObjects import StaticGameObject
from objs.Car import Car
from objs.kivyObjs import paintObject

import tkinter as tk
from tkinter import filedialog

import pickle
import sys, os

class Level():
    @classmethod
    def exportLevel(self, simulation):          
        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\levels"   
        if not os.path.exists(pathname):
            os.makedirs(pathname)

        #Create filedialog
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.asksaveasfilename(initialdir = pathname,title = "Save level")

        if(file_path != ""):
            space = simulation.space
            for shape in space.shapes:
                if(isinstance(shape, Car)):
                    car = shape

                simulation.canvasWindow.canvas.remove(shape.ky)
                shape.ky = None

            simulation.removeCallbacks()

            space.remove(car.body, car)
            with open(file_path, "wb") as f:
                pickle.dump(space, f, pickle.HIGHEST_PROTOCOL)
            
            simulation.addCallbacks()

            space.add(car.body, car)
            for shape in space.shapes:
                paintObject(shape, simulation.canvasWindow)

    @classmethod
    def importLevel(self, simulation):
        pathname = os.path.abspath(os.path.dirname(sys.argv[0]))+"\levels"   
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

            for shape in space.shapes:
                paintObject(shape, simulation.canvasWindow)
        
        
