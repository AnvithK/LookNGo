import tkinter as tk
import cv2
import eyetracker

vid = cv2.VideoCapture(0) 


def on_click():
    return

# Create the main window
root = tk.Tk()
root.title("Project")

# Set the background color to a soft, neutral color typical of neumorphic designs
root.configure(bg='#e0e5ec')
width = 300
height = 200
root.geometry(f"{width}x{height}")

# Function to create a neumorphic effect
def create_neumorphic_widget(parent, widget, x, y, width, height):
    # Light shadow frame
    """light_frame = tk.Frame(parent, width=width, height=height, bg='#ffffff', bd=0)
    light_frame.place(x=x-2, y=y-2)

    # Dark shadow frame
    dark_frame = tk.Frame(parent, width=width, height=height, bg='#bec3c9', bd=0)
    dark_frame.place(x=x+2, y=y+2)

    # Main widget frame
    widget_frame = tk.Frame(parent, width=width-4, height=height-4, bg="#e0e5ec", bd=0)
    widget_frame.place(x=x, y=y)

    # Create the actual widget inside the widget frame
    widget = widget(widget_frame)
    widget.pack(fill=tk.BOTH, expand=True)"""

    """return widget"""

    light_frame = tk.Frame(parent, width=width, height=height, bg='#ffffff', bd=0)
    light_frame.place(x=x-2, y=y-2)

    # Dark shadow frame
    dark_frame = tk.Frame(parent, width=width, height=height, bg='#bec3c9', bd=0)
    dark_frame.place(x=x+2, y=y+2)

    # Main widget frame (adjust the bg color to match the main window)
    widget_frame = tk.Frame(parent, width=width-4, height=height-4, bg='#e0e5ec', bd=0)
    widget_frame.place(x=x, y=y)

    # Place the actual widget on the widget frame
    widget_frame.pack_propagate(False)  # Prevents widget from dictating frame's size
    widget = widget(widget_frame)
    widget.pack(fill=tk.BOTH, expand=True)

    return widget

# Create a neumorphic button
btn = create_neumorphic_widget(root, tk.Button, width/3, height/3, 100, 40)
btn.configure(text="Start", command=on_click)

# Start the GUI event loop
root.mainloop()