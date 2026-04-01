from PyQt5 import QtWidgets, QtCore
from pymem import Pymem, exception as pymem_exception
import struct
import math

class analog_stick:
    click:bool   = False
    x_axis:float = 0
    y_axis:float = 0
class Controller:
    DPAD_UP:bool                = False
    DPAD_DOWN:bool              = False
    DPAD_LEFT:bool              = False
    DPAD_RIGHT:bool             = False
    START:bool                  = False
    SELECT:bool                 = False
    LEFT_SHOULDER:bool          = False
    RIGHT_SHOULDER:bool         = False
    A:bool                      = False
    B:bool                      = False
    X:bool                      = False
    Y:bool                      = False
       
    left_trigger:float          = 0
    right_trigger:float         = 0

    left_stick:analog_stick     = analog_stick()
    right_stick:analog_stick    = analog_stick()

    def _to_dict(self):
        """
        TESTING NOT TO BE USE IN PRODUCTION
        """

        button_vals = {
          "DPAD_UP": self.DPAD_UP,
          "DPAD_DOWN": self.DPAD_DOWN,
          "DPAD_LEFT": self.DPAD_LEFT,
          "DPAD_RIGHT": self.DPAD_RIGHT,
          "START": self.START,
          "SELECT": self.SELECT,
          "LEFT_THUMB": self.LEFT_THUMB,
          "RIGHT_THUMB": self.RIGHT_THUMB,
          "LEFT_SHOULDER": self.LEFT_SHOULDER,
          "RIGHT_SHOULDER": self.RIGHT_SHOULDER,
          "A": self.A,
          "B": self.B,
          "X": self.X,
          "Y": self.Y,
          "left_trigger": self.left_trigger,
          "right_trigger": self.right_trigger 
        }

        stick_vals = {
                "left_stick": (
                    self.left_stick.x_axis,
                    self.left_stick.y_axis
                ),
                "right_stick": (
                    self.right_stick.x_axis,
                    self.right_stick.y_axis
                ),
            }
        
        new_state = {
                "stick_values": stick_vals,
                "buttons": button_vals
            }
        
        return new_state

class rpcs3_offset_values:
    def __init__(self):
        self.X_button_value_offset          = 0x33002CD68
        self.Y_button_value_offset          = 0x33002CD38
        self.A_button_value_offset          = 0x33002CD58
        self.B_button_value_offset          = 0x33002CD48
        self.dpad_up_button_value_offset    = 0x33002CCB8
        self.dpad_down_button_value_offset  = 0x33002CCD8
        self.dpad_left_button_value_offset  = 0x33002CCE8
        self.dpad_right_button_value_offset = 0x33002CCC8
        self.start_button_value_offset      = 0x33002CCA8
        self.select_button_value_offset     = 0x33002CC78
        self.rb_button_value_offset         = 0x33002DB98
        self.lb_button_value_offset         = 0x33002DB88
        self.left_stick_button_offset       = 0x33002DAF8
        self.right_stick_button_offset      = 0x33002DB08
        
        self.right_stick_right_offset       = 0x33002DBF8
        self.right_stick_left_offset        = 0x33002DBE8
        self.right_stick_down_offset        = 0x33002DC18
        self.right_stick_up_offset          = 0x33002DC08
        
        self.left_stick_right_offset        = 0x33002DC38
        self.left_stick_left_offset         = 0x33002DC28
        self.left_stick_down_offset         = 0x33002DC58
        self.left_stick_up_offset           = 0x33002DC48
        
        self.left_trigger_offset            = 0x33002DB68
        self.right_trigger_offset           = 0x33002DB78

        self.menu_show_byte                 = 0x330010DB3
        self.menu_text_pointer              = 0x340602EA0


    def from_dict(self, offset_dict):
        if offset_dict["controller_offsets"] != None:
            self.X_button_value_offset          = offset_dict["controller_offsets"].get("X_button_value_offset", 0x33002CD68)
            self.Y_button_value_offset          = offset_dict["controller_offsets"].get("Y_button_value_offset", 0x33002CD38)
            self.A_button_value_offset          = offset_dict["controller_offsets"].get("A_button_value_offset", 0x33002CD58)
            self.B_button_value_offset          = offset_dict["controller_offsets"].get("B_button_value_offset", 0x33002CD48)
            self.dpad_up_button_value_offset    = offset_dict["controller_offsets"].get("dpad_up_button_value_offset", 0x33002CCB8)
            self.dpad_down_button_value_offset  = offset_dict["controller_offsets"].get("dpad_down_button_value_offset", 0x33002CCD8)
            self.dpad_left_button_value_offset  = offset_dict["controller_offsets"].get("dpad_left_button_value_offset", 0x33002CCE8)
            self.dpad_right_button_value_offset = offset_dict["controller_offsets"].get("dpad_right_button_value_offset", 0x33002CCC8)
            self.start_button_value_offset      = offset_dict["controller_offsets"].get("start_button_value_offset", 0x33002CCA8)
            self.select_button_value_offset     = offset_dict["controller_offsets"].get("select_button_value_offset", 0x33002CC78)
            self.rb_button_value_offset         = offset_dict["controller_offsets"].get("rb_button_value_offset", 0x33002DB98)
            self.lb_button_value_offset         = offset_dict["controller_offsets"].get("lb_button_value_offset", 0x33002DB88)
            self.left_stick_button_offset       = offset_dict["controller_offsets"].get("left_stick_button_offset", 0x33002DAF8)
            self.right_stick_button_offset      = offset_dict["controller_offsets"].get("right_stick_button_offset", 0x33002DB08)

            self.right_stick_right_offset       = offset_dict["controller_offsets"].get("right_stick_right_offset", 0x33002DBF8)
            self.right_stick_left_offset        = offset_dict["controller_offsets"].get("right_stick_left_offset", 0x33002DBE8)
            self.right_stick_down_offset        = offset_dict["controller_offsets"].get("right_stick_down_offset", 0x33002DC18)
            self.right_stick_up_offset          = offset_dict["controller_offsets"].get("right_stick_up_offset", 0x33002DC08)

            self.left_stick_right_offset        = offset_dict["controller_offsets"].get("left_stick_right_offset", 0x33002DC38)
            self.left_stick_left_offset         = offset_dict["controller_offsets"].get("left_stick_left_offset", 0x33002DC28)
            self.left_stick_down_offset         = offset_dict["controller_offsets"].get("left_stick_down_offset", 0x33002DC58)
            self.left_stick_up_offset           = offset_dict["controller_offsets"].get("left_stick_up_offset", 0x33002DC48)

            self.left_trigger_offset            = offset_dict["controller_offsets"].get("left_trigger_offset", 0x33002DB68)
            self.right_trigger_offset           = offset_dict["controller_offsets"].get("right_trigger_offset", 0x33002DB78)

            self.menu_show_byte                 = offset_dict["render_offset"].get("menu_show_byte", 0x330010DB3)
            self.menu_text_pointer              = offset_dict["render_offset"].get("menu_text_pointer", 0x340602EA0)

class ControllerThread(QtCore.QThread):
    state_changed = QtCore.pyqtSignal(object)
    controller = Controller()

    def __init__(self, parent=None, rpcs3_process:Pymem=None):
        super().__init__(parent)

        self._running = True
        self.stick_deadzone = 8000
        self.trigger_deadzone = 30

        if rpcs3_process == None:
            raise pymem_exception.ProcessNotFound("rpcs3.exe")
        
        name = next(rpcs3_process.list_modules()).name

        if name != "rpcs3.exe":
            raise pymem_exception.ProcessNotFound("rpcs3.exe")
        
        self.rpcs3_process = rpcs3_process

        offsets = rpcs3_offset_values()

        self.X_button_value_offset          = offsets.X_button_value_offset
        self.Y_button_value_offset          = offsets.Y_button_value_offset
        self.A_button_value_offset          = offsets.A_button_value_offset
        self.B_button_value_offset          = offsets.B_button_value_offset
        self.dpad_up_button_value_offset    = offsets.dpad_up_button_value_offset
        self.dpad_down_button_value_offset  = offsets.dpad_down_button_value_offset
        self.dpad_left_button_value_offset  = offsets.dpad_left_button_value_offset
        self.dpad_right_button_value_offset = offsets.dpad_right_button_value_offset
        self.start_button_value_offset      = offsets.start_button_value_offset
        self.select_button_value_offset     = offsets.select_button_value_offset
        self.rb_button_value_offset         = offsets.rb_button_value_offset
        self.lb_button_value_offset         = offsets.lb_button_value_offset
        self.left_stick_button_offset       = offsets.left_stick_button_offset
        self.right_stick_button_offset      = offsets.right_stick_button_offset

        self.right_stick_right_offset       = offsets.right_stick_right_offset
        self.right_stick_left_offset        = offsets.right_stick_left_offset
        self.right_stick_down_offset        = offsets.right_stick_down_offset
        self.right_stick_up_offset          = offsets.right_stick_up_offset
    
        self.left_stick_right_offset        = offsets.left_stick_right_offset
        self.left_stick_left_offset         = offsets.left_stick_left_offset
        self.left_stick_down_offset         = offsets.left_stick_down_offset
        self.left_stick_up_offset           = offsets.left_stick_up_offset

        self.left_trigger_offset            = offsets.left_trigger_offset
        self.right_trigger_offset           = offsets.right_trigger_offset

    def apply_analog_deadzone(self, value):
        return value if abs(value) >= self.stick_deadzone else 0
    
    def apply_trigger_deadzone(self, value):
        return value if abs(value) >= self.trigger_deadzone else 0
    
    def read_button_value(self,button_offset):
        button_bytes = self.rpcs3_process.read_bytes(button_offset, 4)
        button_value = struct.unpack(">f", button_bytes)[0]

        return button_value == 1
    
    def read_analog_stick_value(self, low_offset, high_offset):
        stick_range = 32767

        low_val_raw = self.rpcs3_process.read_bytes(low_offset,4)
        low_val_unmapped:float = struct.unpack(">f", low_val_raw)[0]
        low_val_mapped = (low_val_unmapped * stick_range)* -1

        high_val_raw = self.rpcs3_process.read_bytes(high_offset,4)
        high_val_unmapped:float = struct.unpack(">f", high_val_raw)[0]
        high_val_mapped = high_val_unmapped * stick_range


        return high_val_mapped + low_val_mapped

    def read_trigger_value(self, stick_offset):
        trigger_range = 255

        self.trigger_val_raw = self.rpcs3_process.read_bytes(stick_offset,4)
        self.trigger_val:float = struct.unpack(">f", self.trigger_val_raw)[0]
        
        return self.trigger_val * trigger_range
    
    def run(self):
        while self._running:

            self.controller.left_stick.x_axis = self.apply_analog_deadzone(self.read_analog_stick_value(
                        self.left_stick_left_offset,
                        self.left_stick_right_offset
                    ))

            self.controller.left_stick.y_axis = self.apply_analog_deadzone(self.read_analog_stick_value(
                        self.left_stick_down_offset,
                        self.left_stick_up_offset
                    ))
            
            self.controller.right_stick.x_axis = self.apply_analog_deadzone(self.read_analog_stick_value(
                        self.right_stick_left_offset,
                        self.right_stick_right_offset
                    ))
            self.controller.right_stick.y_axis = self.apply_analog_deadzone(self.read_analog_stick_value(
                        self.right_stick_down_offset,
                        self.right_stick_up_offset
                    ))
            
            self.controller.DPAD_UP           = self.read_button_value(self.dpad_up_button_value_offset)
            self.controller.DPAD_DOWN         = self.read_button_value(self.dpad_down_button_value_offset)
            self.controller.DPAD_LEFT         = self.read_button_value(self.dpad_left_button_value_offset)
            self.controller.DPAD_RIGHT        = self.read_button_value(self.dpad_right_button_value_offset)
            self.controller.START             = self.read_button_value(self.start_button_value_offset)
            self.controller.SELECT            = self.read_button_value(self.select_button_value_offset)
            self.controller.left_stick.click  = self.read_button_value(self.left_stick_button_offset)
            self.controller.right_stick.click = self.read_button_value(self.right_stick_button_offset)
            self.controller.LEFT_SHOULDER     = self.read_button_value(self.lb_button_value_offset)
            self.controller.RIGHT_SHOULDER    = self.read_button_value(self.rb_button_value_offset)
            self.controller.A                 = self.read_button_value(self.A_button_value_offset)
            self.controller.B                 = self.read_button_value(self.B_button_value_offset)
            self.controller.X                 = self.read_button_value(self.X_button_value_offset)
            self.controller.Y                 = self.read_button_value(self.Y_button_value_offset)
            self.controller.left_trigger      = self.apply_trigger_deadzone(self.read_trigger_value(self.left_trigger_offset))
            self.controller.right_trigger     = self.apply_trigger_deadzone(self.read_trigger_value(self.right_trigger_offset))


            self.state_changed.emit(self.controller) #read stick click vals
            self.msleep(3)

    def stop(self):
        self._running = False
        self.wait()


class skate_3_internal_menu_controller:
    def __init__(self, rpcs3_process:Pymem=None):
        if rpcs3_process == None:
            raise pymem_exception.ProcessNotFound("rpcs3.exe")
        
        name = next(rpcs3_process.list_modules()).name

        offsets = rpcs3_offset_values()

        if name != "rpcs3.exe":
            raise pymem_exception.ProcessNotFound("rpcs3.exe")

        self.rpcs3_process = rpcs3_process

        self.menu_show_byte = offsets.menu_show_byte
        self.menu_text_pointer = offsets.menu_text_pointer

        self.default_text = "Wireless controller has been disconnected, please reconnect the wireless controller"

        self.selected_index = 0
        self.current_text = ""

        self.line_count = 7

        pointer_value = int.from_bytes(self.rpcs3_process.read_bytes(self.menu_text_pointer,4))
        self.menu_text_address = pointer_value + 0x300000000

    def show(self, on:bool = True):
        self.rpcs3_process.write_bool(self.menu_show_byte, on)

    def set_text(self,text:str, title):

        final_text = ""
        text_lines = text.split("\n")
        for index_val, text_line in enumerate(text_lines):
            if index_val == self.selected_index:
                text_lines[index_val] = f">{text_line}"
        
        render_range = (0,self.line_count)

        floor = math.floor((self.line_count-1)/2)
        ceil  =  math.ceil((self.line_count-1)/2)
        length = len(text_lines)

        if length <= self.line_count:
            render_range = (0, length)
        elif self.selected_index >= length - ceil:
            render_range = (length - self.line_count, length)
        elif self.selected_index <= ceil:
            render_range = (0, self.line_count)

        else:
            render_range = (
                self.selected_index - ceil,
                self.selected_index + floor + 1
            )
        

        for index_val in range(render_range[0], render_range[1]):
            final_text = f"{final_text}^{text_lines[index_val]}"

        final_text = f"{title}^{final_text}"

        self.rpcs3_process.write_string(self.menu_text_address,f"{final_text}\x00")

    def set_default_text(self):
        self.rpcs3_process.write_string(self.menu_text_address,f"{self.default_text}\x00")

    def aob_scan_between_regions_all(self, start_address: int, end_address: int, aob: bytes) -> tuple[int, ...]:
        if start_address >= end_address:
            return ()

        found_addresses = []
        chunk_size = 1024 * 1024
        pattern_length = len(aob)

        if pattern_length == 0:
            return ()

        overlap = pattern_length - 1
        current_address = start_address

        while current_address < end_address:
            bytes_to_read = min(chunk_size, end_address - current_address)

            try:
                memory_chunk = self.rpcs3_process.read_bytes(current_address, bytes_to_read)
            except Exception:
                current_address += chunk_size
                continue

            search_offset = 0

            while True:
                found_at = memory_chunk.find(aob, search_offset)

                if found_at == -1:
                    break

                found_addresses.append(current_address + found_at)
                search_offset = found_at + 1

            current_address += chunk_size - overlap if overlap > 0 else chunk_size

        return tuple(found_addresses)


if __name__ == "__main__":
    test_case = 1

    process = Pymem("rpcs3.exe")

    if test_case == 1:
        import sys
        app = QtWidgets.QApplication(sys.argv)


        thread = ControllerThread(rpcs3_process=process)
        thread.state_changed.connect(lambda b: print(b._to_dict()))
        thread.start()

        app.aboutToQuit.connect(thread.stop)
        sys.exit(app.exec_())

    if test_case == 2:
        s3_controller = skate_3_internal_menu_controller(rpcs3_process=process)
        s3_controller.show(False)


