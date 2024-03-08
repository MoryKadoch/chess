from board import Board
from engine import Engine
from DDQN import DDQNAgent

import numpy as np

total_actions = 4096

def main():
    board = Board()
    engine = Engine()

    agent = DDQNAgent(alpha=0.0005, gamma=0.99, n_actions=total_actions, epsilon=1.0,
                      batch_size=64, input_dims=64)

    episode = 0

    while not engine.endgame:

        moves = board.gen_moves_list()
        
        mask = np.zeros(total_actions, dtype=int)
        for move in moves:
            mask[move[0]*move[1]] = 1

        print(board.get_board_state())
        state = board.get_board_state()
        action = agent.choose_action(state)

        reward = engine.usermove(board, action)

        agent.remember(action, reward)

        agent.learn()

        if episode % 10 == 0 and episode > 0:
            agent.update_network_parameters()

        if episode % 50 == 0 and episode > 0:
            agent.save_model()

if __name__ == '__main__':
    main()
