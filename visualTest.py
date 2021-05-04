import psychopy.visual
import psychopy.event


win = psychopy.visual.Window(
    size=[300, 300],
    units="pix",
    fullscr=False,
    # color=[0.75, 0.75, 0.75],
    color="white",
)

grating = psychopy.visual.GratingStim(
    win=win,
    units="pix",
    size=[250, 250],
)


grating.sf = 6 / 250
grating.mask = "circle"
grating.ori = 45
grating.contrast = 0.005

grating.draw()
win.flip()


while True:
    x = 1