import bw2data as bd
import bw2io as bi

if "outdoor" not in bd.projects:
    bd.projects.create_project("outdoor")
    bd.projects.set_current("outdoor")
    try:
        bi.import_ecoinvent_release(version="3.9.1", system_model="consequential",
                                     username="ACV_IIT",password="Ecoinvent123")
        # This prints the directory where the current project is stored
        print(bd.projects.dir)
        print(bd.__version__)

    except Exception as e:
        print("The following error occurred:",e)

else:
    # print in green
    print("\033[92m" + "Brightway already installed" + "\033[0m")
