# -*- coding: utf-8 -*-
# https://www.bazl.admin.ch/dam/bazl/de/dokumente/Gut_zu_wissen/Drohnen_und_Flugmodelle/
#    how_to_apply_sora.pdf.download.pdf/FOCA-UAS-GM-Part1_ISS01REV00_HowToApply-Part1.pdf
#
import math

CONST = {
    "V2.0": {
        "trt": 1.00,    # Reaction time (page 33/51)
        "g": 9.81,      # The earth gravitational acceleration (page 15/51)
        "sgps": 3.00,   # GNSS accuracy (page 33/51)
        "spos": 3.00,   # Position hold error (page 33/51)
        "smap": 1.00,   # Path definition/Map error (page 33/51)
        "hbaro": 4.00,  # Altitude measurement error for GPS-based measurement
        "roh": 45.00    # Pitch angle
    }
}
CURRENT_VERSION = "V2.0"
AIRCRAFTTYPS = ["rotorcraft", "fixed-wing"]


def torad(value):
    return value * math.pi / 180.0


class GroundRiskBuffer:

    def __init__(self, version="current", aircrafttype="rotorcraft"):
        try:
            if version == "current":
                self.version = CURRENT_VERSION
            self.const = CONST[self.version]
            if aircrafttype in AIRCRAFTTYPS:
                self.aircrafttype = aircrafttype
            else:
                raise KeyError("Aircrafttype {} not in list {}".format(aircrafttype, AIRCRAFTTYPS))
        except Exception:
            raise

    def get_srt(self, v0):
        return self.const["trt"] * v0

    def get_scm(self, v0):
        return 0.5 * (pow(v0, 2) / (self.const["g"] * math.tan(torad(self.const["roh"]))))

    def get_hrt(self, v0):
        return (math.sqrt(2) / 2) *  v0 * self.const["trt"]

    def get_hcm(self, v0):
        if self.aircrafttype == "rotorcraft":
            return 0.5 * (pow(v0, 2) / self.const["g"])
        else:
            return 0.3 * (pow(v0, 2) / self.const["g"])

    def get_hcv(self, v0, hfg):
        return hfg + self.const["hbaro"] + self.get_hrt(v0) + self.get_hcm(v0)

    def get_scv(self, v0):
        return self.const["sgps"] + self.const["spos"] + self.const["smap"] + self.get_srt(v0) + self.get_scm(v0)

    def get_sgrb(self, v0, cd, hfg):
        if self.aircrafttype == "rotorcraft":
            return v0 * math.sqrt((2 * self.get_hcv(v0, hfg))/self.const["g"]) + 0.5 * cd
        else:
            return self.get_hcv(v0, hfg) + 0.5 * cd