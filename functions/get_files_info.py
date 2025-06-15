import os

def get_files_info(working_directory, directory=None):
    if not os.path.isdir(directory):
        return (f'Error: "{directory}" is not a directory')

    if is_outside_working_directory(working_directory, directory):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    

def is_outside_working_directory(working_directory, directory):
    directory = os.path.abspath(directory)
    working_directory = os.path.abspath(working_directory)
    return not directory.startswith(working_directory)
