import math
from pyglet.window import key
from . import physicalobject, resources, enviroment


class Player(physicalobject.PhysicalObject):
    """Physical object that responds to user input"""

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(img=resources.player_image, *args, **kwargs)

        # Set some easy-to-tweak constants
        self.thrust = 300.0
        self.rotate_speed = 200.0

        self.keys = dict(left=False, right=False, up=False)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP:
            self.keys['up'] = True
        elif symbol == key.LEFT:
            self.keys['left'] = True
        elif symbol == key.RIGHT:
            self.keys['right'] = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.keys['up'] = False
        elif symbol == key.LEFT:
            self.keys['left'] = False
        elif symbol == key.RIGHT:
            self.keys['right'] = False

    def update(self, dt):
        # Do all the normal physics stuff
        super(Player, self).update(dt)

        vel_x_abs = abs(self.velocity_x)
        vel_y_abs = abs(self.velocity_y)
        if(vel_x_abs != 0 and vel_y_abs != 0):
            if(vel_x_abs < vel_y_abs):
                resistance_x_ratio = vel_x_abs/vel_y_abs
                resistance_y_ratio = 1
            else:
                resistance_y_ratio = vel_y_abs/vel_x_abs
                resistance_x_ratio = 1
        else:
            resistance_x_ratio = 1
            resistance_y_ratio = 1

        if(vel_x_abs != 0):
            self.velocity_x += (-enviroment.resistance * dt if self.velocity_x > 0 else enviroment.resistance * dt) * resistance_x_ratio
        else:
            self.velocity_x = 0

        if(vel_y_abs != 0):
            self.velocity_y += -enviroment.resistance * dt if self.velocity_y > 0 else enviroment.resistance * dt
        else:
            self.velocity_y = 0

        if self.keys['left']:
            self.rotation -= self.rotate_speed * dt
        if self.keys['right']:
            self.rotation += self.rotate_speed * dt

        if self.keys['up']:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x += force_x
            self.velocity_y += force_y
