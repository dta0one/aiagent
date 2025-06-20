import os

def get_files_info(working_directory, directory=None):
    abs_working_directory = os.path.abspath(working_directory)
    tar_directory = abs_working_directory

    if directory:
        tar_directory = os.path.abspath(os.path.join(working_directory, directory))
    
    if not tar_directory.startswith(abs_working_directory):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')

    if not os.path.isdir(tar_directory):
        return (f'Error: "{directory}" is not a directory')

    try:
        content_string = ""
        for entry in os.listdir(tar_directory):
            entry_path = os.path.join(tar_directory, entry)
            is_dir = os.path.isdir(entry_path)
            try:
                file_size = os.path.getsize(entry_path)
            except OSError:
                return f'Error: File not found or permission errors'

            content_string += f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}\n"
        return content_string
    except FileNotFoundError:
        return f'Error: "{directory}" is not a directory'