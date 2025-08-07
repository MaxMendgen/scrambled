#!/usr/bin/env python
"""
Scrambled v0.2
This is a knowledge based game, created as a substitute exam for 2INF2 LK Q1.1 CvO GyO Bremerhaven.
"""
__author__ = "Max Mendgen"
__copyright__ = "Copyright 2024-2025 - https://creativecommons.org/licenses/by/4.0/"
__credits__ = ["Max Mendgen", "D. Goldhahn, T. Eckart & U. Quasthoff: Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages. - In: Proceedings of the 8th International Language Resources and Evaluation (LREC'12), 2012"]
__license__ = "CC BY 4.0"
__version__ = "0.3"
__maintainer__ = "Max Mendgen"


# ===== Imports ===== #

import tkinter as tk
from random import seed as random_seed, randrange as random_randRange, shuffle as random_shuffle
from os import path as os_path
from tkinter import messagebox as tk_msgBox
from ast import literal_eval as ast_literalEval
from math import ceil as math_ceil 
import webbrowser
import time


# ===== Static variables ===== #

# Paths
CURRENT_PATH = os_path.dirname(__file__) + "\\"
DATA_PATH = CURRENT_PATH + "data\\"

# Design
MAIN_FONT = "Segoe UI"
DARK_COLOR = "#222222"
LIGHT_COLOR = "#DDDDDD"
BUTTON_COLOR = "#31A0E0"
SELECT_COLOR = "#38b6ff"
DESELECT_COLOR = "#DDDDDD"
ROW_COLOR = "#C6C6C6"
WIN_COLOR = "#39DB6C"
LOST_COLOR = "#DB3944"

# Info text
PROGRAM_INFO_TEXT = f"""Scrambled v{__version__} - Copyright 2024/2025 {__license__} - Programmiert von Max Mendgen erschaffen als Klausurersatzleistung für 2INF2 LK Q1.1 CvO GyO Bremerhaven.
Wörterquelle: {__credits__[1]} (https://wortschatz.uni-leipzig.de/de/download/German)"""

# Other things
FPS = 60


# ===== Helper Functions ===== #

def center_window(window, width, height):
    """Center a window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (width/2))
    y_cordinate = int((screen_height/2) - (height/2))
    window.geometry("{}x{}+{}+{}".format(width, height, x_cordinate, y_cordinate))

def center_window_on_parent(window, parent, width, height):
    """Center a window on a parent window."""
    parent.update_idletasks()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x_cordinate = parent.winfo_rootx() + int((parent_width/2) - (width/2))
    y_cordinate = parent.winfo_rooty() + int((parent_height/2) - (height/2))
    window.geometry("{}x{}+{}+{}".format(width, height, x_cordinate, y_cordinate))

def binder(func, *args):
    """Workaround to pass arguments to bound functions."""
    return lambda event: func(event, *args)


def get_random_line(file):
    """Selects a random line from a file."""
    #Uses Waterman's Reservoir Algorithm
    line = next(file)
    for num, aLine in enumerate(file, 2):
        if random_randRange(num):
            continue
        line = aLine
    return line.strip().upper()

def is_anagram(word1, word2):
    word1 = sorted(word1.upper())
    word2 = sorted(word2.upper())
    return word1 == word2

def get_anagramms(word, file):
    """Find anagrams of a word."""
    lines = []
    word = word.upper()
    for line in file:
        line = line.strip().upper()
        if line != word and is_anagram(line, word):
            lines.append(line)
    return list(set(lines))

def get_suffled_word(wordSet):
    """Gets a shuffled word that are not in the wordSet."""
    word = list(wordSet[0])
    random_shuffle(word)
    from itertools import combinations
    for charCombi in combinations(list(word), len(wordSet[0])):
        wordCombined = "".join(charCombi)
        if wordCombined not in wordSet:
            return wordCombined
    return ""

def get_random_word_set(wordLength):
    """Generate a random word set."""
    fileName = f"words{wordLength}.txt"
    with open(DATA_PATH + fileName, "r") as file:
        word = get_random_line(file)
    with open(DATA_PATH + fileName, "r") as file:
        anagramms = get_anagramms(word, file)
    return [word] + anagramms

def move_towards_value(current, target, maxDelta, speed=1.0) -> float:
    if abs(target - current) <= maxDelta:
        return target
    return current + sign(target - current) * maxDelta * speed

def is_near_value(current, target, maxDelta) -> bool:
    return  abs(target - current) <= maxDelta

def sign(value) -> float:
    return -1 if value < 0 else (1 if value > 0 else 0)


# ===== Custom Widigts ===== #

# Main Widgets

class SettigsMenu(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config(background=LIGHT_COLOR)
        
        # Title
        self.labelTitle = tk.Label(
            master=self,
            foreground=DARK_COLOR,
            font=(MAIN_FONT, 20),
            text="Einstellungen",
            background=LIGHT_COLOR
        )
        self.labelTitle.pack(side="top", fill="both", padx=10, pady=10)

        # Word length
        self.sliderWordLength = Slider(self, "Wortlänge:", 3, 8, initial_value=5)
        self.sliderWordLength.pack(fill="x", pady=10)

        # self.sliderExtraLetters = Slider(self, "Extra Buchstaben:", 0, 4, initial_value=1)
        # self.sliderExtraLetters.pack(fill="x", pady=10)

        # Turns
        self.sliderMaxTurns = Slider(self, "Maximale Züge:", 4, 10, initial_value=7)
        self.sliderMaxTurns.pack(fill="x", pady=10)

        self.sliderWordLength.scale.config(command=self.bind_onChangedSliderWordLength)

        # Timer
        self.sliderTimer = Slider(self, "Zeit (in Sek.):", 0, 30, initial_value=0)
        self.sliderTimer.pack(fill="x", pady=10)

        self.labelTimerExtraInfo = tk.Label(
            self,
            text="(0 = keinen Timer)",
            font=(MAIN_FONT, 10, "italic"),
            foreground=DARK_COLOR,
            background=LIGHT_COLOR,
            justify="left"
        )
        self.labelTimerExtraInfo.pack(side="left", padx=10, pady=10)

    def get_settings(self):
        return {"WordLength":self.sliderWordLength.get_value(), "MaxTurns":self.sliderMaxTurns.get_value(), "Timer":self.sliderTimer.get_value()}#, "ExtraLetters":self.sliderExtraLetters.get_value()}

    def bind_onChangedSliderWordLength(self, newValue):
        self.sliderMaxTurns.scale.set(int(self.sliderWordLength.get_value() * 1.5))


class HelpPopup(tk.Toplevel):
    def __init__(self, parent, parentWindow, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # Windows configuration
        self.title("Hilfe")
        center_window_on_parent(self, parentWindow, 648, 648) # geometry 
        #self.grab_set()
        self.focus_set()
        self.transient(parent)
        
        # Help Label
        self.labelHelp = tk.Label(
            self,
            text="Hilfe",
            font=(MAIN_FONT, 16, "bold"),
            foreground="white",
            background=SELECT_COLOR
        )
        self.labelHelp.pack(side="top", fill="both", padx=10, pady=10)

        # Info frame
        self.frameInfo = tk.Frame(self, background="white")
        self.frameInfo.pack(side="top", fill="both", padx=10, pady=10)

        # Create texts
        self.labelTexts = []
        for i in range(4):
            self.labelTexts.append(tk.Label(
                self,
                font=(MAIN_FONT, 12),
                foreground=DARK_COLOR,
                wraplength=628
            ))

        # Configure texts
        self.labelTexts[0].config(text="Dein Ziel ist es, einen Wort am Ende zu erschaffen! Dafür kannst du für jeden Spielzug 2 Buchstaben vertauschen. So macht man einen umtausch:")
        self.labelTexts[1].config(text="1. Klicke den ersten Buchstabe.")
        self.labelTexts[2].config(text="2. Wähle den nächsten Buchstaben, und die beiden gewählten Buchstaben werden direkt vertauscht!")
        self.labelTexts[3].config(text="Wenn du kein wort gefunden hast bis zur unteren Grenze, hast du verloren.\nViel Spaß!")

        # Create images
        self.tutorialImages = []
        self.labelImages = []
        for i in range(2):
            self.tutorialImages.append(tk.PhotoImage(file=DATA_PATH + f"tutorial{i+1}.png"))
            self.labelImages.append(tk.Label(self, image=self.tutorialImages[i]))

        # Place texts and images
        self.labelTexts[0].pack(side="top", fill="both", padx=15, pady=5)
        self.labelTexts[1].pack(side="top", fill="both", padx=15, pady=5)
        self.labelImages[0].pack(side="top", padx=15, pady=5)
        self.labelTexts[2].pack(side="top", fill="both", padx=15, pady=5)
        self.labelImages[1].pack(side="top", padx=15, pady=5)
        self.labelTexts[3].pack(side="top", fill="both", padx=15, pady=5)

        # Ok button
        self.buttonOk = tk.Button(
            self,
            text="Verstanden!",
            font=(MAIN_FONT, 12),
            background=BUTTON_COLOR,
            foreground="white",
            command=self.close
        )
        self.buttonOk.pack(side="bottom", fill="both", padx=20, pady=20)

    def close(self):
        self.destroy()

class EndPopup(tk.Toplevel):
    def __init__(self, parent, parentWindow, gameState, turn, wordSet, newGameBinder, backToMenuBinder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # Save variables
        self.gameState = gameState
        self.wordSet = wordSet
        self.turn = turn
        self.newGameBinder = newGameBinder
        self.backToMenuBinder = backToMenuBinder

        # Windows configuration
        self.title("Ende!")
        center_window_on_parent(self, parentWindow, 384, 384) # geometry 
        self.grab_set()
        self.focus_set()
        self.transient(parent)
        
        # Background
        self.config(background="white")

        # End Label
        self.labelEnd = tk.Label(
            self,
            text= "Supper!" if self.gameState == "won" else "Schade!",
            font=(MAIN_FONT, 16, "bold"),
            foreground="white",
            background= WIN_COLOR if self.gameState == "won" else LOST_COLOR
        )
        self.labelEnd.pack(side="top", fill="both", padx=10, pady=10)

        # Text
        self.frameText = tk.Frame(self, background="white")
        self.frameText.pack(side="top", fill="both", padx=10, pady=10)

        self.labelText = tk.Label(
            self,
            font=(MAIN_FONT, 16),
            foreground=DARK_COLOR,
            background="white",
            wraplength=100
        )
        self.labelText.config(wraplength=384)

        if self.gameState == "won":
            self.labelText.config(text=f"Du hast ein {len(self.wordSet[0])}-stelliges Wort in {turn} Vertauschungen gefunden!\n{self.text_of_wordSet(self.wordSet)}")
        else:    
            self.labelText.config(text=f"Leider kein {len(self.wordSet[0])}-stelliges Wort gefunden!\n{self.text_of_wordSet(self.wordSet)}")
        self.labelText.pack(side="top", fill="both", padx=10, pady=10)

        # Buttons
        self.buttonNewGame = tk.Button(
            self,
            text="Neues Spiel",
            font=(MAIN_FONT, 16),
            background=BUTTON_COLOR,
            foreground="white",
            command=self.bind_onClickNewGame
        )
        self.buttonNewGame.pack(side="top", fill="both", padx=10, pady=10)

        self.buttonBackToMenu = tk.Button(
            self,
            text="Zurück zum Menü",
            font=(MAIN_FONT, 12),
            background=BUTTON_COLOR,
            foreground="white",
            command=self.bind_onClickBackToMenu
        )
        self.buttonBackToMenu.pack(side="top", fill="both", padx=20, pady=5)

        # Return to menu if window closed
        # WARNING: Binder must do close, or else you then can't close the whole application
        self.protocol("WM_DELETE_WINDOW", self.bind_onWindowClose)

    def text_of_wordSet(self, wordSet):
        if len(wordSet) == 1:
            return "Das Wort war:\n" + wordSet[0]
        return "Mögliche Wörter waren:" + "\n" + ", ".join(wordSet)

    def bind_onClickNewGame(self):
        self.newGameBinder()
        self.close()

    def bind_onClickBackToMenu(self):
        self.backToMenuBinder()
        self.close()

    def bind_onWindowClose(self):
        self.backToMenuBinder()
        self.close()

    def close(self):
        self.destroy()

# Sub Widgets

class MainTitle(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.photoImage = tk.PhotoImage(file=DATA_PATH + "logo.png")
        self.config(
            text="Scrambeld!",
            foreground=DARK_COLOR,
            font=(MAIN_FONT, 32, "bold"),
            image=self.photoImage,
            height=140
        )

class Slider(tk.Frame):
    """A slider widget with a label and a scale."""
    def __init__(self, parent, labelText, from__, to__, initial_value=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.config(background=LIGHT_COLOR)

        # Label
        self.label = tk.Label(
            self,
            text=labelText, 
            font=(MAIN_FONT, 10), 
            background=LIGHT_COLOR,
            foreground=DARK_COLOR
        )
        self.label.pack(side="left", padx=10)

        # Scale (slider)
        self.scale = tk.Scale(
            self, 
            from_=from__, to=to__, 
            orient=tk.HORIZONTAL,
            background=BUTTON_COLOR, foreground="white",
        )
        self.scale.pack(side="left", fill="x", expand=True, padx=10)

        # Set initial value if provided
        if initial_value is not None:
            self.scale.set(initial_value)

    def get_value(self):
        """Returns the current value of the slider."""
        return self.scale.get()


class Row(tk.Frame):
    def __init__(self, parent, yPos, rowIndex, word, bindTo, hideBoxesOnCreation=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config(background=ROW_COLOR)
        self.place(relx=0.5, y=yPos, anchor="center", width=10+len(word)*60, height=70)

        self.labelBoxes = []
        for i in range(len(word)):
            labelBox = tk.Label(
                master=self,
                text=word[i],
                font=(MAIN_FONT, 16),
                background=DESELECT_COLOR,
                cursor="hand2"
            )
            labelBox.bind("<Button-1>", binder(bindTo, rowIndex, i))
            yPos = 10
            if hideBoxesOnCreation:
                yPos = -60
            labelBox.place(x=10+i*60, y=yPos, width=50, height=50)
            self.labelBoxes.append(labelBox)
        
        self.selectedBoxes = []

    def place_all_boxes(self, *args, **kwargs):
        for box in self.labelBoxes:
            box.place(*args, **kwargs)

class Table(tk.Frame):
    def __init__(self, parent, yPos, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.yPos = yPos
        self.frameRows = []

        self.config(background=ROW_COLOR)

    def add_new_row(self, turn, currentWord, binder_onBoxClick, selectedBoxSwap=[-1, -1], hideBoxesOnCreation=False):
        """Adds a new row to the table."""
        self.turn = turn
        self.currentWord = currentWord
        self.binder_onBoxClick = binder_onBoxClick
        row = Row(self, self.turn*60 + 35, self.turn, self.currentWord, self.binder_onBoxClick, hideBoxesOnCreation)
        self.frameRows.append(row)
        # Selected boxes
        for i in range(2):
            if selectedBoxSwap[i] >= 0:
                row.labelBoxes[selectedBoxSwap[i]].config(background=SELECT_COLOR)

    def clear_rows(self):
        """Clears all rows."""
        for row in self.frameRows:
            row.destroy()
        self.frameRows = []

    def color_in_row(self, rowIndex, color):
        """Color all boxes in a row."""
        for labelBox in self.frameRows[rowIndex].labelBoxes:
            labelBox.config(background=color)

    # def show_animation(self, root, selectedBoxSwap, rowIndex, data={"n":0}):
    #     waitTime = 0
    #     iterrateI = True
    #     print("n=" + str(data["n"]))

    #     if data["n"] < -1:
    #         return

    #     elif data["n"] == 0:
    #         print("doing n=0")
    #         # Get selected boxes and position
    #         data["selectedBoxes"] = []
    #         data["selectedPositions"] = []
    #         for i in range(2):
    #             if selectedBoxSwap[i] >= 0:
    #                 data["selectedBoxes"].append(self.frameRows[self.turn].labelBoxes[selectedBoxSwap[i]])
    #                 data["selectedPositions"].append(int(data["selectedBoxes"][i].place_info().get("x")))
    #         # Swap them before moving
    #         data["selectedBoxes"][0].place(x=data["selectedPositions"][1])
    #         data["selectedBoxes"][1].place(x=data["selectedPositions"][0])
    #         # Set start positions
    #         data["rowPos"] = -40
    #         data["boxPositions"] = []
    #         data["boxPositions"] += data["selectedPositions"]

    #     elif data["n"] == 1:
    #         print("doing n=1")
    #         # Move row down
    #         nextPos = move_towards_value(data["rowPos"], 10, 0.25, 20)
    #         self.frameRows[rowIndex].place_all_boxes(y=nextPos)
    #         data["rowPos"] = nextPos
    #         iterrateI = is_near_value(data["rowPos"], 10, 0.25)
    #         waitTime = 10

    #     elif data["n"] == 2:
    #         print("doing n=2")
    #         # Swap boxes
    #         nextPos1 = move_towards_value(data["boxPositions"][0], data["selectedPositions"][0], 0.25, 20)
    #         nextPos2 = move_towards_value(data["boxPositions"][1], data["selectedPositions"][1], 0.25, 20)
    #         data["selectedBoxes"][0].place(x=nextPos1)
    #         data["boxPositions"][0] = nextPos1
    #         data["selectedBoxes"][1].place(x=nextPos2)
    #         data["boxPositions"][1] = nextPos2
    #         iterrateI = is_near_value(data["boxPositions"][0], data["selectedPositions"][0], 0.25) and is_near_value(data["boxPositions"][1], data["selectedPositions"][1], 0.25)
    #         waitTime = 10
        
    #     elif data["n"] == 3:
    #         return

    #     # Loop
    #     if data["n"] >= 0 and data["n"] < 3:
    #         print("looping")
    #         data["n"] += 1 if iterrateI else 0
    #         if waitTime > 0:
    #             root.after(waitTime, self.show_animation, root, selectedBoxSwap, rowIndex, data)
    #         else:
    #             self.show_animation(root, selectedBoxSwap, rowIndex, data)
                        

    def destroy(self):
        """Destroy this and all descendants widgets."""
        self.clear_rows()
        super().destroy()


# ===== Scenes ===== #

class MainMenu(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = parent

        # Title
        self.labelMainTitle = MainTitle(self)
        self.labelMainTitle.pack(side="top", fill="x", padx=10, pady=10)

        # Main frame for Settings
        self.frameMain = tk.Frame(self)
        self.frameMain.pack(side="top", fill="x", padx=20, pady=0)

        self.frameSettingsMenu = SettigsMenu(self.frameMain)
        self.frameSettingsMenu.pack(side="top", fill="both", padx=10, pady=10)

        # Help button
        self.buttonHelp = tk.Button(
            master=self.frameMain,
            background=BUTTON_COLOR,
            foreground="white",
            font=(MAIN_FONT, 12),
            text="Hilfe zum Spielen",
            command=self.bind_onClickHelp
        )
        self.buttonHelp.pack(side="bottom", fill="both", padx=30, pady=20)
        self.helpPopup = None

        # Load button
        self.buttonLoad = tk.Button(
            master=self.frameMain,
            background=BUTTON_COLOR,
            foreground="white",
            font=(MAIN_FONT, 12),
            text="Lade vorheriges Spiel",
            command=self.load_previous_game
        )
        self.buttonLoad.pack(side="bottom", fill="both", padx=30, pady=10)
        self.update_loadButtonText()

        # Start button
        self.buttonStart = tk.Button(
            master=self.frameMain,
            background=BUTTON_COLOR,
            foreground="white",
            font=(MAIN_FONT, 16, "bold"),
            text="Neues Spiel starten!",
            command=self.start_game
        )
        self.buttonStart.pack(side="bottom", fill="both", padx=20, pady=20)

        # Info text below
        self.infoText = tk.Label(
            self,
            foreground=DARK_COLOR,
            font=(MAIN_FONT, 10, "italic"),
            wraplength=700,
            text=PROGRAM_INFO_TEXT,
            cursor="hand2"
        )
        self.infoText.bind("<Double-Button-1>", binder(self.bind_openLink))
        self.infoText.pack(side="bottom", fill="x", padx=10, pady=10)

    def update_loadButtonText(self, gameState=""):
        """Update the text of the load button."""
        loadText = "Lade vorheriges Spiel"
        if gameState == "playing":
            loadText = "Vorheriges Spiel fortsetzen"
        self.buttonLoad.config(text=loadText)

    def start_game(self):
        """Handle starting the game."""
        self.controller.start_game()

    def load_previous_game(self):
        """Handle loading the previous game."""
        self.controller.load_previous_game()


    def bind_openLink(self, event):
        print("Clicked link!")
        if(tk_msgBox.askokcancel("Quelle", "Link öffnen zur Wörterqulle?")):
            webbrowser.open_new("https://wortschatz.uni-leipzig.de/de/download/German")

    def bind_onClickHelp(self):
        if self.helpPopup is not None:
            self.helpPopup.close()
        self.helpPopup = HelpPopup(self, self.controller)


class Game(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = parent

        # Design settings
        self.yPos = 247

        # Game global variables
        self.currentWord = ""
        self.wordSet = []
        self.turn = 0
        self.maxTurns = 5
        self.selectedBoxSwap = [-1, -1]
        self.gameState = "" # playing, animating, won, lost
        
        self.frameTable = None
        self.currentWordHistory = []
        self.selectedBoxSwapHistory = []
        self.helpPopup = None

        # Title
        self.labelMainTitle = MainTitle(self)
        self.labelMainTitle.pack(side="top", fill="x", padx=10, pady=10)

        # Hidden frame for buttons
        self.frameHeader = tk.Frame(self)
        self.frameHeader.pack(side="top", fill="x", padx=5)
        
        # Back to menu button
        self.buttonBackToMenu = tk.Button(
            self.frameHeader,
            text="Zurück zum Menü",
            font=(MAIN_FONT, 12),
            background=BUTTON_COLOR,
            foreground="white",
            command=self.bind_onClickBackToMenu
        )
        self.buttonBackToMenu.pack(side="left", padx=20, pady=20)

        # Timer
        self.labelTimer = tk.Label(
            self.frameHeader,
            text="",
            font=(MAIN_FONT, 12),
            foreground=DARK_COLOR,
        )
        self.labelTimer.pack(side="left", expand=True, padx=20, pady=20)

        # Help button
        self.buttonHelp = tk.Button(
            self.frameHeader,
            text="Hilfe zum Spielen",
            font=(MAIN_FONT, 12),
            background=BUTTON_COLOR,
            foreground="white",
            command=self.bind_onClickHelp
        )
        self.buttonHelp.pack(side="left", padx=20, pady=20)

    def initialize_game(self, gameSettings, loadSave=False):
        """Set up the game scene."""
        self.gameSettings = gameSettings

        if loadSave: # Load saved game
            # Try loading values
            try:
                self.load_saved_values()
            except Exception as e:
                # Show error message if can't load and create new empty game
                print(f"Error loading saved game: {e}")
                tk_msgBox.showerror("Fehler beim Laden", "Das Spiel konnte nicht geladen werden. Es wird ein neues Spiel gestartet. Fehlermeldung:\n" + str(e))
                self.gameState = "lost"
                self.initialize_game(self.gameSettings)
                return

            # Create table
            self.frameTable = Table(self, self.yPos)  
            self.frameTable.place(relx=0.5, y=self.yPos, anchor="n", width=10 + len(self.currentWord)*60, height=10+60*self.maxTurns)
            for i in range(self.turn):
                self.frameTable.add_new_row(i, self.currentWordHistory[i], self.bind_onBoxClick, self.selectedBoxSwapHistory[i])
            self.frameTable.add_new_row(self.turn, self.currentWord, self.bind_onBoxClick, self.selectedBoxSwap)

        else: # New game
            # Load values
            self.generate_new_values()

            # Create table
            self.frameTable = Table(self, self.yPos)  
            self.frameTable.place(relx=0.5, y=self.yPos, anchor="n", width=10 + len(self.currentWord)*60, height=10+60*self.maxTurns)
            self.frameTable.add_new_row(self.turn, self.currentWord, self.bind_onBoxClick)

        # Set timer
        if self.timerTime > 0:
            self.labelTimer.config(text=f"Zeit: {float(self.timerTime):.2f} Sekunden")
        else:
            self.labelTimer.config(text=f"")

        # Continue
        self.gameState = "playing"
        # Start timer
        self.start_timer(self.controller)
        
    def load_saved_values(self):
        """Load the last save state."""

        # Load variables
        with open(DATA_PATH + "save.txt", "r") as file:
            self.wordSet = ast_literalEval(file.readline().strip())

            self.turn = int(file.readline().strip())
            self.maxTurns = int(file.readline().strip())

            self.selectedBoxSwap = ast_literalEval(file.readline().strip())
            self.selectedBoxSwapHistory = ast_literalEval(file.readline().strip())

            self.currentWord = file.readline().strip()
            self.currentWordHistory = ast_literalEval(file.readline().strip())

            self.timerTime = float(file.readline().strip())

    def generate_new_values(self):
        """Generate the values for the game."""
        # Get word set and suffled word
        self.wordSet = get_random_word_set(self.gameSettings["WordLength"])
        print(self.wordSet)

        suffledWord = ""
        while suffledWord == "":
            suffledWord = get_suffled_word(self.wordSet)
        self.currentWord = suffledWord

        # Turns
        self.turn = 0
        self.maxTurns = self.gameSettings["MaxTurns"]

        # Timer
        self.timerTime = self.gameSettings["Timer"]


    def next_turn(self):
        # Save to history
        self.currentWordHistory.append(self.currentWord)
        self.selectedBoxSwapHistory.append(self.selectedBoxSwap)

        # Apply changes
        chars = list(self.currentWord)
        letter1 = self.currentWord[self.selectedBoxSwap[0]]
        letter2 = self.currentWord[self.selectedBoxSwap[1]]
        chars[self.selectedBoxSwap[0]] = letter2
        chars[self.selectedBoxSwap[1]] = letter1
        self.currentWord = "".join(chars)

        # Display next row
        self.frameTable.add_new_row(self.turn+1, self.currentWord, self.bind_onBoxClick)#, hideBoxesOnCreation=True)
        #self.frameTable.show_animation(self.controller.parent, self.selectedBoxSwap, self.turn+1)

        # Iterate next and reset others
        self.turn += 1
        self.selectedBoxSwap = [-1, -1]

        print(self.currentWord, self.wordSet)

        # Check if correct
        if self.currentWord in self.wordSet:
            # Apply win visuals
            self.frameTable.color_in_row(self.turn, WIN_COLOR)
            # Change state
            self.gameState = "won"
            self.show_end_popup()
            return

        # Check if end
        if self.turn >= self.maxTurns - 1:
            # Apply lost visuals
            self.frameTable.color_in_row(self.turn, LOST_COLOR)
            # Change state
            self.gameState = "lost"
            self.show_end_popup()
            return

    def clear_game(self):
        """Clear the game scene."""

        # Clear table
        self.frameTable.destroy()

        # Reset variables
        self.currentWord = ""
        self.wordSet = []
        self.turn = 0
        self.maxTurns = 5
        self.selectedBoxSwap = [-1, -1]
        self.selectedBoxSwapHistory = []
        self.currentWordHistory = []
        self.gameState = ""

    def save_game(self):
        """Save the current game state."""
        
        # Create new save file if not exists
        if not os_path.exists(DATA_PATH + "save.txt"):
            with open(DATA_PATH + "save.txt", "w") as file:
                file.write("")

        # Save game state
        if self.gameState == "playing":
            with open(DATA_PATH + "save.txt", "w") as file:
                file.write(f"{self.wordSet}\n")
                file.write(f"{self.turn}\n")
                file.write(f"{self.maxTurns}\n")
                file.write(f"{self.selectedBoxSwap}\n")
                file.write(f"{self.selectedBoxSwapHistory}\n")
                file.write(f"{self.currentWord}\n")
                file.write(f"{self.currentWordHistory}\n")
                file.write(f"{self.timerTime}\n")

                # Update load button text in the main menu
                self.controller.scenes["MainMenu"].update_loadButtonText(self.gameState)


    def show_end_popup(self):
        """Show a popup with the end result."""
        popup = EndPopup(self, self.controller, self.gameState, self.turn, self.wordSet, self.bind_onClickNewGame, self.bind_onClickBackToMenu)

    def start_timer(self, root):
        if self.timerTime > 0:
            self.lastTime = time.perf_counter()
            self.run_timer(root)

    def run_timer(self, root):
        if self.timerTime > 0 and self.controller.inScene == "Game" and self.gameState == "playing":
            deltaTime = max(0, time.perf_counter() - self.lastTime)
            self.timerTime -= deltaTime
            self.labelTimer.config(text=f"Zeit: {math_ceil(self.timerTime)} Sekunden")
            self.lastTime = time.perf_counter()
            root.after(1000 // FPS, self.run_timer, root)
        else:
            # End Game
            if self.gameState == "playing":
                self.timerTime = 0
                self.gameState = "lost"
                self.show_end_popup()

    def bind_onBoxClick(self, event, rowIndex, boxIndex):
        print(f"Clicked ({rowIndex}, {boxIndex})")

        # Only apply changes if current turn and row
        if rowIndex != self.turn:
            return
        
        # Only change and check if playing
        if self.gameState != "playing":
            return
        
        # Get Label
        #labelBox = self.frameRows[rowIndex].labelBoxes[boxIndex]
        labelBox = self.frameTable.frameRows[rowIndex].labelBoxes[boxIndex]

        # Check cases
        if self.selectedBoxSwap[0] < 0: # If none, select 1st
            self.selectedBoxSwap = [boxIndex, -1]
            labelBox.config(background=SELECT_COLOR)
        elif boxIndex in self.selectedBoxSwap: # If same selected, deselect
            self.selectedBoxSwap = [-1, -1]
            labelBox.config(background=DESELECT_COLOR)
        elif self.selectedBoxSwap[0] >= 0 and self.selectedBoxSwap[1] < 0: # If only one selected, select 2nd
            self.selectedBoxSwap[1] = boxIndex
            labelBox.config(background=SELECT_COLOR)
            # Goto next turn
            self.next_turn()
        
        print(f"{rowIndex}, {boxIndex} => {self.selectedBoxSwap}")

    def bind_onClickNewGame(self):
        """Handle the new game button."""
        self.clear_game()
        self.initialize_game(self.controller.scenes["MainMenu"].frameSettingsMenu.get_settings())
        pass

    def bind_onClickBackToMenu(self):
        """Handle the back to menu button."""
        self.save_game()
        self.clear_game()
        self.controller.gameState = self.gameState
        self.controller.show_scene("MainMenu")

    def bind_onClickHelp(self):
        if self.helpPopup is not None:
            self.helpPopup.close()
        self.helpPopup = HelpPopup(self, self.controller)


# ===== Main Application ===== #

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.inScene = None

        # Place scenes
        self.scenes = {}
        for SceneClass in (MainMenu, Game):
            scene_name = SceneClass.__name__
            scene = SceneClass(self, self)
            self.scenes[scene_name] = scene
            scene.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Bind on close
        self.parent.protocol("WM_DELETE_WINDOW", self.bind_onWindowClosed)

        # Show main menu
        self.show_scene("MainMenu")

    def show_scene(self, sceneName):
        """Switch to a specific scene."""
        self.scenes[sceneName].tkraise()
        self.inScene = sceneName

    def start_game(self):
        """Start the game and switch scenes."""
        gameScene = self.scenes["Game"]
        self.show_scene("Game")
        gameScene.initialize_game(self.scenes["MainMenu"].frameSettingsMenu.get_settings())

    def load_previous_game(self):
        """Load the previous game and switch scenes."""
        gameScene = self.scenes["Game"]
        self.show_scene("Game")
        gameScene.initialize_game(self.scenes["MainMenu"].frameSettingsMenu.get_settings(), loadSave=True)

    def bind_onWindowClosed(self):
        """Handle the main window being closed."""
        if "Game" in self.scenes and self.scenes["Game"].gameState == "playing":
            self.scenes["Game"].save_game()
        self.parent.destroy() # /!\ THIS IS IMPORTANT TO CLOSE THE WHOLE APPLICATION, OR ELSE YOU CAN'T CLOSE IT AND NEED TO USE TASK MANAGER


# ===== Main Program ===== #

try:
    if __name__ == "__main__":
        # Create Window
        root = tk.Tk()
        root.title(f"Scrambled! v{__version__}")
        center_window(root, 768, 896)

        # Initialisation of functionality
        root.update_idletasks()
        random_seed()

        # Start main application
        app = MainApplication(root)
        app.pack(side="top", fill="both", expand=True)

        # Loop
        root.mainloop()
        
except Exception as e:
    from tkinter import messagebox as tk_msgBox
    tk_msgBox.showerror(f"Scrambled! v{__version__} - An internal error has accured", f"An internal error has accured. Please contact the developer and provide the error message for more help.\n\nError message:\n    {e}")
    raise SystemError(e)
