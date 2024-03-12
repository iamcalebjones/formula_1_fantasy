import itertools
from sortedcontainers import SortedList
import pandas as pd

# in the google sheets, to have everything be numeric instead of having some entries as 'DNF' when all other entries are integers, the following will be used for OUT, DNF, DNQ, and DQ:
# OUT: 100 (racer did not participate in this round for some reason, e.g. Sainz in Saudi Arabia)
# DNF: 200 (racer did not finish the race, e.g. Gasly and Stroll in Saudi Arabia)
# DNQ: 300 (racer did not set a qualifying position, e.g. Zhou in Saudi Arabia)
# DQ: 400 (racer was disqualified from the session)

# this dictionary is used for awarding points based on race finishing position
race_position_to_points = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
    19: 0,
    20: 0,
    100: 0, # OUT
    200: -20, # DNF
    400: -25, # DQ
}

quali_position_to_points = {
    1: 10,
    2: 9,
    3: 8,
    4: 7,
    5: 6,
    6: 5,
    7: 4,
    8: 3,
    9: 2,
    10: 1,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
    19: 0,
    20: 0,
    100: 0, # OUT
    300: -5, # DNQ
    400: -15, # DQ
}

sprint_position_to_points = {
    1: 8,
    2: 7,
    3: 6,
    4: 5,
    5: 4,
    6: 3,
    7: 2,
    8: 1,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
    19: 0,
    20: 0,
    100: 0, # OUT
    200: -20, # DNF
    400: -25, # DQ
}

# the sheet_gid dict will track the track name and gid number in the google sheet so that I don't have to manually input that in the link
sheet_gid = {
    'bahrain': '0',
    'saudi_arabia': '1292963682',
    'australia': '549961289',
    'japan': '1992988195',
    'china': '1132356747',
    'miami': '681461098',
    'emilia_romagna': '2026706679',
    'monaco': '425345835',
    'canada': '852097953',
    'barcelona': '1202987965',
    'austria': '1330307608',
    'silverstone': '298017335',
    'hungary': '992512954',
    'spa': '189303210',
    'netherlands': '360128226',
    'monza': '1078389160',
    'baku': '1176328441',
    'singapore': '749459917',
    'austin': '1022980799',
    'mexico_city': '1826056750',
    'brazil': '1142844603',
    'las_vegas': '1191685802',
    'qatar': '1874670291',
    'abu_dhabi': '2040100542',
}


def drop_empties(df):
    '''
    quick utility function to drop the empty columns (columns with all NAN values) from a weekend dataframe so that its cleaner. 
    
    parameters:
    df: dataframe of weekend fp results, qualifying and race predictions and results
    
    returns:
    df: same dataframe with the empty columns removed
    '''
    drops = []
    for col in [x for x in df.columns if 'fp' in x or 'predicted' in x or 'actual' in x]:
        if all(df[col].isna()):
            drops.append(col)
    
    df = df.drop(columns = drops, axis=1)
    
    return df


def check_df(weekend_df):
    '''
    This function checks that the columns in the dataframe don't have any errors in the position numbers entered.
    Its checking that the sorted order of positions match the expected list of integers 1 through 20 for a col
    
    parametrs:
    df: dataframe of weekend fp results, qualifying and race predictions and results
    
    returns:
    nothing, just prints some statements based on anything identified that needs fixing
    '''
    
    for col in [x for x in weekend_df.columns if 'fp' in x or 'predicted' in x or 'actual' in x]:
        
        dnf_flag = 'DNF' in weekend_df[col].values.tolist()
        check_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        finishers = [x for x in weekend_df[col].values if x != 'DNF']
        
        if dnf_flag:
            print(f'Column "{col}" had some DNF\'s')
            check_order = check_order[:len(finishers)]
        if sorted(finishers) != check_order:
            print(f'Column "{col}" has an issue with the finishing positins represented in the data!')
            print(sorted(weekend_df[col].values))
            print('\n')
            
            
def driver_constructor_mappings(weekend_df):
    '''
    This function establishes the relationships between drives and constructors for the purpose of scoring lookups when assigning points.
    
    TODO: add the ability to remove any OUT drivers from the final dicts, (e.g. Sainz in Saudi Arabia)
    
    paramters:
    weekend_df: dataframe, full dataframe for a weekend's race
    
    returns:
    driver_to_constructor: dict, keys are drivers, values are their team names
    constructor_to_driver: dict, keys are constructors, values are lists of their drivers
    '''
    constructor_to_driver = {}
    for team in weekend_df.Team.unique():
        constructor_to_driver[team] = weekend_df.loc[weekend_df.Team == team]['Driver'].values.tolist()
        
    driver_to_constructor = {}
    for driver in weekend_df.Driver.unique():
        driver_to_constructor[driver] = weekend_df.loc[weekend_df.Driver == driver]['Team'].values[0]
        
    return driver_to_constructor, constructor_to_driver


def increase_score(what, who, how_much):
    '''
    utility function to increment the score of who by how much, 
    whether they are a driver in 'driver_scores' or a constructor in 'constructor_scores'
    
    parameters:
    what: dict, either constructor or driver scores
    who: string, key of either of the passed in dict to add to the score of. must be a driver or constructor
         as defined earlier in this notebook
    how_much: int, amount to add to the drivers' or constructor's score
    
    returns:
    what: dict, updated dict that was passed in of either the driver or constructor scores
    '''
    what[who] = what.get(who, 0) + how_much
    return what


def quali_result(position):
    '''
    utility function to help determine a driver's qualification result, q1, q2, or q3,
    meaning which qualification session did they end quali in
    
    parameters:
    position: int, numerical qualification finishing position
    
    returns:
    string of the qualification classification, one of 'Q1', 'Q2', 'Q3'
    '''
    if position <= 10:
        return 'Q3'
    elif position >= 11 and position <= 15:
        return 'Q2'
    elif position > 15 and position <= 20:
        return 'Q1'


def score_race_order(
    quali_order,
    race_order,
    driver_scores,
    constructor_scores,
    driver_gain_loss_overtake,
    driver_to_constructor,
    constructor_to_driver):
    '''
    this function scores the race results, whether predicted or actual. 
    it takes the predicted and actual from either qualifying or the race, awards points for positions gained/lost, and awards points for finish order in the top 10. 
    it does not account for fastest lap although maybe it should... have to think more about that.
    
    parameters:
    quali_order: list, either predicted or actual quali order
    race_order: list, either predicted or actual race order
    driver_scores: dict, dict of the drivers' scores
    driver_gain_loss_overtake: dict, dict of each driver's gain/loss and overtake for the race, as determined by F1 Fantasy folks, hand-entered in google sheet after the race
    constructor_scores: dict, dict of the constructors' scores
    driver_to_construcotr: dict, maps drivers to the constructor they drive for
    constructor_to_driver: dict, maps constructors to their drivers
    
    returns: 
    driver_scores: dict, updated dict that was passed in of the drivers' scores
    constructor_scores: dict, updated dict that was passed in of the constructors' scores
    
    '''
    # Assumed to have finished the race. Not looking at streaks yet.
    driver_score_summary = {}
    constructor_score_summary = {}
    for index, driver in enumerate(race_order):
        
        constructor = driver_to_constructor[driver]
        driver_score_summary[driver] = {}
        driver_score_summary[driver]['constructor'] = constructor
        driver_points = 0
        constructor_points = 0
        
        driver_gain_loss = driver_gain_loss_overtake[driver]['gain_loss']
        driver_overtake = driver_gain_loss_overtake[driver]['overtake']
        
        # score driver and constructor for positions gained/lost +1/-1
        driver_points += driver_gain_loss + driver_overtake
        constructor_points += driver_gain_loss + driver_overtake

        quali_position = quali_order.index(driver) + 1
        race_position = index + 1
        
        driver_score_summary[driver]['quali_position'] = quali_position
        driver_score_summary[driver]['race_position'] = race_position
        driver_score_summary[driver]['gain_loss'] = driver_gain_loss
        driver_score_summary[driver]['overtake'] = driver_overtake
        
        # score driver and constructor for finishing position
        # +1-25 for position
        position_points = race_position_to_points.get(race_position)
        if position_points:
            driver_points += position_points
            constructor_points += position_points
        
        driver_score_summary[driver]['quali_position_points'] = 11 - quali_position if quali_position <=10 else 0
        driver_score_summary[driver]['race_position_points'] = position_points
        
        driver_scores = increase_score(driver_scores, driver, driver_points)
        constructor_scores = increase_score(constructor_scores, constructor, constructor_points)
        
    
    return driver_scores, constructor_scores, driver_score_summary, constructor_score_summary


def score_qualification_order(
    quali_order,
    driver_scores,
    constructor_scores,
    driver_to_constructor,
    constructor_to_driver,
    driver_score_summary,
    constructor_score_summary):
    '''
    this scores the quali results for drivers and constructors, whether predicted or actual.
    
    parameters:
    quali_order: list, names in order of qualifying, either predicted or actual
    driver_scores: dict, dict of the drivers' scores
    constructor_scores, dict, dict of the constructors' scores
    driver_to_construcotr: dict, maps drivers to the constructor they drive for
    constructor_to_driver: dict, maps constructors to their drivers
    driver_score_summary: dict, tracks points and their source attributed to each driver
    constructor_score_summary: dict, tracks points and their sourec attributed to each contstructor
    
    returns:
    driver_scores: dict, updated dict that was passed in of the drivers' scores
    constructor_scores, dict, updated dict that was passed in of the constructors' scores
    driver_score_summary: dict, updated tracking points and their source attributed to each driver
    constructor_score_summary: dict, updated tracking points and their sourec attributed to each contstructor
    '''
    
    # score drivers' qualification results assuming all qualify and aren't getting negative points
    for index, driver in enumerate(quali_order):
        driver_points = 0
        constructor_points = 0
        constructor = driver_to_constructor[driver]
        constructor_score_summary[constructor] = {}
        
        # +1-10 for top 10 positions
        quali_position = index + 1
        position_points = quali_position_to_points.get(quali_position)
        position_points = position_points if type(position_points) == int else 0
        
        driver_points += position_points
        constructor_points += position_points
        
        driver_scores = increase_score(driver_scores, driver, driver_points)
        constructor_scores = increase_score(constructor_scores, constructor, constructor_points)
            
    # score constructors' qualification results based on how the drivers qualify
    for constructor, drivers in constructor_to_driver.items():
        # which qualifying position did each driver finish in
        driver1_quali_pos, driver2_quali_pos = quali_order.index(drivers[0]) + 1, quali_order.index(drivers[1]) + 1
        
        # which qualifying round did each driver finish in
        driver1_quali_round, driver2_quali_round = quali_result(driver1_quali_pos), quali_result(driver2_quali_pos)

        quali_position_points = sum(map(lambda d: quali_position_to_points[d], [driver1_quali_pos, driver2_quali_pos]))

        qualis = [driver1_quali_round, driver2_quali_round]
        q3_tot = [x for x in qualis if x == 'Q3']
        q2_tot = [x for x in qualis if x == 'Q2']

        # q3 finishers
        if len(q3_tot) == 2:
            team_quali_score = 10
        elif len(q3_tot) == 1:
            team_quali_score = 5
                
        # q2 finishers
        elif len(q2_tot) == 2:
            team_quali_score = 3
        elif len(q2_tot) == 1:
            team_quali_score = 1

        # nobody got past q1
        else:
            team_quali_score = -1

        constructor_scores = increase_score(constructor_scores, constructor, team_quali_score)
        
        constructor_score_summary[constructor]['quali_position_points'] = quali_position_points
        constructor_score_summary[constructor]['quali_finish_points'] = team_quali_score
        constructor_score_summary[constructor]['quali_results'] = {drivers[0]: driver1_quali_pos, drivers[1]: driver2_quali_pos}

    return driver_scores, constructor_scores, driver_score_summary, constructor_score_summary


def score_superlatives(
    driver_scores,
    constructor_scores,
    driver_to_constructor,
    driver_score_summary,
    constructor_score_summary,
    fastest_driver,
    driver_ofthe_day = None,
    fastest_constructor = None,
    second_fastest_constructor = None,
    third_fastest_constructor = None,):
    '''
    This scores the extra bits after the race is over. Fastest driver, driver of the day, fastest, second and third fastest pitstops.
    
    params:
    fastest_driver: string
    driver_ofthe_day: string
    fastest_constructor: string
    second_fastest_constructor: string
    driver_scores: dictionary
    constructor_scores: dictionary
    driver_score_summary: dict, tracks points and their source attributed to each driver
    constructor_score_summary: dict, tracks points and their sourec attributed to each contstructor
    
    returns:
    driver_scores: dictionary
    constructor_scores: dictionary
    driver_score_summary: dict, updated tracking points and their source attributed to each driver
    constructor_score_summary: dict, updated tracking points and their sourec attributed to each contstructor
    '''
    
    # fastest lap
    driver_scores = increase_score(driver_scores, fastest_driver, 10)
    constructor_scores = increase_score(constructor_scores, driver_to_constructor[fastest_driver], 10)
    driver_score_summary[fastest_driver]['fastest_lap'] = 10
    constructor_score_summary[driver_to_constructor[fastest_driver]]['fastest_lap'] = 10
    
    # driver of the day
    if driver_ofthe_day:
        driver_scores = increase_score(driver_scores, driver_ofthe_day, 10)
        driver_score_summary[driver_ofthe_day]['driver_of_the_day'] = 10
    
    # fastest pitstop
    if fastest_constructor:
        constructor_scores = increase_score(constructor_scores, fastest_constructor, 10)
        constructor_score_summary[fastest_constructor]['fastest_pitstop'] = 10
    
    # second fastest pitstop
    if second_fastest_constructor:
        constructor_scores = increase_score(constructor_scores, second_fastest_constructor, 5)
        constructor_score_summary[second_fastest_constructor]['second_fastest_pitstop'] = 5
    
    # third fastest pitstop
    if third_fastest_constructor:
        constructor_scores = increase_score(constructor_scores, third_fastest_constructor, 3)
        constructor_score_summary[third_fastest_constructor]['third_fastest_pitstop'] = 3

    
    return driver_scores, constructor_scores, driver_score_summary, constructor_score_summary


def score_race_full(driver_scores,
               constructor_scores,
               actual_qualifying_order,
               actual_race_order,
               driver_gain_loss_overtake,
               driver_to_constructor,
               constructor_to_driver, 
               fastest_lap,
               driver_ofthe_day,
               fastest_pitstop,
               second_fastest_pitstop,
               third_fastest_pitstop
              ):
    
    '''
    This function combines all the pieces to score a full race weekend into one function call for the take of taking less space up in the jupyter notebook where its going to be used.
    
    parameters:
    driver_scores: dict, drivers and their scores
    constructor_scores: dict, constructors and their scores
    actual_qualifying_order: list, final order of qualifying
    actual_race_order: list, final order of the race
    driver_gain_loss_overtake: dict, driver's weekend tally for gain/loss and overtakes
    driver_to_constructor: dict, driver to constructor mapping
    constructor_to_driver: dict, constructor to driver mapping
    fastest_lap: str
    driver_ofthe_day: str or None
    fastest_pitstop: str or None
    second_fastest_pitstop: str or None
    third_fastest_pitstop: str or None
    
    returns:
    driver_scores: dict, final tabulated driver scores for the weekend
    constructor_scores: dict, final tabulated constructor scores for the weekend
    driver_score_summary: dict, final details of all the points each driver scored
    constructor_score_summary: dict, final details of all the points each constructor scored
    '''
    
    # score race order
    driver_scores, constructor_scores, driver_score_summary, constructor_score_summary = score_race_order(
        actual_qualifying_order,
        actual_race_order,
        driver_scores,
        constructor_scores,
        driver_gain_loss_overtake,
        driver_to_constructor,
        constructor_to_driver)
    
    # score qualifying order
    driver_scores, constructor_scores, driver_score_summary, constructor_score_summary = score_qualification_order(
        actual_qualifying_order,
        driver_scores,
        constructor_scores,
        driver_to_constructor,
        constructor_to_driver,
        driver_score_summary,
        constructor_score_summary)
    
    # score superlatives
    driver_scores, constructor_scores, driver_score_summary, constructor_score_summary = score_superlatives(
        driver_scores,
        constructor_scores,
        driver_to_constructor,
        driver_score_summary,
        constructor_score_summary,
        fastest_lap,
        driver_ofthe_day,
        fastest_pitstop,
        second_fastest_pitstop,
        third_fastest_pitstop,)
    
    return driver_scores, constructor_scores, driver_score_summary, constructor_score_summary


