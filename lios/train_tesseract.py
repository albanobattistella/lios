#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################


from lios import scanner, editor, imageview, cam, ocr, preferences, speech
from lios.ui.gtk import widget, containers, loop, menu, \
	window, icon_view, dialog, about, tree_view, text_view, terminal

from lios.ui.gtk.file_chooser import FileChooserDialog
from lios import macros
from lios import localization
_ = localization._

import os

class TesseractTrainer(window.Window):
	def __init__(self,image_list=None):
		window.Window.__init__(self, title="Tesseract Trainer")
		grid = containers.Grid()
		
		if( not ocr.ocr_engine_tesseract.OcrEngineTesseract.is_available()):
			label = widget.Label(_("Tesseract is not installed"))
			self.add(label)
			label.show()
			self.set_default_size(400,200)
			return

		label_language = widget.Label(_("Language "));
		self.combobox_language = widget.ComboBox();

		self.languages = []
		for item in ocr.ocr_engine_tesseract.OcrEngineTesseract.get_available_languages():
			self.combobox_language.add_item(item)
			self.languages.append(item)
		self.combobox_language.set_active(0)

		#Notebook
		notebook = containers.NoteBook()
		notebook.show_all()
		
		#Ambiguous Editor
		self.treeview_ambiguous = tree_view.TreeView([("match",str,False),
		("Replacement",int,True),("Mandatory",int,True)],self.ambiguous_edited_callback)
		notebook.add_page("Ambiguous",self.treeview_ambiguous);
		
		#Dictionary Editor
		label_select_word_dict = widget.Label(_("Select Word dict "));
		button_select_word_dict = widget.Button(_("Select word dict"));
		label_select_freequent_word_dict = widget.Label(_("Select Freequent Word dict "));
		button_select_freequent_word_dict = widget.Button(_("Select Freequent Word dict"));
		label_select_punctation_dict = widget.Label(_("Select Punctuation dict "));
		button_select_punctation_dict = widget.Button(_("Select Punctuation dict "));
		label_select_number_dict = widget.Label(_("Select Number dict "));
		button_select_number_dict = widget.Button(_("Select Number dict "));
		label_select_word_with_digit_dict = widget.Label(_("Select Word with digit  dict "));
		button_select_word_with_digit_dict = widget.Button(_("Select Word with digit  dict "));
		
		seperator_user_words = widget.Separator()
		
		label_user_words = widget.Label(_("User Words "));
		text_view_user_words = text_view.TextView()
		text_view_user_words.set_border_width(10);
		
		button_set_dictionary = widget.Button("Apply Dictionary's ")
		
		
		grid_set_dictionary = containers.Grid()
		grid_set_dictionary.add_widgets([(label_select_word_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_word_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_freequent_word_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_freequent_word_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_punctation_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_punctation_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_number_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_number_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(label_select_word_with_digit_dict,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND,containers.Grid.ALIGN_START),
		(button_select_word_with_digit_dict,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(seperator_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		containers.Grid.NEW_ROW,
		(label_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(text_view_user_words,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(button_set_dictionary,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)]);
		notebook.add_page(_("Dictionary's"),grid_set_dictionary);		
		
		# Manual Training (using scanned images)
		label_font_manual = widget.Label("Font ");
		self.entry_font_manual = widget.Entry()
		self.fontbutton_manual = widget.FontButton();
		self.fontbutton_manual.connect_function(self.font_manual_changed)
		self.entry_font_manual.set_text(self.fontbutton_manual.get_font_name())
		
		seperator_select_images = widget.Separator()
		
		label_select_images = widget.Label(_("Select scanned images for training"));
		
		self.tree_view_image_list = tree_view.TreeView([("File name ",str,False)],self.tree_view_image_list_edited_callback)
		
		for item in image_list:
			self.tree_view_image_list.append((item,));
		button_train = widget.Button("Start Training");
		button_train.connect_function(self.button_manual_train_clicked);
			
		
		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_font_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.entry_font_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		(self.fontbutton_manual,1,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_images,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		containers.Grid.NEW_ROW,
		(seperator_select_images,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,		
		(self.tree_view_image_list,2,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),		
		(button_train,1,1,containers.Grid.NO_HEXPAND,containers.Grid.VEXPAND)])		
		
		notebook.add_page(_("Manual Training (using scanned images)"),grid_manual_methord);		


		# Automatic Training (using fonts)
		label_select_font_dir = widget.Label("Font Directory");
		button_select_font_dir = widget.Button("Chose");

		label_font_automatic = widget.Label("Font ");
		fontbutton_automatic = widget.FontButton();
				
		label_select_input_text = widget.Label("Input Text File");
		button_select_input_text = widget.Button("Chose");

		label_writing_mode = widget.Label("Writing Mode");
		combobox_writing_mode = widget.ComboBox();

		
		grid_manual_methord = containers.Grid()
		grid_manual_methord.add_widgets([(label_select_font_dir,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(button_select_font_dir,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_font_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(fontbutton_automatic,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(button_select_input_text,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,
		(label_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND,containers.Grid.ALIGN_START),
		(combobox_writing_mode,1,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND)])		
		
		notebook.add_page(_("Automatic Training (using fonts)"),grid_manual_methord);	
		 
		
		self.output_terminal = terminal.Terminal("/tmp")
		scroll_box_output = containers.ScrollBox()
		scroll_box_output.add(self.output_terminal)
		paned = containers.Paned(containers.Paned.VERTICAL)
		paned.add(notebook);
		paned.add(scroll_box_output);
		
		
		
		button_close = widget.Button(_("Close"));
		button_close.connect_function(self.close_trainer);
		
		grid.add_widgets([(label_language,1,1,containers.Grid.NO_HEXPAND,containers.Grid.NO_VEXPAND),
		(self.combobox_language,2,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND),
		containers.Grid.NEW_ROW,(paned,3,1,containers.Grid.HEXPAND,containers.Grid.VEXPAND),
		containers.Grid.NEW_ROW,(button_close,3,1,containers.Grid.HEXPAND,containers.Grid.NO_VEXPAND)])
		
		
		self.add(grid)
		grid.show_all()
		self.maximize()
	
	def font_manual_changed(self,*data):
		fontname = self.fontbutton_manual.get_font_name()
		self.entry_font_manual.set_text(fontname)

	def close_trainer(self,*data):
		self.destroy();
	
	def ambiguous_edited_callback(self,*data):
		print ("edited")
	
	def tree_view_image_list_edited_callback(self,*data):
		print("hello");
	
	def button_manual_train_clicked(self,*data):
		index = self.tree_view_image_list.get_selected_row_index()
		items = self.tree_view_image_list.get_list()
		item = items[index][0]
		item_name_without_extension = item.split(".")[0]
		self.language = "eng"
		
		font_desc = self.entry_font_manual.get_text()
		
		
		if (os.path.isfile("/tmp/batch.nochop.box")):
			os.remove("/tmp/batch.nochop.box");
		self.output_terminal.run_command("convert {0} -background white -flatten {1}.tif".format(item,item_name_without_extension));
		self.output_terminal.run_command("tesseract {0}.tif -l {1} batch.nochop makebox".format(item_name_without_extension,self.language));
			
		self.output_terminal.run_command("cp /tmp/batch.nochop.box {}.box".format(item_name_without_extension));
		
		# Wait for box file
		os.system("while [ ! -f {0}.box ]; do sleep 1; done".format(item_name_without_extension))

		boxeditor = BoxEditor()
		boxeditor.set_image(item)
		
		list_ = []
		
		for line in open(item_name_without_extension+".box"):
			spl = line.split(" ")
			list_.append((spl[0],int(spl[1]),int(spl[2]),int(spl[3]),int(spl[4]),int(spl[5])))
		
		# [("a",40,40,60,60,0),("a",80,90,100,60,110)]	
		boxeditor.set_list(list_)		
		boxeditor.show_all()
		
		def box_closed(*data):
			file = open(item_name_without_extension+".box","w")
			for item in boxeditor.get_list():
				file.write(' '.join([ str(x) for x in list(item)])+" 0\n")
			
			language = self.languages[self.combobox_language.get_active()]
			if (os.environ['HOME'] in language):
				self.output_terminal.run_command("tesseract {0}.tif {0}.box nobatch box.train -l {1} --tessdata-dir {2}".format(item_name_without_extension,language.split('-')[0],os.environ['HOME']));
				language = language.split('-')[0] #later used for copying 
			else:
				self.output_terminal.run_command("tesseract {0}.tif {0}.box nobatch box.train -l {1}".format(item_name_without_extension,language));
			self.output_terminal.run_command("unicharset_extractor {0}.box".format(item_name_without_extension));
			
			font = font_desc.split(" ")[0]
			italic = 0;
			if ("italic" in font_desc.lower()):
				italic = 1;
			
			bold = 0
			if ("bold" in font_desc.lower()):
				bold = 1;
				 
			self.output_terminal.run_command("echo '{0} {1} {2} 0 0 0' > font_properties".format(font,italic,bold));
			self.output_terminal.run_command("shapeclustering -F font_properties -U unicharset {0}.box.tr".format(item_name_without_extension));
			self.output_terminal.run_command("mftraining -F font_properties -U unicharset -O {0}.unicharset {0}.box.tr".format(item_name_without_extension));
			self.output_terminal.run_command("cntraining {0}.box.tr".format(item_name_without_extension));
			
			self.output_terminal.run_command("mv inttemp {0}.inttemp".format(item_name_without_extension));
			self.output_terminal.run_command("mv normproto {0}.normproto".format(item_name_without_extension));
			self.output_terminal.run_command("mv pffmtable {0}.pffmtable".format(item_name_without_extension));
			self.output_terminal.run_command("mv shapetable {0}.shapetable".format(item_name_without_extension));
			self.output_terminal.run_command("combine_tessdata {0}.".format(item_name_without_extension));

			if (os.path.isfile(os.environ['HOME']+"/tessdata/"+language+".traineddata")):
				dlg = dialog.Dialog(_("Edit filename to avoid replacing"),(_("Replace"), dialog.Dialog.BUTTON_ID_1,_("Give another filename"), dialog.Dialog.BUTTON_ID_2))
				entry = widget.Entry()
				dlg.add_widget_with_label(entry,_("File Name : "))
				entry.set_text(language)
				response = dlg.run()
				if(response == dialog.Dialog.BUTTON_ID_2):
					language = entry.get_text()
				dlg.destroy()
				self.output_terminal.run_command("cp {0}.traineddata {1}/tessdata/{2}.traineddata".format(item_name_without_extension,os.environ['HOME'],language));
			else:
				self.output_terminal.run_command("cp {0}.traineddata {1}/tessdata/{2}.traineddata".format(item_name_without_extension,os.environ['HOME'],language));

		boxeditor.connect_close_function(box_closed)
		

		
		


class BoxEditor(window.Window):
	def __init__(self):
		window.Window.__init__(self, title="Tesseract Trainer")
		self.imageview = imageview.ImageViewer()
		button_close = widget.Button(_("Close"))
		button_close.connect_function(self.close)
		box = containers.Box(containers.Box.VERTICAL)
		box.add(self.imageview)
		box.add(button_close)
		self.add(box)
		self.imageview.show()
		self.maximize()
	
	def set_image(self,image):
		self.imageview.load_image(image,[],imageview.ImageViewer.ZOOM_FIT)

	def set_list(self,list):
		image_height = self.imageview.get_height()
		list_ = []
		for item in list:
			width = item[3]-item[1]
			height = item[4]-item[2]
			y = image_height-item[2]-height
			list_.append((0,item[1],y,width,height,item[0]))
		
		self.imageview.set_list(list_)
	
	def get_list(self):
		image_height = self.imageview.get_height()
		list_ = []
		for item in self.imageview.get_list():
			y = image_height-(item[2]+item[4])
			end_y = y+item[4]
			end_x = item[1]+item[3]
			list_.append((item[5],item[1],y,end_x,end_y))
		return list_		
	
	def close(self,*data):
		self.destroy()
		


if __name__ == "__main__":
	win = TesseractTrainer(["/home/linux/Desktop/TrainingNet/test.png",
							"/home/linux/Desktop/TrainingNet/test3.png",
							"/home/linux/Desktop/test2.png",
							"/home/linux/Desktop/test3.png"])
	win.show()
	loop.start_main_loop()		