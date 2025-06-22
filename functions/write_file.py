import os

def write_file(working_directory, file_path, content):

    abs_working_directory = os.path.abspath(working_directory)
    tar_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not tar_file_path.startswith(abs_working_directory):
        return (f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory')

    try:

        with open(tar_file_path, "w") as file:
            file.write(content)
            return (f'Successfully wrote to "{file_path}" ({len(content)} characters written)')

    except OSError as e:
        return f'Error: An OS error occurred while processing "{file_path}": {e}'
    except Exception as e:
        return f'Error: An unexpected error occurred while processing "{file_path}": {e}'