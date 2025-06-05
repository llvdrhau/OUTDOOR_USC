import bw2io as io
import bw2calc as bc
import bw2data as bw
import pandas as pd

#%%
bw.projects.set_current("superstructure")
bios = bw.Database("ecoinvent-3.9.1-biosphere")
eidb = bw.Database("ecoinvent-3.9.1-consequential")

#%%
midpoint = [m for m in bw.methods if
                    "ReCiPe 2016 v1.03, midpoint (H)" in str(m) and not "no LT" in str(m)]
endpoints = [m for m in bw.methods if
                     "ReCiPe 2016 v1.03, endpoint (H)" in str(m) and not "no LT" in str(m) and "total" in str(m)]
methodconfs = midpoint + endpoints
#%%
for e in methodconfs:
    ## use --> print(e[2],"|", bw.Method(e).metadata.get("unit"))
    #print(e[3],"|", bw.Method(e).metadata.get("unit"))
    abbr = ""
    if "midpoint" in str(e):
        abbr = (e[3].split("(")[1].split(")")[0])
    if "endpoint" in str(e):
        abbr = (e[3])

    print(e[2],"|",abbr, "|", bw.Method(e).metadata.get("unit"))
#%%
was = [m for m in eidb if m["code"] == "b0043a9ba35dea3f767abb1cf200032f"]
print(was[0])
