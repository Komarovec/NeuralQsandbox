
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
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, Color, Triangle, Quad, Rectangle, Mesh
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

class Floor():
    def __init__(self, space, a, b, radius=1, color=(0.2,0.2,0.2,1), friction=1):
        self.segment = pymunk.Segment(space.static_body, a,b,radius)
        self.segment.friction = friction
        self.segment.elasticity = 0.85
        self.points = (a[0],a[1],b[0],b[1])
        self.radius = radius
        self.space = space
        self.color = color

    def add(self):
        self.space.add(self.segment)

    def draw(self, canvas):
        with canvas:
            Color(rgba=self.color)
            self.segment.ky = Line(points=self.points, width=self.radius)

class PymunkDemo(RelativeLayout):
    def box(self, space):
        mass = 10
        size = (100,50)
        pos = (100,200)

        moment = pymunk.moment_for_box(mass, size)
        body = pymunk.Body(mass, moment)          
        shape = pymunk.Poly.create_box(body, size)
        body.position = pos
        shape.friction = 1
        shape.elasticity = 0.4

        space.add(body, shape)

        with self.canvas:
            Color(1,0,0)
            shape.ky = Quad(points=self.points_from_poly(shape))

    def init(self):
        self.step = 1/60.
        self.touches = {}

    def start(self):
        self.scaller = self.height/1080 + self.width/1920
        self.space = space = pymunk.Space()
        space.gravity = 0, 0
        space.sleep_time_threshold = 0.3
        space.steps = 0
        
        wall_width = 10
        self.floors = (Floor(space, (0,0), (900,0), wall_width), Floor(space, (0,0),(0,900),wall_width), Floor(space, (0,900),(900,900),wall_width), Floor(space, (900,0), (900,900), wall_width))

        for floor in self.floors:
            floor.add()
            floor.draw(self.canvas)

        self.box(space)

        def wrap(f):
            return lambda dt: f(space)

        Clock.schedule_interval(self.update, 1.0 / 1000.)

    def reset(self, *args):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start()

    def update(self, dt):
    
        #Scalling coeficient
        scaller = self.height/2160 + self.width/3840
        
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
                    #Zero-out velocity vector if it is approaching 0
                    if(shape.body.velocity.length < 0.001):
                        shape.body.velocity = Vec2d(0,0)

                    #Apply friction every frame *not frame dependent /dt/*
                    shape.body.velocity *= 1 - (dt*0.80)
                    shape.body.angular_velocity *= 1 - (dt*0.80)

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
                    for floor in self.floors:
                        if(shape.ky == floor.segment.ky):
                            shape.ky.width = floor.radius * self.scaller

                    body = shape.body
                    p1 = body.position + shape.a.cpvrotate(body.rotation_vector) 
                    p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                    shape.ky.points = p1.x * self.scaller, p1.y * self.scaller, p2.x * self.scaller, p2.y * self.scaller
                if isinstance(shape, pymunk.Poly):
                    shape.ky.points = self.points_from_poly(shape)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            p = self.to_local(*touch.pos)
            self.touches[1] = p

            self.pos[0] -= self.touches[0][0]-self.touches[1][0]
            self.pos[1] -= self.touches[0][1]-self.touches[1][1]

    def on_touch_down(self, touch):
        touch.grab(self)
        
        p = self.to_local(*touch.pos)
        self.touches[0] = p

    def ellipse_from_circle(self, shape):
        body = shape.body
        pos = body.position - (shape.radius, shape.radius)
        e = Ellipse(pos=pos * (self.scaller, self.scaller), size=[shape.radius*2*self.scaller, shape.radius*2*self.scaller])
        Color(.17,.24,.31)
        return e

    def points_from_poly(self, shape):
        body = shape.body
        ps = [p.rotated(body.angle) + body.position for p in shape.get_vertices()]
        vs = []
        for p in ps:
            vs += [p.x * self.scaller, p.y * self.scaller]
        return vs

#Canvas class
class CanvasWindow(Screen):
    def __init__(self, **kwargs):
        super(CanvasWindow, self).__init__(**kwargs)
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,0
        self.add_widget(self.game)
        self.game.init()

    def on_enter(self, **kwargs):
        self.game.start()