import bw2data as bd
import bw2io as bi

# deleet the existing project
bd.projects.set_current("outdoor")
outd = bd.Database('outdoor')

# delete the existing project
for a in outd:
    a.delete()

print(bd.__version__)

bd.projects.set_current("outdoor_2")
bi.import_ecoinvent_release(version="3.9.1", system_model="consequential",
                            username="ACV_IIT",password="Ecoinvent123")
#This prints the directory where the current project is stored
bd.projects.dir
