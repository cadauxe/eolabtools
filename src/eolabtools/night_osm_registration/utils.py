import os
import rasterio
import pyproj
import geopandas as gpd
import otbApplication
import shapely
from rasterio import features, mask


def otb_img_resample(otb_displacementgrid_path, otb_input_path, otb_output_path, raster_src_shape):
    app = otbApplication.Registry.CreateApplication("GridBasedImageResampling")
    app.SetParameterString("io.in", otb_input_path)
    app.SetParameterString("io.out", otb_output_path)
    app.SetParameterString("grid.in", otb_displacementgrid_path)
    app.SetParameterInt("out.sizex", raster_src_shape[1])
    app.SetParameterInt("out.sizey", raster_src_shape[0])
    app.SetParameterString("grid.type", "def")
    app.SetParameterString("interpolator", "linear")
    app.ExecuteAndWriteOutput()


def crop_raster(path_out, raster_src, roi_file, roi_list):
    raster_src_crs = raster_src.crs
    raster_src_transform = raster_src.transform
    raster_src_shape = raster_src.shape
    raster_src_dtype = raster_src.read(1).dtype

    if roi_file is not None:
        roi = gpd.read_file(roi_file)
        if roi is not None:
            for shapes in roi.geometry:
                if (roi.crs != raster_src_crs):
                    # reproject
                    project = pyproj.Transformer.from_proj(pyproj.Proj(init=roi.crs), pyproj.Proj(init=raster_src_crs))
                    shapes = shapely.ops.transform(project.transform, shapes)
                roi_list.append(shapes)

            print("cropping of the input raster")

            cropped_raster, cropped_transform = mask.mask(raster_src, roi_list, crop=True)

            with rasterio.open(path_out + "/cropped_raster.tif", mode="w", driver="GTiff", height=cropped_raster.shape[1],
                               width=cropped_raster.shape[2], count=cropped_raster.shape[0], dtype=cropped_raster.dtype,
                               transform=cropped_transform, crs=raster_src_crs) as new_dataset:
                new_dataset.write(cropped_raster)

            del cropped_raster
            raster_src = rasterio.open(path_out + "/cropped_raster.tif")
            raster_src_transform = raster_src.transform
            raster_src_shape = raster_src.shape
            raster_src_dtype = raster_src.read(1).dtype
    return raster_src, raster_src_crs, raster_src_dtype, raster_src_shape, raster_src_transform


def remove_otb_path(otb_displacementgrid_path, otb_input_path, otb_output_path):
    if os.path.exists(otb_input_path):
        os.remove(otb_input_path)
    else:
        print("The file does not exist :", otb_input_path)
    if os.path.exists(otb_output_path):
        os.remove(otb_output_path)
    else:
        print("The file does not exist :", otb_output_path)
    if os.path.exists(otb_displacementgrid_path):
        os.remove(otb_displacementgrid_path)
    else:
        print("The file does not exist :", otb_displacementgrid_path)
