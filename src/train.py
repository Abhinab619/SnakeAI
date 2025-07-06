from agent import Agent
from game import SnakeGameAI
from utils import plot, plot_rewards_vs_scores

scores = []
mean_scores = []
total_score = 0
game_scores = []
game_rewards = []

def train():
    global total_score
    agent = Agent()
    game = SnakeGameAI()
    record = 0

    episode_rewards = []  # reward per frame within a game

    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Track rewards during this game
        episode_rewards.append(reward)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            total_episode_reward = sum(episode_rewards)  # total reward for the game
            game_rewards.append(total_episode_reward)
            game_scores.append(score)
            episode_rewards = []  # reset for next game

            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            mean_scores.append(mean_score)

            print(f'Game {agent.n_games} | Score: {score} | Avg: {mean_score:.2f}')
            plot(scores, mean_scores)  # existing plot

            # Plot Reward vs Score at end of each game (separate plot)
            plot_rewards_vs_scores(game_rewards, game_scores)

            if score > record:
                record = score
                agent.model.save(f"model_{score}.pth") 


if __name__ == '__main__':
    train()
