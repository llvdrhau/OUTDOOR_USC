import bw2data as bd
import bw2io as bi
import multiprocessing
projectName = 'outdoor'

if __name__ == "__main__":
    bd.projects.create_project(projectName)
    bd.projects.set_current(projectName)
    # Add use_mp=False to avoid multiprocessing issues
    bi.import_ecoinvent_release(
        version="3.9.1",
        system_model="consequential",
        username="ACV_IIT",
        password="Ecoinvent123",
    )
