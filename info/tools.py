from pathlib import Path
from django.utils.safestring import mark_safe

def open_text(txt):
    """
    Open text file and determine which html element the lines should be displayed as.

    txt = the name of the file to be read

    Returns a list of tuples, where each tuple consist of text and type of text.
    """

    data_folder = Path('static/info_txt/')
    file_to_open = data_folder / txt
    f = open(file_to_open, 'r')
    file_text = f.read()
    text = []

    sections = file_text.split("\n\n")

    for section in sections:

        if section.find('#h1 ') == 0: # header level 1
            text.append((section[4:],'h1'))
        elif section.find('#h2 ') == 0: # header level 2
            text.append((section[4:],'h2'))
        elif section.find('#h3 ') == 0: # header level 3
            text.append((section[4:],'h3'))
        elif section.find('* ') == 0: # list item
            text.append((section[2:],'li'))
        elif section.find('#5stars') == 0:  # Special case, marks where five stars should be diplayed
            text.append(('<i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i>','5stars'))
        else: # regular paragraph
            text.append((section,'p'))

    return text
