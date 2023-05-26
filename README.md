# GPT Programmer

## Initial Setup

Prepare python env:
```sh
conda create --name llm-programmer
conda activate llm-programmer
pip install -r backend/requirements.txt
```

## API credentials setup

This application uses OpenAI's GPT the OpenAI API.
You'll need to configure the API credentials.
To do so, create a `.env` file based on `.env.sample`.

## Running

Backend:
```sh
cd backend/

# Create an empty git repo to work in
mkdir workspace
cd workspace
git init

cd ..

# Either
docker-compose up
# or
uvicorn main:app --reload
```

Frontend:
```sh
cd frontend/
npm ci
npm run dev
```

# TODO

- [ ] do not include .env in Dockerfile (add to .dockerignore)