from main.models import Neighborhood, Tract
import pandas as pd
import pickle
from airbnb.settings import BASE_DIR
from os import path
from django.contrib.gis.geos import Point
import geocoder

# Load dataframes
PRICE_MODEL = pickle.load(open(path.join(BASE_DIR, 'pickles/price_model_with_extras.p'), 'rb'))
TRACT_DATA = pickle.load(open(path.join(BASE_DIR, 'pickles/census_data_ml.p'), 'rb'))
MEDIAN_LISTING_DATA = pickle.load(open(path.join(BASE_DIR, 'pickles/median_listing_data_ml.p'), 'rb'))
LISTING_COLUMNS = pickle.load(open(path.join(BASE_DIR, 'pickles/listing_columns_ml.p'), 'rb'))

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
        return {'error': 'The address could not be geocoded.'}

    # Check that the address is within a tract and neighborhood in our data
    try:
        tract = Tract.objects.filter(mpoly__contains=point).first()
        assert tract
        assert tract.neighborhood
    except AssertionError as e:
        return {'error': 'This app is currently limited to Los Angeles County. Please try another address.'}

    # Return the data
    return {'latitude': g.lat, 'longitude': g.lng, 'tract_id': tract.id}


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

    # Apply LabelEncoder transformations
    df['property_type'] = property_type_le.transform(df.property_type)
    df['room_type'] = room_type_le.transform(df.room_type)
    df['bed_type'] = bed_type_le.transform(df.bed_type)

    # Drop extraneous columns
    df.drop(['block_group_id', 'estimated_revenue_per_month',
             'id', 'neighborhood_id', 'price', 'reviews_per_month',
             'tract_id', 'zipcode_id'], axis=1, inplace=True)

    # Predict
    X = df.iloc[0].values.reshape(1,-1)
    y_predicted = model.predict(X)[0]

    return { 'predicted_price': y_predicted }