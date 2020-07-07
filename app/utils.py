import math
import pandas as pd
import json
import pathlib


class GffDataFrame:
    """
    Class to Parse .GFF files. Uses Composition, reading data into pd.Dataframe.
    :param path: Path to gff file
    """
    gff3_cols = ["seq_id",  "source", "type", "start", "end", "score", "strand", "phase", "attributes"]

    def __init__(self, path):
        self.path = path
        self.data = self.read_gff(path)
        self.header = self._read_header()

    def __getitem__(self, item):
        return self.data[item]

    def read_gff(self, path):
        return pd.read_csv(path, sep="\t", comment="#", names=self.gff3_cols)

    def _read_header(self):
        if not self.data.empty:
            header = ""
            for line in open(self.path):
                if line.startswith("#"):
                    header += line
                else:
                    break
            return header
        else:
            return None

    def to_gff3(self, gff_file):
        gff_feature = self.data[self.gff3_cols].to_csv(sep="\t", index=False, header=None)
        with open(gff_file, "w") as fh:
            fh.write(self.header)
            fh.write(gff_feature)

    def value_counts(self, column):
        return self.data[column].value_counts()

    def dna_sequences(self):
        return self.data[self.gff3_cols[0]].unique()

    def empty_score(self):
        return (self.data["score"] == ".").all()


class PIMMSDataFrame:
    """
    PIMMSDataFrame object contains a merged dataframe from the input test and control data.
    :param control_path: Path to input csv file from control experiment
    :param test_path: Path to input csv file from test experiment
    """

    # Expected columns
    info_columns = ['seq_id', 'locus_tag', 'type', 'gene', 'start', 'end', 'feat_length', 'product']
    simple_columns = ['UK15_Blood_Output_NRM_score', 'UK15_Blood_Output_NIM_score',
                      'UK15_Media_Input_NRM_score', 'UK15_Media_Input_NIM_score']
    # Suffixes
    c_suffix = '_control'
    t_suffix = '_test'

    def __init__(self, control_path, test_path, data=None, comparision_col=None):
        self.control_path = control_path
        self.test_path = test_path
        if data is None:
            self.data = self.load_and_merge(control_path, test_path)
        else:
            self.data = data
        self.comparision_col = comparision_col

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def load_and_merge(self, control_data_path, test_data_path):
        """
        Read input csv paths into pd.Dataframe, merge into dataframe
        :param control_data_path:
        :param test_data_path:
        :return:
        """
        # Read csvs into pandas dataframe
        df_control = pd.read_csv(control_data_path)
        df_test = pd.read_csv(test_data_path)
        # Merge_control_test
        df_merged = self.merge_add_suffix(df_control, df_test, self.info_columns, self.c_suffix, self.t_suffix)
        return df_merged

    def to_json(self):
        """
        Serialise the class. Converts non-serialisable instance attributes to serialisable objects first.
        ref https://medium.com/@yzhong.cs/serialize-and-deserialize-complex-json-in-python-205ecc636caa
        :return: json
        """
        self.data = self.data.to_json(date_format='iso', orient='split')
        self.control_path = str(self.control_path)
        self.test_path = str(self.test_path)
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_data):
        """
        Recreate class instance from json. Restores data, control_path and test_path to their original type.
        :param json_data: json output from to_json method.
        :return: PIMMSDataFrame class instance
        """
        deserialised_data = json.loads(json_data)
        deserialised_data['data'] = pd.read_json(deserialised_data['data'], orient='split')
        deserialised_data['control_path'] = pathlib.Path(deserialised_data['control_path'])
        deserialised_data['test_path'] = pathlib.Path(deserialised_data['test_path'])
        return cls(**deserialised_data)

    @staticmethod
    def merge_add_suffix(df1, df2, on_columns, suffix1, suffix2):
        """
        Merge (inner) two dataframes on `on_columns`.
        Prior to merge adding a suffix to the columns not in 'on_columns' to prevent name clashes in resulting dataframe
        and maintain a record of the source dataframe for these columns.
        :param df1: pandas dataframe 1
        :param df2: pandas dataframe 2
        :param on_columns: cols to join on
        :param suffix1: suffix to append to df1 cols not in on_columns
        :param suffix2: suffix to append to df2 cols not in on_columns
        :return:  merged dataFrame
        """
        if not set(on_columns).issubset(df1) or not set(on_columns).issubset(df2):
            raise ValueError('On columns are not present in both input dataframes')

        # rename columns
        non_on_cols_df1 = set(df1.columns) - set(on_columns)
        non_on_cols_df2 = set(df2.columns) - set(on_columns)
        new_df1_col_names = dict([(i, i + suffix1) for i in list(non_on_cols_df1)])
        new_df2_col_names = dict([(i, i + suffix2) for i in list(non_on_cols_df2)])
        df1.rename(columns=new_df1_col_names, inplace=True)
        df2.rename(columns=new_df2_col_names, inplace=True)

        # Pandas inner merge
        df_m = pd.merge(df1, df2, how='inner', on=on_columns)
        return df_m

    def get_control_data_cols(self):
        return [col for col in self.data.columns if self.c_suffix in col]

    def get_test_data_cols(self):
        return [col for col in self.data.columns if self.t_suffix in col]

    def test_control_cols_containing(self, substring):
        """ Extract the data columns (ending in suffix) that contain input substring """
        c_data_cols = self.get_control_data_cols()
        t_data_cols = self.get_test_data_cols()
        c_cols_containing = [col for col in c_data_cols if substring in col]
        t_cols_containing = [col for col in t_data_cols if substring in col]
        return t_cols_containing, c_cols_containing

    def get_NIM_score_columns(self):
        test_cols, control_cols = self.test_control_cols_containing('NIM_score')
        assert (len(test_cols) == 1 and len(control_cols) == 1), 'Multi or no NIM columns found in test or control'
        return test_cols[0], control_cols[0]

    def get_NRM_score_columns(self):
        test_cols, control_cols = self.test_control_cols_containing('NRM_score')
        assert (len(test_cols) == 1 and len(control_cols) == 1), 'Multi or no NRM columns found in test or control'
        return test_cols[0], control_cols[0]

    def calc_NIM_comparision_metric(self, comparison_func, col_name):
        """
        Calculate a comparision score between test and control NIM scores. store in new column.
        :param comparison_func: Function taking two ints as inputs and returning one value.
        :param col_name: Name for comparision metric column.
        :return:
        """
        # Calc metric and insert as column
        test_NIM_col, control_NIM_col = self.get_NIM_score_columns()
        self.data[col_name] = self.data.apply(lambda row: comparison_func(row[test_NIM_col], row[control_NIM_col]),
                                              axis=1)
        self.comparision_col = col_name

    def get_df_simple(self):
        """
        Return dataframe with subset of simple columns for both test and control
        :return:
        """
        # Get simple column subset
        NIM_cols_t, NIM_cols_c = self.get_NIM_score_columns()
        NRM_cols_t, NRM_cols_c = self.get_NRM_score_columns()
        col_subset = self.info_columns + [NRM_cols_t, NRM_cols_c, NIM_cols_t, NIM_cols_c]
        if self.comparision_col:
            col_subset.append(self.comparision_col)
        return self.data[col_subset]


def log2_fold_change(a, b):
    try:
        fc = a/b
        return math.log(fc, 2)
    except (ZeroDivisionError, ValueError):
        return 0




