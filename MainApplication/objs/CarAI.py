import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Quad, Line
from kivy.app import App
import math
import numpy as np
from statistics import median, mean
from collections import Counter
import random

# AI Framework
from keras.models import Sequential
import keras

# Custom functions and classes
from objs.Car import Car
from objs.kivyObjs import points_from_poly, centerPoint, getVector, normalizeVector, distXY

from ai.models import SequentialModel

class CarAI(Car):
    CARAI = "carai"

    def __init__(self, mass=50, size=(100,50), pos=(100,100), friction=1, ground_friction=1, angular_friction=0.9, forward_speed = 5000, 
                backward_speed = 5000, angular_speed = 500, elasticity=0.4, rgba=(0.8,0,0,1), texture=None, model=None, learningRate=0.001):
        super(CarAI, self).__init__(mass, size, pos, friction, ground_friction, angular_friction, forward_speed, 
                                    backward_speed, angular_speed, elasticity, rgba, texture)
        
        config = App.get_running_app().config

        self.objectType = self.CARAI
        self.raycastLenght = 2000
        self.raycastAngle = np.radians(float(config.get('Game','angleraycasts')))
        self.raycastCount = int(config.get('Game','numraycasts'))-1
        self.raycastObjects = []
        self.raycastColor = (1,1,1, int(config.get('Game', 'boolraycasts')))

        self.action_space = 3

        # AI
        self.learningRate = learningRate
        self.isDead = False
        self.reward = 0

        # LastAction
        self.lastAction = None

        # Create sequential model
        if(model == None):
            self.model = SequentialModel(self.raycastCount+1, self.action_space, self.learningRate)
        else:
            self.model = model
            self.raycastCount = self.model.layers[0].input_shape[1]-1

    # Create raycasts objects
    def createRaycasts(self, simulation):
        space = simulation.space
        points = points_from_poly(self)

        # Calculate raycasts
        a = centerPoint((points[0], points[1]), (points[6], points[7]))
        b = centerPoint((points[4], points[5]), (points[2], points[3]))

        # Calulate origin for vector calc
        origin = (0,0)

        # Normalize vector and prepare it for multiplication
        vectAB = normalizeVector(getVector(a, b))

        # Main vector
        queryVectors = [] 
        queryVectors.append(vectAB)

        # Calculate other vectors
        for i in range(self.raycastCount):
            angle = self.raycastAngle*(i+1)
            multiplier = 1
            # Move vector right to left in circle sectors
            if(i % 2 != 0):
                multiplier = -1
                angle -= self.raycastAngle

            # Sine and Cosine of the angle
            c, s = np.cos(angle*multiplier), np.sin(angle*multiplier)

            # Angle rotation --> Rotation matrix
            x, y = queryVectors[0]
            vectX = x * c - y * s
            vectY = x * s + y * c

            queryVectors.append((vectX, vectY))


        # Check collisions of all vectors
        self.raycastObjects = []
        for vect in queryVectors:
            # Calculate second point with direction vector
            b = (vect[0]*self.raycastLenght+origin[0],vect[1]*self.raycastLenght+origin[1])
            segment = pymunk.Segment(self.body, (0,0), b, 5)
            segment.sensor = True
            segment.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 1 ^ 10)
            segment.rgba = self.raycastColor
            segment.raycast = True
            segment.lastContact = segment.body.local_to_world(b)
            self.raycastObjects.append(segment)
            space.add(segment)

        self.drawRaycasts(simulation.canvasWindow)

    # Calculate distance for every raycast
    def calculateRaycasts(self, space):
        dist = []

        # No raycasts? Return only zeros
        if(self.raycastObjects == []):
            for _ in range(self.raycastCount):
                dist.append(0)
            return np.array([dist])

        # Calculate intersects if raycasts exist
        for raycast in self.raycastObjects:
            # Test query --> collisions
            query = space.segment_query_first(raycast.body.local_to_world(raycast.a), raycast.body.local_to_world(raycast.b), raycast.radius, pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 1 ^ 10))
            # If collisions happened
            if(query):
                # Get point of contant with collidible object
                contact_point = query.point

                # Change graphics representation /Line/
                raycast.lastContact = contact_point
             
                # Calculate distance to the collidible object based on segment query
                dist.append(distXY(raycast.body.local_to_world(raycast.a), contact_point)/self.raycastLenght)
            else:
                dist.append(1)

                # Change graphics representation /Line/
                raycast.lastContact = raycast.body.local_to_world(raycast.b)

        return np.array([dist])

    # Visibility of raycasts --> Requires kivy repaint!
    def raycastsVisibility(self, visibility):
        color = (1,1,1,int(visibility))
        
        self.raycastColor = color
        for raycast in self.raycastObjects:
            raycast.rgba = color

    # Draw raycasts 
    def drawRaycasts(self, canvasHandler):        
        for raycast in self.raycastObjects:
            with canvasHandler.canvas:
                Color(raycast.rgba)
                scalled_points = (raycast.a[0]*canvasHandler.scaller,raycast.a[1]*canvasHandler.scaller,
                                raycast.b[0]*canvasHandler.scaller,raycast.b[1]*canvasHandler.scaller)
                raycast.ky = Line(points=scalled_points, width=raycast.radius*canvasHandler.scaller)


    # Delete raycasts from canvas
    def deleteRaycasts(self, simulation):
        for raycast in self.raycastObjects:
            simulation.space.remove(raycast)
            simulation.canvasWindow.canvas.remove(raycast.ky)

    # Load raycasts
    def loadRaycasts(self, simulation):
        for raycast in self.raycastObjects:
            simulation.space.add(raycast)
            simulation.canvasWindow.canvas.add(Color(rgba=raycast.rgba))
            simulation.canvasWindow.canvas.add(raycast.ky)

    # Calculate distance to nearest finish
    def distToFinish(self, simulation):
        point = simulation.findNearestFinish(self.body.position)
        
        if(point != None):
            return distXY(point, self.body.position)
        else:
            return None

    # Kill the car
    def kill(self, canvasHandler):
        self.isDead = True

    # Create new NN
    def generateRandomBrain(self):
        self.model = SequentialModel(self.raycastCount+1, self.action_space, self.learningRate)

    # Generate random decision
    def randomDecision(self):
        decision = []
        for _ in range(2):
            decision.append(np.random.random())

        return decision

    # Take last action
    def takeLastAction(self):
        if(self.lastAction != None):
            self.think(None, self.lastAction)

    # Makes car think
    def takeAction(self, action=None, dist=None, graph=None):
        # If no action provided, predict here
        if(action == None):
            # Predict action based on rays
            with graph.as_default():
                results = self.model.predict(dist)

            action = np.argmax(results[0])

        # Take appropriate action
        if(action == 0):
            self.forward(6)
        elif(action == 1):
            self.left(1)
            self.forward(6)
        elif(action == 2):
            self.right(1)
            self.forward(6)

        return action