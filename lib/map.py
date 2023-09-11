import os, __main__, shutil, pathlib

class Map:
    # mapname = Friendly name
    # mapid = Folder path for the map
    # mappath = Relative path to the DMM
    # z = Target Z to extract
    def __init__(self, mapname, mapid, mappath, z):
        self.mapname = mapname
        self.mapid = mapid
        self.mappath = mappath
        self.z = z
        self.dmm_short = self.mappath.split(".dmm")[0].split("/")[-1]

    def render(self, codebase):
        # Set directory
        os.chdir("{}/codebases/{}".format(__main__.BASEDIR, codebase.repopath))

        # Make output path
        __main__.logProgress("Creating output paths")
        pathlib.Path("{}/out/{}/{}".format(__main__.BASEDIR, codebase.tname, self.mapid)).mkdir(parents=True, exist_ok=True)

        # Render the map
        os.system("./renderer minimap '{}' {}".format(self.mappath, codebase.renderargs))

        # Copy
        for z in self.z:
            shutil.copy2(
                "{}/codebases/{}/data/minimaps/{}-{}.png".format(__main__.BASEDIR, codebase.repopath, self.dmm_short, z),
                "{}/out/{}/{}/{}-{}.png".format(__main__.BASEDIR, codebase.tname, self.mapid, self.dmm_short, z)
            )
        __main__.logProgress("Completed normal render for {}/{}".format(codebase.name, self.mapname))

        # Render pipenet if applicable
        if codebase.renderpipenet:
            os.system("./renderer-pipenet minimap '{}' {} -o \"./data/minimaps/pipenet\"".format(self.mappath, codebase.renderargs))
            for z in self.z:
                shutil.copy2(
                    "{}/codebases/{}/data/minimaps/pipenet/{}-{}.png".format(__main__.BASEDIR, codebase.repopath, self.dmm_short, z),
                    "{}/out/{}/{}/{}-{}-pipe.png".format(__main__.BASEDIR, codebase.tname, self.mapid, self.dmm_short, z)
                )
            __main__.logProgress("Completed pipenet render for {}/{}".format(codebase.name, self.mapname))