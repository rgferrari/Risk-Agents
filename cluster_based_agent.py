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
        self._select_goal_continent()

    # TODO
    def _select_goal_continent(self):
        pass

    def _get_best_continent_owned(self):
        best_continent = None
        best_continent_value = 0

        # Get best player continent based on bonus troops
        for continent in self.player_data['continents_data'].keys():
            if self.player_data['continents_data'][continent]['owner'] == self.id:
                if self.player_data['continents_data'][continent]['extra_armies'] > best_continent_value:
                    best_continent = continent
                    best_continent_value = self.player_data['continents_data'][continent]['extra_armies']
        
        return best_continent

    def _place_armies_on_cluster_border(self, cluster_root: str):
        """Place an armie on the weakest border country of the cluster
        
        Parameters
        ----------
        cluster_root: str
            Is used to set the cluster. Can be any country in the cluster

        Returns
        -------
        None
        """
        cluster_border = [country for country in self.player_data['border_countries'].keys() if self.player_data['conection_matrix'][cluster_root][country]]

        n_weakest_troops = float('inf')
        weakest_border_country = None
        # find weakest country in the border
        for country in cluster_border:
            if self.player_data['countries_data'][country]['n_troops'] < n_weakest_troops:
                weakest_border_country = country
                n_weakest_troops = self.player_data['countries_data'][country]['n_troops']
        
        action = 'set_new_troops'

        n_troops = 1

        args = [n_troops, weakest_border_country]

        self._call_action(action, args)

    def _get_easiest_continent_to_take(self) -> str:
        """Get the continent with biggest allies_troops / enemies_troops rate"""
        allies_per_enemies_rate = 0
        easiest_continent = None

        for continent in self.player_data['continents_data'].keys():
            continent_countries = self.player_data['continents_data'][continent]['countries']
            allies_troops = 0
            enemies_troops = 0
            for country in continent_countries:
                if self.player_data['countries_data'][country]['owner'] == self.id:
                    allies_troops += self.player_data['countries_data'][country]['n_troops']
                else:
                    enemies_troops += self.player_data['countries_data'][country]['n_troops']

            # Will return a division by 0 if already own a continent
            if (allies_troops / enemies_troops) > allies_per_enemies_rate:
                allies_per_enemies_rate = allies_troops / enemies_troops
                easiest_continent = continent

        return easiest_continent

    #TODO
    def _get_cheapest_route_to_continent(self):
        action = 'set_new_troops'

        n_troops = 1

        args = [n_troops, self.player_data['countries_owned'][0]]

        self._call_action(action, args)

    def _place_armies_to_take_continent(self, continent: str):
        continent_countries = self.player_data['continents_data'][continent]['countries']

        ally_countries_inside_continent = [country for country in continent_countries if self.player_data['countries_data'][country]['owner'] == self.id]

        country_with_most_enemies = None
        biggest_enemy_number = 0

        # Find country owned inside continent with most enemies
        for country in ally_countries_inside_continent:
            n_enemy_troops = 0
            for neighbour in self.player_data['countries_data'][country]['neighbours']:
                if neighbour in self.player_data['continents_data'][continent]['countries']:
                    if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                        n_enemy_troops += self.player_data['countries_data'][neighbour]['n_troops']
            
            if n_enemy_troops > biggest_enemy_number:
                biggest_enemy_number = n_enemy_troops
                country_with_most_enemies = country

        if country_with_most_enemies != None:
            action = 'set_new_troops'

            n_troops = 1

            args = [n_troops, country_with_most_enemies]

            self._call_action(action, args)
        # if there is no country inside continent find     
        else:
            self._get_cheapest_route_to_continent()

    def _get_country_with_most_troops(self) -> str:
        n_troops = 0
        most_troops_country = None

        for country in self.player_data['countries_data'].keys():
            if self.player_data['countries_data'][country]['owner'] == self.id:
                if self.player_data['countries_data'][country]['n_troops'] > n_troops:
                    n_troops = self.player_data['countries_data'][country]['n_troops']
                    most_troops_country = country

        return most_troops_country

    # TODO
    def _attack_from_cluster(self, cluster_root: str):
        pass

    # TODO
    def _fortify_cluster(self, cluster_root: str):
        pass

    def mobilize(self):
        """decides what to do when state is mobilizing"""
        if(self.player_data['n_new_troops'] == 0):
            self._pass_turn()
        else:
            best_continent = self._get_best_continent_owned()

            if best_continent != None:
                cluster_root = self.player_data['continents_data'][best_continent]['countries'][0]
                self._place_armies_on_cluster_border(cluster_root)
                return
            else:
                easiest_continent_to_take = self._get_easiest_continent_to_take()
                self._place_armies_to_take_continent(easiest_continent_to_take)
                return
    
    def attack(self):
        """decides what to do when state is attacking"""
        best_continent = self._get_best_continent_owned()

        if best_continent != None:
            cluster_root = self.player_data['continents_data'][best_continent]['countries'][0]
            self._attack_from_cluster(cluster_root)
        else:
            country = self._get_country_with_most_troops()
            self._attack_from_cluster(country)

    # TODO
    def conquer(self):
        """decides what to do when state is conquering"""
        country_conquering = self.call_data['command']['args'][1]
        country_conquered = self.call_data['command']['args'][2]

        action = 'move_troops'

        # If country conquering has only 1 border move everything to the conquered
        if country_conquering in self.player_data['border_countries'].keys():
            if len(self.player_data['border_countries'][country_conquering]) == 1:
                n_troops = self.player_data['countries_data'][country_conquering]['n_troops'] - 1
                args = [n_troops, country_conquering, country_conquered]
                self._call_action(action, args)
                return
        # If country conquered has only 1 border dont move any troops
        elif country_conquering in self.player_data['border_countries'].keys():
            if len(self.player_data['border_countries'][country_conquering]) == 1:
                n_troops = 0
                args = [n_troops, country_conquering, country_conquered]
                self._call_action(action, args)
                return

        # Get weakest country conquering border inside goal continent 
        country_conquering_border = None

        # Get weakest country conquered border inside goal continent
        country_conquered_border = None

        # If country conquered has no border in continent dont move any troops
        if country_conquered_border == None:
            n_troops = 0
            args = [n_troops, country_conquering, country_conquered]
            self._call_action(action, args)
            return  
        # If country conquering has a border inside the continent
        # and its armies are less than the country conquered border
        # dont move any troops      
        elif country_conquering_border != None:
            if self.player_data['countries_data'][country_conquering_border]['n_troops'] < self.player_data['countries_data'][country_conquered_border]:
                n_troops = 0
                args = [n_troops, country_conquering, country_conquered]
                self._call_action(action, args)
                return
        
        # Move everything to conquered
        n_troops = self.player_data['countries_data'][country_conquering]['n_troops'] - 1
        args = [n_troops, country_conquering, country_conquered]
        self._call_action(action, args) 


    def fortify(self):
        best_continent = self._get_best_continent_owned()

        if best_continent != None:
            cluster_root = self.player_data['continents_data'][best_continent]['countries'][0]
            self._fortify_cluster(cluster_root)
        else:
            country = self._get_country_with_most_troops()
            self._fortify_cluster(country)

if __name__ == "__main__":
    id = AgentBase.read_id(sys.argv)

    agent = ClusterBased(id)

    agent.play()