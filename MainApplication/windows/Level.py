import cffi
import pymunk
from objs.GameObjects import Barrier, Start, Finish
from objs.Car import Car

from xml.dom import minidom
import xml.etree.ElementTree as ET

from ast import literal_eval

class Level():
    @classmethod
    def exportLevel(self, space):
        level = ET.Element("level")
        shapes = ET.SubElement(level, "shapes")
        for shape in space.shapes:
            if(isinstance(shape, Barrier)):
                item = ET.SubElement(shapes, "Barrier")
                item.set("a", str(tuple(shape.a)))
                item.set("b", str(tuple(shape.b)))
                item.set("radius", str(shape.radius))
                item.set("rgba", str(tuple(shape.rgba)))
            if(isinstance(shape, Start)):
                item = ET.SubElement(shapes, "Barrier")
                item.set("a", str(tuple(shape.a)))
                item.set("b", str(tuple(shape.b)))
                item.set("radius", str(shape.radius))
                item.set("rgba", str(tuple(shape.rgba)))
            if(isinstance(shape, Finish)):
                item = ET.SubElement(shapes, "Barrier")
                item.set("a", str(tuple(shape.a)))
                item.set("b", str(tuple(shape.b)))
                item.set("radius", str(shape.radius))
                item.set("rgba", str(tuple(shape.rgba)))

        leveldata = ET.tostring(level)
        with open('level.xml', 'w') as file:
            file.write(leveldata.decode("utf-8"))

    @classmethod
    def importLevel(self, simulation):
        for shape in simulation.space.shapes:
            simulation.canvasWindow.canvas.remove(shape.ky)

        simulation.setupSpace()
        level = minidom.parse('level.xml')

        items = level.getElementsByTagName('Barrier')
        for item in items:
            a, b = literal_eval(item.attributes["a"].value), literal_eval(item.attributes["b"].value)
            rgba = literal_eval(item.attributes["rgba"].value)
            newBarrier = Barrier(a, b, float(item.attributes["radius"].value))
            newBarrier.rgba = rgba
            simulation.space.add(newBarrier)
            newBarrier.paint(simulation.canvasWindow)