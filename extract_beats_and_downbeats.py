import os
import shutil
import zipfile
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

def get_mp3_duration(file_path):
    audio = MP3(file_path)
    duration_in_seconds = audio.info.length
    duration_in_milliseconds = int(duration_in_seconds * 1000)
    return duration_in_milliseconds

def get_mp3_duration_safe(file_path):
    try:
        audio = MP3(file_path)
        duration_in_seconds = audio.info.length
        duration_in_milliseconds = int(duration_in_seconds * 1000)
        return duration_in_milliseconds
    except HeaderNotFoundError:
        print(f"Skipping file {file_path}: HeaderNotFoundError")
        return None

def frange(start, stop, step):
    while start < stop:
        yield start
        start += step

def save_audio_with_original_name(file_path, output_folder):
    # Get original file name
    file_name = os.path.basename(file_path)
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    # Create output file path
    output_file_path = os.path.join(output_folder, file_name)
    # Copy MP3 file to output folder
    with open(file_path, 'rb') as src_file, open(output_file_path, 'wb') as dest_file:
        dest_file.write(src_file.read())
    return output_file_path

def extract_beats_and_downbeats(osu_file, dur):
    beats = []
    downbeats = []
    current_time = 0


    with open(osu_file, 'r', encoding='utf-8') as f:
    # Your existing code for reading the file goes here
        timing_points_started = False
        mpb = 0.0  # Initialize inherited mpb
        lines = [line.strip() for line in f if line.strip()]
        for line in lines:
            #print(line)
            if line == '[TimingPoints]':
                timing_points_started = True
                continue

            if timing_points_started:
                if line.startswith('['):
                    break  # End of timing points section
                parts = line.split(',')
                #print(parts)
                time = float(parts[0])  # Time
                #print(time)
                
                meter = int(parts[2])    # Meter
                uninherited = int(parts[6])  # Check if timing point is uninherited
                if uninherited:
                    mpb = float(parts[1])    # Beat length or slider velocity multiplier

                if current_time == 0:
                    current_time = time

                else:
                
                    beats.extend(frange(current_time, time, mpb))
                    downbeats.extend(frange(current_time, time, mpb * meter))
            
                    current_time = time

        beats.extend(frange(current_time, dur, mpb))
        downbeats.extend(frange(current_time, dur, mpb * meter))


    return beats, downbeats



def extract_beats_downbeats_and_mp3(osz_file):
    beats = []
    downbeats = []
    dur = 0

    try:
        with zipfile.ZipFile(osz_file, 'r') as zip_ref:
            # Extract the .osu file and find mp3 files
            for file_info in zip_ref.infolist():
                file_name = file_info.filename
                if file_name.endswith('.osu'):
                    zip_ref.extract(file_name)
                    osu_file = file_name
                elif file_name.endswith('.mp3'):
                    zip_ref.extract(file_name)
                    dur = get_mp3_duration_safe(file_name)
            
            # Process the .osu file to extract beats and downbeats
            if osu_file and dur != 0 and dur is not None:
                beats, downbeats = extract_beats_and_downbeats(osu_file, dur)
    except zipfile.BadZipFile:
        print("File is not a valid ZIP file.")

    return beats, downbeats

def process_osz_folder(folder_path):
    beats_and_downbeats_folder = os.path.join(folder_path, 'beats_and_downbeats')
    mp3_folder = os.path.join(folder_path, 'audio')

    os.makedirs(beats_and_downbeats_folder, exist_ok=True)
    os.makedirs(mp3_folder, exist_ok=True)

    for file in os.listdir(folder_path):
        if file.endswith('.osz'):
            osz_file = os.path.join(folder_path, file)
            song_name = os.path.splitext(file)[0]

            try:
                beats, downbeats = extract_beats_downbeats_and_mp3(osz_file)

                # Save beats and downbeats
                beats_file = os.path.join(beats_and_downbeats_folder, song_name + '_beats.txt')
                downbeats_file = os.path.join(beats_and_downbeats_folder, song_name + '_downbeats.txt')
                with open(beats_file, 'w') as f:
                    for beat in beats:
                        f.write(str(beat) + '\n')
                with open(downbeats_file, 'w') as f:
                    for downbeat in downbeats:
                        f.write(str(downbeat) + '\n')


            except FileNotFoundError:
                print(f"File not found: {file}. Skipping...")
                continue

def main():
    osz_folder = './osu'
    process_osz_folder(osz_folder)

if __name__ == "__main__":
    main()
