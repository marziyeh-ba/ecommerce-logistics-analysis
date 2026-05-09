"""
utils.py
--------
Helper functions used across the analysis notebook.
Keeping these here avoids repetition in the notebook
and makes the code easier to maintain.

Author: Marziyeh Eslamparasti
"""

import pandas as pd
import numpy as np


def calculate_delivery_delay(df, actual_col, estimated_col):
    """
    Calculate delivery delay in days.
    Negative = arrived early, Zero = on time, Positive = late.

    Parameters
    ----------
    df : pd.DataFrame
    actual_col : str    — column name for actual delivery date
    estimated_col : str — column name for estimated delivery date

    Returns
    -------
    pd.Series — delay in days
    """
    return (pd.to_datetime(df[actual_col]) - pd.to_datetime(df[estimated_col])).dt.days


def classify_delay(delay_days):
    """
    Classify a delivery delay into a human-readable bucket.
    Used for the satisfaction breakpoint analysis.

    Parameters
    ----------
    delay_days : int or float

    Returns
    -------
    str — delay category label
    """
    if delay_days < -7:
        return '1. Early 7+ days'
    elif delay_days < 0:
        return '2. Early 1-7 days'
    elif delay_days == 0:
        return '3. On Time'
    elif delay_days <= 3:
        return '4. Late 1-3 days'
    elif delay_days <= 7:
        return '5. Late 4-7 days'
    elif delay_days <= 14:
        return '6. Late 8-14 days'
    else:
        return '7. Late 14+ days'


def compute_rfm(orders_df, reference_date, customer_col='customer_id',
                date_col='order_date', value_col='order_value',
                order_col='order_id'):
    """
    Compute RFM (Recency, Frequency, Monetary) scores for each customer.

    Parameters
    ----------
    orders_df      : pd.DataFrame — order-level data
    reference_date : str or datetime — date to calculate recency from
    customer_col   : str — customer ID column
    date_col       : str — order date column
    value_col      : str — order value column
    order_col      : str — order ID column

    Returns
    -------
    pd.DataFrame — one row per customer with R, F, M scores
    """
    ref = pd.to_datetime(reference_date)
    orders_df = orders_df.copy()
    orders_df[date_col] = pd.to_datetime(orders_df[date_col])

    rfm = orders_df.groupby(customer_col).agg(
        recency   = (date_col,  lambda x: (ref - x.max()).days),
        frequency = (order_col, 'count'),
        monetary  = (value_col, 'sum')
    ).reset_index()

    rfm['R_score'] = pd.qcut(rfm['recency'],  5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5,
                              labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'),  5,
                              labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['RFM_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

    return rfm


def label_rfm_segment(row):
    """
    Assign a business segment label based on RFM scores.
    Called row-by-row using df.apply().

    Parameters
    ----------
    row : pd.Series — one row of the RFM dataframe

    Returns
    -------
    str — segment label
    """
    if row['R_score'] >= 4 and row['F_score'] >= 4 and row['M_score'] >= 4:
        return 'Champion'
    elif row['R_score'] >= 3 and row['F_score'] >= 3:
        return 'Loyal'
    elif row['R_score'] >= 4 and row['F_score'] <= 2:
        return 'New Customer'
    elif row['R_score'] <= 2 and row['F_score'] >= 3:
        return 'At Risk'
    elif row['R_score'] <= 2 and row['F_score'] <= 2:
        return 'Lost'
    else:
        return 'Potential'


def summarise_performance(df, group_col, metrics=None):
    """
    Generic helper to summarise delivery and satisfaction performance
    by any grouping column (category, state, month, etc.).

    Parameters
    ----------
    df         : pd.DataFrame — master olist dataframe
    group_col  : str — column to group by
    metrics    : list or None — which metrics to include

    Returns
    -------
    pd.DataFrame — grouped summary sorted by on_time_rate descending
    """
    if metrics is None:
        metrics = ['on_time', 'delivery_delay_days', 'review_score',
                   'total_revenue', 'order_id']

    agg_dict = {}
    if 'on_time' in metrics:
        agg_dict['on_time_rate']    = ('on_time',             'mean')
    if 'delivery_delay_days' in metrics:
        agg_dict['avg_delay']       = ('delivery_delay_days', 'mean')
    if 'review_score' in metrics:
        agg_dict['avg_review']      = ('review_score',        'mean')
    if 'total_revenue' in metrics:
        agg_dict['total_revenue']   = ('total_revenue',       'sum')
    if 'order_id' in metrics:
        agg_dict['order_count']     = ('order_id',            'count')

    result = df.groupby(group_col).agg(**agg_dict).reset_index()

    if 'on_time_rate' in result.columns:
        result['on_time_rate'] = (result['on_time_rate'] * 100).round(1)
    if 'avg_delay' in result.columns:
        result['avg_delay']    = result['avg_delay'].round(2)
    if 'avg_review' in result.columns:
        result['avg_review']   = result['avg_review'].round(2)

    sort_col = 'on_time_rate' if 'on_time_rate' in result.columns else result.columns[1]
    return result.sort_values(sort_col, ascending=False)
