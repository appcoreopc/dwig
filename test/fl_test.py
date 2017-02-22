import sys

sys.path.append('.')
import dwig

from common_test import json_comp


class TestFLGeneration:
    def setup_class(self):
        self.parser = dwig.build_cli_parser()

    #../dwig.py -cd 2 -rs 0 fl > data/fl_i_1.json
    def test_fl_i_1(self, capfd):
        json_comp(self.parser, capfd, 'fl_i_1.json', ['-cd', '2', '-rs', '0', 'fl'])

    #../dwig.py -cd 2 -rs 0 fl -s 4 -a 0.3 > data/fl_i_2.json
    def test_fl_i_2(self, capfd):
        json_comp(self.parser, capfd, 'fl_i_2.json', ['-cd', '2', '-rs', '0', 'fl', '-s', '4', '-a', '0.3'])

    #../dwig.py -cd 2 -rs 0 fl -mc -mll 0 > data/fl_i_3.json
    def test_fl_i_3(self, capfd):
        json_comp(self.parser, capfd, 'fl_i_3.json', ['-cd', '2', '-rs', '0', 'fl', '-mc', '-mll', '0'])
