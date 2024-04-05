import fitz

def main():
    doc = fitz.open('sample.pdf')
    redact_document(doc)
    doc.save("test.pdf")

def redact_document(doc:fitz.Document):
    fitz.TOOLS.set_small_glyph_heights(True)

    for page in doc:
        redact_page(page)

def redact_page(page:fitz.Page):
    if is_unexpected_format(page):
        redact_whole_page(page)
    else:
        redact_social_security_number(page)
        redact_address(page)

    page.apply_redactions()

def is_unexpected_format(page:fitz.Page):
    header_line = "BULLETIN DE SALAIRE"
    return not page.search_for(header_line)

def redact_whole_page(page:fitz.Page):
    print(f"Page {page.number+1} has an unexpected format, and will be fully redacted")
    page.add_redact_annot(page.mediabox)
    return True

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
        raise Exception(f"Could not find SS number for page {page.number} (looking for: '{search_text}')")
    if len(instances) > 1:
        raise Exception(f"Found multiple regions with text '{search_text}' on page {page.number}")

    rect = instances[0]

    # Modify the rect to get the value instead of the field label
    rect[0] = rect[2] + 3
    rect[2] = rect[0] + field_width

    return rect

main()