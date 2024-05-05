FROM python:3.12-slim

WORKDIR /usr/src/app
RUN chmod -R 777 .
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -y && apt upgrade -y
RUN apt-get -qq -y install software-properties-common
RUN apt-get -qq -y install postgresql
RUN apt install postgresql-contrib -y
RUN apt install gcc -y
RUN apt install python3-dev -y
RUN apt install musl-dev -y

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh


COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]