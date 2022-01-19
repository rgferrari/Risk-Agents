from cluster_based_agent import ClusterBased
import sys

class MonteCarlo(ClusterBased):
    def __init__(self, id: int):
        super().__init__(id)

if __name__ == "__main__":
    id = MonteCarlo.read_id(sys.argv)

    agent = MonteCarlo(id)

    agent.play()