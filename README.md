# PDF attachments reader

It'll automatically create `attachments` folder in chosen directory (GUI)

```sh
{chosen directory}
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

## Prerequisites

Python 3

## Install

```sh
pip3 install pyinstaller
pip3 install -r requirements.txt
```

## Build GUI

### Linux/Mac

`pyinstaller --onefile --noconsole --clean --add-data 'font:font' --name pdf-extracter gui.py`

### Windows

`python -m PyInstaller --onefile --noconsole --clean --add-data 'font;font' --name pdf-extracter gui.py`

## Run as script

`python3 gui.py`
