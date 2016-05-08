from __future__ import division 
"""
Entry point for running car model simulation.

To run:
    python main.py <fastIterations>
        Args:
            -fastIterations (optional): specifies the number of iterations to 
                run before displaying to viewing window (significantly faster).
                If no command line arguments are entered, just begin running in
                display mode.

Modules required:
pygame
"""

import pygame
from pygame.math import Vector2
from car import Car
from obstacle import Obstacle
from geometry import calculateIntersectPoint
import math
import sys
import time
import os

#############
# Constants #
#############

LOG_PATH = "./log_data/output.csv"

# RGB color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Screen parameters
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
SCREEN_CENTER = (700/2, 500/2)

# Car parameters
CAR_PARAMS = {
    "position": Vector2(350, 250),
    "velocity": Vector2(0, -2),
    "turn_radius": 3,
    "sensor_length": 200,
    "load_state_path": None,
    "log_state": False
}

# Obstacle parameters
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
 
def main(args):
    """
    Main method (entry point into program)
    """

    print "running %s" % args[0]

    #Check command line args - if int command line arg is provided,
    #run in simulation mode for that number of iterations.
    SIMULATION = None
    if len(args) > 1:
        SIMULATION = int(args[1])
        print "simulating %s iterations before displaying..." % SIMULATION

    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
     
    #initialize pygame
    pygame.init()

    # Set the width and height of the screen [width, height]
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)
    
    # Set the caption on the screen window
    pygame.display.set_caption("Car Simulation")
     
    # Loop until the user clicks the close button.
    done = False
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Initialize Car object
    c = Car(CAR_PARAMS)

    # Initialize HUD variables
    trial_num = 1
    start_time = time.time()
    cur_time = time.time()
    elapsed_time = (cur_time - start_time)
    best_time = -1.0
    num_frames = 0

    # Initialize obstacles
    obstacles = generate_obstacles()
     
    # -------- Main Program Loop -----------
    while not done:
        # --- Main event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
     
        # --- Simulation logic

        # Keypress handling used for testing
        handle_keypresses(c)

        # Update car location based on obstacle state
        (sensor_hits, did_reset) = c.update(obstacles, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # If the car crashed...
        if did_reset:
            # Increment trial count
            trial_num += 1
            # Reset start time
            start_time = time.time()
            # Update best time, if necessary
            if elapsed_time > best_time:
                best_time = elapsed_time

            # Log num frames survived
            with open(LOG_PATH, "a+") as f:
                f.write(str(num_frames) + ",")

            num_frames = 0

        # Update elapsed time
        cur_time = time.time()
        elapsed_time = (cur_time - start_time)
     
        # --- Screen-clearing code goes here

        screen.fill(BLACK)
     
        # --- Drawing code should go here

        num_frames += 1

        # Skip drawing on simulation (speed up early exploration)
        if SIMULATION is not None and trial_num < SIMULATION:
            # Print to how far along training is
            if trial_num % 50 == 0:
                print "epoch: %s" % trial_num
            # Jumps to top of loop without running drawing logic
            continue

        # DRAW CAR
        pygame.draw.circle(screen, WHITE, c.get_position(), 5, 0)

        # DRAW CAR SENSORS
        for i in range(len(c.sensors)):
            pygame.draw.line(screen, WHITE, c.get_position(), c.get_sensor_endpoint(i))

        # DRAW OBSTACLES
        for o in obstacles:
            pygame.draw.line(screen, WHITE, o.p1, o.p2)
            pygame.draw.line(screen, WHITE, o.p2, o.p3)
            pygame.draw.line(screen, WHITE, o.p3, o.p4)
            pygame.draw.line(screen, WHITE, o.p4, o.p1)
            o.update(size)

        # DRAW SENSOR DETECTION POINTS
        for i in range(5):
            s_hit = sensor_hits[i]["point"]
            if s_hit:
                pygame.draw.circle(screen, RED, s_hit, 5, 0)

        # DRAW HUD
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
    """
    Handles keypresses, updating car object if necessary
        (used for testing)
    """
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_LEFT]:
        car.turn_left()
    if pressed[pygame.K_RIGHT]:
        car.turn_right()

def compute_obstacle_radius(obs_pt, center):
    """
    Helper method for computing radius of object from center of screen (used to
        calculate angular velocity)
    """
    return math.sqrt((obs_pt[0] - center[0]) * (obs_pt[0] - center[0]) + (obs_pt[1] - center[1]) * (obs_pt[1] - center[1]))

def compute_obstacle_angle(obs_pt, center):
    """
    Helper method for computing angle of object from horizontal vector extending
    from center of screen to right of screen (used to calculate angular velocity)
    """
    theta =  math.degrees(math.atan2(-(obs_pt[1] - center[1]), obs_pt[0] - center[0]))
    if theta < 0:
        theta += 360
    return theta

def generate_obstacles():

    """
    Initializes and returns array of obstacles.
    Commented out regions indicate previous obstacle configurations
    """

    obstacles = []

    #static objects

    # obstacles.append(Obstacle(Vector2(100, 100), Vector2(150, 100), Vector2(150, 150), Vector2(100, 150), 135))
    # obstacles.append(Obstacle(Vector2(350, 50), Vector2(400, 50), Vector2(400, 100), Vector2(350, 100), 90))
    # obstacles.append(Obstacle(Vector2(600, 100), Vector2(650, 100), Vector2(650, 150), Vector2(600, 150), 45))
    # obstacles.append(Obstacle(Vector2(200, 200), Vector2(250, 200), Vector2(250, 250), Vector2(200, 250), 0))
    # obstacles.append(Obstacle(Vector2(300, 100), Vector2(350, 100), Vector2(350, 150), Vector2(300, 150), 20))
    # obstacles.append(Obstacle(Vector2(400, 100), Vector2(450, 100), Vector2(450, 150), Vector2(400, 150), 40))
    # obstacles.append(Obstacle(Vector2(400, 200), Vector2(450, 200), Vector2(450, 250), Vector2(400, 250), 60))
    # obstacles.append(Obstacle(Vector2(100, 200), Vector2(150, 200), Vector2(150, 250), Vector2(100, 250), 80))
   
    #moving objects

    # base_coords = [(100, 100), (600, 100), (100, 400), (600, 400),
    #                 (200, 100), (500, 100), (200, 400), (500, 400),
    #                 (300, 100), (400, 100), (300, 400), (400, 400),
    #                 (100, 200), (600, 200), (100, 300), (600, 300),
    #                 (100, 300), (600, 300), (100, 200), (600, 200),
    #                 (200, 200), (500, 200), (200, 300), (500, 300),
    #                 ]

    base_coords = [(200, 250), (500, 250), (350, 100), (350, 400)]

    for coord in base_coords:
        base_pt = Vector2(coord[0], coord[1])
        obstacles.append(Obstacle(base_pt, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, compute_obstacle_radius(base_pt, SCREEN_CENTER), compute_obstacle_angle(base_pt, SCREEN_CENTER))) 

    return obstacles

#Run program
if __name__ == "__main__":
    main(sys.argv)