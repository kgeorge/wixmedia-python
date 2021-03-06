from exceptions import MissingCmd
from media import Media
import os

VERSION = 'v1'


class CmdBuilder(object):
    def __init__(self, cmd, *param_list, **param_dict):
        self.cmd    = cmd
        self.params = list()

        self.add(*param_list, **param_dict)

    def add(self, *param_list, **param_dict):
        self.params.extend([str(p) for p in param_list])
        self.params.extend(["%s_%s" % (k, v) for k, v in iter(sorted(param_dict.iteritems()))])

    def build_cmd(self):
        return '%s/%s' % (self.cmd, ','.join(self.params))


class Image(Media):
    COMMAND_NONE      = ""
    COMMAND_SRZ       = "srz"
    COMMAND_SRB       = "srb"
    COMMAND_CANVAS    = "canvas"
    COMMAND_FILL      = "fill"
    COMMAND_FIT       = "fit"
    COMMAND_CROP      = "crop"

    adjust_parameter_map = {
        "brightness": "br",
        "contrast":   "con",
        "saturation": "sat",
        "hue":        "hue",
    }

    alignment_value_map = {
        "center":       "c",
        "top":          "t",
        "top-left":     "tl",
        "top-right":    "tr",
        "bottom":       "b",
        "bottom-left":  "bl",
        "bottom-right": "br",
        "left":         "l",
        "right":        "r",
        "face":         "face"
    }

    def __init__(self, image_id, service_host, client):
        super(Image, self).__init__(image_id, service_host, client)

        self.cmd_builder  = None
        self.commands     = list()

    def reset(self):
        self.cmd_builder = None
        self.commands    = list()

    def assert_cmd(self):
        if self.cmd_builder is None:
            raise MissingCmd("Missing transformation command. Original image cannot be used.")

    def canvas(self, width, height, alignment=None, ext_color=None):
        """
        default values: alignment="center", ext_color="000000"
        """

        if self.cmd_builder:
            self.commands.append(self.cmd_builder.build_cmd())

        self.cmd_builder = CmdBuilder(Image.COMMAND_CANVAS, w=width, h=height)

        if alignment is not None:
            self.cmd_builder.add(al=Image.alignment_value_map[alignment])

        if ext_color is not None:
            self.cmd_builder.add(c=ext_color)

        return self

    def crop(self, x, y, width, height):
        if self.cmd_builder:
            self.commands.append(self.cmd_builder.build_cmd())

        self.cmd_builder = CmdBuilder(Image.COMMAND_CROP, x=x, y=y, w=width, h=height)

        return self

    def fill(self, width, height, resize_filter=None, alignment=None):
        """
        default value: resize_filter=LanczosFilter
        """

        if self.cmd_builder:
            self.commands.append(self.cmd_builder.build_cmd())

        self.cmd_builder = CmdBuilder(Image.COMMAND_FILL, w=width, h=height)

        if resize_filter is not None:
            self.cmd_builder.add(rf=resize_filter)

        if alignment is not None:
            self.cmd_builder.add(al=Image.alignment_value_map[alignment])

        return self

    def fit(self, width, height, resize_filter=None):
        """
        default value: resize_filter=LanczosFilter
        """

        if self.cmd_builder:
            self.commands.append(self.cmd_builder.build_cmd())

        self.cmd_builder = CmdBuilder(Image.COMMAND_FIT, w=width, h=height)

        if resize_filter is not None:
            self.cmd_builder.add(rf=resize_filter)

        return self

    def adjust(self, brightness=None, contrast=None, saturation=None, hue=None):

        self.assert_cmd()

        props_dict = {
            'brightness': brightness,
            'contrast': contrast,
            'saturation': saturation,
            'hue': hue
        }

        for prop, value in props_dict.iteritems():
            if value is not None:
                self.cmd_builder.add(**{Image.adjust_parameter_map[prop]: value})

        return self

    def auto_adjust(self):
        self.assert_cmd()
        self.cmd_builder.add('auto_adj')

        return self

    def oil(self):
        self.assert_cmd()
        self.cmd_builder.add('oil')

        return self

    def neg(self):
        self.assert_cmd()
        self.cmd_builder.add('neg')

        return self

    def pixelate(self, value):
        self.assert_cmd()
        self.cmd_builder.add(**{'pix': value})

        return self

    def blur(self, value):
        self.assert_cmd()
        self.cmd_builder.add(**{'blur': value})

        return self

    def sharpen(self, radius):
        self.assert_cmd()
        self.cmd_builder.add(**{'shrp': radius})

        return self

    def unsharp(self, radius=0.5, amount=0.2, threshold=0.0):
        self.cmd_builder.add(**{'usm': "%.2f_%.2f_%.2f" % (radius, amount, threshold)})

        return self

    def quality(self, value=75):
        self.assert_cmd()
        self.cmd_builder.add(**{'q': value})

        return self

    def baseline(self):
        self.assert_cmd()
        self.cmd_builder.add('bl')

        return self

    def get_url(self):
        file_uri_path, org_file_name = os.path.split(self.id)

        params = ['http://%s' % self.service_host, file_uri_path, VERSION]
        params.extend(self.commands)
        params.append(self.cmd_builder.build_cmd())
        params.append(org_file_name)

        return "/".join(params)