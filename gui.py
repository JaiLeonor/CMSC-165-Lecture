import sys

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from tkinter import *

import cv2
from PIL import ImageTk, Image

import count_pollen

def do_stuffs():
	summary_details = [
		"1 pixel : 10 μm",
		"69",
		"24",
		"30 μm",
		"10 μm",
	]
	return summary_details

def open_file(image_panel, class_threshold, hough_param, canny_high, canny_low, min_radius, max_radius, min_distance):

	# params to be modified to detect pollen
	classThreshold = int(class_threshold.get()) 
	houghParam2 = int(hough_param.get()) 

	cannyEdgeLow = int(canny_low.get())
	cannyEdgeHigh = int(canny_high.get())

	minRad = int(min_radius.get())
	maxRad = int(max_radius.get())

	minDist = int(min_distance.get())

	# validates the inputted values
	if (classThreshold not in range(0, 255)):
		image_panel.configure(text="Classification Threshold out of range")
		return
	if (houghParam2 not in range(0, 255)):
		image_panel.configure(text="Hough Parameter out of range")
		return
	if (cannyEdgeHigh not in range(0, 255)):
		image_panel.configure(text="Canny Edge High out of range")
		return
	if (cannyEdgeLow not in range(0, 255)):
		image_panel.configure(text="Canny Edge Low out of range")
		return
	if (minRad not in range(0, 255)):
		image_panel.configure(text="Min Radius out of range")
		return
	if (maxRad not in range(0, 255)):
		image_panel.configure(text="Max Radius out of range")
		return
	if (minDist not in range(0, 255)):
		image_panel.configure(text="Min Distance out of range")
		return

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
	# obtained_values = do_stuffs()

	# ========= ACTUAL function
	mainImg = file_path.split("/")[len(file_path.split("/"))-1]
	outputImgName = "main_output.png"

	obtained_values = count_pollen.count_pollen(mainImg, outputImgName, cannyEdgeLow, cannyEdgeHigh, houghParam2, minDist, minRad, maxRad, classThreshold)

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

def create_variables_form(variables_frame):
	# FIRST COLUMN
	tk.Label(variables_frame, text="Classification Threshold").grid(row=0, column=0, padx=2, pady=2, sticky="e")
	tk.Label(variables_frame, text="Hough Parameter").grid(row=1, column=0, padx=2, pady=2, sticky="e")

	class_threshold = tk.Entry(variables_frame)
	class_threshold.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
	class_threshold.insert(0, 70)

	hough_param = tk.Entry(variables_frame)
	hough_param.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
	hough_param.insert(0, 33)

	# SECOND COLUMN
	tk.Label(variables_frame, text="Canny Edge Low").grid(row=0, column=2, padx=2, pady=2, sticky="e")
	tk.Label(variables_frame, text="Canny Edge High").grid(row=1, column=2, padx=2, pady=2, sticky="e")

	canny_low = tk.Entry(variables_frame)
	canny_low.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
	canny_low.insert(0, 100)
	
	canny_high = tk.Entry(variables_frame)
	canny_high.grid(row=1, column=3, padx=2, pady=2, sticky="ew")
	canny_high.insert(0, 230)

	# THIRD COLUMN
	tk.Label(variables_frame, text="Min Radius").grid(row=0, column=4, sticky="e")
	tk.Label(variables_frame, text="Max Radius").grid(row=1, column=4, sticky="e")

	min_radius = tk.Entry(variables_frame)
	min_radius.grid(row=0, column=5, padx=2, pady=2, sticky="ew")
	min_radius.insert(0, 10)
	
	max_radius = tk.Entry(variables_frame)
	max_radius.grid(row=1, column=5, padx=2, pady=2, sticky="ew")
	max_radius.insert(0, 60)

	# FOURTH COLUMN
	tk.Label(variables_frame, text="Min Distance").grid(row=0, column=6, sticky="e")
	
	min_distance = tk.Entry(variables_frame)
	min_distance.grid(row=0, column=7, padx=2, pady=2, sticky="ew")
	min_distance.insert(0, 70)

	variables_frame.columnconfigure((0,2,4,6), weight=1)
	variables_frame.columnconfigure((1,3,5,7), weight=3)

	return class_threshold, hough_param, canny_high, canny_low, min_radius, max_radius, min_distance

def create_open_image(window):
	open_image_frame = tk.Frame(window)

	# image panels
	image_panel = Label (open_image_frame, text="No Image Selected")

	# other variables
	variables_frame = tk.Frame(open_image_frame)
	class_threshold, hough_param, canny_high, canny_low, min_radius, max_radius, min_distance = create_variables_form(variables_frame)

	# open file button
	open_button = tk.Button(open_image_frame, text="Open File", command= lambda : open_file(image_panel, class_threshold, hough_param, canny_high, canny_low, min_radius, max_radius, min_distance))

	# packing the widgets
	open_button.pack(fill=BOTH, expand=True, padx=5, pady=5)
	variables_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
	image_panel.pack(fill=BOTH, expand=True, padx=5, pady=5)
	
	open_image_frame.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

	return
	
# builds the summary table
def create_summary_table(window):
	summary_table = ttk.Treeview(window, columns=("Detail", "Value"), show="headings", height=5)
	summary_table.heading("#1", text="Detail")
	summary_table.heading("#2", text="Value")
	summary_table.column("#1", anchor="center")
	summary_table.column("#2", anchor="center")
	
	summary_table.pack(side=BOTTOM, fill=X, expand=True, padx=5, pady=5)

	summary_details = [
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