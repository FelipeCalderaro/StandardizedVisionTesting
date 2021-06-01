# LIBRARY IMPORTS
from flask import Flask, jsonify, request, make_response, redirect, Response, send_file
from flask_cors import CORS, cross_origin
from base64 import encodebytes
from icecream import ic
from PIL import Image
import telepot

import sendman
import matplotlib.pyplot as plt
import socket
import os
import io


# FILE IMPORTS


##### FLASK SERVER

app = Flask("API's")
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

######## CONFIGS FOR PROGRAMS #########
####### SETUP

bot = telepot.Bot("798595683:AAFP7RqpJifEtSed10w_4fO19c4CTy-wIt8")
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


@app.route("/calculateResults", methods=["POST"])
def calculateResults():
    # try:
    ic(request.json)
    resultContrastValues = request.json["values"]
    fig, ax = plt.subplots()

    ax.plot(range(1, len(resultContrastValues) + 1), resultContrastValues)
    ax.set(
        xlabel="Trial number",
        ylabel="Contrast",
        title=f"{request.json['cycle']} Spacial Frequencies (cycles/degree)",
    )
    ax.set_xlim([0, len(resultContrastValues) + 1])
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

    telegram_send = {
        "values": request.json["values"],
        "upDown": upDown,
    }

    sendman.sendPhoto(sendman.chatIds.calderaro, open("/tmp/results.png", "rb"), bot)
    sendman.sendPhoto(sendman.chatIds.galende, open("/tmp/results.png", "rb"), bot)
    sendman.send(sendman.chatIds.calderaro, f"`{jsonify(telegram_send)}`")
    sendman.send(sendman.chatIds.calderaro, f"`{jsonify(telegram_send)}`")

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
