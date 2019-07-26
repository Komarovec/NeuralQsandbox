import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Line

class Barrier(pymunk.Segment):
    def __init__(self, canvas, scaller, a, b, radius=1, rgba=(0.2,0.2,0.2,1), friction=1, elasticity=0.85):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        super(Barrier, self).__init__(body, a, b, radius)
        self.friction = friction
        self.elasticity = elasticity
        self.points = (a[0],a[1],b[0],b[1])
        self.rad = radius
        self.rgba = rgba

        self.paint(canvas, scaller)

    def paint(self, canvas, scaller):
        with canvas:
            Color(rgba=self.rgba)
            scalled_points = (self.points[0]*scaller,self.points[1]*scaller,self.points[2]*scaller,self.points[3]*scaller)
            self.ky = Line(points=self.points, width=self.radius*scaller)


class Start(pymunk.Segment):
    def __init__(self, canvas, scaller, a, b, radius=1, rgba=(0,0.8,0,1), friction=1, elasticity=0.85):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        super(Start, self).__init__(body, a, b, radius)
        self.friction = friction
        self.elasticity = elasticity
        self.points = (a[0],a[1],b[0],b[1])
        self.rgba = rgba

        self.filter = pymunk.ShapeFilter(categories=2, mask=(1 and 2))

        self.paint(canvas, scaller)

    def paint(self, canvas, scaller):
        with canvas:
            Color(rgba=self.rgba)
            scalled_points = (self.points[0]*scaller,self.points[1]*scaller,self.points[2]*scaller,self.points[3]*scaller)
            self.ky = Line(points=self.points, width=self.radius*scaller)

class Finish(pymunk.Segment):
    def __init__(self, canvas, scaller, a, b, radius=1, rgba=(0.8,0,0,1), friction=1, elasticity=0.85):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        super(Finish, self).__init__(body, a, b, radius)
        self.friction = friction
        self.elasticity = elasticity
        self.points = (a[0],a[1],b[0],b[1])
        self.rgba = rgba

        self.paint(canvas, scaller)

    def paint(self, canvas, scaller):
        with canvas:
            Color(rgba=self.rgba)
            scalled_points = (self.points[0]*scaller,self.points[1]*scaller,self.points[2]*scaller,self.points[3]*scaller)
            self.ky = Line(points=self.points, width=self.radius*scaller)