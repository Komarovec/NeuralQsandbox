import random
random.seed(5)

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.image import Image
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy_garden.graph import Graph, MeshLinePlot

# Animation
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label

# Custom classes
from windows.Simulation import Simulation
from windows.CanvasHandler import CanvasHandler
from objs.GameObjects import StaticGameObject

import math

# Special widget class with screen and scaling
class GameWidget(Widget):
    # Factor of scaling (Fonts, UI) !!! DOES NOT AFFECT RESOLUTION SCALER ONLY MULTIPLIES THE EFFECT !!!
    scaleFactor = NumericProperty(200)

    def __init__(self, game, screen, **kwargs):
        super(GameWidget, self).__init__(**kwargs)
        self.game = game
        self.screen = screen

class BGLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw)
        self.bind(size=self.draw)
        self.draw()

    def draw(self, *args):
        if(self.canvas == None): return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=(.1,.1,.1,1))
            Rectangle(pos=self.pos, size=self.size)

# Action bars (Game, Level editor)
class ToolBar(GameWidget):
    def __init__(self, manager, game, screen, **kwargs):
        super(ToolBar, self).__init__(game, screen, **kwargs)
        self.manager = manager
class ToolBarGame(ToolBar):
    pass
class ToolBarEditor(ToolBar):
    pass

# Stator, shows ingame vars on the bottom of the UI
class StateBar(GameWidget):
    pass

# Extends stator if needed
class StateInfoBar(GameWidget):
    DEFAULT_YMAX = 0.00001
    DEFAULT_YMIN = 0
    DEFAULT_XMAX = 1
    DEFAULT_XMIN = -0
    DEFAULT_X_TICKS_MAJOR = 1
    DEFAULT_Y_TICKS_MAJOR = 1

    def __init__(self, game, screen, **kwargs):
        super(StateInfoBar, self).__init__(game, screen, **kwargs)

        # Right graph
        self.graph1 = graph1 = Graph(xlabel='Game', ylabel='Reward',
            x_ticks_major=self.DEFAULT_X_TICKS_MAJOR, y_ticks_major=self.DEFAULT_Y_TICKS_MAJOR,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=self.DEFAULT_XMIN, xmax=self.DEFAULT_XMAX, ymin=self.DEFAULT_YMIN, ymax=self.DEFAULT_YMAX)

        self.plot1 = plot1 = MeshLinePlot(color=[1, 0, 0, 1])
        plot1.points = []
        graph1.add_plot(plot1)

        self.ids["graph1"].add_widget(graph1)

        # Left graph
        self.graph2 = graph2 = Graph(xlabel='Generation', ylabel='MaxFitness',
            x_ticks_major=self.DEFAULT_X_TICKS_MAJOR, y_ticks_major=self.DEFAULT_Y_TICKS_MAJOR,
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=True, y_grid=True, xmin=self.DEFAULT_XMIN, xmax=self.DEFAULT_XMAX, ymin=self.DEFAULT_YMIN, ymax=self.DEFAULT_YMAX)

        self.plot2 = plot2 = MeshLinePlot(color=[0, 1, 0, 1])
        plot2.points = []
        graph2.add_plot(plot2)

        self.ids["graph2"].add_widget(graph2)

    # Reset plot on graph:
    def resetPlot(self, graph, plot):
        graph.xmax = self.DEFAULT_XMAX
        graph.xmin = self.DEFAULT_XMIN
        graph.ymax = self.DEFAULT_YMAX
        graph.ymin = self.DEFAULT_YMIN
        graph.x_ticks_major = self.DEFAULT_X_TICKS_MAJOR
        graph.y_ticks_major = self.DEFAULT_Y_TICKS_MAJOR
        plot.points = []

    # Change graph labels
    def changeGraphLabel(self, graph, xlabel=None, ylabel=None):
        if(xlabel != None):
            graph.xlabel = xlabel
        
        if(ylabel != None):
            graph.ylabel = ylabel

    # Left graph
    def addPlotPointLeft(self, x, y, plot=None):
        if(plot == None):
            plot = self.plot2

        self.addPlotPoint(self.graph2, plot, x, y)

    # Right graph
    def addPlotPointRight(self, x, y, plot=None):
        if(plot == None):
            plot = self.plot1

        self.addPlotPoint(self.graph1, plot, x, y)

    # Rescale y axis on graph
    def rescaleY(self, graph, y):
        # Rescaling of y axis
        if(y > (graph.ymax - (graph.ymax/10))):
            graph.ymax = int(math.ceil(y + (y/10))) # Move max more up by fraction of y --> better look

            if(y > abs(graph.ymin)):
                graph.y_ticks_major = math.floor(y/2)

        if(y < (graph.ymin - (graph.ymin/10))):
            graph.ymin = int(math.ceil(y + (y/10))) # Move max more up by fraction of y --> better look

            if(abs(y) > graph.ymax):
                graph.y_ticks_major = abs(math.floor(y/2))

    # Add point to graph
    def addPlotPoint(self, graph, plot, x, y):
        # Add data to graph
        plot.points.append((x, y))

        self.rescaleY(graph, y)

        # Rescaling of x axis
        if((x+1) > graph.xmax):
            graph.xmax = x+1

            # Change major points only dividable by 5
            if(x % 5 == 0):
                graph.x_ticks_major = math.floor(x/5) if((x/5) > 1) else 1

        # Reset graph if x < xmax
        else:
            self.resetPlot(graph, plot)
            plot.points.append((x, y))
            self.rescaleY(graph, y)

    # Changes top value
    def setValue1(self, name, value):
        self.ids["val1"].text = str(name)+": "+str(value)

    # Changes second value
    def setValue2(self, name, value):
        self.ids["val2"].text = str(name)+": "+str(value)

    # Changes third value
    def setValue3(self, name, value):
        self.ids["val3"].text = str(name)+": "+str(value)

    # Changes bottom value
    def setValue4(self, name, value):
        self.ids["val4"].text = str(name)+": "+str(value)

# Menu for choosing mode --> Play, Train, Test
class StartMenu(GameWidget):
    pass

# Object adding
class ObjectMenu(GameWidget):
    visible = False

    def __init__(self, game, screen, **kwargs):
        super(ObjectMenu, self).__init__(game, screen, **kwargs)
        # Defaults
        self.colorVal = (0.2,0.2,0.2, 1)
        self.collisionsVal = True
        self.shapeVal = "Segment"
        self.typeVal = "Barrier"

        # Grids
        self.shapeGrid = GridLayout(cols=2)
        self.typeGrid = GridLayout(cols=2)
        self.colorGrid = GridLayout(cols=2)
        self.collisionGrid = GridLayout(cols=2)

        # Shape Label + Dropdown
        self.shapeDropDown = ShapeDropDown(self)
        self.shapeButton = Button(text="Segment")
        self.shapeButton.bind(on_release=self.shapeDropDown.open)
        self.shapeDropDown.bind(on_select=lambda instance, x: setattr(self.shapeButton, 'text', x))
        self.shapeGrid.add_widget(Label(text="Shape: "))
        self.shapeGrid.add_widget(self.shapeButton)

        # Type Label + Dropdown
        self.typeDropDown = TypeDropDown(self)
        self.typeButton = Button(text="Barrier")
        self.typeButton.bind(on_release=self.typeDropDown.open)
        self.typeDropDown.bind(on_select=lambda instance, x: setattr(self.typeButton, 'text', x))
        self.typeGrid.add_widget(Label(text="Type: "))
        self.typeGrid.add_widget(self.typeButton)

        # COLOR
        self.colorGrid.add_widget(Label(text="Color: "))
        self.colorButton = Button(background_normal=('Image.extension'), background_color=self.colorVal, text="", on_release=lambda instance: self.showColorpicker())
        self.colorGrid.add_widget(self.colorButton)

        # Collisions
        self.collisionGrid.add_widget(Label(text="Collisions: "))
        self.collisionGrid.add_widget(ToggleButton(self))

        # Add all layouts
        self.ids["inObjectMenu"].add_widget(self.shapeGrid)
        self.ids["inObjectMenu"].add_widget(self.typeGrid)
        self.ids["inObjectMenu"].add_widget(self.colorGrid)
        self.ids["inObjectMenu"].add_widget(self.collisionGrid)

    # Change game tools base on buttons
    def changeTool(self, state, btn):
        if(state == "down"):
            if(btn == "add"):
                self.game.changeTool("add")
            elif(btn == "delete"):
                self.game.changeTool("delete")
        else:
            self.game.changeTool("move")

    # Change buttons state
    def changeButtonState(self, state, btn):
        if(state == "down"):
            if(btn == "delete"):
                self.ids["deleteBtn"].state = "down"
            elif(btn == "add"):
                self.ids["addBtn"].state = "down"
        elif(state == "normal"):
            if(btn == "delete"):
                self.ids["deleteBtn"].state = "normal"
            elif(btn == "add"):
                self.ids["addBtn"].state = "normal"


    def showColorpicker(self):
        popup = PopupColor(self)
        popup_color = ColorPicker()
        popup.color = self.colorVal
        popup.open()

    # Resulting callbacks
    def resultShape(self, shape):
        self.shapeVal = shape

    def resultType(self, typeVal):
        self.typeVal = typeVal
        if(self.typeVal == "Finish"):
            self.colorVal = (.8,0,0,1)
        elif(self.typeVal == "Start"):
            self.colorVal = (0,.8,0,1)
        else:
            self.colorVal = (.2,.2,.2, 1)

        self.colorButton.background_color = self.colorVal

    def resultColor(self, color):
        if(color[3] != None and color[3] != 0):
            self.colorVal = (color[0],color[1],color[2],color[3])
        else:    
            self.colorVal = (color[0],color[1],color[2],1)
        self.colorButton.background_color = color

    def resultCollisions(self, val):
        self.collisionsVal = val

    def getData(self):
        data = {"shape": self.shapeVal, "type": self.typeVal, "color": self.colorVal, "collisions": self.collisionsVal}
        return data

# Object editing
class EditMenu(GameWidget):
    visible = False

    def __init__(self, game, screen, **kwargs):
        super(EditMenu, self).__init__(game, screen, **kwargs)
        # Defaults
        self.editObject = None
        self.highlight = None
        self.colorVal = (0.2,0.2,0.2, 1)
        self.collisionsVal = True
        self.shapeVal = "Segment"
        self.typeVal = "Barrier"

        # Grids
        self.typeGrid = GridLayout(cols=2)
        self.colorGrid = GridLayout(cols=2)
        self.collisionGrid = GridLayout(cols=2)

        # Type Label + Dropdown
        self.typeDropDown = TypeDropDown(self)
        self.typeButton = Button(text="Barrier")
        self.typeButton.bind(on_release=self.typeDropDown.open)
        self.typeDropDown.bind(on_select=lambda instance, x: setattr(self.typeButton, 'text', x))
        self.typeGrid.add_widget(Label(text="Type: "))
        self.typeGrid.add_widget(self.typeButton)

        # COLOR
        self.colorGrid.add_widget(Label(text="Color: "))
        self.colorButton = Button(background_normal=('Image.extension'), text="", on_release=lambda instance: self.showColorpicker())
        self.colorGrid.add_widget(self.colorButton)

        # Collisions
        self.collisionGrid.add_widget(Label(text="Collisions: "))
        self.collisionToggleButton = ToggleButton(self)
        self.collisionGrid.add_widget(self.collisionToggleButton)

        # Add all layouts
        self.ids["inEditMenu"].add_widget(self.typeGrid)
        self.ids["inEditMenu"].add_widget(self.colorGrid)
        self.ids["inEditMenu"].add_widget(self.collisionGrid) 

    # Get object
    def setEditObject(self, obj):
        if(obj == None):
            # Disable widget
            self.disableMenu()
            return

        elif(self.editObject == None):
            self.screen.add_widget(self)

        self.editObject = obj

        # Create highlight
        if(self.highlight != None):
            self.game.canvas.remove(self.highlight)
        self.highlight = self.game.highlightObject(self.editObject)

        if(hasattr(self.editObject, "objectType")):
            # Set layer height
            self.ids["layerLabel"].text = str(self.game.simulation.getLayer(self.editObject))

            # Set type button
            if(self.editObject.objectType == StaticGameObject.BARRIER or self.editObject.objectType == StaticGameObject.NOBARRIER):
                self.typeButton.text = "Barrier"
            elif(self.editObject.objectType == StaticGameObject.START):
                self.typeButton.text = "Start"
            elif(self.editObject.objectType == StaticGameObject.FINISH):
                self.typeButton.text = "Finish"

            # Set color
            self.colorButton.background_color = self.editObject.rgba

            # Set collisions
            if(self.editObject.sensor):
                self.collisionToggleButton.forceState(False)
            else:
                self.collisionToggleButton.forceState(True)

        else:
            # Propably chosen a car --> Cant edit
            self.editObject = None
            self.screen.remove_widget(self)

    # Shift selected object
    def shiftLayer(self, shift, spec=False):
        if(self.editObject != None):
            self.game.simulation.shiftLayer(self.editObject, shift, spec)

        self.ids["layerLabel"].text = str(self.game.simulation.getLayer(self.editObject))

    # Deletes selected object
    def deleteObject(self):
        self.game.simulation.deleteObject(self.editObject)
        self.disableMenu()
        
    # Disable widget
    def disableMenu(self):
        if(self.highlight != None):
            self.game.canvas.remove(self.highlight)
        self.screen.remove_widget(self)

        self.highlight = None
        self.editObject = None

    # Color picker
    def showColorpicker(self):
        popup = PopupColor(self)
        popup_color = ColorPicker()
        popup.color = self.colorVal
        popup.open()

    # Resulting callbacks
    def resultType(self, typeVal):
        self.typeVal = typeVal

        if(self.editObject != None):
            if(typeVal == "Finish"):
                # When changed to finish force collisions
                self.editObject.objectType = StaticGameObject.FINISH
                self.editObject.sensor = False
                self.collisionToggleButton.forceState(True)
            elif(typeVal == "Start"):
                # When changed to start force no collisions
                self.editObject.objectType = StaticGameObject.START
                self.editObject.sensor = True
                self.collisionToggleButton.forceState(False)
            elif(typeVal == "Barrier"):
                # When changed to barrier check sensor behav
                if(self.editObject.sensor):
                    self.editObject.objectType = StaticGameObject.NOBARRIER
                else:
                    self.editObject.objectType = StaticGameObject.BARRIER


    def resultColor(self, color):
        if(color[3] != None):
            self.colorVal = (color[0],color[1],color[2],color[3])
        else:    
            self.colorVal = (color[0],color[1],color[2],1)
        self.colorButton.background_color = color

        if(self.editObject != None):
            self.editObject.rgba = self.colorVal
            self.game.canvas.remove(self.editObject.ky)
            self.game.canvas.add(Color(rgba=self.editObject.rgba))
            self.game.canvas.add(self.editObject.ky)

            self.game.simulation.repaintObjects()

    def resultCollisions(self, val):
        self.collisionsVal = val

        if(self.editObject != None):
            self.editObject.sensor = not val


    def getData(self):
        data = {"type": self.typeVal, "color": self.colorVal, "collisions": self.collisionsVal}
        return data

# Custom GUI objects
class ActivationDropDown(DropDown):
    def __init__(self, func, **kwargs):
        super().__init__(**kwargs)
        
        self.func = func
        self.add_widget(Button(text="relu", size_hint_y = None, height=44, on_release=lambda instance: self.select("relu")))
        self.add_widget(Button(text="sigmoid", size_hint_y = None, height=44, on_release=lambda instance: self.select("sigmoid")))
        self.add_widget(Button(text="linear", size_hint_y = None, height=44, on_release=lambda instance: self.select("linear")))

    def on_select(self, data):
        self.func(data)

# Custom GUI objects
class ShapeDropDown(DropDown):
    def __init__(self, menu, **kwargs):
        super().__init__(**kwargs)
        self.menu = menu
        self.add_widget(Button(text="Segment", size_hint_y = None, height=44, on_release=lambda instance: self.select("Segment")))
        self.add_widget(Button(text="Circle", size_hint_y = None, height=44, on_release=lambda instance: self.select("Circle")))
        self.add_widget(Button(text="Box", size_hint_y = None, height=44, on_release=lambda instance: self.select("Box")))

    def on_select(self, data):
        self.menu.resultShape(data)
class TypeDropDown(DropDown):
    def __init__(self, menu, **kwargs):
        super().__init__(**kwargs)
        self.menu = menu
        self.add_widget(Button(text="Barrier", size_hint_y = None, height=44, on_release=lambda instance: self.select("Barrier")))
        self.add_widget(Button(text="Finish", size_hint_y = None, height=44, on_release=lambda instance: self.select("Finish")))
        self.add_widget(Button(text="Start", size_hint_y = None, height=44, on_release=lambda instance: self.select("Start")))

    def on_select(self, data):
        self.menu.resultType(data)

# Separator object
class Separator(Widget):
    pass

# Checkbox
class ToggleButton(ToggleButtonBehavior, Image):
    def __init__(self, menu, **kwargs):
        super(ToggleButton, self).__init__(**kwargs)
        self.source = 'atlas://data/images/defaulttheme/checkbox_on'
        self.menu = menu

    def on_state(self, widget, value):
        if(value == 'down'):
            self.source = 'atlas://data/images/defaulttheme/checkbox_off'
            self.menu.resultCollisions(False)
        else:
            self.source = 'atlas://data/images/defaulttheme/checkbox_on'
            self.menu.resultCollisions(True)

    def forceState(self, state):
        if(state):
            self.source = 'atlas://data/images/defaulttheme/checkbox_on'
        else:
            self.source = 'atlas://data/images/defaulttheme/checkbox_off'

# Popup
class PopupColor(Popup):
    def __init__(self, menu, *args):
        super(PopupColor, self).__init__(*args)
        self.menu = menu

    def on_press_dismiss(self, colorpicker, *args):
        self.dismiss()
        color = colorpicker.color
        self.menu.resultColor(color)