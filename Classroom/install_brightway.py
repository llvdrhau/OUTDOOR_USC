import bw2data as bd
import bw2io as bi
import multiprocessing


def import_ecoinvent(projectName):
    if projectName not in bd.projects:
        bd.projects.create_project(projectName)

    bd.projects.set_current(projectName)

    if not bd.databases:
        print("Installing outdoor database from Ecoinvent")
        # This will install the outdoor database from Ecoinvent
        try:
            # Add use_mp=False to avoid multiprocessing issues
            bi.import_ecoinvent_release(
                version="3.9.1",
                system_model="consequential",
                username="ACV_IIT",
                password="Ecoinvent123",
            )
            # This prints the directory where the current project is stored
            print(bd.projects.dir)
            print(bd.__version__)
        except Exception as e:
            print("The following error occurred:", e)
    else:
        # print in green
        print("\033[92m" + "Brightway already installed" + "\033[0m")
        print(bd.projects.dir)
        print(bd.__version__)


# This is the crucial part that prevents multiprocessing issues on Windows
if __name__ == "__main__":
    # Add freeze_support for Windows
    multiprocessing.freeze_support()
    import_ecoinvent(projectName='outdoor')
