import os
import numpy as np
import numpy.linalg as la
import geopandas as gpd
import pandas as pd
import concurrent.futures
import argparse
import matplotlib.pyplot as plt

 
def compute_angle(v1, v2):
    """ Returns the angle in radians between vectors "v1" and "v2"    """
    v1 = np.array([v1[1][0] - v1[0][0], v1[1][1] - v1[0][1]])
    v2 = np.array([v2[1][0] - v2[0][0], v2[1][1] - v2[0][1]])
    cosang = np.dot(v1, v2)
    sinang = la.norm(np.cross(v1, v2))
    angle = np.degrees(np.arctan2(sinang, cosang))
    if angle > 90:
        return 180 - angle
    else:
        return angle


def chunks(orient_A, orient_B):
    for i in range(len(orient_A)):
        id_parcel = orient_A.at[i, "ID_PARCEL"]
        orient_Bi = orient_B.loc[orient_B["ID_PARCEL"]==id_parcel]
        if not orient_Bi.empty:
            # id_B = orient_Bi.index[0]
            # yield orient_A.at[i, "geometry"], orient_Bi.at[id_B, "geometry"]
            yield orient_A.loc[orient_A["ID_PARCEL"]==id_parcel], orient_B.loc[orient_B["ID_PARCEL"]==id_parcel]


def comparison_worker(orient_AB):
    orient_A, orient_B = orient_AB

    id_A = orient_A.index[0]
    id_B = orient_B.index[0]
    id_parcel = orient_A.at[id_A, "ID_PARCEL"]

    assert id_parcel == orient_B.at[id_B, "ID_PARCEL"]

    vect_A = orient_A.at[id_A, "geometry"].coords
    vect_B = orient_B.at[id_B, "geometry"].coords

    angle_AB = compute_angle(vect_A, vect_B)

    return angle_AB, id_parcel, orient_A.at[id_A, "NB_LINES"], orient_B.at[id_B, "NB_LINES"]


def main(args):
    args_dict = vars(args)
    for key in args_dict:
        print(f"{key}: {args_dict[key]}")

    orient_A = gpd.read_file(args.orientations_A)
    orient_B = gpd.read_file(args.orientations_B)

    print(f"Left Dataframe length: {len(orient_A)}, Right Dataframe length: {len(orient_B)}")

    if len(orient_A) < len(orient_B):
        splits = list(chunks(orient_A, orient_B))
        name_A = os.path.basename(args.orientations_A).split(".")[0]
        name_B = os.path.basename(args.orientations_B).split(".")[0]
    else:
        splits = list(chunks(orient_B, orient_A))
        name_A = os.path.basename(args.orientations_B).split(".")[0]
        name_B = os.path.basename(args.orientations_A).split(".")[0]

    print(f"Found {len(list(splits))} parcel ids in common, computing angles between detected orientations...", end="")
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.nb_cores) as executor:
        res = list(executor.map(comparison_worker, splits, chunksize=len(splits) // args.nb_cores))
    print("done")
    
    n, bins, patches = plt.hist(np.array([r[0] for r in res]), 
                                bins=90//args.bins_size, 
                                density=False, 
                                facecolor="g", 
                                stacked=True)
    plt.xlabel("Angles")
    plt.title("Histogram of angle comparison")
    plt.grid(True)
    plt.savefig(args.out_xls.split(".")[0] + ".png")

    df_compare = pd.DataFrame(res, columns=["ANGLE", "ID_PARCEL", "NB_LINES_" + name_A, "NB_LINES_" + name_B])

    mean_angle = df_compare["ANGLE"].mean()
    mean_nb_lines_A = df_compare["NB_LINES_" + name_A].mean()
    mean_nb_lines_B = df_compare["NB_LINES_" + name_B].mean()

    format_row = "{:<23} {:<40} {:<40}"
    print(f"Mean angle between orientations: {mean_angle:.1}°")
    print(format_row.format("", name_A, name_B))
    print(format_row.format("Mean num lines", mean_nb_lines_A, mean_nb_lines_B))
    print(format_row.format("Num orientations", len(orient_A), len(orient_B)))

    if args.out_xls:
        df_compare.to_excel(args.out_xls)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-orientations_A", "--orientations_A", required=True)
    parser.add_argument("-orientations_B", "--orientations_B", required=True)
    parser.add_argument("-bins_sz", "--bins_size", type=int, default=5, help="Bins size for the histogram")
    parser.add_argument("-out_xls", "--out_xls", default=None, help="Output csv file")
    parser.add_argument("-nb_cores", "--nb_cores", type=int, default=5)

    parser.print_help()
    args = parser.parse_args()

    main(args)
