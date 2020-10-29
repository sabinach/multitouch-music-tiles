import time, sys
from pygame import mixer

# pygame.init()
mixer.init()

sound = mixer.Sound("wav/c1.wav")
sound.play()


#pygame.mixer.music.load("wav/c1.wav")
#pygame.mixer.music.play(0)

time.sleep(5)