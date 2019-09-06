import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Quad, Line

import math
import numpy as np

#Custom functions and classes
from objs.Car import Car
from objs.kivyObjs import points_from_poly, centerPoint, getVector, normalizeVector, distXY
from ai.Models import NeuralModel

class CarAI(Car):
    CARAI = "carai"

    def __init__(self, mass=10, size=(100,50), pos=(100,100), friction=1, ground_friction=0.9, angular_friction=0.9, forward_speed = 5000, backward_speed = 5000, angular_speed = 500, elasticity=0.4, rgba=(0.8,0,0,1), texture=None):
        super(CarAI, self).__init__(mass, size, pos, friction, ground_friction, angular_friction, forward_speed, backward_speed, angular_speed, elasticity, rgba, texture)
        self.objectType = self.CARAI
        self.raycastLenght = 2000
        self.raycastAngle = np.radians(30)
        self.raycastCount = 2
        self.raycastObjects = []

        #Kivy
        self.raycastsKivy = []

        #AI
        self.brain = None
        self.isDead = False

    #Calculate distance for every raycast
    def calculateRaycasts(self, space):
        dist = []
        points = points_from_poly(self)

        #Calculate raycasts
        a = centerPoint((points[0], points[1]), (points[6], points[7]))
        b = centerPoint((points[4], points[5]), (points[2], points[3]))

        #Calulate origin for vector calc
        origin = centerPoint(a, b)

        #Normalize vector and prepare it for multiplication
        vectAB = normalizeVector(getVector(a, b))

        #Main vector
        queryVectors = [] 
        queryVectors.append(vectAB)

        #Calculate other vectors
        for i in range(self.raycastCount):
            angle = self.raycastAngle*(i+1)
            multiplier = 1
            #Move vector right to left in circle sectors
            if(i % 2 != 0):
                multiplier = -1
                angle -= self.raycastAngle

            #Sine and Cosine of the angle
            c, s = np.cos(angle*multiplier), np.sin(angle*multiplier)

            #Angle rotation --> Rotation matrix
            x, y = queryVectors[0]
            vectX = x * c - y * s
            vectY = x * s + y * c

            queryVectors.append((vectX, vectY))


        #Check collisions of all vectors
        self.raycastObjects = []
        for vect in queryVectors:
            #Calculate second point with direction vector
            b = (vect[0]*self.raycastLenght+origin[0],vect[1]*self.raycastLenght+origin[1])

            #Test query --> collisions
            query = space.segment_query_first(origin, b, 1, pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 1))

            #If collisions happened
            if(query):
                #Get point of contant with collidible object
                contant_point = query.point
                segment = pymunk.Segment(space.static_body, origin, contant_point, 3)
                segment.sensor = True
                self.raycastObjects.append(segment)

                #Calculate distance to the collidible object based on segment query
                dist.append(distXY(origin, contant_point)/self.raycastLenght)
            else:
                dist.append(1)

        return dist

    #Draw raycasts !!! WIP !!! DO NOT USE
    def drawRaycasts(self, canvasHandler):
        for ky in self.raycastsKivy:
            canvasHandler.canvas.remove(ky)
        
        self.raycastsKivy = []

        for rcObj in self.raycastObjects:
            with canvasHandler.canvas:
                Color(rgba=(1,1,1,1))
                scalled_points = (rcObj.a[0]*canvasHandler.scaller,rcObj.a[1]*canvasHandler.scaller,
                                rcObj.b[0]*canvasHandler.scaller,rcObj.b[1]*canvasHandler.scaller)

                self.raycastsKivy.append(Line(points=scalled_points, width=rcObj.radius*canvasHandler.scaller))

    #Calculate distance to nearest finish
    def distToFinish(self, simulation):
        point = simulation.findNearestFinish(self.body.position)
        
        if(point != None):
            return distXY(point, self.body.position)
        else:
            return None

    #Kill the car
    def kill(self):
        self.isDead = True

    #Respawn at the first spawnpoint in shapes array
    def respawn(self, simulation):
        self.body.position = simulation.findSpawnpoint()
        self.body.angle = 0
        self.body.velocity = (0,0)
        
        self.isDead = False

    #Create new NN !!WIP!!
    def generateRandomBrain(self):
        self.brain = NeuralModel()

    def think(self, rc):
        #Predict action based on rays
        results = self.brain.predict(rc)
        results = results[0]

        maxIndex = np.argmax(results)

        #return results

        #Take action --> One-hot results
        self.forward(0.1)
        if(maxIndex == 0):
            self.forward(1)
            results = [1,0,0,0]

        elif(maxIndex == 1):
            self.backward(1)
            results = [0,1,0,0]

        elif(maxIndex == 2):
            self.left(1)
            results = [0,0,1,0]

        elif(maxIndex == 3):
            self.right(1)
            results = [0,0,0,1]

        return results