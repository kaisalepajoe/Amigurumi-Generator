import numpy as np 
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import simpledialog
from tkinter import font

# Gauge is [stitches, rows] in a 4x4 cm square
pink_gauge = [10,12]
colors = {
	'platinum':'#EDECE8',
	'gunmetal':'#242F40',
	'pale pink':'#EFD2D4',
	'slate gray':'#747C92',
	'light gray':'#bdbdbd',
	}

elements = {
	'start':['flat','cone','cup'],
	'middle':['tube','open_cone','open_cup','cone_closure','cup_closure'],
	}

requirements = {
	'flat':['maximum circumference'],
	'cone':['maximum circumference'],
	'cup':['maximum circumference'],
	'tube':['length in cm'],
	'open_cone':['hole diameter'],
	'open_cup':['hole diameter'],
	'cone_closure':[],
	'cup_closure':[],
}

def get_stitches(width_cm, gauge, gauge_cm=4):
	# width given in cm
	stitches = int(width_cm*gauge[0]/gauge_cm)
	return stitches

def get_rows(length_cm, gauge, gauge_cm=4):
	# length given in cm
	rows = int(length_cm*gauge[1]/gauge_cm)
	return rows

def get_circumference(diameter_cm):
	circ = np.pi*diameter_cm
	return circ

def div_6(stitches):
	# Returns the closest number divisible by 6
	if stitches < 6:
		out_stitches = 6
	else:
		remainder = stitches % 6
		if remainder == 0:
			out_stitches = stitches
		elif remainder <= 3:
			out_stitches = stitches - remainder
		else:
			out_stitches = stitches + (6 - remainder)
	out_stitches = int(out_stitches)
	assert out_stitches % 6 == 0
	return out_stitches

def get_circumference_in_stitches(diameter_cm, gauge, div_by=6):
	diameter_rows = get_rows(diameter_cm, gauge)
	#print(f"diameter rows {diameter_rows}")
	n_rows = diameter_rows/2 - 0.5
	n_rows = int(n_rows)
	circumference = n_rows*div_by
	return circumference

def get_inc_rows(max_circ, div_by=6):
	n_rows = max_circ//div_by
	inc_rows = np.zeros(n_rows)
	n_stitches = div_by
	for row in range(n_rows):
		inc_rows[row] = n_stitches
		n_stitches += div_by
	return inc_rows

def get_dec_rows(max_circ, min_circ=0, div_by=6):
	if min_circ == 0:
		n_rows = max_circ//div_by - 1
	else:
		n_rows = max_circ//div_by - 1 - (min_circ//div_by - 1)
	dec_rows = np.zeros(n_rows)
	n_stitches = max_circ
	for row in range(n_rows-1):
		n_stitches -= div_by
		dec_rows[row] = n_stitches
	if min_circ == 0:
		dec_rows[-1] = 9
	else:
		n_stitches -= div_by
		dec_rows[-1] = n_stitches
	return dec_rows

def get_inc_length(diameter_cm, circle_d=8):
	# circle_d is a constant indicating the curvature of the decrease
	a = np.sqrt(circle_d**2 - (diameter_cm/2)**2)
	dec_length = circle_d - a
	return dec_length

def get_dec_length(diameter_cm, circle_d=8):
	# circle_d is a constant indicating the curvature of the decrease
	a = np.sqrt(circle_d**2 - (diameter_cm/2)**2)
	dec_length = circle_d - a
	return dec_length

def create_flat_element(diameter_cm, gauge, circ_st=None):
	# Flat spiral beginning
	max_circ = get_circumference_in_stitches(diameter_cm, gauge, div_by=8)
	inc_rows = get_inc_rows(max_circ, div_by=8)
	return ['inc_start',inc_rows,max_circ]

def create_cup_element(diameter_cm, gauge, circ_st=None):
	# Regular amigurumi sphere beginning
	max_circ = get_circumference_in_stitches(diameter_cm, gauge)
	inc_rows = get_inc_rows(max_circ, div_by=6)
	return ['inc_start',inc_rows,max_circ]

def create_cone_element(diameter_cm, gauge, circ_st=None):
	# Cone-shaped beginning
	max_circ = get_circumference_in_stitches(diameter_cm, gauge, div_by=6)
	inc_rows = get_inc_rows(max_circ, div_by=3)
	inc_rows = inc_rows[1:]
	return ['inc_start',inc_rows,max_circ]

def create_tube_element(length_cm, gauge, circ_st):
	n_rows = get_rows(length_cm, gauge)
	return ['straight', n_rows, circ_st]

def create_cup_closure_element(_, gauge, circ_st):
	dec_rows = get_dec_rows(int(circ_st))
	return ['dec', dec_rows, 0]

def create_cone_closure_element(_, gauge, circ_st):
	dec_rows = get_dec_rows(int(circ_st), div_by=3)
	dec_rows = dec_rows[:-1]
	return ['dec', dec_rows, 0]

def create_open_cup_element(hole_diameter_cm, gauge, circ_st=None):
	hole_circ = get_circumference_in_stitches(hole_diameter_cm, gauge, div_by=6)
	_, dec_rows, _ = create_cup_closure_element(None, gauge, circ_st)
	dec_rows = dec_rows[np.where(dec_rows >= hole_circ)]
	return ['dec', dec_rows, hole_circ]

def create_open_cone_element(hole_diameter_cm, gauge, circ_st=None):
	hole_circ = get_circumference_in_stitches(hole_diameter_cm, gauge, div_by=3)
	_, dec_rows, _ = create_cone_closure_element(None, gauge, circ_st)
	dec_rows = dec_rows[np.where(dec_rows >= hole_circ)]
	return ['dec', dec_rows, hole_circ]

# This is the first test function
def create_sausage_elements(diameter_cm, length_cm, gauge):
	max_circ = get_circumference_in_stitches(diameter_cm, gauge)
	#print(f"Maximum circ in st: {max_circ}")
	inc_rows = get_inc_rows(max_circ)
	dec_rows = get_dec_rows(max_circ)
	rows_used = len(inc_rows) + len(dec_rows)
	inc_length_cm = get_inc_length(diameter_cm)
	dec_length_cm = get_dec_length(diameter_cm)
	remaining_length_cm = length_cm - inc_length_cm - dec_length_cm
	straight_n_rows = get_rows(remaining_length_cm, gauge)
	elements = [
		['inc_start',inc_rows],
		['straight',straight_n_rows],
		['dec',dec_rows],
		['sew FO'],
		]
	return elements

def create_inc_start_str(inc_rows, curr_row):
	to_print = "Create magic loop\n"
	curr_row += 1
	to_print += f"Round {curr_row}: Crochet {int(inc_rows[0])} stitches into loop ({int(inc_rows[0])})\n"
	curr_st = inc_rows[0]
	curr_row += 1
	for st in inc_rows[1:]:
		n_inc = st - curr_st
		n_sc = st/n_inc - 2
		if n_sc == 0:
			to_print += f"Round {curr_row}: inc {int(n_inc)} times ({int(st)})\n"
		else:
			to_print += f"Round {curr_row}: (sc {int(n_sc)}, inc) until end of round ({int(st)})\n"
		curr_st = st
		curr_row += 1
	return to_print, curr_row, curr_st

def create_straight_str(n_rows, curr_row, curr_st):
	final_row = curr_row + n_rows - 1
	to_print = f"Round {curr_row}-{final_row}: sc {n_rows} rounds\n"
	curr_row = final_row
	return to_print, curr_row, curr_st

def create_dec_str(dec_rows, curr_row, curr_st):
	to_print = ""
	curr_row += 1
	for st in dec_rows:
		n_dec = curr_st - st
		n_sc = curr_st/n_dec - 2
		to_print += f"Round {curr_row}: (dec, sc {int(n_sc)}) until end of round ({int(st)})\n"
		curr_st = st
		curr_row += 1
	return to_print, curr_row, curr_st

def print_pattern(elements):
	curr_row = 0
	to_print = ""
	for element in elements:
		if element[0] == 'inc_start':
			inc_rows = element[1]
			inc_start_str, curr_row, curr_st = create_inc_start_str(inc_rows, curr_row)
			to_print += inc_start_str
		elif element[0] == 'straight':
			n_rows = element[1]
			straight_str, curr_row, curr_st = create_straight_str(n_rows, curr_row, curr_st)
			to_print += straight_str
		elif element[0] == 'dec':
			dec_rows = element[1]
			dec_str, curr_row, curr_st = create_dec_str(dec_rows, curr_row, curr_st)
			to_print += dec_str
		elif element[0] == 'sew FO':
			to_print += "Fasten off by leaving a long yarn end and stitching the small hole shut\n"
		elif element[0] == 'FO':
			to_print += "Fasten off\n"
		elif element[0] == 'simple print':
			to_print += element[1] + '\n'
		else:
			raise ValueError('Unknown element')
	return to_print

####################################################################################################

# Amigurumi class
class Pattern:
	def __init__(self, root):
		self.pieces = {}
		self.root = root
		self.to_print = ''
		self.startup_draw()

		self.load_plus_photo = Image.open('./images/add.png').resize((50,50))
		self.load_cone_photo = Image.open('./images/cone_start.png')
		self.load_cup_photo = Image.open('./images/cup_start.png')
		self.load_flat_photo = Image.open('./images/flat_start.png')
		self.load_tube_photo = Image.open('./images/tube.png')
		self.load_cup_closure_photo = Image.open('./images/cup_closure.png')
		self.load_cone_closure_photo = Image.open('./images/cone_closure.png')
		self.load_open_cup_photo = Image.open('./images/open_cup.png')
		self.load_open_cone_photo = Image.open('./images/open_cone.png')

		self.plus_photo = ImageTk.PhotoImage(self.load_plus_photo)
		'''
		self.cone_photo = ImageTk.PhotoImage(load_cone_photo)
		self.cup_photo = ImageTk.PhotoImage(load_cup_photo)
		self.flat_photo = ImageTk.PhotoImage(load_flat_photo)
		self.tube_photo = ImageTk.PhotoImage(load_tube_photo)
		self.cup_closure_photo = ImageTk.PhotoImage(load_cup_closure_photo)
		self.cone_closure_photo = ImageTk.PhotoImage(load_cone_closure_photo)
		self.open_cup_photo = ImageTk.PhotoImage(load_open_cup_photo)
		self.open_cone_photo = ImageTk.PhotoImage(load_open_cone_photo)
		'''

	def startup_draw(self):
		self.startup_canvas = tk.Canvas(self.root,width=300,height=200,bg=colors['platinum'])
		self.startup_canvas.pack()

		gauge_label = tk.Label(self.root, text='Set gauge (4x4 cm)', bg=colors['platinum'])
		st_label = tk.Label(self.root, text='Stitches:', bg=colors['platinum'])
		self.st_entry = tk.Entry(self.root)
		self.st_entry.insert('end', pink_gauge[0])
		row_label = tk.Label(self.root, text='Rows:', bg=colors['platinum'])
		self.row_entry = tk.Entry(self.root)
		self.row_entry.insert('end', pink_gauge[1])
		title_label = tk.Label(self.root, text='Set title:', bg=colors['platinum'])
		self.title_entry = tk.Entry(self.root)
		start_button = tk.Button(self.root, text='Start New Pattern', bg=colors['slate gray'])
		start_button.bind("<Button-1>", self.start_button_press, add='+')
		self.root.bind('<Return>', self.start_button_press)

		self.startup_canvas.create_window(5,10,window=gauge_label,anchor='nw')
		self.startup_canvas.create_window(5,30,window=st_label,anchor='nw')
		self.startup_canvas.create_window(100,30,window=self.st_entry,anchor='nw')
		self.startup_canvas.create_window(5,50,window=row_label,anchor='nw')
		self.startup_canvas.create_window(100,50,window=self.row_entry,anchor='nw')
		self.startup_canvas.create_window(5,70,window=title_label,anchor='nw')
		self.startup_canvas.create_window(100,70,window=self.title_entry,anchor='nw')
		self.startup_canvas.create_window(150,130,window=start_button,anchor='center')

	def start_button_press(self, event):
		try:
			sts = int(self.st_entry.get())
			rows = int(self.row_entry.get())
			title = self.title_entry.get()
		except:
			return
		gauge = [sts, rows]
		self.gauge = gauge
		self.title = title
		self.pattern_creation_page()

	def pattern_creation_page(self):
		for widget in self.root.winfo_children():
			widget.destroy()
		self.mainmenu = tk.Menu(self.root)
		self.root.configure(menu=self.mainmenu)
		self.mainmenu.add_command(label='Add piece', command=self.add_piece, background=colors['pale pink'])
		self.mainmenu.add_command(label='Update gauge', command=self.update_gauge)

		self.canvas = tk.Canvas(self.root, width=800,height=600, bg=colors['platinum'])
		self.canvas.pack()

		self.pieces_list = tk.Listbox(self.root, width=52, height=12, selectmode='single', exportselection=False)
		self.pieces_window = self.canvas.create_window(10,10,anchor='nw',window=self.pieces_list)
		self.pieces_list.bind("<<ListboxSelect>>", self.on_piece_select)

		self.temp_elements_list = tk.Listbox(self.root, width=52, height=30, selectmode='extended')
		self.elements_window = self.canvas.create_window(10,200,window=self.temp_elements_list,anchor='nw')
		self.elements_list = []

		self.label_plus_photo = tk.Label(self.root, image=self.plus_photo, bg='white')
		self.canvas.create_window(315,500,window=self.label_plus_photo,anchor='nw')
		self.label_plus_photo.bind("<Button-1>", self.add_element)

		self.text = tk.Text(self.root, width=55, height=51, bg=colors['pale pink'])
		self.text_window = self.canvas.create_window(590,293,anchor='center',window=self.text)

	def add_piece(self):
		piece_title = tk.simpledialog.askstring("Input", "Title of piece (head, body, ...)")
		self.pieces_list.insert('end', piece_title)
		self.pieces[piece_title] = []
		new_listbox = tk.Listbox(self.root, width=52, height=30, selectmode='extended')
		self.elements_list.append(new_listbox)
		self.pieces_list.select_clear(0,-1)
		self.pieces_list.select_set(self.pieces_list.size()-1)
		self.canvas.itemconfig(self.elements_window, window=self.elements_list[-1])
		self.label_plus_photo.lift()
		self.update_print(self.pieces[piece_title], piece_title)

	def on_piece_select(self, event):
		widget = event.widget
		index_tuple = widget.curselection()
		if not index_tuple:
			return
		piece_index = index_tuple[0]
		elements_listbox = self.elements_list[piece_index]
		self.canvas.itemconfig(self.elements_window,window=elements_listbox)
		piece_name = self.pieces_list.get(piece_index)
		piece_elements = self.pieces[piece_name]
		self.update_print(piece_elements, piece_name)

	def add_element(self, event):
		index_tuple = self.pieces_list.curselection()
		if not index_tuple:
			tk.messagebox.showinfo(message='You need to create a piece first.')
			return
		piece_index = index_tuple[0]

		# check if first element exists
		if not self.elements_list[piece_index].get(0):
			choose_start = True
		else:
			choose_start = False

		dialog = ElementSelectionDialog(self.root, self, choose_start)
		self.root.wait_window(dialog.top)
		element_name = dialog.element_choice_str
		element_parameter = dialog.element_parameter
		self.elements_list[piece_index].insert('end', element_name)
		# GET PREVIOUS CIRC_ST FROM SOMEWHERE
		if choose_start == True:
			self.circ_st = 0
		element = eval('create_'+element_name+'_element')(element_parameter, self.gauge, self.circ_st)
		self.circ_st = element[2]
		piece_name = self.pieces_list.get(piece_index)
		self.pieces[piece_name].append(element)
		self.update_print(self.pieces[piece_name], piece_name)

	def update_print(self, elements, piece_title):
		to_print = piece_title+'\n'+'\n'
		to_print += print_pattern(elements)
		self.text.delete(1.0, 'end')
		self.text.insert('end',to_print)
		self.to_print = to_print

	def update_gauge(self):
		dialog = UpdateGaugeDialog(self.root, self.gauge)
		self.root.wait_window(dialog.top)
		new_gauge = dialog.gauge
		self.update_elements

	def update_elements(self):
		pass

class ElementSelectionDialog:
	def __init__(self, parent, pattern, choose_start):
		top = self.top = tk.Toplevel(parent)

		if choose_start == True:
			question = 'Click on a shape to start the piece'
			self.choices_list = elements['start']
		else:
			question = 'Click to choose a shape to continue the piece'
			self.choices_list = elements['middle']
		
		question_label = tk.Label(top, text=question)
		question_label.pack()
		self.canvas = tk.Canvas(top, width=800, height=400)
		self.canvas.pack()

		self.element_parameter_label = tk.Label(top, text='')
		self.element_parameter_entry = tk.Entry(top)
		self.label_window = self.canvas.create_window(20,300,anchor='nw',window=self.element_parameter_label)
		
		self.top.bind('<Return>', self.ok)
		button = tk.Button(top, text='OK', command=self.ok)

		ok_button_window = self.canvas.create_window(400,360,window=button)

		self.error_message_label = tk.Label(top, text='')
		error_message_window = self.canvas.create_window(400,330,window=self.error_message_label)

		self.image_width=(800-40)/len(self.choices_list)
		corner_x = 20
		image_center = 20 + self.image_width/2
		self.element_objects = []
		for choice_str in self.choices_list:
			load_img_varname = 'load_'+choice_str+'_photo'
			load_image = getattr(pattern, load_img_varname).resize((int(self.image_width),int(self.image_width)))
			setattr(pattern, choice_str+'_photo', ImageTk.PhotoImage(load_image))
			canvas_image = self.canvas.create_image((image_center, 20+self.image_width/2), image=getattr(pattern, choice_str+'_photo'))
			rectangle = self.canvas.create_rectangle(corner_x, 20, corner_x+self.image_width, 20+self.image_width,
				outline='', activefill=colors['light gray'], stipple='gray50')
			self.canvas.tag_bind(rectangle, "<Button-1>", self.highlight)
			self.element_objects.append(Element(choice_str, rectangle, self.canvas))
			image_center += self.image_width
			corner_x += self.image_width

	def highlight(self, event):
		for element_object in self.element_objects:
			is_clicked, choice_str = element_object.is_clicked(event.x, event.y)
			if is_clicked:
				self.element_choice_str = choice_str
				rectangle_to_highlight = element_object.rectangle
				self.canvas.itemconfig(element_object.rectangle, fill=colors['slate gray'], activefill='')
				if requirements[choice_str]:
					self.element_parameter_label.config(text='Enter '+requirements[choice_str][0]+' in cm: ')
					label_width = self.element_parameter_label.winfo_width()
					self.entry_window = self.canvas.create_window(20+5+label_width,300,anchor='nw',window=self.element_parameter_entry)
			else:
				self.canvas.itemconfig(element_object.rectangle, fill='', activefill=colors['light gray'])

	def ok(self, event=None):
		if not hasattr(self, 'element_choice_str'):
			self.error_message_label.config(text='Please choose a shape')
			return
		if self.element_parameter_entry.get()=='':
			# check if the entry is supposed to be empty 
			if requirements[self.element_choice_str]:
				self.error_message_label.config(text='Please write a value for the diameter')
				return
		try:
			self.element_parameter = float(self.element_parameter_entry.get())
		except:
			if requirements[self.element_choice_str]:
				self.error_message_label.config(text='Invalid diameter')
				return
			else:
				self.element_parameter = None
		self.top.destroy()

class UpdateGaugeDialog:
	def __init__(self, root, gauge):
		current_sts = gauge[0]
		current_rows = gauge[1]
		top = self.top = tk.Toplevel(root)

		canvas = tk.Canvas(top, width=300, height=150, bg=colors['platinum'])
		canvas.pack()

		modify_label = tk.Label(top, text='Modify gauge (4x4 cm)', bg=colors['platinum'])
		canvas.create_window(10,10,window=modify_label,anchor='nw')

		st_label = tk.Label(top, text='Stitches:', bg=colors['platinum'])
		canvas.create_window(10,30,window=st_label,anchor='nw')

		self.st_entry = tk.Entry(top)
		self.st_entry.insert('end', current_sts)
		canvas.create_window(100,30,window=self.st_entry,anchor='nw')

		row_label = tk.Label(top, text='Rows:', bg=colors['platinum'])
		canvas.create_window(10,50,window=row_label,anchor='nw')

		self.row_entry = tk.Entry(top)
		self.row_entry.insert('end', current_rows)
		canvas.create_window(100,50,window=self.row_entry,anchor='nw')

		ok_button = tk.Button(top, text='OK', bg=colors['slate gray'])
		ok_button.bind("<Button-1>", self.ok_button_press, add='+')
		top.bind('<Return>', self.ok_button_press)
		canvas.create_window(150,100,window=ok_button,anchor='center')

	def ok_button_press(self,event):
		new_sts = self.st_entry.get()
		new_rows = self.row_entry.get()
		self.gauge = [new_sts, new_rows]
		self.top.destroy()


class Element:
	def __init__(self, choice_str, rectangle, canvas):
		self.choice_str = choice_str
		self.rectangle = rectangle
		self.canvas = canvas
		self.selected = False
	def is_clicked(self, click_x, click_y):
		x0, y0, x1, y1 = self.canvas.coords(self.rectangle)
		if click_x>x0 and click_x<x1 and click_y>y0 and click_y<y1:
			clicked = True
		else:
			clicked = False
		return clicked, self.choice_str

####################################################################################################

# Tkinter functions

def main():
	root = tk.Tk()
	root.configure(bg=colors['platinum'])
	root.geometry('800x600')
	root.title('Crochet Pattern Generator')
	pattern = Pattern(root)
	root.mainloop()

if __name__=='__main__':
	main()