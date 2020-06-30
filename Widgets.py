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
import PIL
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

def open_img_from_url(url):
    raw_data = urlopen(url).read()
    return Image.open(BytesIO(raw_data))

def open_img_from_bytes(bytes):
    return Image.open(BytesIO(bytes))

def resize_img(image, max_height=256):
    conv_ratio = image.width/ image.height
    return image.resize((int(max_height * conv_ratio), max_height), Image.ANTIALIAS)

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
    def __init__(self, parent, image, title=None, info=None, artist=None, image_url=None):
        ttk.Frame.__init__(self, parent)
        self.image = image
        self.image_url = image_url
        self.title = title
        self.info = info
        self.artist = artist
        # get picture
        if type(self.image) is str:
            self.raw_image = open_img_from_url(self.image)
        else:
            self.raw_image = open_img_from_bytes(self.image)
        # resize with a max height of 256 pixels
        self.raw_image = resize_img(self.raw_image, 256)
        # create widget & geometry
        self.display_pic = ImageTk.PhotoImage(self.raw_image)
        self.image_widget = ttk.Label(self, image=self.display_pic, relief='raised', borderwidth=10)
        self.image_widget.grid(column=0, row=1, columnspan=2)
        # only make these if kwargs are passed
        # hyperlink widget to link to image in browser
        if self.image_url:
            self.hyperlink = ttk.Label(self, text='View in browser', foreground='blue', cursor='hand2')
            self.hyperlink.bind('<Button-1>', lambda e: callback(self.image_url))
            self.hyperlink.grid(column=0, row=2, sticky='w')
        if self.title:
            self.title_widget = ttk.Label(self, text=self.title, wraplength=200, justify=tk.LEFT)
            self.title_widget.grid(column=0, row=0)
        if self.artist:
            self.artist_widget = ttk.Label(self, text=self.artist)
            self.artist_widget.grid(column=1, row=0)
        if self.info:
            self.info_widget = ttk.Label(self, text=self.info)
            self.info_widget.grid(column=0, row=1)

# =====================================
# ===============Widgets===============
# =====================================


class ArtOfTheDayWidget(ttk.Frame):
    '''art of the day widget, gets art and info on art from Met database
        api requests happen in calendar_proj/apiart.py'''
    def __init__(self, parent, planner_obj):
        ttk.Frame.__init__(self, parent)
        self.config(borderwidth=5, relief='sunken')
        self.planner_obj = planner_obj
        self.art_data = APIs.art_of_the_day()
        self.image = self.art_data[0]
        self.image_url = self.art_data[3]
        self.title = self.art_data[4]
        self.artist = self.art_data[1]
        self.info = self.art_data[2]
        self.art_widget = ImageWithInfo(self, self.image, self.title, self.info, self.artist, self.image_url)
        self.art_widget.pack()


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
        try:
            self.pic_widget = ImageWithInfo(self, self.image_data[1], title=self.image_data[0],
                                            image_url=self.image_data[1])
        except PIL.UnidentifiedImageError:
            self.pic_widget = ttk.Label(self, text='failed')

        self.pic_widget.grid(column=0, row=0)


class BlankWidget(ttk.Frame):
    def __init__(self, parent, planner):
        ttk.Frame.__init__(self, parent)
        self.planner = planner
        self.name = 'BlankWidget'
        self.description = "No description"

    def __str__(self):
        return self.name
