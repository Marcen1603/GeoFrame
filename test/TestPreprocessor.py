import os
import subprocess
import unittest

class TestPreprocessor(unittest.TestCase):

    path_to_raw = 'resources\\raw'
    path_to_buffer = 'resources\\buffer'
    path_to_preprocessed = 'resources\\preprocessed'

    def test_amount_of_raw_files(self):

        path = os.path.join('..', 'src', self.path_to_raw)
        self.assertTrue(len(path) == 8)

    def test_preprocessed_files(self):

        for file in os.listdir(os.path.join('..', 'src', self.path_to_raw)):

            raw_statistics = subprocess.run(['.\\resources\\osmconvert64-0.8.8p.exe', os.path.join('..', 'src', self.path_to_raw, file), '--out-statistics'], stdout=subprocess.PIPE).stdout.decode('utf-8')
            raw_statistics_dict = {}
            for statistic in raw_statistics.split("\n"):

                if statistic != '':
                    split = statistic.split(":", 1)
                    raw_statistics_dict[split[0]] = split[1]

            longitudinal_min = float(raw_statistics_dict['lon min'])
            longitudinal_max = float(raw_statistics_dict['lon max'])
            latitude_min = float(raw_statistics_dict['lat min'])
            latitude_max = float(raw_statistics_dict['lat max'])

            filename = file.split('.')[0]


if __name__ == '__main__':
    unittest.main()
