from fpdf import FPDF
from glob import glob
from tkinter import filedialog
import logging
import os
import pypdf
import re
import shutil
import sys
import tkinter as tk

module_logger = logging.getLogger(__name__)

attachments_directory = 'attachments'
fontPath = os.path.join('font/', 'DejaVuSans.ttf')

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('Running in a PyInstaller bundle')
    fontPath = os.path.join(sys._MEIPASS, fontPath)
else:
    print('Running in a normal Python process')

merge_attachments_list = [
    r'.*_DSPSg_TZ_K_signed\.pdf$',
    r'.*_DSPSg_SS_signed\.pdf$',
    r'.*_DSPSg_POP\.txt$',
    r'.*_DSPSg_TISK1.*signed\.pdf$'
]

pull_attachments_list = [
    r'.*_DSPSg_POP\.txt$',
    r'.*_DSPSg_SS\.txt$'
]

class TextHandler(logging.StreamHandler):
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self) # initialize parent
        self.textctrl = textctrl

    def emit(self, record):
        msg = self.format(record)
        self.textctrl.config(state='normal')
        self.textctrl.insert('end', msg + '\n')
        self.flush()
        self.textctrl.config(state='disabled')

def rm_attachments_dir(directory):
    try:
        shutil.rmtree(directory)
    except:
        module_logger.info('Deletion of attachments folder failed!')
    else:
        module_logger.info('Attachments folder deleted')

def filter_attachments(attachments_list, patterns):
    filtered = []

    for pattern in patterns:
        filter_list = list(filter(lambda x: re.search(pattern, x), attachments_list))
        if len(filter_list) > 0:
            filtered.extend(filter_list)

    return filtered

def convert_txt_to_pdf(attachment):
    try:
        module_logger.info(f'Converting txt attachment to pdf: {attachment}')
        txt = open(attachment, 'rb').read().decode('Windows-1250')

        pdf_file = attachment.replace('.txt', '.pdf')
        pdf = FPDF()
        pdf.add_page()
        module_logger.info(f'Unicode font path: {fontPath}')
        pdf.add_font('DejaVu', '', fontPath, uni=True)
        pdf.set_font('DejaVu', '', 10)
        pdf.write(8, txt.replace('\t', '    '))
        pdf.output(pdf_file)

        return pdf_file
    except Exception as e:
        module_logger.info('Converting .txt to .pdf failed!')
        module_logger.info(e)

def merge_attachments(attachments_list, directory):
    module_logger.info(f'Merging attachments...')

    filtered_attachmentsList = filter_attachments(attachments_list, merge_attachments_list)

    merger = pypdf.PdfWriter()

    try:
        for attachment in filtered_attachmentsList:
            module_logger.info(f'Found attachment for merging to single pdf: {attachment}')

            if attachment.endswith('.pdf'):
                merger.append(open(attachment, 'rb'))
            elif attachment.endswith('.txt'):
                pdf = convert_txt_to_pdf(attachment)
                merger.append(open(pdf, 'rb'))

        # Write to an output PDF document
        dsps = os.path.join(directory, 'dsps.pdf')
        module_logger.info(f'Creating: {dsps}')
        output = open(dsps, 'wb')
        merger.write(output)

        # Close File Descriptors
        merger.close()
        output.close()
    except Exception as e:
        module_logger.info('Merging attachments failed!')
        module_logger.info(e)

def pull_attachments(attachments_list, directory):
    module_logger.info(f'Pulling out attachments...')

    filtered_attachmentsList = filter_attachments(attachments_list, pull_attachments_list)
    
    try:
        for attachment in filtered_attachmentsList:
            module_logger.info(f'Found attachment for pulling out: {attachment}')
            newDir = os.path.dirname(attachment).replace(attachments_directory, '')
            attachmentFile = os.path.basename(attachment)
            newPath = os.path.join(newDir, attachmentFile)
            module_logger.info(f'Copying attachment to: {newPath}')
            shutil.copyfile(attachment, newPath)
            xyz = newPath.replace('.txt', '.xyz')
            module_logger.info(f'Copying attachment to: {xyz}')
            shutil.copyfile(newPath, xyz)
    except Exception as e:
        module_logger.info('Pulling attachments failed!')
        module_logger.info(e)

def extract_attachments(pdf_path, output_dir):
    '''
    Retrieves the file attachments of the PDF as a dictionary of file names
    and the file data as a bytestring.

    :return: dictionary of filenames and bytestrings
    '''
    reader = pypdf.PdfReader(pdf_path)
    attachments = {}
    attachments_list = []
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
      attachmentPath = os.path.join(output_dir, fName)
      attachments_list.append(attachmentPath)
      module_logger.info(f'Saving attachment: {fName}')
      with open(attachmentPath, 'wb') as outfile:
        outfile.write(fData)

    return attachments_list

def find_pdfs(dr, ext):
    return glob(os.path.join(dr,'*.{}'.format(ext)))

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        read_folder(folder_path)

def read_folder(directory):
    module_logger.info(f'Selected directory: {directory}')
    attachmentsPath = os.path.join(directory, attachments_directory)
    module_logger.info(f'Attachments folder: {attachmentsPath}')

    rm_attachments_dir(attachmentsPath)

    try:
        os.mkdir(attachmentsPath)
    except:
        module_logger.info('Creation of attachments folder failed!')
        exit()
    else:
        module_logger.info('Attachments folder created')

    pdfs = find_pdfs(directory, 'pdf')

    attachments_list = []

    for pdf in pdfs:
      module_logger.info('Found pdf: ' + pdf)
      attachments_list.extend(extract_attachments(pdf, attachmentsPath))

    merge_attachments(attachments_list, directory)
    pull_attachments(attachments_list, directory)
    # rm_attachments_dir(attachmentsPath)

    module_logger.info('Done!')
    module_logger.info('--------------------------------------')

def close():
    window.destroy()

if __name__ == '__main__':
    # Create the main window
    window = tk.Tk()
    window.title('Extraktor příloh PDF')

    # Create a button to select the folder
    select_button = tk.Button(window, text='Vyberte složku s pdf soubory', command=select_folder)
    select_button.grid(column=0, row=1)

    mytext = tk.Text(window, state='disabled')
    mytext.grid(column=0, row=2)

    close_button = tk.Button(window, text='Zavřít', command=close)
    close_button.grid(column=0, row=3)

    stderrHandler = logging.StreamHandler()  # no arguments => stderr
    module_logger.addHandler(stderrHandler)
    guiHandler = TextHandler(mytext)
    module_logger.addHandler(guiHandler)
    module_logger.setLevel(logging.INFO)   

    # Start the main event loop
    window.mainloop()