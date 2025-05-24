import networkx as nx
import json
import os

class PreferenceGraph:
    def __init__(self, user_id='user1'):
        self.graph = nx.DiGraph()
        self.user_id = user_id
        self.json_path = f'prefs_{self.user_id}.json'
        self.latest = None
        self.load_graph()

    def add_preference(self, preference):
        preference = preference.strip().lower()  # Normalize input

        self.graph.add_node(self.user_id)
        self.graph.add_node(preference)

        # Remove red from old edge if it exists
        if self.latest and self.graph.has_edge(self.user_id, self.latest):
            self.graph[self.user_id][self.latest]['color'] = 'gray'

        # Check if edge already exists
        if self.graph.has_edge(self.user_id, preference):
            self.graph[self.user_id][preference]['color'] = 'red'
        else:
            self.graph.add_edge(self.user_id, preference, color='red')

        self.latest = preference
        self.save_graph()


    def remove_preference(self, preference):
        preference = preference.strip().lower()
        if self.graph.has_edge(self.user_id, preference):
            self.graph[self.user_id][preference]['color'] = 'black'
        self.save_graph()


    def get_latest_preference(self):
        if self.latest and self.graph.has_edge(self.user_id, self.latest):
            color = self.graph[self.user_id][self.latest].get('color')
            if color != 'black':
                return [self.latest]
        return []


    def get_graph(self):
        return self.graph

    def save_graph(self):
        data = nx.readwrite.json_graph.node_link_data(self.graph)
        with open(self.json_path, 'w') as f:
            json.dump(data, f)

    def load_graph(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                self.graph = nx.readwrite.json_graph.node_link_graph(data)
                for _, tgt, attr in self.graph.edges(data=True):
                    if attr.get('color') == 'red':
                        self.latest = tgt

    def reset(self):
        self.graph.clear()
        self.latest = None
        if os.path.exists(self.json_path):
            os.remove(self.json_path)
