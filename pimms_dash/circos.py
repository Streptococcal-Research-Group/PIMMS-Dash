import dash_bio
import pandas as pd

from utils import GffDataFrame


def circos_df_from_gff(gff_file):
    """ Convert gff file to a Circos compatible dataframe"""
    # Load gff
    GFF = GffDataFrame(gff_file)
    # Select relevant columns
    df = GFF[['seq_id', 'start', 'end', 'score']]
    # Rename columns to circos appropriate columns names
    df = df.rename(columns={"seq_id": "block_id", 'score': "value"})
    # To correctly plot gff where start position == end position, minus 1 from start.
    df['start'] = df['start'] - 1
    # Ensure block_id is correct type
    df['block_id'] = df['block_id'].astype(str)
    return df


def circos_df_from_pimms(pimms_file):
    """ Convert pimms csv file to a Circos compatible dataframe"""
    # Load gff
    df = pd.read_csv(pimms_file)
    # Extract name of NIM column, assuming last named col in pimms file
    NIM_col = df.columns[-1]
    # Select relevant columns
    df = df[['seq_id', 'start', 'end', 'locus_tag', NIM_col]]
    # Rename columns to circos appropriate columns names
    df = df.rename(columns={"seq_id": "block_id", NIM_col: "value"})
    # Ensure block_id is correct type
    df['block_id'] = df['block_id'].astype(str)
    return df


def limit_genome(circos_df, start, end):
    """ limit circos dataframe to inserts within range [start, end]"""
    return circos_df[((circos_df['start'] >= start) & (circos_df['end'] <= end))]


def drop_both_zero(circos_df1, circos_df2, *args):
    """ Remove any rows from circos dataframes where both values are equal to zero. Allows additional circos df
    arguments that will also be reduced."""
    both_zero = ((circos_df1['value'] == 0.0) & (circos_df2['value'] == 0.0))
    circos_df1 = circos_df1[~both_zero]
    circos_df2 = circos_df2[~both_zero]
    result = [circos_df1, circos_df2]
    for arg in args:
        result.append(arg[~both_zero])
    return result


def pimms_circos(inner_ring_df, outer_ring_df, hist_ring_df, start, end, hide_zeros=False, size=550):
    """
    Create circos plot using dash_bio.Circos functionality. Generates figure with two circos rings and an additional
    histogram outer ring.
    :param inner_ring_df: Dataframe containing relevant circos columns
    :param outer_ring_df: Dataframe containing relevant circos columns
    :param hist_ring_df: Dataframe containing relevant circos columns
    :param start: int - genome position
    :param end: int - genome position
    :param hide_zeros: bool - option to hide sections of genome where inner and outer rings values both equal zero.
    :param size: figure size
    :return:
    """
    # Ensure correct types
    inner_ring_df['block_id'] = inner_ring_df['block_id'].astype(str)
    outer_ring_df['block_id'] = outer_ring_df['block_id'].astype(str)
    hist_ring_df['block_id'] = hist_ring_df['block_id'].astype(str)
    # Limit genome to start and position
    inner_ring_df = limit_genome(inner_ring_df, start, end)
    outer_ring_df = limit_genome(outer_ring_df, start, end)
    hist_ring_df = limit_genome(hist_ring_df, start, end)
    # sections of genome where inner and outer rings values both equal zero
    if hide_zeros:
        inner_ring_df, outer_ring_df, hist_ring_df = drop_both_zero(inner_ring_df, outer_ring_df, hist_ring_df)
    # Calculate genome length
    genome_length = inner_ring_df['start'].max() - inner_ring_df['start'].min()
    return dash_bio.Circos(
                id='main-circos',
                selectEvent={'0': 'hover', '1': 'hover'},
                layout=[{'len': genome_length, 'color': 'white', 'label': 'Test', 'id': '1'}],
                config={
                    'innerRadius':  0,
                    'outerRadius': 5,
                    'ticks': {'display': False},
                    'labels': {
                        'position': 'center',
                        'display': False,
                        'size': 14,
                        'color': 'Black',
                        'radialOffset': 1,
                    },
                },
                tracks=[
                    {
                        'type': 'HEATMAP',
                        'data': inner_ring_df.to_dict('records'),
                        'config': {
                            'innerRadius': (size / 2)*0.29,
                            'outerRadius': (size / 2)*0.49,
                            'logScale': True,
                            'color': 'Blues',
                            'tooltipContent': {'name': 'value'},
                        },
                    },
                    {
                        'type': 'HEATMAP',
                        'data': outer_ring_df.to_dict('records'),
                        'config': {
                            'innerRadius': (size / 2)*0.59,
                            'outerRadius': (size / 2)*0.79,
                            'logScale': True,
                            'color': 'Greens',
                            'tooltipContent': {'name': 'value'},
                        },
                    },
                    {
                        'type': 'HISTOGRAM',
                        'data': hist_ring_df.to_dict('records'),
                        'config': {
                            'innerRadius': (size / 2)*0.8,
                            'outerRadius': (size / 2)*1,
                            'color': 'Blues',
                            'logScale': False,
                            'tooltipContent': {'name': 'value'},
                        },
                    },
                ],
                size=size,
            )
