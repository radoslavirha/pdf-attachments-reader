# pdf-reader-roman

## Prerequisites

Python 3

## Install

`pip3 install -r requirements.txt`

## Run script

There should be only relevant pdfs in folder, otherwise it'll extract all the attachments from all the files.

It'll automatically create `attachments`

`python3 reader.py {absolute path to directory with pdfs}`

E.g. `python3 reader.py /Users/radoslavirha/Downloads/pdf`

```
{absolute path to directory with pdfs}
├── 1040020890_DSPSg_TZ_signed.pdf
├── 1040020890_DSPSg_KO-1.pdf
└── attachments (automatically created)
    ├── *.pdf
    ├── *.gml
    ├── *.txt
    ├── *.xlsx
    ├── *.xml
    └── *.dgn
```
