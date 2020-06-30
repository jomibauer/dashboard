import os
import tkinter as tk
import tkinter.ttk as ttk
# Following imports may read as an error in your IDE.  What should happen is sys.path.append should add the current
# working directory to sys.path only while the script runs.  Then it can import stuff from the other .py files in this
# directory.
import sys
sys.path.append(os.getcwd())
import Widgets
import Planner
import Settings

main_path = os.getcwd()


class PlannerFrame(ttk.Frame):
    # separate frame to contain our Planner
    def __init__(self, parent, planner_obj):
        ttk.Frame.__init__(self, parent)
        self.cal_app = startup(self, planner_obj, parent)


class Dashboard(ttk.Frame):
    # Frame to contain the PlannerFrame and two widgets
    def __init__(self, parent, planner_obj, slot1=Widgets.BlankWidget, slot2=Widgets.BlankWidget):
        ttk.Frame.__init__(self, parent)
        self.calendar_slot = PlannerFrame(self, planner_obj)
        self.cal_app = self.calendar_slot.cal_app
        self.planner_obj = planner_obj

        self.slot1 = slot1(self, planner_obj)
        self.slot2 = slot2(self, planner_obj)

        self.calendar_slot.grid(column=0, row=0, sticky='n')
        self.slot1.grid(column=1, row=0, sticky='e')
        self.slot2.grid(column=1, row=1, sticky='w e')

    def refresh_widgets(self):
        # refreshes the widgets in the dashboard when we choose a new one from the Settings->Widget Menu
        # destroy the old widgets
        self.slot1.destroy()
        self.slot2.destroy()
        # redraw the widgets by looking at our planner_obj's widget list.  If the widget list changed, the program will
        # know to draw the new widget here.
        self.slot1 = self.planner_obj.widget_list[0](self, self.planner_obj)
        self.slot2 = self.planner_obj.widget_list[1](self, self.planner_obj)

        self.slot1.grid(column=1, row=0, sticky='e')
        self.slot2.grid(column=1, row=1, sticky='w e')


def on_closing():
    # save the planner and related task & widget data when closing the window
    Planner.pickler(todays_planner_obj)
    root.destroy()


def startup(tk_root, planner_obj, dashboard):
    calendar_app = Planner.CalendarApp(tk_root, planner_obj, dashboard)
    calendar_app.pack(side="top", fill="both", expand=True)
    return calendar_app


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Calendar')

    todays_planner_obj = Planner.cal_maker(main_path)
    style = ttk.Style()
    style.theme_use('clam')
    dash = Dashboard(root, todays_planner_obj, todays_planner_obj.widget_list[0],
                     todays_planner_obj.widget_list[1])
    dash.pack(fill='both', expand=True)
    menubar = Settings.MenuBar(root, todays_planner_obj, dash)
    root.config(menu=menubar)
    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()
