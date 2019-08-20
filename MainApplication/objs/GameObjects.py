import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d
from kivy.graphics import Color, Line, Ellipse
from objs.kivyObjs import ellipse_from_circle, newRectangle

class StaticGameObject():
    BARRIER = "barrier"
    NOBARRIER = "nobarrier"
    START = "start"
    FINISH = "finish"

    def __init__(self, objectType, rgba=(0.2,0.2,0.2,1), friction=1, elasticity=0.85, texture=None):
        #Common attrs
        self.objectType = objectType
        self.rgba = rgba
        self.friction = friction
        self.elasticity = elasticity

    def createSegment(self, a, b, radius, canvasHandler):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(body, a, b, radius)
        self.addAttrs(self.shape)
        self.paint(canvasHandler)
        canvasHandler.simulation.space.add(self.shape)

    def createCircle(self, pos, radius, canvasHandler):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        body.position = pos
        self.shape = pymunk.Circle(body, radius)
        self.addAttrs(self.shape)
        self.paint(canvasHandler)
        canvasHandler.simulation.space.add(self.shape)

    def createBox(self, pos, size, canvasHandler):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        body.position = pos
        self.shape = pymunk.Poly.create_box(body, (size[0],size[1]))
        self.addAttrs(self.shape)
        self.paint(canvasHandler)
        canvasHandler.simulation.space.add(self.shape)

    def createBoxPoints(self, points, canvasHandler):
        body = pymunk.Body(mass=0, moment=0, body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Poly(body, points)
        self.addAttrs(self.shape)
        self.paint(canvasHandler)
        canvasHandler.simulation.space.add(self.shape)

    def addAttrs(self, shape):
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity
        self.shape.rgba = self.rgba
        self.shape.objectType = self.objectType

        if(self.objectType == self.START or self.objectType == self.NOBARRIER):
            self.shape.sensor = True

    def paint(self, canvasHandler):
        with canvasHandler.canvas:
            Color(rgba=self.rgba)
            if(isinstance(self.shape, pymunk.Segment)):
                scalled_points = (self.shape.a[0]*canvasHandler.scaller,self.shape.a[1]*canvasHandler.scaller,
                                self.shape.b[0]*canvasHandler.scaller,self.shape.b[1]*canvasHandler.scaller)
                self.shape.ky = Line(points=scalled_points, width=self.shape.radius*canvasHandler.scaller)
            elif(isinstance(self.shape, pymunk.Circle)):
                self.shape.ky = ellipse_from_circle(self.shape, canvasHandler.scaller)
            elif(isinstance(self.shape, pymunk.Poly)):
                self.shape.ky = newRectangle(self.shape, canvasHandler.scaller)