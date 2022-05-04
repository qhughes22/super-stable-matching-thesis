# Functions used to generate preference lists with indifference.

import random
import SuperStableMatchingInstance
import time
import itertools
from itertools import repeat

import util
from util import find_in_list_of_lists
import SuperStableMatchingInstance
import pickle
import math
from multiprocessing import Pool

def generate_tiered_prefs(size, man_tiers, seed):
    """Generates tiered preference lists.

    Parameters
    ----------
    size : int
        The number of agents in the instance
    man_tiers: list
        List of ints of size of each tier of the men's preferences over the women. IE, [10,20,20] has three tiers, with the top tier being size 10.
    seed: int
        random seed.
    Returns
    -------
    list
        Tiered preference list.
    """
    random.seed(seed)
    assert size == sum(man_tiers), "tiers are wrong size"
    man_prefs = []
     # tracks the starting rank for a given tier
    for man in range(size):
        prefs = []
        index = 0
        for tier in man_tiers:
            l = list(range(index, index + tier))
            random.shuffle(l)
            prefs.append([[item] for item in l])
            index += tier
        prefs = [item for sublist in prefs for item in sublist] # combine the tiers into single preference list
        man_prefs.append(prefs)

    # for woman in range(numAgents):
    #     prefs = []
    #     index = 0
    #
    #     for tier in woman_tiers:
    #         l = list(range(index, index + tier))
    #         random.shuffle(l)
    #         prefs.append([[item] for item in l])
    #         index += tier
    #     prefs = [item for sublist in prefs for item in sublist] # combine the tiers into single preference list
    #     woman_prefs.append(prefs)

    return man_prefs


def generate_k_range(size, woman_k, seed):
    """Generates k-range preference lists

        Parameters
        ----------
        size : int
            The number of agents in the instance
        woman_k: int
            The value of k for the instance.
        seed: int
            random seed.
        Returns
        -------
        list
            K-range preference list.
        """

    # can be uncommented. This code uses tiered generation when k is non binding
    # if woman_k >= size:
    #     return generate_tiered_prefs(size, [size], seed)


    # makes math simpler if the function assumes k-range is exclusive
    woman_k -= 1
    random.seed(seed)
    male_prefs = []
    minranks = [[i, size] for i in range(size)]  # minranks of women. Tuple of (minrank, count of that rank)
    maxranks = [[i, size] for i in range(size)]  # maxranks of women. Tuple of (maxrank, count of that rank)
    swapcount = []
    for i in range(size):
        swapcount.append(random.randint(int(1.5/(math.pi**2) * size * woman_k**2 * math.log(size, 2)),int(2/(math.pi**2) * size * woman_k**2 * math.log(size, 2))))
    notDone = list(range(size))
    for i in range(size):
        male_prefs.append([[i] for i in list(range(size))])

    while notDone != []:
        l = random.choice(notDone)
        place = random.randint(0, size - 2)
        a = male_prefs[l][place][0]
        if place + 1 > maxranks[a][0] and maxranks[a][0] - minranks[a][0] >= woman_k:
            continue
        b = male_prefs[l][place + 1][0]
        if place < minranks[b][0] and maxranks[b][0] - minranks[b][0] >= woman_k:
            continue
        male_prefs[l][place] = [b]
        male_prefs[l][place + 1] = [a]

        # 1 more count at maxrank
        if maxranks[a][0] == place + 1:
            maxranks[a][1] += 1

        # maxrank increased
        elif maxranks[a][0] < place + 1:
            maxranks[a] = [place + 1, 1]

        if minranks[a][0] == place:
            # minrank increased
            if minranks[a][1] == 1:
                minranks[a][0] = get_minrank(male_prefs, a)
                minranks[a][1] = count_occurences_of_agent_in_rank(male_prefs, a, minranks[a][0])
            # count at minrank decreased
            else:
                minranks[a][1] -= 1

        # count at minrank increased
        if minranks[b][0] == place:
            minranks[b][1] += 1
        # minrank decreased
        elif minranks[b][0] > place:
            minranks[b] = [place, 1]

        if maxranks[b][0] == place + 1:
            # maxrank decreased

            if maxranks[b][1] == 1:
                maxranks[b][0] = get_maxrank(male_prefs, b)
                maxranks[b][1] = count_occurences_of_agent_in_rank(male_prefs, b, maxranks[b][0])
            # count at minrank decreased
            else:
                maxranks[b][1] -= 1
        swapcount[l] -=1
        if swapcount[l] ==0:
            notDone.remove(l)
        # assert get_maxrank(male_prefs, a) == maxranks[a][0], "aa"
        # assert get_minrank(male_prefs, a) == minranks[a][0], "aa"
        # assert get_maxrank(male_prefs, b) == maxranks[b][0], "aa"
        # assert get_minrank(male_prefs, b) == minranks[b][0], "aa"

    # for i in range(size):
    #     assert get_maxrank2(male_prefs, i) == maxranks[i][0], "aa"
    #     assert get_minrank2(male_prefs, i) == minranks[i][0], "aa"

    return male_prefs

def count_occurences_of_agent_in_rank(lists, agent, rank):
    """Counts how many times a given agent appears in a given rank

        Parameters
        ----------
        lists : list
            The preference lists to be searched.
        agent: int
            The agent being searched for.
        rank: int
            The rank being checked.
        Returns
        -------
        int
            The count of the agent in that rank.
        """
    count = 0
    for list in lists:
        if list[rank][0] == agent:
            count+=1
    return count

def get_minrank(lists, agent):
    """ Gets the minrank of the agent in the lists.

        Parameters
        ----------
        lists : list
            The preference lists to be searched.
        agent: int
            The agent being searched for.

        Returns
        -------
        int
            The minrank of the agent.
        """
    minrank = float('inf')
    for list in lists:
        lowrank = 1
        ranking = find_in_list_of_lists(agent, list)
        if ranking == -1: # agent not in list
            continue
        for i in range(ranking): # iterate over ranks above agent to count
            lowrank += len(list[i])
        minrank = min(minrank, lowrank)
    # -1 makes 0 the lowest, not 1
    return minrank - 1

def get_maxrank(lists, agent):
    """ Gets the maxrank of the agent in the lists.

        Parameters
        ----------
        lists : list
            The preference lists to be searched.
        agent: int
            The agent being searched for.

        Returns
        -------
        int
            The maxrank of the agent.
        """
    maxrank = -1
    for list in lists:
        highrank = 0
        ranking = find_in_list_of_lists(agent, list)
        if ranking == -1: # agent not in list
            continue
        for i in range(ranking+1): # iterate over ranks above agent inclusive to count
            highrank += len(list[i])
        maxrank = max(maxrank, highrank)
    # -1 makes 0 the lowest, not 1
    return maxrank - 1

def get_k(prefs):
    """ Gets the minimum valid k for the preferences.

        Parameters
        ----------
        prefs : list
            The preference lists to be searched.
        Returns
        -------
        int
            The minimum valid k.
        """
    max_k = 0
    for woman in range(len(prefs)):
        max_k = max(max_k, get_maxrank(prefs, woman) - get_minrank(prefs, woman))
    return max_k + 1



def exhaustively_get_all_krange_prefs(size, k):
    """ Returns all possible k-range preferences by brute force. Not a recommended function without a terabyte of RAM.

        Parameters
        ----------
        size : int
            Size of the instance.
        k : int
            K restriction.
        Returns
        -------
        int
            All possible k-range preferences with those parameters.
        """
    k_range = []
    prefs = list(range(size))
    combos = itertools.product(itertools.permutations(prefs, size), repeat=size)

    for combo in combos:

        if get_k(combo) <= k:
            k_range.append(combo)
    return k_range


def add_indifference_iteratively(male_prefs, gamma, seed, max_k, num_women):
    """ Adds indifference to preference lists. All adjacent pairs on all lists are considered, and the ranks are
    merged with probability gamma if doing so would not violate k-range.

        Parameters
        ----------
        male_prefs : list
            Preferences to have indifference added
        gamma : float
            Probability that a given pair will have indifference added, if k-range restriction satisfied.
        seed : int
            Random seed.
        max_k : int
            K restriction.
        num_women: int
            Number of possible entries on the preference lists.
        Returns
        -------
        None
        """
    random.seed(seed)
    minranks = [get_minrank(male_prefs, i) for i in range(num_women)]
    maxranks = [get_maxrank(male_prefs, i) for i in range(num_women)]
    combos = list(itertools.product(list(range(len(male_prefs))), list(range(num_women))))
    random.shuffle(combos)

    for man, woman in combos:
        if random.random() < gamma:
            continue

        woman_index = find_in_list_of_lists(woman, male_prefs[man])
        # continue if woman not on list, or woman in first spot.
        if woman_index == -1 or woman_index ==0:
            continue

        # get the min/maxranks of all women in the indices to be merged
        highest_maxrank = max(maxranks[i] for i in male_prefs[man][woman_index])
        lowest_minrank = min(minranks[i] for i in male_prefs[man][woman_index-1])


        new_highrank = -1
        for i in range(woman_index + 1):  # new highrank is highrank of less preferred group
            new_highrank += len(male_prefs[man][i])
        new_lowrank = 1
        for i in range(woman_index - 1):  # new lowrank is lowrank of preferred group
            new_lowrank += len(male_prefs[man][i])
        # k range violated
        if max(new_highrank, highest_maxrank) - min(new_lowrank, lowest_minrank) >= max_k:
            continue
        for i in male_prefs[man][woman_index]:
            minranks[i] = min(new_lowrank, minranks[i])
        for i in male_prefs[man][woman_index - 1]:
            maxranks[i] = max(new_highrank, maxranks[i])
        male_prefs[man][woman_index - 1] += male_prefs[man].pop(woman_index)
    ks = [maxranks[i]-minranks[i]+1 for i in range(len(minranks))]

    # print(ks)
    for k in ks:
        assert k <= max_k, ks

# def generate_prefs(generation_func, size, k, indiff, count, remove_func= None, remove_prob=0.9):
#     """ Generates preference lists with indifference and incomplete lists by different possible methods. Has not been tested thoroughly
#
#          Parameters
#          ----------
#          generation_func : func
#              Function to be used to generate preferences. Either generate_tiered_prefs or generate_k_range
#          size : int
#              Size of instance to be generated.
#          k : int
#              K restriction.
#          indiff: float
#             Indifference parameter.
#          count: int
#             How many sets of preferences to generate.
#          remove_func: func
#              Function to use to determine how agents are removed from preference lists.
#          remove_prob: float
#             probability of removal to be passed to remove_func
#          Returns
#          -------
#          list
#             List of instances, each instance comprised of multiple preference lists
#          """
#     lists = []
#     for seed in range(count):
#         male_prefs = generation_func(size,k,seed)
#         # for a in range(size):
#         #     print (get_minrank(male_prefs,a), get_maxrank(male_prefs,a))
#         # add_indifference_push_your_luck(male_prefs, 0.8, seed, k, size)
#         add_indifference_iteratively(male_prefs, indiff, seed, k, size)
#         female_prefs = generation_func(size,k,seed+1)
#         add_indifference_iteratively(female_prefs, indiff, seed+1, k, size)
#         if remove_func is not None:
#             remove_func(male_prefs,female_prefs, remove_prob, seed)
#
#         lists.append([male_prefs, female_prefs])
#         print(seed)
#     return lists

def remove_at_random(male_prefs, female_prefs, prob, seed):
    """ Removes items at random from preference lists. Has not been tested thoroughly.

         Parameters
         ----------
         male_prefs : list
             Male preference list.
         female_prefs : list
             Female preference list.
         prob : float
             Probability of removal for any given pair.
         seed: int
            Random seed

         Returns
         -------
         None
         """
    random.seed(seed)
    combos = list(itertools.product(list(range(len(male_prefs))), list(range(len(female_prefs)))))
    random.shuffle(combos)
    for man,woman in combos:
        if random.random() < prob:
            continue

        woman_index = find_in_list_of_lists(woman, male_prefs[man])
        male_prefs[man][woman_index].remove(woman)
        if male_prefs[man][woman_index] == []:
            del male_prefs[man][woman_index]

        man_index = find_in_list_of_lists(man, female_prefs[woman])
        female_prefs[woman][man_index].remove(man)
        if female_prefs[woman][man_index] == []:
            del female_prefs[woman][man_index]

def save_prefs(prefs, path, size, k, preftype, indiff, remove_prob):
    """ Saves preferences to a file.

          Parameters
          ----------
          prefs : list
              Preferences to be saved.
          path : string
              Path to directory.
          size : int
              Size of instance.
          k: int
             K restriction.
          preftype: string
             Type of preferences.
          indiff: float
             Indifference parameter
          remove_prob: float
             removal parameter
          Returns
          -------
          None
          """
    filename = (f"{path}/{size}_{k}_{preftype}_{indiff}_{remove_prob}")
    try:
        my_file = open(filename)
        print(filename + "exists.")
        return False
    except FileNotFoundError:
        with open(filename, 'wb') as f:
            pickle.dump(prefs, f)

def load_prefs(dir, size, k, type, indiff, remove_prob):
    """ Loads preferences from a file.

          Parameters
          ----------
          prefs : list
              Preferences to be saved.
          path : string
              Path to directory.
          size : int
              Size of instance.
          k: int
             K restriction.
          preftype: string
             Type of preferences.
          indiff: float
             Indifference parameter
          remove_prob: float
             removal parameter
          Returns
          -------
          list
            Preferences loaded. Or false if not found
          """
    filename = (f"{dir}/{size}_{k}_{type}_{indiff}")
    try:
        with open(filename, 'rb') as fp:
            prefs = pickle.load(fp)
        return prefs
    except FileNotFoundError:
        print(filename + "exists.")
        return False

if __name__ == "__main__":
    start = time.time()

    # man_prefs, woman_prefs = generate_tiered_prefs(20,[10,10],[10,10], 0)
    k = 49
    size = 50
    indiff = 0.9
    count = 1
    lists = []
    remove_prob = 0.9
    seed = 13 # 5 50 13
    num_swaps = random.randint(int(k * size**2 * 1.5* math.log(size, 2)),int(k * size**2 * 2 * math.log(size, 2))) #TODO insert logn
    print(num_swaps)
    num_swaps2 = random.randint(int(1.5/(math.pi**2) * size * k**2 * math.log(size, 2)),int(2/(math.pi**2) * size * k**2 * math.log(size, 2)))
    print(num_swaps2)
    prefs = []
    # with Pool(8) as p:
    #     prefs = p.starmap( generate_k_range_one_side, zip(repeat(size), repeat(k), range(50), repeat(num_swaps)))
    # print(prefs)
    for seed in range(1):
    # #     # lists = generate_prefs(generate_k_range_one_side, size, k, indiff, count)
    # #     print(seed)
        generate_k_range(size, k, seed)
        print (time.time()-start)
        generate_k_range(size, k, seed)
        print(time.time() - start)

    #     # remove_at_random(man_prefs, woman_prefs, remove_prob, seed, size)
    #     # remove_at_random(woman_prefs, remove_prob, seed+1, size)
    #
    #     # for l in lists:
    #     # SuperStableMatchingInstance.run_example([man_prefs, woman_prefs])
    #
    #     # prefs = load_prefs("savedprefs",size, k, "k-range", 0.9)
    #     print (time.time()-start)
    # save_prefs(lists,"savedprefs",size, k, "k-range-removal", indiff)

    # man_prefs, woman_prefs = generate_tiered_prefs(100,[20,20,20,20,20],[25,25,25,25], 0)
    # man_prefs, woman_prefs = generate_tiered_prefs(100,[100],[100], 0)

    # SuperStableMatchingInstance.run_example([man_prefs,woman_prefs])
    # man_prefs, woman_prefs = generate_tiered_prefs(500,[50]*10,[50]*10, 0)
    # SuperStableMatchingInstance.run_example([man_prefs,woman_prefs])

    #
    # for i in range(len(prefs)):
    #     assert get_maxrank(prefs, i) - get_minrank(prefs, i) <k, 'a'
    # print(prefs)
    # print(exhaustively_get_all_krange_prefs(4, 2))


