# Welcome to tune-tools

A site to help you create and practice music.

**Tune-tools has the following functions:**

`Generate chords from input notes`

`Print a chord to an instrument fingerboard`

`Suggest scales for a chord`

`Print a scale to an instrument fingerboard`


# Dependencies

Flask is required to run the tune-tools GUI application install with the following if not already on your system.

```
pip install flask
```


# flask

Run tune-tools as a python flask application:

from `flask/`

run:

```
python3 app.py
```

# src

Source code for main tune-tools functionality


from `src/`

```
usage: tune-tools.py [-h] [-i str] [-k str] [-w] [-n] [-ins str] [-m str]

optional arguments:
  -h, --help            show this help message and exit
  -i str, --input str   Input txt file or string where each line is a space delimited list of notes to generate chords with, or chord name and symbol to get the notes of (default: )
  -k str, --keys str    Choice of sharp (#) or flat (b) to write note and chord labels with (default: b)
  -w, --weights         A boolean flag for using chord weights to less randomly select chords (default: False)
  -n, --notes_gen_chord
                        A boolean flag for whether to print the notes of chords created with create_chord_chart (default: False)
  -ins str, --instrument str
                        Type of instrument to print fingerboard of options: 'guitar', 'bass', 'ukulele', 'violin', 'mandolin' (default: )
  -m str, --main str    main function to 
  						1) generate a chord chart from notes -m "create_chord_chart", 
  						2) Get note from a chord -m "get_chord_notes", 
  						3) Suggest scales to play over chords "suggest_scales", 
                        4) Print a chord to an instrument fingerboard "print_chord_fingerboard", 
                        5) Print a scale to an instrument fingerboard "print_scale_fingerboard" 
                        (default: create_chord_chart)
```


Example runs

from `src/`

```
python3 tune-tools.py -i input/notes/1.txt -w -m 'create_chord_chart' -k b -n
python3 tune-tools.py -i input/chords/1.txt -w -m 'get_chord_notes' -k b
python3 tune-tools.py -i input/chords/1.txt -w -m 'suggest_scales' -k b
python3 tune-tools.py -i input/chords/2.txt -m 'print_chord_fingerboard' -ins 'guitar' -k b
python3 tune-tools.py -i input/scales/1.txt -m 'print_scale_fingerboard' -ins 'guitar' -k b
```


# Similar Resources

[Excel spreadsheet giving the diatonic chords for a mode / makam](https://docs.google.com/spreadsheets/d/1mPL_SlPrmCADD__exaGY3V1CzavXGyhJnh27C83vTfo/edit?usp=sharing)
