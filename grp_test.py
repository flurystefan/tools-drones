# -*- coding: utf-8 -*-

from grb import GroundRiskBufferCalc

aircrafts = ["rotorcraft", "fixed-wing"]

v0 = 5.00
cd = 0.90
hfg = 45.00


grp_rotorcraft = GroundRiskBufferCalc()
print("Rotorcraft / Fixed wing srt: {:0.2f}".format(grp_rotorcraft.get_srt(v0)))
print("Rotorcraft / Fixed wing scm: {:0.2f}".format(grp_rotorcraft.get_scm(v0)))
print("Rotorcraft / Fixed wing hrt: {:0.2f}".format(grp_rotorcraft.get_hrt(v0)))
print("Rotorcraft hcm: {:0.2f}".format(grp_rotorcraft.get_hcm(v0)))
print("Rotorcraft hcv: {:0.2f}".format(grp_rotorcraft.get_hcv(v0, hfg)))
print("Rotorcraft svc: {:0.2f}".format(grp_rotorcraft.get_scv(v0)))
print("Rotorcraft grb: {:0.2f}".format(grp_rotorcraft.get_sgrb(v0, cd, hfg)))

grp_fixedwing = GroundRiskBufferCalc(aircrafttype="fixed-wing")
print("Fixed wing hcm: {:0.2f}".format(grp_fixedwing.get_hcm(v0)))
print("Fixed wing hcv: {:0.2f}".format(grp_fixedwing.get_hcv(v0, hfg)))
print("Fixed wing scv: {:0.2f}".format(grp_fixedwing.get_scv(v0)))
print("Fixed wing grb: {:0.2f}".format(grp_fixedwing.get_sgrb(v0, cd, hfg)))
