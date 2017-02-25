"""
Functions for processing of Airbnb filter arguments.
"""

from ast import literal_eval

from django.db.models import Q, ExpressionWrapper, FloatField
from django.db.models.aggregates import Count
from main.models import Neighborhood, Listing
import json

def get_filter_query(filters, geom_name='point'):
    """
    Returns a Q object encapsulating the filter criteria.
    """
    # Create base (empty) filter query
    query = Q()

    # Append (AND) region query, if provided
    if 'region' in filters.keys():
        region_filter = filters['region']
        kwargs = {region_filter['region_type'].lower(): region_filter['id']}
        query &= Q(**kwargs)

    # Append (AND) sequence of numerical range filters, if provided
    if 'numerical_range' in filters.keys():
        for range_filter in filters['numerical_range']:
            attr = range_filter['attribute_name'].lower()
            kwargs = dict()
            if 'min' in range_filter.keys() and range_filter['min']:
                kwargs['%s__gte' % attr] = range_filter['min']
            if 'max' in range_filter.keys() and range_filter['max']:
                kwargs['%s__lte' % attr] = range_filter['max']
            query &= Q(**kwargs)

    return query

def random_sample(queryset, n):
    """
    Returns a random sample of the queryset, up to the max sample size of n.
    (If n < N, N records will be returned.)
    """
    if queryset.model.__name__ == 'Listing':
        return queryset.order_by('random')[:n] # use pre-indexed random int field
    else:
        return queryset.order_by('?')[:n]



from collections import OrderedDict
sample_stats = OrderedDict({
    'neighborhood': {
        'meta': 'Comp_avg is the average value for all neighborhoods in LA (for comparison graphs). '
                'Z score can be used to programmatically display messages such as, '
                '"about average for Los Angeles neighborhoods" ( -0.5 to 0.5, eg.)',
        'crime': {
            'crime_count': {
                'value': 9631,
                'comp_avg': 4500,
                'z_score': 2.6332,
            },
            'crimes_per_capita': {
                'value': 0.0093,
                'comp_avg': 0.0023,
                'z_score': 1.915,
            }
        },
        'household_income': {
            'median': {
                'value': 48911.23,
                'comp_avg': 56321.12,
                'z_score': -0.52
            },
            'distribution': {
                'meta': 'Values are decimal proportions. Income bins: [0] 0-24999, '
                        '[1] 25000-49999, [2] 50000-99999, [3] 100000-199999, and [4] 200000+',
                'value': [0.2077, 0.1674, 0.3188, 0.1691, 0.0531],
                'comp_avg': [0.0867, 0.3678, 0.3017, 0.2273, 0.0165],
            }
        },
        'home_value': {
            'median': 344300,
            'comp_avg': 610400,
            'z_score': -1.75321
        },
        'gross_rent': {
            'median': 780,
            'comp_avg': 1431,
            'z_score': -1.52
        },
        'demographics': {
            'age': {
                'median': {
                    'value': 38.1,
                    'comp_avg': 39.3,
                    'z_score': -0.15
                },
                'distribution': {
                    'meta': 'Values are decimal proportions. Age bins: [0] 0-17, [1] 18-34, '
                            '[2] 35-49, [3] 50-64, [4] 65+',
                    'value': [0.1111, 0.1227, 0.1054, 0.1174, 0.036],
                    'comp_avg': [0.1027, 0.1111, 0.1174, 0.1054, 0.056]
                }
            }
        }
    },
    'listings': {
        'meta': 'Comp_avg is the average value for all listings in LA (for comparison graphs). '
                'Z score can be used to programmatically display messages such as, '
                '"about average for Los Angeles Airbnb listings" ( -0.5 to 0.5, eg.)',
        'count': {
            'meta': 'Value represents the # of listings that matched the filter criteria. '
                    'Comp_total is the total # of listings in LA. Ex: 4531 out of 26070 selected.',
            'value': 4531,
            'comp_total': 26070
        },
        'room_type_distribution': {
            'meta': 'Arrays indexed as: [0] Entire home/apt, [1] Private room, [2] Shared room. ',
            'value': [0.2962, 0.5738, 0.1299],
            'comp_avg': [0.5822, 0.3680, 0.04975]

        },
        'bed_type_distribution': {
            'meta': "Arrays indexed as: [0] 'Couch', [1] 'Airbed', [2] 'Real Bed', [3] 'Futon', [4] 'Pull-out Sofa'.",
            'value': [0.2207, 0.4414, 0.1299, 0.0754, 0.1324],
            'comp_avg': [0.4414, 0.2207, 0.1324, 0.0754, 0.1299]
        },
        'amenities_distribution': {
            'meta': 'Value is decimal proportion. Arrays are parallel.',
            'array_labels': ['24-Hour Check-in', 'Air Conditioning', 'Breakfast', 'Buzzer/Wireless Intercom',
                             'Cable TV', 'Carbon Monoxide Detector', 'Cat(s)', 'Dog(s)', 'Doorman', 'Dryer',
                             'Elevator in Building', 'Essentials', 'Family/Kid Friendly', 'Fire Extinguisher',
                             'First Aid Kit', 'Free Parking on Premises', 'Gym', 'Hair Dryer', 'Hangers', 'Heating',
                             'Hot Tub', 'Indoor Fireplace', 'Internet', 'Iron', 'Kitchen', 'Laptop Friendly Workspace',
                             'Lock on Bedroom Door', 'Other pet(s)', 'Pets Allowed', 'Pets live on this property',
                             'Pool', 'Safety Card', 'Shampoo', 'Smoke Detector', 'Smoking Allowed',
                             'Suitable for Events', 'TV', 'Washer', 'Washer / Dryer', 'Wheelchair Accessible',
                             'Wireless Internet'],
            'value': [0.8116, 0.9259, 0.8617, 0.628, 0.5255, 0.2188, 0.2526, 0.1729, 0.6939, 0.1765, 0.9388,
                      0.84, 0.3342, 0.3822, 0.864, 0.0214, 0.7043, 0.4621, 0.1435, 0.4714, 0.4756, 0.0298, 0.1563,
                      0.2787, 0.8971, 0.5273, 0.6447, 0.7122, 0.6525, 0.7543, 0.8462, 0.0403, 0.9731, 0.6605, 0.1958,
                      0.4896, 0.7851, 0.3904, 0.1534, 0.8022, 0.4699],
            'comp_avg': [0.3725, 0.2778, 0.6775, 0.6205, 0.2877, 0.9765, 0.3512, 0.654, 0.6171, 0.6563, 0.2945,
                         0.9682, 0.3401, 0.3215, 0.1453, 0.0145, 0.7755, 0.8985, 0.818, 0.2217, 0.3878, 0.732,
                         0.2696, 0.9668, 0.9535, 0.7359, 0.925, 0.5229, 0.0151, 0.9735, 0.7827, 0.9592, 0.3676,
                         0.6775, 0.5297, 0.8154, 0.245, 0.6646, 0.6694, 0.9525, 0.9047],
        },
        'most_discriminating_terms': {
            'meta': 'This is a list of the words that, statistically, best differentiate the selected listings from '
                    'the rest. Words are ranked from most-to-least significant. I recommend using rank to '
                    'determine the weights used in the word cloud.',
            'value': ['santa', 'monica', 'pier', 'promenade', 'beach', 'st', 'ocean', 'montana', 'bedrooms', '3rd',
                       'family', 'main', 'third', 'street', 'spectacular', 'vacation', 'avenue', 'essentials',
                       'bathrooms', 'stocked']
        }
    }
})