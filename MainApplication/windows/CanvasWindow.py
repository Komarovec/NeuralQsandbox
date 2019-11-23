import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

# Custom classes
from windows.GameWidgets import ToolBar, ToolBarGame, ToolBarEditor, StateBar, StateInfoBar, StartMenu, ObjectMenu, EditMenu
from windows.Simulation import Simulation
from windows.CanvasHandler import CanvasHandler
from objs.GameObjects import StaticGameObject

# Window class, manages GUI and creates internal CanvasHandler object
class CanvasWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = None
        self.app = App.get_running_app()

    # Entered the screen
    def on_enter(self):
        if(self.game == None):
            self.create_game()

    # Screen left
    def on_leave(self):
        pass

    # Deltes CanvasHandler object and all GUI
    def delete_game(self):
        self.game.stop()
        self.clear_widgets()
        self.remove_widget(self.game)
        self.game = None

    # Creates CanvasHandler object and all GUI
    def create_game(self):
        self.game = CanvasHandler()
        self.gameToolbar = ToolBarGame(self.manager, self.game, self)
        self.editorToolbar = ToolBarEditor(self.manager, self.game, self)
        self.statebar = StateBar(self.game, self)
        self.stateInfoBar = StateInfoBar(self.game, self)
        self.objectMenu = ObjectMenu(self.game, self)
        self.editMenu = EditMenu(self.game, self)
        self.startMenu = StartMenu(self.game, self)

        self.game.size_hint = 1,1
        self.game.pos = 0,0

        self.add_widget(self.game, 10)
        self.add_widget(self.statebar)
        self.add_widget(self.gameToolbar)

        self.simulation = Simulation(self.game)

        self.game.init(self)
        self.game.start(self.simulation)
        
        self.toggleStartMenu(True)
        # self.add_widget(self.build())

    # Open/Close start menu // True/False
    def toggleStartMenu(self, state):
        if(state):
            self.add_widget(self.startMenu)
        else:
            self.remove_widget(self.startMenu) 

    # Open/Close start menu
    def toggleObjectMenu(self):
        if(self.objectMenu.visible):
            self.disableObjectMenu()
        else:
            self.enableObjectMenu()

    # Closes object menu
    def disableObjectMenu(self):
        self.remove_widget(self.objectMenu)
        self.objectMenu.visible = False

    # Opens object menu
    def enableObjectMenu(self):
        size = self.objectMenu.ids["mainLayout"].size[1]
        self.objectMenu.ids["mainLayout"].size[1] = 0

        self.add_widget(self.objectMenu)
        self.objectMenu.visible = True

        animation = Animation(size=(self.objectMenu.ids["mainLayout"].size[0],size), duration=.1)
        animation.start(self.objectMenu.ids["mainLayout"])

    # Closes/Opens object menu
    def toggleStateInfoBar(self, state):
        if(state == "normal"):
            self.remove_widget(self.stateInfoBar)
        else:
            self.add_widget(self.stateInfoBar)

    # Ends level editor & closes everything 
    def endLevelEditor(self):
        self.remove_widget(self.editorToolbar)
        self.add_widget(self.gameToolbar)
        self.disableObjectMenu()

        self.game.changeState("game")

    # OPens level editor & opens everything
    def startLevelEditor(self):
        self.add_widget(self.editorToolbar)
        self.remove_widget(self.gameToolbar)
        self.enableObjectMenu()

        self.game.changeState("editor")
