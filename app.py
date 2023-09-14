from flask import Flask, render_template, send_file, request, jsonify
import requests
from dotenv import load_dotenv
import os

from utils.generate_leads import get_leads

app = Flask(__name__)

# load the environment variables from the .env file
load_dotenv()


@app.route('/')
def home():
    url = "https://api.apollo.io/v1/labels"

    querystring = {
        "api_key": os.environ["LABEL_API_KEY"]
    }

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    labels = response.json()

    return render_template('index.html', labels=labels)


@app.route('/download_file', methods=['POST'])
def download_file():
    label_id = request.form['radio-label']
    try:
        _, filename = get_leads(label_id=label_id)
    except requests.exceptions.HTTPError as err:
        print("HTTP Error")
        print(err.args[0])

    return send_file(filename, as_attachment=True)
