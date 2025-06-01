import os
import subprocess


class Preprocessor:

    def __init__(self):

        self.path_to_planet = 'resources\\planet-250505.osm.pbf'


    def get_planet_bounding_box(self):

        result = subprocess.run(['.\\resources\\osmconvert64-0.8.8p.exe', self.path_to_planet, '--out-statistics'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        print(type(result))
        print(result)


    def main(self):

        self.get_planet_bounding_box()


if __name__ == '__main__':

    preprocessor = Preprocessor()
    preprocessor.main()