from agent_base import AgentBase
import sys
import json
import os

class ClusterBased(AgentBase):
    """
    This is a model of an Agent class based on sillysoft's Cluster agent
    """

    def __init__(self, id: int):
        super().__init__(id)
    
    # Modify the next four methods to implement your AI
    
    def attack(self):
        """decides what to do when state is attacking"""
        pass

    def mobilize(self):
        """decides what to do when state is mobilizing"""
        pass

    def conquer(self):
        """decides what to do when state is conquering"""
        pass

    def fortify(self):
        #player_data['continents_owners']
        pass
    
if __name__ == "__main__":
    id = AgentBase.read_id(sys.argv)

    agent = ClusterBased(id)

    agent.play()