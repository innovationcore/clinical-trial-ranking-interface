import requests
import pandas as pd
from typing import Dict, List, Optional
from urllib.parse import urlencode
import json


# Written by Mitchell Klusty
class ClinicalTrialsFilterV2:
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        
    def search_trials(self,
                     condition: Optional[str] = None,
                     sex: Optional[str] = None,
                     min_age: Optional[int] = None,
                     max_age: Optional[int] = None,
                     location: Optional[str] = None,
                     status: str = "RECRUITING",
                     sort_by_relevance: bool = False, # by default, results are unsorted although clinicaltrials has relevance as an internal system
                     page_size: int = 100) -> pd.DataFrame: # maximum value is 1000, anything higher is coerced down
        """
        Search for clinical trials using ClinicalTrials.gov API v2 studies endpoint
        """
        params = {
            'format': 'json',
            'pageSize': page_size,
            'filter.overallStatus': status,
        }
        
        if condition:
            params['query.cond'] = condition
            
        if location:
            params['query.locn'] = location
            
        agg_filters = []
        if sex and sex != 'ALL':
            agg_filters.append(f'sex:{sex[0].lower()}')
            
        if agg_filters:
            params['aggFilters'] = ','.join(agg_filters)

        if sort_by_relevance:
            params['sort'] = '@relevance'
        
        response = requests.get(
            self.base_url,
            params=params,
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        
        data = response.json()
        studies = data.get('studies', [])
        
        if not studies:
            return pd.DataFrame()

        records = []
        for study in studies:
            protocol = study.get('protocolSection', {})
            identification = protocol.get('identificationModule', {})
            description = protocol.get('descriptionModule', {})
            eligibility = protocol.get('eligibilityModule', {})
            status_module = protocol.get('statusModule', {})
            contacts_locations = protocol.get('contactsLocationsModule', {})
            
            locations = contacts_locations.get('locations', [])
            location_info = locations[0] if locations else {}
            
            record = {
                "nct_id": identification.get('nctId'),
                "title": identification.get('briefTitle'),
                "detailed_description": description.get('detailedDescription'),
                "brief_summary": description.get('briefSummary'),
                "conditions": protocol.get('conditionsModule', {}).get('conditions', []),
                "eligibility_criteria": eligibility.get('eligibilityCriteria'),
                "healthy_volunteers": eligibility.get('healthyVolunteers'),
                "sex": eligibility.get('sex'),
                "minimum_age": eligibility.get('minimumAge'),
                "maximum_age": eligibility.get('maximumAge'),
                "std_age_list": eligibility.get('stdAges', []),
                "phase": status_module.get('phase'),
                "status": status_module.get('overallStatus'),
                "facility": location_info.get('facility', ''),
                "city": location_info.get('city', ''),
                "state": location_info.get('state', ''),
                "zip": location_info.get('zip', ''),
                "country": location_info.get('country', '')
            }
            records.append(record)
            
        df = pd.DataFrame(records)
        
        if min_age is not None or max_age is not None:
            df = self._filter_by_age(df, min_age, max_age)
            
        return df
    
    def _filter_by_age(self, df: pd.DataFrame, 
                      min_age: Optional[int], 
                      max_age: Optional[int]) -> pd.DataFrame:
        """Filter trials by age criteria"""
        def parse_age(age_str: str) -> Optional[float]:
            if pd.isna(age_str) or not isinstance(age_str, str):
                return None
            try:
                value = int(''.join(filter(str.isdigit, age_str)))
                if 'Month' in age_str:
                    value = value / 12
                elif 'Week' in age_str:
                    value = value / 52
                return value
            except:
                return None
        
        df["min_age_years"] = df["minimum_age"].apply(parse_age)
        df["max_age_years"] = df["maximum_age"].apply(parse_age)
        
        if min_age is not None:
            df = df[df["max_age_years"].isna() | (df["max_age_years"] >= min_age)]
            
        if max_age is not None:
            df = df[df["min_age_years"].isna() | (df["min_age_years"] <= max_age)]
            
        return df

def display_trial_details(trial: pd.Series, patient_info: Dict):
    """
    Display detailed information about a trial and matching criteria
    
    Args:
        trial: Series containing trial information
        patient_info: Dictionary containing patient criteria
    """
    print("\n" + "="*80)
    print(f"Study: {trial['title']}")
    print(f"NCT ID: {trial['nct_id']}")
    print("="*80)
    
    print("\nBRIEF SUMMARY:")
    print("-"*80)
    print(trial['brief_summary'] if pd.notna(trial['brief_summary']) else "Not provided")
    
    print("\nDETAILED DESCRIPTION:")
    print("-"*80)
    print(trial['detailed_description'] if pd.notna(trial['detailed_description']) else "Not provided")
    
    print("\nMATCHING CRITERIA:")
    print("-"*80)
    print(f"Location: {trial['city']}, {trial['state']}, {trial['country']}")
    print(f"Your location: {patient_info['location']}")
    
    print(f"\nsex: {trial['sex']}")
    print(f"Your sex: {patient_info['sex']}")
    
    print(f"\nAge range: {trial['minimum_age']} - {trial['maximum_age']}")
    print(f"Your age: {patient_info['age']}")
    
    print(f"\nConditions: {', '.join(trial['conditions'])}")
    print(f"Your condition: {patient_info['condition']}")
    
    print("\nFULL ELIGIBILITY CRITERIA:")
    print("-"*80)
    if pd.notna(trial['eligibility_criteria']):
        print(trial['eligibility_criteria'])
    else:
        print("Not provided")
    
    print("\nADDITIONAL INFORMATION:")
    print("-"*80)
    print(f"Phase: {trial['phase']}")
    print(f"Status: {trial['status']}")
    print(f"Facility: {trial['facility']}")
    print(f"Accepts healthy volunteers: {trial['healthy_volunteers']}")
    print("="*80 + "\n")

def find_trials_for_patient(patient_info: Dict) -> pd.DataFrame:
    """Find clinical trials matching patient criteria"""
    ct_filter = ClinicalTrialsFilterV2()
    
    trials = ct_filter.search_trials(
        condition=patient_info['condition'],
        sex=patient_info['sex'],
        min_age=patient_info['age'],
        max_age=patient_info['age'],
        location=patient_info['location']
    )
    
    return trials
def get_trial_details(trial: pd.Series, patient_info: Dict) -> Dict:
    """
    Get detailed information about a trial and matching criteria as a dictionary.
    
    Args:
        trial: Series containing trial information
        patient_info: Dictionary containing patient criteria
    
    Returns:
        Dict: A dictionary with trial details
    """
    return {
        "nct_id": trial['nct_id'],
        "title": trial['title'],
        "brief_summary": trial['brief_summary'] if pd.notna(trial['brief_summary']) else "Not provided",
        "detailed_description": trial['detailed_description'] if pd.notna(trial['detailed_description']) else "Not provided",
        "location": {
            "city": trial['city'],
            "state": trial['state'],
            "country": trial['country']
        },
        "patient_location": patient_info['location'],
        "sex": trial['sex'],
        "patient_sex": patient_info['sex'],
        "age_range": {
            "minimum_age": trial['minimum_age'],
            "maximum_age": trial['maximum_age']
        },
        "patient_age": patient_info['age'],
        "conditions": trial['conditions'],
        "patient_condition": patient_info['condition'],
        "eligibility_criteria": trial['eligibility_criteria'] if pd.notna(trial['eligibility_criteria']) else "Not provided",
        "additional_info": {
            "phase": trial['phase'],
            "status": trial['status'],
            "facility": trial['facility'],
            "accepts_healthy_volunteers": trial['healthy_volunteers']
        }
    }

# Example usage
if __name__ == "__main__":
    patient = {
        'condition': 'Lung cancer',
        'age': 45,
        'sex': 'FEMALE',
        'location': 'Boston Massachusetts'
    }

    matching_trials = find_trials_for_patient(patient)

    if not matching_trials.empty:
        print(f"\nFound {len(matching_trials)} matching trials.")
        
        # Convert all trials to JSON format
        trials_data = [get_trial_details(trial, patient) for _, trial in matching_trials.iterrows()]
        
        # Write to a JSON file
        with open("clinical_trials_results.json", "w") as f:
            json.dump(trials_data, f, indent=4)
        
        print("Trial details saved to clinical_trials_results.json")
    else:
        print("No matching trials found")