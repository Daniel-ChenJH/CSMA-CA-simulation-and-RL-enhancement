import RL_brain

class agent:
    def __init__(self, mac, action_space, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9) -> None:
        self.mac = mac
        self.RL = RL_brain.QLearningTable(actions=list(range(action_space)), learning_rate=learning_rate, reward_decay=reward_decay, e_greedy=e_greedy)

    def action_choosing(self, observation):
        return self.RL.choose_action(observation)

    def learn(self, s, a, r, s_):
        self.RL.learn(s, a, r, s_)