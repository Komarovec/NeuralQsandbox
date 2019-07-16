
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
from kivy.graphics import Ellipse, Line, Color, Triangle, Quad, Rectangle
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

class PymunkDemo(RelativeLayout):
    def small_ball(self, space):
        for x in range(10):
            mass = 3
            radius = 8
            moment = pymunk.moment_for_circle(mass, 0, radius)
            b = pymunk.Body(mass, moment)
            c = pymunk.Circle(b, radius)
            c.friction = 1
            x = random.randint(100, 350)
            y = random.randint(300, 340)
            b.position = x,y

            space.add(b,c)

            with self.canvas:
                Color(.2,.6,.86)
                c.ky = self.ellipse_from_circle(c)
            
    def big_ball(self, space):
        mass = 1000
        radius = 50
        moment = pymunk.moment_for_circle(mass, 0, radius)
        b = pymunk.Body(mass, moment)
        c = pymunk.Circle(b, radius)
        c.friction = 1
        c.color = 255,0,0
        b.position = 800, 200
        b.apply_impulse_at_local_point((-10000,0),(0,1000))

        space.add(b,c)
        
        with self.canvas:
            Color(1,0,0)
            c.ky = self.ellipse_from_circle(c)
        

    def boxfloor(self, space):
        mass = 10
        vs = [(-50,30),(60,22),(-50, 22)]
        
        moment = pymunk.moment_for_poly(mass, vs)
        b = pymunk.Body(mass, moment)
        s = pymunk.Poly(b, vs)
        s.friction = 1
        s.color = 0,0,0
        b.position = 600,250

        space.add(b,s)
        with self.canvas:
            Color(0.2,0.2,0.2)
            s.ky = Triangle(points=self.points_from_poly(s))

    
    def box(self, space):        
        mass = 10
        moment = pymunk.moment_for_box(mass, (40,20))
        b = pymunk.Body(mass, moment)
        s = pymunk.Poly.create_box(b, (40,20))
        s.friction = 1
        b.position = 600, self.box_y
        self.box_y += 30
        space.add(b,s)
        
        with self.canvas:
            Color(0.2,0.2,0.2)
            s.ky = Quad(points=self.points_from_poly(s))


    def car(self, space):
        pos = Vec2d(100,100)

        wheel_color = .2,.86,.47
        shovel_color = .86,.47,.2
        mass = 100
        radius = 25
        moment = pymunk.moment_for_circle(mass, 20, radius)
        wheel1_b = pymunk.Body(mass, moment)
        wheel1_s = pymunk.Circle(wheel1_b, radius)
        wheel1_s.friction = 1.5
        wheel1_s.color = wheel_color
        space.add(wheel1_b, wheel1_s)

        mass = 100
        radius = 25
        moment = pymunk.moment_for_circle(mass, 20, radius)
        wheel2_b = pymunk.Body(mass, moment)
        wheel2_s = pymunk.Circle(wheel2_b, radius)
        wheel2_s.friction = 1.5
        wheel2_s.color = wheel_color
        space.add(wheel2_b, wheel2_s)

        mass = 100
        size = (50,30)
        moment = pymunk.moment_for_box(mass, size)
        chassi_b = pymunk.Body(mass, moment)
        chassi_s = pymunk.Poly.create_box(chassi_b, size)
        space.add(chassi_b, chassi_s)

        vs = [(0,0),(0,-45),(25,-45)]
        shovel_s = pymunk.Poly(chassi_b, vs, transform = pymunk.Transform(tx=85))
        shovel_s.friction = 0.5
        shovel_s.color = shovel_color
        space.add(shovel_s)

        wheel1_b.position = pos - (55,0)
        wheel2_b.position = pos + (55,0)
        chassi_b.position = pos + (0,25)

        space.add(
            pymunk.PinJoint(wheel1_b, chassi_b, (0,0), (-25,-15)),
            pymunk.PinJoint(wheel1_b, chassi_b, (0,0), (-25, 15)),
            pymunk.PinJoint(wheel2_b, chassi_b, (0,0), (25,-15)),
            pymunk.PinJoint(wheel2_b, chassi_b, (0,0), (25, 15))
            )
        
        speed = -4
        space.add(
            pymunk.SimpleMotor(wheel1_b, chassi_b, speed),
            pymunk.SimpleMotor(wheel2_b, chassi_b, speed)
        )
        with self.canvas:
            Color(*wheel_color)
            wheel1_s.ky = self.ellipse_from_circle(wheel1_s)
            Color(*wheel_color)
            wheel2_s.ky = self.ellipse_from_circle(wheel2_s)
            Color(*shovel_color)
            chassi_s.ky = Quad(points=self.points_from_poly(chassi_s))
            shovel_s.ky = Triangle(points=self.points_from_poly(shovel_s))

    def cannon(self, space):
        mass = 100
        radius = 15
        moment = pymunk.moment_for_circle(mass, 0, radius)
        b = pymunk.Body(mass, moment)
        s = pymunk.Circle(b, radius)
        s.color = .86,.2,.6
        b.position = 700, 400
        space.add(b,s)
        impulse = Vec2d(-200000,-75000)
        b.apply_impulse_at_local_point((impulse))
        with self.canvas:
            Color(*s.color)
            s.ky = self.ellipse_from_circle(s)

        line_set = pymunk.autogeometry.PolylineSet()
        def segment_func(v0, v1):
                line_set.collect_segment(v0, v1)
        
        r = 10
        
        lines = []
        for line in line_set:
            line = pymunk.autogeometry.simplify_curves(line, .7)
            
            max_x = 0
            min_x = 1000
            max_y = 0
            min_y = 1000
            for l in line:
                max_x = max(max_x, l.x)
                min_x = min(min_x, l.x)
                max_y = max(max_y, l.y)
                min_y = min(min_y, l.y)
            w,h = max_x - min_x, max_y - min_y    
                
            # we skip the line which has less than 35 height, since its the "hole" in 
            # the p in pymunk, and we dont need it.
            if h < 35:
                continue

            center = Vec2d(min_x + w/2., min_y + h/2.)   
            t = pymunk.Transform(a=1.0, d=1.0, tx=-center.x, ty=-center.y)

            r += 30
            if r > 255:
                r = 0
            line = [Vec2d(l.x, 300-l.y) for l in line]
            lines.append(line)
        return lines
                      

    def init(self):
        self.step = 1/60.
        self.touches = {}
        self.start()

    def start(self):
        self.space = space = pymunk.Space()
        space.gravity = 0, -900
        space.sleep_time_threshold = 0.3
        space.steps = 0
        
        floor = pymunk.Segment(space.static_body, (-100,0),(900,62),5)
        floor.friction = 1.0
        space.add(floor)
        with self.canvas:
            Color(0.2,0.2,0.2)
            floor.ky = Line(points=[-100,0,900,62], width=5)
            
        def wrap(f):
            return lambda dt: f(space)

        # we use our own event scheduling to make sure a event happens exactly 
        # after X amount of simulation steps
        self.events = []
        self.events.append((10, self.big_ball))
        for x in range(8):
            self.events.append((1+10*x, self.small_ball))
        
        self.events.append((200, self.big_ball))
        self.events.append((350, self.boxfloor))
        self.box_y = 150
        for x in range(8):
            self.events.append((400+x*10, self.box))
        self.events.append((650, self.car))
        self.events.append((850, self.cannon))
        self.events.append((1200, self.reset))

        self.update_event = Clock.schedule_interval(self.update, 1.0 / 20.)
        

    def reset(self, *args):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start()

    def update(self, dt):
        stepdelay = 25
        for x in range(6):
            self.space.step(1.0/60./2)
            self.space.step(1.0/60./2)
            self.space.steps += 1
            if len(self.events) > 0 and self.space.steps-stepdelay > self.events[0][0]:
                _, f = self.events.pop(0)
                f(self.space)

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
        self.game.init()
        self.game.pos = 0,300
        self.add_widget(self.game)