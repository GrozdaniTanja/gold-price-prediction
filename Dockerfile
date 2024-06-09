FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . /app
ENV DAGSHUB_API_TOKEN = 3def17bd6cacf587ec01861510ecdbca35ee2eed


EXPOSE 5000

CMD ["python", "src/serve/rest.py", "--host", "0.0.0.0", "--port", "5000"]