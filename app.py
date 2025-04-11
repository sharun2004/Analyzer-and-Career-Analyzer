import streamlit as st
import requests
import os
import pdfplumber
from dotenv import load_dotenv
from streamlit_lottie import st_lottie
import re

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("LANGFLOW_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for dark mode
def local_css():
    st.markdown("""
    <style>
        /* Dark theme colors */
        :root {
            --primary-color: #6C63FF;
            --secondary-color: #00C896;
            --background-color: #121212;
            --card-background: #1E1E1E;
            --text-color: #E0E0E0;
            --border-color: #333333;
            --highlight-color: rgba(108, 99, 255, 0.2);
        }

        /* General styling */
        .main {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        h1, h2, h3, h4, h5, h6, p, li, div {
            color: var(--text-color);
        }

        /* Custom card styling */
        .card {
            border-radius: 10px;
            border: 1px solid var(--border-color);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            background-color: var(--card-background);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        /* Section styling */
        .section {
            margin-bottom: 2rem;
            padding: 1.5rem;
            border-radius: 10px;
            background-color: var(--card-background);
            border-left: 4px solid var(--primary-color);
        }

        /* Section headers */
        .section-header {
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }

        /* Custom button styling */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #5A52D5;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        /* File uploader styling */
        .uploadedFile {
            border: 2px dashed var(--primary-color);
            border-radius: 10px;
            padding: 1rem;
            background-color: rgba(108, 99, 255, 0.1);
        }

        /* Analysis result styling */
        .result-item {
            background-color: rgba(30, 30, 30, 0.7);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
        }

        .highlight {
            background-color: var(--highlight-color);
            border-left: 4px solid var(--secondary-color);
            padding: 0.8rem 1rem;
            margin: 1rem 0;
        }

        /* Progress bar */
        .stProgress > div > div > div {
            background-color: var(--primary-color);
        }

        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--card-background);
        }

        /* Custom list styling */
        ul.custom-list {
            list-style-type: none;
            padding-left: 0;
        }

        ul.custom-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }

        ul.custom-list li:last-child {
            border-bottom: none;
        }

        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .badge-primary {
            background-color: var(--primary-color);
            color: white;
        }

        .badge-secondary {
            background-color: var(--secondary-color);
            color: white;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: var(--card-background);
            border-radius: 4px 4px 0 0;
            padding: 0.5rem 1rem;
            border: 1px solid var(--border-color);
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color);
            color: white;
        }

        /* Section divider */
        .divider {
            height: 1px;
            background-color: var(--border-color);
            margin: 2rem 0;
        }

        /* Animation container */
        .animation-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)


# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() or "" for page in pdf.pages])


# Function to load Lottie animations
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Function to clean markdown text (remove ** symbols)
def clean_markdown(text):
    # Replace ** with nothing (to remove bold formatting)
    cleaned_text = re.sub(r'\*\*', '', text)
    cleaned_text = re.sub(r'\*', '', text)
    return cleaned_text


# UPDATED: Function to parse and extract the analysis text from API response
def parse_resume_analysis(result):
    """
    Improved function to extract the analysis text from the Langflow API response.
    This handles the specific structure of your Langflow JSON response.
    """
    try:
        # Direct path to the text content based on your Langflow JSON structure
        if 'outputs' in result and len(result['outputs']) > 0:
            if 'outputs' in result['outputs'][0]:
                if 'results' in result['outputs'][0]['outputs'][0]:
                    message_data = result['outputs'][0]['outputs'][0]['results'].get('message', {})
                    if 'text' in message_data:
                        return message_data['text']
    except Exception as e:
        st.error(f"Error parsing result: {e}")
        return str(result)

    # If we couldn't find the text, return a fallback message
    return "Could not extract analysis text from the response."


# UPDATED: Function to extract sections from the analysis text
def extract_sections(text):
    """
    Improved function to extract sections from the analysis text.
    This handles the specific formatting of your API response.
    """
    sections = {
        "Personal Data": [],
        "Job Roles": [],
        "Skill Gaps": [],
        "Improvements": []
    }

    # Split the text by section headers
    if "2. Suitable Job Roles:" in text:
        personal_data = text.split("2. Suitable Job Roles:")[0].strip()
        sections["Personal Data"] = [clean_markdown(line.strip()) for line in personal_data.split('\n') if line.strip()]

    if "2. Suitable Job Roles:" in text and "3. Skill Gaps and Weaknesses:" in text:
        job_roles = text.split("2. Suitable Job Roles:")[1].split("3. Skill Gaps and Weaknesses:")[0].strip()
        sections["Job Roles"] = [clean_markdown(line.strip()) for line in job_roles.split('\n') if line.strip()]

    if "3. Skill Gaps and Weaknesses:" in text and "4. Suggested Improvements:" in text:
        skill_gaps = text.split("3. Skill Gaps and Weaknesses:")[1].split("4. Suggested Improvements:")[0].strip()
        sections["Skill Gaps"] = [clean_markdown(line.strip()) for line in skill_gaps.split('\n') if line.strip()]

    if "4. Suggested Improvements:" in text:
        improvements = text.split("4. Suggested Improvements:")[1].strip()
        sections["Improvements"] = [clean_markdown(line.strip()) for line in improvements.split('\n') if line.strip()]

    return sections


# Function to parse item with label and description
def parse_item_with_label(item):
    """
    Parse items that have a label and description format.
    Example: "Name: John Doe" or "Limited Project Experience: This is a description"
    """
    if ":" in item:
        parts = item.split(":", 1)
        label = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else ""
        return label, desc
    return item, ""


def main():
    local_css()

    # Sidebar with animation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/resume.png", width=80)
        st.title("Resume Analyzer Pro")

        # Add Lottie animation
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_sSF6EG.json"
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, speed=1, height=200, key="sidebar_animation")

        st.markdown("---")

        st.markdown("### About")
        st.info(
            "This tool analyzes your resume and provides personalized insights "
            "to help you improve your job application materials and career prospects."
        )

        st.markdown("### How it works")
        st.markdown(
            "1. Upload your resume (PDF format)\n"
            "2. Our AI will automatically analyze it\n"
            "3. Review the detailed analysis\n"
            "4. Use the insights to improve your resume"
        )

        st.markdown("---")
        st.caption("© 2025 Resume Analyzer Pro")

    # Main content
    st.title("📊 Resume Analysis Tool")
    st.markdown(
        "<p class='highlight'>Upload your resume to receive personalized career insights and improvement suggestions</p>",
        unsafe_allow_html=True
    )

    if not API_TOKEN:
        st.error("⚠️ API token not found in environment variables. Please check your .env file.")
        st.stop()

    # API endpoint
    API_URL = "https://api.langflow.astra.datastax.com/lf/07244700-521b-4e7e-a951-509c8b3161aa/api/v1/run/e200f741-39d5-4ee7-ab2a-5d06a65d161b"

    # File upload card

    st.markdown("### Upload your resume")
    st.markdown("Supported format: PDF")

    uploaded_file = st.file_uploader("", type=["pdf"])

    if uploaded_file:
        # Process the file automatically
        with st.spinner("Analyzing your resume..."):
            try:
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)

                if not resume_text.strip():
                    st.warning("⚠️ No text could be extracted from the PDF. Please check the file.")
                    st.stop()

                # Send to API for analysis
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_TOKEN}"
                }

                payload = {
                    "input_value": resume_text,
                    "output_type": "chat",
                    "input_type": "text"
                }

                response = requests.post(API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    result = response.json()

                    # Parse the result to get the clean analysis text
                    analysis_text = parse_resume_analysis(result)

                    # Extract sections from the analysis text
                    sections = extract_sections(analysis_text)

                    # Store in session state
                    st.session_state.analysis_sections = sections

                    st.success("✅ Resume analysis complete!")
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
                    st.stop()

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.stop()

    st.markdown("</div>", unsafe_allow_html=True)

    # Display results if available
    if 'analysis_sections' in st.session_state and st.session_state.analysis_sections:
        sections = st.session_state.analysis_sections

        # 1. Personal Data Section
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>1. User Name and Personal Data</h3>", unsafe_allow_html=True)

        if sections["Personal Data"]:
            for item in sections["Personal Data"]:
                if item.strip():
                    label, desc = parse_item_with_label(item)
                    if desc:
                        st.markdown(f"""
                        <div class='result-item'>
                            <strong>{label}:</strong> {desc}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-item'>{item}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-item'>No personal data found.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 2. Job Roles Section
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>2. Suitable Job Roles</h3>", unsafe_allow_html=True)

        if sections["Job Roles"]:
            for item in sections["Job Roles"]:
                if item.strip():
                    # Check if this is a role with description (contains a colon)
                    if ":" in item:
                        label, desc = parse_item_with_label(item)

                        st.markdown(f"""
                        <div class='result-item'>
                            <span class='badge badge-primary'>{label}</span>
                            <p>{desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-item'>{item}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-item'>No job roles found.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 3. Skill Gaps Section
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>3. Skill Gaps and Weaknesses</h3>", unsafe_allow_html=True)

        if sections["Skill Gaps"]:
            for item in sections["Skill Gaps"]:
                if item.strip():
                    # Check if this is a skill gap with description (contains a colon)
                    if ":" in item:
                        label, desc = parse_item_with_label(item)

                        st.markdown(f"""
                        <div class='result-item'>
                            <strong>{label}:</strong>
                            <p>{desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-item'>{item}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-item'>No skill gaps found.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 4. Improvements Section
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-header'>4. Suggested Improvements</h3>", unsafe_allow_html=True)

        if sections["Improvements"]:
            for item in sections["Improvements"]:
                if item.strip():
                    # Check if this is an improvement with description (contains a colon)
                    if ":" in item:
                        label, desc = parse_item_with_label(item)

                        st.markdown(f"""
                        <div class='result-item'>
                            <strong>{label}:</strong>
                            <p>{desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-item'>{item}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='result-item'>No improvements found.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()