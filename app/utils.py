import pandas as pd


class GffDataFrame:

    gff3_cols = ["seq_id",  "source", "type", "start", "end", "score", "strand", "phase", "attributes"]

    def __init__(self, path):
        self.path = path
        self._data = self.read_gff(path)
        self.header = self._read_header()

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
