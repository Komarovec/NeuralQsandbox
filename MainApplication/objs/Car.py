import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Quad

#Custom functions and classes
from objs.kivyObjs import points_from_poly

class Car(pymunk.Poly):
    def __init__(self, canvas, scaller, texture, mass=10, size=(100,50), pos=(100,100), friction=1, ground_friction=0.9, angular_friction=0.9, forward_speed = 5000, backward_speed = 5000, angular_speed = 500, elasticity=0.4, rgba=(0.8,0,0,1)):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size);
        super(Car, self).__init__(shape._get_body(), shape.get_vertices())

        self.rgba = rgba
        self.forward_speed = forward_speed
        self.backward_speed = backward_speed
        self.angular_speed = angular_speed
        self.texture = texture

        self.ground_friction = ground_friction
        self.angular_friction = angular_friction
        self.size = size
        self.body.position = pos
        self.friction = friction
        self.elasticity = elasticity

        self.filter = pymunk.ShapeFilter(categories=1, mask=(1 and 2))

        self.paint(canvas, scaller)
        
    #Paint Car
    def paint(self, canvas, scaller):
        with canvas:
            Color(rgba=self.rgba)
            #self.ky = Quad(points=points_from_poly(self, scaller), texture=self.texture)
            self.ky = Quad(points=points_from_poly(self, scaller))

    #Control methods
    def forward(self, vel):
        self.body.apply_force_at_local_point(Vec2d(self.forward_speed*vel,0), (0,0))

    def backward(self, vel):
        self.body.apply_force_at_local_point(Vec2d(-self.backward_speed*vel,0), (0,0))

    def left(self, vel):
        self.body.apply_force_at_local_point(Vec2d(-self.angular_speed*vel,0), (0,self.size[0]))
        self.body.apply_force_at_local_point(Vec2d(self.angular_speed*vel,0), (0,-self.size[0]))

    def right(self, vel):
        self.body.apply_force_at_local_point(Vec2d(self.angular_speed*vel,0), (0,self.size[0]))
        self.body.apply_force_at_local_point(Vec2d(-self.angular_speed*vel,0), (0,-self.size[0]))
    