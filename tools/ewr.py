import os
from . import config_tools as ct
from . import data_utils as du


def setup_ewr(data_path,
              estimate_shifts=True,
              show_shifts=True,
              **kwargs):
    """
    Create a config file for a set of .SER images representing a focal series
    Also copy the ser files according to the required naming convention.

    Parameters
    ----------
    data_path: str
        The path to the folder containing the images

    Other parameters
    ----------------
    estimate_shifts: boolean
        Use hyperspy to calculate the relative shifts of images with cross-correlation.
        This is used in the first step as a first guess in the EWR algorithm.
    show_shifts: boolean
        Plot the images after the alignment to see whether the result makes sense
    alpha: float
        Beam spread parameter in mrad (spatial coherence). Default is 4e-4
    focal_spread: float
        Defocus spread in nm (temporal coherence). Default is 4
    spherical_aberation: float
        Spherical aberation constant C_s in nm. Default is -40,
    sub_x: int
        If you want to run the calculation on a rectangular subset of the data,
        this represents the upper-left x-coordinate. Default is 0.
    sub_y: int
        If you want to run the calculation on a rectangular subset of the data,
        this represents the upper-left y-coordinate. Default is 0.
    sub_w: int
        If you want to run the calculation on a rectangular subset of the data,
        this represents the width of the subset. Default is -1, representing
        The full image.
    sub_h: int
        If you want to run the calculation on a rectangular subset of the data,
        this represents the height of the subset. Default is -1, representing
        The full image.
    filename: str
        Full or relative path to where the file should be saved. Default is ./config.param.
    config_path: str
        Full or relative path to the default template config file.
    **kwargs
        Any additional option from the EWR config file may be passed as argument.
        Please refer to the in-line comments of the default config file
    """
    pics = du._load_all_emi(data_path)
    output = du.get_images_info(pics,
                                estimate_shifts=estimate_shifts,
                                show_shifts=show_shifts)
    voltage, N, x, y, lenx, leny, focus_list, shfts_x, shfts_y = output
    if estimate_shifts:
        image_indexes = list(range(1, N))
    else:
        image_indexes = []
    du._create_renamed_ser(data_path)
    ct.create_config(os.path.join(data_path, "renamed"), voltage, N, x, y, lenx, leny,
                     focus_list, image_indexes=image_indexes,
                     image_shx=shfts_x, image_shy=shfts_y, **kwargs)
