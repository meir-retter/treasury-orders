FROM python:3.11
WORKDIR /src
RUN mkdir /src/main
COPY . .
RUN pip install dash
CMD [ "python3", "./app.py"]