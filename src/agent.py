# agent.py
import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
from game import SnakeGameAI, Direction, Point

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(14, 256, 128, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        head = game.snake[0]

        # Direction flags
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # Relative points
        def move_in_direction(point, direction):
            if direction == Direction.RIGHT:
                return Point(point.x + 20, point.y)
            elif direction == Direction.LEFT:
                return Point(point.x - 20, point.y)
            elif direction == Direction.UP:
                return Point(point.x, point.y - 20)
            elif direction == Direction.DOWN:
                return Point(point.x, point.y + 20)

        # Get relative directions
        if dir_r:
            dir_straight = Direction.RIGHT
            dir_right = Direction.DOWN
            dir_left = Direction.UP
        elif dir_l:
            dir_straight = Direction.LEFT
            dir_right = Direction.UP
            dir_left = Direction.DOWN
        elif dir_u:
            dir_straight = Direction.UP
            dir_right = Direction.RIGHT
            dir_left = Direction.LEFT
        else:
            dir_straight = Direction.DOWN
            dir_right = Direction.LEFT
            dir_left = Direction.RIGHT

        def danger_in_path(start_point, direction, steps = 10):
            point = start_point
            for _ in range(steps):
                point = move_in_direction(point, direction)
                if game.is_collision(point):
                    return 1
            return 0


        # Danger
        danger_straight = danger_in_path(head, dir_straight)
        danger_right = danger_in_path(head, dir_right)
        danger_left = danger_in_path(head, dir_left)

        # Free space ahead in each direction (up to N steps)
        def free_blocks_in_direction(start_point, direction, max_steps=10):
            count = 0
            point = start_point
            for _ in range(max_steps):
                point = move_in_direction(point, direction)
                if game.is_collision(point):
                    break
                count += 1
            return count / max_steps  # normalize (0 to 1)

        free_ahead = free_blocks_in_direction(head, dir_straight)
        free_right = free_blocks_in_direction(head, dir_right)
        free_left = free_blocks_in_direction(head, dir_left)

        # Food direction
        food_left = int(game.food.x < head.x)
        food_right = int(game.food.x > head.x)
        food_up = int(game.food.y < head.y)
        food_down = int(game.food.y > head.y)

        # Final state (length = 14)
        state = [
            # Danger
            danger_straight,
            danger_right,
            danger_left,

            # Direction
            int(dir_l),
            int(dir_r),
            int(dir_u),
            int(dir_d),

            # Food direction
            food_left,
            food_right,
            food_up,
            food_down,

            # Free space (normalized)
            free_ahead,
            free_right,
            free_left
        ]

        return np.array(state, dtype=float)



    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        self.epsilon = max(3, 80 * (0.995 ** self.n_games))  # explore vs exploit
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move

