def read_raw_text_file(file_path):
  try:
      with open(file_path, 'r', encoding='utf-8') as f:
          return f.read()
  except FileNotFoundError:
      print(f"Error: File '{file_path}' not found.")
  except Exception as e:
      print(f"Error al cargar las reglas desde el archivo: {e}")