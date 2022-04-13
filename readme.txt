Run this file directly through python:
> python .\vacuum.py

This will run all three agents in both environments and print out their results.
The random agent is run 50 times. Sample output is below:

AGENT: Model-based reflex agent with memory
Ending:     CLEAN: 100,  DIRTY 0
Cleaned 100 cells in 225 actions

.AGENT: Model-based reflex agent with memory
Wall in front of vacuum, unable to move forward
Wall in front of vacuum, unable to move forward
Ending:     CLEAN: 73,  DIRTY 12
Cleaned 73 of 84 cells in 225 actions

.AGENT: Memory-less deterministic reflex agent
Ending:     CLEAN: 36,  DIRTY 49
Cleaned 36 of 84 cells in 85 actions

.AGENT: Memory-less deterministic reflex agent
Ending:     CLEAN: 36,  DIRTY 64
Cleaned 36 of 99 cells in 85 actions

.[489, 600, 517, 592, 469, 622, 636, 479, 600, 608, 579, 406, 656, 627, 582, 490
, 428, 628, 525, 541, 500, 477, 497, 522, 612, 606, 627, 522, 488, 590, 507, 425
, 345, 462, 550, 630, 499, 480, 549, 624, 501, 365, 683, 505, 517, 559, 433, 821
, 495, 513]
Avg of 50 trials (single room): 539
.[592, 642, 794, 537, 842, 638, 873, 689, 978, 463, 734, 612, 747, 1053, 612, 70
4, 928, 709, 541, 479, 657, 920, 424, 617, 1140, 1053, 1092, 1010, 770, 768, 73
, 761, 543, 824, 716, 424, 625, 813, 861, 984, 712, 521, 692, 909, 765, 937, 66
, 762, 999, 689]
Avg of 50 trials (4 room): 751
.
----------------------------------------------------------------------
Ran 6 tests in 2.336s

OK

Process finished with exit code 0
