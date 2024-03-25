# Formula 1 Fantasy 2024

I'm developing some code for picking fantasy team adjustments throughout the Formula 1 season. These picks are initially going to be based on gambling lines' predicted qualifying and finish positions for each weekend. The pick methodology may grow into something different throughout the season as I see how well the initial code works.

The functions are in `weekend_functions.py`, and the two notebooks `prediction_analysis.ipynb` and `free_practice_analysis.ipynb` are used to perform the analyses. Since this effort is an ongoing work in progress, only essential updates will be posted here, as well as picks for each weekend.

The links below are to the actual race results for each race.

## Picks

[Bahrain](https://www.formula1.com/en/results.html/2024/races/1229/bahrain/race-result.html)  
**Driver Team**: Fernando Alonso (2x), Daniel Ricciardo, Carlos Sainz Jr., Oscar Piastri, Nico Hulkenberg  
**Constructor Team**: Ferrari, VisaCashApp RB  
**Predicted Points**: 85  
**Actual Points**: 142  

[Saudi Arabia](https://www.formula1.com/en/results.html/2024/races/1230/saudi-arabia/race-result.html)  
**Driver Team**: Max Verstappen (2x), Sergio Perez, Fernando Alonso, Charles Leclerc, Lando Norris  
**Constructor Team**: Ferrari, Red Bull Racing-RBPT  
**Predicted Points**: 288  
**Actual Points**: 312  
**Chip Used**: Limitless  

[Australia](https://www.formula1.com/en/results.html/2024/races/1231/australia/race-result.html)  
**Driver Team**: Max Verstappen (2x), Daniel Ricciardo, Oscar Piastri, Pierre Gasly, Nico Hulkenberg  
**Constructor Team**: Ferrari, VisaCashApp RB  
**Predicted Pointes**: 167  
**Actual Points**: 141  
**Note**: This would have been a great team if Verstappen hadn't DNF...  

### Notes

March 12, 2024:
I finally set this up as a repo to track my progress and have some github presence again.

March 20, 2024:
First time I generated team recommendations that I am confident in using, for the Australia GP. The main thing was getting the predicted scoring to be accurate based on each driver's predicted qualifying and race finishing positions. I used some logic found in another similar repo to score each possible team combination and pick the highest scoring team combination based on what team finances I have available. This also takes into account penalties incurred from the trade limits, each trade after 2 trades incurs a 10-point penalty on the weekend's score. So it really assesses each possible team combination within my budget and recommends the highest points value for the weekend.


