from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

WARNING_ICON = "warning"
DANGER_ICON = "danger"
INFO_ICON = "info"

def getIcon(picture):
    if(picture == WARNING_ICON):
        return Image(source="icons/warningicon.png", size_hint=(0.4, 1))
    elif(picture == DANGER_ICON):
        return Image(source="icons/dangericon.png", size_hint=(0.4, 1))
    elif(picture == INFO_ICON):
        return Image(source="icons/infoicon.png", size_hint=(0.4, 1))
    else:
        return None

class InfoPopup():
    def __init__(self, text, title="Information", picture=None, size=(400,300)):
            #Popup layouts
            content = BoxLayout(orientation="vertical")
            subcontent = BoxLayout(orientation="horizontal")

            #Create popup object
            popup = Popup(title=title, content=content, size_hint=(None,None), size=size)

            #Add text and icon
            subcontent.add_widget(Label(text=text))
            icon = getIcon(picture)
            if(icon != None):
                subcontent.add_widget(icon)

            #Create popup
            content.add_widget(subcontent)
            content.add_widget(Button(text="Close", on_press=popup.dismiss, size_hint=(1, 0.2)))
            popup.open()

class ConfirmPopup():
    def __init__(self, text, title, fnc, picture=None, size=(400,300)):
            #Execute this function when clicked yes
            self.fnc = fnc

            #Popup layouts
            content = BoxLayout(orientation="vertical")
            subcontent = BoxLayout(orientation="horizontal")
            buttons = BoxLayout(orientation="horizontal", size_hint=(1, 0.2))

            #Create popup object
            self.popup = popup = Popup(title=title, content=content, size_hint=(None,None), size=size)

            #Add text and icon
            subcontent.add_widget(Label(text=text))
            icon = getIcon(picture)
            if(icon != None):
                subcontent.add_widget(icon)

            #When user wants to continue
            def clickedYes(*args):
                self.fnc()
                self.popup.dismiss()

            #Add buttons
            buttons.add_widget(Button(text="Cancel", on_press=popup.dismiss))
            buttons.add_widget(Button(text="Continue", on_press=clickedYes))

            #Create popup
            content.add_widget(subcontent)
            content.add_widget(buttons)
            popup.open()
