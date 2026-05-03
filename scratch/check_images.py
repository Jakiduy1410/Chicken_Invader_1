import pygame
import os

pygame.init()

assets_path = r'd:\Chicken_Invader\assets\image'
files = ['27.png', 'step_1.png', 'step_2_1.png', 'step_2_2.png']

for f in files:
    p = os.path.join(assets_path, f)
    if os.path.exists(p):
        img = pygame.image.load(p)
        print(f"{f}: {img.get_width()}x{img.get_height()}")
    else:
        print(f"{f}: NOT FOUND")

pygame.quit()
