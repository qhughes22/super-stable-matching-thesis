import random
import tests
import numpy as np
from copy import deepcopy
from collections import Counter
from GraphVisualization import Digraph
import util
import networkx as nx


def test_example(prefs, rotations_expected, rotation_digraph_expected):
    """Takes in preferences and asserts that the rotations and the rotation digraph given by the preferences are as expected.

    Parameters
    ----------
    prefs: list
        Pair of male prefs and female prefs. Male and female prefs are each a list of individual prefs.
    rotations_expected: list
        A list of rotations in the instance. Must match what the algorithm finds.
    rotation_digraph_expected: list
        A list of the edges of the rotation digraph in the instance. Must match what the algorithm finds.
    Returns
    -------
    None
    """
    male_prefs = prefs[0]
    female_prefs = prefs[1]
    instance = SuperStableMatchingInstance(male_prefs, female_prefs)
    instance.set_extreme_SMs()
    instance.set_all_rotations()
    instance.set_all_matchings()
    rotation_digraph = instance.get_rotation_digraph_edges(instance.rotations)
    print(instance.rotations)
    print(rotation_digraph)
    for matching in instance.matchings:
        assert instance.is_weakly_stable(matching), matching
        assert instance.is_strongly_stable(matching), matching
        assert instance.is_super_stable(matching), matching

    assert len(instance.matchings) == instance.count_matchings()
    assert instance.rotations == rotations_expected
    assert rotation_digraph_expected == rotation_digraph
    instance.create_rotation_digraph()
    print(instance.count_matchings())

def run_example(male_prefs, female_prefs):
    """Takes in preferences and returns the results of the algorithms: the matchings, rotations, and rotation digraph.

    Parameters
    ----------
    male_prefs: list
        A list of individual male prefs for the instance.
    female_prefs: list
        A list of individual female prefs for the instance.
    Returns
    -------
    list:
        The super stable matchings in the instance.
    list:
        The rotations in the instance.
    list:
        The edges of the rotation poset in the instance.

    """
    instance = SuperStableMatchingInstance(male_prefs, female_prefs)
    instance.set_all_rotations()
    instance.set_all_matchings()
    instance.create_rotation_digraph()
    return instance.matchings, instance.rotations, list(instance.rotation_digraph.edges)

class SuperStableMatchingInstance:
    """
    A class used to represent a single SMTI instance, with super stable matchings in mind.

    ...

    Attributes
    ----------
    matchings : list
        A list of the super stable matchings in the instance. In each matching, the index of an entry represents
        the man and the value his partner. -1 indicates the man is unmatched. This attribute is set by set_all_matchings
    rotations : list
        A list of the rotations in the super stable matching poset. Each rotation consists of a list of man-woman pairs.
         Set by set_all_rotations
    cycle_starts : list
        A list parallel to rotations that tracks the indices in the rotation where a cycle starts, since rotations can have multiple cycles.
    female_prefs : list
        List of individual preference lists. Each individual list is also a list of lists, to account for indifference.
    male_prefs : list
        List of individual preference lists. Each individual list is also a list of lists, to account for indifference.
    female_prefs_GSlist : list
        The reduced GS-list for the female preferences.
    male_prefs_GSlist : list
        The reduced GS-list for the female preferences.
    rotation_digraph : nx.DiGraph
        Rotation digraph for the super stable matching instance.
    rotation_digraph_edges : list
        List of the edges in the rotation digraph. Each edge is a triplet in the form of (from_node, to_node, type)
        where type is 1 or 2, as described in Gusfield and Irving.
    Methods
    -------
    count_matchings(self):
        Counts the super stable matchings in the instance.
    eliminate_rotation(og_matching, rotation):
        Eliminates a rotation from a matching
    get_all_predecessor(graph, node):
        Gets all predecessors of a node in the rotation digraph
    set_all_matchings():
        Sets all matchings in an instance. Needs rotation digraph to be created
    create_rotation_digraph():
        Creates and sets rotation digraph from rotatons
    set_extreme_SMs():
        Sets the man and woman optimal stable matchings, as well as the reduced GS-lists.
    get_gendered_GS_list_incomplete_prefs(proposer_prefs_orig, proposee_prefs_orig):
        Gets the gendered GS list by running the extended Gale-Shapely algorithm.
    make_Gd(edges, M):
        Creates Gd, a graph used in the algorithm in set_all_rotations.
    set_all_rotations():
        Finds all rotations in the instance.
    eliminate_rotation_by_graph(rotation_subgraph, M):
        Eliminates a rotation from the graph of men and women.
    remove_dominated_nonblocking_edges(M, E_prime):
        Removes from E' edges that can be removed in the set_all_rotations algorithm.
    delete_multiple_engagement_edges(E_prime, Gc, Ec, Gd, edge_ranks):
        Deletes edges to multiply engaged women in the set_all_rotations algorithm.
    get_rotation_digraph_edges(rotations):
        Returns the edges of the rotation digraph given the rotations.
    is_super_stable(matching):
        Checks if the matching is super stable.
    is_strongly_stable(matching):
        Checks if the matching is strongly stable.
    is_weakly_stable(matching):
        Checks if the matching is weakly stable.
    blocking_status(matching, man, woman):
        Returns the extent to which the man and woman block the matching.


    """
    def __init__(self, male_prefs, female_prefs):
        self.matchings = []
        self.rotations = []
        self.female_prefs_GSlist = []
        self.male_prefs_GSlist = []
        self.male_prefs = male_prefs
        self.female_prefs = female_prefs
        self.set_extreme_SMs()
        self.rotation_digraph_edges = []
        self.cycle_starts = []

    def is_super_stable(self, matching):
        """Checks whether a matching is super stable in the instance.

        Parameters
        ----------
        matching : list
            The matching being checked.

        Returns
        -------
        bool
            True if super stable, false if not.
        """
        for i in range(len(matching)):
            man = i
            woman = matching[i]
            r= util.find_in_list_of_lists(woman, self.male_prefs[i]) # man's ranking of partner

            # iterate over all women man weakly prefers to current partner
            for tier in range(r):
                for potential_homewrecker in self.male_prefs[i][tier]:
                    if self.blocking_status(matching, man, potential_homewrecker) >=0:
                        return False
        return True

    def is_strongly_stable(self, matching):
        """Checks whether a matching is strongly stable in the instance.

        Parameters
        ----------
        matching : list
            The matching being checked.

        Returns
        -------
        bool
            True if strongly stable, false if not.
        """
        for i in range(len(matching)):
            man = i
            woman = matching[i]
            r = util.find_in_list_of_lists(woman, self.male_prefs[i])  # man's ranking of partner

            # iterate over all women man weakly prefers to current partner
            for tier in range(r):
                for potential_homewrecker in self.male_prefs[i][tier]:
                    if self.blocking_status(matching, man, potential_homewrecker) >= 1:
                        return False
        return True

    def is_weakly_stable(self, matching):
        """Checks whether a matching is weakly stable in the instance.

        Parameters
        ----------
        matching : list
            The matching being checked.

        Returns
        -------
        bool
            True if weakly stable, false if not.
        """
        for i in range(len(matching)):
            man = i
            woman = matching[i]
            r = util.find_in_list_of_lists(woman, self.male_prefs[i])  # man's ranking of partner

            # iterate over all women man strictly prefers to current partner
            for tier in range(r-1):
                for potential_homewrecker in self.male_prefs[i][tier]:
                    if self.blocking_status(matching, man, potential_homewrecker) >= 2:
                        return False
        return True
    def blocking_status(self, matching, man, woman):
        """Checks whether a pair blocks. Returns -1 if not blocking at all, 0 if it would block a matching from being super stable,
        1 if it blocks strongly stable,  2 if it blocks weakly stable

        Parameters
        ----------
        matching : list
            The matching being checked
        man : int
            The man being checked in the pair
        woman : int
            The woman being checked in the pair

        Returns
        -------
        int
            The extent to which the matching is blocking. -1 if not blocking at all, 0 if it would block a matching from being super stable,
        1 if it blocks strongly stable,  2 if it blocks weakly stable
        """

        # man's ranking of current partner
        mans_matched_rank = util.find_in_list_of_lists(matching[man], self.male_prefs[man])

        # man's ranking of woman
        mans_woman_rank = util.find_in_list_of_lists(woman, self.male_prefs[man])

        # woman's ranking of current partner
        womans_matched_rank = util.find_in_list_of_lists(matching.index(woman), self.female_prefs[woman])
        # woman's ranking of man
        womans_man_rank = util.find_in_list_of_lists(man, self.female_prefs[woman])

        if mans_woman_rank == -1: # if the woman isn't a potential partner for the man
            return -1

        # if man unmatched or man prefers woman to current partner
        if mans_woman_rank < mans_matched_rank or mans_matched_rank == -1:
            man_opinion = 1
        elif mans_woman_rank == mans_matched_rank:
            man_opinion = 0
        else:
            man_opinion = -1

        if womans_man_rank < womans_matched_rank or womans_matched_rank == -1:
            woman_opinion = 1
        elif womans_man_rank == womans_matched_rank:
            woman_opinion = 0
        else:
            woman_opinion = -1
        if man_opinion + woman_opinion == 2:
            return 2
        if man_opinion + woman_opinion == 1:
            return 1
        if man_opinion == 0 and woman_opinion == 0:
            return 0
        return -1

# -1, not blocking at all. 0, blocks super only. 1 blocks strongly. 2 blocks weakly

    def count_matchings(self):
        """Counts the number of super stable matchings in an instance. Creates rotation digraph attribute if not present.

        Parameters
        ----------
        None

        Returns
        -------
        int
            number of super stable matchings in an instance
        """
        if not hasattr(self, 'man_optimal_SM'):
            return 0
        if not hasattr(self, 'rotation_digraph'):
            self.create_rotation_digraph()
        return sum(1 for _ in nx.algorithms.dag.antichains(self.rotation_digraph))

    def eliminate_rotation(self, og_matching, rotation, cycle_indices):
        """Eliminates rotation from matching. Checks instance prefs and throws assertion error if rotation is not exposed.

        Parameters
        ----------
        og_matching : list
            List that represents a matching. Index represents the man, value the woman.
        rotation : list of tuples
            List of tuples representing a rotation. Each tuple is formatted as (man, woman)

        Returns
        -------
        list
            The matching after the rotation is eliminated.
        """
        matching = deepcopy(og_matching)
        for pair in rotation:
            assert matching[pair[0]] == pair[1], f"rotation {rotation} not exposed in {matching}, {self.male_prefs}, {self.female_prefs}"

        cycles = [(rotation + [''])[slice(ix, iy)] for ix, iy in zip([0] + cycle_indices, cycle_indices + [-1])]

        for cycle in cycles:
            for i in range(len(cycle)):
                man, woman = cycle[i]
                next = cycle[(i+1)%len(cycle)][1]
                matching[man] = next
        return matching

    def get_all_predecessor(self, graph, node):
        """Recursively finds the predecessors of a node in the rotation poset.

        Parameters
        ----------
        graph : DiGraph
            The rotation poset.
        node : int
            the index of the rotation in self.rotations

        Returns
        -------
        dict
            a dict with the indices of the predecessors as keys, 1 as the values.
        """
        parents = list(graph.predecessors(node))
        if parents ==[]:
            return {node: 1}
        total = self.get_all_predecessor(graph, parents[0])
        for parent in parents[1:]:
            total.update(self.get_all_predecessor(graph, parent))
        total[node] = 1
        return total

    def set_all_matchings(self):
        """Sets and returns all the super stable matchings for the instance.

        Parameters
        ----------
        file_loc : str
            The file location of the spreadsheet
        print_cols : bool, optional
            A flag used to print the columns to the console (default is
            False)

        Returns
        -------
        list
            a list of strings used that are the header columns
        """
        if not hasattr(self, 'man_optimal_SM'):
            return 0
        if not hasattr(self, 'rotation_digraph'):
            self.create_rotation_digraph()

        antichains = list(nx.algorithms.dag.antichains(self.rotation_digraph))

        matchings = []
        for antichain in antichains:
            all_rotations = {}
            matching = deepcopy(self.man_optimal_SM)
            for terminal_rotation in antichain:
                all_rotations[terminal_rotation] = 1
                # dict of keys being the indices of rotations involved to reach the matching
                all_rotations = {**self.get_all_predecessor(self.rotation_digraph,terminal_rotation), **all_rotations}

            for rotation in all_rotations:
                matching = self.eliminate_rotation(matching, self.rotations[rotation], self.cycle_starts[rotation])

            matchings.append(matching)
        self.matchings = matchings
        return matchings
    def create_rotation_digraph(self):
        """Sets the instance's rotation digraph attribute.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.rotation_digraph_edges = self.get_rotation_digraph_edges(self.rotations)
        nodes = range(len(self.rotations))
        edges = set([(edge[1], edge[2]) for edge in self.rotation_digraph_edges])

        self.rotation_digraph = nx.DiGraph()
        self.rotation_digraph.add_nodes_from(nodes)
        self.rotation_digraph.add_edges_from(edges)



    def set_extreme_SMs(self):
        """sets the man optimal and woman optimal stable matchings, as well as the reduced GS-lists

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # if they've been set, return
        if hasattr(self,"male_prefs_MGS"):
            return
        male_prefs_MGS, female_prefs_MGS, self.unmatched_men, self.unmatched_women = self.get_gendered_GS_list_incomplete_prefs(
            self.male_prefs, self.female_prefs)
        female_prefs_FGS, male_prefs_FGS, unmatched_women2, unmatched_men2 = self.get_gendered_GS_list_incomplete_prefs(
            self.female_prefs, self.male_prefs)

        if unmatched_men2 is not None and self.unmatched_men is not None:
            assert unmatched_men2.sort() == self.unmatched_men.sort()
            assert unmatched_women2.sort() == self.unmatched_women.sort()

        self.male_prefs_MGS = male_prefs_MGS
        self.female_prefs_MGS = female_prefs_MGS
        self.male_prefs_FGS = male_prefs_FGS
        self.female_prefs_FGS = female_prefs_FGS

        if male_prefs_MGS is None or female_prefs_FGS is None:
            return

        # set GS lists (intersection of FGS and MGS lists)
        for i in range(len(male_prefs_MGS)):
            self.male_prefs_GSlist.append([])
            for tier in male_prefs_MGS[i]:
                new_tier = [pref for pref in tier if util.find_in_list_of_lists(pref, male_prefs_FGS[i])>= 0]
                if new_tier != []:
                    self.male_prefs_GSlist[i].append(new_tier)


        for i in range(len(female_prefs_MGS)):
            self.female_prefs_GSlist.append([])

            for tier in female_prefs_MGS[i]:
                new_tier = [pref for pref in tier if util.find_in_list_of_lists(pref, female_prefs_FGS[i])>= 0]
                if new_tier != []:
                    self.female_prefs_GSlist[i].append(new_tier)

        # set man optimal, woman optimal SMs, both with man as index woman as value

        self.man_optimal_SM = [-1] * len(
            male_prefs_FGS)  # note this is different from man optimal, since the man still needs to be index, woman value
        for i in range(len(male_prefs_MGS)):
            if i not in self.unmatched_men:
                self.man_optimal_SM[i] = male_prefs_MGS[i][0][0]
        self.woman_optimal_SM = [-1] * len(
            female_prefs_FGS)  # note this is different from man optimal, since the man still needs to be index, woman value
        for i in range(len(female_prefs_FGS)):
            if i not in self.unmatched_women:
                self.woman_optimal_SM[female_prefs_FGS[i][0][0]] = i



    def get_gendered_GS_list_incomplete_prefs(self, proposer_prefs_orig,
                                              proposee_prefs_orig):  # algorithm SUPER2 from Manlove
        """Runs the algorithm SUPER2 from Manlove to get the man-optimal or woman-optimal lists.

        Parameters
        ----------
        proposer_prefs_orig : list
            The preferences for the proposing side of the algorithm.
            List of lists, where each sublist is the preferences for one agent. The sublist is a list of lists as well.
        proposee_prefs_orig : list
            The preferences for the non-proposing side of the algorithm.
            List of lists, where each sublist is the preferences for one agent. The sublist is a list of lists as well.

        Returns
        -------
        list x2
            The proposer-optimal GS list of the proposer prefs, the proposer-optimal GS list of the proposee prefs.

        """
        free = []
        proposer_prefs = deepcopy(proposer_prefs_orig)
        proposee_prefs = deepcopy(proposee_prefs_orig)

        proposed = np.zeros(len(proposee_prefs))  # array storing whether or not a given woman has been proposed to
        matchings = []
        for i in range(len(proposer_prefs)):
            matchings.append([])  # matchings is list of lists, with index being proposer and value being proposed
        # assign each proposer to be free
        for i in range(len(proposer_prefs)):
            if proposer_prefs[i] != []:
                free.append(i)
        iteration = 0
        while len(free) > 0:
            iteration +=1

            # choose a random man
            bended_knee = free[random.randint(0, len(free) - 1)]
            surprised_list = proposer_prefs[bended_knee][0]
            for surprised in surprised_list:
                proposed[surprised] = 1
                # get all men less preferred than the proposer by the proposed woman
                to_remove = []

                # range from surprised's ranking of bended knee to the end of surprised's list
                if util.find_in_list_of_lists(bended_knee, proposee_prefs[surprised]) != -1:
                    for i in range(util.find_in_list_of_lists(bended_knee, proposee_prefs[surprised]) + 1,
                                   len(proposee_prefs[surprised])):
                        to_remove.append(proposee_prefs[surprised][i])
                rejects = [item for sublist in to_remove for item in
                           sublist]  # flatten the list of lists into a list of the men to remove
                # remove the pairs made impossible by the current proposal
                for reject in rejects:
                    util.remove_from_list_of_lists(surprised, proposer_prefs[reject])
                    util.remove_from_list_of_lists(reject, proposee_prefs[surprised])  # remove from each other's lists

                    if surprised in matchings[reject]:
                        matchings[reject].remove(surprised)

                # engage_broken = [man for man in range(len(matchings)) if surprised in matchings[man]] #get all men with woman in proposed list
                # for man in engage_broken:
                #     matchings[man].remove(surprised) #remove the matching
                #     if len(matchings[man]) is 0: #make man free if not engaged to any woman
                #         free.append(man)

                matchings[bended_knee].append(surprised)
                if bended_knee in free:
                    free.remove(bended_knee)
            # get multiply engaged women
            # counter = Counter(map(tuple,matchings)).items()
            multiply_engaged = [item for item, count in Counter(x for xs in matchings for x in set(xs)).items() if
                                count > 1]
            # for k, v in counter:
            #     if v > 1:
            #         multiply_engaged = multiply_engaged + list(k)

            for woman in multiply_engaged:
                # remove engagements involving multiply engaged women
                engage_broken = [man for man in range(len(matchings)) if
                                 woman in matchings[man]]  # get all men with woman in proposed list

                for man in engage_broken:

                    matchings[man].remove(woman)  # remove the matching
                    if len(matchings[man]) is 0:  # make man free if not engaged to any woman
                        free.append(man)

                # get men involved with multiply engaged women
                # men_to_remove = proposee_prefs[-1][0]
                men_to_remove = proposee_prefs[woman][-1]

                for man in men_to_remove:
                    # remove woman from man's list. Should be in top spot of man
                    util.remove_from_list_of_lists(woman, proposer_prefs[man])
                    # proposer_prefs[man][0].remove(woman)

                # remove tail of woman's list
                proposee_prefs[woman].pop()

            # cleanup

            for i in range(len(proposer_prefs)):
                proposer_prefs[i] = [rank for rank in proposer_prefs[i] if
                                     len(rank) > 0]  # removes any ranks with 0 women
                if len(matchings[i]) is 0 and len(proposer_prefs[
                                                      i]) > 0 and i not in free:  # if man has women left on list and is not engaged, add back to free
                    free.append(i)
                if len(proposer_prefs[i]) is 0 and i in free:  # once man's list is empty, remove from free
                    free.remove(i)
            for i in range(len(proposee_prefs)):
                proposee_prefs[i] = [rank for rank in proposee_prefs[i] if
                                     len(rank) > 0]  # removes any ranks with 0 men

        matched_women = [match[0] for match in matchings if len(match) > 0]
        unmatched_women = [woman for woman in range(len(proposee_prefs_orig)) if woman not in matched_women]
        unmatched_men = [man for man in range(len(matchings)) if len(matchings[man]) == 0]

        for woman in unmatched_women:
            if proposed[woman] > 0:
                return None, None, None, None  # no SSM exists

        return proposer_prefs, proposee_prefs, unmatched_men, unmatched_women

    def make_Gd(self, edges, M):
        """Gets and prints the spreadsheet's header columns

        Parameters
        ----------
        edges : list
            list of tuples. Each tuple is a pair of strings representing the man and woman who the edge connects.
        M : list
            List representing the man optimal matching. Index is the man, value the woman he's paired with.

        Returns
        -------
        Digraph
            Gd
        """
        Gd = self.initialize_digraph2()

        for edge in edges:
            if M[int(edge[0][1:])] == int(edge[1][1:]):  # if edge is a match in M
                Gd.addDirectedEdge(edge[1], edge[0])
            else:
                Gd.addDirectedEdge(edge[0], edge[1])

        # self.add_directed_edges(Gd, woman_to_man, False)
        return Gd

    def set_all_rotations(self):
        """Runs the algorithm to find all the rotations in a super-stable matching instance.
        Sets the instances rotations attribute to the list of rotations.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if not hasattr(self, 'man_optimal_SM'):
            return [], []

        # M0 = self.initialize_digraph(self.man_optimal_SM, True, True)
        M0 = self.man_optimal_SM
        Mz = self.woman_optimal_SM
        # M0.addNodes(range(len(self.man_optimal_SM))) #self.man_optimal_SM
        # Mz = self.initialize_digraph(self.woman_optimal_SM, True, True) # need to use man preference lists?
        M = deepcopy(M0)
        matchings = []
        rotations = []
        # matchings.append(deepcopy(M))
        # M_prime has all man to woman edges in M not in Mz
        M_prime = []
        for man, woman in enumerate(self.man_optimal_SM):
            if self.woman_optimal_SM[man] is woman and woman is not -1:
                M_prime.append([man, woman])

        # E is the list of all edges, in form of man, woman
        E = []
        edge_ranks = {}  # edge_ranks is a dict with edge as key, (man's rank of woman, woman's rank of man) as value

        for man, l in enumerate(self.male_prefs_GSlist): # TODO: Prove GS-List edges are okay here?
            for rank in l:
                for woman in rank:
                    edge = ('m' + str(man), 'w' + str(woman))
                    E.append(edge)
                    edge_ranks[edge] = (util.find_in_list_of_lists(woman, self.male_prefs_GSlist[man]),
                                        util.find_in_list_of_lists(man, self.female_prefs_GSlist[woman]))

        Ed = []
        for i in range(len(M)):
            if M[i]!= -1:
                Ed.append(('m' + str(i), 'w' + str(M[i])))
        Gd = self.make_Gd(Ed, M)
        E_prime = [edge for edge in E if edge not in Ed]

        Ec = deepcopy(M_prime)

        Gc = self.initialize_digraph2()
        self.add_directed_edges(Gc, Ec, True)
        Ec = list(Gc.digraph.edges)  # format Ec properly

        while (M != Mz):  # while the current matching is not the woman optimal

            # remove irrelevant edges
            self.remove_dominated_nonblocking_edges(M, E_prime)

            zerodeg_men = [node for node in Gc.digraph if Gc.digraph.degree(node) == 0 and node[0] is 'm']

            while (len(zerodeg_men) > 0):
                validManExists = False

                # search for a man with zero edges in Gc and strongly connected component with 0 outdegree
                for man in zerodeg_men:
                    # component containing man
                    component = [c for c in list(nx.strongly_connected_components(Gd.digraph)) if man in c][0]
                    if util.get_outdegree_of_component(Gd, component) == 0:
                        m = man
                        validManExists = True
                        break

                if not validManExists:  # if no man fulfilling condition exists, break loop
                    break
                lowest_rank = 99999999999
                m_edges = []
                for edge in E_prime:
                    if edge[0] == m:  # if edge contains m
                        m_edges.append(edge)
                        lowest_rank = min(lowest_rank, edge_ranks[edge][0])

                m_best_edges = [edge for edge in m_edges if edge_ranks[edge][0] is lowest_rank]

                for edge in m_best_edges:
                    Ed.append(edge)
                    Gd.addDirectedEdge(edge[0], edge[1])

                # component containing m
                component = [c for c in list(nx.strongly_connected_components(Gd.digraph)) if m in c][0]

                if util.get_outdegree_of_component(Gd, component) == 0:
                    for edge in m_best_edges:
                        w_partner_edge = (
                        'm' + str(M.index(int(edge[1][1:]))), edge[1])  # edge between w and her current partner
                        m_partner_edge = (
                        edge[0], 'w' + str(M[int(edge[0][1:])]))  # edge between w and her current partner
                        if edge_ranks[edge][1] < edge_ranks[w_partner_edge][1] and edge_ranks[edge][0] > \
                                edge_ranks[m_partner_edge][0]  \
                                :  # if the woman prefers this edge to her current partner and the man prefers his current partner to this edge, add to Ec

                            current_Gc_edges = Gc.digraph.in_edges('w' + edge[1][1:])

                            #if the woman either has no edges in Gc or prefers the new edge to the one(s) she has in Gc
                            # note if she has multiple edges in Gc, she must be indifferent towards them
                            if len(current_Gc_edges)==0 or edge_ranks[list(current_Gc_edges)[0]][1] > edge_ranks[edge][1]:
                                Ec.append(edge)
                                Gc.addDirectedEdge(edge[0], edge[1])

                                # remove any edges dominated by new edge
                                toremove = []
                                for edge2 in Ec:
                                    if edge2[1] == edge[1] and edge_ranks[edge2][1] > edge_ranks[edge][1]:
                                        toremove.append(edge2)
                                for goner in toremove:
                                    Ec.remove(goner)
                                    Gc.digraph.remove_edge(goner[0], goner[1])
                        E_prime.remove(edge)
                zerodeg_men = [node for node in Gc.digraph if Gc.digraph.degree(node) == 0 and node[
                    0] is 'm']  # since edges can be removed from Ed in this loop, must be recalculated

            # delete lowest ranked edges incident to women that are multiply engaged
            self.delete_multiple_engagement_edges(E_prime, Gc, Ec, Gd, edge_ranks)

            components = list(nx.strongly_connected_components(Gd.digraph))
            valid_components = [c for c in components if util.get_outdegree_of_component(Gd, c) == 0]
            while (len(valid_components) > 0):  # while a rotation is exposed
                isMatching = False
                for component in valid_components:  # iterate over components until perfect matching found
                    rotation_subgraph = Gc.digraph.subgraph(component).copy()
                    if nx.is_perfect_matching(rotation_subgraph, rotation_subgraph.edges):
                        isMatching = True
                        break
                if not isMatching:
                    break

                # get rotation in [man, woman] pair form with man and woman being the pre rotation match
                matchings.append(deepcopy(M))
                rotation, M, starts = self.eliminate_rotation_by_graph(deepcopy(rotation_subgraph), M)
                self.cycle_starts.append(starts)
                rotations.append(rotation)

                # update Gc
                toremove = []
                for edge in Ec:

                    if edge in rotation_subgraph.edges:  # both ends of edge must be in strongly connected component. TODO: comment this if out even though it's in the algorithm?
                        if M[int(edge[0][1:])] != Mz[int(edge[0][1:])] or M[int(edge[0][1:])] != int(edge[1][
                                                                                                      1:]):  # if the man's partner in current matching equals man's partner in woman optimal and edge connects partners, edge remains in Ec
                            toremove.append(edge)
                for goner in toremove:
                    Ec.remove(goner)
                    Gc.digraph.remove_edge(goner[0], goner[1])
                # update Gd
                toremove = []  # Gd needs directions fixed
                toadd = []  # reversed edges to be added
                for edge in Gd.digraph.edges:
                    if edge[0] not in rotation_subgraph.nodes and edge[1] not in rotation_subgraph.nodes:
                        continue
                    if edge[0][0] == 'm':  # if necessary since graph is directed

                        edgeman = int(edge[0][1:])
                        edgewoman = int(edge[1][1:])
                        if not M[edgeman] == edgewoman:
                            toremove.append(edge)
                        else:  # if the man to woman edge qualifies to stay, add the reverse edge and remove
                            toadd.append(edge)
                            toremove.append(edge)

                    else:
                        edgeman = int(edge[1][1:])
                        edgewoman = int(edge[0][1:])
                        if not M[edgeman] == edgewoman:
                            toremove.append((edge[1], edge[0]))

                for goner in toremove:
                    Ed.remove(goner)
                    if goner in Gd.digraph.edges:
                        Gd.digraph.remove_edge(goner[0], goner[1])
                    else:
                        Gd.digraph.remove_edge(goner[1], goner[0])
                for new in toadd:
                    Ed.append(new)
                    Gd.addDirectedEdge(new[1], new[0])

                # update components list to see if other rotations are exposed
                components = list(nx.strongly_connected_components(Gd.digraph))
                valid_components = [c for c in components if util.get_outdegree_of_component(Gd, c) == 0]

        # add woman-optimal matching
        matchings.append(M)
        # self.matchings = matchings
        self.rotations = rotations
        # return rotations

    #
    def eliminate_rotation_by_graph(self, rotation_subgraph, M):
        """transforms directed edges representing a cycle into a rotation represented by current pairings, updates matching

        Parameters
        ----------
        M : list
            The current matching.
        rotation_subgraph : networkx.DiGraph
            The graph of nodes and edges included in the rotation.

        Returns
        -------
        list x3
            list representing the rotation, list representing the new matching, list of indices representing where the cycles begin in the rotation
        """
        rotation = []
        new_M = deepcopy(M)

        j = 0
        # get the lowest numbered man in the rotation who is still with his old partner
        cycle_starts = []
        while len(rotation_subgraph.edges) >0:
            edge = min(rotation_subgraph.edges, key=lambda x: x[0])
            first_man = int(edge[0][1:])
            cycle_starts.append(j)
            rotation.append([first_man, M[first_man]])
            j+=1
            # next woman in rotation
            next = int(list(rotation_subgraph.out_edges("m" + str(first_man)))[0][1][1:])
            rotation_subgraph.remove_edge(edge[0], edge[1])

            # partner of next woman in rotation
            new_M[first_man] = next

            current_man = M.index(next)
            # update the matching

            while current_man != first_man:
                rotation.append([current_man, next])
                j+=1
                edge = list(rotation_subgraph.out_edges("m" + str(current_man)))[0]
                next = int(edge[1][1:])

                new_M[current_man] = next

                current_man = M.index(next)
                rotation_subgraph.remove_edge(edge[0], edge[1])

        return rotation, new_M, cycle_starts

    def remove_dominated_nonblocking_edges(self, M, E_prime):
        """Checks M and removes all edges from E' that are dominated by edges in M and are safe to remove.

        Parameters
        ----------
        M : list
            The current matching.
        E_prime : list
            List of edges in E', the edges not yet added to the graph.

        Returns
        -------
        none
        """
        for man, woman in enumerate(M):
            # rank of man's current partner
            current_partner = util.find_in_list_of_lists(woman, self.male_prefs[man])
            for woman2 in range(len(self.male_prefs)):
                # remove all pairs where m prefers woman2 to current partner
                if util.find_in_list_of_lists(woman2, self.male_prefs[man]) <= current_partner:
                    if ('m' + str(man), 'w' + str(woman2)) in E_prime:
                        E_prime.remove(('m' + str(man), 'w' + str(woman2)))

            # rank of woman's current partner
            current_partner = util.find_in_list_of_lists(man, self.female_prefs[woman])
            for man2 in range(len(self.female_prefs)):

                # remove all pairs where w strictly prefers her current partner to man2
                if util.find_in_list_of_lists(man2, self.female_prefs[woman]) > current_partner:
                    if ('m' + str(man2), 'w' + str(woman)) in E_prime:
                        E_prime.remove(('m' + str(man2), 'w' + str(woman)))

    def delete_multiple_engagement_edges(self, E_prime, Gc, Ec, Gd, edge_ranks):
        """Deletes edges from E_prime and Ec that are involved in multiple engagements.

        Parameters
        ----------
        E_prime : list
            List of edges in E', the edges not yet added to the graph.
        Gc : Digraph
            The digraph of candidate edges.
        Ec : list
            The edges that form Gc.
        Gd : Digraph
            The digraph of current relevant edges.
        edge_ranks: dict
            Keys are edges, values are tuple. First value in tuple is man's ranking of the edge, second woman's.
        Returns
        -------
        None
        """
        multiple_engaged_women = []
        lowest_rank_in_edges_female = {}  # dict with woman as the key, [rank of lowest rank edge, count of that rank] seen as value.
        for woman in range(len(self.female_prefs)):
            lowest_rank_in_edges_female[woman] = []
        for edge in E_prime + Ec:
            woman = int(edge[1][1:])
            if len(lowest_rank_in_edges_female[woman]) == 0 or lowest_rank_in_edges_female[woman][1] > edge_ranks[edge][
                1]:  # if this edge is of lower rank for the woman, make this her new lowest rank edge
                lowest_rank_in_edges_female[woman] = [edge_ranks[edge][1], 1]
            elif lowest_rank_in_edges_female[woman][0] == edge_ranks[edge][
                1]:  # if this edge is tied with the lowest, increment count
                lowest_rank_in_edges_female[woman][1] = lowest_rank_in_edges_female[woman][1] + 1

        for woman in lowest_rank_in_edges_female:
            if  lowest_rank_in_edges_female[woman]!= [] and lowest_rank_in_edges_female[woman][1] > 1:
                multiple_engaged_women.append(woman)
        if len(multiple_engaged_women) > 1:
            outdeg_zero_men = []
            for man in range(len(self.male_prefs)):
                component = \
                [c for c in list(nx.strongly_connected_components(Gd.digraph)) if 'm' + str(man) in c][
                    0]  # component containing m TODO: Is Gd the correct graph?
                if util.get_outdegree_of_component(Gd, component) == 0:
                    outdeg_zero_men.append(man)

            lowest_ranked_edges_male = {}  # dict containing [[lowest ranked edges for man], rank of those edges]
            for man in range(len(self.male_prefs)):
                lowest_ranked_edges_male[man] = []
            # get lowest ranked edges for outdeg_zero_men
            for edge in E_prime + Ec:
                man = int(edge[0][1:])
                if man in outdeg_zero_men:
                    if len(lowest_ranked_edges_male[man]) == 0 or lowest_ranked_edges_male[man][1] > edge_ranks[edge][
                        0]:
                        lowest_ranked_edges_male[man] = [[edge], edge_ranks[edge][0]]
                    elif lowest_ranked_edges_male[man][1] == edge_ranks[edge][0]:
                        lowest_ranked_edges_male[man][0].append(edge)

            toremove = []
            for man in lowest_ranked_edges_male:
                if lowest_ranked_edges_male[man] == []:
                    continue
                edges = lowest_ranked_edges_male[man][0]
                for edge in edges:
                    if int(edge[1][1:]) in multiple_engaged_women:
                        toremove.append(edge)

            for edge in toremove:
                if edge in Ec:
                    Ec.remove(edge)
                    Gc.digraph.remove_edge(edge[0], edge[1])
                else:
                    E_prime.remove(edge)

    #terminology of function assumes we're looking at woman's rankings of edges
    # def get_lowest_ranked_edges(self, E_prime, Ec, edge_ranks):
    #     """Gets and prints the spreadsheet's header columns
    #
    #     Parameters
    #     ----------
    #     E_prime : list
    #         List of edges in E', the edges not yet added to the graph.
    #     Ec : list
    #         The edges that form Gc.
    #     edge_ranks: dict
    #         Keys are edges, values are tuple. First value in tuple is man's ranking of the edge, second woman's.
    #     Returns
    #     -------
    #     list
    #         a list of strings used that are the header columns
    #     """
    #     lowest_rank_in_edges = {}  # dict with woman as the key, [lowest rank edges] as value.
    #     for woman in range(len(self.female_prefs)):
    #         lowest_rank_in_edges[woman] = []
    #     for edge in E_prime + Ec:
    #         woman = int(edge[1][1:])
    #         if len(lowest_rank_in_edges[woman]) == 0 or lowest_rank_in_edges[woman][1] > edge_ranks[edge][
    #             1]:  # if this edge is of lower rank for the woman, make this her new lowest rank edge
    #             lowest_rank_in_edges[woman] = [edge_ranks[edge][1], 1]
    #         elif lowest_rank_in_edges[woman][1] == edge_ranks[edge][
    #             1]:  # if this edge is tied with the lowest, increment count
    #             lowest_rank_in_edges[woman][1] = lowest_rank_in_edges[woman][1] + 1


    def initialize_digraph2(self):
        """Initializes a digraph with a node for every matched man and woman.

        Parameters
        ----------
        None

        Returns
        -------
        Digraph
            Digraph with no edges and a node for every matched man and woman.
        """
        g = Digraph()
        for i in range(len(self.man_optimal_SM)):
            if self.man_optimal_SM[i] != -1:
                g.addNodes(['m' + str(i), 'w' + str(i)])
        return g

    def add_directed_edges(self, digraph, edges, male_to_female):
        """Adds directed edges to a digraph.

        Parameters
        ----------
        digraph : Digraph
            The digraph to receive edges.
        edges : list
            List of edges to be added to the digraph. Edges are pair of strings.
        male_to_female: bool
            Boolean that determines whether edges will be added man to woman or woman to man.

        Returns
        -------
        None
        """
        digraph_edges = []
        edge_data = []
        for edge in edges:
            if male_to_female:
                digraph_edges.append(['m' + str(edge[0]), 'w' + str(edge[1])])
                edge_data.append({'male_rank': util.find_in_list_of_lists(edge[1], self.male_prefs[edge[0]]),
                                  'female_rank': util.find_in_list_of_lists(edge[0], self.female_prefs[
                                      edge[1]])})  # include the respective rankings in the edge data

            else:
                digraph_edges.append(['w' + str(edge[0]), 'm' + str(edge[1])])
                edge_data.append({'male_rank': util.find_in_list_of_lists(edge[0], self.male_prefs[edge[1]]),
                                  'female_rank': util.find_in_list_of_lists(edge[1], self.female_prefs[
                                      edge[0]])})  # include the respective rankings in the edge data
        for i in range(len(digraph_edges)):
            digraph.addDirectedEdge(digraph_edges[i][0], digraph_edges[i][1], **edge_data[i])


    # returns edges representing the rotation digraph
    #
    def get_rotation_digraph_edges(self, rotations):
        """Returns the edges representing the rotation digraph in the instance.

        Parameters
        ----------
        rotations: list
            the rotations in the instance.

        Returns
        -------
        list
            list of edges. Edges are [edge type, source, destination]
        """
        # create the type 1 label structure parallel to male prefs
        type_1_labels = deepcopy(self.male_prefs_GSlist)
        for i in range(len(type_1_labels)):
            for j in range(len(type_1_labels[i])):
                for k in range(len(type_1_labels[i][j])):
                    type_1_labels[i][j][k] = -1

        type_2_labels = deepcopy(self.male_prefs_GSlist)
        for i in range(len(type_2_labels)):
            for j in range(len(type_2_labels[i])):
                for k in range(len(type_2_labels[i][j])):
                    type_2_labels[i][j][k] = -1

        for i in range(len(rotations)):
            for pair in rotations[i]:
                rank = util.find_in_list_of_lists(pair[1], self.male_prefs_GSlist[pair[0]])
                index = self.male_prefs_GSlist[pair[0]][rank].index(pair[1])
                type_1_labels[pair[0]][rank][index] = i  # give type 1 label in the spot of the woman on the man's list

        for i in range(len(rotations)):
            for j in range(len(rotations[i])):
                woman = rotations[i][j][1]
                old_man = rotations[i][j][0]
                new_man = rotations[i][(j - 1) % len(rotations[i])][
                    0]  # woman's new man is the one in the previous pair in the rotation
                old_man_rank = util.find_in_list_of_lists(old_man, self.female_prefs_GSlist[woman])
                #    old_man_index = self.female_prefs_GSlist[woman][old_man_rank].index(old_man)
                new_man_rank = util.find_in_list_of_lists(new_man, self.female_prefs_GSlist[woman])
                #                new_man_index = self.female_prefs_GSlist[woman][new_man_rank].index(new_man)
                skipped_men = self.female_prefs_GSlist[woman][new_man_rank
                                                              + 1: old_man_rank]  # all the men in between the new man and the old in the woman's list
                for rank in skipped_men:
                    for man in rank:
                        # apply type 2 label in the spot of the woman in the skipped man's list
                        rank = util.find_in_list_of_lists(woman, self.male_prefs_GSlist[man])
                        index = self.male_prefs_GSlist[man][rank].index(woman)
                        type_2_labels[man][util.find_in_list_of_lists(woman, self.male_prefs_GSlist[man])][index] = i

        # print(type_1_labels)
        # print(type_2_labels)

        edges = []
        for i in range(len(self.male_prefs_GSlist)):
            p_star = -1
            for j in range(len(self.male_prefs_GSlist[i])):
                for k in range(len(self.male_prefs_GSlist[i][j])):
                    p = type_1_labels[i][j][k]
                    if p != -1:
                        if p_star != -1:
                            edges.append([1, p_star, p])
                        p_star = p
                    p2 = type_2_labels[i][j][k]
                    if p2 != -1 and p_star != -1 and p2 != p_star: # rotation can't have edge to itself, important
                        edges.append([2, p2, p_star])
                # if p != -1:
                #     p_star = p
        # print(edges)
        return edges


if __name__ == "__main__":


    pass