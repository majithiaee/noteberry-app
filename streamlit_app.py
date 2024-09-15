import streamlit as st
import time as t

import base64


import fitz  # PyMuPDF




# Define your colors
background_color = "#ffffff"  # Main background color
text_color = "#333333"        # Text color
primary_color = "#1f77b4"     # Primary color
secondary_color = "#f0f0f0"   # Secondary color for backgrounds and components
hover_color = "#5a8e99"       # Darker shade for hover effects
active_color = "#155a8a"      # Even darker shade for active states

st.set_page_config(page_title="Noteberry - AI Note Taker")
def read_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")  # Using "text" option for better text extraction
    return text
 #
def create_download_link(filename):
    with open(filename, "rb") as f:
        pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()  # encode in base64 (binary-to-text)
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download file</a>'



def show_pdf_file():
    from markdown_pdf import MarkdownPdf
    from markdown_pdf import Section

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
    pdf_file = "AI-Generator-" + str(
        myContainer.notestext[myContainer.notestext.find(' ') + 1:myContainer.notestext.find('\n')]) + "_notes.pdf"
    pdf.save(pdf_file)

    # Create a download link for the PDF
    html = create_download_link(pdf_file)

    # Display the download link in Streamlit
    st.markdown(html, unsafe_allow_html=True)

import textwrap

import google.generativeai as genai

from IPython.display import Markdown

st.title(":strawberry: Noteberry :grapes:")

contentformat = st.selectbox('Select an option',['Generate Notes', 'Generate Video Notes (Experimental)'])
summarize = st.checkbox("Summarize (This will condense the content into short, precise information)")

uploadedtext = st.file_uploader(label="Upload PDF Document (May not work well with Math/Equations)", type='pdf')

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
            genai.configure(api_key=st.secrets['api_key'])

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
            genai.configure(api_key=st.secrets['api_key'])

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
        else:
            st.write("There was an error. Please try again.")
            myContainer.pressed = False


if st.button("Generate"):
    st.toast("Generation Started...")
    generatecontent()
    st.toast("Generation Complete!")
    st.balloons()






































