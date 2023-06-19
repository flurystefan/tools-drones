# -*- coding: utf-8 -*-

from grb import GroundRiskBufferCalc

aircrafts = ["rotorcraft", "fixed-wing"]

v0 = 5.00
cd = 0.90
hfg = 45.00


grp_rotorcraft = GroundRiskBufferCalc()
print(grp_rotorcraft.get_srt(v0))
print(grp_rotorcraft.get_scm(v0))
print(grp_rotorcraft.get_hrt(v0))
print(grp_rotorcraft.get_hcm(v0))
print(grp_rotorcraft.get_hcv(v0, hfg))
print(grp_rotorcraft.get_scv(v0))
print(grp_rotorcraft.get_sgrb(v0, cd, hfg))

print("-------")
grp_fixedwing = GroundRiskBufferCalc(aircrafttype="fixed-wing")
print(grp_fixedwing.get_hcm(v0))
print(grp_fixedwing.get_hcv(v0, hfg))
print(grp_fixedwing.get_scv(v0))
print(grp_fixedwing.get_sgrb(v0, cd, hfg))
