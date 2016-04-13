from __future__ import division 
"""
 Pygame base template for opening a window
 
 Sample Python/Pygame Programs
 Simpson College Computer Science
 http://programarcadegames.com/
 http://simpson.edu/computer-science/
 
 Explanation video: http://youtu.be/vRB_983kUMc
"""
 
import pygame
from pygame.math import Vector2
from car import Car
from obstacle import Obstacle
from geometry import calculateIntersectPoint
import math
import sys
import time
 
def main():
    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
     
    pygame.init()
     
    # Set the width and height of the screen [width, height]
    size = (700, 500)
    screen = pygame.display.set_mode(size)
     
    pygame.display.set_caption("Car Simulation")
     
    # Loop until the user clicks the close button.
    done = False
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Initialize car
    c = Car(Vector2(350, 250), Vector2(0, -3), 3)
    trial_num = 1
    start_time = time.time()
    cur_time = time.time()
    elapsed_time = (cur_time - start_time)
    best_time = -1.0

    # Initialize obstacles
    obstacles = generate_obstacles()
     
    # -------- Main Program Loop -----------
    while not done:
        # --- Main event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
     
        # --- Game logic should go here
        handle_keypresses(c)
        (sensor_hits, did_reset) = c.update(obstacles, (700, 500))
        if did_reset:
            trial_num += 1
            start_time = time.time()
            if elapsed_time > best_time:
                best_time = elapsed_time

        cur_time = time.time()
        elapsed_time = (cur_time - start_time)
     
        # --- Screen-clearing code goes here
     
        # Here, we clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
     
        # If you want a background image, replace this clear with blit'ing the
        # background image.
        screen.fill(BLACK)
     
        # --- Drawing code should go here

        #CAR
        pygame.draw.circle(screen, WHITE, c.get_position(), 5, 0)
        for i in range(len(c.sensors)):
            pygame.draw.line(screen, WHITE, c.get_position(), c.get_sensor_endpoint(i))

        #OBSTACLES
        for o in obstacles:
            pygame.draw.line(screen, WHITE, o.p1, o.p2)
            pygame.draw.line(screen, WHITE, o.p2, o.p3)
            pygame.draw.line(screen, WHITE, o.p3, o.p4)
            pygame.draw.line(screen, WHITE, o.p4, o.p1)

        #SENSOR TRIP
        for i in range(5):
            s_hit = sensor_hits[i]["point"]
            if s_hit:
                pygame.draw.circle(screen, RED, s_hit, 5, 0)

        # #HUD
        hud_str = """Trial: %s     Elapsed Time: % 6.2f     Best Time: % 6.2f""" % (trial_num, elapsed_time, best_time)
        font = pygame.font.Font(None, 36)
        text = font.render(hud_str, 1, WHITE)
        textrect = text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.centery = 490
        screen.blit(text, textrect)
        
     
        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
     
        # --- Limit to 60 frames per second
        clock.tick(60)
     
    # Close the window and quit.
    pygame.quit()


def handle_keypresses(car):
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        car.turn_left()
    if pressed[pygame.K_RIGHT]:
        car.turn_right()

def generate_obstacles():
    obstacles = []
    obstacles.append(Obstacle(Vector2(100, 100), Vector2(150, 100), Vector2(150, 150), Vector2(100, 150)))
    obstacles.append(Obstacle(Vector2(200, 200), Vector2(250, 200), Vector2(250, 250), Vector2(200, 250)))
    obstacles.append(Obstacle(Vector2(300, 100), Vector2(350, 100), Vector2(350, 150), Vector2(300, 150)))
    obstacles.append(Obstacle(Vector2(400, 100), Vector2(450, 100), Vector2(450, 150), Vector2(400, 150)))
    obstacles.append(Obstacle(Vector2(400, 200), Vector2(450, 200), Vector2(450, 250), Vector2(400, 250)))
    obstacles.append(Obstacle(Vector2(100, 200), Vector2(150, 200), Vector2(150, 250), Vector2(100, 250)))
    return obstacles





if __name__ == "__main__":
    main()