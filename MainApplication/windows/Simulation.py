
import random
random.seed(5)

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

import math

#Custom function and classes
from objs.GameObjects import StaticGameObject
from objs.Car import Car


class Simulation():
    def __init__(self, canvasWindow):
        #Important values
        self.step = 1/60.
        self.canvasWindow = canvasWindow

    def setupSpace(self):
        self.space = space = pymunk.Space()

        self.handler = space.add_default_collision_handler()
        self.handler.begin = self.coll_begin
        self.handler.pre_solve = self.coll_pre
        self.handler.post_solve = self.coll_post
        self.handler.separate = self.coll_separate

        space.gravity = 0, 0
        space.sleep_time_threshold = 0.3
        space.steps = 0

        return space

    def start(self):
        space = self.setupSpace()

        #Spawning objects
        StaticGameObject(StaticGameObject.BARRIER).createSegment((0,0), (2000,0), 20, self.canvasWindow)
        StaticGameObject(StaticGameObject.BARRIER).createSegment((2000,0), (2000,1000), 20, self.canvasWindow)
        StaticGameObject(StaticGameObject.BARRIER).createSegment((2000,1000), (0,1000), 20, self.canvasWindow)
        StaticGameObject(StaticGameObject.BARRIER).createSegment((0,0), (0,1000), 20, self.canvasWindow)
        
        start = StaticGameObject(StaticGameObject.START, rgba=(0,.8,0,.8))
        start.createSegment((100,400), (100,600), 20, self.canvasWindow)

        finish = StaticGameObject(StaticGameObject.FINISH, rgba=(.8,0,0,.8))
        finish.createSegment((1800,400), (1800,600), 20, self.canvasWindow)
        
        car = Car(10, (100,50), (100,100), ground_friction=1, angular_friction=3)
        self.space.add(car.body, car)
        car.paint(self.canvasWindow)

        #No idea
        def wrap(f):
            return lambda dt: f(space)

    def update(self, dt):
        #Physics simulation
        for x in range(2):
            for shape in self.space.shapes:
                if(not shape.body.is_sleeping):
                    #If there is friction set by class use it
                    if(isinstance(shape, Car)):
                        friction = shape.ground_friction
                        angular_friction = shape.angular_friction
                    else:
                        friction = 0.9
                        angular_friction = 0.9

                    #Zero-out velocity vector if it is approaching 0
                    if(shape.body.velocity.length < 0.001):
                        shape.body.velocity = Vec2d(0,0)

                    #Apply friction every frame *not frame dependent /dt/*
                    shape.body.velocity *= 1 - (dt*friction)
                    shape.body.angular_velocity *= 1 - (dt*angular_friction)

            #Stepping space simul
            self.space.step(dt)
            self.space.steps += 1

    #Adding
    def addStaticGameObject(self, a, b, radius):
        #StaticGameObject(StaticGameObject.BARRIER).createSegment(a, b, radius, self.canvasWindow)
        #StaticGameObject(StaticGameObject.BARRIER).createCircle(a, radius, self.canvasWindow)
        StaticGameObject(StaticGameObject.BARRIER).createBox(a, (100,50), self.canvasWindow)

    #Collistions handlers
    def coll_begin(self, arbiter, space, data):
        if((isinstance(arbiter.shapes[0], Car) and isinstance(arbiter.shapes[1], pymunk.Segment)) or (isinstance(arbiter.shapes[1], Car) and isinstance(arbiter.shapes[0], pymunk.Segment))):        
            car = None
            if(isinstance(arbiter.shapes[0], Car)):
                car = arbiter.shapes[0]
                if(arbiter.shapes[1].objectType != StaticGameObject.FINISH):
                    return True
            else:
                car = arbiter.shapes[1]
                if(arbiter.shapes[0].objectType != StaticGameObject.FINISH):
                    return True

            for shape in self.space.shapes:
                if(hasattr(shape, "objectType")):
                    if(shape.objectType == StaticGameObject.START):
                        car.body.position = ((shape.a[0]+shape.b[0])/2, (shape.a[1]+shape.b[1])/2)

        return True

    def coll_pre(self, arbiter, space, data):
        return True

    def coll_post(self, arbiter, space, data):
        pass

    def coll_separate(self, arbiter, space, date):
        pass
