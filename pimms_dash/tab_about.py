import dash_bootstrap_components as dbc
import dash_html_components as html

about_tab_layout = dbc.Card(
    [
        dbc.CardHeader(html.H4("About PIMMS Dashboard"), className="font-weight-bold"),
        dbc.CardImg(src="/assets/Strept.png", top=True),
        dbc.CardBody(
            [
                # html.H5("Pragmatic Insertional Mutation Mapping System"),
                # html.P("""The PIMMS pipeline has been
                # developed for simple conditionally essential genome discovery experiments in bacteria.
                # Capable of using raw sequence data files alongside a FASTA sequence of the
                # reference genome and GFF file, PIMMS will generate a tabulated output of each coding
                # sequence with corresponding mapped insertions accompanied with normalized results
                # enabling streamlined analysis. This allows for a quick assay of the genome to identify
                # conditionally essential genes on a standard desktop computer prioritizing results for
                # further investigation.""", className="card-text"),
                html.H5("What it is"),
                html.P("""
                The PIMMS2 Dashboard allows for easy and approachable further analysis and summary from high
                 throughput mutagenesis data.
                """),
                html.H5("What it does"),
                html.P("Produces summaries, metrics, statistics and publication ready figures."),
                html.H5("How to use"),
                html.P("Upload and select the PIMMs pipeline output files in the Data tab. After running your "
                       "selection, interactive figures become available in their respective tabs"),
                html.H5("Supported by"),
                html.P("""
                The International Development Research Centre through the InnoVet-AMR project “Disease intervention
                targets for porcine Streptococccus suis infections in Vietnam”
                """),
                html.H5("Useful links"),
                dbc.Row(
                    [
                        dbc.Button("PIMMS Paper", color="dark", outline=True, external_link=True, target='_blank',
                                   className="text-center mr-3",
                                   href='https://www.frontiersin.org/articles/10.3389/fmicb.2016.01645/full'),
                        dbc.Button("Transposon insertion mapping with PIMMS", color="dark", outline=True, external_link=True, target='_blank',
                                   className="text-center mr-3",
                                   href='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4391243/pdf/fgene-06-00139.pdf'),
                        dbc.Button("PIMMS GitHub", color="dark", outline=True, external_link=True, target='_blank',
                                   className="text-center",
                                   href='https://github.com/Streptococcal-Research-Group/PIMMS2'),
                    ],
                    justify="center",
                    className="mt-2 ml-1"
                ),
            ]
        ),
    ],
    className="mt-3 text-center",
)