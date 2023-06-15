# -*- coding: utf-8 -*-

from grp import GroundRiskBuffer

aircrafts = ["rotorcraft", "fixed-wing"]

v0 = 5.00
cd = 0.90
hfg = 45.00


grp_rotorcraft = GroundRiskBuffer()
grp_fixedwing = GroundRiskBuffer(aircrafttype="fixed-wing")
print(grp_rotorcraft.get_srt(v0))
print(grp_rotorcraft.get_scm(v0))
print(grp_rotorcraft.get_hrt(v0))
print(grp_rotorcraft.get_hcm(v0))
print(grp_rotorcraft.get_hcv(v0, hfg))
print(grp_rotorcraft.get_scv(v0))
print(grp_rotorcraft.get_sgrb(v0, cd, hfg))

print("-------")
print(grp_fixedwing.get_hcm(v0))
print(grp_fixedwing.get_hcv(v0, hfg))
print(grp_fixedwing.get_scv(v0))
print(grp_fixedwing.get_sgrb(v0, cd, hfg))