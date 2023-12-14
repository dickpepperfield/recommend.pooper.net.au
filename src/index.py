from flask import Flask, request, render_template, make_response
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
from openai import OpenAI
import re
import requests

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
omdb_api_key = os.environ.get("OMDB_API_KEY")
recaptcha_key = os.environ.get("RECAPTCHA_SITE_KEY")
umami_key = os.environ.get("UMAMI_SITE_KEY")
umami_url = os.environ.get("UMAMI_URL")
fa_token = os.environ.get("FA_TOKEN")

app = Flask(__name__)

def default_error_responder(request_limit: RequestLimit):
    return make_response(
        render_template("error.html", request_limit=request_limit, umamu_url=umami_url, umami_key=umami_key, fa_token=fa_token),
        429
    )

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
    storage_options={},
    on_breach=default_error_responder
)

@app.route("/", methods=["GET", "POST"])
@limiter.limit("20/minute")
def index(prompt=None):
    gpt_responses = []
    omdb_urls = []

    if request.method == "POST":
        prompt = request.form["prompt"]
        # Send the request to ChatGPT-4
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """
                    You recommend movies or tv of a specific genre, or similar movies or tv to whats requested, 
                    just provide the list of recommendations, dont provide any other information including messages to the user submitting. 
                    Only provide 10 or less items in your response and ensure that the TV and movies are labelled as to what they are in each response, 
                    including the year they were released - like this (Movie 2020), or (TV Series 1980). 
                    The list should be dashes and the movie or tv name in quotes.
                    If the question does not relate at all to movies or TV or genres, reject the response and say: 
                    Try a different prompt, this doesn't seem to relate to movies or TV.
                    """
                 },
                {"role": "user", "content": f"Recommend based on this: {prompt}" }
            ],
            temperature=0.1
            )

        gpt_responses = response.choices[0].message.content.split('\n')

        # Remove leading dashes and surrounding whitespaces
        gpt_responses = [re.sub(r'^[-\s]+', '', response) for response in gpt_responses]

        # Extract movie/TV titles and years for OMDB search
    for response in gpt_responses:
        title = ""
        year = ""
        matches = re.findall(r'(.+?)(?: \((\w+) \d+\))', response)
        if matches:
            title, year = matches[0]
        omdb_url = get_omdb_url(title, year, omdb_api_key)
        omdb_urls.append(omdb_url)

    return render_template(
        "index.html", 
        gpt_responses=gpt_responses, 
        omdb_urls=omdb_urls, 
        prompt=prompt, 
        zip=zip,
        umamu_url=umami_url,
        umami_key=umami_key,
        recaptcha_key=recaptcha_key,
        fa_token=fa_token
        )

@app.route('/about/')
def about():
    return render_template('about.html', umamu_url=umami_url, umami_key=umami_key, fa_token=fa_token)

@app.route('/contact/')
def contact():
    return render_template('contact.html', umamu_url=umami_url, umami_key=umami_key, recaptcha_key=recaptcha_key, fa_token=fa_tokens)

def get_omdb_url(title, year, omdb_api_key):
    base_url = f"https://www.omdbapi.com/?apikey={omdb_api_key}"
    url = f"{base_url}&t={title}&y={year}"

    try:
        response = requests.get(url)
        data = response.json()
        if data["Response"] == "True":
            return f"https://www.imdb.com/title/{data['imdbID']}"
    except Exception:
        return None

