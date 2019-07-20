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

def ellipse_from_circle(shape, scaller):
    body = shape.body
    pos = body.position - (shape.radius, shape.radius)
    e = Ellipse(pos=pos * (scaller, scaller), size=[shape.radius*2*scaller, shape.radius*2*scaller])
    Color(.17,.24,.31)
    return e

def points_from_poly(shape, scaller):
    body = shape.body
    ps = [p.rotated(body.angle) + body.position for p in shape.get_vertices()]
    vs = []
    for p in ps:
        vs += [p.x * scaller, p.y * scaller]
    return vs

def newRectangle(shape, scaller):
    return Quad(points=points_from_poly(shape, scaller))
