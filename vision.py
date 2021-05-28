from psychopy.logging import data
import psychopy.visual
import psychopy.event

import random
from icecream import ic

import numpy as np
import seaborn as sns

import matplotlib
import matplotlib.pyplot as plt

########################
# Data needed to be save
# - Spatial frequency (Wavelength)
# - Contrast (Amplitute)
# - Orientation
# - User response to the group of elements above
########################


class GratingPhases:
    CSV_1000E_Standart = (3, 6, 12, 18)
    # CSV_1000E_Standart = (3,)
    allowedRotation_R = (5, 65)
    allowedRotation_L = (-5, -65)


class Vision:
    def calculateIfRotated(self):
        leftRotation = random.randint(
            GratingPhases.allowedRotation_L[1], GratingPhases.allowedRotation_L[0]
        )
        rightRotation = random.randint(
            GratingPhases.allowedRotation_R[0], GratingPhases.allowedRotation_R[1]
        )

        if random.randint(0, 1) == 1:
            return leftRotation if random.randint(0, 1) == 0 else rightRotation
        else:
            return 0

    def generateGrating(self, win, grating, size, contrast, sf, rotation):
        # contrast = round(random.uniform(0, 0.6), 2)
        # contrast = 0.03

        grating.sf = sf
        # grating.mask = "cicrle"
        grating.contrast = contrast
        grating.ori = rotation
        # grating.phase = 0.5
        grating.draw()
        win.flip()

        win.getMovieFrame()
        win.saveMovieFrames("/tmp/ContrastSensitivity.png")
        win.close()
        # ic(rotation)
        # ic(contrast)
        return {
            "contrast": contrast,
            "rotation": rotation,
        }

    def CalculateThresholdAndSensitivity(self, win, grating, grating_size, cycle):
        result = []
        hits = 0
        contrast = 0.5
        for i in range(18):
            trialResult = {
                "values": self.generateGrating(
                    win,
                    grating,
                    grating_size,
                    contrast,
                    cycle / grating_size,
                )
            }
            trialResult["key"] = psychopy.event.waitKeys(
                keyList=["left", "right", "up"]
            )[0]
            if trialResult["key"] == "right" and trialResult["values"][
                "rotation"
            ] in range(
                GratingPhases.allowedRotation_R[0], GratingPhases.allowedRotation_R[1]
            ):
                trialResult["correct_result"] = True
                hits += 1
                if hits == 2:
                    contrast /= 2
                    hits = 0

            elif trialResult["key"] == "left" and trialResult["values"][
                "rotation"
            ] in range(
                GratingPhases.allowedRotation_L[1], GratingPhases.allowedRotation_L[0]
            ):
                trialResult["correct_result"] = True
                hits += 1
                if hits == 2:
                    contrast /= 2
                    hits = 0

            elif trialResult["key"] == "up" and trialResult["values"]["rotation"] == 0:
                trialResult["correct_result"] = True
                hits += 1
                if hits == 2:
                    contrast /= 2
                    hits = 0

            else:
                trialResult["correct_result"] = False
                hits = 0
                contrast = contrast * 2 if contrast * 2 <= 0.5 else contrast

            result.append(trialResult)

        fig, fig = plt.subplots()

        fig.plot(range(1, 19), [i["values"]["contrast"] for i in result])
        fig.set(
            xlabel="Trial number",
            ylabel="Contrast",
            title=f"{cycle} Spacial Frequencies (cycles/degree)",
        )
        fig.set_xlim([0, 19])
        fig.grid()
        plt.draw()

        # to save image
        # win.getMovieFrame()
        # win.saveMovieFrames("teste.png")

        # win.close()

        # Calculate the median for the inflection points
        resultContrastValues = [i["values"]["contrast"] for i in result]
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

        ic(contrastThreshold)
        ic(sensitivity)

        # plt.show(block=False)

        return cycle, contrastThreshold, sensitivity, resultContrastValues


# def generateGraphs(results):


# def main():
#     grating_size = 400
#     padding = grating_size * 0.22
#     win = psychopy.visual.Window(
#         size=[grating_size + padding, grating_size + padding],
#         units="pix",
#         fullscr=False,
#         color=[1, 1, 1],
#     )

#     grating = psychopy.visual.GratingStim(
#         win=win,
#         units="pix",
#         size=[grating_size, grating_size],
#     )

#     overallResults = []

#     for cycle in GratingPhases.CSV_1000E_Standart:
#         overallResults.append(
#             CalculateThresholdAndSensitivity(win, grating, grating_size, cycle)
#         )

#     ic(overallResults)
#     # generateGraphs([results[-1] for results in overallResults])
#     plt.show()


# def main():
#     testValues = np.array(
#         [
#             0.5,
#             0.25,
#             0.25,
#             0.125,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.25,
#             0.125,
#             0.125,
#             0.0625,
#             0.0625,
#         ]
#     )

#     ic(len(testValues))

#     sns.set_theme(style="darkgrid")
#     fig = sns.relplot(
#         x=range(0, 17),
#         y=testValues,
#         kind="line",
#     )
#     fig.fig.set_size_inches(8, 4)
#     fig.height = 10

#     plt.tight_layout()
#     plt.subplots_adjust(top=0.9)
#     plt.xlabel("Numero de imagens")
#     plt.ylabel("Contraste")
#     # plt.figure(figsize=(10, 8))
#     plt.show()


if __name__ == "__main__":
    main()