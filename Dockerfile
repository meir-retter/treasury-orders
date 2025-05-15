FROM python:3.9
WORKDIR /src
RUN mkdir /src/main
COPY . .
RUN pip install dash
CMD [ "python3", "./app.py"]