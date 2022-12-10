import sys
from copy import deepcopy

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter import *

import cv2
from PIL import ImageTk, Image

def do_stuffs():
	summary_details = [0,1,2,3]
	return summary_details

def open_file(image_panel):
	is_not_initialized = True

	# browse file system with jpeg and jpg extensions
	file_path = askopenfilename(
		filetypes = [
			("image", "*.jpeg"),
			("image", "*.jpg"),
		]
	)

	# if file is empty, return
	if not file_path:
		return

	# read image file
	image = cv2.imread(file_path)

	# ==== THIS IS WHERE WE DO STUFFS ====

	# expects a list of values
	obtained_values = do_stuffs()
	# index of obtained_values
	index = 0
	# gets each item of the treeview
	list_of_entries = summary_table.get_children()
	# iterates through each treeview element
	for each in list_of_entries:
		# updates the value of the treeview element
		summary_table.item(each, text="", values=(summary_table.item(each)['values'][0], obtained_values[index]))
		# updates the index of obtained_values
		index = index + 1

	# =============== END ================

	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image = Image.fromarray(image)
	width, height = image.size
	image = image.resize((300, 169))
	image = ImageTk.PhotoImage(image)

	# update image panel
	image_panel.configure(image=image)
	image_panel.image = image

def create_open_image(window):
	open_image_frame = tk.Frame(window)
	image_panel = Label (open_image_frame, text="No Image Selected")
	open_button = tk.Button(open_image_frame, text="Open File", command= lambda : open_file(image_panel))

	open_button.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
	image_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

	open_image_frame.rowconfigure(0, weight=1)
	open_image_frame.columnconfigure(0, weight=1)
	open_image_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

	return
	
# builds the summary table
def create_summary_table(window):
	summary_table = ttk.Treeview(window, columns=("Detail", "Value"), show="headings", height=4)
	summary_table.heading("#1", text="Detail")
	summary_table.heading("#2", text="Value")
	summary_table.column("# 1", anchor="center")
	summary_table.column("# 2", anchor="center")
	
	summary_table.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

	summary_details = [
		['Num. of Healthy', 'N/A'],
		['Num. of Wilted', 'N/A'],
		['Largest Healthy', 'N/A'],
		['Smallest Healthy', 'N/A'],
	]

	for i in range(len(summary_details)):
			summary_table.insert("", tk.END, values=(summary_details[i][0], summary_details[i][1]))

	return summary_table

window = tk.Tk()
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

create_open_image(window)
summary_table = create_summary_table(window)

window.mainloop()