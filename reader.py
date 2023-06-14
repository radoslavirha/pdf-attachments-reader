import PyPDF2
import sys
import os
import shutil
from glob import glob

directory = sys.argv[1]
attachments = os.path.join(directory, 'attachments')

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
      print ("Saving attachment: %s" % fName)
      with open(os.path.join(output_dir, fName), 'wb') as outfile:
        outfile.write(fData)

def find_pdfs(dr, ext):
    return glob(os.path.join(dr,"*.{}".format(ext)))

print("Attachments folder: %s" % attachments)

try:
    shutil.rmtree(attachments)
except:
    print ("Deletion of attachments folder failed")
else:
    print ("Attachments folder deleted")

try:
    os.mkdir(attachments)
except:
    print ("Creation of attachments folder failed")
    exit()
else:
    print ("Attachments folder created")

pdfs = find_pdfs(directory, "pdf")

for pdf in pdfs:
  print('Found pdf: ' + pdf)
  extract_attachments(pdf, attachments)
