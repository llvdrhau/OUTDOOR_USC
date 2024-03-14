import bw2data as bw
import bw2io as io


class LCA_Back:
    ##ctor for the LCA backend. Also pass a hook to the gui here so it can send up angries like "you didn't make a project you ghoul"
    def __init__(self,project: str = "outdoor",) -> None:
        self.project = project
        bw.projects.set_current(self.project)
        needs_ei = True
        needs_bios = True
        for db in bw.databases:
            print(db)
            if "ei_" in db:
                self.eidb = bw.Database(db)
                needs_ei = False
            if "biosphere" in db:
                self.bios = bw.Database(db)
                needs_bios = False
        if needs_ei:
            ##Do a notify to PyQT but for now just log to console
            pass
        if needs_bios:
            #second verse same as the first
            pass
    
    def search(self,term: str ="") -> list[str] | None:
        eidb_results = [m for m in self.eidb if term in m["name"]]
        bios_results = [m for m in self.bios if term in m["name"]]
        
        return eidb_results + bios_results