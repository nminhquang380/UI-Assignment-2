import tkinter as tk
import keyboard_design as kd
import recognizer
from template import Point, WordTemplates
import tkinter.filedialog as filedialog
from tkinter import messagebox

class Application(tk.Frame):
    def __init__(self, window_width, window_height, master=None):
        super().__init__(master)  # Call tk.Frame.__init__(master)
        self.master = master  # Update the master object after tk.Frame() makes necessary changes to it
        frame_bottom_height = 200
        frame_middle_height = 50
        frame_top_height = window_height - frame_bottom_height - frame_middle_height

        # the top frame is used to show input words in the text
        frame_top = tk.Frame(self.master)
        frame_top.place(x=0, y=0, width=window_width, height=frame_top_height)

        self.text = tk.Text(frame_top, bg='white', borderwidth=2, relief='groove', font=('Arial', 20))
        self.text.place(x=0, y=0, width=window_width, height=frame_top_height)

        # the middle frame is used to list word candidates (four labels)
        frame_middle = tk.Frame(self.master)
        frame_middle.place(x=0, y=frame_top_height, width=window_width, height=frame_middle_height)

        word_candidate_num = 4
        self.label_word_candidates = []  # labels used to show word candidates
        for i in range(word_candidate_num):  # the values 0 to (word_candidate_num - 1)
            label_word = tk.Label(frame_middle, bg='white', borderwidth=2, relief='groove', font=15) #anchor='w',
            label_word.place(relx=i/word_candidate_num, relwidth=1/word_candidate_num, height=frame_middle_height)
            label_word.bind("<ButtonRelease-1>", self.select_word_candidate)
            print(i/word_candidate_num)
            self.label_word_candidates.append(label_word)

        # the bottom frame is used to show the keyboard
        frame_bottom = tk.Frame(self.master)
        frame_bottom.place(x=0, y=(frame_top_height + frame_middle_height), width=window_width,
                           height=frame_bottom_height)

        self.canvas_keyboard = tk.Canvas(frame_bottom, bg='light gray', borderwidth=2, relief='groove')
        self.canvas_keyboard.place(x=0, y=0, width=window_width, height=frame_bottom_height)

        self.keyboard = kd.Keyboard(self.canvas_keyboard)
        self.keyboard.keyboard_layout()

        # generate word templates
        templates = WordTemplates(self.keyboard.get_keys())

        # generate a recognizer
        self.word_recognizer = recognizer.Recognizer(templates.set_templates())
        self.gesture_points = []

        # mouse events on the canvas keyboard
        self.canvas_keyboard.bind("<ButtonPress-1>", self.mouse_left_button_press)
        self.canvas_keyboard.bind("<ButtonRelease-1>", self.mouse_left_button_release)
        self.canvas_keyboard.bind("<B1-Motion>", self.mouse_move_left_button_down)

        # store x, y, segment tag
        self.cursor_move_position_list = []

        # store the tag for each segment of the drawn gesture
        self.line_tag = []

        #self.canvas_keyboard.bind("<ButtonPress-3>", self.mouse_right_button_press)
        self.canvas_keyboard.bind("<Double-Button-1>", self.mouse_left_button_double_press)
        self.entered_words = []
        self.undone_words = []
        self.text = tk.Text(frame_top, bg='white', borderwidth=2, relief='groove', font=('Arial',20), undo=True)
        self.text.place(x=0,y=0, width= window_width, height= frame_top_height)

        #Create a variableto store the original contents of the text widget
        self.orig_text_contents = self.text.get("1.0", "end")
        self.copy_buffer = ''
        self.text_change_stack = [] #Stack to store text changes
        self.text_change_index = -1 #Index for tracking the current change
        self.attachment_label = tk.Label(self.text, text="", font=('Arial', 12))
        self.attachment_label.pack(side="bottom", anchor = "w")

        self.command_mode = False
        self.temp_command_letter = None
        self.command_letter = None
        self.key_press_timer = None


    def trig_command(self, command_letter, mode):
        self.command_mode = mode
        self.command_letter = command_letter
        if self.command_letter == None:
            pass
        else:
            print(f"Command mode with letter {self.command_letter} is triggered")

    def save_to_file(self):
        text_to_save = self.text.get("1.0", "end-1c")

        if text_to_save:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(text_to_save)
                messagebox.showinfo("Success",f"Text saved to {file_path}")
            else:
                messagebox.showinfo("Info", "File not saved")
        else:
            messagebox.showinfo("Warning", "No text found.")

    def attach_file(self):
        attached_file_path = filedialog.askopenfilename()
        if attached_file_path:
            self.attached_file_path = attached_file_path
            self.attached_file_name = attached_file_path.split("/")[-1]
            self.attachment_label.config(text=f"Attached file: {self.attached_file_name}")
            messagebox.showinfo("Attachment", f"File '{self.attached_file_name}' attached.")

    def undo(self):
        if self.text.edit_undo():
            self.orig_text_contents = self.text.get("1.0", "end")

    def text_change(self, event):
        if self.text_change_index < len(self.text_change_stack) - 1:
            self.text_change_stack = self.text_change_stack[:self.text_change_index+1]

        self.text_change_stack.append(self.text.get("1.0","end"))
        self.text_change_index = len(self.text_change_index) -1

    def redo(self):
        try:
            self.text.edit_redo()
        except:
            print("Error: Can not be redone!!")

    # when users select a word candidate from the four labels in the middle frame
    def select_word_candidate(self, event):
        btn = event.widget  # event.widget is the widget that called the event
        selected_word = btn.cget('text').lower()
        current_cursor_position = self.text.index(tk.INSERT)
        if self.command_mode == True:
            if selected_word.lower() == "undo" and self.command_letter == 'U':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Undo Command?")
                if response == "yes":
                    self.undo()
                    print(f"Command mode with {self.command_letter} has been deactivated")
                    self.trig_command(None, False)
                else:
                    self.text.insert(current_cursor_position, "undo")

            elif selected_word.lower() == "redo" and self.command_letter == 'R':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Redo Command?")
                if response == "yes":
                    self.redo()
                    print(f"Command mode with {self.command_letter} has been deactivated")
                    self.trig_command(None, False)
                else:
                    self.text.insert(current_cursor_position, "redo")

            elif selected_word.lower() == "copy" and self.command_letter == 'C':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Copy Command?")
                try:
                    if response == "yes":
                        selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
                        self.copy_buffer = selected_text
                        print(f"Command mode with {self.command_letter} has been deactivated")
                        self.trig_command(None, False)
                    else:
                        self.text.insert(current_cursor_position, "copy")
                except:
                    print("There is no text to copy!")

            elif selected_word.lower() == "paste" and self.command_letter == 'P':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Paste Command?")
                if response == "yes":
                    self.text.insert(current_cursor_position, self.copy_buffer)
                    print(f"Command mode with {self.command_letter} has been deactivated")
                    self.trig_command(None, False)
                else:
                    self.text.insert(current_cursor_position, "paste")

            elif selected_word.lower() == "attach" and self.command_letter == 'A':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Attach Command?")
                if response == "yes":
                    self.attach_file()
                    print(f"Command mode with {self.command_letter} has been deactivated")
                    self.trig_command(None, False)
                else:
                    self.text.insert(current_cursor_position, "attach")

            elif selected_word.lower() == "save" and self.command_letter == 'S':
                response = messagebox.askquestion("Confirmation", "Do you want trigger the Save Command?")
                if response == "yes":
                    self.save_to_file()
                    print(f"Command mode with {self.command_letter} has been deactivated")
                    self.trig_command(None, False)
                else:
                    self.text.insert(current_cursor_position, "save")
            else:
                messagebox.showwarning("Warning", "This is not a valid command!")
                print(f"Command mode with {self.command_letter} has been deactivated")
                # Turn off the command mode
                self.command_mode = False
                self.command_letter = None
                self.temp_command_letter = None

        else:
            if self.undone_words:
                self.undone_words.clear()
            self.entered_words.append(selected_word)
            self.text.edit_separator()
            self.text.insert(current_cursor_position, selected_word + " ")

        for i in range(len(self.label_word_candidates)): # clear the content of all word labels
            self.label_word_candidates[i].config(text='')

    #Command Button
    def mouse_left_button_double_press(self, event):
        self.temp_command_letter = self.keyboard.get_key_pressed()
        temp_command_letter = self.temp_command_letter
        if not self.command_mode:
            self.key_press_timer = self.master.after(1000, self.trig_command, temp_command_letter, True)
        self.keyboard.key_press(460,120)
        self.gesture_points.clear()
    # press mouse left button
    def mouse_left_button_press(self, event):
        self.cursor_move_position_list.append([event.x, event.y, 0])  # store x, y, segment tag
        self.keyboard.key_press(event.x, event.y)
        self.gesture_points.clear()
        # self.gesture_points.append(Point(event.x, event.y))

    """def mouse_right_button_press(self,event):
        print(f"Command mode with {self.command_letter} has been deactivated")
        self.trig_command(None,False)"""

    # release mouse left button
    def mouse_left_button_release(self, event):
        previous_x = self.cursor_move_position_list[-1][0]
        previous_y = self.cursor_move_position_list[-1][1]
        line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)
        self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.key_release(event.x, event.y)
        result = self.word_recognizer.recognize(self.gesture_points)
        if len(result) > 0:
            for i in range(len(result)):
                if i < len(self.label_word_candidates):
                    self.label_word_candidates[i].config(text=result[i][1])
                else:
                    break
        else:
            key = self.keyboard.get_key_pressed()
            if key == '<--':
                if self.text.tag_ranges(tk.SEL):
                    self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                else:
                    current_cursor_position = self.text.index(tk.INSERT)
                    current_cursor_position_parts = current_cursor_position.split(".")
                    line, char_index = int(current_cursor_position_parts[0]), int(current_cursor_position_parts[1])
                    if char_index > 0:
                        char_index -= 1  # Decrement the character index to remove the character before the cursor
                        new_cursor_position = f"{line}.{char_index}"
                        self.text.edit_separator()
                        self.text.delete(new_cursor_position)  # Remove the character before the cursor
            elif key == 'Space':
                current_cursor_position = self.text.index(tk.INSERT)  # Get the current cursor position
                self.text.edit_separator()
                self.text.insert(current_cursor_position, ' ')  # Add a space at the current cursor position
            else:
                current_cursor_position = self.text.index(tk.INSERT)
                self.text.insert(current_cursor_position, key.lower())

        if len(self.cursor_move_position_list) > 1:
            for x in self.cursor_move_position_list[1:]:
                self.canvas_keyboard.delete(x[2])

    # users drag the mouse cursor on the keyboard while pressing the left button: drawing gestures on the keyboard
    def mouse_move_left_button_down(self, event):
        previous_x = self.cursor_move_position_list[-1][0]
        previous_y = self.cursor_move_position_list[-1][1]

        if not self.command_mode and (previous_x != event.x or previous_y != event.y):
            if self.key_press_timer:
                self.master.after_cancel(self.key_press_timer)
                self.temp_command_letter = None

        line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)  # draw a line
        self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.mouse_move_left_button_down(event.x, event.y)
        self.gesture_points.append(Point(event.x, event.y))  # store all cursor movement points


if __name__ == '__main__':
    master = tk.Tk()
    window_width = 500
    window_height = 600
    master.geometry(str(window_width) + 'x' + str(window_height))  # master.geometry('500x600')
    master.resizable(0, 0)  # can not change the size of the window
    app = Application(window_width, window_height, master=master)
    app.mainloop()  # mainloop() tells Python to run the Tkinter event loop. This method listens for events, such as button clicks or keypresses, and blocks any code that comes after it from running until the window it's called on is closed.
