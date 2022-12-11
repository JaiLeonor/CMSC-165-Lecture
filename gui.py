import sys

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter import *

import cv2
from PIL import ImageTk, Image

import count_pollen

def do_stuffs(threshold_slider):
	summary_details = [
		threshold_slider.get(),
		"1 pixel : 10 μm",
		"69",
		"24",
		"30 μm",
		"10 μm",
	]
	return summary_details

def open_file(image_panel, threshold_slider):
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

	# ==== THIS IS WHERE WE DO STUFFS ====

	# ========= TEST function
	obtained_values = do_stuffs(threshold_slider)

	# ========= ACTUAL function
	mainImg = file_path.split("/")[len(file_path.split("/"))-1]
	outputImgName = "main_output.png"

	# params to be modified to detect pollen
	cannyEdgeLow = 100
	cannyEdgeHigh = 230
	houghParam2 = 33  # controls tuning of circle detection

	minDist = 70    # min distance between circles
	minRad = 10     # min radius of circles
	maxRad = 60     # max radius of circles

	count_pollen.count_pollen(mainImg, outputImgName, cannyEdgeLow, cannyEdgeHigh, houghParam2, minDist, minRad, maxRad)

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

	# read image files
	main_image = cv2.imread(file_path)
	output_image = cv2.imread(outputImgName)

	# convert main image to something that can be displayed
	main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2RGB)
	main_image = Image.fromarray(main_image)
	init_width, init_height = main_image.size
	width = int(init_width*0.4)
	height = int(init_height*0.4)
	output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
	output_image = Image.fromarray(output_image)
	output_image = output_image.resize((width, height))
	output_image = ImageTk.PhotoImage(output_image)

	# update image panel
	image_panel.configure(image=output_image)
	image_panel.image=output_image

def create_open_image(window):
	open_image_frame = tk.Frame(window)

	# image panels
	image_panel = Label (open_image_frame, text="No Image Selected")

	# threshold slider
	threshold_slider = Scale(open_image_frame, from_=0, to=255, orient=HORIZONTAL, label="Threshold")

	# open file button
	open_button = tk.Button(open_image_frame, text="Open File", command= lambda : open_file(image_panel, threshold_slider))

	# packing the widgets
	open_button.pack(fill=BOTH, expand=True, padx=5, pady=5)
	threshold_slider.pack(fill=BOTH, expand=True, padx=5, pady=5)
	image_panel.pack(fill=BOTH, expand=True, padx=5, pady=5)
	
	open_image_frame.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

	return
	
# builds the summary table
def create_summary_table(window):
	summary_table = ttk.Treeview(window, columns=("Detail", "Value"), show="headings", height=6)
	summary_table.heading("#1", text="Detail")
	summary_table.heading("#2", text="Value")
	summary_table.column("#1", anchor="center")
	summary_table.column("#2", anchor="center")
	
	summary_table.pack(side=BOTTOM, fill=X, expand=True, padx=5, pady=5)

	summary_details = [
		['Threshold', 'N/A'],
		['Pixel-to-μm', 'N/A'],
		['Num. of Dark', 'N/A'],
		['Num. of Light', 'N/A'],
		['Largest Dark', 'N/A'],
		['Largest Light', 'N/A'],
	]

	for i in range(len(summary_details)):
			summary_table.insert("", tk.END, values=(summary_details[i][0], summary_details[i][1]))

	return summary_table

window = tk.Tk()
window.title("Yung Team na 'Di Nangangagat")
create_open_image(window)
summary_table = create_summary_table(window)

window.mainloop()