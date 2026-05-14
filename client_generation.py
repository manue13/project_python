# =========================================================
# CLIENT GENERATOR
# =========================================================

import random

def generate_clients(num_clients=20):

    clients = []

    for i in range(num_clients):

        x = random.randint(-5, 8)
        y = random.randint(0, 9)

        client = {
            "id": f"Klient_{i+1}",
            "pos": (x, y)
        }

        clients.append(client)

    return clients
