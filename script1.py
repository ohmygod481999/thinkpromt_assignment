from lib.pdf_extractor import PdfExtractor, TextSpan

if __name__ == "__main__":
    PDF_FILE_PATH = "./documents/pdf_mock_file.pdf"
    IMAGE_FOLDER = "./out/task123/pdf_exported_images"

    extractor = PdfExtractor(PDF_FILE_PATH)

    # 1, 2. Extract all text with its details and images from the provided PDF/DOCX
    text_els = extractor.extract_text_spans()
    extractor.text_spans_to_csv(text_els, "./out/task123/extracted_texts.csv")
    extractor.extract_images(IMAGE_FOLDER)

    
    # 3. Convert the text of each extracted paragraph to UPPERCASE. Subsequently, compile all the UPPERCASE paragraphs into a new PDF/DOCX
    def to_upper_case(text_span: TextSpan):
        text_span.text = text_span.text.upper()
        return text_span
    def reduce_font_size(text_span: TextSpan):
        text_span.font_size = text_span.font_size - 3
        return text_span

    extractor.add_text_transform(to_upper_case)
    extractor.add_text_transform(reduce_font_size)
    extractor.export_pdf("./out/task123/pdf_mock_file_uppercase.pdf", text_els)
