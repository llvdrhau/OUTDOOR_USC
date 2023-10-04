import os


def delete_all_files_in_directory(directory_path):
    """
    Delete all files in the specified directory.

    Parameters:
        directory_path (str): The path of the directory whose files should be deleted.

    Returns:
        None
    """
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Check if the path is a directory
    if not os.path.isdir(directory_path):
        print(f"{directory_path} is not a directory.")
        return

    # Loop through all files in the directory and remove them
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # Check if it's a file
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File {filename} deleted.")
            except Exception as e:
                print(f"Error occurred while deleting file {filename}: {str(e)}")
