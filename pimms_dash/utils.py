import json
import pathlib
import math
import copy
import io
import base64
import time
import shutil

import pandas as pd

from app import DATA_PATH

class GffDataFrame:
    """
    Class to Parse .GFF files. Uses Composition, reading data into pd._Dataframe.
    :param path: Path to gff file
    """
    gff3_cols = ["seq_id",  "source", "type", "start", "end", "score", "strand", "phase", "attributes"]

    def __init__(self, path, data=None, header=None):
        self.path = path
        if data is None:
            self._data = self.read_gff(path)
        else:
            self._data = data

        if header is None:
            self.header = self._read_header()
        else:
            self.header = header

    def __getitem__(self, item):
        return self._data[item]

    def read_gff(self, path):
        return pd.read_csv(path, sep="\t", comment="#", names=self.gff3_cols)

    def _read_header(self):
        if not self._data.empty:
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
        gff_feature = self._data[self.gff3_cols].to_csv(sep="\t", index=False, header=None)
        with open(gff_file, "w") as fh:
            fh.write(self.header)
            fh.write(gff_feature)

    def value_counts(self, column):
        return self._data[column].value_counts()

    def dna_sequences(self):
        return self._data[self.gff3_cols[0]].unique()

    def empty_score(self):
        return (self._data["score"] == ".").all()

    def to_json(self):
        """
        Serialise the class. Converts non-serialisable instance attributes to serialisable objects first.
        ref https://medium.com/@yzhong.cs/serialize-and-deserialize-complex-json-in-python-205ecc636caa
        :return: json
        """
        serialisable_instance = copy.deepcopy(self)
        serialisable_instance._data = serialisable_instance._data.to_json(date_format='iso', orient='split')
        serialisable_instance.path = str(serialisable_instance.path)
        return json.dumps(serialisable_instance.__dict__)

    @classmethod
    def from_json(cls, json_data):
        """
        Recreate class instance from json. Restores data, control_path and test_path to their original type.
        :param json_data: json output from to_json method.
        :return: PIMMSDataFrame class instance
        """
        deserialised_data = json.loads(json_data)
        deserialised_data['data'] = deserialised_data.pop('_data')
        deserialised_data['data'] = pd.read_json(deserialised_data['data'], orient='split')
        deserialised_data['path'] = pathlib.Path(deserialised_data['path'])
        return cls(**deserialised_data)


class PIMMSDataFrame:
    """
    PIMMSDataFrame object contains a merged dataframe from the input test and control data.
    Uses Composition to extend pandas dataframe with methods specific to PIMMS use case.
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

    def __init__(self, control_path, test_path, data=None, comparison_cols=None):
        self.control_path = control_path
        self.test_path = test_path

        if data is None:
            self._data = self.load_and_merge(control_path, test_path)
        else:
            self._data = data

        if comparison_cols is not None:
            self.comparison_cols = [col_name for col_name in comparison_cols if col_name in self._data.columns]
        else:
            self.comparison_cols = []

        # Calculate comparison columns
        self.calc_NIM_comparision_metric(fold_change_comparision, 'fold_change')
        self.calc_NIM_comparision_metric(percentile_rank_comparision, 'pctl_rank')

    def __len__(self):
        return len(self._data)

    def get_data(self):
        return self._data.round(3)

    def get_columns(self, simple=False, c_metric='all'):
        if c_metric not in self.comparison_cols + [None, 'all']:
            raise ValueError(f"c_metric {c_metric} not in comparison columns")

        if simple:
            # Get simple column subset
            NIM_cols_t, NIM_cols_c = self.get_NIM_score_columns()
            NRM_cols_t, NRM_cols_c = self.get_NRM_score_columns()
            columns = self.info_columns + [NRM_cols_t, NRM_cols_c, NIM_cols_t, NIM_cols_c] + self.comparison_cols
        elif not simple:
            columns = self._data.columns.to_list()
        else:
            raise ValueError

        if c_metric == "all":
            return columns
        else:
            columns = [col for col in columns if col not in self.comparison_cols]
            if c_metric:
                columns.append(c_metric)
            return columns

    def insert_column(self, col_name, series):
        self._data.insert(len(self._data.columns), col_name, series)

    def load_and_merge(self, control_data_path, test_data_path):
        """
        Read input csv paths into pd._Dataframe, merge into dataframe
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
        serialisable_instance = copy.deepcopy(self)
        serialisable_instance._data = serialisable_instance._data.to_json(date_format='iso', orient='split')
        serialisable_instance.control_path = str(serialisable_instance.control_path)
        serialisable_instance.test_path = str(serialisable_instance.test_path)
        return json.dumps(serialisable_instance.__dict__)

    @classmethod
    def from_json(cls, json_data):
        """
        Recreate class instance from json. Restores data, control_path and test_path to their original type.
        :param json_data: json output from to_json method.
        :return: PIMMSDataFrame class instance
        """
        deserialised_data = json.loads(json_data)
        deserialised_data['data'] = deserialised_data.pop('_data')
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
        return [col for col in self._data.columns if self.c_suffix in col]

    def get_test_data_cols(self):
        return [col for col in self._data.columns if self.t_suffix in col]

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
        :param comparison_func: Function taking two pandas series as inputs and returning one series.
        :param col_name: Name for comparision metric column.
        :return:
        """
        if col_name not in self._data.columns:
            # Calc metric and insert as column
            test_NIM_col, control_NIM_col = self.get_NIM_score_columns()
            self._data[col_name] = comparison_func(self._data[test_NIM_col], self._data[control_NIM_col])
        if col_name not in self.comparison_cols:
            self.comparison_cols.append(col_name)


def log2_fold_change(a, b):
    try:
        fc = float(a)/float(b)
        return math.log(fc, 2)
    except (ZeroDivisionError, ValueError):
        return 0


def fold_change_comparision(series_a, series_b):
    df = pd.concat([series_a, series_b], axis=1)
    return df.apply(lambda row: log2_fold_change(row[series_a.name], row[series_b.name]), axis=1)


def percentile_rank_comparision(series_a, series_b):
    df = pd.concat([series_a, series_b], axis=1)
    df['percentile_a'] = df[series_a.name].rank(method='min', pct=True)
    df['percentile_b'] = df[series_b.name].rank(method='min', pct=True)
    return df['percentile_a'] - df['percentile_b']


def parse_upload(contents, filename):
    content_type, content_string = contents.split(',')
    save_path = DATA_PATH.joinpath(filename)
    decoded = base64.b64decode(content_string)
    try:
        if save_path.is_file():
            raise IOError('File Already Exists')
        if '.csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df.to_csv(save_path, index=False)
            return f'Uploaded {filename}'
        elif '.xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_excel(DATA_PATH.joinpath(filename), index=False)
            return f'Uploaded {filename}'
        else:
            raise TypeError('Unexpected file format')
    except Exception as e:
        print(e)
        return f'Error processing {filename}: {e}'


def get_stored_csv_files():
    return list(DATA_PATH.glob('*.csv'))


def store_data(string, name, session_id):
    session_dir = DATA_PATH.joinpath('session_data', session_id)
    if not session_dir.exists():
        session_dir.mkdir(parents=True, exist_ok=True)
        with open(session_dir.joinpath("timestamp.txt"), "w") as text_file:
            text_file.write(str(time.time()))
    with open(session_dir.joinpath(f'{name}.json'), 'w') as f:
        json.dump(string, f)

def load_data(name, session_id):
    session_dir = DATA_PATH.joinpath('session_data', session_id)
    with open(session_dir.joinpath(f'{name}.json')) as f:
        data = json.load(f)
    return data

def manage_session_data():
    data_session_folder = DATA_PATH.joinpath('session_data')
    for session_dir in data_session_folder.iterdir():
        timestamp_path = session_dir.joinpath('timestamp.txt')
        if not timestamp_path.exists():
            continue
        with open(timestamp_path, "r") as f:
            ts = float(f.readlines()[0])
        time_period = time.time() - float(ts)
        if time_period > 60*20:
            shutil.rmtree(session_dir)
