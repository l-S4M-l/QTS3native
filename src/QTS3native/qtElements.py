from PyQt5 import QtWidgets, QtCore
from .rpcs3Hooks import skate_3_internal_menu_controller, ControllerThread, Controller
from .keylistener import GlobalKeyboardListener
from collections import deque
from pymem import Pymem
import sys
import time
import clipboard

class bind_vals:
    DPAD_UP                = "DPAD_UP"
    DPAD_DOWN              = "DPAD_DOWN"
    DPAD_LEFT              = "DPAD_LEFT"
    DPAD_RIGHT             = "DPAD_RIGHT"
    START                  = "START"
    SELECT                 = "SELECT"
    LEFT_THUMB             = "LEFT_THUMB"
    RIGHT_THUMB            = "RIGHT_THUMB"
    LEFT_SHOULDER          = "LEFT_SHOULDER"
    RIGHT_SHOULDER         = "RIGHT_SHOULDER"
    A                      = "A"
    B                      = "B"
    X                      = "X"
    Y                      = "Y"
    left_trigger           = "left_trigger"
    right_trigger          = "right_trigger"
    left_stick_click       = "left_stick_click"
    right_stick_click      = "right_stick_click"

class bind_handler(QtCore.QObject):
    bind_hit = QtCore.pyqtSignal()

    def __init__(self, controller_thread:ControllerThread, parent=None):
        super().__init__(parent)
        if controller_thread == None:
            raise ValueError("Controller thread doesnt exists.")

        self.controller = controller_thread

        self.controller.state_changed.connect(self.check_bind)
        self.binds = bind_vals()
        
        self.bind = []

        self.DPAD_UP:bool                = True
        self.DPAD_DOWN:bool              = True
        self.DPAD_LEFT:bool              = True
        self.DPAD_RIGHT:bool             = True
        self.START:bool                  = True
        self.SELECT:bool                 = True
        self.LEFT_THUMB:bool             = True
        self.RIGHT_THUMB:bool            = True
        self.LEFT_SHOULDER:bool          = True
        self.RIGHT_SHOULDER:bool         = True
        self.A:bool                      = True
        self.B:bool                      = True
        self.X:bool                      = True
        self.Y:bool                      = True

        self.left_trigger:float          = 128
        self.right_trigger:float         = 128

        self.left_stick_click            = True
        self.right_stick_click           = True
    
    def set_bind(self, bind:list = None):
        if bind == None:
            return

        the_vars = list(vars(bind_vals).values())

        for i in bind:
            if i not in the_vars:
                raise ValueError("bind key is not part of binds")
        
        self.bind = bind

    def check_bind(self,controller:Controller):
        bind_hit = True

        if self.bind == []:
            bind_hit = False

        for bind_key in self.bind:
            expected_value = getattr(self, bind_key)

            if bind_key != self.binds.left_stick_click and bind_key != self.binds.right_stick_click:
                current_value = getattr(controller, bind_key)
            
            else:
                if bind_key == self.binds.left_stick_click:
                    current_value = controller.left_stick.click
                if bind_key == self.binds.right_stick_click:
                    current_value = controller.right_stick.click

            
            if isinstance(expected_value, bool):
                if current_value != expected_value:
                    bind_hit = False
                    break
            else:
                if current_value < expected_value:
                    bind_hit = False
                    break

        if bind_hit == True:
            self.bind_hit.emit()

class menu_inputs:
    UP             = "UP"
    DOWN           = "DOWN"
    LEFT           = "LEFT"
    RIGHT          = "RIGHT"
    A              = "A"
    B              = "B"
    X              = "X"
    Y              = "Y"
    LEFT_TRIGGER   = "LEFT_TRIGGER"
    RIGHT_TRIGGER  = "RIGHT_TRIGGER"
    LEFT_SHOULDER  = "LEFT_SHOULDER"
    RIGHT_SHOULDER = "RIGHT_SHOULDER"




class _base_menu_item(QtCore.QObject):
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self._parent_menu:sub_menu | None = None
        self._selected = False
        self._max_length_text = 38

    def set_parent_menu(self, parent_menu):
        self._parent_menu:sub_menu = parent_menu

    def set_selected(self, Selected):
        self._selected = Selected

    def key_pressed(self,key_press):
        pass

    def text(self):
        pass

    def up(self):
        pass

    def down(self):
        pass

    def left(self):
        pass

    def right(self):
        pass

    def click(self):
        self.clicked.emit()

class menu_item(_base_menu_item):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._text = ""
    
    def set_text(self,text_string):
        self._text = text_string

    def text(self):
        return self._text
    
class menu_typing_item(_base_menu_item):
    value_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self._label = ""
        self._render_value = ""
        self._value = ""
        self.is_cursor = False

        self.cursor_timer = QtCore.QTimer()
        self.cursor_timer.timeout.connect(self.cursor_render)
        self.cursor_timer.start(500)
    
    def set_label(self,text_string):
        self._label = text_string

    def set_value(self, value):
        self._value = value

    def check_length(self):
        text_val = f"{self._label}: {self._render_value}"
        length = len(text_val)

        return length

    def key_pressed(self, key_press):
        super().key_pressed(key_press)
        if self._parent_menu == None:
            return
        try:
            current_menu_controller:menu_controller = self._parent_menu.menu_controller
        except:
            return

        if self._selected == True:
            if current_menu_controller.menu_shown == 1:
                if key_press[0] == "BACKSPACE":
                    if len(self._value) != 0:
                        self._value = f"{self._value[:-1]}"
                        self.value_changed.emit(self._value)

                if self.check_length() <= self._max_length_text:
                    
                    if (key_press == ("CTRL", "v")) or (key_press == ("CTRL", "V")): #newline bugged
                        value = clipboard.paste()

                        value = value.replace("\n"," ")

                        combined_value = f"{self._value}{value}"

                        if len(combined_value) >= self._max_length_text:
                            combined_value = combined_value[0:self._max_length_text]

                        self._value = combined_value

                    elif key_press[0] == "SPACE":
                        self._value = f"{self._value} "

                    elif key_press[0] == "SHIFT":
                        try:
                            if key_press[1] not in current_menu_controller.key_listener.NON_SYMBOL_KEYS:
                                self._value = f"{self._value}{key_press[1].upper()}"
                        except IndexError:
                            pass

                    elif key_press[0] not in current_menu_controller.key_listener.NON_SYMBOL_KEYS:
                        self._value = f"{self._value}{key_press[0]}"
                
                    self.value_changed.emit(self._value)


    def cursor_render(self):
        self.is_cursor = not self.is_cursor

    def text(self):
        final_text = self._label

        if self.is_cursor == False:
            self._render_value = f"{self._value}"
        elif self.is_cursor == True:
            self._render_value = f"{self._value}_"

        final_text = f"{final_text}: {self._render_value}"

        return final_text

class menu_option:
    _value = ""

    def __init__(self, text):
        self._value = text
    def set_value(self, value):
        self._value = value
    def value(self):
        return self._value

class menu_option_item(_base_menu_item):

    value_change = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._label = ""
        self._options:list[menu_option] = []
        self._current_index = 0

    def text(self):
        try:
            return f"{self._label}: {self._options[self._current_index].value()}"
        except IndexError:
            return ""
    
    def set_label(self, label):
        self._label = label
    
    def add_option(self, option):
        self._options.append(option)

    def current_option(self):
        return self._options[self._current_index]
    
    def current_index(self):
        return self._current_index
    
    def set_current_option(self, current_option):
        for val, option in enumerate(self._options):
            if option == current_option:
                self._current_index = val
                return
        
        raise IndexError()
    
    def set_current_index(self, current_index):
        self._current_index = current_index

    def add_items(self, option_items:list[menu_option]):
        for option in option_items:
            self.add_option(option)

    def left(self):
        super().left()

        if self._current_index != 0:
            self._current_index = self._current_index - 1

    def right(self):
        super().right()

        if self._current_index != (len(self._options))-1:
            self._current_index = self._current_index + 1

class menu_slider_item(_base_menu_item):
    value_change = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._label = ""
        self._options:list[menu_option] = []
        self._current_index = 0

    def text(self):
        return f"{self._label}: {self._options[self._current_index].value()}"
    
    def set_label(self, label):
        self._label = label

    def value(self):
        return int(self._options[self._current_index].value())
    
    def current_index(self):
        return self._current_index
    
    def set_current_option(self, current_option):
        for val, option in enumerate(self._options):
            if option == current_option:
                self._current_index = val
                return
        
        raise IndexError()
    
    def set_current_index(self, current_index):
        self._current_index = current_index

    def set_range(self, range_val:tuple):
        for option in range(range_val[0], range_val[1]+1):
            self._options.append(menu_option(option))

    def left(self):
        super().left()

        if self._current_index != 0:
            self._current_index = self._current_index - 1

    def right(self):
        super().right()

        if self._current_index != (len(self._options))-1:
            self._current_index = self._current_index + 1


class sub_menu(QtCore.QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self._title = ""
        self._menu_items:list[menu_item] = []
        self._selected_item:menu_item = None
        self.menu_controller:menu_controller = None

    def _set_menu_controller(self, menu_controller):
        self.menu_controller = menu_controller

    def set_title(self,title):
        self._title = title
    def title(self):
        return self._title
    
    def add_item(self,item:menu_item):
        if item not in self._menu_items:
            self._menu_items.append(item)
            item.set_parent_menu(self)

    def remove_item(self,item):
        for list_index, list_item in enumerate(self._menu_items):
            if list_item == item:
                del self._menu_items[list_index]
            
    
    def set_selected_item(self,item:_base_menu_item):
        if self._selected_item != None:
            self._selected_item.set_selected(False)

        if isinstance(item, _base_menu_item):
            self._selected_item = item
            self._selected_item.set_selected(True)

    def selected_item(self):
        return self._selected_item
    
    
    def selected_item_index(self):
        index = -1
        for i, menu_item in enumerate(self._menu_items):
            if menu_item == self._selected_item:
                index = i
                break
        
        return index

    def get_text(self):
        final_text = ""

        
        for i in self._menu_items:
            i: menu_item = i
            if final_text:
                final_text += "\n"
            final_text += i.text()

        final_text = final_text.rstrip("\n")
        return final_text
    
    #button
    def a_button_pressed(self):
        item = self.selected_item()

        if item != None:
            item.click()

    def b_button_pressed(self):
        pass

    def x_button_pressed(self):
        pass

    def y_button_pressed(self):
        pass

    def left_trigger_button_pressed(self):
        pass

    def right_trigger_button_pressed(self):
        pass

    def left_shoulder_button_pressed(self):
        pass

    def right_shoulder_button_pressed(self):
        pass
    
    def up_button_pressed(self):
        current_item_index = self.selected_item_index()
        if current_item_index != 0:
            if self.selected_item() != None:
                self.set_selected_item(self._menu_items[current_item_index-1])

    def down_button_pressed(self):
        current_item_index = self.selected_item_index()
        if current_item_index != (len(self._menu_items))-1:
            if self.selected_item() != None:
                self.set_selected_item(self._menu_items[current_item_index+1])

    def left_button_pressed(self):
        if self.selected_item() != None:
            self._selected_item.left()
    
    def right_button_pressed(self):
        if self.selected_item() != None:
            self._selected_item.right()

    #key press
    def key_pressed(self,keys):
        if self._selected_item != None:
            self._selected_item.key_pressed(keys)

class menu_controller(QtCore.QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._menu:sub_menu = None

        process = Pymem("rpcs3.exe")
        self.internal_menu_controller = skate_3_internal_menu_controller(process)
        self.controller = ControllerThread(rpcs3_process=process)
        self.controller.state_changed.connect(self.controller_input_enter)
        self.controller.start()
        self.bind_handler = bind_handler(controller_thread=self.controller)
        self.bind_handler.bind_hit.connect(self.bind_hit)
        self.key_listener = GlobalKeyboardListener()
        self.key_listener.keys_pressed.connect(self.key_pressed)
        self.key_listener.start()

        self.last_button_press = 0
        self.button_press_debounce_ms = 100
        self.menu_shown = 1

        self.available_inputs = menu_inputs()

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(33)


        self.menu_shown = 0

    def set_bind(self, bind = None):
        self.bind_handler.set_bind(bind)

    def set_menu(self,menu:sub_menu):
        menu._set_menu_controller(self)
        self._menu = menu

        self.input_callbacks = {
                    self.available_inputs.UP: self._menu.up_button_pressed,
                    self.available_inputs.DOWN: self._menu.down_button_pressed,
                    self.available_inputs.LEFT: self._menu.left_button_pressed,
                    self.available_inputs.RIGHT: self._menu.right_button_pressed,
                    self.available_inputs.A: self._menu.a_button_pressed,
                    self.available_inputs.B: self._menu.b_button_pressed,
                    self.available_inputs.X: self._menu.x_button_pressed,
                    self.available_inputs.Y: self._menu.y_button_pressed,
                    self.available_inputs.LEFT_TRIGGER: self._menu.left_trigger_button_pressed,
                    self.available_inputs.RIGHT_TRIGGER: self._menu.right_trigger_button_pressed,
                    self.available_inputs.LEFT_SHOULDER: self._menu.left_shoulder_button_pressed,
                    self.available_inputs.RIGHT_SHOULDER: self._menu.right_shoulder_button_pressed,
                }

    def bind_hit(self):
        if self.menu_shown == 0:
            self.menu_shown = 1

    def key_pressed(self, keys):
        if self._menu != None:
            self._menu.key_pressed(keys)        

    def key_checks(self, controller:Controller):
        stick_activate_value = 10000
        trigger_activation_value = 100

        if controller.A == True:
            return self.available_inputs.A

        elif controller.B == True:
            return self.available_inputs.B

        if controller.X == True:
           return self.available_inputs.X

        if controller.Y == True:
           return self.available_inputs.Y

        if controller.LEFT_SHOULDER == True:
           return self.LEFT_SHOULDER

        if controller.RIGHT_SHOULDER == True:
           return self.available_inputs.RIGHT_SHOULDER

        
        if controller.right_trigger >= trigger_activation_value:
            return self.available_inputs.RIGHT_TRIGGER
        
        if controller.left_trigger >= trigger_activation_value:
            return self.available_inputs.LEFT_TRIGGER

        elif controller.DPAD_UP == True or controller.left_stick.y_axis >= stick_activate_value:
            return self.available_inputs.UP

        elif controller.DPAD_DOWN == True or controller.left_stick.y_axis <= (-1*stick_activate_value):
            return self.available_inputs.DOWN

        elif controller.DPAD_LEFT == True or controller.left_stick.x_axis <= (-1*stick_activate_value):
            return self.available_inputs.LEFT
        elif controller.DPAD_RIGHT == True or controller.left_stick.x_axis >= stick_activate_value:
            return self.available_inputs.RIGHT

    def controller_input_enter(self, controller:Controller):

            current_time_ms = int(time.time() * 1000)
            if self.menu_shown == 1:

                current_input = self.key_checks(controller=controller)

                if current_input == None:
                    return

                if self.last_button_press+self.button_press_debounce_ms < current_time_ms:
                    self.last_button_press = current_time_ms

                    self.input_callbacks[current_input]()

                    


    def close_menu(self):
        self.internal_menu_controller.show(False)
        self.internal_menu_controller.set_default_text()
        self.menu_shown = 0

    def refresh(self):
        if self.menu_shown == 1:
            self.render()

    def render(self):

        if self._menu != None:
            title = self._menu.title()
            selected_index = self._menu.selected_item_index()
            self.internal_menu_controller.selected_index = selected_index
            self.internal_menu_controller.set_text(self._menu.get_text(), title)
            self.internal_menu_controller.show()
            self.menu_shown = 1


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    
    test_case = 1
    if test_case == 1:

        class new_sub_menu(sub_menu):
            def __init__(self, parent=None):
                super().__init__(parent)

            def b_button_pressed(self):
                if self.menu_controller:
                    self.menu_controller.close_menu()

        new_menu = new_sub_menu()

        typing_menu_item = menu_typing_item()
        typing_menu_item.set_label("Typing Shit")
        new_menu.add_item(typing_menu_item)

        menu_option_new = menu_option_item()
        menu_option_new.set_label("option pick")
        menu_option_new.add_items([
            menu_option("option01"),
            menu_option("option02"),
            menu_option("option03"),
            menu_option("option04"),
            menu_option("option05"),
            menu_option("option06"),
            menu_option("option07"),
            menu_option("option08"),
            menu_option("option09"),
            menu_option("option10"),
            menu_option("option11"),
            menu_option("option12"),
            menu_option("option13"),
        ])

        new_menu.add_item(menu_option_new)

        new_slider = menu_slider_item()
        new_slider.set_label("slider testing")
        new_slider.set_range((41, 67)) 

        new_menu.add_item(new_slider)

        for i in range(10):
            new_menu_item = menu_item()
            new_menu_item.set_text(f"Hello world{i}")
            new_menu.add_item(new_menu_item)

        new_menu.set_selected_item(typing_menu_item)
        new_menu.set_title("TESTING TITLE")

        new_menu_controller = menu_controller()
        new_menu_controller.set_menu(new_menu)

        menu_bind_handler = new_menu_controller.bind_handler
        new_menu_controller.set_bind([menu_bind_handler.binds.right_stick_click])

    if test_case == 2:
        pass


    sys.exit(app.exec_())