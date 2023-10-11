import tkinter as tk


class Application(tk.Frame):
    def __init__(self, window_width, window_height, master=None):
        super().__init__(master)  # Call tk.Frame.__init__(master)
        self.master = master

        # Create a frame and place it in the window
        frame = tk.Frame(self.master, width=window_width, height=window_height)
        frame.pack()

        # Create a canvas and place it in the frame
        self.canvas = tk.Canvas(frame, bg='red')
        self.canvas.place(x=100, y=20, width=500, height=240)

        # bind the event of click left button to the canvas
        self.canvas.bind('<ButtonPress-1>', self.mouse_left_button_press)
        frame.bind('<Button-3>', self.right_button_press)
        
        self.canvas.bind('<Motion>', self.mouse_move)
        frame.bind('<B1-Motion>', self.mouse_move_left_button_press)
        
    def mouse_left_button_press(self, event):
        print("Mouse Left Button Pressed on the Canvas", event.x, " ", event.y)

    def right_button_press(self, event):
        print('Right Button Pressed on Frame', event.x, " ", event.y)
        
    def mouse_move(self, event):
        print('Mouse move on Canvas', event.x, " ", event.y)
    
    def mouse_move_left_button_press(self, event):
        print('Mouse move left button Press', event.x, " ", event.y)
    
        
if __name__ == '__main__':
    master = tk.Tk()
    window_width = 700
    window_height = 300
    # Define window size
    master.geometry(str(window_width) + 'x' + str(window_height))
    app = Application(window_width, window_height, master=master)
    app.mainloop()
