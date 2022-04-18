# First networkx library is imported
# along with matplotlib
import networkx as nx
import matplotlib.pyplot as plt


class Digraph:

    def __init__(self):
        # visual is a list which stores all
        # the set of edges that constitutes a
        # graph
        self.digraph = nx.DiGraph()

    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list
    # def addEdge(self, a, b):
    #     temp = [a, b]
    #     self.visual.append(temp)
    #     # self.digraph.add_edge(a,b)


    def addNodes(self, nodes):
        self.digraph.add_nodes_from(nodes)

    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list. a is origin, b destination
    def addDirectedEdge(self, a, b, **kwargs):
        self.digraph.add_edge(a,b, **kwargs)


    # In visualize function G is an object of
    # class Graph given by networkx G.add_edges_from(visual)
    # creates a graph with a given list
    # nx.draw_networkx(G) - plots the graph
    # plt.show() - displays the graph
    def visualize(self):
        color_map = ['red' if node[0] is 'm' else 'green' for node in self.digraph]

        nx.draw_networkx(self.digraph,  with_labels=True, node_color=color_map)
        plt.show()

# Driver code
if __name__ == '__main__':
    G = Digraph()
    G.digraph.add_nodes_from(['m0','m1','m2','m3','m4'])
    G.digraph.add_nodes_from(['w0','w1','w2','w3','w4'])

    G.addDirectedEdge('w0', 'm2')
    color_map = ['red' if node[0] is 'm' else 'green' for node in G.digraph]

    # G.addDirectedEdge(1, 2)
    # G.addDirectedEdge(1, 3)
    # G.addDirectedEdge(5, 3)
    # G.addDirectedEdge(3, 4)
    # G.addDirectedEdge(1, 0)
    nx.draw(G.digraph, with_labels=True, node_color=color_map)
    print(G.digraph.nodes)
    plt.show()
    G = nx.complete_graph(5)
    nx.draw(G)