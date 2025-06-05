import bw2data as bd
import bw2io as bi


def check_project_database(project_name):
    # Save current project to restore it later
    current = bd.projects.current

    if project_name not in bd.projects:
        print(f"Project '{project_name}' does not exist")
        return False

    # Switch to the project you want to check
    bd.projects.set_current(project_name)

    # Check if databases exist
    if not bd.databases:
        print(f"Project '{project_name}' has no databases")
        bd.projects.set_current(current)  # Restore original project
        return False

    # Check if databases have data
    valid_databases = []
    for db_name in bd.databases:
        db = bd.Database(db_name)
        size = len(db)
        if size > 0:
            valid_databases.append((db_name, size))

    # Restore original project
    bd.projects.set_current(current)

    if valid_databases:
        print(f"Project '{project_name}' has functional databases:")
        for db_name, size in valid_databases:
            print(f"  - {db_name}: {size} datasets")
        return True
    else:
        print(f"Project '{project_name}' has empty databases")
        return False

# Example usage
for project in bd.projects:
    projectName = project.name
    check_project_database(projectName)

##################   Check project names
# print('The current projects in Brightway are:')
# pj = bd.projects
# print(bd.projects)
# outdoorPj = bd.projects.set_current('outdoor')

################# Deleting projects
# # Be careful - this will delete all projects!
# # You might want to add a confirmation or only delete specific projects
# for project in bd.projects:
#     # Skip default project as it cannot be deleted
#     projectName = project.name
#     if projectName != "default":
#         print(f"Deleting project: {projectName}")
#         bd.projects.delete_project(projectName)
#
# print("")
# print('Projects after deletion:')
# print(bd.projects)


