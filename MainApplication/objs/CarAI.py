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
        self.raycastsToRemove = []

    def calculateRaycasts(self, space):
        dist = []
        points = points_from_poly(self)
        
        #Save raycast kivy
        kivy = []
        for raycastObject in self.raycastObjects:
            if(hasattr(raycastObject, "ky")):
                kivy.append(raycastObject.ky)


        #Calculate raycasts
        a = centerPoint((points[0], points[1]), (points[6], points[7]))
        b = centerPoint((points[4], points[5]), (points[2], points[3]))
        origin = centerPoint(a, b)
        vectAB = normalizeVector(getVector(a, b))

        #Main vector
        queryVectors = [] 
        queryVectors.append((vectAB[0]*self.raycastLenght+origin[0],vectAB[1]*self.raycastLenght+origin[1]))

        #Calculate other vectors
        for i in range(self.raycastCount):
            angle = self.raycastAngle*(i+1)
            multiplier = 1
            if(i % 2 != 0):
                multiplier = -1
                angle -= self.raycastAngle

            #Sine and Cosine of the angle
            c, s = np.cos(angle*multiplier), np.sin(angle*multiplier)

            #Angle rotation
            x, y = queryVectors[0]
            vectX = x * c - y * s
            vectY = x * s + y * c

            queryVectors.append((vectX, vectY))


        #Check collisions of all vectors
        queries = []
        for vect in queryVectors:
            queries.append(space.segment_query_first(origin, vect, 1, pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 1)))

        #Check raycast collision detection
        self.raycastObjects = []
        for query in queries:
            if(query):
                contant_point = query.point
                self.raycastObjects.append(pymunk.Segment(space.static_body, origin, contant_point, 1))
                dist.append(distXY(origin, contant_point)/self.raycastLenght)

        #Add kivy to all segments
        for index, rcObj in enumerate(self.raycastObjects):
            rcObj.sensor = True

            if(len(kivy) > index):
                rcObj.ky = kivy[index]
            else:
                rcObj.ky = None

        return dist

    def drawRaycasts(self, canvasHandler):
        for rcObj in self.raycastObjects:
            with canvasHandler.canvas:
                Color(rgba=(1,1,1,1))
                scalled_points = (rcObj.a[0]*canvasHandler.scaller,rcObj.a[1]*canvasHandler.scaller,
                                rcObj.b[0]*canvasHandler.scaller,rcObj.b[1]*canvasHandler.scaller)

                if(rcObj.ky != None):
                    rcObj.ky.points = scalled_points
                else:
                    rcObj.ky = Line(points=scalled_points, width=rcObj.radius*canvasHandler.scaller)

        for ky in self.raycastsToRemove:
            canvasHandler.canvas.remove(ky)
        
        self.raycastsToRemove = []