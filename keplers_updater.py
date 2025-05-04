import tkinter as tk
from tkinter import ttk
import sv_ttk
import os
import sys
import webbrowser as wb
import requests
from datetime import datetime
import math
from myutils import Popup, resource_path, is_keplers

VERSION = '1.0.1'

WXTOIMG_DIR = os.path.join(os.getenv('APPDATA'), 'WXtoImg')
CFG_PATH = os.path.join(WXTOIMG_DIR, 'kepler-updater.cfg')
KEPLER_PATH = os.path.join(WXTOIMG_DIR, 'weather.txt')
ICON_PATH = 'icon.ico'
LICENSES_DIR = 'licenses'

URL_DEFAULT = "http://www.celestrak.org/NORAD/elements/weather.txt"
VERSION_URL = "https://api.github.com/repos/stefan-wr/keplers-updater-for-wxtoimg/releases/latest"
TIMEOUT = 5

time_fmt = "%Y.%m.%d - %H:%M"

# Create WXtoImg directory
if not os.path.exists(WXTOIMG_DIR):
    os.mkdir(WXTOIMG_DIR)


# Class for an about-window
# =========================
class AboutWindow(Popup):
    def __init__(self, master, app):
        """A popup window for an about-dialog, showing links, used software and their licenses."""
        Popup.__init__(self, master, title="About", icon=ICON_PATH)

        # List of projects with links and licenses that are being used
        # [(project name, url, (license name, license txt file)), ...]
        infos = [(f"Keplers Updater for WXtoImg on Github",
                  "https://github.com/stefan-wr/keplers-updater-for-wxtoimg",
                  ('MIT License', os.path.join(LICENSES_DIR, 'license.txt'))),
                 ("WRAASE electronic",
                  "https://www.wraase.de", None),
                 ("WXtoImg Restored",
                  "https://wxtoimgrestored.xyz/", None),
                 ("Python Programming Language",
                  "https://www.python.org/",
                  ('Python License', os.path.join(LICENSES_DIR, 'python.txt'))),
                 ("WinPython",
                  "https://github.com/winpython",
                  ('MIT License', os.path.join(LICENSES_DIR, 'winpython.txt'))),
                 ("Sun Valley ttk theme by rdbende",
                  "https://github.com/rdbende/Sun-Valley-ttk-theme",
                  ('MIT License', os.path.join(LICENSES_DIR, 'theme.txt'))),
                 ("Python Requests",
                  "https://github.com/psf/requests",
                  ('Apache Software License 2.0', os.path.join(LICENSES_DIR, 'requests.txt'))),
                 ("PyInstaller",
                  "https://github.com/pyinstaller/pyinstaller",
                  ('GNU General Public License', os.path.join(LICENSES_DIR, 'requests.txt')))]

        main_frame = ttk.Frame(self.top)

        # Program name & version number
        title_frame = ttk.Frame(main_frame)
        text = f"Keplers Updater for WXtoImg v{VERSION}"

        bold = ("Segoe UI", 10, 'bold')
        title_label = ttk.Label(title_frame, font=bold, justify=tk.CENTER, text=text)
        title_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to check for software update
        text = "Check for update"
        update_btn = ttk.Button(title_frame, text=text, command=app.check_for_update)
        update_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        title_frame.pack(fill=tk.X)

        # Disclaimer
        text = "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND."
        disclaimer_label = ttk.Label(main_frame, justify=tk.CENTER, text=text)
        disclaimer_label.pack(padx=5, pady=5)

        # Separator
        separator = ttk.Separator(main_frame)
        separator.pack(fill=tk.X, padx=5, pady=10)

        # Creating list of info about used software/projects and licenses
        for text, link, license in infos:
            line_frame = ttk.Frame(main_frame)

            # Name of the project/software/website -> clickable if an url was provided
            link_label = ttk.Label(line_frame, justify=tk.LEFT, text=f"▪  {text}")
            if link is not None:
                link_label.bind("<Button-1>", lambda e, url=link: wb.open_new_tab(url))
                link_label['cursor'] = 'hand2'
            link_label.pack(side=tk.LEFT, padx=5, pady=5)

            # Add clickable label with license information -> opens license in editor
            if license is not None:
                license_label = ttk.Label(line_frame, text=f"({license[0]})",
                                          justify=tk.LEFT, cursor='hand2')
                license_label.pack(side=tk.LEFT, padx=5, pady=5)
                open_license = lambda e, txt=license[1]: wb.open(resource_path(txt))
                license_label.bind("<Button-1>", open_license)

            line_frame.pack(anchor=tk.W)
        main_frame.pack(padx=10, pady=10)

        self.finalize()  # Center windows and add icon


# Class for popup dialogs ((error-) messages and update notifications)
# ====================================================================
class PopupDialog(Popup):
    def __init__(self, master, title, msg, err=None, up_url=None):
        """
        A popup window for (error-) messages.
        :param master: Root TK element
        :param title: Window title
        :param msg: Short, informativ message
        :param err: Error-mode: Full error message, showed after additional button press
        :param up_url: Update-mode: Link to download program update from
        """
        Popup.__init__(self, master, title=title, icon=ICON_PATH)
        self.top.minsize(width=370, height=0)
        self.err = err
        self.update_url = up_url

        # Short message
        label = ttk.Label(self.top, text=msg, justify=tk.LEFT, wraplength=340)
        label.pack(side=tk.TOP, anchor=tk.NW, padx=15, pady=15)

        # Buttons frame, close button
        buttons_frame = ttk.Frame(self.top)
        ctn_btn = ttk.Button(buttons_frame, text="Close", command=self.close,
                             style="Accent.TButton")

        # ERROR-MODE: Add button to show the full error message if one was passed on
        if self.err is not None:
            self.show_err_btn = ttk.Button(buttons_frame, text="Show full error message",
                                           command=self.show_full_err)
            self.show_err_btn.pack(side=tk.LEFT, padx=5, pady=5)
            ctn_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # UPDATE-MODE: Add button to open download page of new program update
        elif self.update_url is not None:
            self.upt_btn = ttk.Button(buttons_frame, text="Download new version",
                                      command=lambda url=up_url: wb.open_new(url))
            self.upt_btn.pack(side=tk.LEFT, padx=5, pady=5)
            ctn_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # MESSAGE-MODE: Just a message
        else:
            ctn_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        buttons_frame.pack(side=tk.BOTTOM, anchor=tk.S, padx=10, pady=10)

        self.finalize()  # Center windows and add icon

    def show_full_err(self):
        """Add another text label holding the full error message."""
        self.show_err_btn.destroy()

        full_error_frame = ttk.LabelFrame(self.top, text="Full Error Message")
        full_error_text = tk.Text(full_error_frame, width=45, bd=0,
                                  height=math.ceil(len(str(self.err)) / 45))
        full_error_text.insert(tk.END, f"{self.err}")
        full_error_text.config(state=tk.DISABLED)
        full_error_text.pack(padx=10, pady=5)
        full_error_frame.pack(padx=15, pady=0)


# Main App Class
# ==============
class App:
    def __init__(self, master):
        self.master = master

        # Time of last update
        self.last_update_time = None

        # Define UI variables
        self.url_var = tk.StringVar()
        self.auto_update_var = tk.BooleanVar()
        # self.auto_quit_var = tk.BooleanVar()
        self.progress_var = tk.IntVar()
        self.last_update_var = tk.StringVar()

        # Initialise UI variables with default values
        self.url_var.set(URL_DEFAULT)
        self.auto_update_var.set(False)
        # self.auto_quit_var.set(False)
        self.progress_var.set(0)
        self.last_update_var.set("never")

        # Load configuration
        self.load_cfg()

        # Build UI & setup window geometry
        self.setup_ui()
        self.setup_window()

        # Auto update mode
        if self.auto_update_var.get():
            self.master.after(500, self.update_keplers)

    # Build main UI
    # -------------
    def setup_ui(self):
        # Paddings
        padx = pady = 5

        # Setup UI
        # ========
        self.master_frame = ttk.Frame(self.master)

        # Info Label
        text = "This application updates the Kepler data of your WXtoImg installation by downloading" \
               " the data from  the URL specified below. Setting changes will be saved on every" \
               " successful data update."
        self.info_label = ttk.Label(self.master_frame, justify=tk.LEFT, wraplength=480, text=text)
        self.info_label.pack(anchor=tk.W, padx=padx, pady=pady)

        # Settings Frame
        # <<<<<<<<<<<<<<
        self.settings_frame = ttk.LabelFrame(self.master_frame, text="Settings")

        # URL Entry with reset button
        self.url_frame = ttk.Frame(self.settings_frame)

        self.url_label = ttk.Label(self.url_frame, text="URL:")
        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.url_var, width=50)
        self.url_entry.bind("<Return>", lambda e: self.update_keplers())
        self.url_reset_btn = ttk.Button(self.url_frame, text="Reset",
                                        command=lambda: self.url_var.set(URL_DEFAULT))

        self.url_label.pack(side=tk.LEFT, padx=padx, pady=pady)
        self.url_entry.pack(side=tk.LEFT, padx=padx, pady=pady)
        self.url_reset_btn.pack(side=tk.RIGHT, padx=padx, pady=pady)

        self.url_frame.pack(padx=padx, pady=pady)

        # Auto-Update Checkbox (Data)
        text = "Update Kepler data automatically when this app opens."
        self.auto_update_chbtn = ttk.Checkbutton(self.settings_frame, variable=self.auto_update_var,
                                                 text=text)
        self.auto_update_chbtn.pack(padx=padx, pady=pady, anchor=tk.W)

        self.settings_frame.pack(padx=padx, pady=pady * 2 + 2)
        # >>>>>>>>>>>>>>

        # Update Keplers Button
        self.update_btn = ttk.Button(self.master_frame, style="Accent.TButton",
                                     command=self.update_keplers,
                                     text="Update Kepler Data")
        self.update_btn.pack(padx=padx, pady=pady * 2)

        # Progressbar
        self.progressbar = ttk.Progressbar(self.master_frame, maximum=4, variable=self.progress_var,
                                           mode="determinate")
        self.progressbar.pack(fill=tk.X, padx=padx, pady=pady * 2)

        # Last-Update Frame
        # <<<<<<<<<<<<<<<<<
        self.last_frame = ttk.Frame(self.master_frame)

        # Last update-time
        self.last_txt_label = ttk.Label(self.last_frame, text="Last update:")
        self.last_txt_label.pack(side=tk.LEFT, padx=padx, pady=pady)
        self.last_time_label = ttk.Label(self.last_frame, textvariable=self.last_update_var)
        self.last_time_label.pack(side=tk.LEFT, fill=tk.X, padx=padx, pady=pady)

        # Quit button
        self.quit_btn = ttk.Button(self.last_frame, text="Exit", command=self.master.destroy)
        self.quit_btn.pack(side=tk.RIGHT, padx=padx, pady=pady)

        # About button
        self.about_btn = ttk.Button(self.last_frame, text="About", command=self.show_about)
        self.about_btn.pack(side=tk.RIGHT, padx=padx, pady=pady)

        self.last_frame.pack(fill=tk.X)
        # >>>>>>>>>>>>>>>>>

        # Pack Master Frame
        self.master_frame.pack(padx=padx * 2, pady=pady * 2)

    # Setup window
    # ------------
    def setup_window(self):
        self.master.update_idletasks()

        # Center window on screen
        w, h = self.master.winfo_width(), self.master.winfo_height()
        x = int((self.master.winfo_screenwidth() / 2) - (w / 2))
        y = int((self.master.winfo_screenheight() / 2) - (w / 2))
        self.master.geometry(f"+{x}+{y}")

        self.master.iconbitmap(resource_path(ICON_PATH))  # set icon

    # Create a popup-dialog
    # ---------------------
    def show_popup(self, title, msg, err=None, up_url=None):
        """
        Create and open a popup-dialog.
        :param title: Title of the popup window
        :param msg: Message shown on popup
        :param err: A full error message
        :param up_url: URL for update download
        """
        popup = PopupDialog(self.master, title, msg, err, up_url)
        self.master.wait_window(popup.top)

    # Show the about-window
    # ---------------------
    def show_about(self):
        """Show an about-window"""
        about = AboutWindow(self.master, self)
        self.master.wait_window(about.top)

    # Reset UI to pre-update state
    # ----------------------------
    def reset_ui(self, rst_progress: bool = True):
        """
        Reset UI states.
        :param rst_progress: Reset progress bar too
        """
        self.master.update()
        self.update_btn.config(state=tk.NORMAL)
        if rst_progress:
            self.set_progress(0)

    # Update progress bar
    # -------------------
    def set_progress(self, level: int):
        """
        Set progress bar to a certain level.
        :param level: Level to set progress bar to
        """
        self.progress_var.set(level)
        self.master.update_idletasks()

    # Update Kepler Data
    # ------------------
    def update_keplers(self):
        """Download Kepler data from URL and save it into WXTOIMG directory."""
        self.update_btn.config(state=tk.DISABLED)
        self.set_progress(1)

        # Check HTML status code and the content-type of the response
        # head of the URL before actually downloading the file.
        try:
            head = requests.head(self.url_var.get(), timeout=TIMEOUT, allow_redirects=True)
            if not head.status_code == 200:
                msg = f"Final status code {head.status_code} is not 200"
                self.show_popup(title="Error - Status Code", msg=msg)
                self.reset_ui()
                return
            if not 'text/plain' in head.headers.get('content-type'):
                msg = "Content-type of the requested URL does not match the expected type" \
                      " 'text/plain'. Please use a different URL or reset it to default."
                self.show_popup(title="Error - Content-Type", msg=msg)
                self.reset_ui()
                return

        except requests.exceptions.Timeout as err:
            msg = f"The connection to the requested URL timed out after {TIMEOUT} seconds."
            self.show_popup(title="Timeout Error", msg=msg, err=err)
            self.reset_ui()
            return

        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema,
                requests.exceptions.MissingSchema) as err:
            msg = "Can not connect to the requested URL." \
                  " Please check the URL for typos and / or test it using your browser."
            self.show_popup(title="Connection Error", msg=msg, err=err)
            self.reset_ui()
            return

        except Exception as err:
            msg = "An unexpected error occurred while trying to connect to the specified URL."
            self.show_popup(title="Unexpected Error", msg=msg, err=err)
            self.reset_ui()
            return

        self.set_progress(2)

        # Download Keplers after successful pre-checks
        try:
            response = requests.get(self.url_var.get(), timeout=TIMEOUT, allow_redirects=True)

        except requests.exceptions.Timeout as err:
            msg = f"The connection to the requested URL timed out after {TIMEOUT} seconds."
            self.show_popup(title="Timeout Error", msg=msg, err=err)
            self.reset_ui()
            return

        except requests.exceptions.ConnectionError as err:
            msg = "Can not connect to the requested URL."
            self.show_popup(title="Connection Error", msg=msg, err=err)
            self.reset_ui()
            return

        except Exception as err:
            msg = "An unexpected error occurred while trying" \
                  " to download Kepler data from  the specified URL."
            self.show_popup(title="Unexpected Error", msg=msg, err=err)
            self.reset_ui()
            return

        self.set_progress(3)

        # Check wether the downloaded data is indeed Kepler data
        if not is_keplers(response.text):
            msg = "Either the data is not formatted correctly, or one of" \
                  " the NOAA satellites (15, 18, 19) is missing in the data."
            self.show_popup(title="Data Error", msg=msg)
            self.reset_ui()
            return

        # Save Kepler data in to weather.txt file in WXTOIMG directory
        try:
            with open(KEPLER_PATH, 'wb') as keplers_file:
                keplers_file.write(response.content)

        except (OSError, Exception) as err:
            msg = f"Could not save Kepler data at ({KEPLER_PATH})."
            self.show_popup(title="Error Saving", msg=msg, err=err)
            self.reset_ui()
            return

        self.set_progress(4)

        # Set last-update time
        self.last_update_time = datetime.now()
        self.set_last_update_var()

        # Save settings
        self.save_cfg()

        # Reset UI, but leave progressbar at finished state, indicating successful update
        self.reset_ui(rst_progress=False)

    # Update the 'last-update' label
    # ------------------------------
    def set_last_update_var(self):
        """Convert time of last update into human-friendly string and set it to UI variable."""
        delta = (datetime.now() - self.last_update_time)
        delta_d = delta.days

        if delta_d == 0:
            delta_h = delta.seconds // 3600
            if delta_h == 0:
                delta_m = (delta.seconds // 60) % 60
                if delta_m == 0:
                    self.last_update_var.set("just now")
                else:
                    self.last_update_var.set(f"{delta_m} minute{'' if delta_m == 1 else 's'} ago")
            else:
                self.last_update_var.set(f"{delta_h} hour{'' if delta_h == 1 else 's'} ago")
        else:
            self.last_update_var.set(f"{delta_d} day{'' if delta_d == 1 else 's'} ago")

    # Save configuration to file
    # --------------------------
    def save_cfg(self):
        """Save program settings into a cfg-file in the WXTOIMG directory."""
        try:
            cfg_file = open(CFG_PATH, 'w')
            cfg_file.write(f"URL: {self.url_var.get()}\n")
            cfg_file.write(f"AUTO-MODE: {self.auto_update_var.get()}\n")
            cfg_file.write(f"LAST-UPDATE: {datetime.strftime(self.last_update_time, time_fmt)}\n")
            cfg_file.close()
        except (OSError, Exception):
            return

    # Load configuration from file
    # ----------------------------
    def load_cfg(self):
        """Load program settings from cfg-file"""
        # Check wether cfg file exists
        if os.path.exists(CFG_PATH):
            try:
                cfg_file = open(CFG_PATH, 'r')
            except (OSError, Exception):
                return

            # Read cfg file
            for line in cfg_file:
                option, value = line.split(maxsplit=1)
                value = value.rstrip('\n')

                # Kepler data URL
                if option == 'URL:':
                    self.url_var.set(value)

                # Auto mode enabled?
                elif option == 'AUTO-MODE:':
                    if value == 'True':
                        self.auto_update_var.set(True)
                    else:
                        self.auto_update_var.set(False)

                # Time of last update
                elif option == 'LAST-UPDATE:':
                    try:
                        self.last_update_time = datetime.strptime(value, time_fmt)
                        self.set_last_update_var()
                    except (ValueError, Exception):
                        pass
                    else:
                        self.set_last_update_var()
            cfg_file.close()

    # Check for program update
    # ------------------------
    def check_for_update(self):
        """Check for an updated version of this program"""
        try:
            response = requests.get(VERSION_URL, timeout=TIMEOUT, allow_redirects=True).json()
            latest_version = response["tag_name"][2:]
            latest_url = response["html_url"]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception):
            self.show_popup(title="Error", msg="Checking for software update failed.")
            return

        from packaging import version

        if version.parse(latest_version) > version.parse(VERSION):
            msg = f"A new version (v{latest_version} > v{VERSION})" \
                  f" of 'Keplers Updater for WXtoImg' is available!"
            self.show_popup(title="Update Available", msg=msg, up_url=latest_url)
        else:
            msg = f"No update available. You already have the latest" \
                  f" version (v{VERSION}) of 'Keplers Updater for WXtoImg'."
            self.show_popup(title="No Update Available", msg=msg)


# =================================================================================================
if __name__ == '__main__':
    window = tk.Tk()  # create root window
    window.resizable(False, False)  # disable resizing
    sv_ttk.set_theme("light")  # set theme
    window.title("Keplers Updater for WXtoImg")  # set window title

    app = App(window)  # create UI
    window.mainloop()
# =================================================================================================
