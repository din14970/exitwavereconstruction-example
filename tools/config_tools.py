import re
import os
import sys


class config_dict(dict):
    def __init__(self, data):
        super().__init__(data)

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if isinstance(value, list):
            stringlist = " ".join(map(str, value))
            value = f"{{ {stringlist} }}"
        super().__setitem__(key, str(value))

    def save(self, path):
        write_config(self, path)


def load_config(path):
    with open(path) as f:
        config = f.read()
    options = re.findall(r"^(\w+)\s+(.+)$", config, flags=re.M)
    return config_dict(options)


def write_config(options, path):
    config = ""
    for key, value in options.items():
        config = config+str(key)+" "+str(value)+"\n"
    with open(path, "w") as f:
        f.write(config)


def create_config(folder, voltage, n, x, y, lenx, leny, focus_list,
                  alpha=4e-4, focal_spread=4, spherical_aberation=-40,
                  sub_x=0, sub_y=0, sub_w=-1, sub_h=-1,
                  image_indexes=[], image_shx=[], image_shy=[],
                  filename="config.param",
                  config_path="default_parameters.param",
                  **kwargs):
    try:
        config_dict = load_config(config_path)
    except Exception as e:
        print(f"Something went wrong reading the default config file: {e}")
        sys.exit()
    config_dict.inputDataFile = "\""+os.path.abspath(folder)+"\""
    config_dict.AcceleratingVoltage = voltage
    config_dict.alpha = alpha
    config_dict.FocalSpread = focal_spread
    config_dict.SphericalAberration = spherical_aberation
    config_dict.N = n
    config_dict.X = x
    config_dict.Y = y
    config_dict.lenX = lenx
    config_dict.lenY = leny
    config_dict.Focus = focus_list
    config_dict.subsection_x = sub_x
    config_dict.subsection_y = sub_y
    config_dict.subsection_width = sub_w
    config_dict.subsection_height = sub_h
    config_dict.initialGuess_TranslationHint_Img = image_indexes
    config_dict.initialGuess_TranslationHint_ShiftX = image_shx
    config_dict.initialGuess_TranslationHint_ShiftY = image_shy
    for key, value in kwargs.items():
        config_dict[key] = value
    config_dict.save(filename)
    print(f"Created config file in {os.path.abspath(filename)}")
