import threading

Verbose = True

StartPrintString = ""
LastCallingThread = None
Printed = False

def vPrint(Input: str, Force: bool = False) -> None:
    global LastCallingThread

    if Input == None:
        Input = ""

    def NewLine() -> str:
        global Printed
        if not Printed:
            Printed = True
        else:
            return "\n"
        return ""

    CallerThread = threading.current_thread()

    if CallerThread.name != LastCallingThread or LastCallingThread == None:
        LastCallingThread = CallerThread.name
        print(NewLine() + "\033[1;34m ## " + CallerThread.name + " ## \033[1;37m")

    if Verbose or Force:
        if Input.startswith("\n"):
            print(NewLine() + Input[2:])
        else:
            print(StartPrintString + Input)