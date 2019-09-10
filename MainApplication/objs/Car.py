import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Quad

#Custom functions and classes
from objs.kivyObjs import points_from_poly

class Car(pymunk.Poly):
    CAR = "car"

    def __init__(self, mass=10, size=(100,50), pos=(100,100), friction=1, ground_friction=0.9, angular_friction=0.9, forward_speed = 5000, backward_speed = 5000, angular_speed = 500, elasticity=0.4, rgba=(0.8,0,0,1), texture=None):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, (size[0],size[1]))
        super(Car, self).__init__(shape._get_body(), shape.get_vertices())
        
        self.objectType = self.CAR

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

        self.filter = pymunk.ShapeFilter(categories=1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 1)

    #Respawn at the first spawnpoint in shapes array
    def respawn(self, simulation):
        self.body.position = simulation.findSpawnpoint()
        self.body.angle = 0
        self.body.velocity = (0,0)
        
        self.isDead = False

    #Paint Car
    def paint(self, canvasHandler):
        with canvasHandler.canvas:
            Color(rgba=self.rgba)
            
            #self.ky = Quad(points=points_from_poly(self, scaller), texture=self.texture)
            self.ky = Quad(points=points_from_poly(self, canvasHandler.scaller))

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
    