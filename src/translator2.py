import pdfplumber
import google.generativeai as genai
import os

# *********************** CONFIGURATION ***********************
# Google AI Gemini API Key (Use environment variables!)
GOOGLE_API_KEY = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"

# Gemini AI Model for translation
TRANSLATION_MODEL = 'gemini-2.0-flash'  # or 'gemini-pro'

# Target language for translation
TARGET_LANGUAGE = "Spanish"

# Chunk size (number of characters per chunk)
CHUNK_SIZE = 4000
OVERLAP_SIZE = 200

# Number of pages to initially translate
INITIAL_PAGES = 8

# *********************** TRANSLATION FUNCTIONS ***********************
genai.configure(api_key=GOOGLE_API_KEY)

def translate_text(text, target_language=TARGET_LANGUAGE, model_name=TRANSLATION_MODEL):
    """Translates the text to the target language using the Gemini model."""
    model = genai.GenerativeModel(model_name)
    prompt = f"""Translate the following text to {target_language}.

    Original Text:
    {text}

    Translation:
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

# *********************** PDF READING FUNCTION ***********************
def read_pdf_pages(pdf_path, start_page=0, end_page=None):
    """Reads the content of specific pages from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            # Adjust end_page if it's None (read all pages)
            if end_page is None:
                end_page = len(pdf.pages)

            # Check if the start_page and end_page are valid
            if start_page < 0 or end_page > len(pdf.pages) or start_page >= end_page:
                raise ValueError("Invalid page range.")

            # Extract the text from the specified page range
            for i in range(start_page, end_page):
                page = pdf.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        return None
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# *********************** TEXT CHUNKING FUNCTION ***********************
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap_size=OVERLAP_SIZE):
    """Splits a large text into smaller overlapping chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

# *********************** FILE SAVING FUNCTION ***********************
def save_text_to_file(text, file_path, append=False):
    """Saves the text to a file.  Can append to existing file."""
    mode = 'a' if append else 'w'  # Use 'a' to append, 'w' to overwrite
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully saved text to file: {file_path}")
    except Exception as e:
        print(f"Error saving text to file: {e}")

# *********************** MAIN ORCHESTRATION FUNCTION ***********************
def translate_pdf_with_initial_pages(pdf_path, txt_path, initial_pages=INITIAL_PAGES):
    """Translates a PDF, translating the first `initial_pages` separately,
    and then translating the rest, and saves to a file."""

    # --- Translate the initial pages ---
    print(f"Translating the first {initial_pages} pages...")
    initial_text = read_pdf_pages(pdf_path, start_page=0, end_page=initial_pages)
    if initial_text:
        initial_chunks = chunk_text(initial_text)
        translated_initial_text = ""
        for i, chunk in enumerate(initial_chunks):
            print(f"Translating initial chunk {i+1} of {len(initial_chunks)}...")
            translated_chunk = translate_text(chunk)
            if translated_chunk:
                translated_initial_text += translated_chunk + "\n\n"
            else:
                print(f"Error translating initial chunk {i+1}.")
        save_text_to_file(translated_initial_text, txt_path, append=False) # Overwrite existing file
    else:
        print(f"Could not read the first {initial_pages} pages.")

    # --- Translate the remaining pages ---
    print(f"Translating the remaining pages (from page {initial_pages})...")
    remaining_text = read_pdf_pages(pdf_path, start_page=initial_pages, end_page=None) # Read until the end
    if remaining_text:
        remaining_chunks = chunk_text(remaining_text)
        translated_remaining_text = ""
        for i, chunk in enumerate(remaining_chunks):
            print(f"Translating remaining chunk {i+1} of {len(remaining_chunks)}...")
            translated_chunk = translate_text(chunk)
            if translated_chunk:
                translated_remaining_text += translated_chunk + "\n\n"
            else:
                print(f"Error translating remaining chunk {i+1}.")
        save_text_to_file(translated_remaining_text, txt_path, append=True) # Append to existing file
    else:
        print(f"Could not read the remaining pages (from page {initial_pages}).")

# *********************** EXAMPLE USAGE ***********************
if __name__ == "__main__":
    # Input PDF file name
    input_pdf_file = 'WFDF-Rules-of-Ultimate-2025-2028.pdf'
    # Output TXT file name
    output_txt_file = 'rules_translated_with_initial_pages.txt'

    translate_pdf_with_initial_pages(input_pdf_file, output_txt_file)