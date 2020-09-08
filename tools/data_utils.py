import os
from shutil import copyfile
import hyperspy.api as hs
import temmeta.data_io as dio


def _load_all_emi(data_path):
    """Load all ser images in a folder as a list of hyperspy datasets"""
    fls = os.listdir(data_path)
    fls.sort()
    pics = []
    for i in fls:
        n, e = os.path.splitext(i)
        if e == ".emi":
            k = hs.load(f"{data_path}/{i}")
            pics.append(k)
    return pics


def _pics_to_tm(pics):
    """Convert a list of hyperspy images to a TEMMETA imagestack dataset"""
    pics_tm = []
    for i in pics:
        pixelsize = i.axes_manager["x"].scale
        pixelunit = i.axes_manager["x"].units
        im = dio.create_new_image(i.data, pixelsize, pixelunit,
                                  process="Converted from Hyperspy")
        pics_tm.append(im)
    return dio.images_to_stack(pics_tm)


def _create_renamed_ser(data_path):
    """Copy all ser images in a folder and name according
    to the pattern expected by EWR"""
    fls = os.listdir(data_path)
    fls.sort()
    index = 0
    folder = os.path.join(data_path, "renamed")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    for i in fls:
        n, e = os.path.splitext(i)
        if e == ".ser":
            source = os.path.join(data_path, i)
            dest = os.path.join(data_path,
                                f"renamed/Image{str(index).zfill(3)}.ser")
            copyfile(source, dest)
            index = index+1


def _pics_to_hs(pics):
    """
    Convert a list of hyperspy images to a hyperspy stack
    """
    stck = _pics_to_tm(pics)
    return stck.to_hspy()


def _hs_stack_to_tm(stackhs):
    """
    Convert a hyperspy stack to a temmeta stack
    """
    return dio.create_new_image_stack(stackhs.data,
                                      stackhs.axes_manager["x"].scale,
                                      stackhs.axes_manager["x"].units)


def load_emi_folder_temmeta_stack(data_path):
    """
    Load a folder containing emi/ser files as a temmeta stack
    """
    pics = _load_all_emi(data_path)
    return _pics_to_tm(pics)


def load_emi_folder_hyperspy(data_path):
    """
    Load a folder containing emi/ser files as a hyperspy stack
    """
    pics = _load_all_emi(data_path)
    return _pics_to_hs(pics)


def get_defocus_values(images):
    """
    Get a list of defocus values from a list of hyperspy images.
    """
    defocs = [i.original_metadata.ObjectInfo.ExperimentalDescription.Defocus_um*1000 for i in images]
    return defocs


def inspect_folder(data_path):
    """
    Load images in a folder and view as a stack
    """
    stck = load_emi_folder_temmeta_stack(data_path)
    stck.plot_interactive()


def get_shifts(images):
    """
    Calculate the shifts from a simple cross-correlation between the
    images in a list. Uses the hyperspy function estimate_shift2D.
    """
    stackhs = _pics_to_hs(images)
    shfts = stackhs.estimate_shift2D(reference='cascade', normalize_corr=False,
                                     sobel=True,
                                     medfilter=True,
                                     hanning=True, plot=False, dtype='float',
                                     show_progressbar=True, sub_pixel_factor=1)
    return shfts


def verify_shifts(pics, shfts):
    """
    Apply shifts to list of images and plot it to see whether
    the calculation went well
    """
    stackhs = _pics_to_hs(pics)
    stackhs.align2D(crop=True, fill_value=0, shifts=shfts,
                    interpolation_order=1, show_progressbar=True,
                    parallel=True)
    stacktm = _hs_stack_to_tm(stackhs)
    stacktm.plot_interactive()


def get_images_info(pics, estimate_shifts=True, show_shifts=True):
    """Extract all available relevant info for the EWR config
    file from the images"""
    voltage = pics[0].original_metadata.ObjectInfo.ExperimentalConditions.MicroscopeConditions.AcceleratingVoltage
    voltage = int(float(voltage)/1000)
    N = len(pics)
    x = pics[0].axes_manager["x"].size
    y = pics[0].axes_manager["y"].size
    lenx = pics[0].axes_manager["x"].scale*x
    leny = pics[0].axes_manager["y"].scale*y
    focus_list = get_defocus_values(pics)
    if estimate_shifts:
        shfts = get_shifts(pics)
        shfts_x = shfts[1:, 0].tolist()
        shfts_y = shfts[1:, 1].tolist()
        if show_shifts:
            verify_shifts(pics, shfts)
    else:
        shfts_x = []
        shfts_y = []
    return voltage, N, x, y, lenx, leny, focus_list, shfts_x, shfts_y
