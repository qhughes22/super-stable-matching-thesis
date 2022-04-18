# A few utility functions.

from GraphVisualization import Digraph



def find_in_list_of_lists(element, l):
    """Returns index of element in list of lists. Returns -1 if not found.

    Parameters
    ----------
    element: int
        Element that's being searched for.
    l: list
        List that's being searched.

    Returns
    -------
    int:
        Index of the element in the list, or -1 if not found.
    """
    for i in range(len(l)):
        if element in l[i]:
            return i
    return -1

def remove_from_list_of_lists(element, list):
    """ Removes element from list of lists.


       Parameters
       ----------
       element: int
           Element that's being removed.
       l: list
           List that's being searched.

       Returns
       -------
       None
       """
    for i in range(len(list)):
        if element in list[i]:
            list[i].remove(element)

# Returns the outdegree of a connected component as defined by nodes in a digraph.
def get_outdegree_of_component(digraph, component_nodes):
    """ Gets the outdegree of a component in a digraph.


       Parameters
       ----------
       digraph: Digraph
           Graph that the component is a part of
       component_nodes: list
           Nodes in the component being checked.

       Returns
       -------
       int:
            Outdegree of the component.
       """
    out_count = 0
    for node in component_nodes:
        node_outedges = digraph.digraph.out_edges(node)
        for edge in node_outedges:
            if edge[1] not in component_nodes:
                out_count = out_count + 1
    return out_count
