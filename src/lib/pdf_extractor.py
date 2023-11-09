from typing import List, Tuple
from lib.utils import decimal_to_rgb
import fitz
import csv
import os


class TextSpan:
    """
    TextSpan stores a span of text with its informations
    """
    def __init__(self,
                 text: str,
                 pos: Tuple[float, float],
                 font_name: str,
                 font_size: float,
                 color: int,
                 flags: int,
                 rotate: int) -> None:
        self.text = text
        self.pos = pos
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.flags = self.flags_decomposer(flags)
        self.rotate = rotate

    def flags_decomposer(self, flags: int):
        """Make font flags human readable."""
        l = []
        if flags & 2 ** 0:
            l.append("superscript")
        if flags & 2 ** 1:
            l.append("italic")
        if flags & 2 ** 2:
            l.append("serifed")
        else:
            l.append("sans")
        if flags & 2 ** 3:
            l.append("monospaced")
        else:
            l.append("proportional")
        if flags & 2 ** 4:
            l.append("bold")
        return l

    def __repr__(self) -> str:
        return f"text: {self.text}, pos: {self.pos}, font_name: {self.font_name}, font_size: {self.font_size}, color: {self.color}, rotate: {self.rotate}"


class PdfExtractor:
    def __init__(self, pdf_file_path: str) -> None:
        self.file_path = pdf_file_path
        self.doc: fitz.Document = fitz.open(pdf_file_path)
        self.text_transforms = []

    def add_text_transform(self, text_transform):
        self.text_transforms.append(text_transform)

    def extract_fonts(self):
        fonts = []
        for page in self.doc:
            for font in page.get_fonts():
                fonts.append(font)

        return fonts

    def extract_text_spans(self) -> List[List[TextSpan]]:
        """
        Return all text spans of each page
        """
        result = []
        for page in self.doc: # iterate the document pages
            blocks = page.get_text("dict", flags=11)["blocks"]
            text_elements: List[TextSpan] = []
            for b in blocks:  # iterate through the text blocks
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:
                        text_elements.append(TextSpan(s["text"], s["origin"], s["font"], s["size"], s["color"],s["flags"], 0))

            result.append(text_elements)

        return result


    def text_spans_to_csv(self, text_spans: List[List[TextSpan]], file_path) -> None:
        header = ["page", "text", "font_name", "font_size", "color", "flags"]

        with open(file_path, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write the data
            for i, page in enumerate(text_spans):
                for text_span in page:
                    writer.writerow([i + 1, text_span.text, text_span.font_name, text_span.font_size, text_span.color, ",".join(text_span.flags)])
        print(f"Extracted texts to file: {file_path}")

    def extract_images(self, folder: str):
        for page_index in range(len(self.doc)): # iterate over pdf pages
            page = self.doc[page_index] # get the page
            image_list = page.get_images()

            for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(self.doc, xref) # create a Pixmap

                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save("%s/page_%s-image_%s.png" % (folder, page_index, image_index)) # save the image as png
                pix = None
        print(f"Extracted all images to folder: {folder}")

    def export_pdf(self, file_path: str, text_els: List[List[TextSpan]]):
        doc = fitz.open()

        for page_idx, text_els_per_page in enumerate(text_els):
            page = doc.new_page()

            for text_el in text_els_per_page:
                transformed_text_el = text_el
                for text_transform in self.text_transforms:
                    transformed_text_el = text_transform(transformed_text_el)

                p = fitz.Point(transformed_text_el.pos[0], transformed_text_el.pos[1])

                page.insert_text(p,  # bottom-left of 1st char
                                 transformed_text_el.text,
                                 # fontname = transformed_text_el.font_name,
                                 fontname = "tiro",
                                 fontsize = transformed_text_el.font_size,
                                 rotate = transformed_text_el.rotate,
                                 color = decimal_to_rgb(transformed_text_el.color)
                             )
        doc.save(file_path)



class PdfExtractor:
    def __init__(self, pdf_file_path: str) -> None:
        self.file_path = pdf_file_path
        self.doc: fitz.Document = fitz.open(pdf_file_path)
        self.text_transforms = []

    def add_text_transform(self, text_transform):
        self.text_transforms.append(text_transform)

    def extract_fonts(self):
        fonts = []
        for page in self.doc:
            for font in page.get_fonts():
                fonts.append(font)

        return fonts

    def extract_text_spans(self) -> List[List[TextSpan]]:
        """
        Return all text spans of each page
        """
        result = []
        for page in self.doc: # iterate the document pages
            blocks = page.get_text("dict", flags=11)["blocks"]
            text_elements: List[TextSpan] = []
            for b in blocks:  # iterate through the text blocks
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:
                        text_elements.append(TextSpan(s["text"], s["origin"], s["font"], s["size"], s["color"],s["flags"], 0))

            result.append(text_elements)

        return result


    def text_spans_to_csv(self, text_spans: List[List[TextSpan]], file_path) -> None:
        header = ["page", "text", "font_name", "font_size", "color", "flags"]

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write the data
            for i, page in enumerate(text_spans):
                for text_span in page:
                    writer.writerow([i + 1, text_span.text, text_span.font_name, text_span.font_size, text_span.color, ",".join(text_span.flags)])
        print(f"Extracted texts to file: {file_path}")

    def extract_images(self, folder: str):
        if not os.path.exists(folder):
            os.mkdir(folder)

        for page_index in range(len(self.doc)): # iterate over pdf pages
            page = self.doc[page_index] # get the page
            image_list = page.get_images()

            for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(self.doc, xref) # create a Pixmap

                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save("%s/page_%s-image_%s.png" % (folder, page_index, image_index)) # save the image as png
                pix = None
        print(f"Extracted all images to folder: {folder}")

    def export_pdf(self, file_path: str, text_els: List[List[TextSpan]]):
        doc = fitz.open()

        for page_idx, text_els_per_page in enumerate(text_els):
            page = doc.new_page()

            for text_el in text_els_per_page:
                transformed_text_el = text_el
                for text_transform in self.text_transforms:
                    transformed_text_el = text_transform(transformed_text_el)

                p = fitz.Point(transformed_text_el.pos[0], transformed_text_el.pos[1])

                page.insert_text(p,  # bottom-left of 1st char
                                 transformed_text_el.text,
                                 # fontname = transformed_text_el.font_name,
                                 fontname = "tiro",
                                 fontsize = transformed_text_el.font_size,
                                 rotate = transformed_text_el.rotate,
                                 color = decimal_to_rgb(transformed_text_el.color)
                             )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        doc.save(file_path)


