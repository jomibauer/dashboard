import tkinter as tk
import tkinter.ttk as ttk
from io import BytesIO
from PIL import ImageTk, Image
from urllib.request import urlopen
import os
import random
import webbrowser
import datetime
import pickle
# Following imports may read as an error in your IDE.  What should happen is sys.path.append should add the current
# working directory to sys.path only while the script runs.  Then it can import stuff from the other .py files in this
# directory.
import sys
sys.path.append(os.getcwd())
import API.APIs as APIs

main_path = os.getcwd()


# =====================================
# ============Widget Pieces============
# =====================================

def save_widget_data(data, widget, planner):

    with open(planner.mainpath + '/task_data/widget_data.txt', 'wb') as saving_file:
        planner.widget_data[type(widget)][planner.get_week_key()][datetime.datetime.now().weekday()] = data
        dumped_data = pickle.dumps(planner.widget_data)
        saving_file.write(dumped_data)

def callback(url):
    # open embedded hyperlinks (at param url) in widgets
    webbrowser.open_new(url)


class MultiChoiceQuiz(ttk.Frame):
    '''
    Makes a multiple choice quiz with a max of 10 randomly ordered answer choices.  User picks an option and checks
    with the 'check' button.  Allows the user to pick an answer and check as much as they want.
    input: parent, correct answer(str), alternate answers(list)
    '''
    def __init__(self, parent, answer, choices):
        if len(choices) > 9:
            raise ValueError("MultiChoiceQuiz can't have more than 10 choices.")
        ttk.Frame.__init__(self, parent)
        self.config(borderwidth=2, relief='sunken', padding='3 3 3 3')
        self.v = tk.IntVar()
        self.feedback = ttk.Label(self, width=7)
        self.button = ttk.Button(self, text='Check', command=self.check)
        self.quiz = self.make_quiz(answer, choices)

        for i, item in enumerate(self.quiz, start=1):
            item.grid(column=0, row=i, sticky='w', pady=3)
        self.button.grid(column=0, row=len(self.quiz)+1)
        self.feedback.grid(column=0, row=0)

    def make_quiz(self, answer, choices):
        choices.append(answer)
        random.shuffle(choices)
        ans_list = []
        for i, ans in enumerate(choices, start=1):
            ans_list.append(ttk.Radiobutton(self, text=ans, variable=self.v, value=i, state="NORMAL"))
            if ans == answer:
                ans_list[i-1].config(value=11)
        return ans_list

    def check(self):
        if self.v.get() == 11:
            self.feedback.config(text='Correct!', foreground='green', font=('verdana', 14, 'bold'))
        else:
            self.feedback.config(text='Incorrect', foreground='red', font=('verdana', 14, 'bold'))


class ShortWritingWidget(ttk.Frame):
    '''
    Creates a text widget where a user can write a sample, then saves the written sample when the 'Finished' button
    is pressed. This widget can be used to prompt a sentence using a vocabulary word or to answer a short question.

    params: parent, host_widget, subject
    parent -- standard behavior for parent param in tkinter
    host_widget -- class of the widget this shortWritingWidget is being used in; used to store the writing data in the
                    correct place in the widget_data dictionary.
    subject -- keyword or prompt for the writing; data is stored in a single key, value pair like:
                {subject: user's writing} each time the finished button is pressed.
    '''
    def __init__(self, parent, host_widget, subject):
        ttk.Frame.__init__(self, parent)
        self.subject = subject
        self.host_widget = host_widget

        self.entry = tk.Text(self, wrap='word', height=5, width=30, state=tk.NORMAL)
        self.button = ttk.Button(self, text='Finished!', command=self.saved)

        self.entry.grid(column=0, row=0)
        self.button.grid(column=0, row=1, sticky='e')

    def saved(self):
        res = self.entry.get("1.0", 'end-1c')
        tbs = {self.subject: res}
        save_widget_data(tbs, self.host_widget, self.host_widget.planner)
        self.entry.delete('1.0', tk.END)


class ImageWithInfo(ttk.Frame):
    def __init__(self, parent, image_url, title=None, info=None):
        ttk.Frame.__init__(self, parent)
        print(image_url)
        self.image_url = image_url
        self.title = title
        self.info = info
        # get picture from image_url
        self.raw_image = self.open_img_url(self.image_url)
        # resize with a max height of 100 pixels
        self.conv_ratio = self.raw_image.width / self.raw_image.height
        self.raw_image.resize((int(100*self.conv_ratio), 100))
        # create widget & geometry
        self.display_pic = ImageTk.PhotoImage(self.raw_image)
        self.image_widget = ttk.Label(self, image=self.display_pic, relief='raised', borderwidth=10)
        self.image_widget.grid(column=0, row=1)
        # only make these if kwargs are passed
        if self.title:
            self.title_widget = ttk.Label(self, text=self.title)
            self.title_widget.grid(column=0, row=0)
        if self.info:
            self.info_widget = ttk.Label(self, text=self.info)
            self.info_widget.grid(column=0, row=2)

    def open_img_url(self, url):

        raw_data = urlopen(url).read()
        print(raw_data)

        return Image.open(BytesIO(raw_data))



# =====================================
# ===============Widgets===============
# =====================================


class FlagOfTheDayWidget(ttk.Frame):
    '''
    Gets a country's flag using APIs.flag_of_the_day, then via multiple choice quiz asks for the country's identity
    '''
    def __init__(self, parent, planner):
        ttk.Frame.__init__(self, parent)
        self.config(borderwidth=5, relief='sunken')
        self.description = "Provides user with a random country's flag each day and has them identify which country" \
                           " it belongs to."
        self.name = 'FlagOfTheDayWidget'
        self.planner = planner
        self.flag_data = APIs.flag_of_the_day()

        self.other_countries = self.flag_data[2]

        self.flag = (Image.open(BytesIO(self.flag_data[1])))
        self.flag.resize((128, 128))
        self.flag_display = ImageTk.PhotoImage(self.flag)

        self.flag_frame = ttk.Frame(self, padding='3 3 3 3')
        self.quiz_frame = ttk.Frame(self)

        self.flag_label = ttk.Label(self.flag_frame, image=self.flag_display).pack()
        self.quiz = MultiChoiceQuiz(self.quiz_frame, self.flag_data[0], self.other_countries).pack()

        self.flag_frame.grid(column=0, row=0)
        self.quiz_frame.grid(column=1, row=0, sticky='n')

    def __str__(self):
        return self.name


class WordOfTheDayWidget(ttk.Frame):
    '''
    Gets a 'word of the day' from Wordnik and creates a widget containing the word, its definition, and its
    pronunciation (when available).  It also adds a box where the user can try to create a sentence with the word.

    Requires a wordnik APIs key!!  Paste in 'dashboard_app/APIs/apisword.py' as the apisKey variable on line 13:

    apisKey = 'yourAPIsKeyHere'

    Get a key here: https://developer.wordnik.com/
    '''
    def __init__(self, parent, planner):
        ttk.Frame.__init__(self, parent)
        self.config(borderwidth=5, relief='sunken')
        self.planner = planner
        self.description = "Provides the user with a new word, pronunciation and definitions and prompts them to " \
                           "write a sentences with the new word."
        self.name = 'WordOfTheDayWidget'
        self.word_data = APIs.word_of_the_day()
        self.word = tk.StringVar()
        self.word.set(self.word_data[0])
        self.definition = tk.StringVar()
        self.definition.set(self.word_data[1])
        self.pron = tk.StringVar()
        self.pron.set(self.word_data[2])
        self.try_it = ShortWritingWidget(self, self, self.word.get())

        self.word_label = ttk.Label(self, text=self.word.get(), justify='center',font=("Courier", 44))
        self.def_label = ttk.Label(self, text=self.definition.get(), justify='center', wraplength=175)
        self.pron_label = ttk.Label(self, text=self.pron.get(), justify='center', font="Courier")

        self.word_label.grid(column=0, row=0, sticky='n')
        self.pron_label.grid(column=0, row=1, sticky='n')
        self.def_label.grid(column=0, row=2, sticky='n')
        self.try_it.grid(column=0, row=3, sticky='n')


class PictureOfTheDayWidget(ttk.Frame):
    def __init__(self, parent, planner_obj):
        ttk.Frame.__init__(self, parent)
        self.image_data = APIs.picture_of_the_day()
        self.planner_obj = planner_obj
        self.pic_widget = ImageWithInfo(self, self.image_data[1], self.image_data[0])

        self.pic_widget.grid(column=0, row=0)

class BlankWidget(ttk.Frame):
    def __init__(self, parent, planner):
        ttk.Frame.__init__(self, parent)
        self.planner = planner
        self.name = 'BlankWidget'
        self.description = "No description"

    def __str__(self):
        return self.name
