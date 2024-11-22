import json
from typing import List, Dict
from enum import Enum


class MatchType(Enum):
    EQUAL = 'equalto'
    NOT_EQUAL = 'notequalto'
    IS_IN = 'isin'
    IS_NOT_IN = 'isnotin'

# Mapping dictionaries
AIRPORT_TO_COUNTRY = {
    'LHR': 'UK',
    'LGW': 'UK',
    'MAN': 'UK',
    'HKG': 'HK',
    'JFK': 'US',
    'LAX': 'US',
    'SHA': 'CN',
    'PEK': 'CN'
}

AIRPORT_TO_CITY = {
    'LHR': 'LON',
    'LGW': 'LON',
    'HKG': 'HKG',
    'JFK': 'NYC',
}

def match_airline(pnr_value: str, condition: Dict) -> bool:
    """
    Match airline specific rules
    """
    pnr_airline = pnr_value.upper()
    rule_value = condition['airlineKey'].upper()
    operator = MatchType(condition['operatorKey'])
    
    # Handle comma-separated values
    rule_values = set(rule_value.split(',')) if ',' in rule_value else {rule_value}
    
    # Special case for 'all'
    if rule_value == 'ALL':
        return True if operator == MatchType.EQUAL else False
        
    match operator:
        case MatchType.EQUAL:
            return pnr_airline in rule_values
        case MatchType.NOT_EQUAL:
            return pnr_airline not in rule_values
        case MatchType.IS_IN:
            return pnr_airline in rule_values
        case MatchType.IS_NOT_IN:
            return pnr_airline not in rule_values
    
    return False

def match_destination(pnr_value: str, condition: Dict) -> bool:
    """
    Match destination specific rules with second layer support
    """
    pnr_destination = pnr_value.upper()
    rule_value = condition['destinationKey'].upper()
    operator = MatchType(condition['operatorKey'])
    second_layer = condition.get('secondLayer')
    
    # Transform PNR value based on second layer
    if second_layer == 'country':
        pnr_destination = AIRPORT_TO_COUNTRY.get(pnr_destination, pnr_destination)
    elif second_layer == 'city':
        pnr_destination = AIRPORT_TO_CITY.get(pnr_destination, pnr_destination)
    
    # Handle comma-separated values
    rule_values = set(rule_value.split(',')) if ',' in rule_value else {rule_value}
    
    # # Special case for 'all'
    # if rule_value == 'ALL':
    #     return True if operator == MatchType.EQUAL else False
        
    match operator:
        case MatchType.EQUAL:
            return pnr_destination in rule_values
        case MatchType.NOT_EQUAL:
            return pnr_destination not in rule_values
        case MatchType.IS_IN:
            return pnr_destination in rule_values
        case MatchType.IS_NOT_IN:
            return pnr_destination not in rule_values
    
    return False

def match_origin(pnr_value: str, condition: Dict) -> bool:
    """
    Match origin specific rules with second layer support
    """
    pnr_origin = pnr_value.upper()
    rule_value = condition['originKey'].upper()
    operator = MatchType(condition['operatorKey'])
    second_layer = condition.get('secondLayer')
    
    # Transform PNR value based on second layer
    if second_layer == 'country':
        pnr_origin = AIRPORT_TO_COUNTRY.get(pnr_origin, pnr_origin)
    elif second_layer == 'city':
        pnr_origin = AIRPORT_TO_CITY.get(pnr_origin, pnr_origin)
    
    # Handle comma-separated values
    rule_values = set(rule_value.split(',')) if ',' in rule_value else {rule_value}
    
    # # Special case for 'all'
    # if rule_value == 'ALL':
    #     return True if operator == MatchType.EQUAL else False
        
    match operator:
        case MatchType.EQUAL:
            return pnr_origin in rule_values
        case MatchType.NOT_EQUAL:
            return pnr_origin not in rule_values
        case MatchType.IS_IN:
            return pnr_origin in rule_values
        case MatchType.IS_NOT_IN:
            return pnr_origin not in rule_values
    
    return False

def match_cabinclass(pnr_value: str, condition: Dict) -> bool:
    """
    Match cabin class specific rules
    """
    pnr_cabin = pnr_value.lower()
    rule_value = condition['cabinclassKey'].lower()
    operator = MatchType(condition['operatorKey'])
    
    # Handle comma-separated values
    rule_values = set(rule_value.split(',')) if ',' in rule_value else {rule_value}
    
    # Special case for 'all'
    if rule_value == 'all':
        return True if operator == MatchType.EQUAL else False
        
    match operator:
        case MatchType.EQUAL:
            return pnr_cabin in rule_values
        case MatchType.NOT_EQUAL:
            return pnr_cabin not in rule_values
        case MatchType.IS_IN:
            return pnr_cabin in rule_values
        case MatchType.IS_NOT_IN:
            return pnr_cabin not in rule_values
    
    return False

def match_condition(pnr_data: Dict, condition: Dict) -> bool:
    """
    Route condition to appropriate matching function
    """
    rule_type = condition['ruleTypeKey']
    
    match rule_type:
        case 'origin':
            return match_origin(pnr_data.get('origin', ''), condition)
        case 'destination':
            return match_destination(pnr_data.get('destination', ''), condition)
        case 'cabinclassname':
            return match_cabinclass(pnr_data.get('cabinclass', ''), condition)
    
    return False

def find_matching_rules(pnr_data: Dict, rules_file: str = 'rules.json') -> List[Dict]:
    """
    Main function to find matching rules for a PNR, filtering first by airline
    """
    matching_rules = []
    pnr_airline = pnr_data.get('airline', '').upper()
    
    # Load rules
    with open(rules_file, 'r') as f:
        rules_data = json.load(f)
    
    # First filter rules by airline
    airline_matching_rules = []
    for rule in rules_data['rules']:
        airline_condition = next(
            (condition for condition in rule['conditions'] 
             if condition['ruleTypeKey'] == 'airline'),
            None
        )
        
        # If no airline condition, skip this rule
        if not airline_condition:
            continue
            
        # Check if airline matches using match_airline function
        if match_airline(pnr_airline, airline_condition):
            airline_matching_rules.append(rule)
    
    # Then check other conditions only for airline-matching rules
    for rule in airline_matching_rules:
        all_conditions_match = True
        
        # Check each non-airline condition in the rule
        for condition in rule['conditions']:
            if condition['ruleTypeKey'] == 'airline':
                continue  # Skip airline condition as we already checked it
                
            if not match_condition(pnr_data, condition):
                all_conditions_match = False
                break
        
        if all_conditions_match:
            matching_rules.append({
                'ruleId': rule['ruleId'],
                'point': rule.get('point', 0),  # Default to 0 if point not specified
                'markupValue' :rule.get('markupValue')
            })
    
    # Sort matching rules by points in descending order
    matching_rules.sort(key=lambda x: x['point'], reverse=True)
    
    return matching_rules


if __name__ == '__main__':
    # Example usage
    pnr_data = {
        "airline": "AC",
        "origin": "SHA",
        "destination": "PEK",
        "cabinclass": "economy"
    }

    matching_rules = find_matching_rules(pnr_data)

    # Print sorted rules with points
    print("Matching Rules (sorted by points):")
    for rule in matching_rules:
        print(f"Rule ID: {rule['ruleId']}, Points: {rule['point']}, markupValue: {rule['markupValue']}")