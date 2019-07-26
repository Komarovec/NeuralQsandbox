
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
from objs.GameObjects import Barrier, Start, Finish
from objs.Car import Car
from objs.kivyObjs import ellipse_from_circle, points_from_poly, newRectangle


class PymunkDemo(RelativeLayout):
    def init(self):
        #Important values
        self.step = 1/60.
        self.touches = {}
        self.keys = {"up" : 0, "down" : 0, "left" : 0, "right" : 0}
        self.scallerVar = 5000
        self.state = "game"

        #Level editor vals
        #Adding barrier
        self.add_barrier = False
        self.adding_barrier = False
        self.temp_barrier = None
        
        #Deleting objects
        self.deleteObject = False

        #Moving objects
        self.movingObject = False
        self.movingVar = None
        self.movingPoint = None

        #Highlighted object
        self.tempHighlight = None

    def start(self):
        texture = CoreImage('textures/carTexture.png').texture
        #texture.uvsize = (1,1)

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

        #Keyboard/Mouse listener
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        #Spawning objects
        barriers = [Barrier(self.canvas, self.scaller, (0,0), (2000,0), 20), Barrier(self.canvas, self.scaller, (2000,0), (2000,1000), 20), Barrier(self.canvas, self.scaller, (2000,1000), (0,1000), 20), Barrier(self.canvas, self.scaller, (0,0), (0,1000), 20)]
        start = Start(self.canvas, self.scaller, (100,400), (100,600), 30, rgba=(0,0.6,0,0.6))
        finish = Finish(self.canvas, self.scaller, (1800,400), (1800,600), 30, rgba=(0.6,0,0,0.6))
        car = Car(self.canvas, self.scaller, texture, 10, (100,50), ((start.a[0]+start.b[0])/2, (start.a[1]+start.b[1])/2), ground_friction=1, angular_friction=3)

        for barrier in barriers:
            self.space.add(barrier)
        self.space.add(start.body, start)
        self.space.add(finish.body, finish)
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
        #Scalling coeficient
        scaller = self.height/self.scallerVar + self.width/self.scallerVar
        
        #If resolution has changed change scaling on all shapes
        if(scaller != self.scaller):
            self.scaller = scaller
            scallerChanged = True
        else:
            scallerChanged = False

        #---- Controls ----
        #Barrier adding
        if(self.temp_barrier != None):
            if(self.keys["up"] == 1):
                if(self.temp_barrier.width/self.scaller < 100):
                    self.temp_barrier.width += 1
            elif(self.keys["down"] == 1):
                if(self.temp_barrier.width/self.scaller > 1 and self.temp_barrier.width > 1):
                    self.temp_barrier.width -= 1

        #Car control + Highligting
        else:
            pos = self.to_local(*Window.mouse_pos)
            pos = (pos[0]/self.scaller, pos[1]/self.scaller)

            for shape in self.space.shapes:
                #Highlight object ONLY in level editor
                if(self.state == "editor" and not self.movingObject):
                    #Highlight hover objects
                    if(shape.point_query(pos)[0] < 0):
                        if(self.tempHighlight != None):
                            self.canvas.remove(self.tempHighlight)
                            self.tempHighlight = None

                        if(isinstance(shape, pymunk.Segment)):
                            with self.canvas:
                                Color(0.6,0.6,0.6,0.6)
                                self.tempHighlight = Line(points=shape.ky.points, width=shape.ky.width)
                        if(isinstance(shape, Car)):
                            with self.canvas:
                                Color(0.6,0.6,0.6,0.6)
                                self.tempHighlight = newRectangle(shape, scaller)
                        break

                    #Cleanup
                    elif(self.tempHighlight != None):
                        self.canvas.remove(self.tempHighlight)
                        self.tempHighlight = None
                elif(self.tempHighlight != None):
                    self.canvas.remove(self.tempHighlight)
                    self.tempHighlight = None

                #Car control
                if isinstance(shape, Car):
                    if(self.keys["up"] == 1):
                        shape.forward(dt*100)
                    if(self.keys["down"] == 1):
                        shape.backward(dt*100)
                    if(self.keys["left"] == 1):
                        shape.left(dt*100)
                    if(self.keys["right"] == 1):
                        shape.right(dt*100)


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

        #Repaint all graphics
        for shape in self.space.shapes:
            if(hasattr(shape, "ky") and (not shape.body.is_sleeping or scallerChanged)):
                if isinstance(shape, pymunk.Circle):
                    body = shape.body
                    shape.ky.size = [shape.radius*2*self.scaller, shape.radius*2*self.scaller]
                    shape.ky.pos = (body.position - (shape.radius, shape.radius)) * (self.scaller, self.scaller)

                if isinstance(shape, pymunk.Segment):
                    #If Is barrier class than increase width by scaller
                    shape.ky.width = shape.radius * self.scaller

                    body = shape.body
                    p1 = body.position + shape.a.cpvrotate(body.rotation_vector) 
                    p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                    shape.ky.points = p1.x * self.scaller, p1.y * self.scaller, p2.x * self.scaller, p2.y * self.scaller

                if isinstance(shape, pymunk.Poly):
                    shape.ky.points = points_from_poly(shape, scaller)

    #Level editor
    def addObject(self, obj):
        self.add_barrier = True

    #Collistions handlers
    def coll_begin(self, arbiter, space, data):
        if((isinstance(arbiter.shapes[0], Car) and isinstance(arbiter.shapes[1], Finish)) or (isinstance(arbiter.shapes[1], Car) and isinstance(arbiter.shapes[0], Finish))):
            car = None
            if(isinstance(arbiter.shapes[0], Car)):
                car = arbiter.shapes[0]
            else:
                car = arbiter.shapes[1]

            for shape in self.space.shapes:
                if(isinstance(shape, Start)):
                    car.body.position = ((shape.a[0]+shape.b[0])/2, (shape.a[1]+shape.b[1])/2)

        return True

    def coll_pre(self, arbiter, space, data):
        return True

    def coll_post(self, arbiter, space, data):
        pass

    def coll_separate(self, arbiter, space, date):
        pass


    #Interface functions
    def on_touch_up(self, touch):
        if(touch.button == "scrolldown" or touch.button == "scrollup"):
            return

        #Ungrab screen when stopped touching
        if touch.grab_current is self:
            touch.ungrab(self)
        
        #Create body for barrier and place it in place
        elif(self.adding_barrier):
            #Delete temp line when cursor removed
            self.add_barrier = False
            self.adding_barrier = False

            self.space.add(Barrier(self.canvas, self.scaller, (self.temp_barrier.points[0]/self.scaller, 
                                                self.temp_barrier.points[1]/self.scaller), 
                                                (self.temp_barrier.points[2]/self.scaller, 
                                                self.temp_barrier.points[3]/self.scaller), 
                                                self.temp_barrier.width/self.scaller))

            self.canvas.remove(self.temp_barrier)
            self.temp_barrier = None

        #Stop moving
        elif(self.movingObject):
            self.movingObject = False
            self.movingVar = None
            self.movingPoint = None

    def on_touch_move(self, touch):
        if(touch.button == "scrolldown" or touch.button == "scrollup"):
            return

        p = self.to_local(*touch.pos)
        self.touches[1] = p

        #Move screen when grabbed
        if touch.grab_current is self:
            self.pos[0] -= self.touches[0][0]-self.touches[1][0]
            self.pos[1] -= self.touches[0][1]-self.touches[1][1]
        
        #If adding_barrier then show "pre barrier"
        elif(self.adding_barrier):
            #Update line when moved
            self.temp_barrier.points = [self.touches[0][0], self.touches[0][1], p[0], p[1]]

        #If move, move clicked on object
        elif(self.movingObject):
            if(isinstance(self.movingVar, Car)):
                p_scaled = (p[0]/self.scaller,p[1]/self.scaller)
                self.movingVar.body.position = p_scaled 
            if(isinstance(self.movingVar, pymunk.Segment)):
                #Move whole thing
                if(touch.is_double_tap):
                    if(self.movingPoint == "a"):
                        self.movingVar.unsafe_set_endpoints((p[0]/self.scaller, p[1]/self.scaller), self.movingVar.b)
                    else:
                        self.movingVar.unsafe_set_endpoints(self.movingVar.a, (p[0]/self.scaller, p[1]/self.scaller))
                
                #Move only one point (closest)
                else:
                    center_vector = ((self.movingVar.a[0]-self.movingVar.b[0])/2, (self.movingVar.a[1]-self.movingVar.b[1])/2)
                    self.movingVar.unsafe_set_endpoints(((p[0]/self.scaller)+center_vector[0], (p[1]/self.scaller)+center_vector[1]), ((p[0]/self.scaller)-center_vector[0], (p[1]/self.scaller)-center_vector[1]))
                
                self.space.reindex_shapes_for_body(self.movingVar.body)


    def on_touch_down(self, touch):
        #Scale screen if mouse scroll
        if(touch.button == "scrolldown"):
            if(self.scallerVar > 100):
                self.scallerVar -= 100
        elif(touch.button == "scrollup"):
            if(self.scallerVar < 10000):
                self.scallerVar += 100

        #Cancel if right button
        if(touch.button == "right"):
            self.add_barrier = False
            self.deleteObject = False

        #Save current pos
        p = self.to_local(*touch.pos)
        self.touches[0] = p


        if(self.state == "editor" and touch.button == "left"):
            #If AddBarrier was clicked on, draw a line
            if(self.add_barrier):
                self.adding_barrier = True
                with self.canvas:
                    Color(1,0,0,0.5)
                    line = Line(points = [p[0], p[1], p[0], p[1]], width = 10)
                
                self.temp_barrier = line

            #Delete Object
            elif(self.deleteObject):
                deletePoint = (p[0]/self.scaller, p[1]/self.scaller)

                for shape in self.space.shapes:
                    if(shape.point_query(deletePoint)[0] < 0):
                        self.space.remove(shape)
                        self.canvas.remove(shape.ky)

                self.deleteObject = False

            #Move object
            else:
                movePoint = (p[0]/self.scaller, p[1]/self.scaller)
                for shape in self.space.shapes:
                    if(shape.point_query(movePoint)[0] < 0):
                        self.movingObject = True

                        #Move depending on the type
                        if(isinstance(shape, Car)):
                            self.movingVar = shape
                        if(isinstance(shape, pymunk.Segment)):
                            #Use nearest endpoint
                            self.movingVar = shape
                            p1 = movePoint
                            p2 = shape.a
                            p3 = shape.b
                            distance1 = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
                            distance2 = math.sqrt(((p1[0]-p3[0])**2)+((p1[1]-p3[1])**2))
                            if(distance1 < distance2):
                                self.movingPoint = "a"
                            else:
                                self.movingPoint = "b"
                
                if(not self.movingObject):
                    touch.grab(self)
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


    def reset(self):
        self.remove_widget(self.game)
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,0
        self.add_widget(self.game, 10)
        self.game.init()
        self.game.start()