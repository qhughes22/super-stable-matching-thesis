# Super Stable Matching and K-Range
Codebase for my senior honors project on super-stable matching and k-range preferences.

This is the code I used for the honors project I submitted to Amherst College on 4/18/22. 

If you want to use these functions to run stable matching algorithms, I suggest you look to this repo instead. It contains the scripts that might be useful without files specific to my project.

# Files
1. SuperStableMatchingInstance.py: This class includes the stable matching algorithms implemented for this paper. It includes functions to find the super-stable matching poset for any SMTI instance and to find all super-stable matchings.
2. test.py: This file includes tests for the functions in SuperStableMatchingInstance.py.
3. util.py: This file includes helper functions used in SuperStableMatchingInstance.py
4. GraphVisualization.py: This file includes the Digraph class, a wrapper class around NetworkX's DiGraph. Mostly used for easier visualization of digraphs for debugging SuperStableMatchingInstance.py.
5. generate_prefs_with_indifference.py: This file provides functions for generating random k-range preferences through a method of iterative adjacent swaps. It also provides functions for generating tiered preferences and adding indifference to existing lists.
6. generate_and_upload.py: This file generates random k-range preferences using functions in generate_prefs_with_indifference.py based on command-line arguments and pushes them to AWS S3. 
7. generate_and_upload.py: Same as above, but for tiered preferences.
8. add_indifference.py: This file reads preferences pushed to S3 and adds indifference to them using functions in generate_prefs_with_indifference.py and uploads to S3 the new lists.
9. make_results.py: This script takes preference lists from S3 and runs the algorithms in SuperStableMatchingInstance.py on them, and saves the stable matchings, rotations, and edges of the rotation poset to S3.
10. ec2_script.py: This is a script used to run the scripts above on AWS EC2 instances.
11. generate_swaps_analysis.py: This script was used to generate the figures analyzing the swapping method in my paper.
12. indifference_analysis.ipynb: This notebook was used to generate graphs analyzing the indifference adding method in my paper.
13. master_datavis.ipynb: This notebook generated the graphs in my paper for analyzing the structure of the rotation poset. In particular it calculated the number of stable matching, the number of rotations, and the height, size of the maximum antichain, and pathwidth of the rotation poset.
