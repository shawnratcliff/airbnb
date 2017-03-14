from django.db.models import F, Q, Expression, ExpressionWrapper, FloatField
from django.db.models.aggregates import Count
from main.models import Neighborhood, Listing
from textacy import preprocess_text
from textacy.keyterms import most_discriminating_terms
from itertools import chain
import pandas as pd
import numpy as np
import pickle
from api.filters import random_sample
from os import path
from airbnb.settings import BASE_DIR

STOP_WORDS = pickle.load(open(path.join(BASE_DIR, 'pickles/stopwords.p'), 'rb'))
NEIGHBORHOOD_DATA = pickle.load(open(path.join(BASE_DIR, 'pickles/neighborhood_data.p'), 'rb'))
TRACT_DATA = pickle.load(open(path.join(BASE_DIR,'pickles/census_data.p'), 'rb'))['dataframe'] # df is inside an outer obj here

def _get_discriminating_terms(queryset, queryset_all):
    if queryset.count() == 0 or queryset.count() == queryset_all.count():
        return list()

    excluded = queryset_all.exclude(id__in=queryset.values_list('id', flat=True))

    # Take a random sample of each
    queryset = random_sample(queryset, 125)
    excluded = random_sample(excluded, 125)

    # Build input features
    all_docs = list()
    bools = list()
    for l in chain(queryset, excluded):
        # Generate a list of lists of tokens, excluding stop words
        all_docs.append(filter(
            lambda w: w not in STOP_WORDS and len(w) > 1,
            preprocess_text(
                l.description,
                lowercase=True,
                no_punct=True,
                no_numbers=True).split()
            )
        )
        bools.append(l in queryset)

    # Train model and output results
    return most_discriminating_terms(terms_lists=all_docs, bool_array_grp1=bools, top_n_terms=20)[0]

def _get_val_or_none(neighborhood_id, column):
    """
    Retrieves data item for single neighborhood, or None if NaN/null/etc.
    """
    df = NEIGHBORHOOD_DATA
    val = df[df['id'] == neighborhood_id].iloc[0][column]
    return val if not np.isnan(val) else None

def _neighborhood_weighted_avg(total_field, value_fields, neighborhood_id=None, make_percent=False):
    """
    Compute weighted average of statistic for neighborhood, by aggregating from tract-level data.
    If no neighborhood_id is supplied, aggregates all tracts in all neighborhoods.
    Note: returns None if total_field column summation is not > 0
    @param total_field: the applicable totals field (e.g., total population in tract)
    @param value_fields: a list of variable names to be added together to produce the value of interest. (For a single value, use a list of one element.)
    @param neighborhood_id: the neighborhood id to select
    @param make_percent: convert count-based target values to decimal fractions
    """
    df = TRACT_DATA
    if neighborhood_id:
        nhood = df[df['neighborhood_id'] == neighborhood_id] # select all rows with neighborhood_id
    else:
        nhood = df # select all rows
    weights = nhood[total_field] / nhood[total_field].sum()
    if not nhood[total_field].sum() > 0:
        return None

    # Produce a 'values' series by adding all the values in value_fields
    values = nhood[value_fields[0]].copy()
    for field in value_fields[1:]:
        values += nhood[field]

    if (make_percent):
        # Return the weighted sum of all target values, each divided by the applicable total
        return_val = ((values / nhood[total_field]) * weights).sum()
    else:
        # Return the weighted sum of all target values
        return_val = (values * weights).sum()
    if np.isnan(return_val):
        return None
    else:
        return return_val

def _compute_listing_stats(queryset):
    q = queryset.only('room_type', 'bed_type', 'description', 'neighborhood_id').prefetch_related('amenities')
    q_all = Listing.objects.all().only('room_type', 'bed_type', 'description').prefetch_related('amenities')
    q_count = q.count()
    q_all_count = q_all.count()
    # Calculate distributions for room types
    room_type_list = ['Entire home/apt', 'Private room', 'Shared room']

    q_room_type_dist = dict(q.values_list('room_type').distinct().annotate(
        percent=ExpressionWrapper(Count('room_type') * 1.0 / q_count, output_field=FloatField())))

    q_all_room_type_dist = dict(q_all.values_list('room_type').distinct().annotate(
        percent=ExpressionWrapper(Count('room_type') * 1.0 / q_all_count, output_field=FloatField())))

    # Calculate distributions for bed types
    bed_type_list = ['Couch', 'Airbed', 'Real Bed', 'Futon', 'Pull-out Sofa']

    q_bed_type_dist = dict(q.values_list('bed_type').distinct().annotate(
        percent=ExpressionWrapper(Count('bed_type') * 1.0 / q_count, output_field=FloatField())))

    q_all_bed_type_dist = dict(q_all.values_list('bed_type').distinct().annotate(
        percent=ExpressionWrapper(Count('bed_type') * 1.0 / q_all_count, output_field=FloatField())))

    # Calculate distributions for amenities
    amenities_list = [name for name
                      in q_all.values_list('amenities__name', flat=True).distinct().order_by('amenities__name')
                      if name is not None]

    q_amenities_dist = dict(q.values_list('amenities__name').distinct().order_by('amenities__name').annotate(
                            percent=ExpressionWrapper(Count('amenities__name') * 1.0 / q_count, output_field=FloatField())))

    q_all_amenities_dist = dict(q_all.values_list('amenities__name').distinct().order_by('amenities__name').annotate(
                            percent=ExpressionWrapper(Count('amenities__name') * 1.0 / q_all_count, output_field=FloatField())))

    return {
        'meta': 'Comp_avg is the average value for all listings in LA (for comparison graphs). '
                'Z score can be used to programmatically display messages such as, '
                '"about average for Los Angeles Airbnb listings" ( -0.5 to 0.5, eg.)',
        'count': {
            'meta': 'Value represents the # of listings that matched the filter criteria. '
                    'Comp_total is the total # of listings in LA. Ex: 4531 out of 26070 selected.',
            'value': q_count,
            'comp_total': q_all_count
        },
        'room_type_distribution': {
            'meta': 'Value is decimal proportion. Arrays are parallel.',
            'array_labels': room_type_list,
            'value': [
                q_room_type_dist[room_type] if room_type in q_room_type_dist else 0.0
                for room_type in room_type_list
            ],
            'comp_avg': [
                q_all_room_type_dist[room_type] if room_type in q_all_room_type_dist else 0.0
                for room_type in room_type_list
            ]
        },
        'bed_type_distribution': {
            'meta': "Value is decimal proportion. Arrays are parallel.",
            'array_labels': bed_type_list,
            'value': [
                q_bed_type_dist[bed_type] if bed_type in q_bed_type_dist else 0.0
                for bed_type in bed_type_list
            ],
            'comp_avg': [
                q_all_bed_type_dist[bed_type]
                for bed_type in bed_type_list
            ]
        },
        'amenities_distribution': {
            'meta': 'Value is decimal proportion. Arrays are parallel.',
            'array_labels': amenities_list,
            'value': [
                q_amenities_dist[amenity] if amenity in q_amenities_dist else 0.0
                for amenity in amenities_list
                if amenity is not None
            ],
            'comp_avg': [
                q_all_amenities_dist[amenity] if amenity in q_all_amenities_dist else 0.0
                for amenity in amenities_list
                if amenity is not None
            ]
        },
        'most_discriminating_terms': {
            'meta': 'This is a list of the words that, statistically, best differentiate the selected listings from '
                    'the rest. Words are ranked from most-to-least significant. I recommend using rank to '
                    'determine the weights used in the word cloud.',
            'value': _get_discriminating_terms(q, q_all)
        }
    }

def _compute_neighborhood_stats(neighborhood_id):
    df = NEIGHBORHOOD_DATA
    id = neighborhood_id
    household_income_totals = 'B19001_001E' # Total num. of respondents (effective population size) for income stats
    household_income_vars = [ # Each sublist is a set of census variables to combine into one histogram bin
        ['B19001_002E', 'B19001_003E', 'B19001_004E', 'B19001_005E'], # 0-24.9K
        ['B19001_006E', 'B19001_007E', 'B19001_008E', 'B19001_009E', 'B19001_010E'], # 25-49.9K
        ['B19001_011E', 'B19001_012E', 'B19001_013E'],  # 50-99.9K
        ['B19001_014E', 'B19001_015E', 'B19001_016E'],  # 100-199.9K
        ['B19001_017E'],  # 200K+
    ]
    age_totals = 'B01001_001E' # Total num. of respondents (effective population size) for age stats
    age_vars = [
        ['B01001_003E', 'B01001_004E', 'B01001_005E', 'B01001_006E', 'B01001_027E',
         'B01001_028E', 'B01001_029E', 'B01001_030E'], # 0-17
        ['B01001_007E', 'B01001_008E', 'B01001_009E', 'B01001_010E', 'B01001_011E', 'B01001_012E',
         'B01001_031E', 'B01001_032E', 'B01001_033E', 'B01001_034E', 'B01001_035E', 'B01001_036E'], # 18-34
        ['B01001_013E', 'B01001_014E', 'B01001_015E', 'B01001_037E', 'B01001_038E', 'B01001_039E'], # 35-49
        ['B01001_016E', 'B01001_017E', 'B01001_018E', 'B01001_019E', 'B01001_040E', 'B01001_041E',
         'B01001_042E', 'B01001_043E'], # 50-64
        ['B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E', 'B01001_025E',
         'B01001_044E', 'B01001_045E', 'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E'] # 65+
    ]
    neighborhood_stats = {
        'meta': 'Comp_avg is the average value for all neighborhoods in LA (for comparison graphs). '
                'Z score can be used to programmatically display messages such as, '
                '"about average for Los Angeles neighborhoods" ( -0.5 to 0.5, eg.)',
        'crime': {
            'crime_count': {
                'value': _get_val_or_none(id, 'crime_count'),
                'comp_avg': df['crime_count'].mean(),
                'z_score': _get_val_or_none(id, 'crime_count_z'),
            },
            'crimes_per_capita': {
                'value': _get_val_or_none(id, 'crimes_per_capita'),
                'comp_avg': df['crimes_per_capita'].mean(),
                'z_score': _get_val_or_none(id, 'crimes_per_capita_z'),
            }
        },
        'household_income': {
            'median': {
                'value': _get_val_or_none(id, 'median_household_income'),
                'comp_avg': df['median_household_income'].mean(),
                'z_score': _get_val_or_none(id, 'median_household_income_z')
            },
            'distribution': {
                'meta': 'Values are decimal proportions. Income bins: [0] 0-24999, '
                        '[1] 25000-49999, [2] 50000-99999, [3] 100000-199999, and [4] 200000+',
                'value': [
                    _neighborhood_weighted_avg(total_field=household_income_totals,
                                               neighborhood_id=neighborhood_id,
                                               value_fields=vars,
                                               make_percent=True)
                    for vars in household_income_vars
                ],
                'comp_avg': [
                    _neighborhood_weighted_avg(total_field=household_income_totals,
                                               neighborhood_id=None,
                                               value_fields=vars,
                                               make_percent=True)
                    for vars in household_income_vars
                ],
            },
        },
        'home_value': {
            'median': _get_val_or_none(id, 'median_home_value_owner_occupied'),
            'comp_avg': df['median_home_value_owner_occupied'].mean(),
            'z_score': _get_val_or_none(id, 'median_home_value_owner_occupied_z')
        },
        'gross_rent': {
            'median': _get_val_or_none(id, 'median_gross_rent'),
            'comp_avg': df['median_gross_rent'].mean(),
            'z_score': _get_val_or_none(id, 'median_gross_rent_z'),
        },
        'demographics': {
            'age': {
                'median': {
                    'value': _get_val_or_none(id, 'median_age'),
                    'comp_avg': df['median_age'].mean(),
                    'z_score': _get_val_or_none(id, 'median_age_z'),
                },
                'distribution': {
                    'meta': 'Values are decimal proportions. Age bins: [0] 0-17, [1] 18-34, '
                            '[2] 35-49, [3] 50-64, [4] 65+',
                    'value': [
                        _neighborhood_weighted_avg(total_field=age_totals,
                                                   neighborhood_id=neighborhood_id,
                                                   value_fields=vars,
                                                   make_percent=True)
                        for vars in age_vars
                    ],
                    'comp_avg': [
                        _neighborhood_weighted_avg(total_field=age_totals,
                                                   neighborhood_id=None,
                                                   value_fields=vars,
                                                   make_percent=True)
                        for vars in age_vars
                    ],
                }
            }
        }
    }
    return neighborhood_stats

def get_stats(queryset):
    """
    Get stats object for given queryset.
    :param queryset: The queryset to crunch stats on.
    :return: dict
    """
    if queryset.count() == 0:
        return {
            'error': 'There are no listings within the filter criteria.',
            'listings': {
                'count': {
                    'meta': 'Value represents the # of listings that matched the filter criteria. '
                            'Comp_total is the total # of listings in LA. Ex: 4531 out of 26070 selected.',
                    'value': 0,
                    'comp_total': 26070
                },
            }
        }

    stats = dict()

    # Add a neighborhood report, but only if this queryset spans 1 neighborhood.
    if queryset.values('neighborhood_id').distinct().count() == 1:
        stats['neighborhood'] = _compute_neighborhood_stats(queryset.first().neighborhood_id)

    # Add a listings report
    stats['listings'] = _compute_listing_stats(queryset)
    return stats
