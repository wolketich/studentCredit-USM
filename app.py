from flask import Flask, request, render_template, redirect, url_for
import re, time, requests
from bs4 import BeautifulSoup


allowed_IDNP = ['2002500133457', '2006048027786']
error_message = "Codul personal este introdus gresit."
global data

app = Flask(__name__)

def GetData(IDNP):
    url = "http://studentcrd.usm.md/"
    login_url = url  # The same URL is used for login

    # Send a GET request to the website to get the initial form data
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract __VIEWSTATE and __EVENTVALIDATION from the hidden input fields
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    # Prepare the form data for the POST request
    form_data = {
        '__VIEWSTATE': viewstate,
        '__EVENTVALIDATION': eventvalidation,
        'txtCodperson': IDNP,
        'btLogin': 'Login'
    }

    # Send a POST request with the form data to simulate button click
    response = requests.post(login_url, data=form_data)

    # Wait for the next page to load (you may need to adjust the time if necessary)
    time.sleep(5)

    # Parse the content of the new page after the POST request
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check if the span with id "lbErr" and text "Codul personal nu corect" exists
    error_span = soup.find('span', {'id': 'lbErr', 'text': 'Codul personal nu corect'})

    # If the error span exists, return 808
    if error_span:
        return 808

    # Extract the content of the div with id "nav-tabContent"
    div_content = soup.find('div', {'id': 'nav-tabContent'})

    # Return the content of the div as a string
    return str(div_content)
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/Users/Student.aspx', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        IDNP = request.form.get('txtCodperson')
        if re.match(r'^\d{13}$', IDNP):
            if IDNP in allowed_IDNP:
                student_path = "students/" + IDNP + ".html"
                with open(student_path, "r") as student_info:
                    data = student_info.read()
                    return render_template('base.html', tab_content=data)
            else:
                data = GetData(IDNP)
                if data == None:
                    return render_template('index.html', error_message=error_message)
                return render_template('base.html', tab_content=GetData(IDNP))
        else:
            return render_template('index.html', error_message=error_message)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)