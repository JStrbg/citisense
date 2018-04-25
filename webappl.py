import os
from flask import Flask
#https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/4
#https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

def read_log():
    log_content = "Time, Temp, CO2, TVOC, Rain, Noise"
    try:
        with open("/media/pi/KINGSTON/data_log.csv") as file:
            for line in file:
                log_content += '\n' + line
        return log_content
    except IOError:
        print("USB-mem IO-Err webapp")
        return "IO Error USB-mem webapp"

app = Flask(__name__)
@app.route('/')
def index():
    return read_log()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int("80"))
