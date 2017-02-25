from django.db.models import F, Q, Expression, ExpressionWrapper, FloatField
from django.db.models.aggregates import Count
from main.models import Neighborhood, Listing
import textacy
from itertools import chain
import pickle
from api.filters import random_sample

stop_words = pickle.load(open('pickles/stopwords.p', 'rb'))

def get_discriminating_terms(queryset, queryset_all):
    if queryset.count() == 0 or queryset.count() == queryset_all.count():
        return list()

    excluded = queryset_all.exclude(id__in=queryset.values_list('id', flat=True))

    # Take a random sample of each
    queryset = random_sample(queryset, 250)
    excluded = random_sample(excluded, 100)

    # Build input features
    all_docs = list()
    bools = list()
    for l in chain(queryset, excluded):
        # Generate a list of lists of tokens, excluding stop words
        all_docs.append(filter(
            lambda w: w not in stop_words,
            textacy.preprocess_text(
                l.description,
                lowercase=True,
                no_punct=True,
                no_numbers=True).split()
            )
        )
        bools.append(l in queryset)

    # Train model and output results
    return textacy.keyterms.most_discriminating_terms(terms_lists=all_docs, bool_array_grp1=bools, top_n_terms=20)[0]

def get_stats(queryset):
    """
    Returns statistics object for queryset
    :param queryset: a Listing queryset
    :return: stats dict
    """
    q = queryset.only('room_type', 'bed_type', 'description', 'neighborhood_id').prefetch_related('amenities')
    q_all = Listing.objects.all().only('room_type', 'bed_type', 'description').prefetch_related('amenities')
    q_count = q.count()
    q_all_count = q_all.count()

    if q_count == 0:
        return {'error': 'There are no listings within the filter criteria.'}

    stats = dict()


    # Add a neighborhood report, but only if this queryset spans 1 neighborhood.
    if q.values('neighborhood_id').distinct().count() == 1:
        stats['neighborhood'] = {
            'meta': 'Comp_avg is the average value for all neighborhoods in LA (for comparison graphs). '
                    'Z score can be used to programmatically display messages such as, '
                    '"about average for Los Angeles neighborhoods" ( -0.5 to 0.5, eg.)',
        }

    # Add a listings report

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

    stats['listings'] = {
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
            'value': get_discriminating_terms(q, q_all)
        }
    }
    return stats
