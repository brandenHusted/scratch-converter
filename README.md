## Online Scratch to Python Converter

> Because this project used seleninum to download the scratch file, so it is easier to setup the environment with docker.

### Usage (Intall Docker First)

1. Clone this repo
2. Run `docker build -t flask-scratch-converter .`
3. Run `docker run -p 5000:5000 flask-scratch-converter`
4. Open `http://localhost:5000` in your browser
