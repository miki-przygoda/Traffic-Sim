import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# Calculate road positions
NUMBER_OF_LANES = 5


# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
LANE_WIDTH = 60  # Width of a single lane
CAR_WIDTH = 40
CAR_HEIGHT = 60
CAR_SPEED = 3
MOTORWAY_SPACING = 150  # Space between motorways

# Junction constants (for simulation 2)
JUNCTION_VERTICAL_ROAD_X = WINDOW_WIDTH // 2 - LANE_WIDTH // 2  # Center of vertical road
JUNCTION_HORIZONTAL_ROAD_Y = WINDOW_HEIGHT // 2  # Center of horizontal road
TURN_RADIUS = LANE_WIDTH * 0.50  # Smaller radius for tighter turns

# Spawn time options
SPAWN_TIMES = [2.0, 1.5, 1.0, 0.5]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (34, 139, 34)  # Forest green for the background

# Car colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
CAR_COLORS = [RED, BLUE, YELLOW, PINK, ORANGE]


TOTAL_ROAD_WIDTH = LANE_WIDTH * NUMBER_OF_LANES  # Width for 3 lanes
LEFT_ROAD_START_X = (WINDOW_WIDTH - MOTORWAY_SPACING - 2 * TOTAL_ROAD_WIDTH) // 2
RIGHT_ROAD_START_X = LEFT_ROAD_START_X + TOTAL_ROAD_WIDTH + MOTORWAY_SPACING

class Car:
    def __init__(self, lane, y_pos, direction="down"):
        self.lane = lane
        self.direction = direction
        if direction == "down":
            self.x = LEFT_ROAD_START_X + (LANE_WIDTH * lane) + (LANE_WIDTH - CAR_WIDTH) // 2
            self.speed = CAR_SPEED
            self.y = -CAR_HEIGHT  # Start above screen
        else:  # direction == "up"
            self.x = RIGHT_ROAD_START_X + (LANE_WIDTH * lane) + (LANE_WIDTH - CAR_WIDTH) // 2
            self.speed = -CAR_SPEED  # Negative speed for upward movement
            self.y = WINDOW_HEIGHT  # Start below screen
        self.color = random.choice(CAR_COLORS)

    def move(self):
        # Apply consistent speed regardless of direction
        self.y += self.speed
        
        # Return True if car should be removed
        if self.direction == "down":
            return self.y > WINDOW_HEIGHT
        else:
            return self.y < -CAR_HEIGHT

    def draw(self, screen):
        if self.direction == "down":
            # Only draw the part of the car that has entered the screen from the top
            if self.y < 0:
                visible_height = CAR_HEIGHT + self.y
                if visible_height <= 0:
                    return
                pygame.draw.rect(screen, self.color, 
                               (self.x, 0, 
                                CAR_WIDTH, visible_height))
            # Only draw the part of the car that hasn't left the screen at the bottom
            elif self.y > WINDOW_HEIGHT - CAR_HEIGHT:
                visible_height = WINDOW_HEIGHT - self.y
                if visible_height <= 0:
                    return
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, 
                                CAR_WIDTH, visible_height))
            # Draw the full car when completely in view
            else:
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, 
                                CAR_WIDTH, CAR_HEIGHT))
        else:  # direction == "up"
            # Only draw the part of the car that has entered the screen from the bottom
            if self.y > WINDOW_HEIGHT - CAR_HEIGHT:
                visible_height = WINDOW_HEIGHT - self.y
                if visible_height <= 0:
                    return
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, 
                                CAR_WIDTH, visible_height))
            # Only draw the part of the car that hasn't left the screen at the top
            elif self.y < 0:
                visible_height = self.y + CAR_HEIGHT
                if visible_height <= 0:
                    return
                pygame.draw.rect(screen, self.color, 
                               (self.x, 0, 
                                CAR_WIDTH, visible_height))
            # Draw the full car when completely in view
            else:
                pygame.draw.rect(screen, self.color, 
                               (self.x, self.y, 
                                CAR_WIDTH, CAR_HEIGHT))

class JunctionCar:
    def __init__(self, start_pos, direction):
        self.x, self.y = start_pos
        self.direction = "down"  # Always start moving down
        self.color = random.choice(CAR_COLORS)
        self.speed = CAR_SPEED
        
        # Initialize turning parameters
        self.turning = False
        self.turn_progress = 0  # 0 to 1, used for turning animation
        self.turn_direction = None  # Will be set when reaching junction
        self.turn_complete = False
        
        # Arc parameters (will be set when turning starts)
        self.pivot_x = 0  # Fixed pivot point x
        self.pivot_y = 0  # Fixed pivot point y
        self.initial_x = 0  # Store initial position relative to pivot
        self.initial_y = 0
        
    def start_turn(self):
        self.turning = True
        self.turn_direction = random.choice(["straight", "left", "right"])
        
        if self.turn_direction == "straight":
            self.turning = False
            return
        
        # Set pivot points at the corners of the junction
        if self.turn_direction == "right":
            # For right turn, pivot at inner corner of vertical and horizontal roads
            self.pivot_x = JUNCTION_VERTICAL_ROAD_X + LANE_WIDTH
            self.pivot_y = JUNCTION_HORIZONTAL_ROAD_Y
        else:  # left turn
            # For left turn, pivot at inner corner of vertical and horizontal roads
            self.pivot_x = JUNCTION_VERTICAL_ROAD_X
            self.pivot_y = JUNCTION_HORIZONTAL_ROAD_Y
        
        # Store initial position for proper alignment
        self.initial_x = self.x + CAR_WIDTH/2
        self.initial_y = self.y + CAR_HEIGHT

    def move(self):
        if not self.turning:
            # Move straight down until reaching junction or after choosing straight
            if self.y < JUNCTION_HORIZONTAL_ROAD_Y - CAR_HEIGHT:
                self.y += self.speed
            elif not self.turn_direction:  # Haven't decided direction yet
                self.start_turn()
            else:  # Going straight through junction
                self.y += self.speed
        elif not self.turn_complete:
            # Handle turning motion
            self.turn_progress += 0.02
            angle = self.turn_progress * math.pi / 2  # 0 to 90 degrees
            
            if self.turn_direction == "right":
                # Calculate position along the arc - stay within road
                arc_radius = LANE_WIDTH * 0.5  # Keep within the lane width
                new_x = self.pivot_x - arc_radius * math.sin(angle)
                new_y = self.pivot_y + arc_radius - arc_radius * math.cos(angle)
                
                # Position the car's top-left corner
                self.x = new_x - CAR_WIDTH/2
                self.y = new_y - CAR_HEIGHT/2
            else:  # left turn
                # Calculate position along the arc - stay within road
                arc_radius = LANE_WIDTH * 0.5  # Keep within the lane width
                new_x = self.pivot_x + arc_radius * math.sin(angle)
                new_y = self.pivot_y + arc_radius - arc_radius * math.cos(angle)
                
                # Position the car's top-left corner
                self.x = new_x - CAR_WIDTH/2
                self.y = new_y - CAR_HEIGHT/2

            if self.turn_progress >= 1:
                self.turn_complete = True
                self.direction = self.turn_direction
                # Align with horizontal road
                self.y = JUNCTION_HORIZONTAL_ROAD_Y + (LANE_WIDTH - CAR_WIDTH) // 2
                if self.turn_direction == "left":
                    self.x = self.pivot_x - CAR_HEIGHT
                else:  # right
                    self.x = self.pivot_x
        else:
            # Continue straight after completing turn
            if self.direction == "left":
                self.x -= self.speed
            else:  # right
                self.x += self.speed

        # Remove conditions
        if self.direction == "left" and self.x < -CAR_WIDTH:
            return True
        elif self.direction == "right" and self.x > WINDOW_WIDTH:
            return True
        elif self.direction == "down" and self.y > WINDOW_HEIGHT:  # For straight-moving cars
            return True
        return False

    def draw(self, screen):
        if (self.turning or self.turn_complete) and self.turn_direction != "straight":
            # Draw the car with height and width swapped to maintain driving direction
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, CAR_HEIGHT, CAR_WIDTH))
        else:
            # Draw the car vertically before turning or when going straight
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, CAR_WIDTH, CAR_HEIGHT))

class TrafficSimulator:
    def __init__(self, num_lanes):
        self.num_lanes = num_lanes
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Traffic Simulator")
        self.left_cars = []  # Cars moving down (Simulation 1)
        self.right_cars = [] # Cars moving up (Simulation 1)
        self.junction_cars = []  # Cars for junction (Simulation 2)
        self.clock = pygame.time.Clock()
        self.last_spawn_time = time.time()
        self.spawn_time_index = 0
        self.current_spawn_time = SPAWN_TIMES[self.spawn_time_index]
        self.paused = True
        self.status_font = pygame.font.Font(None, 28)
        self.controls_font = pygame.font.Font(None, 24)
        self.current_simulation = 1
        self.total_simulations = 2
        
        # Lane-based tracking for spawn times
        self.lane_next_spawn_times = {
            "left": [0] * self.num_lanes,  # Next spawn time for each left lane
            "right": [0] * self.num_lanes  # Next spawn time for each right lane
        }
        
        # Spawn time multipliers to choose from
        self.spawn_time_multipliers = [1.25, 1.5, 1.75, 2.0]
        
        # Legacy variables kept for compatibility
        self.queued_left_cars = []
        self.queued_right_cars = []
        self.next_car_spawn_time = 0
        
        self.spawn_cars()

    def reset_simulation(self):
        self.left_cars = []
        self.right_cars = []
        self.junction_cars = []
        self.queued_left_cars = []
        self.queued_right_cars = []
        self.last_spawn_time = time.time()
        self.next_car_spawn_time = 0
        
        # Reset all lane spawn times
        for i in range(self.num_lanes):
            self.lane_next_spawn_times["left"][i] = 0
            self.lane_next_spawn_times["right"][i] = 0
        
        self.spawn_cars()

    def cycle_spawn_time(self):
        self.spawn_time_index = (self.spawn_time_index + 1) % len(SPAWN_TIMES)
        self.current_spawn_time = SPAWN_TIMES[self.spawn_time_index]

    def switch_simulation(self):
        self.paused = True  # Pause current simulation
        self.current_simulation = 2 if self.current_simulation == 1 else 1

    def draw_status(self):
        # Draw simulation counter
        sim_text = f"Simulation {self.current_simulation}/{self.total_simulations}"
        sim_surface = self.status_font.render(sim_text, True, BLACK)
        self.screen.blit(sim_surface, (10, 10))

        # Draw spawn time (moved down)
        spawn_text = f"Spawn Time: {self.current_spawn_time}s"
        spawn_surface = self.status_font.render(spawn_text, True, BLACK)
        self.screen.blit(spawn_surface, (10, 40))
        
        # Draw pause status (moved down)
        pause_text = "PAUSED" if self.paused else "RUNNING"
        pause_surface = self.status_font.render(pause_text, True, BLACK)
        self.screen.blit(pause_surface, (10, 70))

        # Draw controls at bottom left
        controls = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset Simulation",
            "C - Change Spawn Time",
            "S - Switch Simulation",
            "ESC - Exit"
        ]
        
        for i, text in enumerate(controls):
            control_surface = self.controls_font.render(text, True, BLACK)
            y_pos = WINDOW_HEIGHT - (len(controls) - i) * 25 - 10
            self.screen.blit(control_surface, (10, y_pos))

    def get_random_spawn_time_multiplier(self):
        """Return a random spawn time multiplier"""
        return random.choice(self.spawn_time_multipliers)

    def check_and_spawn_lane_cars(self, current_time):
        """Check each lane and spawn cars based on individual lane timers"""
        
        # Check left lanes (downward moving cars)
        for lane in range(self.num_lanes):
            if current_time >= self.lane_next_spawn_times["left"][lane]:
                # Spawn car in this lane (if not occupied)
                if random.random() < 0.7:  # 70% chance to spawn a car
                    self.left_cars.append(Car(lane, -CAR_HEIGHT, "down"))
                
                # Set next spawn time for this lane with random multiplier
                multiplier = self.get_random_spawn_time_multiplier()
                self.lane_next_spawn_times["left"][lane] = current_time + (self.current_spawn_time * multiplier)
        
        # Check right lanes (upward moving cars)
        for lane in range(self.num_lanes):
            if current_time >= self.lane_next_spawn_times["right"][lane]:
                # Spawn car in this lane (if not occupied)
                if random.random() < 0.7:  # 70% chance to spawn a car
                    self.right_cars.append(Car(lane, WINDOW_HEIGHT, "up"))
                
                # Set next spawn time for this lane with random multiplier
                multiplier = self.get_random_spawn_time_multiplier()
                self.lane_next_spawn_times["right"][lane] = current_time + (self.current_spawn_time * multiplier)

    def spawn_cars(self):
        """Initialize lane-based spawn times"""
        current_time = time.time()
        
        # Initialize each lane with a random spawn time
        for lane in range(self.num_lanes):
            # Random initial delay (0 to current_spawn_time)
            initial_delay = random.random() * self.current_spawn_time
            
            # Set initial spawn times for each lane
            self.lane_next_spawn_times["left"][lane] = current_time + initial_delay
            self.lane_next_spawn_times["right"][lane] = current_time + initial_delay
    
    def spawn_queued_cars(self):
        """Legacy method kept for compatibility"""
        pass
    
    def spawn_junction_cars(self):
        # Only spawn if no cars are present (to avoid collisions in single lane)
        if not self.junction_cars and random.random() < 0.3:  # 30% chance to spawn
            x = JUNCTION_VERTICAL_ROAD_X + (LANE_WIDTH - CAR_WIDTH) // 2
            self.junction_cars.append(JunctionCar((x, -CAR_HEIGHT), "down"))

    def update_cars(self):
        # Update and remove cars that are off screen
        self.left_cars = [car for car in self.left_cars if not car.move()]
        self.right_cars = [car for car in self.right_cars if not car.move()]

    def update_junction(self):
        # Update and remove cars that are off screen or completed their turn
        self.junction_cars = [car for car in self.junction_cars if not car.move()]

    def draw_lanes(self):
        # Draw left motorway
        pygame.draw.rect(self.screen, GRAY, 
                        (LEFT_ROAD_START_X, 0, TOTAL_ROAD_WIDTH, WINDOW_HEIGHT))
        for i in range(self.num_lanes + 1):
            x = LEFT_ROAD_START_X + (i * LANE_WIDTH)
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, WINDOW_HEIGHT), 2)

        # Draw right motorway
        pygame.draw.rect(self.screen, GRAY, 
                        (RIGHT_ROAD_START_X, 0, TOTAL_ROAD_WIDTH, WINDOW_HEIGHT))
        for i in range(self.num_lanes + 1):
            x = RIGHT_ROAD_START_X + (i * LANE_WIDTH)
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, WINDOW_HEIGHT), 2)

    def draw_junction(self):
        # Draw vertical road (top part)
        pygame.draw.rect(self.screen, GRAY,
                        (JUNCTION_VERTICAL_ROAD_X, 0,
                         LANE_WIDTH, WINDOW_HEIGHT))  # Extend to full height
        
        # Draw horizontal road
        pygame.draw.rect(self.screen, GRAY,
                        (0, JUNCTION_HORIZONTAL_ROAD_Y,
                         WINDOW_WIDTH, LANE_WIDTH))
        
        # Draw road lines
        # Vertical lines
        pygame.draw.line(self.screen, WHITE, 
                        (JUNCTION_VERTICAL_ROAD_X, 0),
                        (JUNCTION_VERTICAL_ROAD_X, WINDOW_HEIGHT), 2)
        pygame.draw.line(self.screen, WHITE,
                        (JUNCTION_VERTICAL_ROAD_X + LANE_WIDTH, 0),
                        (JUNCTION_VERTICAL_ROAD_X + LANE_WIDTH, WINDOW_HEIGHT), 2)
        
        # Horizontal lines
        pygame.draw.line(self.screen, WHITE,
                        (0, JUNCTION_HORIZONTAL_ROAD_Y),
                        (WINDOW_WIDTH, JUNCTION_HORIZONTAL_ROAD_Y), 2)
        pygame.draw.line(self.screen, WHITE,
                        (0, JUNCTION_HORIZONTAL_ROAD_Y + LANE_WIDTH),
                        (WINDOW_WIDTH, JUNCTION_HORIZONTAL_ROAD_Y + LANE_WIDTH), 2)

    def run(self):
        running = True
        while running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_simulation()
                    elif event.key == pygame.K_c:
                        self.cycle_spawn_time()
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_s:
                        self.switch_simulation()

            if not self.paused:
                if self.current_simulation == 1:
                    # Use the lane-based spawning system
                    self.check_and_spawn_lane_cars(current_time)
                    self.update_cars()
                else:
                    # Original spawning for simulation 2
                    if current_time - self.last_spawn_time >= self.current_spawn_time:
                        self.spawn_junction_cars()
                        self.last_spawn_time = current_time
                    
                    self.update_junction()

            # Draw everything
            self.screen.fill(GREEN)
            if self.current_simulation == 1:
                self.draw_lanes()
                for car in self.left_cars:
                    car.draw(self.screen)
                for car in self.right_cars:
                    car.draw(self.screen)
            else:
                self.draw_junction()
                for car in self.junction_cars:
                    car.draw(self.screen)
            
            self.draw_status()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    simulator = TrafficSimulator(NUMBER_OF_LANES)
    simulator.run()