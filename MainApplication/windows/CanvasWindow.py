
import random
random.seed(5)

import kivy
kivy.require('1.0.7')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.actionbar import ActionBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, Color, Triangle, Quad, Rectangle, Mesh
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

import math

#Custom function and classes
from objs.Car import Car
from objs.Barrier import Barrier
from objs.kivyObjs import ellipse_from_circle, points_from_poly


class PymunkDemo(RelativeLayout):
    def init(self):
        #Important values
        self.step = 1/60.
        self.touches = {}
        self.keys = {"up" : 0, "down" : 0, "left" : 0, "right" : 0}
        self.scallerVar = 3000

        #Level editor vals
        self.add_barrier = False
        self.adding_barrier = False
        self.temp_barrier = None
        
        self.delete = False

    def start(self):
        #Setting up few things
        self.scaller = self.height/self.scallerVar + self.width/self.scallerVar
        self.space = space = pymunk.Space()

        self.handler = space.add_default_collision_handler()
        self.handler.begin = self.coll_begin
        self.handler.pre_solve = self.coll_pre
        self.handler.post_solve = self.coll_post
        self.handler.separate = self.coll_separate

        space.gravity = 0, 0
        space.sleep_time_threshold = 0.3
        space.steps = 0

        #Keyboard listener
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        #Spawning objects
        car = Car(self.canvas, self.scaller, 10, (100,50), (300,250), ground_friction=1, angular_friction=3)
        barriers = [Barrier(self.canvas, (0,0), (2000,0), 20), Barrier(self.canvas, (2000,0), (2000,1000), 20), Barrier(self.canvas, (2000,1000), (0,1000), 20), Barrier(self.canvas, (0,0), (0,1000), 20)]

        for barrier in barriers:
            self.space.add(barrier)

        self.space.add(car.body, car)

        #No idea
        def wrap(f):
            return lambda dt: f(space)

        #Set time clock
        Clock.schedule_interval(self.update, 1.0 / 10000)

    def reset(self, *args):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start()

    def update(self, dt):
        #Debug vypis
        if(self.space.steps % 100 == 0):
            print(self.keys)

        #--- Controls ----
        #Barrier editing
        if(self.adding_barrier):
            if(self.keys["up"] == 1):
                if(self.temp_barrier.width < 100):
                    self.temp_barrier.width += 1
            elif(self.keys["down"] == 1):
                if(self.temp_barrier.width > 1):
                    self.temp_barrier.width -= 1
        
        #Car control <---- MOVE TO CAR CLASS
        else:
            for shape in self.space.shapes:
                if isinstance(shape, Car):
                    if(self.keys["up"] == 1):
                        shape.body.apply_force_at_local_point(Vec2d(shape.forward_speed*dt*100,0), (0,0))
                    if(self.keys["down"] == 1):
                        shape.body.apply_force_at_local_point(Vec2d(-shape.backward_speed*dt*100,0), (0,0))
                    if(self.keys["left"] == 1):
                        shape.body.apply_force_at_local_point(Vec2d(-shape.angular_speed*dt*100,0), (0,shape.size[0]))
                        shape.body.apply_force_at_local_point(Vec2d(shape.angular_speed*dt*100,0), (0,-shape.size[0]))
                    if(self.keys["right"] == 1):
                        shape.body.apply_force_at_local_point(Vec2d(shape.angular_speed*dt*100,0), (0,shape.size[0]))
                        shape.body.apply_force_at_local_point(Vec2d(-shape.angular_speed*dt*100,0), (0,-shape.size[0]))

        #Scalling coeficient
        scaller = self.height/self.scallerVar + self.width/self.scallerVar
        
        #If resolution has changed change scaling on all shapes
        if(scaller != self.scaller):
            self.scaller = scaller
            scallerChanged = True
        else:
            scallerChanged = False

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

        #Move all shapes in kivy based on bodies --> calculated objects, Also scale everything --> scaller
        for shape in self.space.shapes:
            if(hasattr(shape, "ky") and (not shape.body.is_sleeping or scallerChanged)):
                if isinstance(shape, pymunk.Circle):
                    body = shape.body
                    shape.ky.size = [shape.radius*2*self.scaller, shape.radius*2*self.scaller]
                    shape.ky.pos = (body.position - (shape.radius, shape.radius)) * (self.scaller, self.scaller)

                if isinstance(shape, pymunk.Segment):
                    #If Is barrier class than increase width by scaller
                    if isinstance(shape, Barrier):
                        shape.ky.width = shape.rad * self.scaller

                    body = shape.body
                    p1 = body.position + shape.a.cpvrotate(body.rotation_vector) 
                    p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                    shape.ky.points = p1.x * self.scaller, p1.y * self.scaller, p2.x * self.scaller, p2.y * self.scaller

                if isinstance(shape, pymunk.Poly):
                    shape.ky.points = points_from_poly(shape, scaller)

    #Level editor
    def addBarrier(self):
        self.add_barrier = True

    def deleteObject(self):
        self.delete = True

    #Collistions handlers
    def coll_begin(self, arbiter, space, data):
        print(arbiter.shapes)
        return True

    def coll_pre(self, arbiter, space, data):
        print("Pre solve")
        return True

    def coll_post(self, arbiter, space, data):
        print("Post solve")

    def coll_separate(self, arbiter, space, date):
        print("Separated")


    #Interface functions
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        elif(self.adding_barrier):
            #Delete temp line when cursor removed
            self.add_barrier = False
            self.adding_barrier = False

            self.space.add(Barrier(self.canvas, (self.temp_barrier.points[0]/self.scaller, 
                                                self.temp_barrier.points[1]/self.scaller), 
                                                (self.temp_barrier.points[2]/self.scaller, 
                                                self.temp_barrier.points[3]/self.scaller), 
                                                self.temp_barrier.width/self.scaller))

            self.canvas.remove(self.temp_barrier)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            p = self.to_local(*touch.pos)
            self.touches[1] = p

            self.pos[0] -= self.touches[0][0]-self.touches[1][0]
            self.pos[1] -= self.touches[0][1]-self.touches[1][1]
        elif(self.adding_barrier):
            p = self.to_local(*touch.pos)
            self.touches[1] = p

            #Update line when moved
            self.temp_barrier.points = [self.touches[0][0], self.touches[0][1], p[0], p[1]]

    def on_touch_down(self, touch):
        #Scale screen if mouse scroll
        if(touch.button == "scrolldown"):
            if(self.scallerVar > 100):
                self.scallerVar -= 100
        elif(touch.button == "scrollup"):
            if(self.scallerVar < 10000):
                self.scallerVar += 100

        #Save current pos
        p = self.to_local(*touch.pos)
        self.touches[0] = p

        #If AddBarrier was clicked on, draw a line
        if(self.add_barrier):
            self.adding_barrier = True
            with self.canvas:
                Color(1,0,0,0.5)
                line = Line(points = [p[0], p[1], p[0], p[1]], width = 15)
            
            self.temp_barrier = line
        elif(self.delete):
            deletePoint = (p[0]/self.scaller, p[1]/self.scaller)

            for shape in self.space.shapes:
                if(shape.point_query(deletePoint)[0] < 0):
                    self.space.remove(shape)
                    self.canvas.remove(shape.ky)

            self.delete = False
        else:    
            touch.grab(self)

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_up(self, keyboard, keycode):
        self.keys[keycode[1]] = 0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keys[keycode[1]] = 1


#Main class
class CanvasWindow(Screen):
    def __init__(self, **kwargs):
        super(CanvasWindow, self).__init__(**kwargs)

    def on_enter(self, **kwargs):
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,0
        self.add_widget(self.game, 10)
        self.game.init()
        self.game.start()

    def on_leave(self, **kwargs):
        self.remove_widget(self.game)

    def levelEdit(self):
        print("level edit!")

    def reset(self):
        self.remove_widget(self.game)
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,0
        self.add_widget(self.game, 10)
        self.game.init()
        self.game.start()