# GPT Programmer

## Initial Setup

Prepare python env:
```sh
conda create --name gpt-programmer
conda activate gpt-programmer
pip install -r requirements.txt
```

## API credentials setup

This application uses OpenAI's GPT from an Azure Cloud deployment.
You'll need to configure these credentials.
To do so, create a `.env` file based on `.env.sample`.

## Running

```sh
uvicorn main:app --reload
```
