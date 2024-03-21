# Formula 1 Fantasy 2024

I'm developing some code for picking fantasy team adjustments throughout the Formula 1 season.

The functions are in `weekend_functions.py`, and the function development and testing is in `weekend_scoring.ipynb`. The notebook `free_practice_assessment.ipynb` was initially used to assess the Free Practice results during a race weekend. I may revisit this eventually, but for now I'm focusing on accurately scoring the race weekend per the fantasy scoring structure, and then I will adjust this code to predicting scoring based on odds lines issued by DraftKings going into the weekend. This will eventually be used to forecast the best team composition ahead of the weekend for making the correct team changes going into the next race.

March 12, 2024:
I finally set this up as a repo to track my progress and have some github presence again.

March 20, 2024:
First time I generated team recommendations that I am confident in using, for the Australia GP. The main thing was getting the predicted scoring to be accurate based on each driver's predicted qualifying and race finishing positions. I used some logic found in another similar repo to score each possible team combination and pick the highest scoring team combination based on what team finances I have available. This also takes into account penalties incurred from the trade limits, each trade after 2 trades incurs a 10-point penalty on the weekend's score. So it really assesses each possible team combination within my budget and recommends the highest points value for the weekend.


