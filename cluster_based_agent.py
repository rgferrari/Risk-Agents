from agent_base import AgentBase
import sys
import json
import os

class ClusterBased(AgentBase):
    """
    This is a model of an Agent class based on sillysoft's Cluster agent
    """

    continents_values = {
        'north_america': 5,
        'south_america': 2,
        'australia': 2,
        'europe': 5,
        'asia': 7,
        'africa': 3
    }

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
        
        # if own a continent
        if self.id in self.player_data['continents_owners'].values:
            
            most_valuable_continent = None
            biggest_value = 0

            # get the most valuable continent
            for continent in self.player_data['continents_owners']:
                if self.player_data['continents_owners'][continent] == self.id:
                    if self.continents_values[continent] > biggest_value:
                        most_valuable_continent = continent

            # get the country in it with most troops that is not in the border

            # get the border country with higher troop difference among it and its borders

            # transfer all troops to it
        
        else:
            # get the country with most troops

            # fortify the most weak conected border country
            pass


if __name__ == "__main__":
    id = AgentBase.read_id(sys.argv)

    agent = ClusterBased(id)

    agent.play()