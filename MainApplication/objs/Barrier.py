import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Line


class Barrier(pymunk.Segment):
    def __init__(self, canvas, a, b, radius=1, rgba=(0.2,0.2,0.2,1), friction=1, elasticity=0.85):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        super(Barrier, self).__init__(body, a, b, radius)
        self.friction = friction
        self.elasticity = elasticity
        self.points = (a[0],a[1],b[0],b[1])
        self.rad = radius

        with canvas:
            Color(rgba=rgba)
            self.ky = Line(points=self.points, width=self.rad)