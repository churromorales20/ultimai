import pdfplumber
import google.generativeai as genai
import os
# If you are using a .env file to store your API key, include these lines:
# from dotenv import load_dotenv
# load_dotenv()

# *********************** CONFIGURATION ***********************
# Google AI Gemini API Key (Use environment variables!)
#GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_API_KEY = "AIzaSyDuz_7HUA9hfzkB6NU0tPEWvYG9uaKpnP8"

# Gemini AI Model for translation
TRANSLATION_MODEL = 'gemini-2.0-flash'  # or 'gemini-pro'

# Target language for translation
TARGET_LANGUAGE = "Spanish" # Change this if you want a different output language

# *********************** TRANSLATION FUNCTIONS ***********************
# Initialize the Gemini API key
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}. Make sure GOOGLE_API_KEY is set.")

def translate_text(text, target_language=TARGET_LANGUAGE, model_name=TRANSLATION_MODEL):
    """Translates the text to the target language using the Gemini model."""
    model = genai.GenerativeModel(model_name)
    
    # Create the translation prompt
    prompt = f"""Translate the following text to {target_language}. Maintain the original formatting as much as possible.

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
def read_pdf(pdf_path):
    """Reads the content of a PDF file and returns the text."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                # Extract text from the current page and add a newline
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n" 
        return full_text
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# *********************** FILE SAVING FUNCTION ***********************
def save_text_to_file(text, file_path):
    """Saves the text to a file."""
    try:
        # Use 'utf-8' encoding to support various languages and characters
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully saved text to file: {file_path}")
    except Exception as e:
        print(f"Error saving text to file: {e}")

# *********************** MAIN ORCHESTRATION FUNCTION ***********************
def translate_pdf_and_save(pdf_path, txt_path):
    """Reads a PDF, translates it using Gemini AI, and saves the translation to a text file."""
    print(f"Reading PDF: {pdf_path}...")
    pdf_text = read_pdf(pdf_path)

    if pdf_text:
        print("Translating text using Gemini AI...")
        translated_text = translate_text(pdf_text)

        if translated_text:
            print("Saving translated text...")
            save_text_to_file(translated_text, txt_path)
        else:
            print("Could not translate the PDF text.")
    else:
        print("Could not read the PDF or the PDF is empty.")

# *********************** EXAMPLE USAGE ***********************
if __name__ == "__main__":
    # Input PDF file name
    input_pdf_file = 'WFDF-Rules-of-Ultimate-2025-2028.pdf' # Replace with the path to your PDF file.
    
    # Output TXT file name
    output_txt_file = 'rules_translated_to_spanish.txt'

    print("--- Starting PDF Translation Process ---")
    translate_pdf_and_save(input_pdf_file, output_txt_file)
    print("--- Process Finished ---")