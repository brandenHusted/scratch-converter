FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update && \
        apt-get install -y gcc && \
        apt-get install -y build-essential libssl-dev libffi-dev \ 
        libxml2 libxml2-dev libxslt1-dev zlib1g-dev libcurl4-openssl-dev && \
        apt install -y ./public/chrome.deb && \
        chmod 777 ./public/chromedriver

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "./main.py"]
