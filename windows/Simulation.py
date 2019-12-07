# Kivy
from kivy.graphics import Color

# Tensorflow
import tensorflow as tf

# Pymunk
import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

import threading as th
from time import sleep, time
import os
import sys
import math
import random

from objs.GameObjects import StaticGameObject
from objs.CarAI import CarAI
from objs.Car import Car
from objs.kivyObjs import distXY, centerPoint
from windows.ImportExport import IELevel
from ai.GameController import GameController

random.seed(5)

class Simulation():

    def __init__(self, canvasWindow):
        # Important values
        self.step = 1/60.
        self.canvasWindow = canvasWindow

        # Learning vars
        self.gameController = GameController(self)

        # Create thread for physics
        self.stopThread = True

        # Tensorflow computational graph
        self.graph = tf.get_default_graph()

        # Default level
        self.defaultLevel = os.path.abspath(os.path.dirname(sys.argv[0]))+"/levels/conti.lvl"

        #Simulation speed cap
        self.fast_update_frequency = 1000
        self.normal_update_frequency = 150
        self.update_frequency = self.normal_update_frequency

    # Create new space
    def setupSpace(self):
        self.endPhysicsThread()

        self.space = space = pymunk.Space()

        self.addCallbacks()

        space.gravity = 0, 0
        space.sleep_time_threshold = 0.3
        space.steps = 0

        self.startPhysicsThread()

        return space

    # Prepare collisions callbacks
    def addCallbacks(self):
        self.handler = self.space.add_collision_handler(0,0)
        self.handler.begin = self.coll_begin
        self.handler.pre_solve = self.coll_pre
        self.handler.post_solve = self.coll_post
        self.handler.separate = self.coll_separate

    # Remove collisions callbacks
    def removeCallbacks(self):
        self.handler.begin = None
        self.handler.pre_solve = None
        self.handler.post_solve = None
        self.handler.separate = None
        self.handler = None

    # Delete everything from space & canvas
    def deleteSpace(self):
        for shape in self.space.shapes:
            self.canvasWindow.canvas.remove(shape.ky)

        self.setupSpace()

    # Load shapes from space to current space
    def loadSpace(self, loadedSpace):
        for shape in loadedSpace.shapes:
            self.space.add(shape.copy().body, shape.copy())

        self.addCallbacks()

    # First start, setup space and import level
    def start(self):
        self.setupSpace()

    # Load default level
    def loadDefaultLevel(self):
        # Check if default level exists
        if(not IELevel.importLevelSilent(self, self.defaultLevel)):
            # Spawning objects
            StaticGameObject(StaticGameObject.BARRIER).createSegment((0,0), (2000,0), 20, self.canvasWindow)
            StaticGameObject(StaticGameObject.BARRIER).createSegment((2000,0), (2000,1000), 20, self.canvasWindow)
            StaticGameObject(StaticGameObject.BARRIER).createSegment((2000,1000), (0,1000), 20, self.canvasWindow)
            StaticGameObject(StaticGameObject.BARRIER).createSegment((0,0), (0,1000), 20, self.canvasWindow)
        
            start = StaticGameObject(StaticGameObject.START, rgba=(0,.8,0,1))
            start.createSegment((100,400), (100,600), 20, self.canvasWindow)

            finish = StaticGameObject(StaticGameObject.FINISH, rgba=(.8,0,0,1))
            finish.createSegment((1800,400), (1800,600), 20, self.canvasWindow)
        
    """ 
            Threaded loop functions 
    """
    # Start thread --> MUST BE CALLED FROM MAIN THREAD
    def startPhysicsThread(self):
        if(hasattr(self, "thread")):
            if(self.thread != None):
                self.endPhysicsThread()
                print("Tried to start a new thread when there is still a running thread!") # DEBUG

        self.stopThread = False
        self.thread = th.Thread(target=self.physicsThread, name="PhysicsThread")
        self.thread.daemon = True
        self.thread.start()

    # End thread --> MUST BE CALLED FROM MAIN THREAD
    def endPhysicsThread(self):
        if(hasattr(self, "thread")):
            if(self.thread != None):
                self.stopThread = True
                self.thread.join()
                self.thread = None
            else:
                print("Tried to end non-existing thread! NONE") # DEBUG
        else:
            print("Tried to end non-existing thread! ATTR") # DEBUG

    # Thread function for physics
    def physicsThread(self):
        _last_time = 0
        while True:
            _now = time()
            if(_now - _last_time > (1/self.update_frequency)):
                self.update()
                _last_time = _now
            else:
                sleep(_now - _last_time)

            if(self.stopThread):
                break

        return True

    # Main looping function - Run in thread
    def update(self):
        # Game logic loop
        if(self.gameController != None):
            self.gameController.loop()

        # Physics loop
        self.stepSpace()

    # Step simulation space
    def stepSpace(self):
        for shape in self.space.shapes:
            if(not shape.body.is_sleeping):
                if(hasattr(shape, "raycast")): continue

                # If there is friction set by class use it
                if(isinstance(shape, Car)):
                    friction = shape.ground_friction
                    angular_friction = shape.angular_friction
                else:
                    friction = 0.9
                    angular_friction = 0.9

                # Zero-out velocity vector if it is approaching 0
                if(shape.body.velocity.length < 0.001):
                    shape.body.velocity = Vec2d(0,0)

                # Apply friction every step
                shape.body.velocity *= 1 - (self.step*friction)
                shape.body.angular_velocity *= 1 - (self.step*angular_friction)

        # Stepping space simul
        self.space.step(self.step)
        self.space.steps += 1


    """ 
        Enviroment functions 
    """
    # Reset level
    def resetLevel(self):
        # Delete all Cars from level and canvas
        for shape in self.space.shapes:
            if(isinstance(shape, Car)):
                # Delete any raycast if CarAI
                if(isinstance(shape, CarAI)):
                    shape.deleteRaycasts(self)
                self.space.remove(shape.body, shape)
                self.canvasWindow.canvas.remove(shape.ky)

    # Adding
    def addSegment(self, a, b, radius, typeVal, collisions, rgba, change="change"):
        if(typeVal == "Finish"):
            segment = StaticGameObject(StaticGameObject.FINISH, rgba=rgba)
        elif(typeVal == "Start"):
            segment = StaticGameObject(StaticGameObject.START, rgba=rgba)
        elif(collisions == False):
            segment = StaticGameObject(StaticGameObject.NOBARRIER, rgba=rgba)
        else:
            segment = StaticGameObject(StaticGameObject.BARRIER, rgba=rgba)

        segment.createSegment(a, b, radius, self.canvasWindow)
        self.repaintObjects()

        # Undo system
        if(change == "change"):
            self.canvasWindow.changes.append(segment.shape)

    def addCircle(self, a, radius, typeVal, collisions, rgba, change="change"):
        if(typeVal == "Finish"):
            circle = StaticGameObject(StaticGameObject.FINISH, rgba=rgba)
        elif(typeVal == "Start"):
            circle = StaticGameObject(StaticGameObject.START, rgba=rgba)
        elif(collisions == False):
            circle = StaticGameObject(StaticGameObject.NOBARRIER, rgba=rgba)
        else:
            circle = StaticGameObject(StaticGameObject.BARRIER, rgba=rgba)
        
        circle.createCircle(a, radius, self.canvasWindow)
        self.repaintObjects()

        # Undo system
        if(change == "change"):
            self.canvasWindow.changes.append(circle.shape)

    def addBox(self, points, typeVal, collisions, rgba, change="change"):
        if(typeVal == "Finish"):
            box = StaticGameObject(StaticGameObject.FINISH, rgba=rgba)
        elif(typeVal == "Start"):
            box = StaticGameObject(StaticGameObject.START, rgba=rgba)
        elif(collisions == False):
            box = StaticGameObject(StaticGameObject.NOBARRIER, rgba=rgba)
        else:
            box = StaticGameObject(StaticGameObject.BARRIER, rgba=rgba)

        box.createBoxPoints(points, self.canvasWindow)
        self.repaintObjects()

        # Undo system
        if(change == "change"):
            self.canvasWindow.changes.append(box.shape)

    # Delete object from space
    def deleteObject(self, obj, change="change"):
        self.space.remove(obj)
        self.canvasWindow.canvas.remove(obj.ky)

        # Undo system
        if(change == "change"):
            self.canvasWindow.changes.append(obj)

    # Repaint all object and keep layering in mind
    def repaintObjects(self):
        cars = []

        for shape in self.space.shapes:
            if(hasattr(shape, "ky")):
                self.canvasWindow.canvas.remove(shape.ky)

        for shape in self.space.shapes:
            self.canvasWindow.canvas.add(Color(rgba=shape.rgba))
            if(isinstance(shape, Car)):
                cars.append(shape)
            else:
                self.canvasWindow.canvas.add(shape.ky)

        # Paint cars on top of everything
        for car in cars:
            car.paint(self.canvasWindow)

    # Add one car as an AI model
    def addCarAI(self, model=None):
        point = self.findSpawnpoint()
        if(point != None):
            car = CarAI(10, (100,50), self.findSpawnpoint(), ground_friction=1, angular_friction=3, model=model)
            car.createRaycasts(self)
            self.space.add(car.body, car)
            self.repaintObjects()
            return car
        else:
            self.canvasWindow.t_signal = self.canvasWindow.TS_SPAWN_ERROR
            return None

    # Add one car as a player
    def addPlayer(self):
        point = self.findSpawnpoint()
        if(point != None):
            car = Car(10, (100,50), self.findSpawnpoint(), ground_friction=1, angular_friction=3)
            self.space.add(car.body, car)
            self.repaintObjects()
            return car
        else:
            self.canvasWindow.t_signal = self.canvasWindow.TS_SPAWN_ERROR
            return None

    # Returns all car instances from space.shapes
    def getCars(self):
        cars = []
        for shape in self.space.shapes:
            if(isinstance(shape, Car)):
                cars.append(shape)
        
        return cars

    # Load cars from an array
    def loadCars(self, cars):
        # If empty array return
        if(cars == []):
            return False
        
        for car in cars:
            self.space.add(car.body, car)
            if(isinstance(car, CarAI)):
                car.loadRaycasts(self)
            car.paint(self.canvasWindow)
        
        self.canvasWindow.selectedCar = cars[0]

        return True

    # Remove player from space (all car class instances)
    def removeCars(self):
        for shape in self.space.shapes:
            if(isinstance(shape, Car)):
                # Delete any raycast if CarAI
                if(isinstance(shape, CarAI)):
                    shape.deleteRaycasts(self)
                self.space.remove(shape.body, shape)
                self.canvasWindow.canvas.remove(shape.ky)

        self.canvasWindow.selectedCar = None

    # Find spawnpoint for car
    def findSpawnpoint(self):
        spawnPoint = None

        for shape in self.space.shapes:
            if(hasattr(shape, "objectType")):
                if(shape.objectType == StaticGameObject.START):
                    spawnPoint = self.getCenterPos(shape)
        
        return spawnPoint
    
    # Find nearest finish
    def findNearestFinish(self, point):
        finishPoint = None

        for shape in self.space.shapes:
            if(hasattr(shape, "objectType")):
                if(shape.objectType == StaticGameObject.FINISH):
                    finishPoint = self.getCenterPos(shape)
        
        return finishPoint

    # Get center position of any shape
    def getCenterPos(self, shape):
        point = None
        if(isinstance(shape, pymunk.Segment)):
            point = centerPoint(shape.a, shape.b)
        elif(isinstance(shape, pymunk.Circle)):
            point = shape.body.position
        elif(isinstance(shape, pymunk.Poly)):
            vertices = shape.get_vertices()
            point = centerPoint(centerPoint(vertices[0], vertices[1]), centerPoint(vertices[2], vertices[3]))
        
        return point

    # Shift layer shif --> direction, spec --> special TOP, BOTTOM --> ALL THE WAY
    def shiftLayer(self, obj, shift, spec):
        temp = None
        tempShapes = []
        splitIndex = None

        if(spec):
            for shape in self.space.shapes:
                if(shape == obj):
                    temp = obj
                else:
                    tempShapes.append(shape)

                self.space.remove(shape)

            if(shift > 0):
                for tempShape in tempShapes:
                    self.space.add(tempShape)
                self.space.add(temp)
            else:
                self.space.add(temp)
                for tempShape in tempShapes:
                    self.space.add(tempShape)
            

            self.repaintObjects()
        else:
            # Save moving object, Save all object from moving one --> tempShapes
            for index, shape in enumerate(self.space.shapes):
                if(shape == obj):
                    splitIndex = index
                    temp = shape

                    if(shift < 0 and splitIndex != 0):
                        tempShapes.append(self.space.shapes[splitIndex-1])

                elif(splitIndex != None):
                    tempShapes.append(shape)

            if(len(tempShapes) != 0):
                # Delete all tempShapes from space
                for tempShape in tempShapes:
                    self.space.remove(tempShape)

                # Delete moving object from space
                self.space.remove(temp)

                # Add first from tempShapes and then moving object itself
                if(shift > 0):
                    self.space.add(tempShapes[0])

                self.space.add(temp)

                # Add rest of tempShapes except of the first one
                for index, tempShape in enumerate(tempShapes):
                    if(index == 0 and shift > 0):
                        continue

                    self.space.add(tempShape)

                # Repaint everything
                self.repaintObjects()

    # Get layer of object     
    def getLayer(self, obj):
        for index, shape in enumerate(self.space.shapes):
            if(shape == obj):
                return index

    # Collistions handlers
    def coll_begin(self, arbiter, space, data):
        if(isinstance(arbiter.shapes[0], Car) or isinstance(arbiter.shapes[1], Car)):        
            car = None
            otherObject = None
            if(isinstance(arbiter.shapes[0], Car)):
                car = arbiter.shapes[0]
                otherObject = arbiter.shapes[1]
            else:
                car = arbiter.shapes[1]
                otherObject = arbiter.shapes[0]

            if(otherObject.objectType != StaticGameObject.START):
                self.gameController.handleCollision(car, otherObject)
            return True
        return True

    def coll_pre(self, arbiter, space, data):
        return True

    def coll_post(self, arbiter, space, data):
        pass

    def coll_separate(self, arbiter, space, date):
        pass
