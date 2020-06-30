import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime
from time import strftime
import pickle
import copy
import os
# Following imports may read as an error in your IDE.  What should happen is sys.path.append should add the current
# working directory to sys.path only while the script runs.  Then it can import stuff from the other .py files in this
# directory.
import sys
sys.path.append(os.getcwd())
import Settings
import Dashboard
import Widgets

# the two biggest pieces of this .py file are the Planner object and the CalendarApp object.  The Planner is
# what gets passed around to everything -- it's where we store our data on tasks, widgets, etc.  And it is what
# gets saved when we close the file.  If something is accessing data or saving it or whatever, it needs to have a way
# to talk to this object.

# the CalendarApp is where all the Data stored in our Planner obj gets visualized and turned into a UI, thru
# combining various widgets.

class Planner(object):
    # this is the Planner object where we store data and create ids for using with our different data structures.

    # task ids is a list of keys used to get our tasks for the day from the tasks_dict
    # week_key is used to store user input (if there is any) in our widget_data data structure.
    def __init__(self, task_dict, date_id, mainpath):
        # for loop exists to create spots in our dictionary for everything in task_keys, even if we dont have a task
        # there.  This helps us avoid keyErrors later on when printing todays tasks.
        self.task_dict = task_dict
        self.mainpath = mainpath
        self.date_id = date_id
        self.task_ids = ['daily'] + self.date_id.split('-') + [strftime('%d')]
        self.week_key = datetime.datetime.now().isocalendar()[:2]
        self.widget_list = self.get_widgets()
        self.widget_data = widget_data_maker(self.mainpath, self)
        for key in self.task_ids:
            if key not in self.task_dict.keys():
                self.task_dict[key] = None
        self.todays_tasks = self.get_todays_tasks()
        self.every_other()

    def __str__(self):
        return strftime('%A') + ', ' + strftime('%b') + ' ' + strftime('%-d') + ', ' + strftime('%Y')

    def every_other(self):
        # this handles 'every other' type tasks.  Every time we start the Planner, it checks what 'last' points to in
        # the task_dict.  If it is a different number than today's date, it points 'last' to todays date, then swaps the
        # every_other boolean value for all tasks that occur every other day.
        # It does the same thing for every other week tasks on Sundays.
        today = datetime.datetime.now().day
        if today != self.task_dict['last']:
            self.task_dict['last'] = today
            if self.task_dict['daily']:
                [i.swap_every_other() for i in self.task_dict['daily']]
            if strftime("%a").upper() == 'SUN':
                if self.get_tasks_by_freq(('every other week')):
                    [i.swap_every_other() for i in self.get_tasks_by_freq('every other week')]

    def get_widget_list(self):
        return self.widget_list

    def set_widget_list(self, new_list):
        self.widget_list = new_list

    def get_week_key(self):
        return self.week_key

    def get_widgets(self):
        # load widgets from a binary text file.  If it's blank, load up the default widgets.
        widgets = open(self.mainpath + '/task_data/widgets.txt', 'rb').read()
        if not widgets:
            widgets = [Widgets.WordOfTheDayWidget, Widgets.FlagOfTheDayWidget]
            saved_widgets = pickle.dumps(widgets)
            save_file = open(self.mainpath + '/task_data/widgets.txt', 'wb')
            save_file.write(saved_widgets)
            save_file.close()
        else:
            widgets = pickle.loads(widgets)
        return widgets

    def get_tasks_by_freq(self, freq):
        # returns a list of tasks according to the freq put into the function
        res =[]
        for value in self.task_dict.values():
            if value is not None and type(value) != int:
                try:
                    res.extend([i.get_text() for i in value if i.get_frequency() == freq])
                except TypeError:
                    print(value)
                    raise TypeError

        return res

    def get_task_dict(self):
        # used just for making a copy of the whole task dict when we're exiting the calendar. not called when listing
        # our daily tasks
        return self.task_dict

    def get_todays_tasks(self):
        # this is used to list tasks but only for today.  It looks up the task_ids for today in the task_dict and
        # puts every task.text into a list
        # then it returns the task list.
        task_list = []
        for key in self.task_ids:
            if self.task_dict[key] is not None:
                [self.reset_var(i) for i in self.task_dict[key]]
                task_list.extend([i for i in self.task_dict[key]])
        return task_list

    def reset_var(self, task):
        # checks to see if the 'last' key (the last day we opened the planner) is equal to today.  If not, it sets
        # the tasks var to 0, i.e. unticks the checkbutton
        if self.task_dict['last'] != datetime.datetime.now().day:
            print('var is reset')
            if task.get_var() == 1:
                task.add_completed()
            task.set_var(0)

    def refresh_todays_tasks(self):
        self.todays_tasks = self.get_todays_tasks()


class Task(object):
    def __init__(self, text, task_id, frequency, every_other=None):
        # Task object that gets saved(pickled) in our task dictionary.
        # text is the task info provided by the user, id is derived from the frequency and todays date.  Frequency is
        # chosen by the user via an option menu, every_other is set to True if it falls into an everyother frequency,
        # left as None if it doesnt.
        # added on is the date it was created, var is saved each day so the app remembers what you've completed when
        # redrawing the tasks menu.

        self.text = text
        self.task_id = task_id
        self.frequency = frequency
        self.every_other = every_other
        self.added_on = datetime.datetime.now()
        self.completed = 0
        self.var = 0

    # ===========GETTERS==============
    def get_var(self):
        return self.var

    def get_text(self):
        return self.text

    def get_task_id(self):
        return self.task_id

    def get_frequency(self):
        return self.frequency

    def get_every_other(self):
        return self.every_other

    def get_days_added(self):
        duration = self.added_on - datetime.datetime.now()
        return duration.days

    def get_times_completed(self):
        return self.completed

    # ===========SETTERS==============

    def swap_every_other(self):
        if self.every_other:
            self.every_other = False
        elif self.every_other is False:
            self.every_other = True

    def add_completed(self):
        self.completed += 1

    def set_var(self, x):
        self.var = x


class TaskCheck(ttk.Checkbutton):
    def __init__(self, parent, task):
        ttk.Checkbutton.__init__(self, parent)
        self.var = tk.IntVar()
        self.task = task
        self.var.set(task.get_var())
        self.config(text=task.get_text(), variable=self.var, command=self.change_var)

    def change_var(self):
        self.task.set_var(self.var.get())


class CalendarApp(ttk.Frame):
    # this is the whole widget on the left of the dashboard.  Contains the clock, date, settings, etc.
    def __init__(self, parent, planner_obj, dashboard):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.dashboard = dashboard
        # add the widgets
        self.planner_obj = planner_obj
        self.date_id = planner_obj.date_id
        self.clock = ClockWidget(self)
        self.date = DateWidget(self)
        self.tasks = TasksWidget(self, planner_obj)
        self.add_button = AddTaskWidget(self, planner_obj)
        #self.settings = SettingsWidget(self, dashboard)

        # geometry management for the widgets
        self.clock.grid(column=0, row=0)
        #self.settings.grid(column=1, row=0)
        self.date.grid(column=0, row=1, sticky='w')
        self.tasks.grid(column=0, row=2, sticky='w')
        self.add_button.grid(column=0, row=3, sticky='e')

    def refresh_tasks(self):
        # destroy and redraw tasks, called whenever our tasks_dict is altered by AddNewTask or RemoveTask toplevels
        self.tasks.destroy()
        self.tasks = TasksWidget(self, self.planner_obj)
        self.tasks.grid(column=0, row=2, sticky='w')


class SettingsWidget(ttk.Frame):
    # Creates settings button in the top right of the planner
    def __init__(self, parent, dashboard):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.configure(padding='3 3 3 3')
        self.photo = tk.PhotoImage(file=Dashboard.main_path + '/images/settings.png')
        self.settings_button = ttk.Button(self, image=self.photo,  command=lambda: Settings.settings_window(self.parent,
                                                                                                            self.parent,
                                                                                                            dashboard))
        self.settings_button.grid(column=0, row=0)


class AddTaskWidget(ttk.Frame):
    def __init__(self, parent, cal):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.cal = cal
        self.configure(padding='3 3 3 3')
        # add widget
        self.add_task_button = ttk.Button(self, text='Add a task', command=lambda: add_task_window(self.parent, self.parent))
        # geometry
        self.add_task_button.grid(column=0, row=0, sticky='e')


class TasksWidget(ttk.Frame):
    def __init__(self, parent, cal):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add title widget
        task_widget_title = ttk.Label(self, text='Today\'s Tasks', font=('verdana', 14, 'bold'))
        # geometry
        task_widget_title.grid(column=0, row=0, sticky='n')
        # task maker function that creates checkbox widgets and adds them to geometry manager for us
        tasks_maker(cal, self)


class DateWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widget
        self.date_display = ttk.Label(self, font=('helvetica', 18, 'bold'))
        self.date_display.configure(background='black', foreground='#438763', borderwidth=3, relief='raised')
        # create date object, use as arg in date_maker
        date_obj = datetime.datetime.now()
        self.date_display.configure(text=date_maker(date_obj))
        # geometry
        self.date_display.pack(side='left')


class ClockWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widget
        self.clock_display = ttk.Label(self, font=('application', 25, 'bold'))
        self.clock_display.configure(background='black', foreground='#EB4739', borderwidth=3, relief='raised')
        # geometry
        self.clock_display.pack()
        # time function updates our clock
        self.time()

    def time(self):
        # updates clock every second
        time_string = strftime('%H:%M:%S %p')
        self.clock_display.configure(text=time_string)
        self.clock_display.after(1000, self.time)


# ======= ADD TASK TOPLEVEL STUFF =======
def add_task_window(parent, main_app):
    AddNewTask(parent, main_app)


class AddNewTask(tk.Toplevel):
    def __init__(self, parent, cal_app):
        tk.Toplevel.__init__(self, parent)

        self.cal_app = cal_app
        self.tasks = cal_app.tasks
        self.planner_obj = cal_app.planner_obj
        self.task_id_maker = {'daily': self.planner_obj.task_ids[0], 'every other day': self.planner_obj.task_ids[0],
                          'weekly': self.planner_obj.task_ids[1], 'every other week':self.planner_obj.task_ids[1],
                          'monthly': 'monthly', 'specific date': 'specific date'}

        self.title('Add a task')
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        # adding the widgets
        self.background = ttk.Frame(self)
        self.entry = TaskEntryWidget(self.background)
        self.frequency_menu = FrequencyMenuWidget(self.background)
        self.confirm_button = ConfirmButtonFrame(self.background, self)
        self.tasks_added_list = TasksAddedFrame(self.background)

        # geometry management for widgets
        self.background.pack(fill='both', expand=True)
        self.entry.grid(column=0, row=0, sticky='n')
        self.frequency_menu.grid(column=0, row=1, sticky='n')
        self.confirm_button.grid(column=0, row=3, sticky='e')
        self.tasks_added_list.grid(column=0, row=4, sticky='n')

    def on_closing(self):
        save_box = messagebox.askyesnocancel(title='Save your task?',
                                             message='Do you want to save the task(s) you added?')
        if not save_box:
            self.destroy()
        elif save_box:
            pickler(self.planner_obj)
            self.cal_app.refresh_tasks()
            self.destroy()
        else:
            pass

    def add_new_task(self):
        # big function.  Adds new tasks to our task dict based on entries from entry boxes.  Gets the key in different
        # ways based on the freq_var, or which option we've chosen from a dropdown menu.
        # then, it updates cal.tasks using the key.
        frequency = self.frequency_menu.freq_var.get()
        if frequency == 'weekly' or frequency == 'every other week':
            temp_entry = tk.StringVar()
            temp_entry.set(self.frequency_menu.week_entry.var.get())
            task_id = temp_entry.get().upper()[:3]
        elif frequency == 'monthly':
            while True:
                # monthly tasks get a day on which the task should be repeated as a 2digit number.
                # that becomes the task's task_id/date_id
                temp_entry = tk.StringVar()
                temp_entry.set(self.frequency_menu.month_entry.entry_box.get())
                self.frequency_menu.month_entry.entry_box.delete(0, tk.END)
                if int(temp_entry.get()) and len(temp_entry.get()) == 2:
                    break
            task_id = temp_entry.get()
        elif frequency == 'specific date':
            # messy but essentially full_calendar.selection_get() returns a string of the date like: '2020-02-07'
            # so we get that and then via some yucky indexing we get the date in the format we need for our date_id
            # ie 'DDMMYY'
            temp_entry = tk.StringVar()
            temp_entry.set(self.frequency_menu.spec_entry.full_calendar.selection_get())
            temp_entry.set(''.join(temp_entry.get()[2:].split('-')[::-1]))
            self.frequency_menu.spec_entry.full_calendar.selection_clear()
            task_id = temp_entry.get()
        else:
            task_id = self.task_id_maker[self.frequency_menu.freq_var.get()]
        text = self.entry.entry_box.get()
        self.entry.entry_box.delete(0, tk.END)
        if frequency.startswith('every other'):
            # if the task is an everyother task, set the optional variable to True
            new_task = Task(text, task_id, frequency, True)
        else:
            # else leave it blank so it stays as None
            new_task = Task(text, task_id, frequency)
        if task_id not in self.planner_obj.task_dict.keys() or self.planner_obj.task_dict[task_id] is None:
            self.planner_obj.task_dict[task_id] = [new_task]
        else:
            self.planner_obj.task_dict[task_id].append(new_task)
        self.tasks_added_list.list_added_tasks(new_task)


class TaskEntryWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widget
        self.default_text = tk.StringVar(self, value='What do you want to do?')
        self.entry_box = ttk.Entry(self, textvariable=self.default_text, justify='right')
        # geometry
        self.entry_box.grid(column=0, row=1)


class FrequencyMenuWidget(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        self.frequencies = ['daily', 'weekly', 'monthly', 'specific date', 'every other day', 'every other week']
        self.freq_var = tk.StringVar(parent)
        self.freq_var.set('specific date')
        # add widgets
        self.freq_prompt = ttk.Label(self, text='How often do you want to do it?')
        self.freq_menu = ttk.OptionMenu(self, self.freq_var, self.frequencies[3], *self.frequencies,
                                        command=self.optional_entries)
        self.week_entry = WeeklyEntryFrame(self)
        self.month_entry = MonthlyEntryFrame(self)
        self.spec_entry = SpecificDateFrame(self)
        # geometry management
        self.freq_prompt.grid(column=1, row=0, sticky='n')
        self.freq_menu.grid(column=1, row=1, sticky='n')
        # special geometry management for optional fields

        self.week_entry.grid(column=1, row=2, sticky='n')
        self.week_entry.grid_forget()
        self.month_entry.grid(column=1, row=2, sticky='n')
        self.month_entry.grid_forget()
        self.spec_entry.grid(column=1, row=2, sticky='n')


    def optional_entries(self, value):
        # command for our dropdown menu.  Creates or forgets frames based on what's selected by the user, allowing them
        # to enter a number which represents the day they want a monthly activity to repeat or the exact date they
        # want a one time, specific date entry to take place.
        # in next version, it's probably easier to replace this with a dropdown menu (rather than typing in).
        if value == 'weekly' or value == 'every other week':
            self.month_entry.grid_forget()
            self.spec_entry.grid_forget()
            self.week_entry.grid(column=1, row=2, sticky='n')
        elif value == 'monthly':
            self.week_entry.grid_forget()
            self.spec_entry.grid_forget()
            self.month_entry.grid(column=1, row=2, sticky='n')
        elif value == 'specific date':
            self.month_entry.grid_forget()
            self.week_entry.grid_forget()
            self.spec_entry.grid(column=1, row=2, sticky='n')
        else:
            self.month_entry.grid_forget()
            self.spec_entry.grid_forget()
            self.week_entry.grid_forget()
        return

# The _____EntryFrame widgets get the relevant date information from the user when adding a task.
class WeeklyEntryFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # optionmenu options
        self.days = ['Monday', "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        # add widgets
        self.info = ttk.Label(self, text='When do you want this task to repeat?')
        self.var = tk.StringVar(self)
        self.var.set('Monday')
        self.choices = ttk.OptionMenu(self, self.var, self.var.get(), *self.days)
        # geometry
        self.info.grid(column=0, row=0, sticky='w')
        self.choices.grid(column=0, row=1, sticky='n')

class MonthlyEntryFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widgets
        self.info = ttk.Label(self, text='Enter a day as two digits.')
        self.entry_box = ttk.Entry(self)
        # geometry
        self.info.grid(column=0, row=0, sticky='w')
        self.entry_box.grid(column=0, row=1, sticky='n')


class SpecificDateFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widgets
        self.info = ttk.Label(self, text='Pick a date')
        self.full_calendar = Calendar(self,
                                          font="Arial 14", selectmode='day',
                                          cursor="hand2", year=int(datetime.datetime.now().year),
                                          month=int(datetime.datetime.now().month),
                                          day=int(datetime.datetime.now().day))

        # geometry
        self.info.grid(column=0, row=0, sticky='w')
        self.full_calendar.grid(column=0, row=1, sticky='n')


class ConfirmButtonFrame(ttk.Frame):
    def __init__(self, parent, toplevel):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        # add widget
        self.button = ttk.Button(self, text="Add task", command=toplevel.add_new_task)
        # geometry
        self.button.grid(column=0, row=2, sticky='e')


class TasksAddedFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.configure(padding='3 3 3 3')
        self.row = 1
        # creating labels for an empty tasks_added chart.  blanks are there so that the headers arent on the bottom
        # before we add anything. (that doesn't look very nice.)
        # The first task fills those blanks in, and any extra tasks we add extend the chart/ toplevel window
        self.header_1 = ttk.Label(self, text='Tasks to be added', borderwidth=3, relief="groove", background='#abb4c4')
        self.header_2 = ttk.Label(self, text='How often?', borderwidth=3, relief="groove", background='#abb4c4')
        self.blank_1 = ttk.Label(self)
        self.blank_2 = ttk.Label(self)
        # geometry management
        self.header_1.grid(column=0, row=0, sticky='w')
        self.header_2.grid(column=1, row=0, sticky='e')
        self.blank_1.grid(column=0, row=1, sticky='w')
        self.blank_2.grid(column=1, row=1, sticky='e')

    def list_added_tasks(self, task):
        # lists tasks we're adding with their frequency at the bottom of the add_task toplevel
        # for monthly and specific date tasks, it combines the task frequency and task_id in the 'task frequency'
        # column to be more descriptive
        task_text = ttk.Label(self, text=task.get_text())
        task_text.grid(column=0, row=self.row)
        freq = task.get_frequency()
        if freq == 'specific date' or freq == 'monthly':
            freq += ' (' + task.task_id + ')'
        task_freq = ttk.Label(self, text=freq)
        task_freq.grid(column=1, row=self.row)
        self.row += 1

# **********FUNCTIONS FOR CALENDAR**********

def widget_data_maker(mainpath, planner_obj):
    # loads widget data into the planner_obj in a json-like dict.
    # widget_dict -> widget -> week_key -> array[7]

    # each widget has a dictionary with each week of a year acting as keys.  Each day of the week then stores its
    # data in the corresponding spot in the array (Monday = array[0]... Sunday = [6])
    widget_data = open(mainpath + '/task_data/widget_data.txt', 'rb').read()
    try:
        widget_dict = pickle.loads(widget_data)
    except EOFError:
        widget_dict = {}
        for widget in planner_obj.get_widget_list():
            widget_dict[widget] = {}
    for widget in planner_obj.get_widget_list():
        if planner_obj.get_week_key() not in widget_dict[widget]:
            widget_dict[widget][planner_obj.get_week_key()] = [None] * 7
    return widget_dict



def cal_maker(mainpath):
    # This makes a Calendar object to use when we start the app.  We can modify it to accept different args to load
    # different calendars.
    date_id = make_date_id()
    task_data = open(mainpath + '/task_data/tasks.txt', 'rb').read()
    try:
        tasks = pickle.loads(task_data)
    except EOFError:
        tasks = {'last': datetime.datetime.now().day}
    return Planner(tasks, date_id, mainpath)


def date_maker(date_object):
    # returns a string of todays date like "Monday, April 2, 2020"
    return date_object.strftime('%B' + ' ' + str(date_object.day) + ', ' + str(date_object.year))


def tasks_maker(cal, frame):
    # takes today's tasks from our calendar, then makes a checkbutton for each task.

    cal.refresh_todays_tasks()
    todays_tasks = cal.todays_tasks
    task_row = 1
    for t in todays_tasks:
        temp = TaskCheck(frame, t)
        temp.grid(column=0, row=task_row, sticky='w')
        task_row += 1


def pickler(calendar_object, widget=False):
    # pickles the task dictionary and saves it for later when we close/ end the calendar
    if widget:
        widgets = calendar_object.widget_list
        saved_widgets = pickle.dumps(widgets)
        save_file = open(calendar_object.mainpath + '/task_data/widgets.txt', 'wb')
        save_file.write(saved_widgets)
        save_file.close()
    else:
        tasks = calendar_object.task_dict
        saving_cal = copy.deepcopy(tasks)
        # the weird comprehension thing takes the specific date keys and splits it into a list of ints
        # [e.g. [15, 5, 20] and then thru if statements compares them with todays date.  If the specific date in the key
        # has already past, delete the key.
        today_date = [int(i) for i in list(map(''.join, zip(*[iter(calendar_object.task_ids[2])] * 2)))]
        for key in tasks.keys():
            if len(key) == 6 and key.isdigit():
                key_date = [int(i) for i in list(map(''.join, zip(*[iter(key)] * 2)))]
                if key_date[1] < today_date[1]:
                    saving_cal.pop(key)
                    continue
                elif key_date[1] == today_date[1] and key_date[0] < today_date[0]:
                    saving_cal.pop(key)
                    continue
            if tasks[key] is None:
                saving_cal.pop(key)
        saved_tasks = pickle.dumps(saving_cal)
        save_file = open(calendar_object.mainpath + '/task_data/tasks.txt', 'wb')
        save_file.write(saved_tasks)
        save_file.close()


def make_date_id():
    # MON-270420
    # ============
    # - it goes month and then the date all mashed together as a 6 digit number.
    # - the date id will be used to match to items we store to be added to our calendar.

    day = strftime("%a").upper()
    date = strftime("%d") + strftime("%m") + strftime("%y")
    return '-'.join([day, date])