import psychopy.visual
import psychopy.event
from time import sleep

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
)


sf = 12 / grating_size
rotation = [
    0,
    45,
    -45,
    0,
    45,
    0,
    45,
    -45,
    45,
]
a = 0.5
contrast = [0.5]
for i in range(9):
    a /= 2
    contrast.append(a)

for r in rotation:
    for c in contrast:
        grating.sf = sf
        grating.contrast = c
        grating.ori = r
        grating.draw()
        win.flip()

        win.getMovieFrame()
        win.saveMovieFrames(f"T_IMG_{r}_{c}.png")
        sleep(1)

win.close()