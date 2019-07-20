import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color

#Custom functions and classes
from objs.kivyObjs import newRectangle

class Car(pymunk.Poly):
    def __init__(self, canvas, scaller, mass=10, size=(100,50), pos=(100,100), friction=1, elasticity=0.4, rgba=(1,0,0,1)):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size);
        super(Car, self).__init__(shape._get_body(), shape.get_vertices())

        self.body.position = pos
        self.friction = friction
        self.elasticity = elasticity

        with canvas:
            Color(rgba=rgba)
            self.ky = newRectangle(self, scaller)