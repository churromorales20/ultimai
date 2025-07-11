import json
import re
import os
from utils.text_file_reader import read_raw_text_file

class ViewsSrvc:
  @classmethod  
  def render(cls, view_name, language):
    html = read_raw_text_file(f'views/{view_name}.html')
    lang_file = f'languages/{language}.json'

    if not os.path.isfile(lang_file):
      language = 'en'

    language_data = json.loads(read_raw_text_file(f'languages/{language}.json'))

    def replace_placeholder(match):
      key = match.group(1)

      if key in language_data:
        return language_data[key]
      else:
        print(f"Warning: Translation key '{key}' not found in JSON.")
        return match.group(0)

    translated_html = re.sub(r"\{\{Lang:([a-zA-Z0-9_]+)\}\}", replace_placeholder, html)
    return translated_html