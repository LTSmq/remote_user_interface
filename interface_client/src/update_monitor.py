from datetime import datetime
from threading import Thread
from time import sleep

from remote_interface import RemoteInterfaceHeader, RemoteInterface
from shell import print_payload

UPDATE_BREAK_TIME = 0.05
CONTROL_LIGHT = True

def now() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")


def receive(information: dict) -> None:
    if CONTROL_LIGHT:
        switch_on = information.get("switch_on")
        if isinstance(switch_on, bool):
            gpio_value = 1 if switch_on else 0
            ri.execute("set_light", to=gpio_value)

    print(f"({now()})")
    print_payload(information)


if __name__ == "__main__":
    ri = RemoteInterface()
    ri.update_receiver = receive

    updating = True
    def idle():
        global updating
        while updating:
            sleep(0.05)

    idler = Thread(target=idle)
    idler.start()

    input("Receiving updates (press enter to quit)\n")
    idler.join()
    updating = False
