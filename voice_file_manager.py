import subprocess
import time
import speech_recognition as sr
import pyautogui
import pyttsx3
import PyPDF2
import fitz # pip install PyMuPDF
import os
import shutil
import nltk
nltk.download('punkt')
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from PIL import Image
import pygame


LANGUAGE = "english"
SENTENCES_COUNT = 3  # Number of sentences in the summary
current_file = None
img = None    
paused = False   # Global variable to track the video playback status
current_directory = os.getcwd()  # Get the current working directory
tts = pyttsx3.init()
pygame.mixer.init()  # Initialize Pygame mixer for audio and video


def initialize_tts():
    tts = pyttsx3.init()
    tts.setProperty('rate', 150)  # Adjust the speed (rate) of the speech
    return tts


def listen_for_command():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening..., say goodbye to exit !")
            audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("Command:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            tts.say("Sorry, I didn't understand that.")
            tts.runAndWait()
        except sr.RequestError:
            print("Sorry, Please try again later.")
            tts.say("Sorry, Please try again later.")
            tts.runAndWait()


def create_file(filename):
    global current_directory
    try:
        filepath = os.path.join(current_directory, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w'):
                print(filename, "created successfully.")
                tts.say(filename)
                tts.say("created successfully")
                tts.runAndWait()
        else:
            print(filename, "already exists.")
            tts.say("filename already exists.")
            tts.runAndWait()
    except Exception as e:
        print("error creating file.")
        tts.say("file is not created.")
        tts.runAndWait()


def rename_file(old_filename, new_filename):
    global current_file  # Declare current_file as global

    try:
        # Add .txt extension if not present in old filename
        old_filename = old_filename + ".txt" if not old_filename.endswith(".txt") else old_filename
       
        # Add .txt extension if not present in new filename
        new_filename = new_filename + ".txt" if not new_filename.endswith(".txt") else new_filename
       
        old_filepath = os.path.join(current_directory, old_filename)
        new_filepath = os.path.join(current_directory, new_filename)

        os.rename(old_filepath, new_filepath)
        print("file is renamed successfully.")
        tts.say("File is renamed successfully.")
        tts.runAndWait()
        # Update current_file if it matches the old filename
        if current_file == old_filepath:
            current_file = new_filepath

    except FileNotFoundError:
        print(old_filename, "not found.")
        tts.say("File not found.")
        tts.runAndWait()
    except FileExistsError:
        print(new_filename, "already exists.")
        tts.say("File alraedy exists.")
        tts.runAndWait()
    except Exception as e:
        print("sorry, try again.")
        tts.say("Sorry, try again.")
        tts.runAndWait()


def write_file(text):
    global current_file, current_directory
    if current_file:
        filepath = os.path.join(current_directory, current_file)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.write(text)  # Write the text to Notepad
        print("Text written to file.")
        tts.say("Text written to file.")
        tts.runAndWait()
    else:
        print("no file currently opened.")
        tts.say("No file currently opened.")
        tts.runAndWait()


def append_file(text):
    global current_file, current_directory
    if current_file:
        filepath = os.path.join(current_directory, current_file)
        pyautogui.press('end')  # Move cursor to the end of the file
        pyautogui.write('\n' + text)  # Write the text to a new line in Notepad
        print("Text appended to file.")
        tts.say("Text appended to file.")
        tts.runAndWait()
    else:
        print("no file currently opened.")
        tts.say("No file currently opened.")
        tts.runAndWait()


def save_file(filename):
    pyautogui.hotkey('ctrl', 's')  # Send Ctrl + S to save the file in Notepad
    print("File saved successfully.")


def summarize_file():
    if current_file.endswith('.txt'):
        parser = PlaintextParser.from_file(current_file, Tokenizer(LANGUAGE))
    else:
        raise ValueError("Unsupported file format")

    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    summary = []
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        summary.append(str(sentence))

    text = ' '.join(summary)
    print(text)
    tts.say(text)
    tts.runAndWait()


def open_file_pdf(filename):
    global current_file, current_directory
    try:
        if current_file:
            close_any_file(current_file)
        filepath = os.path.join(current_directory, filename)    
        if filename.lower().endswith(".pdf"):
            document = fitz.open(filepath)
            os.startfile(filepath)
            print("PDF file opened successfully:", filename)
            current_file = filename
        else:
            if os.path.exists(filepath):  # Check if the file exists
                process = subprocess.Popen(["notepad.exe", filepath])
                print("File opened successfully:", filename)
                current_file = filename
            else:
                print(filename, "file not found.")
                tts.say("File not found.")
                tts.runAndWait()
    except FileNotFoundError:
        print(filename, "file not found.")
        tts.say("File not found.")
        tts.runAndWait()


def scroll_up():
    pyautogui.press('pageup')  # Scroll up 3 steps (adjust as needed)


def scroll_down():
    pyautogui.press('pagedown') # Scroll down 3 steps (adjust as needed)


def read_file_pdf():
    global current_file, current_directory
    if current_file:
        try:
            filepath = os.path.join(current_directory, current_file)
            if current_file.lower().endswith(".pdf"):
                with open(filepath,"rb") as pdf:
                    reader = PyPDF2.PdfReader(pdf,strict=False)
                    for page in reader.pages:
                        content = page.extract_text()
                        tts.say(content)
                        tts.runAndWait()
            else:
                with open(filepath, "r") as file:
                    file_content = file.read()
                    tts.say(file_content)
                    tts.runAndWait()
        except FileNotFoundError:
            print(current_file, "file not opened.")
            tts.say("File is not opened.")
            tts.runAndWait()
    else:
        print("no file currently opened.")
        tts.say("No file currently opened.")
        tts.runAndWait()


def make_folder(folder_name):
    global current_directory
    new_folder_path = os.path.join(current_directory, folder_name)
    try:
        os.makedirs(new_folder_path)
        print("folder", folder_name, "created successfully.")
        tts.say("Folder is created successfully.")
        tts.runAndWait()
    except FileExistsError:
        print("folder", folder_name, "already exists.")
        tts.say("Folder already exists.")
        tts.runAndWait()
    except Exception as e:
        print("try again later.")
        tts.say("Try again later.")
        tts.runAndWait()


def open_folder(folder_name):
    global current_directory
    new_folder_path = os.path.join(current_directory, folder_name)
    if os.path.exists(new_folder_path):
        current_directory = new_folder_path
        print(current_directory, "is now opened.")
        tts.say(folder_name)
        tts.say("is now opened.")
        tts.runAndWait()
    else:
        print(folder_name, "does not exis.")
        tts.say("Folder does not exists.")
        tts.runAndWait()


def go_back():
    global current_directory
    root_drive = os.path.splitdrive(current_directory)[0]  # Get the root drive of the current directory
    if current_directory != root_drive:  # Check if the current directory is not the root drive
        current_directory = os.path.dirname(current_directory)  # Go back one directory
        print(current_directory, " is current folder.")
        tts.say(current_directory)
        tts.say("is current folder.")
        tts.runAndWait()
    else:
        print("cannot go back beyond the root drive.")
        tts.say("cannot go back beyond the root drive.")
        tts.runAndWait()


def list_directory():
    global current_directory
    try:
        files = os.listdir(current_directory)
        if files:
            print("Files and Folders in ", current_directory + " are ")
            tts.say("Files and Folders in current directory are")
            tts.runAndWait()
            for item in files:
                print(item)
                tts.say(item)
                tts.runAndWait()
        else:
            print("the directory is empty.")
            tts.say("The directory is empty")
            tts.runAndWait()
    except FileNotFoundError:
        print("directory not found.")
        tts.say("Directory not found.")
        tts.runAndWait()
    except Exception as e:
        print("try again later.")
        tts.say("Try again later.")
        tts.runAndWait()


def delete_folder(folder_name):
    global current_directory
    folder_path = os.path.join(current_directory, folder_name)
    try:
        shutil.rmtree(folder_path)
        print("folder", folder_name, "deleted successfully.")
        tts.say("Folder deleted successfully")
        tts.runAndWait()
    except FileNotFoundError:
        print("folder", folder_name, "not found.")
        tts.say("Folder not found.")
        tts.runAndWait()
    except Exception as e:
        print("error deleting folder.")
        tts.say("folder could not be deleted.")
        tts.runAndWait()


def delete_any_file(filename):
    global current_directory
    filepath = os.path.join(current_directory, filename)
    try:
        os.remove(filepath)
        print(filename, "deleted successfully.")
        tts.say("File deleted successfully")
        tts.runAndWait()
    except FileNotFoundError:
        print(filename, "not found.")
        tts.say("Not Found")
        tts.runAndWait()


def open_image(filename):
    global current_file, img, current_directory
    if current_file:
        close_any_file()
    try:
        # Add file extension if not present
        if not filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            filename += ".jpg"  # Assuming it's a JPEG image

        filepath = os.path.join(current_directory, filename)
        img = Image.open(filepath)
        current_file = filename
        img.show()
        print("Image opened successfully:", filename)
        tts.say("Image opened successfully.")
        tts.runAndWait()
    except FileNotFoundError:
        print("Image not found:", filename)
        tts.say("Image not found.")
        tts.runAndWait()
    except Exception as e:
        print("An error occurred while opening the image.")
        tts.say("image could not be opened.")
        tts.runAndWait()


def play_audio(filename):
    global current_directory
    try:
        # Add file extension if not present
        if not filename.lower().endswith((".mp3", ".wav")):
            filename += ".mp3"
        filepath = os.path.join(current_directory, filename)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        print("Playing audio:", filename)
    except pygame.error as e:
        print("Error playing audio.")
        tts.say("audio could not be played.")
        tts.runAndWait()


def stop_audio():
    pygame.mixer.music.stop()
    close_any_file()
    print("Audio playback stopped.")


def pause_audio():
    pygame.mixer.music.pause()
    print("Audio playback paused.")


def resume_audio():
    pygame.mixer.music.unpause()
    print("Audio  playback resumed.")


def increase_volume():
    current_volume = pygame.mixer.music.get_volume()
    new_volume = min(1.0, current_volume + 0.1)
    pygame.mixer.music.set_volume(new_volume)
    print(f"Volume increased to {new_volume:.2f}")


def decrease_volume():
    current_volume = pygame.mixer.music.get_volume()
    new_volume = max(0.0, current_volume - 0.1)
    pygame.mixer.music.set_volume(new_volume)
    print(f"Volume decreased to {new_volume:.2f}")


def close_any_file():
    global current_file
    if current_file:
        if current_file.lower().endswith(".txt"):
            save_file(current_file)
        filepath = os.path.join(current_directory, current_file)
        pyautogui.hotkey('alt', 'f4')  # Send Alt + f4 to close the any opened file
        print(current_file, "closed successfully.")
        current_file = None
    else:
        print("no file is currently opened.")


def exit_script():
    close_any_file() # close the file before exiting
    print("Good bye ")
    tts.say("Good Bye")
    tts.runAndWait()
    exit()

def display_info():  
    print("\t===========================")
    print("\t|                         |")
    print("\t| Welcome to Talking Tom! |")
    print("\t|                         |")
    print("\t===========================\n")
    print(">>>> I am your computer buddy, how can I help you ? \n")


def main():
    tts.say("Welcome to Talking Tom!, how can I help you ?")
    tts.runAndWait()
    os.system('cls' if os.name == 'nt' else 'clear')
    display_info()

    while True: 
        command = listen_for_command()
       
        # for txt files ----------------
        if command.startswith("open file"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".txt" if not filename.endswith(".txt") else filename
                open_file_pdf(filename)
            else:
                print("provide a filename to open.")
                tts.say("Provide a filename to open.")
                tts.runAndWait()

        elif command.startswith("create file"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".txt" if not filename.endswith(".txt") else filename
                create_file(filename)
            else:
                print("provide a filename to create.")
                tts.say("Provide a filename to create.")
                tts.runAndWait()

        elif command.startswith("write"):
            text = command.split(" ", 1)[1] if len(command.split(" ")) > 1 else None
            if text:
                write_file(text)
            else:
                print("provide text to write.")
                tts.say("Provide text to write.")
                tts.runAndWait()

        elif command.startswith("append"):
            text = command.split(" ", 1)[1] if len(command.split(" ")) > 1 else None
            if text:
                append_file(text)
            else:
                print("provide text to append.")
                tts.say("Provide text to append.")
                tts.runAndWait()

        elif command.startswith("delete file"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".txt" if not filename.endswith(".txt") else filename
                delete_any_file(filename)
            else:
                print("provide a filename to delete.")  
                tts.say("Provide a filename to delete.")    
                tts.runAndWait()

        elif command.startswith("rename"):
            filenames = command.split(" ")[1:]  # Extract both old and new filenames
            if len(filenames) == 2:
                old_filename, new_filename = filenames
                old_filename = old_filename + ".txt" if not old_filename.endswith(".txt") else old_filename
                renamed_file = rename_file(old_filename, new_filename)
                if renamed_file:
                    if current_file == old_filename:
                        current_file = renamed_file
            else:
                print("provide both old and new filenames.")
                tts.say("Provide both old and new filenames.")
                tts.runAndWait()

        # for pdf files ----------------
        elif command.startswith("open pdf"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".pdf" if not filename.endswith(".pdf") else filename
                open_file_pdf(filename)
            else:
                print("provide a PDF name to open.")
                tts.say("Provide a PDF name to open.")
                tts.runAndWait()

        elif command.startswith("delete pdf"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".pdf" if not filename.endswith(".pdf") else filename
                delete_any_file(filename)
            else:
                print("provide a PDF name to delete.")
                tts.say("Povide a PDF name to delete.")
                tts.runAndWait()

        # for image files ----------------
        elif command.startswith("open image"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                open_image(filename)
            else:
                print("provide an image file to open.")
                tts.say("provide an image file to open.")
                tts.runAndWait()
       
        elif command.startswith("delete image"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".jpg" if not filename.endswith(".jpg") else filename
                delete_any_file(filename)
            else:
                print("provide an image filename to delete.")
                tts.say("provide an image filename to delete.")
                tts.runAndWait()

        # for audio files ----------------
        elif command.startswith("play audio"):
            filename = command.split(" ")[2] if len(command.split(" ")) > 2 else None
            if filename:
                filename = filename + ".mp3" if not filename.endswith(".mp3") else filename
                play_audio(filename)
            else:
                print("Please provide an audio filename to play.")
                tts.say("Please provide an audio filename to play.")
                tts.runAndWait()
       
        elif command.startswith("stop audio"):
            stop_audio()

        elif command.startswith("pause"):
            pause_audio()

        elif command.startswith("continue"):
            resume_audio()    

        elif command.startswith("increase volume"):
            increase_volume()

        elif command.startswith("decrease volume"):
            decrease_volume()

        # summarize txt files --------------
        elif command.startswith("summarise"):
            summarize_file()

        # for both txt and pdf files ----------------
        elif command.startswith("scroll up"):
            scroll_up()

        elif command.startswith("scroll down"):
            scroll_down()

        elif command.startswith("read"):
            read_file_pdf()

        # for folder ----------------
        elif command.startswith("make folder"):
            folder_name = command.split(" ", 2)[2] if len(command.split(" ")) > 2 else None
            if folder_name:
                make_folder(folder_name)
            else:
                print("provide a folder name to create.")
                tts.say("Provide a folder name to create.")
                tts.runAndWait()

        elif command.startswith("open folder"):
            folder_name = command.split(" ", 2)[2] if len(command.split(" ")) > 2 else None
            if folder_name:
                open_folder(folder_name)
            else:
                print("provide a folder name to open.")
                tts.say("Provide a folder name to open")
                tts.runAndWait()

        elif command.startswith("go back"):
            go_back()

        elif command.startswith("delete folder"):
            folder_name = command.split(" ", 2)[2] if len(command.split(" ")) > 2 else None
            if folder_name:
                delete_folder(folder_name)
            else:
                print("provide a folder name to delete.")
                tts.say("Provide a folder name to delete.")
                tts.runAndWait()

        elif command.startswith("list"):
            list_directory()

        # for closing any file ----------------
        elif command.startswith("close"):
            close_any_file()

        # for exiting script ----------------
        elif command.startswith("goodbye") | command.startswith("good bye"):
            exit_script()

if __name__ == "__main__":
    main()