import os

def get_file_content(working_directory, file_path):

    try:
        abs_working_directory = os.path.abspath(working_directory)
        tar_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
        if not tar_file_path.startswith(abs_working_directory):
            return (f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
    
        if not os.path.isfile(tar_file_path):
            return (f'Error: File not found or is not a regular file: "{file_path}"')

        max_size = 10000

        with open(tar_file_path, "r") as file:
        #with open(tar_file_path, "r", encoding='utf-8') as f: # Specify encoding for text files
            file_content_string = file.read(max_size)

            if os.path.getsize(tar_file_path) > max_size:
                file_content_string += (f'[...File "{file_path}" truncated at {max_size} characters]')
            
            return file_content_string

#    except FileNotFoundError:
#        return f'Error: File not found: "{file_path}"'
    except PermissionError:
        return f'Error: Permission denied to access: "{file_path}"'
#    except IsADirectoryError:
#        return f'Error: Path is a directory, not a file: "{file_path}"'
    except UnicodeDecodeError:
        return f'Error: Could not decode file content with UTF-8 encoding: "{file_path}"'
    except OSError as e: # Catch other potential OS errors
        return f'Error: An OS error occurred while processing "{file_path}": {e}'
    except Exception as e: # Catch any other unexpected exceptions
        return f'Error: An unexpected error occurred while processing "{file_path}": {e}'
