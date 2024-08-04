import streamlit as st
import time as t
import html
import pickle

import base64

import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.silence import split_on_silence
from io import BytesIO

import fitz  # PyMuPDF

import speech_recognition
import pyttsx3

from vosk import KaldiRecognizer, Model
import zipfile
import requests

model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
model_zip = "vosk-model-small-en-us-0.15.zip"
model_dir = "model"


# Function to download the Vosk model
def download_model(url, save_path):
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


# Download the Vosk model if it doesn't exist
if not os.path.exists(model_dir):
    with st.spinner("Retrieving Transcription Model..."):
        download_model(model_url, model_zip)

        with zipfile.ZipFile(model_zip, 'r') as zip_ref:
            zip_ref.extractall(".")

        # Verify the extracted directory name
        extracted_dir = None
        for item in os.listdir('.'):
            if item.startswith("vosk-model") and os.path.isdir(item):
                extracted_dir = item
                break

        if extracted_dir:
            os.rename(extracted_dir, model_dir)
            os.remove(model_zip)
            st.write("Model downloaded and extracted.")
        else:
            st.write("Error: Model extraction failed.")
            st.stop()

# Load the Vosk model
model = Model(model_dir)



hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define your colors
background_color = "#ffffff"  # Main background color
text_color = "#333333"        # Text color
primary_color = "#1f77b4"     # Primary color
secondary_color = "#f0f0f0"   # Secondary color for backgrounds and components
hover_color = "#5a8e99"       # Darker shade for hover effects
active_color = "#155a8a"      # Even darker shade for active states

def inject_styles():
    # Inject custom CSS styles
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

        body {{
            font-family: 'Poppins', sans-serif;
            background-color: {background_color}; /* Light background */
            color: {text_color}; /* Darker text for contrast */
            margin: 0; /* Remove default margin */
            padding: 0; /* Remove default padding */
            line-height: 1.6; /* Improve readability */
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {primary_color}; /* Soft blue color for headings */
            font-weight: 600; /* Bold headings */
            margin-bottom: 10px; /* Space below headings */
        }}
        .stapp {{
            max-width: 900px; /* Set maximum width for the app */
            margin: auto; /* Center the app */
            padding: 20px; /* Add padding around content */
            background-color: #ffffff; /* White background for the app */
            border-radius: 10px; /* Rounded corners */
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1); /* Soft shadow */
        }}
        .stbutton > button {{
            background-color: {primary_color}; /* Custom primary color buttons */
            color: white; /* White text on buttons */
            border-radius: 8px; /* Rounded corners */
            padding: 10px 20px; /* Button padding */
            font-size: 16px; /* Button text size */
            font-family: 'Poppins', sans-serif; /* Font for button text */
            border: none; /* Remove default border */
            cursor: pointer; /* Pointer on hover */
            font-weight: bold; /* Make text bold */
            transition: background-color 0.3s ease, transform 0.2s; /* Smooth transition */
        }}
        .stbutton > button:hover {{
            background-color: {hover_color}; /* Darker shade on hover */
            transform: scale(1.05); /* Scale effect on hover */
        }}
        .stbutton > button:active {{
            background-color: {active_color}; /* Even darker for active state */
            transform: scale(0.95); /* Scale down effect on click */
        }}
        .stcheckbox > div:first-child {{
            transform: scale(1.3); /* Enlarge checkbox */
            margin-right: 10px; /* Space after checkbox */
        }}
        .stcheckbox > div > div {{
            font-family: 'Poppins', sans-serif; /* Font for checkbox labels */
            color: {primary_color}; /* Color for checkbox labels */
        }}

        /* Styling for select box labels */
        .stselectbox > div > label,
        .stmultiselectbox > div > label {{
            font-family: 'Poppins', sans-serif; /* Font for select box labels */
            color: {primary_color}; /* Color for select box labels */
            font-weight: 600; /* Bold select box labels */
        }}
        .stselectbox > div > div:first-child,
        .stmultiselect > div > div:first-child {{
            font-size: 16px; /* Font size for dropdowns */
            color: {primary_color}; /* Color for dropdowns */
            background-color: #f9f9f9; /* Background for the select box */
            border-radius: 8px; /* Rounded corners */
            padding: 10px; /* Padding for the select box */
            transition: background-color 0.3s ease; /* Smooth transition for background */
        }}
        .stselectbox > div > div:first-child:hover,
        .stmultiselect > div > div:first-child:hover {{
            background-color: #e0e0e0; /* Hover color for dropdown items */
        }}
        .stselectbox > div > div > div > div,
        .stmultiselect > div > div > div > div {{
            background-color: #ffffff; /* Background for dropdown items */
            border-radius: 8px; /* Rounded corners */
            color: {text_color}; /* Text color for dropdown items */
        }}
        .stselectbox > div > div > div > div:hover,
        .stmultiselect > div > div > div > div:hover {{
            background-color: {hover_color}; /* Hover color for dropdown items */
        }}

        /* Styling for text areas */
        .sttextinput > div > div > input,
        .sttextarea > div > textarea {{
            border-radius: 8px; /* Rounded corners for text fields */
            padding: 10px; /* Padding for text fields */
            border: 1px solid #ccc; /* Light border */
            font-size: 16px; /* Text size for inputs */
            background-color: #f9f9f9; /* Light gray background for text areas */
            color: {text_color}; /* Dark text */
            font-family: 'Poppins', sans-serif; /* Font for inputs */
        }}
        .sttextinput > div > div > input:focus,
        .sttextarea > div > textarea:focus {{
            outline: none; /* Remove outline */
            border: 1px solid {primary_color}; /* Custom border color on focus */
            box-shadow: 0 0 5px {primary_color}; /* Soft shadow on focus */
        }}

        .stfile_uploader > div > div {{
            border: 2px dashed {primary_color}; /* Dashed border for file uploader */
            border-radius: 8px; /* Rounded corners */
            padding: 20px; /* Padding for file uploader */
            background-color: #f9f9f9; /* Light gray background */
            color: {primary_color}; /* Color for file uploader text */
            font-family: 'Poppins', sans-serif; /* Font for file uploader text */
        }}
        .stfile_uploader:hover > div {{
            background-color: #f0f0f0; /* Hover effect for file uploader */
        }}
        .stslider > div > div {{
            color: {primary_color}; /* Slider text color */
            font-family: 'Poppins', sans-serif; /* Font for slider labels */
        }}
        .stradio > div > div {{
            color: {primary_color}; /* Radio button text color */
        }}
        .stexpander > div > div:first-child {{
            background-color: {primary_color}; /* Expander title background */
            color: white; /* White text */
            border-radius: 8px; /* Rounded corners */
            padding: 10px; /* Padding for expander title */
        }}
        .ststatus {{
            background-color: {primary_color}; /* Status background color */
            color: white; /* White text */
            font-size: 16px; /* Font size for status */
            font-family: 'Poppins', sans-serif; /* Font for status messages */
        }}
        .stmarkdown h2 {{
            color: {primary_color}; /* Markdown heading color */
        }}
        .stprogress > div {{
            background-color: {primary_color}; /* Progress bar color */
            border-radius: 8px; /* Rounded corners */
        }}
        .st.spinner {{
            color: {primary_color}; /* Spinner color */
            font-family: 'Poppins', sans-serif; /* Font for spinner */
        }}
        /* Additional styles for toast */
        .toastify__toast {{
            background-color: {primary_color}; /* Toast background */
            color: white; /* Toast text color */
            font-family: 'Poppins', sans-serif; /* Font for toast text */
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Inject custom CSS with the button styled to be bold
    st.markdown(
        f"""
              <style>
              body {{
                  font-family: 'poppins', sans-serif;
                  background-color: {background_color}; /* light background */
                  color: {text_color}; /* darker text for contrast */
                  margin: 0; /* remove default margin */
                  padding: 0; /* remove default padding */
                  line-height: 1.6; /* improve readability */
              }}
              h1, h2, h3, h4, h5, h6 {{
                  font-family: 'poppins', sans-serif;
                  color: {primary_color}; /* soft blue color for headings */
                  font-weight: 600; /* bold headings */
                  margin-bottom: 10px; /* space below headings */
              }}
              .stbutton > button {{
                  background-color: {primary_color}; /* custom primary color buttons */
                  color: white; /* white text on buttons */
                  border-radius: 8px; /* rounded corners */
                  padding: 10px 20px; /* button padding */
                  font-size: 16px; /* button text size */
                  font-family: 'poppins', sans-serif; /* font for button text */
                  border: none; /* remove default border */
                  cursor: pointer; /* pointer on hover */
                  font-weight: bold; /* make text bold */
                  transition: background-color 0.3s ease; /* smooth transition */
              }}
              .stbutton > button:hover {{
                  background-color: #5a8e99; /* slightly darker shade on hover */
              }}
              </style>
              """,
        unsafe_allow_html=True,
    )

inject_styles()

def read_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")  # Using "text" option for better text extraction
    return text


def silence_based_conversion(audio_file):
    # open the audio file stored in
    # the local system as a wav file.
    song = AudioSegment.from_wav(audio_file)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_song_name = temp_file.name
        song.export(temp_song_name, format="wav")

    st.audio(temp_song_name)

    # open a file where we will concatenate
    # and store the recognized text
    full_transcription = ""
    pickle.dump(full_transcription, open("silence_based_transcript.p", "wb"))

    # split track where silence is 0.5 seconds
    # or more and get chunks
    # Set the interval in milliseconds (e.g., 30 seconds)
    interval = 30 * 1000  # 30 seconds

    # Split the audio into chunks and store them in a list
    chunks = [song[i:i + interval] for i in range(0, len(song), interval)]

    #chunks = split_on_silence(song,
                              # must be silent for at least 0.5 seconds
                              # or 500 ms. adjust this value based on user
                              # requirement. if the speaker stays silent for
                              # longer, increase this value. else, decrease it.
                              #min_silence_len=600,

                              # consider it silent if quieter than -16 dBFS
                              # adjust this per requirement
                              #silence_thresh=-16
                              #)

    i = 0
    # process each chunk
    for chunk in chunks:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file_name = temp_file.name
            chunk.export(temp_file_name, format="wav")


        # create a speech recognition object
        r = speech_recognition.Recognizer()

        # recognize the chunk
        with speech_recognition.AudioFile(temp_file_name) as source:
            audio_listened = r.listen(source)

        try:
            # try converting it to text
            rec = r.recognize_vosk(audio_listened)
            rec = rec[14 : len(rec) - 3]
            # write the output to the file.
            full_transcription = str(pickle.load(open("silence_based_transcript.p", "rb")))
            pickle.dump(full_transcription + rec + " ", open("silence_based_transcript.p", "wb"))
            # catch any errors.
        except speech_recognition.UnknownValueError:
            r = speech_recognition.Recognizer()
        except speech_recognition.RequestError as e:
            st.write("Could not request results. check your internet connection")

        i += 1


def wav_to_audiodata(wav_file_path):
    # Initialize the recognizer
    recognizer = speech_recognition.Recognizer()

    # Load the WAV file using AudioFile
    audio_data = speech_recognition.AudioFile(wav_file_path)

    # Convert the WAV file to AudioData
    with audio_data as source:
        audio = recognizer.record(source)

    return audio


# Example usage:
# audiodata = wav_to_audiodata("path_to_your_file.wav")


def convert_to_wav_mono_pcm(input_file):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)
    # Convert to mono
    audio = audio.set_channels(1)
    # Ensure it is PCM format
    audio = audio.set_sample_width(2)
    # Create a temporary file for the converted audio
    output_file = "converted.wav"
    # Export as WAV
    audio.export(output_file, format="wav")
    return output_file

def create_download_link(filename):
    with open(filename, "rb") as f:
        pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()  # encode in base64 (binary-to-text)
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download file</a>'

def show_pdf_file():
    from markdown_pdf import MarkdownPdf
    from markdown_pdf import Section
    import html as h

    # Initialize MarkdownPdf and add sections
    pdf = MarkdownPdf(toc_level=1)
    pdf.add_section(
        Section(
            '''<style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body {
            font-family: 'Roboto', sans-serif;
            font-size: 12pt;
            color: #333333;
            }
            h1 {
            font-size: 36pt;
            color: #0066cc;
            font-weight: bold;
            }
            h2 {
            font-size: 20pt;
            color: #333333;
            }
            h3 {
            font-size: 16pt;
            color: #333333;
            }
            p {
            margin-bottom: 10pt;
            }
            </style>'''

            +
              "\n" + myContainer.notestext))  # Replace with your actual content

    # Save the PDF to a file
    pdf_file = "AI-Generator-" + str(myContainer.notestext[myContainer.notestext.find(' ') + 1:myContainer.notestext.find('\n')]) + "_notes.pdf"
    pdf.save(pdf_file)

    # Create a download link for the PDF
    html = create_download_link(pdf_file)

    # Display the download link in Streamlit
    st.markdown(html, unsafe_allow_html=True)


import pathlib
import textwrap
import tempfile
from datetime import time

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

st.title("NoteBerry :grapes:")
# Inject CSS for selectbox and its label
st.markdown(
    f"""
    <style>
    /* General body styles */
    body {{
        font-family: 'Poppins', sans-serif;
        background-color: {background_color}; /* Main background color */
    }}

    /* Styling for select box label */
    .stSelectbox > div > label {{
        font-family: 'Poppins', sans-serif; /* Font for select box labels */
        color: {primary_color}; /* Color for select box labels */
        font-weight: 600; /* Bold label */
        font-size: 18px; /* Larger font size */
        margin-bottom: 5px; /* Space below the label */
        display: block; /* Ensure label takes full width */
    }}

    /* Styling for the select box itself */
    .stSelectbox > div > div:first-child {{
        background-color: {secondary_color}; /* Background for select box */
        border-radius: 8px; /* Rounded corners */
        padding: 0; /* Adjusted padding */
        border: 1px solid #ccc; /* Light border */
        transition: background-color 0.3s, border 0.3s; /* Smooth transition */
    }}

    /* Set text color and font for the dropdown and options */
    .stSelectbox > div > div:first-child select {{
        font-family: 'Poppins', sans-serif; /* Font for dropdown selected option */
        color: {text_color}; /* Text color for dropdown selected option */
        background-color: {secondary_color}; /* Background for dropdown selected option */
        border: none; /* Remove default border */
        padding: 10px; /* Padding for visible area */
        font-size: 16px; /* Font size for select options */
        border-radius: 8px; /* Rounded corners */
    }}

    /* Set color and font for options in the dropdown */
    .stSelectbox > div > div:first-child select option {{
        font-family: 'Poppins', sans-serif; /* Font for each option */
        color: {text_color}; /* Text color for each option */
        background-color: {secondary_color}; /* Option background color */
    }}

    .stSelectbox > div > div:first-child:hover {{
        background-color: {hover_color}; /* Hover color for the select box */
    }}

    .stSelectbox > div > div:first-child:focus {{
        border: 1px solid {primary_color}; /* Highlight border on focus */
        box-shadow: 0 0 5px {primary_color}; /* Soft shadow on focus */
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
option = st.selectbox('Select an option',['Upload Audio/Record a Lecture', 'Upload PDF/Enter Text Content'])
contentformat = st.selectbox('Select an option',['Generate Notes', 'Generate Audio Notes', 'Generate Video Notes (Experimental)'])
summarize = st.checkbox("Summarize (This will condense the content into short, precise information)")

recordingmode = option == 'Upload Audio/Record a Lecture'
uploadedaudio = st.file_uploader(label="Upload WAV or MP3 Audio", type=['wav', 'mp3']) if recordingmode else st.empty()
uploadedtext = st.file_uploader(label="Upload PDF Document (May not work well with Math/Equations)", type='pdf', on_change=inject_styles) if not recordingmode else st.empty()

subheader = st.empty()

if uploadedtext is None or uploadedaudio is None:
    subheader = st.subheader("OR")
else:
    subheader = st.empty()

user_input = None if recordingmode else (st.text_area("Enter your content:", height=200) if uploadedtext is None else read_pdf(uploadedtext))


class datacontainerobj:
    def __init__(self):
        try:
            with open("audiotranscription.p", "rb") as audiofile:
                self.audiotranscription = audiofile
        except FileNotFoundError:
            self.audiotranscription = None


        self.pressed = False
        self.notestext = None
        self.audiogeneratefromlecture = None
        self.hasStoppedRecording = False
        self.hasStartedRecording = False
        self.transcription = None
        self.transcript = ""


myContainer = datacontainerobj()





def generatecontent(recordingmode = False):
    myContainer.pressed = False
    # Use the input from the text area to run code
    if contentformat == 'Generate Notes' and not myContainer.pressed:
        myContainer.pressed = True

        # The 'with' statement is used here to manage the spinner context
        with st.spinner("Initializing AI Model..."):
            genai.configure(api_key='')

            model = genai.GenerativeModel('gemini-1.5-flash')

        def to_markdown(text):
            text = text.replace('•', '  *')
            return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        input_text = user_input if not recordingmode else myContainer.audiotranscription

        response = ""

        with st.spinner("Processing your content with AI..."):
            response = model.generate_content(str(r'''Put every single thing from this input into notes. Don't leave out any content at all. 
            All content MUST be in the notes. Use markdown notation for headers, subheaders, and bullet points. Give good spacing and organization. Use markdown-style tables and numbered
             lists often (but dont use numbered lists in subheaders, e.g., numbered lists that have more content under them), bullet points, etc. when applicable. If you have math equations, use Latex notation. For example, "f&#x27;(x) = lim_{\Delta x \to 0} \frac{f(x + \Delta x) - f(x)}{\Delta x}" would be
             converted to LaTeX notation. Here's the content:''') + str(
                input_text)) if not summarize else model.generate_content(str(r'''Summarize and condense this content into notes with just the most important
                information. Only get the important info and overview, no need to include all of the content. Use markdown notation for headers, subheaders, and bullet points. Used markdown-style tables and numbered
             lists often (but don't put numbered lists in subheaders, e.g., numbered lists that have more content under them), bullet points, etc. when applicable.  If you have math equations, use Latex notation. For example, "f&#x27;(x) = lim_{\Delta x \to 0} \frac{f(x + \Delta x) - f(x)}{\Delta x}" would be
             converted to LaTeX notation. Give good spacing and organization.  Here's the content''') + str(
                input_text))
            myContainer.notestext = response.text

        st.write("Your AI Notes are Ready!")

        show_pdf_file()

        # Render the styled box using st.markdown
        st.markdown(myContainer.notestext, unsafe_allow_html=True)
        myContainer.pressed = False






















































    elif contentformat == 'Generate Audio Notes' and not myContainer.pressed:
        myContainer.notestext = None
        myContainer.pressed = True

        # The 'with' statement is used here to manage the spinner context
        with st.spinner("Initializing AI Audio Model..."):
            genai.configure(api_key=st.secrets["api_key"])

            model = genai.GenerativeModel('gemini-1.5-flash')

        def to_markdown(text):
            text = text.replace('•', '  *')
            return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        input_text = user_input if not recordingmode else myContainer.audiotranscription

        with st.spinner("Processing your content with AI..."):
            myContainer.audiogeneratefromlecture = model.generate_content(str('''Summarize and put this content into notes with ALL of the
                information. Include all information, don't leave out ANY content. Then, take those notes and make it into a long paragraph to be read out loud as a 
                lecture, proportional to the length of the notes. No characters other than what you would see in an english essay, because
               a text to speech agent will be reading this out loud. For example, no greater than symbols because the
               text to speech agent will read out "greater than symbol." Have good spacing in the script because
               a transcript will be provided. Don't provide me with the notes, just the lecture script paragraph. If certain sentences don't make sense,
                rephrase the sentence to make sense in English language (as some of the sentences are from a faulty audio transript). Heres the content:''') + str(
                input_text)).text if not summarize else model.generate_content(str('''Summarize and condense this content into notes with just the most important
                information. Only get the important info and overview, no need to include all of the content. Just a brief summary of the most important stuff. 
                Then, take those notes and make it into a paragraph to be read out loud as a lecture, proportional to the length of the notes. 
                No characters other than what you would see in an english essay, because
               a text to speech agent will be reading this out loud. For example, no greater than symbols because the
               text to speech agent will read out "greater than symbol." Have good spacing in the script because
               a transcript will be provided. Don't provide me with the notes, just the lecture script paragraph. If certain sentences don't make sense,
                rephrase the sentence to make sense in English language (as some of the sentences are from a faulty audio transript). Heres the content:''') + str(
                input_text)).text

        # Function to split text into segments of maximum 1500 characters ending at sentence boundaries
        def split_text_into_segments(text, max_length=1500):
            import re
            sentence_endings = re.compile(r'(?<=[.!?]) +')
            sentences = sentence_endings.split(text)

            segments = []
            current_segment = ""

            for sentence in sentences:
                if len(current_segment) + len(sentence) + 1 <= max_length:
                    if current_segment:
                        current_segment += " "
                    current_segment += sentence
                else:
                    segments.append(current_segment)
                    current_segment = sentence

            if current_segment:
                segments.append(current_segment)

            return segments

        # Function to synthesize speech and return audio bytes using gTTS
        def synthesize_speech(text, lang='en'):
            tts = gTTS(text=text, lang=lang)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            return audio_bytes.read()

        # Function to join audio streams
        def join_audio_streams(audio_streams):
            combined = AudioSegment.empty()
            for audio_stream in audio_streams:
                audio_segment = AudioSegment.from_file(BytesIO(audio_stream))
                combined += audio_segment

            output_bytes = BytesIO()
            combined.export(output_bytes, format="mp3")
            output_bytes.seek(0)
            return output_bytes

        # Main text to be converted to speech
        text_to_convert = myContainer.audiogeneratefromlecture

        with st.spinner("Generating Audio File... "):
            # Split the text into segments
            segments = split_text_into_segments(text_to_convert)

            # Synthesize speech for each segment and collect audio streams
            audio_streams = []
            for segment in segments:
                audio_stream = synthesize_speech(segment)
                audio_streams.append(audio_stream)

            # Join the audio streams into one
            final_output_bytes = join_audio_streams(audio_streams)

        # Display the combined audio to the user
        st.write("Your audio file is ready!")
        st.audio(final_output_bytes.getvalue(), format='audio/mp3')
        st.write("")
        st.subheader("Transcript:")
        with st.spinner("Generating user-friendly transcript..."):
            st.markdown((model.generate_content('''If there are any math equations present or anything that looks like it
            should be a math equation (such as the limit of f of x as x approaches a), convert them
                                                to latex notation. Add in markdown headers and subheaders. Keep the text unchanged.
                                                Keeping the text unchanged, use markdown format to apply bullet points and use markdown-style tables and numbered lists if applicable (but dont use numbered lists in subheaders, e.g., numbered lists that have more content under them).
                                                Keep everything else unchanged. If there is math that should be converted to equations or symbols
                                                use Latex notation. Keep the text unchanged.
                                                Here's the content: ''' + myContainer.audiogeneratefromlecture).text),
                        unsafe_allow_html=True)
        myContainer.pressed = False



    # Use the input from the text area to run code
    elif contentformat == 'Generate Video Notes (Experimental)' and not myContainer.pressed:
        myContainer.notestext = None
        myContainer.pressed = True

        # The 'with' statement is used here to manage the spinner context
        with st.spinner("Initializing AI Video Model..."):
            genai.configure(api_key='AIzaSyCZObffhLbps5I-NhjgDF5seb-eeZQ8bP8')

            model = genai.GenerativeModel('gemini-1.5-flash')

        def to_markdown(text):
            text = text.replace('•', '  *')
            return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        input_text = user_input if not recordingmode else myContainer.audiotranscription

        with st.spinner("Processing your content with AI..."):
            response = model.generate_content(str('''Summarize and put this content into notes with ALL of the
                information. Include all information, don't leave out ANY content. Then, take those notes and make it into a long paragraph to be read out loud as a 
                lecture, proportional to the length of the notes. No characters other than what you would see in an english essay, because
               a text to speech agent will be reading this out loud. For example, no greater than symbols because the
               text to speech agent will read out "greater than symbol." Have good spacing in the script because
               a transcript will be provided. Don't provide me with the notes, just the lecture script paragraph. This paragraph will be the video script.

               Demarcate this video script with quotation marks, and before the video script, generate a prompt for an AI video generator to make a video about 
               that topic demarcated by curly brackets, give the tone/mood, background images that correspond to the script, text to speech : male voice, 
               and primary audience and goal. Heres the content:''') + str(
                input_text)) if not summarize else model.generate_content(str('''Summarize and condense this content into notes with just the most important
                information. Only get the important info and overview, no need to include all of the content. Just a brief summary of the most important stuff. 
                Then, take those notes and make it into a paragraph to be read out loud as a lecture, proportional to the length of the notes. 
                No characters other than what you would see in an english essay, because
               a text to speech agent will be reading this out loud. For example, no greater than symbols because the
               text to speech agent will read out "greater than symbol." Have good spacing in the script because
               a transcript will be provided. Don't provide me with the notes, just the lecture script paragraph. This paragraph will be the video script.


                Demarcate this video script with quotation marks, and before the video script, generate a prompt for an AI video generator to make a video about 
               that topic demarcated by curly brackets, give the tone/mood, background images that correspond to the script, text to speech : male voice, 
               and primary audience and goal. Heres the content:''') + str(input_text))

        def extract_inside_curly_braces(s):
            start = s.find('{') + 1
            end = s.find('}', start)
            if start > 0 and end > start:
                return s[start:end]
            return None  # or return an empty string or raise an error, depending on your needs

        def after_curly_braces(s):
            start = s.find('{') + 1
            end = s.find('}', start)
            if start > 0 and end > start:
                return s[end + 1:]
            return None  # or return an empty string or raise an error, depending on your needs


        import requests

        url = 'https://www.veed.io/text-to-video-ap/api/generate/async'
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            "prompt": extract_inside_curly_braces(response.text),
            "script": after_curly_braces(response.text),
            "voice": "male"
        }

        with st.spinner("Generating Video Link..."):
            response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            result = response.json()

            progress_bar = st.progress(0)
            percent_complete = 0
            loading_message = st.empty()

            for i in range(1000):
                percent_complete += 0.001
                percentstring = str(percent_complete * 100)
                loading_message.write("Loading Final Video (" + percentstring[0: percentstring.find('.') + 2] + "%)...")
                t.sleep(.18 * (len(after_curly_braces(response.text)) / 2500.0))  # Simulate work being done
                progress_bar.progress(percent_complete)

            loading_message = st.empty()
            st.write("Video Link:", result['project']['link'])
            myContainer.pressed = False

            # print("Project ID:", result['project']['id'])
            # print("Project Title:", result['project']['title'])
            # print("Project Link:", result['project']['link'])
            # print("Project Thumbnail:", result['project']['thumbnail'])
        else:
            st.write("There was an error. Please try again.")
            myContainer.pressed = False


if recordingmode:
    import shutil

    import os


    def specialgeneratefortranscribe():
        transcripttorender = str(pickle.load(open("audiotranscription.p", "rb")))
        with st.expander("Final Transcript"):
            st.write(transcripttorender)
        myContainer.audiotranscription = transcripttorender
        st.write("Recording Stopped.")
        myContainer.hasStoppedRecording = True
        st.toast("Generation Started...")
        generatecontent(recordingmode=True)
        st.toast("Generation Complete!")
        st.balloons()
        st.session_state.running = False

    def record_and_transcribe_audio(stopbutton : st.button):
        if stopbutton:
            specialgeneratefortranscribe()

        if st.session_state.running == True:
            recognizer = speech_recognition.Recognizer()

            try:
                with speech_recognition.Microphone() as mic:
                    recognizer.adjust_for_ambient_noise(mic)
                    audio = recognizer.listen(mic)

                    text = recognizer.recognize_google(audio)
                    text = text.lower()
                    myContainer.transcript = myContainer.transcript + text
                    myContainer.transcription.write(str(myContainer.transcript))
                    myContainer.audiotranscription = str(myContainer.transcript)
                    pickle.dump(myContainer.audiotranscription, open("audiotranscription.p", "wb"))


            except speech_recognition.UnknownValueError:
                recognizer = speech_recognition.Recognizer()
                pass


    if 'running' not in st.session_state:
        st.session_state.running = False

    if uploadedaudio is None:
        startbutton = st.button("Start Recording")
        subheader = st.empty()

        if startbutton:
            subheader = st.subheader("Transcript: ")
            myContainer.transcription = st.empty()
            st.session_state.running = True

    if st.session_state.running == True:
        stopbutton = st.button("Stop Recording")

        for i in range(10000):
            if st.session_state.running == False:
                break
            record_and_transcribe_audio(stopbutton=stopbutton)

    elif st.button("Generate from Upload"):
        with st.status(label = "Transcribing Upload", expanded = True):
            silence_based_conversion(convert_to_wav_mono_pcm(uploadedaudio))
            text = str(pickle.load(open("silence_based_transcript.p", "rb")))
            st.write(str(text))
            myContainer.audiotranscription = str(text)

        st.toast("Generation Started...")
        generatecontent(recordingmode=True)
        st.toast("Generation Complete!")
        st.balloons()




elif st.button("Generate"):
    st.toast("Generation Started...")
    generatecontent(recordingmode=False)
    st.toast("Generation Complete!")
    st.balloons()






































