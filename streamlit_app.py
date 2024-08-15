import streamlit as st
import time as t
import pickle

import base64

from pydub import AudioSegment


import fitz  # PyMuPDF

import speech_recognition



# Define your colors
background_color = "#ffffff"  # Main background color
text_color = "#333333"        # Text color
primary_color = "#1f77b4"     # Primary color
secondary_color = "#f0f0f0"   # Secondary color for backgrounds and components
hover_color = "#5a8e99"       # Darker shade for hover effects
active_color = "#155a8a"      # Even darker shade for active states

def inject_styles():
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
            rec = r.recognize_houndify(audio_listened)
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

from IPython.display import Markdown

st.title("NoteBerry :grapes:")

contentformat = st.selectbox('Select an option',['Generate Notes', 'Generate Video Notes (Experimental)'])
summarize = st.checkbox("Summarize (This will condense the content into short, precise information)")

uploadedtext = st.file_uploader(label="Upload PDF Document (May not work well with Math/Equations)", type='pdf', on_change=inject_styles)

subheader = st.empty()

if uploadedtext is None:
    subheader = st.subheader("OR")
else:
    subheader = st.empty()

user_input = st.text_area("Enter your content:", height=200) if uploadedtext is None else read_pdf(uploadedtext)


class datacontainerobj:
    def __init__(self):
        try:
            with open("audiotranscription.p", "rb") as audiofile:
                self.audiotranscription = audiofile
        except FileNotFoundError:
            self.audiotranscription = None


        self.pressed = False
        self.notestext = None


myContainer = datacontainerobj()





def generatecontent():
    myContainer.pressed = False
    # Use the input from the text area to run code
    if contentformat == 'Generate Notes' and not myContainer.pressed:
        myContainer.pressed = True

        # The 'with' statement is used here to manage the spinner context
        with st.spinner("Initializing AI Model..."):
            genai.configure(api_key="AIzaSyCZObffhLbps5I-NhjgDF5seb-eeZQ8bP8")

            model = genai.GenerativeModel('gemini-1.5-flash')

        def to_markdown(text):
            text = text.replace('•', '  *')
            return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        input_text = user_input

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




























    # Use the input from the text area to run code
    elif contentformat == 'Generate Video Notes (Experimental)' and not myContainer.pressed:
        myContainer.notestext = None
        myContainer.pressed = True

        # The 'with' statement is used here to manage the spinner context
        with st.spinner("Initializing AI Video Model..."):
            genai.configure(api_key="AIzaSyCZObffhLbps5I-NhjgDF5seb-eeZQ8bP8")

            model = genai.GenerativeModel('gemini-1.5-flash')

        def to_markdown(text):
            text = text.replace('•', '  *')
            return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        input_text = user_input

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


if st.button("Generate"):
    st.toast("Generation Started...")
    generatecontent()
    st.toast("Generation Complete!")
    st.balloons()






































