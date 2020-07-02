import dash_bio
import pathlib
import pandas as pd

from utils import GffDataFrame

BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()


def circos_df_from_gff(gff_file):
    GFF = GffDataFrame(gff_file)
    df = GFF[['seq_id', 'start', 'end', 'score']]
    df = df.rename(columns={"seq_id": "block_id", 'score': "value"})
    df['start'] = df['start'] - 1
    df['block_id'] = df['block_id'].astype(str)
    return df


def circos_df_from_pimms(pimms_file):
    df = pd.read_csv(pimms_file)
    NIM_col = df.columns[-1]
    df = df[['seq_id', 'start', 'end', 'locus_tag', NIM_col]]
    df = df.rename(columns={"seq_id": "block_id", NIM_col: "value"})
    df['block_id'] = df['block_id'].astype(str)
    return df


def limit_genome(circos_df, start, end):
    return circos_df[((circos_df['start'] >= start) & (circos_df['end'] <= end))]


def drop_both_zero(circos_df1, circos_df2, *args):
    both_zero = ((circos_df1['value'] == 0.0) & (circos_df2['value'] == 0.0))
    circos_df1 = circos_df1[~both_zero]
    circos_df2 = circos_df2[~both_zero]
    result = [circos_df1, circos_df2]
    for arg in args:
        result.append(arg[~both_zero])
    return result


def load_data_test():
    pimms_data1 = circos_df_from_pimms(DATA_PATH.joinpath('UK15_redo_ucbold_UK15_Blood_Output_pimms2out_trim50_lev1_bwa_md3_mm_countinfo_tab.csv'))
    pimms_data2 = circos_df_from_pimms(DATA_PATH.joinpath('UK15_redo_ucbold_UK15_Media_Input_pimms2out_trim50_lev1_bwa_md3_mm_countinfo_tab.csv'))
    return pimms_data1, pimms_data2


def create_pimms_circos(inner_ring_df, outer_ring_df, hist_ring_df, start, end, hide_zeros=False, size=550):
    inner_ring_df['block_id'] = inner_ring_df['block_id'].astype(str)
    outer_ring_df['block_id'] = outer_ring_df['block_id'].astype(str)
    hist_ring_df['block_id'] = hist_ring_df['block_id'].astype(str)
    inner_ring_df = limit_genome(inner_ring_df, start, end)
    outer_ring_df = limit_genome(outer_ring_df, start, end)
    hist_ring_df = limit_genome(hist_ring_df, start, end)
    if hide_zeros:
        inner_ring_df, outer_ring_df, hist_ring_df = drop_both_zero(inner_ring_df, outer_ring_df, hist_ring_df)
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
                            #'tooltipContent': {'name': 'all'},
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
                            #'tooltipContent': {'name': 'all'},
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
