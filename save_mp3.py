import os
import shutil
import zipfile
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

def extract_mp3_files(zip_file, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_file_name = os.path.splitext(os.path.basename(zip_file))[0]  # Get base name of ZIP file
            for file_info in zip_ref.infolist():
                file_name = file_info.filename
                if file_name.endswith('.mp3'):
                    output_path = os.path.join(output_folder, f"{zip_file_name}.mp3")
                    with zip_ref.open(file_info) as source, open(output_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    print(f"Extracted {file_name} to {output_path}")
    except zipfile.BadZipFile:
        print("File is not a valid ZIP file.")


def save_mp3(folder_path):
    mp3_folder = os.path.join(folder_path, 'audio')
    os.makedirs(mp3_folder, exist_ok=True)
    for file in os.listdir(folder_path):

        if file.endswith('.osz'):
            osz_file = os.path.join(folder_path, file)

            try:
                extract_mp3_files(osz_file, mp3_folder)

            except FileNotFoundError:
                print(f"File not found: {file}. Skipping...")
                continue



def main():
    osz_folder = './osu'
    save_mp3(osz_folder)

if __name__ == "__main__":
    main()
