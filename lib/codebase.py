import __main__, os, requests, shutil
from datetime import datetime

class Codebase:
    def __init__(self, name, tname, gitapiurl, remotebranch, repopath, renderpipenet, executablepath, mapdir, maps, renderargs=""):
        self.name = name
        self.tname = tname
        self.gitapiurl = gitapiurl
        self.remotebranch = remotebranch
        self.repopath = repopath
        self.mapdir = mapdir
        self.renderpipenet = renderpipenet
        self.executablepath = executablepath
        self.maps = maps
        self.renderargs = renderargs
        self.hash = None
        self.exit_code = 0
        self.total_maps = []
        self.rendered_maps = []
        for _map in maps:
            self.total_maps.append(_map.mapname)

    def update(self):
        os.chdir("{}/codebases/{}".format(__main__.BASEDIR, self.repopath))
        os.system("git fetch origin")
        os.system("git reset --hard origin/{}".format(self.remotebranch))
        os.system("git clean -dfx")

        # Copy render executables in
        shutil.copy2("{}/executables/{}".format(__main__.BASEDIR, self.executablepath), "{}/codebases/{}/renderer".format(__main__.BASEDIR, self.repopath))
        if self.renderpipenet:
            shutil.copy2("{}/executables/{}-pipenet".format(__main__.BASEDIR, self.executablepath), "{}/codebases/{}/renderer-pipenet".format(__main__.BASEDIR, self.repopath))

    def process(self):
        t = datetime.now()
        __main__.logProgress("Updating local git for {}...".format(self.name))
        self.update()
        __main__.logProgress("Updated local git for {} successfully within {}s".format(self.name, round((datetime.now() - t).total_seconds())))
        __main__.logProgress("Processing maps for {}...".format(self.name))
        t = datetime.now()
        for _map in self.maps:
            try:
                mt = datetime.now()
                __main__.logProgress("Processing {}/{}...".format(self.name, _map.mapname))
                _map.render(self)
                self.rendered_maps.append(_map.mapname)
                __main__.logProgress("Processed {}/{} within {}s".format(self.name, _map.mapname, round((datetime.now() - mt).total_seconds())))
            except Exception as e:
                print(e)
                __main__.logProgress("Failed to process {}/{}. Skipping to next map.".format(self.name, _map.mapname))
                __main__.failCode = 1
                self.exit_code = 1 # Minor fail
        __main__.logProgress("Processed maps for {} successfully within {}s".format(self.name, round((datetime.now() - t).total_seconds())))
        # Save new hash
        with __main__.DB() as dbi:
            dbc = dbi.cursor(buffered=True)
            # Update its last processed date
            stmt = "UPDATE codebases SET hash=%s, maps_total=%s, maps_successful=%s, last_updated=NOW() WHERE id=%s"
            data = (self.hash, ", ".join(self.total_maps), ", ".join(self.rendered_maps), self.tname)
            dbc.execute(stmt, data)
        self.setExitCode() # We successfully rendered


    def checkForUpdate(self):
        __main__.logProgress("Checking {} for updates...".format(self.name))
        headers = {"Authorization" : "token {}".format(__main__.GIT_TOKEN)}
        remote = requests.get("{}/{}".format(self.gitapiurl, self.remotebranch), headers=headers).json()
        trees = remote["tree"]
        for tree in trees:
            if tree["path"] == self.mapdir:
                # Found the right tree. Compare hashes
                with __main__.DB() as dbi:
                    dbc = dbi.cursor(buffered=True)
                    stmt = "SELECT hash FROM codebases WHERE id=%s"
                    data = (self.tname,)
                    dbc.execute(stmt, data)
                    result = dbc.fetchone()[0]
                    if result != tree["sha"]:
                        # Hashes differ, queue it for an update!
                        self.hash = tree["sha"]
                        __main__.codebasesToProcess.append(self)
                    
                    # Update its last processed date
                    stmt = "UPDATE codebases SET last_checked=NOW() WHERE id=%s"
                    data = (self.tname,)
                    dbc.execute(stmt, data)

    def setExitCode(self):
        with __main__.DB() as dbi:
            dbc = dbi.cursor(buffered=True)
            stmt = "UPDATE codebases SET render_code=%s WHERE id=%s"
            data = (self.exit_code, self.tname)
            dbc.execute(stmt, data)
