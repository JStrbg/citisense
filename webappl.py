import os
from flask import Flask
#https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/4
#https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

def read_log():
    log_content = ""
    try:
        with open("/home/pi/citisense/logs/data_log.csv") as file:
            for line in file:
                log_content += line + "<br/>"
        return log_content
    except IOError:
        print("IO-Err webapp")
        return "IO Error webapp"

app = Flask(__name__)
@app.route('/')
def index():
    return read_log()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("80"))
