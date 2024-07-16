# Talk to your website

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Given a website URL, we want to have a conversational interface to talk to URL content.

# Getting started

0. Add API key to .env file
```
echo 'GROQ_API_KEY="XXXX"' >> .env
```

1. Create a virtual environment:
```
virtualenv .venv
source .venv/bin/activate
```

2. Install requirements:
```
make requirements
```

3. Running the SDK:
- Read the [notebook](notebooks/1.0-pto-url-chat-sdk-and-api.ipynb)

4. Running the API:

```
cd src
uvicorn api:app --reload --port 8001
curl -X POST "http://127.0.0.1:8001/index-url/" -H "Content-Type: application/json" -d '{"url": "https://en.wikipedia.org/wiki/Brazil"}'
curl -X POST "http://127.0.0.1:8001/ask/" -H "Content-Type: application/json" -d '{"url": "https://en.wikipedia.org/wiki/Brazil", "question": "what is the population of Brazil?"}'
```

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for talk_to_your_website
│                         and configuration for tools like black
│
├── references         <- Coding exercise explanation
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src                <- Source code for use in this project.
    │
    ├── __init__.py    <- Makes src a Python module
    │
    ├── api.py         <- Scripts to generate endpoint API
    │
    └── url_chat.py    <- Scripts to create url augmented QA model
```

--------

