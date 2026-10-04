"""Small helpers shared by the tkinter GUIs."""

import os


def exit_application():
    # Mirrors javax.swing.JFrame.EXIT_ON_CLOSE: closing the window terminates
    # the whole program, including its background GUI threads.
    os._exit(0)


def center_window(root):
    # Mirrors frame.setLocationRelativeTo(null): center the window on screen.
    root.eval("tk::PlaceWindow . center")
