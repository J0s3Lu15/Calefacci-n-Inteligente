import numpy as np
import pickle
import random

# ======================================
# PARÁMETROS DEL ENTRENAMIENTO
# ======================================
max_episodes = 50000
max_steps = 500

alpha = 0.1
gamma = 0.95
epsilon = 1.0
epsilon_decay = 0.00002
epsilon_min = 0.05

T_margin = 1.0            # margen donde consideramos que está "bien"
C = 8.0                   # capacidad térmica
R = 10.0                  # resistencia térmica
dt = 5.0                  # paso de simulación
max_heat_step = 10.0      # calor/frío máximo que puede aplicar la acción

# ======================================
# DISCRETIZACIÓN
# ======================================
T_in_bins  = np.linspace(-20, 40, 30)
T_out_bins = np.linspace(-20, 40, 30)
T_set_bins = np.linspace(-10, 40, 11)

actions = [0, 1]  # 0 = no prender calefaccion, 1 = actuar aplicando calor o frío

# Q-table inicial
q_table = np.zeros((len(T_in_bins)+1,
                    len(T_out_bins)+1,
                    len(T_set_bins)+1,
                    len(actions)))

rng = np.random.default_rng()

# ======================================
# FUNCIÓN DE RECOMPENSA
# ======================================
def compute_reward(T_in, T_set, heat_power):
    error = abs(T_in - T_set)

    # si está dentro de 1 grado cerca al objetivo → excelente
    if error <= T_margin:
        return 200 - 0.1 * abs(heat_power)

    # si está lejos → castigo fuerte
    return -10 * error - 0.1 * abs(heat_power)

# ======================================
# ENTRENAMIENTO
# ======================================
rewards_per_episode = []

for episode in range(max_episodes):

    T_in  = rng.uniform(0, 25)
    T_out = rng.uniform(-10, 36)
    T_set = rng.uniform(15, 25)

    total_reward = 0

    for step in range(max_steps):

        state_in  = np.digitize(T_in, T_in_bins)
        state_out = np.digitize(T_out, T_out_bins)
        state_set = np.digitize(T_set, T_set_bins)

        # Política ε-greedy
        if rng.random() < epsilon:
            action = rng.choice(actions)
        else:
            action = np.argmax(q_table[state_in, state_out, state_set, :])

        heat_loss = (T_out - T_in) / R

        if action == 1:
            heat_power = np.clip(T_set - T_in, -max_heat_step, max_heat_step)
        else:
            heat_power = 0.0

        T_in_new = T_in + (dt / C) * (heat_loss + heat_power)

        reward = compute_reward(T_in_new, T_set, heat_power)
        total_reward += reward

        new_state_in  = np.digitize(T_in_new, T_in_bins)
        new_state_out = np.digitize(T_out, T_out_bins)

        q_table[state_in, state_out, state_set, action] += alpha * (
            reward + gamma * np.max(q_table[new_state_in, new_state_out, state_set, :])
            - q_table[state_in, state_out, state_set, action]
        )

        T_in = T_in_new

    rewards_per_episode.append(total_reward)

    epsilon = max(epsilon - epsilon_decay, epsilon_min)

    if episode % 500 == 0:
        mean_r = np.mean(rewards_per_episode[-500:])
        print(f"Episodio: {episode}, Recompensa media últimos 500: {mean_r:.2f}, Epsilon: {epsilon:.3f}")

# ======================================
# GUARDAR Q-TABLE
# ======================================
with open("calefaccion_q_table.pkl", "wb") as f:
    pickle.dump(q_table, f)

print("Entrenamiento completado")
print("Q-table guardada como 'calefaccion_q_table.pkl'")
