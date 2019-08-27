
import random
random.seed(5)

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

import pymunk
import math

#Custom function and classes
from objs.GameObjects import StaticGameObject
from objs.Car import Car
from objs.CarAI import CarAI
from objs.kivyObjs import ellipse_from_circle, points_from_poly, newRectangle, distXY, calculateRectangle
from windows.Simulation import Simulation
from windows.Level import Level

class CanvasHandler(RelativeLayout):
    def init(self, window):
        #Important values
        self.touches = {}
        self.keys = {"up" : 0, "down" : 0, "left" : 0, "right" : 0, 'lctrl': 0, 'z': 0}
        self.scallerVar = 10000
        self.state = "game"
        self.window = window

        #Undo field
        self.changes = []
        self.undoDone = False

        #Level editor vals
        self.editorTool = "move"

        #Draw
        self.isDrawing = True

        #Adding object
        self.adding_barrier = False
        self.temp_barrier = None
        self.temp_rect = None
        self.addingStage = 0
        self.addingIndication = None

        #Deleting objects
        self.deleteObject = False

        #Moving objects
        self.movingObject = False
        self.movingVar = None
        self.movingPoint = None

        #Highlighted object
        self.tempHighlight = None

    def start(self, simulation):
        self.simulation = simulation

        texture = CoreImage('textures/carTexture.png').texture
        #texture.uvsize = (1,1)

        #Setting up few things
        self.scaller = self.height/self.scallerVar + self.width/self.scallerVar

        #Keyboard/Mouse listener
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        #Start physics engine
        self.simulation.start()

        #Set time clock
        self.startDrawing()

    #Completely stops clock, drawing and physics!
    def stopDrawing(self):
        Clock.unschedule(self.update_event)

    #Start clock, drawing and physics
    def startDrawing(self):
        self.update_event = Clock.schedule_interval(self.draw, 1.0 / 100)

    #Reset enviroment
    def reset(self):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()
        self.start(Simulation(self))

    #Stops end DELETES entire universe!!
    def stop(self):
        self.clear_widgets()
        self.update_event.cancel()
        self.canvas.clear()


    """
    ----> Main loop method <----
    
    Calls for physics computation
    Handles car controls
    Undo action
    Highlighting
    Drawing
    """
    def draw(self, dt):
        #Game mode
        if(self.state != "editor"):
            self.simulation.update(dt)
            self.window.statebar.ids["steps"].text = "Steps: "+str(self.simulation.space.steps)

            #Car control
            for shape in self.simulation.space.shapes:
                if isinstance(shape, Car):
                    if(self.keys["up"] == 1):
                        shape.forward(dt*100)
                    if(self.keys["down"] == 1):
                        shape.backward(dt*100)
                    if(self.keys["left"] == 1):
                        shape.left(dt*100)
                    if(self.keys["right"] == 1):
                        shape.right(dt*100)

        #Editor mode
        elif(self.state == "editor"):
            #Undo action
            if(self.keys["lctrl"] == 1 and self.keys["z"] == 1 and not self.undoDone):
                #Do undo //Delete and create only
                if(self.changes.__len__() != 0):
                    change = self.changes[self.changes.__len__()-1]
                    match = None
                    for shape in self.simulation.space.shapes:
                        if(shape == change):
                            self.simulation.deleteObject(shape, "nochange")
                            self.changes.remove(shape)
                            match = "found"

                    if(match == None):
                        self.simulation.space.add(change)

                        self.canvas.add(Color(rgba=change.rgba))
                        self.canvas.add(change.ky)

                        self.simulation.repaintObjects()
                        self.changes.remove(change)

                self.undoDone = True
                
            #Reset undo action
            if(self.keys["z"] == 0 and self.undoDone):
                self.undoDone = False

            #Adding tool indication + rectangle adding grap rep
            if(self.editorTool == "add"):
                pos = self.to_local(*Window.mouse_pos)

                #Mouse indication shape
                if(self.addingIndication == None):
                    with self.canvas:
                        Color(0,0.8,0,0.6)
                        self.addingIndication = Ellipse(pos=(pos[0]-5, pos[1]-5), size=(10,10))
                else:
                    self.addingIndication.pos = (pos[0]-5, pos[1]-5)

                #When adding rectangle show its graphical representation
                if(self.addingStage == 1):
                    c = pos
                    a = (self.temp_rect.points[0], self.temp_rect.points[1])
                    b = (self.temp_rect.points[2], self.temp_rect.points[3])

                    a, b, c, d = calculateRectangle(a,b,c)

                    if(self.temp_barrier == None):
                        if(a != None):
                            with self.canvas:
                                Color(0.8,0,0,0.6)
                                self.temp_barrier = Quad(points=(a[0], a[1], b[0], b[1], d[0], d[1], c[0], c[1]))
                    else:
                        if(a != None):
                            self.temp_barrier.points = (a[0], a[1], b[0], b[1], d[0], d[1], c[0], c[1])

            #Deleting mouse indication
            elif(self.editorTool == "delete"):
                pos = self.to_local(*Window.mouse_pos)
                pos = (pos[0]-5, pos[1]-5)

                if(self.addingIndication == None):
                    with self.canvas:
                        Color(0.8,0,0,0.6)
                        self.addingIndication = Ellipse(pos=pos, size=(10,10))
                else:
                    self.addingIndication.pos = pos
            else:
                if(self.addingIndication != None):
                    self.canvas.remove(self.addingIndication)
                    self.addingIndication = None

            #Barrier adding width change
            if(self.temp_barrier != None and isinstance(self.temp_barrier, Line)):
                if(self.keys["up"] == 1):
                    if(self.temp_barrier.width/self.scaller < 100):
                        self.temp_barrier.width += 1
                elif(self.keys["down"] == 1):
                    if(self.temp_barrier.width/self.scaller > 1 and self.temp_barrier.width > 1):
                        self.temp_barrier.width -= 1
    
            #Highligting
            else:
                pos = self.to_local(*Window.mouse_pos)
                pos = (pos[0]/self.scaller, pos[1]/self.scaller)

                for shape in reversed(self.simulation.space.shapes):
                    #Highlight object when no moving
                    if(not self.movingObject):
                        #Highlight hover objects
                        if(shape.point_query(pos)[0] < 0):
                            if(self.tempHighlight != None):
                                self.canvas.remove(self.tempHighlight)
                                self.tempHighlight = None

                            self.tempHighlight = self.highlightObject(shape)
                            break

                        #Cleanup highlight
                        elif(self.tempHighlight != None):
                            self.canvas.remove(self.tempHighlight)
                            self.tempHighlight = None
                    #Cleanup highlight
                    elif(self.tempHighlight != None):
                        self.canvas.remove(self.tempHighlight)
                        self.tempHighlight = None

        if(self.isDrawing):
            #------ Common draw -------
            #Scalling coeficient
            scaller = self.height/self.scallerVar + self.width/self.scallerVar
            
            #If resolution has changed change scaling on all shapes
            if(scaller != self.scaller):
                self.scaller = scaller
                scallerChanged = True
            else:
                scallerChanged = False

            #Repaint all graphics
            for shape in self.simulation.space.shapes:
                if(hasattr(shape, "ky") and (not shape.body.is_sleeping or scallerChanged)):
                    if isinstance(shape, pymunk.Circle):
                        body = shape.body
                        shape.ky.size = [shape.radius*2*self.scaller, shape.radius*2*self.scaller]
                        shape.ky.pos = (body.position - (shape.radius, shape.radius)) * (self.scaller, self.scaller)

                    if isinstance(shape, pymunk.Segment):
                        #If Is barrier class than increase width by scaller
                        shape.ky.width = shape.radius * self.scaller

                        body = shape.body
                        p1 = body.position + shape.a.cpvrotate(body.rotation_vector) 
                        p2 = body.position + shape.b.cpvrotate(body.rotation_vector)
                        shape.ky.points = p1.x * self.scaller, p1.y * self.scaller, p2.x * self.scaller, p2.y * self.scaller

                    if isinstance(shape, pymunk.Poly):
                        shape.ky.points = points_from_poly(shape, scaller)

                    if isinstance(shape, CarAI):
                        pass
                        #shape.drawRaycasts(self)

    #Highlight object
    def highlightObject(self, obj):
        saveobj = None
        if(isinstance(obj, pymunk.Segment)):
            with self.canvas:
                Color(0.6,0.6,0.6,0.6)
                saveobj = Line(points=obj.ky.points, width=obj.ky.width)
        elif(isinstance(obj, Car) or isinstance(obj, pymunk.Poly)):
            with self.canvas:
                Color(0.6,0.6,0.6,0.6)
                saveobj = newRectangle(obj, self.scaller)
        elif(isinstance(obj, pymunk.Circle)):
            with self.canvas:
                Color(0.6,0.6,0.6,0.6)
                saveobj = ellipse_from_circle(obj, self.scaller)

        return saveobj


    #Camera change
    def changeCamera(self, state):
        if(state == "center"):
            self.pos = (0,0)

    #Pickle export
    def exportFile(self):
        Level.exportLevel(self.simulation)
        self.focus = True

    #Pickle import
    def importFile(self):
        Level.importLevel(self.simulation)
        self.focus = True
        
    #Change tool
    def changeTool(self, tool):
        self.window.statebar.ids["tool"].text = "Tool: "+str(tool)
        self.editorTool = tool

        #Changes buttons on object menu --> Add toogle, delete toggle etc..
        if(tool == "add"):
            self.window.objectMenu.changeButtonState("normal", "delete")
        elif(tool == "delete"):
            self.window.objectMenu.changeButtonState("normal", "add")
        elif(tool == "move"):
            self.window.objectMenu.changeButtonState("normal", "delete")
            self.window.objectMenu.changeButtonState("normal", "add")

        #Removing mouse indication
        if(self.addingIndication != None):
            self.canvas.remove(self.addingIndication)
            self.addingIndication = None

    #Change state
    def changeState(self, state):
        if(state == "game"):
            #Updates statebar
            self.window.statebar.ids["tool"].text = "Game state"
            
            #Closes edit menu (if opened)
            self.window.editMenu.setEditObject(None)

            #Delete highlight
            if(self.tempHighlight != None):
                self.canvas.remove(self.tempHighlight)
                self.tempHighlight = None

        elif(state == "editor"):
            #Updates statebar
            self.window.statebar.ids["tool"].text = "Tool: "+str(self.editorTool)

            #Despawns player
            self.simulation.removePlayer()


        self.state = state


    """
    -----> Interface functions <-----
    """
    def on_touch_up(self, touch):
        #Scale screen if mouse scroll
        if(touch.button == "scrolldown"):
            return
        elif(touch.button == "scrollup"):
            return

        #Ungrab screen when stopped touching
        if touch.grab_current is self:
            touch.ungrab(self)
        
        #Create body for barrier and place it in place
        elif(self.adding_barrier):
            data = self.window.objectMenu.getData()

            #Delete temp line when cursor removed
            self.adding_barrier = False

            #Nice
            if(self.addingShape == "Segment"):
                self.simulation.addSegment((self.temp_barrier.points[0]/self.scaller, 
                                        self.temp_barrier.points[1]/self.scaller), 
                                        (self.temp_barrier.points[2]/self.scaller, 
                                        self.temp_barrier.points[3]/self.scaller), 
                                        self.temp_barrier.width/self.scaller, typeVal=data["type"], collisions=data["collisions"] ,rgba=data["color"])
            elif(self.addingShape == "Circle"):
                self.simulation.addCircle(((self.temp_barrier.pos[0]+self.temp_barrier.size[0]/2)/self.scaller,(self.temp_barrier.pos[1]+self.temp_barrier.size[0]/2)/self.scaller), (self.temp_barrier.size[0]/2)/self.scaller, typeVal=data["type"], collisions=data["collisions"] ,rgba=data["color"])

            #If adding box, do not delete Line from canvas
            elif(self.addingShape == "Box"):
                if(self.addingStage == 0):
                    self.temp_rect = self.temp_barrier
                    self.addingStage = 1
                    self.adding_barrier = True
                elif(self.addingStage == 1):
                    self.addingStage = 0
                    c = (self.touches[0][0]/self.scaller,self.touches[0][1]/self.scaller)
                    a = (self.temp_rect.points[0]/self.scaller, self.temp_rect.points[1]/self.scaller)
                    b = (self.temp_rect.points[2]/self.scaller, self.temp_rect.points[3]/self.scaller)

                    a, b, c, d = calculateRectangle(a,b,c)

                    if(a != None):
                        self.simulation.addBox((a,b,c,d), typeVal=data["type"], collisions=data["collisions"] ,rgba=data["color"])

            if(self.temp_barrier != None):
                self.canvas.remove(self.temp_barrier)
                self.temp_barrier = None

        #Stop moving
        elif(self.movingObject):
            self.movingObject = False
            self.movingVar = None
            self.movingPoint = None

    def on_touch_move(self, touch):
        if(touch.button == "scrolldown" or touch.button == "scrollup"):
            return

        p = self.to_local(*touch.pos)
        self.touches[1] = p

        #Move screen when grabbed
        if touch.grab_current is self:
            self.pos[0] -= self.touches[0][0]-self.touches[1][0]
            self.pos[1] -= self.touches[0][1]-self.touches[1][1]
        
        #If adding_barrier then show "pre barrier"
        elif(self.adding_barrier):
            #Update line when moved
            if(self.addingShape == "Segment"):
                self.temp_barrier.points = [self.touches[0][0], self.touches[0][1], p[0], p[1]]
            elif(self.addingShape == "Circle"):
                radius = math.sqrt(((p[0]-self.touches[0][0])**2)+((p[1]-self.touches[0][1])**2))
                self.temp_barrier.size = (radius*2, radius*2)
                self.temp_barrier.pos = (self.touches[0][0]-radius, self.touches[0][1]-radius)
            elif(self.addingShape == "Box"):
                if(self.addingStage == 0):
                    self.temp_barrier.points = [self.touches[0][0], self.touches[0][1], p[0], p[1]]

        #If move, move clicked on object
        elif(self.movingObject):
            self.window.editMenu.disableMenu()

            if(isinstance(self.movingVar, Car) or isinstance(self.movingVar, pymunk.Circle)):
                p_scaled = (p[0]/self.scaller,p[1]/self.scaller)
                self.movingVar.body.position = p_scaled 
            elif(isinstance(self.movingVar, pymunk.Poly)):
                #Measure change in distance and apply vector to all points
                p1_scaled = (p[0]/self.scaller,p[1]/self.scaller)
                p0_scaled = (self.touches[0][0]/self.scaller,self.touches[0][1]/self.scaller)
                moveVector = (p1_scaled[0] - p0_scaled[0], p1_scaled[1] - p0_scaled[1])
                self.touches[0] = self.touches[1]

                vert = self.movingVar.get_vertices()
                self.movingVar.unsafe_set_vertices(((vert[0][0]+moveVector[0],vert[0][1]+moveVector[1]),
                                                    (vert[1][0]+moveVector[0],vert[1][1]+moveVector[1]),
                                                    (vert[2][0]+moveVector[0],vert[2][1]+moveVector[1]),
                                                    (vert[3][0]+moveVector[0],vert[3][1]+moveVector[1])))
                self.simulation.space.reindex_shapes_for_body(self.movingVar.body)

            elif(isinstance(self.movingVar, pymunk.Segment)):
                #Move only one point (closest)
                if(touch.is_double_tap):
                    if(self.movingPoint == "a"):
                        self.movingVar.unsafe_set_endpoints((p[0]/self.scaller, p[1]/self.scaller), self.movingVar.b)
                    else:
                        self.movingVar.unsafe_set_endpoints(self.movingVar.a, (p[0]/self.scaller, p[1]/self.scaller))
                
                #Move whole thing
                else:
                    p1_scaled = (p[0]/self.scaller,p[1]/self.scaller)
                    p0_scaled = (self.touches[0][0]/self.scaller,self.touches[0][1]/self.scaller)
                    moveVector = (p1_scaled[0] - p0_scaled[0], p1_scaled[1] - p0_scaled[1])
                    self.touches[0] = self.touches[1]
                    self.movingVar.unsafe_set_endpoints(
                                                        (self.movingVar.a[0]+moveVector[0],self.movingVar.a[1]+moveVector[1]),
                                                        (self.movingVar.b[0]+moveVector[0],self.movingVar.b[1]+moveVector[1]))
            
            self.simulation.space.reindex_shapes_for_body(self.movingVar.body)


    def on_touch_down(self, touch):
        #Scale screen if mouse scroll
        if(touch.button == "scrolldown"):
            if(self.scallerVar > 1000):
                self.scallerVar -= 100
        elif(touch.button == "scrollup"):
            if(self.scallerVar < 30000):
                self.scallerVar += 100

        #Cancel if right button
        if(touch.button == "right"):
            if(self.state == "editor"):
                if(self.editorTool == "add"):
                    self.changeTool("move")
                elif(self.editorTool == "delete"):
                    self.changeTool("move")
                else:
                    self.window.editMenu.setEditObject(None)
                #End level editor when right click
                #elif(self.editorTool == "move"):
                #    self.window.endLevelEditor()
            
        #Save current pos
        p = self.to_local(*touch.pos)
        self.touches[0] = p

        if(self.state == "editor" and touch.button == "left"):
            #Selecting none --> closes edit menu
            selectObject = None
            #If AddBarrier was clicked on, draw a line
            if(self.editorTool == "add"):
                self.adding_barrier = True
                self.addingShape = self.window.objectMenu.getData()["shape"]

                temp_shape = None

                with self.canvas:
                    Color(1,0,0,0.5)
                    if(self.addingShape == "Segment"):
                        temp_shape = Line(points = [p[0], p[1], p[0], p[1]], width = 10)
                    elif(self.addingShape == "Circle"):
                        temp_shape = Ellipse(pos=(p[0]+1, p[1]+1), size=(1,1))
                    elif(self.addingShape == "Box"):
                        if(self.addingStage == 0):
                            temp_shape = Line(points = [p[0], p[1], p[0], p[1]], width = 10)
                        else:
                            temp_shape = self.temp_barrier
                
                self.temp_barrier = temp_shape

            #Delete Object
            elif(self.editorTool == "delete"):
                deletePoint = (p[0]/self.scaller, p[1]/self.scaller)

                for shape in reversed(self.simulation.space.shapes):
                    if(shape.point_query(deletePoint)[0] < 0):
                        if(not isinstance(shape, Car)):
                            self.simulation.deleteObject(shape)
                            break

                self.deleteObject = False

            #Move object
            else:
                movePoint = (p[0]/self.scaller, p[1]/self.scaller)
                for shape in self.simulation.space.shapes:
                    if(shape.point_query(movePoint)[0] < 0):
                        self.movingObject = True
                        
                        #Select object for editing
                        selectObject = shape

                        #Move depending on the type
                        if(isinstance(shape, Car) or isinstance(shape, pymunk.Circle) or isinstance(shape, pymunk.Poly)):
                            self.movingVar = shape
                        if(isinstance(shape, pymunk.Segment)):
                            #Use nearest endpoint
                            self.movingVar = shape
                            p1 = movePoint
                            p2 = shape.a
                            p3 = shape.b
                            distance1 = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
                            distance2 = math.sqrt(((p1[0]-p3[0])**2)+((p1[1]-p3[1])**2))
                            if(distance1 < distance2):
                                self.movingPoint = "a"
                            else:
                                self.movingPoint = "b"

                if(not self.movingObject):
                    touch.grab(self)

            #If object selected then edit if not then send None --> Closes menu
            self.window.editMenu.setEditObject(selectObject)
        else:
            touch.grab(self)

    #Keyboard
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_up(self, keyboard, keycode):
        self.keys[keycode[1]] = 0

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keys[keycode[1]] = 1