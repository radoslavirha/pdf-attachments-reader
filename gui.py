from glob import glob
from tkinter import filedialog
import logging
import os
import PyPDF2
import shutil
import tkinter as tk

module_logger = logging.getLogger(__name__)

class TextHandler(logging.StreamHandler):
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self) # initialize parent
        self.textctrl = textctrl

    def emit(self, record):
        msg = self.format(record)
        self.textctrl.config(state="normal")
        self.textctrl.insert("end", msg + "\n")
        self.flush()
        self.textctrl.config(state="disabled")

def extract_attachments(pdf_path, output_dir):
    '''
    Retrieves the file attachments of the PDF as a dictionary of file names
    and the file data as a bytestring.

    :return: dictionary of filenames and bytestrings
    '''
    reader = PyPDF2.PdfReader(pdf_path)
    attachments = {}
    #First, get those that are pdf attachments
    catalog = reader.trailer['/Root']
    if '/Names' in catalog:
      if '/EmbeddedFiles' in catalog['/Names']:
          fileNames = catalog['/Names']['/EmbeddedFiles']['/Names']
          for f in fileNames:
              if isinstance(f, str):
                  name = f
                  dataIndex = fileNames.index(f) + 1
                  fDict = fileNames[dataIndex].getObject()
                  fData = fDict['/EF']['/F'].getData()
                  attachments[name] = fData

    # #Next, go through all pages and all annotations to those pages
    # #to find any attached files
    for pagenum in range(0, len(reader.pages)):
        page_object = reader.pages[pagenum]
        if '/Annots' in page_object:
            for annot in page_object['/Annots']:
                annotobj = annot.get_object()
                if annotobj['/Subtype'] == '/FileAttachment':
                    fileobj = annotobj['/FS']
                    attachments[fileobj['/F']] = fileobj['/EF']['/F'].get_data()
    for fName, fData in attachments.items():
      module_logger.info(f"Saving attachment: {fName}")
      with open(os.path.join(output_dir, fName), 'wb') as outfile:
        outfile.write(fData)

def find_pdfs(dr, ext):
    return glob(os.path.join(dr,"*.{}".format(ext)))

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        read_folder(folder_path)

def read_folder(directory):
    module_logger.info(f"Selected directory: {directory}")
    attachments = os.path.join(directory, 'attachments')
    module_logger.info(f"Attachments folder: {attachments}")

    try:
        shutil.rmtree(attachments)
    except:
        module_logger.info("Deletion of attachments folder failed")
    else:
        module_logger.info("Attachments folder deleted")

    try:
        os.mkdir(attachments)
    except:
        module_logger.info("Creation of attachments folder failed")
        exit()
    else:
        module_logger.info("Attachments folder created")

    pdfs = find_pdfs(directory, "pdf")

    for pdf in pdfs:
      module_logger.info('Found pdf: ' + pdf)
      extract_attachments(pdf, attachments)

def close():
    window.destroy()

if __name__ == "__main__":
    # Create the main window
    window = tk.Tk()
    window.title('Extraktor příloh PDF')

    # Create a button to select the folder
    select_button = tk.Button(window, text="Vyberte složku s pdf soubory", command=select_folder)
    select_button.grid(column=0, row=1)

    mytext = tk.Text(window, state="disabled")
    mytext.grid(column=0, row=2)

    close_button = tk.Button(window, text="Zavřít", command=close)
    close_button.grid(column=0, row=3)

    stderrHandler = logging.StreamHandler()  # no arguments => stderr
    module_logger.addHandler(stderrHandler)
    guiHandler = TextHandler(mytext)
    module_logger.addHandler(guiHandler)
    module_logger.setLevel(logging.INFO)   

    # Start the main event loop
    window.mainloop()