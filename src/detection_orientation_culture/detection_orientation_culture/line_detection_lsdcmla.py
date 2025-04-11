import os
import otbApplication #(module load otb/7.0-python3.6.5)

import argparse
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sys
# https://gis.stackexchange.com/questions/279874/using-qgis-3-processing-algorithms-from-pyqgis-standalone-scripts-outside-of-gu/279937#279937
# https://gis.stackexchange.com/questions/408684/using-custom-processing-algorithm-from-standalone-pyqgis-scripts-outside-of-gui
# from qgis.core import (
#      QgsApplication, 
#      QgsProcessingFeedback, 
#      QgsVectorLayer
# )

def lineSegmentDetection_CMLA(inputs):
    '''
    This function uses Orfeo ToolBox to compute a vector of detected segment lines from a given image
    :param path_in: path of the input image used tu calculate the vector of detected segment lines
    :param path_out: path of the output vector of detected segment lines
    :return: null
    '''
    path_in, path_out = inputs
    app = otbApplication.Registry.CreateApplication("LSDCMLA")
    app.SetParameterString("in", path_in)
    app.SetParameterString("out", path_out)
    app.ExecuteAndWriteOutput()


def main(args):

    if os.path.isdir(args.img):
        out_name = args.out_shp.split(".")[0]
        img_dataset = [(im_path, out_name + str(i) + ".shp") for i,im_path in enumerate(sorted(glob.glob(args.img + "/*." + args.type)))]
        with concurrent.futures.ProcessPoolExecutor(max_workers=nb_cores) as executor:
            r = list(executor.map(lineSegmentDetection_CMLA, img_dataset, chunck_size=len(img_dataset) // args.nb_cores))
    
    else:
        lineSegmentDetection_CMLA((args.img, args.out_shp))
    
    # QgsApplication.setPrefixPath('/usr', True)
    # qgs = QgsApplication([], False)
    # qgs.initQgis()





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Line Segment Detection sur images PHR')
    parser.add_argument('-img', '--img', metavar='[IMAGE]', help='Image path or directory containing the images', required=True)
    parser.add_argument('-out_shp', '--out_shp', default=None, help='Output shapefile')
    parser.add_argument('-out_csv', '--out_csv', default=None, help='Output csv file')
    parser.add_argument('-type', '--type', default="tif", help='file extension for the image(s)')
    parser.add_argument('-nb_cores', '--nb_cores', type=int, default=5)
    args = parser.parse_args()

    main(args)