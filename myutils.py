import tkinter as tk
import os.path
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Popup:
    def __init__(self, master, title="", icon=None):
        """An empty, non-resizable popup window
        :param master: Parent window
        :param title: Popup windows title
        :param icon: Popup window icon
        """
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title(title)
        self.top.resizable(False, False)
        self.icon = icon

    def finalize(self):
        """Center popup window on its parent window and set the title icon."""
        self.top.update_idletasks()
        w, h = self.top.winfo_width(), self.top.winfo_height()
        x = int(self.master.winfo_x() + (self.master.winfo_width() / 2 - w / 2))
        y = int(self.master.winfo_y() + (self.master.winfo_height() / 2 - h / 2))
        self.top.geometry(f"+{x}+{y}")

        if self.icon is not None:
            self.top.iconbitmap(resource_path(self.icon))

    def close(self):
        self.top.destroy()


def is_keplers(data: str) -> bool:
    """
    Test wether data is correct Kepler data by checking the
    line lengths and searching for NOAA satellites.
    :param data: String to be tested
    """
    # Data is empty
    if data == "":
        return False

    noaa_found = {'NOAA 15': False, 'NOAA 18': False, 'NOAA 19': False}
    data_lines = data.splitlines()
    for i in range(0, len(data_lines), 3):

        # Check wether lines have the correct length
        # Correct line lengths in sets of 3 are: 24, 69, 69
        if not (len(data_lines[i]) == 24):
            return False
        if len(data_lines) > i + 2:
            if len(data_lines[i + 1]) != 69 or len(data_lines[i + 2]) != 69:
                return False
        else:
            return False

        # Look for the NOAA satellites
        if data_lines[i].rstrip() in noaa_found:
            noaa_found[data_lines[i].rstrip()] = True

    # Check if NOAA 15, 18 and 19 were found.
    if not all(noaa_found.values()):
        return False

    return True
