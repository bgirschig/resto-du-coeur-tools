import fitz
import os
import argparse
import pathlib

current_filename = None

def main():
    parser = argparse.ArgumentParser(
        prog="Redactor",
        description="Redact pdf payslips",
        usage="python main.py --input ~/Downloads/*.pdf --output ~/Downloads/redacted"
    )
    parser.add_argument("--input", nargs='+', help="input file(s) to be redacted")
    parser.add_argument("--output", help="path to the directory where the files will be saved")
    parser.add_argument("--suffix", default="_redacted", help="adds a suffix to the end of the generated filenames")
    args = parser.parse_args()

    for file in args.input:
        redact_file(file, args.output, args.suffix)

def redact_file(path:str, output_dir:str, filename_suffix:str=""):
    global current_filename
    current_filename = os.path.basename(path)

    doc = fitz.open(path)
    redact_document(doc)
    
    name, extension = os.path.splitext(current_filename)
    output_filename = os.path.join(output_dir, f"{name}{filename_suffix}{extension}")
    pathlib.Path(os.path.dirname(output_filename)).mkdir(parents=True, exist_ok=True)
    doc.save(output_filename)

def redact_document(doc:fitz.Document):
    fitz.TOOLS.set_small_glyph_heights(True)

    for page in doc:
        redact_page(page)

def redact_page(page:fitz.Page):
    if is_unexpected_format(page):
        print(f"{current_filename}#{page.number+1} has an unexpected format, and will not be redacted")
        # redact_whole_page(page)
    else:
        redact_social_security_number(page)
        redact_address(page)

    page.apply_redactions()

def is_unexpected_format(page:fitz.Page):
    header_line = "BULLETIN DE SALAIRE"
    return not page.search_for(header_line)

def redact_whole_page(page:fitz.Page):
    page.add_redact_annot(page.mediabox)

def redact_address(page:fitz.Page):
    # This is kinda hard to detect programmatically,
    # so we'll just use a harcoded rect for now
    address_x = 270
    address_y = 90
    address_width=260
    address_height=100
    address_rect = (address_x,address_y,address_x+address_width,address_y+address_height)
    
    page.add_redact_annot(address_rect)

def redact_social_security_number(page:fitz.Page):
    rect = get_social_security_number_rect(page)
    page.add_redact_annot(rect)

def get_social_security_number_rect(page:fitz.Page):
    search_text = "N° SS :"
    field_width = 120

    instances = page.search_for(search_text)

    if not instances:
        raise Exception(f"{current_filename}#{page.number} Could not find SS number. (looking for: '{search_text}')")
    if len(instances) > 1:
        raise Exception(f"{current_filename}#{page.number} Found multiple regions with text '{search_text}' on page {page.number}")

    rect = instances[0]

    # Modify the rect to get the value instead of the field label
    rect[0] = rect[2] + 3
    rect[2] = rect[0] + field_width

    return rect

if __name__ == "__main__":
    main()