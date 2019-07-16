
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
        self.points = (a[0],a[1],b[0],b[1])
        self.radius = radius
        self.space = space
        self.color = color

    def add(self):
        self.space.add(self.segment)

    def draw(self, canvas):
        with canvas:
            Color(rgba=self.color)
            self.ky = Line(points=self.points, width=self.radius)

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

        space.add(body, shape)

        with self.canvas:
            Color(1,0,0)
            shape.ky = Quad(points=self.points_from_poly(shape))

    def init(self):
        self.step = 1/60.
        self.touches = {}

    def start(self):
        self.space = space = pymunk.Space()
        space.gravity = 0, -600
        space.sleep_time_threshold = 0.3
        space.steps = 0
        
        wall_width = 10
        floors = (Floor(space, (0,0), (900,0), wall_width), Floor(space, (0,0),(0,900),wall_width), Floor(space, (0,900),(900,900),wall_width), Floor(space, (900,0), (900,900), wall_width))


        for floor in floors:
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
        for x in range(2):
            self.space.step(dt)
            self.space.steps += 1

        for shape in self.space.shapes:
            if hasattr(shape, "ky") and not shape.body.is_sleeping:
                if isinstance(shape, pymunk.Circle):
                    body = shape.body
                    shape.ky[0].pos = body.position - (shape.radius, shape.radius)
                    circle_edge = body.position + Vec2d(shape.radius, 0).rotated(body.angle)
                    shape.ky[1].points = [body.position.x, body.position.y, circle_edge.x,   circle_edge.y]
                if isinstance(shape, pymunk.Segment):
                    body = shape.body
                    p1 = body.position + shape.a.cpvrotate(body.rotation_vector)
                    p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                    shape.ky.points = p1.x, p1.y, p2.x, p2.y
                if isinstance(shape, pymunk.Poly):
                    shape.ky.points = self.points_from_poly(shape)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            p = self.to_local(*touch.pos)
            d = self.touches[touch.uid]

            d["line"].points = [d["start"][0] ,d["start"][1], p[0], p[1]]
            self.canvas.remove(d["line"])

            mass = 50
            radius = 15
            moment = pymunk.moment_for_circle(mass, 0, radius)
            b = pymunk.Body(mass, moment)
            s = pymunk.Circle(b, radius)
            s.color = .86,.2,.6
            s.friction = 1
            b.position = d["start"]
            self.space.add(b,s)
            impulse = 200 * (Vec2d(p) - Vec2d(d["start"]))
            b.apply_impulse_at_local_point(impulse)
            with self.canvas:
                Color(*s.color)
                s.ky = self.ellipse_from_circle(s)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            p = self.to_local(*touch.pos)
            d = self.touches[touch.uid]
            d["line"].points = [d["start"][0], d["start"][1], p[0], p[1]]

    def on_touch_down(self, touch):
        touch.grab(self)
        
        p = self.to_local(*touch.pos)
        self.touches[touch.uid] = {"start": p}
            
        with self.canvas:
            Color(1,0,0,0.5)
            line = Line(points = [p[0], p[1], p[0], p[1]], width = 15)
            
            self.touches[touch.uid]["line"] = line

        return True


    def ellipse_from_circle(self, shape):
        pos = shape.body.position - (shape.radius, shape.radius)
        e = Ellipse(pos=pos, size=[shape.radius*2, shape.radius*2])
        circle_edge = shape.body.position + Vec2d(shape.radius, 0).rotated(shape.body.angle)
        Color(.17,.24,.31)
        l = Line(points = [shape.body.position.x, shape.body.position.y, circle_edge.x, circle_edge.y])
        return e,l

    def points_from_poly(self, shape):
        body = shape.body
        ps = [p.rotated(body.angle) + body.position for p in shape.get_vertices()]
        vs = []
        for p in ps:
            vs += [p.x, p.y]
        return vs

#Canvas class
class CanvasWindow(Screen):
    def __init__(self, **kwargs):
        super(CanvasWindow, self).__init__(**kwargs)
        self.game = PymunkDemo()
        self.game.size_hint = 1,1
        self.game.pos = 0,300
        self.add_widget(self.game)
        self.game.init()

    def on_enter(self, **kwargs):
        self.game.start()