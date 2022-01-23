from agent_base import AgentBase
import sys

class ClusterBased(AgentBase):
    """
    This is a model of an Agent class based on sillysoft's Cluster agent's heuristic
    """
    target_enemy_country = None

    def __init__(self, id: int):
        super().__init__(id)
        self.log = False
        # self.goal_continent = self._select_goal_continent()

    # what happens if agent starts already with a country?
    # def _select_goal_continent(self) -> str:
    #     """Select the best continent to take as a goal to conquer"""
    #     goal_continent = None

    #     continents = []

    #     # Get all the continents with no owner
    #     for continent in self.player_data['continents_data'].keys():
    #         if self.player_data['continents_data'][continent]['owner'] == None:
    #             continents.append(continent)

    #     goal_continent_value = 0
    #     goal_continent_enemies = float('inf')

    #     # Get the continent with less enemy countries and more extra armies
    #     for continent in continents:
    #         continent_countries = self.player_data['continents_data'][continent]['countries']

    #         n_enemies = 0
    #         # Get the amount of continent countries owned by the enemy
    #         for country in continent_countries:
    #             if self.player_data['countries_data'][country]['owner'] != self.id:
    #                 n_enemies += 1

    #         # If it has less enemies than the goal continent, make it the goal
    #         if n_enemies < goal_continent_enemies:
    #             goal_continent = continent

    #         # If it has the same amount of enemies than the goal continent, compare their values
    #         elif n_enemies == goal_continent_enemies:
    #             continent_value = continent_countries = self.player_data['continents_data'][continent]['extra_armies']
    #             if continent_value > goal_continent_value:
    #                 goal_continent = continent

    #             # If they have the same value, take the small one
    #             elif continent_value == goal_continent_value:
    #                 continent_size = len(self.player_data['continents_data'][continent]['countries'])
    #                 goal_continent_size = len(self.player_data['continents_data'][goal_continent]['countries'])

    #                 if continent_size < goal_continent_size:
    #                     goal_continent = continent

    #     return goal_continent

    def _get_best_continent_owned(self):
        """Get the best continent owned based on its extra armies"""
        best_continent = None
        best_continent_value = 0

        # Compare continents owned to find the one that provides the most extra armies
        for continent in self.player_data['continents_data'].keys():
            if self.player_data['continents_data'][continent]['owner'] == self.id:
                if self.player_data['continents_data'][continent]['extra_armies'] > best_continent_value:
                    best_continent = continent
                    best_continent_value = self.player_data['continents_data'][continent]['extra_armies']
        
        return best_continent

    def _get_cluster_inner(self, cluster_root: str) -> list:
        """Get all the ally countries that are conected to the root and dont have a border"""
        cluster_inner = []

        for country in self.player_data['countries_owned']:
            if country not in self.player_data['border_countries'].keys():
                if country == cluster_root:
                    cluster_inner.append(country)
                elif self.player_data['connection_matrix'][country][cluster_root]:
                    cluster_inner.append(country)

        return cluster_inner

    def _get_cluster_border(self, cluster_root: str) -> list:
        """Get all the ally countries that are conected to the root and have a border"""
        cluster_border = []

        for country in self.player_data['border_countries'].keys():
            if country == cluster_root:
                cluster_border.append(country)
            elif self.player_data['connection_matrix'][country][cluster_root]:
                cluster_border.append(country)

        return cluster_border

    def _get_moveable_troops(self, country) -> int:
        """Get all troops from a country able to be moved to another country"""
        return self.player_data['countries_data'][country]['n_troops'] - 1
                              
    def _get_strongest_country(self, countries: list) -> str:
        """Get the country with most troops among the countries in a list"""
        n_troops = 0
        most_troops_country = None

        for country in countries:
            if self.player_data['countries_data'][country]['n_troops'] > n_troops:
                n_troops = self.player_data['countries_data'][country]['n_troops']
                most_troops_country = country

        return most_troops_country  

    def mobilize(self):
        """Decide what to do when state is mobilizing"""
        if(self.player_data['n_new_troops'] == 0):
            self._pass_turn()
            self.target_enemy_country = None
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

    def _get_easiest_continent_to_take(self) -> str:
        """Get the continent with biggest (allies_troops / enemies_troops) rate"""
        allies_per_enemies_rate = 0
        easiest_continent = None

        for continent in self.player_data['continents_data'].keys():
            if self.player_data['continents_data'][continent]['owner'] == self.id:
                continue

            continent_countries = self.player_data['continents_data'][continent]['countries']
            allies_troops = 0
            enemies_troops = 0
            for country in continent_countries:
                if self.player_data['countries_data'][country]['owner'] == self.id:
                    allies_troops += self.player_data['countries_data'][country]['n_troops']
                else:
                    enemies_troops += self.player_data['countries_data'][country]['n_troops']

            # Will return a division by 0 if already own a continent
            if (allies_troops / enemies_troops) >= allies_per_enemies_rate:
                allies_per_enemies_rate = allies_troops / enemies_troops
                easiest_continent = continent

        return easiest_continent
    
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

        cluster_border = self._get_cluster_border(cluster_root)

        n_weakest_troops = float('inf')
        weakest_border_country = None

        # Find weakest country in the border
        for country in cluster_border:
            if self.player_data['countries_data'][country]['n_troops'] < n_weakest_troops:
                weakest_border_country = country
                n_weakest_troops = self.player_data['countries_data'][country]['n_troops']

        if weakest_border_country == None:
            print('cluster_border', cluster_border)
            print('cluster_root:', cluster_root)
            print("Algo de errado 1")
        
        # Set one troop on the weakest border country
        action = 'set_new_troops'
        n_troops = 1
        args = [n_troops, weakest_border_country]
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
            # TODO
            print('You should not be here')

    def attack(self):
        """decides what to do when state is attacking"""
        count = 0
        # Check if can attack
        for country in self.player_data['countries_owned']:
            if self.player_data['countries_data'][country]['n_troops'] >= 4:
                count += 1

        # If not, pass the turn
        if count == 0:
            self._pass_turn()
            return

        best_continent = self._get_best_continent_owned()

        if best_continent != None:
            cluster_root = self.player_data['continents_data'][best_continent]['countries'][0]
            self._attack_from_cluster(cluster_root)
        else:
            countries_owned = self.player_data['countries_owned']
            country = self._get_strongest_country(countries_owned)
            self._attack_from_cluster(country)

    def _attack_from_cluster(self, cluster_root: str):
        
        # Check if the target was conquered
        if self.target_enemy_country in self.player_data['countries_owned']:
            self.target_enemy_country = None

        if self.target_enemy_country != None:
            did_consolidate_attack = self._consolidate_attack(cluster_root) # TODO
            if did_consolidate_attack:
                return

        did_easy_attack = self._make_easy_attack(cluster_root)
        if did_easy_attack:
            return

        did_isolated_attack = self._make_isolated_attack(cluster_root)
        if did_isolated_attack:
            return
        
        did_consolidate_attack = self._consolidate_attack(cluster_root)
        if did_consolidate_attack:
            return

        self._pass_turn()        

    def _make_easy_attack(self, cluster_root: str) -> bool:
        """
        Search for cluster's enemy neighbours with only 1 troop
        
        Then attack it with the strongest ally country
        """

        cluster_border = self._get_cluster_border(cluster_root)

        one_troop_enemy_neighbours = []
        attacker_options = []

        # Get all enemy neighbours with 1 troop
        for country in cluster_border:
            neighbours = self.player_data['countries_data'][country]['neighbours']       
            for neighbour in neighbours:
                if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                    if self.player_data['countries_data'][neighbour]['n_troops'] == 1:
                        if neighbour not in one_troop_enemy_neighbours:
                            one_troop_enemy_neighbours.append(neighbour)
                        if country not in attacker_options:
                            # Check if country has chance to win
                            if self.player_data['countries_data'][country]['n_troops'] > 2: 
                                attacker_options.append(country)

        if len(one_troop_enemy_neighbours) == 0:
            return False

        if len(attacker_options) == 0:
            return False

        most_troops_country = self._get_strongest_country(attacker_options)
        n_troops = self.player_data['countries_data'][most_troops_country]['n_troops']

        for neighbour in self.player_data['countries_data'][most_troops_country]['neighbours']:
            if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                if self.player_data['countries_data'][neighbour]['n_troops'] == 1:
                    action = 'attack'
                    if n_troops == 2:
                        n_dice = 1
                    elif n_troops == 3:
                        n_dice = 2
                    elif n_troops >= 4:
                        n_dice = 3
                    args = [n_dice, most_troops_country, neighbour]
                    self._call_action(action, args)
                    return True
        
        return False

    def _make_isolated_attack(self, cluster_root: str) -> bool:
        cluster_border = self._get_cluster_border(cluster_root)

        isolated_enemies = []
        attacker_options = []

        for country in cluster_border:
            enemies = self.player_data['border_countries'][country]
            for enemy in enemies:
                enemys_neighbours = self.player_data['countries_data'][enemy]['neighbours']
                for enemys_neighbour in enemys_neighbours:
                    # If it is not isolated, check next enemy
                    if self.player_data['countries_data'][enemys_neighbour]['owner'] != self.id:
                        break
                    if enemy not in isolated_enemies:
                        isolated_enemies.append(enemy)
                    if country not in attacker_options:
                        attacker_options.append(country)

        if len(isolated_enemies) == 0:
            return False
        if len(attacker_options) == 0:
            return False

        most_troops_country = self._get_strongest_country(attacker_options)
        n_troops = self.player_data['countries_data'][most_troops_country]['n_troops']

        if n_troops == 1:
            return False

        neighbours = self.player_data['countries_data'][most_troops_country]['neighbours']

        for neighbour in neighbours:
            if neighbour in isolated_enemies:
                action = 'attack'
                if n_troops == 2:
                    n_dice = 1
                elif n_troops == 3:
                    n_dice = 2
                elif n_troops >= 4:
                    n_dice = 3
                args = [n_dice, most_troops_country, neighbour]
                self._call_action(action, args)
                return True
        
        return False    

    def _consolidate_attack(self, cluster_root: str) -> bool:
        # print('consolidate')
        if self.target_enemy_country != None:
            enemys_neighbours = self.player_data['countries_data'][self.target_enemy_country]['neighbours']

            attacker_options = []

            for neighbour in enemys_neighbours:
                if self.player_data['countries_data'][neighbour]['owner'] == self.id:
                    attacker_options.append(neighbour)

            most_troops_country = self._get_strongest_country(attacker_options)
            n_troops = self.player_data['countries_data'][most_troops_country]['n_troops'] # TODO

            if n_troops == 1:
                self.target_enemy_country = None
                return False
            
            action = 'attack'
            if n_troops == 2:
                n_dice = 1
            elif n_troops == 3:
                n_dice = 2
            elif n_troops >= 4:
                n_dice = 3
            args = [n_dice, most_troops_country, self.target_enemy_country]
            self._call_action(action, args)
            return True
        
        else:
            cluster_border = self._get_cluster_border(cluster_root)

            enemies = []

            # Get all the enemies of the border
            for country in cluster_border:
                neighbours = self.player_data['countries_data'][country]['neighbours']
                for neighbour in neighbours:
                    if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                        if neighbour not in enemies:
                            enemies.append(neighbour)

            troops_rate = 0
            
            # Select the enemy with biggest (ally troops / enemy troops) rate
            for enemy in enemies:
                enemy_troops = self.player_data['countries_data'][enemy]['n_troops']
                ally_troops = 0
                neighbours = self.player_data['countries_data'][enemy]['neighbours']
                for neighbour in neighbours: 
                    if self.player_data['countries_data'][neighbour]['owner'] == self.id:
                        ally_troops += self.player_data['countries_data'][neighbour]['n_troops']

                if (ally_troops / enemy_troops) > troops_rate:
                    troops_rate = ally_troops / enemy_troops
                    self.target_enemy_country = enemy
            
            if self.target_enemy_country != None:
                return self._consolidate_attack(cluster_root)
            else:
                return False                

    def conquer(self):
        """decides what to do when state is conquering"""
        country_conquering = self.call_data['command']['args'][1]
        country_conquered = self.call_data['command']['args'][2]

        action = 'move_troops'

        # If country conquering has only 1 border move everything to the conquered
        if country_conquering in self.player_data['border_countries'].keys():
            if len(self.player_data['border_countries'][country_conquering]) == 1:
                n_troops = self._get_moveable_troops(country_conquering)
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

        continent = self._get_easiest_continent_to_take()

        # Get weakest country conquering border inside goal continent 
        country_conquering_border = self._get_weakest_enemy_neighbour_in_continent(country_conquering, continent)

        # Get weakest country conquered border inside goal continent
        country_conquered_border = self._get_weakest_enemy_neighbour_in_continent(country_conquered, continent)

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
            if self.player_data['countries_data'][country_conquering_border]['n_troops'] < self.player_data['countries_data'][country_conquered_border]['n_troops']:
                n_troops = 0
                args = [n_troops, country_conquering, country_conquered]
                self._call_action(action, args)
                return
        
        # Move everything to conquered
        n_troops = self._get_moveable_troops(country_conquering)
        args = [n_troops, country_conquering, country_conquered]
        self._call_action(action, args) 
        
    def _get_weakest_enemy_neighbour_in_continent(self, country, continent) -> str:
        border_countries = self.player_data['border_countries']

        if country not in border_countries.keys():
            return None
        
        country_borders = border_countries[country]

        country_borders_in_continent = []

        # Check if the country borders are in the continent
        for country_border in country_borders:
            if country_border in self.player_data['continents_data'][continent]['countries']:
                country_borders_in_continent.append(country_border)

        n_weakest_troops = float('inf')
        weakest_border_country = None

        # Get the weakest border country in the continent
        for country_border in country_borders_in_continent:
            if self.player_data['countries_data'][country_border]['n_troops'] < n_weakest_troops:
                weakest_border_country = country_border
                n_weakest_troops = self.player_data['countries_data'][country_border]['n_troops']

        return weakest_border_country

    def fortify(self):
        best_continent = self._get_best_continent_owned()

        if best_continent != None:
            cluster_root = self.player_data['continents_data'][best_continent]['countries'][0]
            self._fortify_cluster(cluster_root)
        else:
            countries_owned = self.player_data['countries_owned']
            country = self._get_strongest_country(countries_owned)
            self._fortify_cluster(country)

    def _fortify_cluster(self, cluster_root: str):
        """Move all the troops from strongest country inside the cluster to the weakest country in the cluster border"""
        cluster_border = self._get_cluster_border(cluster_root)
        
        cluster_inner = self._get_cluster_inner(cluster_root)

        if (len(cluster_inner) == 0):
            self._pass_turn()
            return

        from_country = self._get_strongest_country(cluster_inner)

        n_weakest_troops = float('inf')
        to_country = None

        # Get weakest country in the border
        for country in cluster_border:
            if self.player_data['countries_data'][country]['n_troops'] < n_weakest_troops:
                to_country = country
                n_weakest_troops = self.player_data['countries_data'][country]['n_troops']

        action = 'move_troops'
        n_troops = self._get_moveable_troops(from_country)
        args = [n_troops, from_country, to_country]
        self._call_action(action, args)

if __name__ == "__main__":
    id = ClusterBased.read_id(sys.argv)

    agent = ClusterBased(id)

    agent.play()