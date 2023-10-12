from flask import Flask, request, render_template, redirect, url_for
import re
import time
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Constants
ALLOWED_IDNP = ['2002500133457', '2006048027786']
ERROR_MESSAGE = "Codul personal este introdus gresit."
URL = "http://studentcrd.usm.md/"

def fetch_student_data(IDNP):
    """
    Fetch student data from the given URL using the provided IDNP.
    
    Args:
    - IDNP (str): The student's IDNP.
    
    Returns:
    - str: The content of the student data if found, otherwise an error code.
    """
    # Send a GET request to the website to get the initial form data
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract necessary data for POST request
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    form_data = {
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'txtCodperson': IDNP,
        'btLogin': 'Login'
    }

    # Send a POST request with the form data
    response = requests.post(URL, data=form_data)
    time.sleep(5)  # Wait for the response

    soup = BeautifulSoup(response.text, 'html.parser')
    error_span = soup.find('span', {'id': 'lbErr', 'text': 'Codul personal nu corect'})

    if error_span:
        return 808

    div_content = soup.find('div', {'id': 'nav-tabContent'})
    return str(div_content)

@app.route('/')
def index():
    """Redirect to the home route."""
    return redirect(url_for('home'))

@app.route('Users/Students.aspx', methods=['GET', 'POST'])
def home():
    """Render the student data or the index page based on the provided IDNP."""
    if request.method == 'POST':
        IDNP = request.form.get('txtCodperson')
        
        if re.match(r'^\d{13}$', IDNP):
            if IDNP in ALLOWED_IDNP:
                student_path = f"students/{IDNP}.html"
                with open(student_path, "r") as student_info:
                    data = student_info.read()
                    return render_template('base.html', tab_content=data)
            else:
                data = fetch_student_data(IDNP)
                if data == 808:
                    return render_template('index.html', error_message=ERROR_MESSAGE)
                return render_template('base.html', tab_content=data)
        else:
            return render_template('index.html', error_message=ERROR_MESSAGE)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
