from main.models import Neighborhood, Tract
import pandas as pd
import pickle
from airbnb.settings import BASE_DIR
from os import path
from django.contrib.gis.geos import Point
import geocoder
from treeinterpreter import treeinterpreter as ti
from collections import defaultdict

# Load dataframes
PRICE_MODEL = pickle.load(open(path.join(BASE_DIR, 'pickles/price_model_with_extras.p'), 'rb'))
TRACT_DATA = pickle.load(open(path.join(BASE_DIR, 'pickles/census_data_ml.p'), 'rb'))
MEDIAN_LISTING_DATA = pickle.load(open(path.join(BASE_DIR, 'pickles/median_listing_data_ml.p'), 'rb'))
LISTING_COLUMNS = pickle.load(open(path.join(BASE_DIR, 'pickles/listing_columns_ml.p'), 'rb'))

# Define groups of explanatory variables for contribution analysis
CATEGORIES = {
    'amenities': [c for c in LISTING_COLUMNS if c.startswith('amenity_')],
    'location': ['latitude', 'longitude', 'demographics', 'B01003_001E', 'percent_age_0_17', 'percent_age_18_34',
                 'percent_age_35_49', 'percent_age_50_64', 'percent_age_65_up', 'percent_bachelors_degree',
                 'percent_masters_degree', 'percent_associate_degree', 'percent_bachelors_or_higher',
                 'percent_doctoral_degree', 'percent_professional_degree', 'B19301_001E', 'B25001_001E', 'B25064_001E',
                 'percent_homes_vacant'],
    'miscellaneous': ['cancellation_policy', 'host_experience_days', 'minimum_nights'],
    'listing_type': ['room_type', 'property_type'],
    'bedrooms': ['bedrooms',],
    'availability': ['availability_365'],
    'maximum_occupancy': ['accommodates'],
    'bathrooms': ['bathrooms'],
}


# Drop irrelevant TRACT_DATA columns
drop_columns = [c for c in TRACT_DATA.columns
                if c not in ('tract_id', 'B25064_001E', 'B19301_001E', 'B01003_001E', 'B25001_001E')
                and not c.startswith('percent_')]
TRACT_DATA.drop(drop_columns, axis=1, inplace=True)

# Fill NaN values
percent_cols = [c for c in TRACT_DATA.columns if c.startswith('percent_')]
TRACT_DATA[percent_cols] = TRACT_DATA[percent_cols].fillna(value=0.0)

def resolve_address(address):
    # Geocode the address
    g = geocoder.google(address)
    if g.ok:
        point = Point(x=g.lng, y=g.lat, srid=4326)
    else:
        return {'error': 'Sorry, we couldn\'t understand that address. Please try again.'}

    # Check that the address is within a tract and neighborhood in our data
    try:
        tract = Tract.objects.filter(mpoly__contains=point).first()
        assert tract
        assert tract.neighborhood
    except AssertionError as e:
        return {'error': 'Sorry, this app is currently limited to Los Angeles County.'}

    # Check that census data isn't missing for this location
    try:
        has_null = TRACT_DATA[TRACT_DATA.tract_id == tract.id].isnull().any(axis=1).iloc[0]
        assert not has_null
    except AssertionError as e:
        return {'error': "Sorry, we can't process that address because of Census data suppression "
                         "at that location."}

    # Return the data
    return {'latitude': g.lat, 'longitude': g.lng, 'tract_id': tract.id}


def analyze_contributions(contributions):
    """
    Input: list of tuples, e.g. [('bedrooms', -49.5352),]
    Output: list of tuples, aggregated by category, sorted by absolute contrib value
    """
    # Aggregate by category
    aggregated = defaultdict(float) # Initialize each new key to 0.0 on first access attempt
    for variable, contribution in contributions:
        for category in CATEGORIES.keys():
            if variable in CATEGORIES[category]:
                aggregated[category] += contribution

    # Return as list of tuples ordered by absolute-value contribution
    return sorted(aggregated.items(), key=lambda x: -abs(x[1]))


def predict_price(listing_attrs):
    address_data = resolve_address(listing_attrs['address'])

    if 'error' in address_data:
        return address_data

    # Fill in the tract, lat & lon
    listing_attrs['tract_id'] = address_data['tract_id']
    listing_attrs['latitude'] = address_data['latitude']
    listing_attrs['longitude'] = address_data['longitude']

    # Create a dataframe and fill in missing values with medians
    df = pd.DataFrame(data=[listing_attrs], columns=LISTING_COLUMNS)
    df.fillna(MEDIAN_LISTING_DATA, inplace=True)

    # Merge in the applicable tract data for this location
    df = pd.merge(df, TRACT_DATA, on='tract_id', how='left')

    # Unpack estimator and labelencoders
    model = PRICE_MODEL['model']
    property_type_le = PRICE_MODEL['property_type_le']
    room_type_le = PRICE_MODEL['room_type_le']
    bed_type_le = PRICE_MODEL['bed_type_le']
    cancellation_policy_le = PRICE_MODEL['cancellation_policy_le']

    # Apply LabelEncoder transformations to categorical columns
    df['property_type'] = property_type_le.transform(df.property_type)
    df['room_type'] = room_type_le.transform(df.room_type)
    df['bed_type'] = bed_type_le.transform(df.bed_type)
    df['cancellation_policy'] = cancellation_policy_le.transform(df.cancellation_policy)

    # Drop extraneous columns
    df.drop(['block_group_id', 'estimated_revenue_per_month',
             'id', 'neighborhood_id', 'price', 'reviews_per_month',
             'tract_id', 'zipcode_id', 'review_count'], axis=1, inplace=True)

    # Predict
    X = df.iloc[0].values.reshape(1,-1)
    y_predicted, bias, contributions = ti.predict(model, X)

    # Unpack 1-element lists
    y_predicted = y_predicted[0]
    bias = bias[0]
    contributions = contributions[0]

    # Combine the float values with corresponding columns
    contributions = zip(df.columns, contributions)

    # Aggregate the contributions over categories
    contributions = analyze_contributions(contributions)

    return { 'prediction': y_predicted, 'bias': bias, 'contributions': contributions }



