# LIBRARY IMPORTS
from pprint import pprint
from flask import Flask, jsonify, request, make_response, redirect, Response, send_file
from flask_cors import CORS, cross_origin
from base64 import encodebytes
from datetime import datetime
from pathlib import Path
from icecream import ic
from time import sleep
from uuid import uuid4
from PIL import Image

import matplotlib.pyplot as plt
from psychopy.hardware.crs.bits import status
import psychopy.visual
import psychopy.event
import matplotlib
import requests
import random
import socket
import json
import time
import os
import io


# FILE IMPORTS

import vision

##### FLASK SERVER

app = Flask("API's")
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

######## CONFIGS FOR PROGRAMS #########
####### SETUP

Vision = vision.Vision()
GratingPhases = vision.GratingPhases()


# headers for sending
headers = {"Content-Type": "Application/json"}
###########################

#### FOR FLASK FUNCTIONS ####
def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def encodedImage(image_path):
    pil_img = Image.open(image_path, mode="r")
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format="PNG")
    encoded_img = encodebytes(byte_arr.getvalue()).decode()
    return encoded_img.replace("\n", "")


#############################
#### ROUTES ######
#  DEFAULT ROUTE #
@app.errorhandler(404)
def page_not_found(error):
    return redirect("https://photricity.com/flw/ajax/", code=302)


@app.route("/getImage", methods=["GET"])
def getImages():
    image = encodedImage("./teste0.50.png")
    response = {
        "A": "testando",
        "message": "message",
        "ImageBytes": image,
    }
    return jsonify(response)


@app.route("/getTest", methods=["GET"])
def getTest():
    try:
        grating_size = 300
        padding = grating_size * 0.01
        win = psychopy.visual.Window(
            size=[grating_size + padding, grating_size + padding],
            units="pix",
            fullscr=False,
            color=[2, 2, 1],
        )

        grating = psychopy.visual.GratingStim(
            win=win,
            units="pix",
            size=[grating_size, grating_size],
            # color=[0.5, 1, 0.25],
        )

        contrast = float(request.headers["contrast"])
        cycle = float(request.headers["cycle"])

        results = Vision.generateGrating(
            win,
            grating,
            grating_size,
            contrast,
            cycle / grating_size,
        )
        results["img"] = encodedImage("/tmp/ContrastSensitivity.png")
        results["sf"] = int(cycle)

        return jsonify(results)

    except:
        return Response(status=400)


@app.route("/calculateResults", methods=["POST"])
def calculateResults():
    # try:
    ic(request.json)
    resultContrastValues = request.json["values"]
    fig, ax = plt.subplots()

    ax.plot(range(1, 18), resultContrastValues)
    ax.set(
        xlabel="Trial number",
        ylabel="Contrast",
        title=f"{request.json['cycle']} Spacial Frequencies (cycles/degree)",
    )
    ax.set_xlim([0, 18])
    ax.grid()
    plt.draw()
    plt.savefig("/tmp/results.png")

    upDown = []
    for i in range(len(resultContrastValues)):
        if i - 1 >= 0:
            if resultContrastValues[i] < resultContrastValues[i - 1]:
                upDown.append({"action": "desceu", "index": i})
            elif resultContrastValues[i] == resultContrastValues[i - 1]:
                # upDown.append({"action": "igual", "index": i})
                pass
            else:
                upDown.append({"action": "subiu", "index": i})
        else:
            pass

    change = 0
    up = False
    for a in upDown:
        if a["action"] == "subiu" and not up:
            change = a["index"]
            up = True
        if up and a["action"] == "desceu":
            change = a["index"]
            break

    # Descartando 2 primeiros pontos de reversão e calculando a média do contraste
    subListResult = resultContrastValues[change - 1 :]

    contrastThreshold = sum(subListResult) / len(subListResult)
    sensitivity = 1 / contrastThreshold
    ic(change - 1)
    ic(contrastThreshold)
    ic(sensitivity)

    return jsonify(
        {
            "graph": encodedImage("/tmp/results.png"),
            "contrastThreshold": contrastThreshold,
            "sensitivity": sensitivity,
        }
    )


# except:
#     return "error", 500


@app.route("/generateGraph", methods=["POST"])
def generateChart():
    fig, ax = plt.subplots()

    ax.plot(range(1, 18), request.json["values"])
    ax.set(
        xlabel="Trial number",
        ylabel="Contrast",
        title=f"{request.json['cycle']} Spacial Frequencies (cycles/degree)",
    )
    ax.set_xlim([0, 18])
    ax.grid()
    plt.draw()
    plt.savefig("/tmp/results.png")
    return jsonify({"img": encodedImage("/tmp/results.png")})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 34939))
    # Process(target=someFunction, args=(x,)).start()
    # Process(target=botKeepAlive,).start()
    app.run(host=getIp(), port=port, debug=True, threaded=True)
    # app.run(host="0.0.0.0", port=port)
    # last_update()
