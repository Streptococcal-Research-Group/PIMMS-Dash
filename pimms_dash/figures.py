# Standard library
import base64
import io

# Package imports
import numpy as np
import matplotlib.pyplot as plt
import dash_table
import plotly.graph_objects as go
from matplotlib_venn import venn2
from dash_table.Format import Format, Scheme
from plotly.subplots import make_subplots

# Local imports
from app import plotly_template


def main_datatable(df, id, **kwargs):
    """
    Use dash_table package to create a datatable component from pandas dataframe.
    Define default table args here, can be updated with kwargs.
    """
    default_args = dict(
        id=id,
        columns=[{"name": i.replace("_", " "),
                  "id": i,
                  "selectable": True,
                  "format": Format(precision=2, scheme=Scheme.fixed)} for i in df.columns],
        data=df.to_dict('records'),
        tooltip_data=[{'product': {'type': 'text', 'value': f'{r}'}} for r in df['product'].values],
        style_table={'overflowX': 'scroll', 'overflowY': 'auto', 'color': 'black'},
        style_header={'fontWeight': 'bold', 'backgroundColor': 'white','fontSize': 14},
        style_cell={
            'minWidth': '2vw', 'width': '4vw', 'maxWidth': '10vw',
            'whiteSpace': 'normal', 'textAlign': 'left',
            'font-family': 'sans-serif',
            'fontSize': 12
        },
        style_cell_conditional=[
            {'if': {'column_id': 'product'},
             'overflow': 'hidden',
             'text-overflow': 'ellipsis',
             'white-space': 'nowrap'}],
        page_size=15,
        sort_action="native",
    )
    default_args.update(kwargs)
    return dash_table.DataTable(**default_args)


def histogram(series_control, series_test, range_x=None, range_y=None, bin_size=None):
    """
    Create plotly figure containing two histogram subplots. One above the other with the lower flipped in the y axis.
    In order to provide interactivity linked to both plots (always display the same axis range), this function takes
    advantage of the numpy histogram function which provides the max hist bar y value (plotly does not), this is then
    used to limit the graph axes.
    :param series_control: pandas series control values
    :param series_test: pandas series test values
    :param range_x: x axis limit list [min, max]
    :param range_y: y axis limit list [min, max]
    :param bin_size:
    :return: plotly fig
    """
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
    # Get histogram max and min y values
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
    # Create sub plot figure
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0,
                        column_titles=['Sampled Results'],  # title of plot
                        x_title='NIM',  # xaxis label
                        y_title='Count',
                        )
    fig.add_trace(hist_c, row=1, col=1)
    fig.add_trace(hist_t, row=2, col=1)

    # update styling
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


def histogram_type2(series_control, series_test, bin_size=None):
    """
    Create a multi-bar histogram with plotly
    :param series_control: pandas series control values
    :param series_test: pandas series test values
    :param bin_size:
    :return:
    """
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


def genome_scatter(gff_df):
    """
    Create a scatter plot of genome insertions from a Gff dataframe object.
    :param gff_df: GffDataFrame object
    :return: plotly fig
    """
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
    fig.update_traces(mode='markers', marker_line_width=1, marker_size=4)
    fig.update_layout(title='Insertions across the genome',
                      xaxis=dict(title_text="Position in the Genome"),
                      yaxis=dict(title_text="Number of Mutations / base"),
                      template=plotly_template,
                      )
    return fig


def venn_diagram(set_a, set_b, backgroundcolor='white'):
    """
    Creates a venn diagram given two sets. As plotly venn diagrams are limited, uses matplotlib_venn package.
    The resulting matplotlib figure currently can not be directly converted to a plotly figure. As a work around the
    figure is encoded to a base64 string which can be read as an image by dash Img component.
    :param set_a:
    :param set_b:
    :return: base64 str encoding of plot.
    """
    # get venn sets
    aB = len(set(set_b) - set(set_a))
    Ab = len(set(set_a) - set(set_b))
    AB = len(set(set_a) & set(set_b))

    # Create venn using matplotlib, encode to b64, pass to html.img
    plt.figure(linewidth=10, edgecolor=backgroundcolor, facecolor=backgroundcolor)
    mpl_fig = venn2(subsets=(Ab, aB, AB))

    # Style to plotly simple_white colours
    for ven_id, color in [('10', '#8FBBDA'), ('01', '#FFBF87'), ('11', '#B599C7')]:
        if mpl_fig.get_patch_by_id(ven_id) is not None:
            mpl_fig.get_patch_by_id(ven_id).set_color(color)
            mpl_fig.get_patch_by_id(ven_id).set_alpha(1.0)
            mpl_fig.get_patch_by_id(ven_id).set_edgecolor('black')

    # Convert to b64
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png', facecolor=backgroundcolor, edgecolor=backgroundcolor)
    pic_IObytes.seek(0)
    encoded_image = base64.b64encode(pic_IObytes.read())
    img = 'data:image/png;base64,{}'.format(encoded_image.decode())
    # plotly_fig = mpl_to_plotly(mpl_fig) # Not working for venn
    plt.close()
    return img
