FROM python:3.10.0-slim-buster
WORKDIR /app
COPY . .

RUN pip3 --version
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000","--noreload"]
