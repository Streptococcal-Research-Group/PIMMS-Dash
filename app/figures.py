# Standard Library
import io
import base64

# Package imports
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_table
from dash_table.Format import Format, Scheme
import matplotlib
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

# Local imports
from settings import plotly_template

matplotlib.use('Agg')


def create_datatable(df):
    return dash_table.DataTable(
                id='main_table',
                columns=[{"name": i.replace("_", " "),
                          "id": i,
                          "selectable": True,
                          "format": Format(precision=2, scheme=Scheme.fixed)} for i in df.columns],
                data=df.to_dict('records'),
                merge_duplicate_headers=True,
                sort_mode="multi",
                column_selectable="multi",
                tooltip_data=[{'product': {'type': 'text', 'value': f'{r}'}} for r in df['product'].values],
                style_table={'overflowX': 'scroll', 'overflowY': 'auto', 'color': 'black'},
                style_as_list_view=True,
                style_header={'backgroundColor': 'white', 'fontWeight': 'bold'},

                style_cell={
                    'minWidth': '50px', 'width': '180px', 'maxWidth': '180px',
                    'whiteSpace': 'normal', 'padding': '5px', 'textAlign': 'left'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'product'},
                        'overflow': 'hidden',
                        'text-overflow': 'ellipsis',
                        'white-space': 'nowrap'}],
                style_data={
                    'lineHeight': '15px'
                },
                page_size=12,
                sort_action="native",
            )


def create_histogram(series_control, series_test, range_x=None, range_y=None, bin_size=None):
    # Create numpy xbins
    if bin_size == None:
        xbins = 'auto'
    else:
        xbins = np.arange(0, np.max([series_control.max(), series_test.max()])+bin_size, bin_size)

    # Build histogram first using numpy to be able to extract y range.
    np_hist_t = np.histogram(series_test.values, bins=xbins)
    np_hist_c = np.histogram(series_control.values, bins=np_hist_t[1])
    np_hist_info = {
        'test': {
            'nbins': len(np_hist_t[1]) - 1,
            'start': np_hist_t[1][0],
            'end': np_hist_t[1][-1],
            'max': np_hist_t[0].max(),
            'min': np_hist_t[0].min(),
            'size': np_hist_t[1][1]
        },
        'control': {
            'nbins': len(np_hist_c[1]) - 1,
            'start': np_hist_c[1][0],
            'end': np_hist_c[1][-1],
            'max': np_hist_c[0].max(),
            'min': np_hist_c[0].min(),
            'size': np_hist_c[1][1]
        },
    }
    range_max = np.max([np_hist_info['test']['max'], np_hist_info['control']['max']])
    range_min = np.min([np_hist_info['test']['min'], np_hist_info['control']['min']])

    # Replicate numpy histograms as plotly graph objects
    hist_t = go.Histogram(x=series_test,
                          xbins={'end': np_hist_info['test']['end'],
                                 'size': np_hist_info['test']['size'],
                                 'start': np_hist_info['test']['start']},
                          name='Test',
                          opacity=0.5,
                          marker={'line': {'width': 1}}
                          )
    hist_c = go.Histogram(x=series_control,
                          xbins={'end': np_hist_info['control']['end'],
                                 'size': np_hist_info['control']['size'],
                                 'start': np_hist_info['control']['start']},
                          name='Control',
                          opacity=0.5,
                          marker={'line': {'width': 1}}
                          )
    # Create figure
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0,
                        column_titles=['Sampled Results'],  # title of plot
                        x_title='NIM',  # xaxis label
                        y_title='Count',
                        )

    fig.add_trace(hist_c, row=1, col=1)
    fig.add_trace(hist_t, row=2, col=1)

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)

    fig.update_layout(template=plotly_template, legend=dict(x=0.9, y=1))

    # Manage range, reversing range for subplot 2
    if range_y:
        fig.update_layout(go.Layout(yaxis=dict(range=range_y)))
        fig.update_layout(go.Layout(yaxis2=dict(range=range_y[::-1])))
    else:
        fig.update_layout(go.Layout(yaxis=dict(range=[range_min, range_max])))
        fig.update_layout(go.Layout(yaxis2=dict(range=[range_max, range_min])))

    if range_x:
        fig.update_layout(go.Layout(xaxis=dict(range=range_x)))
        fig.update_layout(go.Layout(xaxis2=dict(range=range_x)))

    return fig


def create_histogram_type2(series_control, series_test, bin_size=None):
    if bin_size:
        xbins = {'start': 0, 'size': bin_size}
    else:
        xbins = None

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=series_control,
                               xbins=xbins,
                               name='Control',
                               opacity=0.5,
                               marker={'line': {'width': 1}}
                               ))
    fig.add_trace(go.Histogram(x=series_test,
                               xbins=xbins,
                               name='Test',
                               opacity=0.5,
                               marker={'line': {'width': 1}}
                               ))

    fig.update_layout(
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0,  # gap between bars of the same location coordinates
        xaxis_title="NIM",
        yaxis_title="Count",
        template=plotly_template,
        legend=dict(x=0.9, y=1),
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey', showline=False)

    return fig


def create_genome_scatter(gff_df):
    # If gff has score values - assume these are insert counts
    if gff_df.empty_score():
        insert_counts = gff_df.value_counts('start')
    else:
        insert_counts = gff_df['score']
    # Create figure, Use scattergl for large datasets.
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=insert_counts.index, y=insert_counts,
        name='mutations',
        mode='markers',
    ))
    # Set options common to all traces with fig.update_traces
    fig.update_traces(mode='markers', marker_line_width=2, marker_size=6)
    fig.update_layout(title='Insertions across the genome',
                      xaxis=dict(title_text="Position in the Genome"),
                      yaxis=dict(title_text="Number of Mutations / base"),
                      template=plotly_template,
                      )
    return fig


def create_venn(set_a, set_b):
    # get venn sets
    aB = len(set(set_b) - set(set_a))
    Ab = len(set(set_a) - set(set_b))
    AB = len(set(set_a) & set(set_b))

    # Create venn using matplotlib, encode to b64, pass to html.img
    plt.figure(linewidth=10, edgecolor="black", facecolor="black")
    mpl_fig = venn2(subsets=(Ab, aB, AB))

    # Style to plotly simple_white colours
    for ven_id, color in [('10', '#8FBBDA'), ('01', '#FFBF87'), ('11', '#B599C7')]:
        if mpl_fig.get_patch_by_id(ven_id) is not None:
            mpl_fig.get_patch_by_id(ven_id).set_color(color)
            mpl_fig.get_patch_by_id(ven_id).set_alpha(1.0)
            mpl_fig.get_patch_by_id(ven_id).set_edgecolor('black')

    # Convert to b64
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png')
    pic_IObytes.seek(0)
    encoded_image = base64.b64encode(pic_IObytes.read())
    img = 'data:image/png;base64,{}'.format(encoded_image.decode())
    # plotly_fig = mpl_to_plotly(mpl_fig) # Not working for venn
    plt.close()
    return img
