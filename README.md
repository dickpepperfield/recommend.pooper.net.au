# recommend.pooper.net.au

# Prerequisites

```
Python 39
```

# Required env vars

```
# Open AI API Key
OPENAI_API_KEY=sk_apikeyhere

# Open Movie Database API Key
OMDB_API_KEY=apikeyhere

# Google recaptcha v3 Site Key
RECAPTCHA_SITE_KEY=apikeyhere

# Umami analytics URL and key
UMAMI_URL=https://umami.url/script.js
UMAMI_SITE_KEY=umamikeyhere

# Fontawesome token (https://kit.fontawesome.com/thisparthere.js)
FA_TOKEN=token here
```

# Dev

```
# Create the virtual venv
python -m venv venv

# Install requirements
pip install -U pip
pip install -r requirements.txt

# Fill out env file
cp env.example .env

# Start dev server
python manage.py 
```

# Build and deploy

```
docker compose build

docker compose up -d
```

# License

MIT