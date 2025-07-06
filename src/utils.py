import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    plt.figure(1)  # Use Figure 1 for score vs mean score
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training Progress')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores, label='Score')
    plt.plot(mean_scores, label='Mean Score')
    plt.ylim(ymin=0)
    plt.legend()
    plt.grid(True)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.pause(0.1)

def plot_rewards_vs_scores(rewards, scores):
    plt.figure(2)
    plt.clf()
    plt.title('Total Reward vs Score per Game')
    plt.xlabel('Game Number')
    plt.ylabel('Score / Reward')
    
    games = list(range(1, len(scores) + 1))
    
    plt.plot(games, scores, marker='o', label='Score', color='blue')
    plt.plot(games, rewards, marker='x', label='Total Reward', color='crimson')
    
    # Optional: Add labels to every 5th point to reduce clutter
    for i in range(len(games)):
        if i % 5 == 0 or i == len(games) - 1:
            plt.text(games[i], scores[i], f"{scores[i]}", color='blue', fontsize=8)
            plt.text(games[i], rewards[i], f"{rewards[i]}", color='crimson', fontsize=8)
