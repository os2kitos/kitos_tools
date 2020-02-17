FROM python:3-alpine

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN pip install -e kitos_tools/

CMD python service/app.py
