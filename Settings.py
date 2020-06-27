import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
# Following imports may read as an error in your IDE.  What should happen is sys.path.append should add the current
# working directory to sys.path only while the script runs.  Then it can import stuff from the other .py files in this
# directory.
import os
import sys
sys.path.append(os.getcwd())
import Planner
import Widgets

# Settings Toplevel


def make_descr():
    descr =  {"Flag of the Day": "Provides user with a random country's flag each day and has them identify which "
                                 "country it belongs to.",
              "Word of the Day": "Provides the user with a new word, pronunciation and definitions and prompts them to "
                                 "write a sentences with the new word.",
              "Picture of the Day": "Provides user with a pleasant picture to look at every day."
              }

    return descr


def make_titles():
    titles = {Widgets.FlagOfTheDayWidget: "Flag of the Day",
              Widgets.WordOfTheDayWidget: "Word of the Day",
              Widgets.PictureOfTheDayWidget: "Picture of the Day"
              }
    return titles


def make_classes():
    classes = {"Flag of the Day": Widgets.FlagOfTheDayWidget,
               "Word of the Day": Widgets.WordOfTheDayWidget,
               "Picture of the Day": Widgets.PictureOfTheDayWidget
               }
    return classes


def settings_window(parent, main_app, dashboard):
    SettingsTopLevel(parent, main_app, dashboard)


class SettingsTopLevel(tk.Toplevel):
    def __init__(self, parent, main_app, dashboard):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.main_app = main_app
        self.remove_button = ttk.Button(self, text='Remove a task',
                                        command=lambda: remove_window(self.parent,
                                                                      self.main_app,
                                                                      self.main_app.cal.task_dict))

        self.widget_menu_button = ttk.Button(self, text='Widget Menu', command=lambda: widget_menu(self.parent,
                                                                                                   self.main_app.cal,
                                                                                                   dashboard))
        self.remove_button.grid(column=0, row=0)
        self.widget_menu_button.grid(column=0, row=1)

# RemoveTasks Toplevel, Class
def remove_window(parent, main_app, task_dict):
    RemoveTasksTopLevel(parent, main_app, task_dict)

def widget_menu(parent, planner_obj, dashboard):
    WidgetMenu(parent, planner_obj, dashboard)


class RemoveTasksTopLevel(tk.Toplevel):
    def __init__(self, parent, main_app, task_dict):
        '''
        list of task frequencies is made into a option menu where users can view tasks by frequency.  They can select
        tasks using a checkbox and delete them by pressing the button.  They can save changes made before exiting
        this Toplevel window
        '''
        tk.Toplevel.__init__(self, parent)
        self.main_app = main_app
        self.cal = main_app.cal
        self.temp_dict = dict(task_dict)
        self.frequencies = ['daily', 'weekly', 'monthly', 'specific date', 'every other day', 'every other week']

        self.background = ttk.Frame(self)
        self.blank = ttk.Frame(self.background)
        self.remove_widgets = self.make_remove_widgets()
        self.checkbuttons = self.make_checkbuttons()
        self.tbr_frame = TBRFrame(self.background)
        self.remove_tasks_button = ttk.Button(self.background, text='Remove selected tasks',
                                              command=lambda: self.remove_task(self.temp_dict))
        self.freq_var = tk.StringVar(parent)
        self.freq_var.set('pick a frequency')
        self.freq_menu = ttk.OptionMenu(self.background, self.freq_var, self.freq_var.get(), *self.frequencies,
                                        command=self.optional_entries)
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.background.pack(fill='both', expand=True)
        self.freq_menu.grid(column=0, row=0)
        self.blank.grid(column=0, row=1)
        self.remove_tasks_button.grid(column=0, row=2)
        self.tbr_frame.grid(column=0, row=3)

    def make_remove_widgets(self):
        res = {}
        for freq in self.frequencies:
            res[freq] = GenericRemoveWidget(self.background, self.temp_dict, freq)
            res[freq].grid(column=0, row=1)
            res[freq].grid_forget()
        return res

    def make_checkbuttons(self):
        res = {}
        for freq in self.frequencies:
            task_list = self.cal.get_tasks_by_freq(freq)
            res[freq] = [ttk.Checkbutton(self.remove_widgets[freq].check_button_frame, text=task, onvalue=True,
                                         offvalue=False, variable=tk.BooleanVar()) for task in task_list]
        return res

    def optional_entries(self, freq):
        # gets value from our frequency option menu.  Forgets every other widget that isn't value, then creates the
        # widget of the value we selected in the geometry manager.
        [i.grid_forget() for i in self.remove_widgets.values() if i is not self.remove_widgets[freq]]
        [ch.grid(column=0, row=n, sticky='w') for n, ch in enumerate(self.checkbuttons[freq])]
        self.remove_widgets[freq].grid(column=0, row=1, sticky='n')

    def remove_task(self, tasks_dict):
        # remove tasks function.
        # modifies our task dict based on the checkbuttons in removetasks toplevel.  If the checkbutton is selected
        # when the function is called, the associated task will be removed from the task_dict.
        tbr = []
        for checklist in self.checkbuttons.values():
            [tbr.append(check['text']) for check in checklist if check.state() == ('selected',)]
            [self.tbr_frame.list_tbr(check['text']) for check in checklist if check.state() == ('selected',)]
        for key, value in tasks_dict.items():
            # type(value) is there so we dont get tripped up here with last: ## in our task dictionary
            if value == [] or value is None or type(value) == int:
                continue
            temp_vals = [v for v in value if v.get_text() not in tbr]
            tasks_dict[key] = temp_vals
        self.temp_dict = tasks_dict


    def on_closing(self):
        save_box = messagebox.askyesnocancel(title='Save changes?',
                                             message='Do you want to save the changes you made?')
        if not save_box:
            self.destroy()
        elif save_box:
            self.cal.update_task_dict(self.temp_dict)
            Planner.pickler(self.cal)
            self.main_app.refresh_tasks()
            self.destroy()
        else:
            pass


class WidgetMenu(tk.Toplevel):
    # Toplevel for the WidgetMenu section of Settings.
    # notifiers are used in Labels to give user feedback to make sure they've made all the selections needed to swap a
    # widget
    def __init__(self, parent, planner_obj, dashboard):
        tk.Toplevel.__init__(self, parent)
        self.dashboard = dashboard
        self.planner_obj = planner_obj
        self.background = ttk.Frame(self)
        self.notifier_1 = tk.StringVar()
        self.notifier_2 = tk.StringVar()
        self.notifier_1.set(' ')
        self.notifier_2.set(' ')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.descr_list = make_descr()
        self.title_list = make_titles()
        self.class_list = make_classes()

        # MyWidgets and WidgetMasterList draw the User's currently selected widgets and the master list of all
        # available widgets, respectively.
        self.my_widgets = MyWidgets(self.background, self, planner_obj.get_widget_list())
        self.widget_master = WidgetMasterList(self, planner_obj)
        # Widget info and title are where we print the description and name of the widget from the Masterlist that's
        # currently selected.
        self.widget_info_frame = ttk.Frame(self.background, padding='3 3 3 3')
        self.widget_title = ttk.Label(self.widget_info_frame, text='Nothing\'s selected.')
        self.widget_info = ttk.Label(self.widget_info_frame,
                                     text='n/a', wraplength=240)
        self.swap_button = ttk.Button(self.widget_info_frame, text='Swap Widgets', command=self.swap_widgets)
        self.select_old_notifier = ttk.Label(self.widget_info_frame, textvariable=self.notifier_1,
                                             foreground='red')
        self.select_new_notifier = ttk.Label(self.widget_info_frame, textvariable=self.notifier_2,
                                             foreground='red')

        # geometry management
        self.background.pack(fill="both", expand=True)
        self.my_widgets.grid(column=0, row=0)
        self.widget_master.grid(column=0, row=1)
        self.widget_info_frame.grid(column=1, row=0, rowspan=2, sticky='n')

        # Geometry inside widget info frame
        self.widget_title.grid(column=0, row=0, sticky='n')
        self.widget_info.grid(column=0, row=1, sticky='n')
        self.select_old_notifier.grid(column=0, row=3, sticky='s')
        self.select_new_notifier.grid(column=0, row=4, sticky='s')
        self.swap_button.grid(column=0, row=6, sticky='s')

    def swap_widgets(self):
        # modifies the planner_obj widget list based on the choices made by the User.  The newly selected widgets are
        # redrawn when the WidgetMenu window is closed.
        if not self.my_widgets.widget_var.get():
            self.notifier_1.set('Select one of your widgets to replace!')
            self.notifier_2.set(' ')
        elif not self.widget_master.avail_widgets.curselection():
            self.notifier_1.set(' ')
            self.notifier_2.set('Select a new widget!')
        else:
            self.notifier_1.set(' ')
            self.notifier_2.set(' ')
            old = self.class_list[self.my_widgets.widget_var.get()]
            new = self.class_list[self.widget_master.avail_widgets.get(self.widget_master.avail_widgets.curselection())]
            widget_pool = self.planner_obj.get_widget_list()
            widget_pool.append(new)
            new_list = [i for i in widget_pool if i is not old]
            self.planner_obj.set_widget_list(new_list)
            self.my_widgets = MyWidgets(self.background, self, self.planner_obj.get_widget_list())

    def on_closing(self):
        Planner.pickler(self.planner_obj, widget=True)
        self.dashboard.refresh_widgets()
        self.destroy()


class MyWidgets(ttk.Frame):
    # makes a radiobutton for each widget in the planner obj's widget list.
    def __init__(self, parent, toplevel, my_widgets):
        ttk.Frame.__init__(self, parent)
        self.toplevel = toplevel
        self.heading = ttk.Label(self, text='My Widgets', font={'verdana', 12, 'bold'})
        self.my_widget_frame = ttk.Frame(self)
        self.widget_var = tk.StringVar()

        self.heading.grid(column=0, row=0)
        self.my_widget_frame.grid(column=0, row=1)

        for e, wi in enumerate(my_widgets):
            temp = ttk.Radiobutton(self.my_widget_frame, text=self.toplevel.title_list[wi], variable=self.widget_var,
                                   value=self.toplevel.title_list[wi])
            temp.grid(column=0, row=e, sticky='w')


class WidgetMasterList(ttk.Frame):
    # adds widgets that aren't already in the planner_obj widget list to a listbox.  Available widgets need to be added
    # to the dictionaries at the top of Settings.py by the developer.
    def __init__(self, parent, planner_obj):
        ttk.Frame.__init__(self, parent.background)
        self.parent = parent
        self.heading = ttk.Label(self, text='Available Widgets', font={'verdana', 12, 'bold'})
        self.avail_widgets = tk.Listbox(self, selectmode=tk.BROWSE)
        self.avail_widgets.bind('<<ListboxSelect>>', self.update_widget_info)
        for wi in parent.title_list:
            if wi not in planner_obj.get_widget_list():
                self.avail_widgets.insert(tk.END, self.parent.title_list[wi])

        self.heading.grid(column=0, row=0)
        self.avail_widgets.grid(column=0, row=1)

    def update_widget_info(self, event=None):
        self.parent.widget_title['text'] = self.avail_widgets.get(self.avail_widgets.curselection())
        self.parent.widget_info['text'] = self.parent.descr_list \
        [self.avail_widgets.get(self.avail_widgets.curselection())]


class GenericRemoveWidget(ttk.Frame):
    # used by the RemoveTasksToplevel.  It pairs a frequency (daily, weekly, monthly, etc) with all the tasks that the
    # user has that occur at that frequency.
    def __init__(self, parent, tasks_dict, frequency):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        self.tasks_dict = tasks_dict
        self.frequency = frequency
        # add widgets
        self.info = ttk.Label(self, text='{0} tasks'.format(self.frequency), borderwidth=3, relief="groove",
                              background='#abb4c4')
        self.check_button_frame = ttk.Frame(self)

        # geometry
        self.info.grid(column=0, row=0, sticky='w')
        self.check_button_frame.grid(column=1, row=0, sticky='n')


class TBRFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        self.row = 1
        # creating labels for an empty tasks_added chart.  blanks are there so that the headers arent on the bottom
        # before we add anything. (that doesn't look very nice.)
        # The first task fills those blanks in, and any extra tasks we add extend the chart/ toplevel window
        self.header_1 = ttk.Label(self, text='Tasks to be removed', borderwidth=3, relief="groove",
                                  background='#abb4c4')
        self.blank_1 = ttk.Label(self)
        # geometry management
        self.header_1.grid(column=0, row=0, sticky='w')
        self.blank_1.grid(column=0, row=1, sticky='w')

    def list_tbr(self, task):
        # lists tasks we're adding with their frquency at the bottom of the add_task toplevel
        # for monthly and specific date tasks, it combines the task frequency and task_id in the 'task frequency'
        # column to be more descriptive

        task_text = ttk.Label(self, text=task)
        task_text.grid(column=0, row=self.row)
        self.row += 1