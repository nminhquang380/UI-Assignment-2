import tkinter as tk
import keyboard_design as kd
import Characters_design as cd
import recognizer
from template import Point, WordTemplates
import tkinter.filedialog as filedialog
from tkinter import messagebox
import speech_recognition as sr
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
            label_word = tk.Label(frame_middle, bg='white', borderwidth=2, relief='groove', font=15)  # anchor='w',
            label_word.place(relx=i / word_candidate_num, relwidth=1 / word_candidate_num, height=frame_middle_height)
            label_word.bind("<ButtonRelease-1>", self.select_word_candidate)
            print(i / word_candidate_num)
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

        self.canvas_keyboard.bind("<Double-Button-1>", self.mouse_left_button_double_click)
        self.entered_words = []
        self.undone_words = []
        self.text = tk.Text(frame_top, bg='white', borderwidth=2, relief='groove', font=('Arial', 20), undo=True)
        self.text.place(x=0, y=0, width=window_width, height=frame_top_height)

        # Create a variable to store the original contents of the text widget
        self.orig_text_contents = self.text.get("1.0", "end")
        self.copy_buffer = ''
        self.text_change_stack = []  # Stack to store text changes
        self.text_change_index = -1  # Index for tracking the current change
        self.attachment_label = tk.Label(self.text, text="", font=('Arial', 14))
        self.attachment_label.pack(side="bottom", anchor="w")
        self.keyboard_designs = [kd.Keyboard(self.canvas_keyboard), cd.Keyboard(self.canvas_keyboard)]
        self.current_keyboard = 0
        self.change_keyboard()
        self.canvas_keyboard.bind("123", self.toggle_keyboard)
        self.recognizer = sr.Recognizer()

        # Nút để kích hoạt nhận diện giọng nói
        self.voice_recognition_button = tk.Button(frame_top, text="Voice Recognize",
                                                  command=self.start_voice_recognition)
        self.voice_recognition_button.place(x=10, y=50)

    def start_voice_recognition(self):
        current_cursor_position = self.text.index(tk.INSERT)
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening for command...")
                audio = self.recognizer.listen(source)
                recognized_text = self.recognizer.recognize_google(audio)
                print("You said:", recognized_text)
                if "save" == recognized_text.lower():
                    self.save_to_file()
                elif "copy" == recognized_text.lower():
                    selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
                    self.copy_buffer = selected_text
                elif "print" == recognized_text.lower():
                    self.text.insert(current_cursor_position, self.copy_buffer)
                elif "undo" == recognized_text.lower():
                    self.undo()
                elif "redo" == recognized_text.lower():
                    self.redo()
                else:
                    messagebox.showwarning("Warning", "This is not a command or we can not realize your command.")
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
        except sr.RequestError:
            print("Could not request results. Check your internet connection.")

    def change_keyboard(self):
        self.canvas_keyboard.delete("all")
        self.keyboard = self.keyboard_designs[self.current_keyboard]
        self.keyboard.keyboard_layout()

    def toggle_keyboard(self,event):
        self.current_keyboard = (self.current_keyboard + 1) % 2
        self.change_keyboard()
    def save_to_file(self):
        text_to_save = self.text.get("1.0", "end-1c")

        if text_to_save:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(text_to_save)
                messagebox.showinfo("Success", f"Text saved to {file_path}")
            else:
                messagebox.showinfo("Info", "File not saved.")
        else:
            messagebox.showwarning("Warning", "No text to save.")
    def attach_file(self):
        attached_file_path = filedialog.askopenfilename()
        if attached_file_path:
            self.attached_file_path = attached_file_path
            self.attached_file_name = attached_file_path.split("/")[-1]
            self.attachment_label.config(text=f"Attached file: {self.attached_file_name}")
            messagebox.showinfo("Attachment", f"File '{self.attached_file_name}' attached.")

    # when users select a word candidate from the four labels in the middle frame
    def mouse_left_button_double_click(self, event):
        current_cursor_position = self.text.index(tk.INSERT)
        character = self.label_word_candidates[0].cget("text")
        character += self.keyboard.get_key_pressed()
        self.label_word_candidates[0].config(text=character)

    def undo(self):
        if self.text.edit_undo():
            self.orig_text_contents = self.text.get("1.0", "end")

    def text_change(self, event):
        # Track text changes and update the stack
        if self.text_change_index < len(self.text_change_stack) - 1:
            self.text_change_stack = self.text_change_stack[:self.text_change_index + 1]

        self.text_change_stack.append(self.text.get("1.0", "end"))
        self.text_change_index = len(self.text_change_stack) - 1

    def redo(self):
        try:
            self.text.edit_redo()
        except:
            pass

    def select_word_candidate(self, event):
        # Get the button that triggered the event
        btn = event.widget
        # Extract the selected word from the button and convert it to lowercase
        selected_word = btn.cget('text').lower()
        # Get the current cursor position in the text widget
        current_cursor_position = self.text.index(tk.INSERT)

        # Check if the selected word is "cmd undo"
        if selected_word.lower() == "cmd undo":
            # Ask for confirmation before triggering the Undo command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Undo command?")
            if response == "yes":
                self.undo()  # Call the undo function
            else:
                self.text.insert(current_cursor_position, "cmd undo ")  # Insert "cmd undo" at the current cursor position

        # Check if the selected word is "cmd redo"
        elif selected_word.lower() == "cmd redo":
            # Ask for confirmation before triggering the Redo command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Redo command?")
            if response == "yes":
                self.redo()  # Call the redo function
            else:
                self.text.insert(current_cursor_position, "cmd redo ")  # Insert "cmd redo" at the current cursor position

        # Check if the selected word is "cmd copy"
        elif selected_word.lower() == "cmd copy":
            # Ask for confirmation before triggering the Copy command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Copy command?")
            if response == "yes":
                # Get the selected text and store it in the copy buffer
                selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.copy_buffer = selected_text
            else:
                self.text.insert(current_cursor_position, "cmd copy ")  # Insert "cmd copy" at the current cursor position

        # Check if the selected word is "cmd paste"
        elif selected_word.lower() == "cmd paste":
            # Ask for confirmation before triggering the Paste command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Paste command?")
            if response == "yes":
                # Insert the content of the copy buffer at the current cursor position
                self.text.insert(current_cursor_position, self.copy_buffer)
            else:
                self.text.insert(current_cursor_position, "cmd paste ")  # Insert "cmd paste" at the current cursor position

        # Check if the selected word is "cmd attach"
        elif selected_word.lower() == "cmd attach":
            # Ask for confirmation before triggering the Attach file command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Attach file?")
            if response == "yes":
                self.attach_file()  # Call the attach file function
            else:
                self.text.insert(current_cursor_position, "cmd attach ")  # Insert "cmd attach" at the current cursor position

        # Check if the selected word is "cmd save"
        elif selected_word.lower() == "cmd save":
            # Ask for confirmation before triggering the Save file command
            response = messagebox.askquestion("Confirmation", "Do you want to trigger the Save file?")
            if response == "yes":
                self.save_to_file()  # Call the save to file function
            else:
                self.text.insert(current_cursor_position, "cmd save ")  # Insert "cmd save" at the current cursor position

        # If none of the special commands were triggered, handle normal text input
        else:
            # Clear the undone_words list if it is not empty
            if self.undone_words:
                self.undone_words.clear()
            # Append the selected word to the entered_words list
            self.entered_words.append(selected_word)
            # Create an edit separator to demarcate this change
            self.text.edit_separator()  
            # Insert the selected word at the current cursor position followed by a space
            self.text.insert(current_cursor_position, selected_word + " ")

        # Clear the labels displaying word candidates
        for i in range(len(self.label_word_candidates)):
            self.label_word_candidates[i].config(text='')

    # press mouse left button
    def mouse_left_button_press(self, event):
        self.cursor_move_position_list.append([event.x, event.y, 0])  # store x, y, segment tag
        self.keyboard.key_press(event.x, event.y)
        self.gesture_points.clear()
        # self.gesture_points.append(Point(event.x, event.y))

    # release mouse left button
    def mouse_left_button_release(self, event):
        previous_x = self.cursor_move_position_list[-1][0]
        previous_y = self.cursor_move_position_list[-1][1]
        line_tag = self.canvas_keyboard.create_line(previous_x, previous_y, event.x, event.y)
        self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.key_release(event.x, event.y)
        result = self.word_recognizer.recognize(self.gesture_points)
        key = self.keyboard.get_key_pressed()
        if key == '123':
            self.toggle_keyboard(None)
        elif key == 'abc':
            self.toggle_keyboard(None)
        elif len(result) > 0:
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
