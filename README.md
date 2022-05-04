# Super Stable Matching and K-Range
Tools I created as part of my senior honors project on super-stable matching and k-range preferences. Implementations of algorithms related to super-stable matchings can be found here, along with scripts to generate preferences restricted in either a tiered model or a k-range model.

The full codebase for my project can be found at https://github.com/qhughes22/super-stable-matching-thesis. This repo contains the code that may be useful to anyone trying to study the stable matching problem, introduce by [Gale and Shapley](https://www.eecs.harvard.edu/cs286r/courses/fall09/papers/galeshapley.pdf).

Super-stable matchings are a notion of stability when considering stable matching with ties.
A matching is super stable if and only if there is no man and woman such that the two weakly
prefer to be with each other than with their current respective partners. The super stable
matchings in an instance follow the structure of a rotation poset analogous to that of
stable matchings, as shown in 
[this paper](https://www.semanticscholar.org/paper/Characterization-of-Super-stable-Matchings-Hu-Garg/26a40b22967e22eb417a31c4e6c2d2291e09b1c1) by Hu and Garg. 

K-range preferences were introduced by [Bhatnagar et al](https://www.researchgate.net/publication/220780434_Sampling_stable_marriages_Why_spouse-swapping_won't_work)
as a parametrically restricted preference model.
In this model, there is an objective ranking for each set of agents, and no agent can deviate to
o far from this objective ranking. This model is motivated by examples such as colleges ranking prospective applicants. They may be use objective metrics like SAT scores as a guide, but have some flexibility within that objective ranking.

Formally, if a set of men's preferences over women has a range of *k*, and a man ranks some woman in the *i*th rank on his list, then that woman can be ranked no lower than *i-k+1* and no higher than *i+k-1* on any list. This model can be extended to preferences with indifference; we consider women to occupy all the ranks on a list possible under any resolution of ties.


## Setup

Clone the repo, and run `pip install -r requirements.txt` to install necessary packages.

## Usage

SuperStableMatchingInstance is the class which stores an instance of SMTI and has methods implemented to find the woman/man-optimal super-stable matchings, check for weak stability, strong stability, and super-stability, and find the super-stable rotation poset and all super-stable matchings for the instance.

Instances are created using pairs of sets of preferences, where each element in the set is a list of lists denoting a single agent's preferences. generate_prefs_with_indifference.py includes functions to generate preferences in that format, either under the k-range model or with a tiered model. There is also a function to randomly insert indifference into lists.

The tiered model is simple. Considering the lists of male preferences of women, the tiered model divides women into sequential tiers, with men universally preferring women in one tier to women in the next. We generate tiered preferences by simply dividing women into tiers and then shuffling within the tier in each list. The function generate_tiered_prefs implements this

We also generate k-range preferences through a method of iterative adjacent swaps. We start with master list preferences of men over women.
For each man's list, we randomly set a number of swaps to be executed, ranging between *(1.5/\π^2 * n * k^2 * log(n))* to 
*(2/π^2 * n * k^2 * log(n))*. We select lists at random and swap two random adjacent elements, if doing so would not violate k-range restrictions.
This process continues until all lists have had their predetermined number of swaps executed.

Indifference is added to created lists similarly. To add indifference, we consider every pair of adjacent elements on all lists.
We select at random one such pair, and with a set probability merge them into a single indifference class if doing so would not violate k-range.

Through this method we get random k-range instances with indifference. It has not been proven that we reach a uniform distribution of k-range instances
with the number of swaps executed; further work aims to analyze this question. 

## Files
1. SuperStableMatchingInstance.py: This class includes stable matching algorithms. It includes functions to find the super-stable matching poset for any SMTI instance and to find all super-stable matchings.
2. test.py: This file includes tests for the functions in SuperStableMatchingInstance.py.
3. util.py: This file includes helper functions used in SuperStableMatchingInstance.py
4. GraphVisualization.py: This file includes the Digraph class, a wrapper class around NetworkX's DiGraph. Mostly used for easier visualization of digraphs for debugging SuperStableMatchingInstance.py.
5. generate_prefs_with_indifference.py: This file provides functions for generating random k-range preferences through a method of iterative adjacent swaps. It also provides functions for generating tiered preferences and adding indifference to existing lists.
