# Standard library
import base64
import io

# Package imports
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import dash_table
import plotly.graph_objects as go
from matplotlib_venn import venn2
from dash_table.Format import Format, Scheme
from plotly.subplots import make_subplots
from matplotlib.colors import ColorConverter

# Local imports
from app import plotly_template
from utils import scale_lightness


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
    if 'product' in df.columns:
        default_args["tooltip_data"] = [{'product': {'type': 'text', 'value': f'{r}'}} for r in df['product'].values]

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
        inserts_data = gff_df.value_counts('start').reset_index().rename(columns={"index": "position", "start": "count"})
    else:
        inserts_data = gff_df[['start', 'score']].rename(columns={"start": "position", "score": "count"})
    # Create figure, Use scattergl for large datasets.
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=inserts_data["position"], y=inserts_data["count"],
        name='mutations',
        mode='markers',
    ))
    # Set options common to all traces with fig.update_traces
    fig.update_traces(mode='markers', marker_line_width=1, marker_size=4)
    fig.update_layout(title='Insertions across the genome',
                      xaxis=dict(
                          title_text="Position in the Genome",
                          rangeslider=dict(
                              visible=True,
                              bgcolor="#eee",
                              thickness=0.05,
                          ),
                      ),
                      yaxis=dict(title_text="Number of Mutations / base"),
                      template=plotly_template,
                      )
    return fig


def genome_comparison_scatter(gff_df_control, gff_df_test, control_title, test_title):
    """
    Create a subplot of two scatter plots of genome insertions from Gff dataframe objects.
    :param gff_df_control: GffDataFrame object
    :param gff_df_test: GffDataFrame object
    :return: plotly fig
    """
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.15,
                        subplot_titles=[control_title, test_title],
                        y_title="Number of Mutations / base")
    for row, gff_df in enumerate([gff_df_control, gff_df_test]):
        # If gff has score values - assume these are insert counts
        if gff_df.empty_score():
            inserts_data = gff_df.value_counts('start').reset_index().rename(
                columns={"index": "position", "start": "count"})
        else:
            inserts_data = gff_df[['start', 'score']].rename(columns={"start": "position", "score": "count"})
        # Add trace
        fig.add_trace(
            go.Scattergl(
                x=inserts_data["position"], y=inserts_data["count"],
                name='mutations',
                mode='markers',
            ),
            row=row + 1,
            col=1
        )
    # Set options common to all traces with fig.update_traces
    fig.update_traces(mode='markers', marker_line_width=1, marker_size=4)
    fig.update_layout(
        showlegend=False, title_x=0.5, template=plotly_template,
        xaxis2=dict(
            title="Position in the Genome",
            rangeslider=dict(
                visible=True, bgcolor="#eee", thickness=0.05
            ),
        )
    )
    return fig


def venn_diagram(set_a, set_b, backgroundcolor='white', set_labels=('Group A', 'Group B'), color_list=None):
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
    mpl_fig = venn2(subsets=(Ab, aB, AB), set_labels=set_labels)

    if color_list and len(color_list) == 3:
        colors = zip(["10", "01", "11"], color_list)
    else:
        colors = [('10', '#8FBBDA'), ('01', '#FFBF87'), ('11', '#B599C7')]

    # Style to plotly simple_white colours
    for ven_id, color in colors:
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



def mpl_needleplot(mutation_data: pd.DataFrame, gene_name: str, gene_start: int, gene_end: int, log=True,
                   color_dict=None, gene_label_width=15, stem_width=1, marker_size=6):
    """
    Create a needleplot of gene mutations using matplotlib stem.
    :param mutation_data: dataframe holding mutation information
    :param gene_name:
    :param gene_start: coord of start
    :param gene_end: coord of end
    :param log: Bool

    Example mutation_data  input dataframe:
    df = pd.DataFrame(
        {
            "position": list(np.random.randint(low=1309354, high=1312965, size=10)),
            "group": list(np.random.choice(["test", "control"], 10)),
            "count": list(np.random.poisson(3, 10))
        }
    )
    """
    def myLogFormat(y, pos):
        """ Utility function to format log ticks - hides ticks <1"""
        if y < 1:
            return ""
        # Find the number of decimal places required
        decimalplaces = int(np.maximum(-np.log10(y), 0))  # =0 for numbers >=1
        # Insert that number into a format string
        formatstring = '{{:.{:1d}f}}'.format(decimalplaces)
        # Return the formatted tick label
        return formatstring.format(y)

    # List to hold legend objects
    legend_elements = []
    # Loop through groups
    for i, group in enumerate(mutation_data["group"].unique()):
        # Get only the rows belonging to group
        subset_df = mutation_data[mutation_data["group"] == group]
        # Create matplotlib stem plot, baseline is white to hide, colour changes through loop
        markerline, stemlines, baseline = plt.stem(subset_df["position"], subset_df['count'], f"C{i}", basefmt="w",
                                                   markerfmt=f"C{i}o", label=group, use_line_collection=True)
        # Choose marker color
        if color_dict and group.lower() in color_dict:
            clr = color_dict[group.lower()]
        else:
            clr = f"C{i}"

        plt.setp(markerline, 'color', clr)
        plt.setp(stemlines, 'color', clr)

        # Set the line width, markersize and baseline width. Baseline to 0 will hide.
        plt.setp(stemlines, "linewidth", stem_width)
        plt.setp(markerline, markersize=marker_size)
        plt.setp(baseline, "linewidth", 0)

        # Create the legend icon using line2D object and append to legend elements list
        legend_elements.append(
            Line2D([0], [0], marker='o', color="w", label=group, markerfacecolor=clr, markersize=10))

    if log is True:
        plt.yscale("log")
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(myLogFormat))
        #plt.gca().yaxis.set_minor_formatter(ticker.FuncFormatter(myLogFormat))

    # Set genelabel y position. Set >0 to work with log yscale.
    label_y = 0.8

    # Use another call to stem to create the gene rectangle with its baseline.
    markerline, stemlines, baseline = plt.stem([gene_start, gene_end], [0, 0], "w", markerfmt="r", basefmt="r-",
                                               use_line_collection=True, bottom=label_y)
    # Define the height of the gene label
    plt.setp(baseline, "linewidth", gene_label_width)
    # Add a patch to the legend to label gene
    legend_elements.append(Patch(facecolor='r', edgecolor='r', label=gene_name))

    plt.text(gene_start + (gene_end - gene_start) / 2, label_y, gene_name, horizontalalignment='center',
             verticalalignment='center')

    # Create custom legend with legend elements
    plt.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc='lower right', ncol=3)
    # General plot formating
    plt.ylabel("Mutations", fontsize=14)
    plt.xlabel("Position", fontsize=14)

    # At this point a call to plt.show would display needleplot
    # For the purposes of the dash board we covert to img b64 string
    # Convert to b64
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png', facecolor="w", edgecolor="w")
    pic_IObytes.seek(0)
    encoded_image = base64.b64encode(pic_IObytes.read())
    img = 'data:image/png;base64,{}'.format(encoded_image.decode())
    # plotly_fig = mpl_to_plotly(mpl_fig) # Not working for venn
    plt.close()
    return img

def NIM_comparison_bar(series_control, series_test, start_positions, end_positions, get_trace=False):
    """ Create plotly bar chart to compare NIM/NRM scores between conditions
    May have poor performance for large datasets"""
    # Use start and end positions to define bar positions
    bar_centers = ((end_positions - start_positions) / 2) + start_positions
    bar_widths = end_positions - start_positions

    # Create fig object
    fig = go.Figure()
    t1 = go.Bar(
        x=bar_centers,
        y=series_test,
        width=bar_widths,
        name='Test Condition',
        opacity=0.75
    )
    t2 = go.Bar(
        x=bar_centers,
        y=series_control,
        width=bar_widths,
        name='Control Condition',
        opacity=0.75
    )
    if get_trace:
        return [t1, t2]
    else:
        fig.add_trace(t1)
        fig.add_trace(t2)

        # Log y axis and y title
        fig.update_yaxes(type="log",
                         title="NIM Score")

        # add slider to x axis
        full_range = end_positions.max() - start_positions.min()
        initial_slider_width = full_range * 0.2
        fig.update_xaxes(rangeslider=dict(visible=True),
                         range=[full_range / 2 - initial_slider_width / 2, full_range / 2 + initial_slider_width / 2])

        # General layout
        fig.update_layout(template=plotly_template,
                          title='NIM Score Across Genome',
                          legend=dict(
                              x=0,
                              y=1.0,
                          ))
        return fig

def NIM_comparison_bar_gl(series_control, series_test, start_positions, end_positions, locus_tags, test_label, control_label, get_trace=False):
    """
    To address performance issues in standard plotly bar with large datasets. Hack scattergl (better performance)
    to produce a bar-like chart using fill.
    """
    # Create scatter points to build bar.
    x_points = [item for x in zip(start_positions, end_positions) for item in [x[0], x[0], x[1], x[1]]]
    y_points_test = [item for x in series_test.to_list() for item in [0, x, x, 0]]
    y_points_control = [item for x in series_control.to_list() for item in [0, -x, -x, 0]]
    locus_labels = [item for x in locus_tags.to_list() for item in ["", x, x, ""]]
    # Create figure
    fig = go.Figure()
    t1 = go.Scattergl(x=x_points, y=y_points_test, fill='tozeroy', name=test_label,
                      hovertemplate='<b>Score</b>: %{text}' +
                                    '<br><b>Position</b>: %{x}' +
                                    '<br><b>Locus Tag</b>: %{customdata}<br>',
                      text=[str(abs(y)) for y in y_points_test],
                      customdata=locus_labels
                      )
    t2 = go.Scattergl(x=x_points, y=y_points_control, fill='tozeroy', name=control_label,
                      hovertemplate='<b>Score</b>: %{text}' +
                                    '<br><b>Position</b>: %{x}' +
                                    '<br><b>Locus Tag</b>: %{customdata}<br>',
                      text=[str(abs(y)) for y in y_points_control],
                      customdata=locus_labels
                      )

    if get_trace:
        return [t1, t2]
    else:
        fig.add_trace(t1)  # fill to trace0 y
        fig.add_trace(t2)  # fill to trace0 y

        fig.update_yaxes(title="Score")
        # General layout
        fig.update_layout(template=plotly_template,
                          title='Score Across Genome',
                          legend=dict(
                              x=0,
                              y=1.0,
                          ))
        return fig

def NIM_comparison_heatmap(series_control, series_test,  start_positions, end_positions, locus_tags, test_label, control_label, get_trace=False):
    """ Create a heatmap comparison between the two conditions"""
    conditions = [test_label, control_label]
    # Zip start and end positions into one list
    x_points = [item for x in zip(start_positions.to_list(), end_positions.to_list()) for item in x]
    # Create z values array - insert 0 between elements for sections inbetween loci
    z_values = np.array([series_test.to_list(), series_control.to_list()])
    z_values = np.dstack((z_values, np.zeros_like(z_values))).reshape(z_values.shape[0], -1)[:, :-1]
    # Create locus tag labels - insert empty string between elements for sections inbetween loci
    labels = [j for i in zip(locus_tags, [""] * len(locus_tags)) for j in i][:-1]
    # As both conditions have same labels concat in np array
    labels = np.array([labels, labels])
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.01)
    t1 = go.Heatmap(
        z=z_values,
        x=x_points,
        y=[conditions[0]],
        colorscale=[
            [0, 'rgb(255,255,255)'],  # 0
            [1. / 10000, 'rgb(201, 234, 237)'],  # 10
            [1. / 1000, 'rgb(142, 188, 204)'],  # 100
            [1. / 100, 'rgb(94, 141, 173)'],  # 1000
            [1. / 10, 'rgb(63, 94, 140)'],  # 10000
            [1., 'rgb(50, 48, 100)'],  # 100000
        ],
        customdata=labels,
        hovertemplate="Locus Tag: %{customdata}<br>NIM: %{z}<br><extra></extra>",
        showscale=False
    )
    t2 = go.Heatmap(
        z=z_values[::-1],
        x=x_points,
        y=[conditions[1]],
        colorscale=[
            [0, 'rgb(255,255,255)'],  # 0
            [1. / 10000, 'rgb(201, 234, 237)'],  # 10
            [1. / 1000, 'rgb(142, 188, 204)'],  # 100
            [1. / 100, 'rgb(94, 141, 173)'],  # 1000
            [1. / 10, 'rgb(63, 94, 140)'],  # 10000
            [1., 'rgb(50, 48, 100)'],  # 100000
        ],
        customdata=labels,
        hovertemplate="Locus Tag: %{customdata}<br>NIM: %{z}<br><extra></extra>",
        showscale=False
    )
    if get_trace:
        return [t1, t2]
    else:
        fig.add_trace(t1, 1, 1)
        fig.add_trace(t2, 2, 1)
        fig.update_layout(margin=dict(l=80, r=80, t=0, b=80),
                          xaxis2_rangeslider_visible=True,
                          xaxis1_visible=False)
        fig.update_xaxes(matches='x')
        return fig

def NIM_comparison_linked(series_control, series_test, start_positions, end_positions, locus_tags, title, color_test, color_control, test_label, control_label):
    """Create both the bar chart and heatmap but with linked xaxes"""
    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=[title])
    traces = []
    traces += NIM_comparison_bar_gl(series_control, series_test, start_positions,end_positions, locus_tags, test_label, control_label, get_trace=True)
    traces += NIM_comparison_heatmap(series_control, series_test, start_positions, end_positions, locus_tags, test_label, control_label, get_trace=True)

    traces[0]['line'].color = color_test
    traces[1]['line'].color = color_control

    traces[2]["colorscale"] = [
        (0, "white"),
        (0.0001, f'rgb{scale_lightness(ColorConverter.to_rgb(color_test), 2)}'),
        (0.001, f'rgb{scale_lightness(ColorConverter.to_rgb(color_test), 1.75)}'),
        (0.01, f'rgb{scale_lightness(ColorConverter.to_rgb(color_test), 1.5)}'),
        (0.1, f'rgb{scale_lightness(ColorConverter.to_rgb(color_test), 1.25)}'),
        (1, color_test)
    ]
    traces[3]["colorscale"] = [
        (0, "white"),
        (0.0001, f'rgb{scale_lightness(ColorConverter.to_rgb(color_control), 2)}'),
        (0.001, f'rgb{scale_lightness(ColorConverter.to_rgb(color_control), 1.75)}'),
        (0.001, f'rgb{scale_lightness(ColorConverter.to_rgb(color_control), 1.5)}'),
        (0.1, f'rgb{scale_lightness(ColorConverter.to_rgb(color_control), 1.25)}'),
        (1, color_control)
    ]

    fig.append_trace(traces[0], 1, 1)
    fig.append_trace(traces[1], 1, 1)
    fig.append_trace(traces[2], 2, 1)
    fig.append_trace(traces[3], 3, 1)

    fig.update_xaxes(matches='x')
    fig['layout']['xaxis1'].update(visible=False)
    fig['layout']['xaxis2'].update(visible=False)
    fig['layout']['xaxis3'].update(rangeslider=dict(visible=True, thickness=0.05))

    fig['layout']['yaxis1'].update(domain=[0.5, 1.0],
                                   tickmode="array")
    fig['layout']['yaxis2'].update(domain=[0.230, 0.45])
    fig['layout']['yaxis3'].update(domain=[0, 0.220])

    # General layout
    fig.update_layout(template=plotly_template,
                      legend=dict(
                          x=0,
                          y=1.0,
                      ),
                      height=800)

    return fig

def pca_plot(pca_df, control_color, test_color):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            mode='markers',
            name="Control",
            x=pca_df[pca_df["group"] == "control"]["PC1"],
            y=pca_df[pca_df["group"] == "control"]["PC2"],
            text=pca_df[pca_df["group"] == "control"].index,
            hovertemplate=
            "<b>%{text}</b><br><br>" +
            "PC1: %{x}<br>" +
            "PC2: %{y}<br>" +
            "<extra></extra>",
            marker=dict(
                line=dict(
                    color='black',
                ),
                color=control_color,
            ),
            showlegend=True
        )
    )
    # Add trace with large marker
    fig.add_trace(
        go.Scatter(
            mode='markers',
            name="Test",
            x=pca_df[pca_df["group"] == "test"]["PC1"],
            y=pca_df[pca_df["group"] == "test"]["PC2"],
            text=pca_df[pca_df["group"] == "test"].index,
            hovertemplate=
            "<b>%{text}</b><br><br>" +
            "PC1: %{x}<br>" +
            "PC2: %{y}<br>" +
            "<extra></extra>",
            marker=dict(
                size=12,
                line=dict(
                    color='black',
                    width=1
                ),
                color=test_color,
            ),
            showlegend=True
        )
    )
    fig.update_layout(
        template=plotly_template,
        height=600,
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    return fig