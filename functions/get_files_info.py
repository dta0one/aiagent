import os

def get_files_info(working_directory, directory=None):
    if directory is None:
        directory = working_directory

    if is_outside_working_directory(working_directory, directory):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory')

    if not os.path.isdir(directory):
        return (f'Error: "{directory}" is not a directory')


#####
    try:
        # Get the list of all files and directories in the specified path
        entries = os.listdir(directory)

        # Build the string representation
        content_string = ""
        for entry in entries:
            entry_path = os.path.join(directory, entry)  # Get the full path

            # Check if it's a directory
            is_dir = os.path.isdir(entry_path)

            try:
                file_size = os.path.getsize(entry_path)
            except OSError:
                return f'Error: File not found or permission errors'

            content_string += f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}\n"

        return content_string

    except FileNotFoundError:
        return f'Error: "{directory}" is not a directory'
    #####


def is_outside_working_directory(working_directory, directory):
    directory = os.path.join(working_directory, directory)
    directory = os.path.abspath(directory)
    working_directory = os.path.abspath(working_directory)
    return not directory.startswith(working_directory)
