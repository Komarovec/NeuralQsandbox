
"""A rudimentary port of the intro video used for the intro animation on 
pymunk.org. The code is tested on both Windows and Android.
Note that it doesn't display Kivy best practices, the intro_video 
code was just converted to Kivy in the most basic way to show that its possible,
its not supposed to show the best way to structure a Kivy application using 
Pymunk.
"""
__version__ = "0.1.2"

# python main.py -m screen:iphone4,portrait

import random
random.seed(5)

import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, Color, Triangle, Quad, Rectangle
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

class PymunkDemo(RelativeLayout):
    def big_ball(self, space):
        mass = 1
        radius = 50
        moment = pymunk.moment_for_circle(mass, 0, radius)
        b = pymunk.Body(mass, moment)
        c = pymunk.Circle(b, radius)
        c.friction = 10
        c.color = 255,0,0
        b.position = 300, 200

        space.add(b,c)
        
        with self.canvas:
            Color(1,0,0)
            c.ky = self.ellipse_from_circle(c)

    def init(self):
        self.start()

    def start(self):
        self.space = space = pymunk.Space()
        space.gravity = 0, -900
        space.sleep_time_threshold = 0.3
        space.steps = 0

        # we use our own event scheduling to make sure a event happens exactly 
        # after X amount of simulation steps
        self.events = []
        self.events.append((10, self.big_ball))

        self.update_event = Clock.schedule_interval(self.update, 1.0 / 20.)

    def reset(self, *args):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start()

    def update(self, dt):
        stepdelay = 25
        space.step(0.02)

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


class MyApp(App):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        Window.set_title("Pymunk demo")
        demo = PymunkDemo()
        demo.size_hint = 1,1
        demo.init()
        demo.pos = 0,300
        l = FloatLayout()
        l.add_widget(demo)
        return l
        
if __name__ == '__main__':
    MyApp().run()