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
from kivy.uix.actionbar import ActionBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Ellipse, Line, Color, Triangle, Quad, Rectangle, Mesh
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

import cffi
import pymunk
import pymunk.autogeometry
from pymunk.vec2d import Vec2d

import math
import numpy as np

#Kivy functions
def paintObject(shape, canvasHandler):
    with canvasHandler.canvas:
        Color(rgba=shape.rgba)
        if(isinstance(shape, pymunk.Segment)):
            scalled_points = (shape.a[0]*canvasHandler.scaller,shape.a[1]*canvasHandler.scaller,
                            shape.b[0]*canvasHandler.scaller,shape.b[1]*canvasHandler.scaller)
            shape.ky = Line(points=scalled_points, width=shape.radius*canvasHandler.scaller)
        elif(isinstance(shape, pymunk.Circle)):
            shape.ky = ellipse_from_circle(shape, canvasHandler.scaller)
        elif(isinstance(shape, pymunk.Poly)):
            shape.ky = newRectangle(shape, canvasHandler.scaller)

def ellipse_from_circle(shape, scaller=1):
    body = shape.body
    pos = body.position - (shape.radius, shape.radius)
    e = Ellipse(pos=pos * (scaller, scaller), size=[shape.radius*2*scaller, shape.radius*2*scaller])
    return e

def points_from_poly(shape, scaller=1):
    body = shape.body
    ps = [p.rotated(body.angle) + body.position for p in shape.get_vertices()]
    vs = []
    for p in ps:
        vs += [p.x * scaller, p.y * scaller]
    return vs

def newRectangle(shape, scaller=1):
    return Quad(points=points_from_poly(shape, scaller))


#Math functions
def centerPoint(a, b):
    return ((a[0]+b[0])/2,(a[1]+b[1])/2)

def distXY(a, b):
    return math.sqrt(((a[0]-b[0])**2)+((a[1]-b[1])**2))

def getVector(a, b):
    return (b[0]-a[0], b[1]-a[1])

def normalizeVector(v):
    norm = np.linalg.norm(v)
    if(norm == 0): 
       return v

    return v / norm

def calculateRectangle(a, b, c):
    if(distXY(a,b) <= 0 or distXY(a,c) <= 0 or distXY(b,c) <= 0):
        return (None,None,None,None)

    #Calculate remaining points for Rectangle !!!MATH WARNING!!!
    alpha = math.atan2(c[1]-a[1], c[0]-a[0]) - math.atan2(b[1]-a[1], b[0]-a[0])
    distAT = distXY(a, c) * math.cos(alpha)
    t = distAT/distXY(a,b)
    vectAT = ((b[0] - a[0])*t, (b[1] - a[1])*t)

    T = (a[0]+vectAT[0],a[1]+vectAT[1])
    vectTC = (c[0]-T[0], c[1]-T[1])

    Cdash = (a[0]+vectTC[0], a[1]+vectTC[1])
    D = (b[0]+vectTC[0], b[1]+vectTC[1])
    #END OF !!!MATH WARNING!!!

    #Rename
    c = Cdash
    d = D
    return (a,b,c,d)
