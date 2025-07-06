import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font(None, 30)

# Constants
BLOCK_SIZE = 20
SPEED = 100

# Directions
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Point class
Point = namedtuple('Point', 'x, y')

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.prev_distance_to_food = None
        self.step_logs = []  # Collect sub-rewards per game
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - 2 * BLOCK_SIZE, self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.steps_since_food = 0

    def log_step_rewards(self, reward_dict):
        self.step_logs.append(reward_dict)

    def _place_food(self):
        while True:
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.food = Point(x, y)
            if self.food not in self.snake:
                break

    

    def play_step(self, action):
        self.frame_iteration += 1
        self.steps_since_food += 1  # Track how long since last food
        game_over = False

        

        # Event handling (optional if not using keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Move
        self._move(action)
        self.snake.insert(0, self.head)
        
            # initialize all sub‑rewards
        r_idle = -0.1
        r_collision = 0
        r_body = 0
        r_eat = 0
        r_timeout = 0
        r_shape = 0
        r_openness = 0
        r_self_loop = 0
        r_tail_follow = 0
        
        

        reward = r_idle  # small penalty to discourage idling
        length_factor = len(self.snake) / 5  # or use log(len(self.snake)) for slower growth


        if self.is_collision():
            r_collision = -10
            reward = r_collision
            game_over = True

        if self.is_collision_body():
            r_body = -15
            reward = r_body
            game_over = True

        elif self.head == self.food:
            r_eat = 20
            reward = r_eat
            self.score += 1
            self._place_food()
            self.steps_since_food = 0
            self.prev_distance_to_food = None

        else:
            self.snake.pop()
            new_distance = abs(self.head.x - self.food.x) + abs(self.head.y - self.food.y)

            # Scale factor based on snake length
            
            if self.prev_distance_to_food is not None:
                if new_distance < self.prev_distance_to_food:
                    r_shape = 0.5 * length_factor  # moved closer
                elif new_distance > self.prev_distance_to_food:
                    r_shape = -0.25 * length_factor  # moved away
            reward += r_shape

            self.prev_distance_to_food = new_distance


        # if not game_over and self.steps_since_food > 1:
        #     tail_vec = pygame.Vector2(
        #         self.head.x - self.snake[-1].x,
        #         self.head.y - self.snake[-1].y
        #     )

        #     if tail_vec.length_squared() > 0:
        #         tail_vec = tail_vec.normalize()
        #         if self.direction == Direction.RIGHT:
        #             move_vec = pygame.Vector2(1, 0)
        #         elif self.direction == Direction.LEFT:
        #             move_vec = pygame.Vector2(-1, 0)
        #         elif self.direction == Direction.UP:
        #             move_vec = pygame.Vector2(0, -1)
        #         else:
        #             move_vec = pygame.Vector2(0, 1)

        #         alignment = move_vec.dot(tail_vec)

        #         if alignment < 0.6:
        #             r_tail_follow = -0.3  # Removed length_factor here
        #             reward += r_tail_follow

        #         print(f"alignment: {alignment:.2f}, r_tail_follow: {r_tail_follow}, head: {self.head}, tail: {self.snake[-1]}")


        # Timeout condition
        base_timeout = 200
        max_steps_without_food = max(base_timeout, 30 * len(self.snake))
        if self.steps_since_food > max_steps_without_food:
            r_timeout = -5
            reward = r_timeout
            game_over = True

        # Penalize lack of openness (small corridor ahead)
        if not game_over:
            if self.direction == Direction.RIGHT:
                dir_straight = Direction.RIGHT
            elif self.direction == Direction.LEFT:
                dir_straight = Direction.LEFT
            elif self.direction == Direction.UP:
                dir_straight = Direction.UP
            else:
                dir_straight = Direction.DOWN

            free_ahead = self.free_blocks_in_direction(self.head, dir_straight)

            if free_ahead < 0.3:
                r_openness = -0.5 * (1 - free_ahead) * length_factor
            elif free_ahead > 0.7:
                r_openness = 0.2 * free_ahead * length_factor
            reward += r_openness

            

            if not game_over and self.is_self_loop(self.head):
                r_self_loop = -1.0 * length_factor  # stronger penalty for longer snake
                reward += r_self_loop


    # Store or log these per‑step:
        self.log_step_rewards({
            'idle': r_idle,
            'collision': r_collision,
            'body': r_body,
            'eat': r_eat,
            'timeout': r_timeout,
            'shape': r_shape,
            'openness': r_openness,
            'self_loop' : r_self_loop,
            'tail_follow': r_tail_follow
        })
  

        # Update UI and tick
        self._update_ui()
        self.clock.tick(SPEED)

        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # Hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        return False
        # Hits itself
    def is_collision_body(self,pt=None):
        if pt is None:
            pt = self.head
        if pt in self.snake[1:]:
            return True
        return False
    
    def move_in_direction(self, point, direction):
        if direction == Direction.RIGHT:
            return Point(point.x + BLOCK_SIZE, point.y)
        elif direction == Direction.LEFT:
            return Point(point.x - BLOCK_SIZE, point.y)
        elif direction == Direction.UP:
            return Point(point.x, point.y - BLOCK_SIZE)
        elif direction == Direction.DOWN:
            return Point(point.x, point.y + BLOCK_SIZE)
        
    def free_blocks_in_direction(self, start_point, direction, max_steps=10):
        count = 0
        point = start_point
        for _ in range(max_steps):
            point = self.move_in_direction(point, direction)
            if self.is_collision(point):
                break
            count += 1
        return count / max_steps  # normalized value between 0 and 1
    
    def is_self_loop(self, point):
        """Check if the point is almost enclosed (loop risk)."""
        directions = [Point(20, 0), Point(-20, 0), Point(0, 20), Point(0, -20)]
        blocked = 0

        for d in directions:
            next_point = Point(point.x + d.x, point.y + d.y)
            if next_point in self.snake or not (0 <= next_point.x < self.w and 0 <= next_point.y < self.h):
                blocked += 1

        return blocked >= 3  # surrounded on 3 or more sides = loop risk




    def _update_ui(self):
        self.display.fill(BLACK)
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render(f"Score: {self.score} | Steps: {self.frame_iteration}", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        # action = [straight, right, left]
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # No change
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = clock_wise[(idx + 1) % 4]  # Right turn
        else:  # [0, 0, 1]
            new_dir = clock_wise[(idx - 1) % 4]  # Left turn

        # Prevent reversing direction
        opposite_directions = {
            Direction.RIGHT: Direction.LEFT,
            Direction.LEFT: Direction.RIGHT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP
        }
        if new_dir != opposite_directions[self.direction]:
            self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)






# class SnakeGameManual(SnakeGameAI):
#     def __init__(self, w=640, h=480):
#         super().__init__(w, h)

#     def get_keyboard_action(self):
#         keys = pygame.key.get_pressed()

#         if keys[pygame.K_LEFT] and self.direction != Direction.RIGHT:
#             self.direction = Direction.LEFT
#         elif keys[pygame.K_RIGHT] and self.direction != Direction.LEFT:
#             self.direction = Direction.RIGHT
#         elif keys[pygame.K_UP] and self.direction != Direction.DOWN:
#             self.direction = Direction.UP
#         elif keys[pygame.K_DOWN] and self.direction != Direction.UP:
#             self.direction = Direction.DOWN

#     def play_step_manual(self):
#         self.frame_iteration += 1
#         self.steps_since_food += 1

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 quit()

#         self.get_keyboard_action()
#         self._move_manual()
#         self.snake.insert(0, self.head)

#         reward = 0
#         game_over = False

#         if self.is_collision() or self.frame_iteration > 100 * len(self.snake) or self.steps_since_food > 100:
#             game_over = True
#             return reward, game_over, self.score

#         if self.head == self.food:
#             self.score += 1
#             self._place_food()
#             self.steps_since_food = 0
#         else:
#             self.snake.pop()

#         self._update_ui()
#         self.clock.tick(SPEED)

#         return reward, game_over, self.score

#     def _move_manual(self):
#         x = self.head.x
#         y = self.head.y
#         if self.direction == Direction.RIGHT:
#             x += BLOCK_SIZE
#         elif self.direction == Direction.LEFT:
#             x -= BLOCK_SIZE
#         elif self.direction == Direction.DOWN:
#             y += BLOCK_SIZE
#         elif self.direction == Direction.UP:
#             y -= BLOCK_SIZE

#         self.head = Point(x, y)

# if __name__ == '__main__':
#     game = SnakeGameManual()

#     while True:
#         reward, game_over, score = game.play_step_manual()

#         if game_over:
#             print('Final Score:', score)
#             break

#     pygame.quit()
