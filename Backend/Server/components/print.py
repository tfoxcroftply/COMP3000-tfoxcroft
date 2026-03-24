# probably needs a rewrite

import os
import threading
from inspect import stack

from components.types import PrintType, _Config

start_print_string = ""
last_calling_thread = None
has_printed = False
config = _Config()

def vprint(input: str | None, force: bool = False, error: bool = False) -> None:
    global last_calling_thread

    if input == None: # redo checks
        input = "None"

    def new_line() -> str:
        global has_printed
        if has_printed == False:
            has_printed = True
            return ""
        return "\n"
    
    def get_caller_module() -> str:
        try:
            frame_full_path = stack()[2].filename
            frame = os.path.splitext(os.path.basename(frame_full_path))[0]
            return frame
        except Exception:
            return "unknown"

    caller_thread = threading.current_thread()

    if caller_thread == "serial" and config.debug_serial == False:
        return None

    if caller_thread.name != last_calling_thread or last_calling_thread == None:
        last_calling_thread = caller_thread.name
        print(new_line() + "\033[34m[" + caller_thread.name + "]\033[37m")

    text_colour = PrintType.GENERAL.value if not error else PrintType.ERROR.value

    caller_section = "\033[32m[" + get_caller_module().lower().ljust(config.print_module_spacing) + f"]:\033[{text_colour}m "
    to_print = ""
    if input.startswith("\n"):
        to_print = new_line() + input[2:]
    else:
        to_print = start_print_string + caller_section + input

    if not to_print.endswith("."):
        to_print += "."

    print(to_print)