"""
Functions for processing of Airbnb filter arguments.
"""

from ast import literal_eval
from django.db.models import Q

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