import os
import subprocess

def run_python_file(working_directory, file_path):

    abs_working_directory = os.path.abspath(working_directory)
    tar_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not tar_file_path.startswith(abs_working_directory):
        return (f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')

    if not os.path.isfile(tar_file_path):
        return (f'Error: File "{file_path}" not found.')
    
    if os.path.splitext(tar_file_path)[1].lower() != ".py":
        return (f'Error: "{file_path}" is not a Python file.')
    
    try:
        result = subprocess.run(
            ["python3", tar_file_path],  # Command to run
            cwd=abs_working_directory,   # Set working directory
            capture_output=True,         # Capture stdout and stderr
            text=True,                   # Return strings instead of bytes
            timeout=30                   # 30-second timeout
        )
    except subprocess.TimeoutExpired as e:
        return f"Error: executing Python file: {e}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
# result.stdout - standard output
# result.stdout - standard error output
# result.returncode - the exit code (0 means success)

# After running subprocess...
    output_parts = []

    if result.stdout:
        output_parts.append(f"STDOUT:\n{result.stdout}")
        
    if result.stderr:
        output_parts.append(f"STDERR:\n{result.stderr}")
        
    if result.returncode != 0:
        output_parts.append(f"Process exited with code {result.returncode}")

    if not output_parts:
        return "No output produced."
        
    return "\n".join(output_parts)
