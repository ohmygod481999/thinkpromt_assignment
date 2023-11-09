from lib.pptx_translator import PptxExtractor

if __name__ == "__main__":
    PRESENTATION_PATH = "./documents/Networking.pptx"
    TRANSLATED_PRESENTATION_PATH = "./out/task4/Networking-vi-translated.pptx"
    pptxExtractor = PptxExtractor(PRESENTATION_PATH)
    pptxExtractor.save_texts_to_files("./out/task4/presentation_out_text.txt")
    pptxExtractor.extract_images("./out/task4/presentation_images")

    pptxExtractor.translate(TRANSLATED_PRESENTATION_PATH)
