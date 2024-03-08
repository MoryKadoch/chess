﻿# source: https://www.youtube.com/watch?v=UCgsv6tMReY&ab_channel=MachineLearningwithPhil
# explication: https://www.youtube.com/watch?v=RuraP4ef4nU&ab_channel=ThibaultNeveu


from keras.layers import Dense, Activation, LeakyReLU
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np

class ReplayBuffer(object):
    def __init__(self, max_size, input_shape, n_actions, discrete=False):
        self.mem_size = max_size
        self.mem_cntr = 0
        self.discrete = discrete
        self.state_memory = np.zeros((self.mem_size, input_shape))
        self.new_state_memory = np.zeros((self.mem_size, input_shape))
        dtype = np.int8 if self.discrete else np.float32
        self.action_memory = np.zeros((self.mem_size, n_actions), 
                                      dtype=dtype)
        self.reward_memory = np.zeros(self.mem_size)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.float32)
        
    def store_transition(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_

        if self.discrete:
            actions = np.zeros(self.action_memory.shape[1])
            actions[action] = 1.0
            self.action_memory[index] = actions
        else:
            self.action_memory[index] = action
            
        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1 - int(done)
        self.mem_cntr += 1
        
    def sample_buffer(self, batch_size):
        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, batch_size)
    
        states = self.state_memory[batch]
        states_ = self.new_state_memory[batch]
        rewards = self.reward_memory[batch]
        actions = self.action_memory[batch]
        terminal = self.terminal_memory[batch]
    
        return states, actions, rewards, states_, terminal
    
def build_dqn(lr, n_actions, input_dims, fc1_dims, fc2_dims):
    
    model = Sequential()
    model.add(Dense(fc1_dims, input_shape=(input_dims,), activation=LeakyReLU(0.2)))
    model.add(Dense(fc2_dims, activation=LeakyReLU(0.2)))
    
    model.compile(optimizer=Adam(learning_rate=lr), loss='mse')
    
    return model
    
class DDQNAgent(object):
    def __init__(self, alpha, gamma, n_actions, epsilon, batch_size,
                 input_dims, epsilon_dec=0.996, epsilon_end=0.01,
                 mem_size=1000000, fname='ddqn_model.h5'):
        self.n_actions = n_actions
        self.action_space = [i for i in range(n_actions)]
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_dec = epsilon_dec
        self.epsilon_min = epsilon_end
        self.batch_size = batch_size
        self.model_file = fname
        self.memory = ReplayBuffer(mem_size, input_dims, n_actions, discrete=True)
        self.q_eval = build_dqn(alpha, n_actions, input_dims, 256, 256)
        self.q_target = build_dqn(alpha, n_actions, input_dims, 256, 256)
        
    def remember(self, state, action, reward, new_state, done):
        self.memory.store_transition(state, action, reward, new_state, done)
        
    def choose_action(self, state):
        state = np.array(state)
        state = state[np.newaxis, :]
        rand = np.random.random()
        
        if rand < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            actions = self.q_eval.predict(state)
            action = np.argmax(actions)
            
        return action
    
    def learn(self):
        if self.memory.mem_cntr > self.batch_size:
            state, action, reward, new_state, done = self.memory.sample_buffer(self.batch_size)
            
            action_values = np.array(self.action_space, dtype=np.int8)
            action_indices = np.dot(action, action_values)
            
            q_next = self.q_target.predict(new_state)
            q_eval = self.q_eval.predict(new_state)
            
            q_pred = self.q_eval.predict(state)
            
            max_actions = np.argmax(q_eval, axis=1)
            
            q_target = q_pred
            
            batch_index = np.arange(self.batch_size, dtype=np.int32)
            
            q_target[batch_index, action_indices] = reward + self.gamma*q_next[batch_index, max_actions.astype(int)]*done
            
            _ = self.q_eval.fit(state, q_target, verbose=0)
            
            self.epsilon = self.epsilon*self.epsilon_dec if self.epsilon > self.epsilon_min else self.epsilon_min
            
    def update_network_parameters(self):
        self.q_target.set_weights(self.q_eval.get_weights())
        
    def save_model(self):
        self.q_eval.save(self.model_file)
        
    def load_model(self):
        self.q_eval = load_model(self.model_file)
        if self.epsilon == self.epsilon_min:
            self.update_network_parameters()