from lib.codebase import Codebase
from lib.map import Map
from datetime import datetime
import os, mysql.connector, traceback, pytoml

with open('config.toml', 'rb') as config_file:
    config_object = pytoml.load(config_file)

BASEDIR = config_object["general"]["basedir"]
GIT_TOKEN = config_object["general"]["git_token"]

os.chdir(BASEDIR)

jobLog = []

# 0 = success
# 1 = codebase map fail
# 2 = codebase fail
# 3 = major fail
failCode = 0

# DB Handler
class DB(object):
    def __enter__(self):
        self.dbcon = mysql.connector.connect(
            host=config_object["database"]["host"],
            user=config_object["database"]["username"],
            passwd=config_object["database"]["password"],
            database=config_object["database"]["db"]
        )
        return self.dbcon

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbcon.commit()
        self.dbcon.close()

def logProgress(text):
    global jobLog
    text = "[{}] {}".format(datetime.now().isoformat().split(".")[0], text)
    jobLog.append(text)
    print(text)

# Logging timestamp
startTime = datetime.now()
logProgress("Starting up")

# This will be populated by the class initialization below
codebasesToProcess = []

tempTime = datetime.now()
logProgress("Registering codebases...")

codebases = [
    # name, tname, gitapiurl, remotebranch, repopath, renderpipenet, mapdir, maps, dmmtoolsargs
    Codebase("AquilaStation", "aquila", "https://api.github.com/repos/aq33/NSV13/git/trees", "master", "Aquila-NSV", True, "_maps", [
        Map("Atlas Lower", "atlas", "_maps/map_files/Atlas/atlas.dmm", [1]),
        Map("Atlas Upper", "atlas", "_maps/map_files/Atlas/atlas2.dmm", [1]),
        Map("Atlantis Lower", "atlantis", "_maps/map_files/Atlantis/Atlantis.dmm", [1]),
        Map("Atlantis Upper", "atlantis", "_maps/map_files/Atlantis/Atlantis2.dmm", [1]),
        Map("Snake Lower", "snake", "_maps/map_files/Snake/snake_lower.dmm", [1]),
        Map("Snake Upper", "snake", "_maps/map_files/Snake/snake_upper.dmm", [1]),
        Map("Serendipity Lower", "serendipity", "_maps/map_files/Serendipity/Serendipity2.dmm", [1]),
        Map("Serendipity Upper", "serendipity", "_maps/map_files/Serendipity/Serendipity1.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("Austation", "austation", "https://api.github.com/repos/austation/austation/git/trees", "master", "austation", True, "_maps", [
        Map("Austation", "austation", "_maps/map_files/Austation/Austation.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("Baystation12", "bay12", "https://api.github.com/repos/Baystation12/Baystation12/git/trees", "dev", "Baystation12", True, "maps", [
        Map("Torch 1", "torch", "maps/torch/torch1_deck5.dmm", [1]),
        Map("Torch 2", "torch", "maps/torch/torch2_deck4.dmm", [1]),
        Map("Torch 3", "torch", "maps/torch/torch3_deck3.dmm", [1]),
        Map("Torch 4", "torch", "maps/torch/torch4_deck2.dmm", [1]),
        Map("Torch 5", "torch", "maps/torch/torch5_deck1.dmm", [1]),
        Map("Torch Bridge", "torch", "maps/torch/torch6_bridge.dmm", [1]),
    ]),

    Codebase("BeeStation", "bee", "https://api.github.com/repos/BeeStation/BeeStation-Hornet/git/trees", "master", "BeeStation-Hornet", True, "_maps", [
        Map("BoxStation", "boxstation", "_maps/map_files/BoxStation/BoxStation.dmm", [1]),
        Map("CorgStation", "corgstation", "_maps/map_files/CorgStation/CorgStation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2.dmm", [1]),
        Map("KiloStation", "kilostation", "_maps/map_files/KiloStation/KiloStation.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]),
        Map("FlandStation", "flandstation", "_maps/map_files/FlandStation/FlandStation.dmm", [1]),
        Map("RadStation", "radstation", "_maps/map_files/RadStation/RadStation.dmm", [1]),
        Map("EchoStation", "echostation", "_maps/map_files/EchoStation/EchoStation.dmm", [1, 2, 3, 4]),
    ], "--disable smart-cables"),

    Codebase("BlueMoon", "bluemoon", "https://api.github.com/repos/BlueMoon-Labs/MOLOT-BlueMoon-Station/git/trees", "master", "MOLOT-BlueMoon-Station", False, "_maps", [
        Map("ArmyStation", "armystation", "_maps/map_files/ArmyStation/ArmyStation.dmm", [1]),
        Map("BoxStation", "boxstation", "_maps/map_files/BoxStation/BoxStation.dmm", [1]),
        Map("CogStation", "cogstation", "_maps/map_files/CogStation/CogStation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2.dmm", [1]),
        Map("KiloStation", "kilostation", "_maps/map_files/KiloStation/KiloStation.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]),
        Map("OmegaStation", "omegastation", "_maps/map_files/OmegaStation/OmegaStation.dmm", [1]),
        Map("PubbyStation", "pubbystation", "_maps/map_files/PubbyStation/PubbyStation.dmm", [1]),
        Map("SyndicateBoxStation", "syndicateboxstation", "_maps/map_files/SyndicateStation/SyndicateBoxStation.dmm", [1]),
        Map("TauStation", "taustation", "_maps/map_files/TauStation/TauStation.dmm", [1]),
    ]),

    Codebase("BurgerStation", "burger", "https://api.github.com/repos/BurgerLUA/burgerstation/git/trees", "master", "burgerstation", False, "maps", [
        Map("BurgerStation", "burgerstation", "maps/core/burgerstation.dmm", [1]),
    ]),
    
    Codebase("Citadel Station RP", "citrp", "https://api.github.com/repos/Citadel-Station-13/Citadel-Station-13-RP/git/trees", "master", "Citadel-Station-13-RP", True, "maps", [
        # Atlas has a ton
        Map("Atlas Western Plains", "atlas", "maps/rift/levels/rift-10-west_plains.dmm", [1]),
        Map("Atlas Western Caves S", "atlas", "maps/rift/levels/rift-09-west_caves.dmm", [1]),
        Map("Atlas Western Caves D", "atlas", "maps/rift/levels/rift-08-west_deep.dmm", [1]),
        Map("Atlas Western Canyons", "atlas", "maps/rift/levels/rift-07-west_base.dmm", [1]),
        Map("Atlas S3 Command Deck", "atlas", "maps/rift/levels/rift-06-surface3.dmm", [1]),
        Map("Atlas S2 Opearations Deck", "atlas", "maps/rift/levels/rift-05-surface2.dmm", [1]),
        Map("Atlas S1 Logistics Deck", "atlas", "maps/rift/levels/rift-04-surface1.dmm", [1]),
        Map("Atlas U-1 Maintenance Deck", "atlas", "maps/rift/levels/rift-03-underground1.dmm", [1]),
        Map("Atlas U-2 Engineering Deck", "atlas", "maps/rift/levels/rift-02-underground2.dmm", [1]),
        Map("Atlas U-3 Canyon", "atlas", "maps/rift/levels/rift-01-underground3.dmm", [1]),
        # Tether
        Map("Tether ST2 Logistics Deck", "tether", "maps/tether/levels/station2.dmm", [1]),
        Map("Tether ST1 Engineering Deck", "tether", "maps/tether/levels/station1.dmm", [1]),
        Map("Tether SU3 Service Command", "tether", "maps/tether/levels/surface3.dmm", [1]),
        Map("Tether SU2 Research Life Support", "tether", "maps/tether/levels/surface2.dmm", [1]),
        Map("Tether SU1 Lobby External", "tether", "maps/tether/levels/surface1.dmm", [1]),
        # Triumph
        Map("Triumph 4 Command Deck", "triumph", "maps/triumph/levels/deck4.dmm", [1]),
        Map("Triumph 3 Operations Deck", "triumph", "maps/triumph/levels/deck3.dmm", [1]),
        Map("Triumph 2 Service Deck", "triumph", "maps/triumph/levels/deck2.dmm", [1]),
        Map("Triumph 1 Engineering Deck", "triumph", "maps/triumph/levels/deck1.dmm", [1]),
    ]),

    Codebase("ChaoticOnyx", "onyx", "https://api.github.com/repos/ChaoticOnyx/OnyxBay/git/trees", "dev", "OnyxBay", False, "maps", [
        Map("Exodus 1", "exodus", "maps/exodus/exodus-1.dmm", [1]),
        Map("Exodus 2", "exodus", "maps/exodus/exodus-2.dmm", [1]),
        Map("Exodus 4", "exodus", "maps/exodus/exodus-4.dmm", [1]),
        Map("Exodus 6", "exodus", "maps/exodus/exodus-6.dmm", [1]),
        Map("Frontier 1", "frontier", "maps/exodus/frontier/frontier-1.dmm", [1]),
        Map("Frontier 3", "frontier", "maps/exodus/frontier/frontier-3.dmm", [1]),
        Map("Genesis 1", "genesis", "maps/exodus/genesis/genesis-1.dmm", [1]),
        Map("Genesis 2", "genesis", "maps/exodus/genesis/genesis-2.dmm", [1]),
        Map("Genesis 3", "genesis", "maps/exodus/genesis/genesis-3.dmm", [1]),
        Map("Genesis 6", "genesis", "maps/exodus/genesis/genesis-6.dmm", [1]),
    ]),

    Codebase("Citadel Station TG", "cit", "https://api.github.com/repos/Citadel-Station-13/Citadel-Station-13/git/trees", "master", "Citadel-Station-13", True, "_maps", [
        Map("BoxStation", "boxstation", "_maps/map_files/BoxStation/BoxStation.dmm", [1]),
        Map("CogStation", "cogstation", "_maps/map_files/CogStation/CogStation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2.dmm", [1]),
        Map("LambdaStation", "lambdastation", "_maps/map_files/LambdaStation/lambda.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]),
        Map("OmegaStation", "omegastation", "_maps/map_files/OmegaStation/OmegaStation.dmm", [1]),
        Map("PubbyStation", "pubbystation", "_maps/map_files/PubbyStation/PubbyStation.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("CM-SS13", "cm", "https://api.github.com/repos/cmss13-devs/cmss13/git/trees", "master", "cmss13", True, "maps", [
        Map("Fiorina Science Annex", "fiorina", "maps/map_files/FOP_v3_Sciannex/Fiorina_SciAnnex.dmm", [1]),
        Map("Kutjevo Refinery", "kutjevo", "maps/map_files/Kutjevo/Kutjevo.dmm", [1]),
        Map("USS Almayer", "almayer", "maps/map_files/USS_Almayer/USS_Almayer.dmm", [1]),
        Map("LV624", "lv624", "maps/map_files/LV624/LV624.dmm", [1]),
        Map("Solaris Ridge", "solaris", "maps/map_files/BigRed/BigRed.dmm", [1]),
        Map("Trijent Dam", "trijent", "maps/map_files/DesertDam/Desert_Dam.dmm", [1]),
        Map("Shivas Snowball", "shivas", "maps/map_files/Ice_Colony_v3/Shivas_Snowball.dmm", [1]),
        Map("Whiskey Outpost", "whiskey", "maps/map_files/Whiskey_Outpost_v2/Whiskey_Outpost_v2.dmm", [1]),
        Map("Sorokyne Strata", "sorokyne", "maps/map_files/Sorokyne_Strata/Sorokyne_Strata.dmm", [1]),
        Map("LV522", "lv522", "maps/map_files/LV522_Chances_Claim/LV522_Chances_Claim.dmm", [1]),
        Map("NewVaradero", "newvaradero", "maps/map_files/New_Varadero/New_Varadero.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("DaedalusDock", "daedalus", "https://api.github.com/repos/DaedalusDock/daedalusdock/git/trees", "master", "daedalusdock", True, "_maps", [
        Map("Theseus", "theseus", "_maps/map_files/Theseus/Theseus.dmm", [1]),
    ]),

    Codebase("Effigy", "effigy", "https://api.github.com/repos/effigy-se/effigy-se/git/trees", "main", "effigy-se", True, "_maps", [
        Map("FoxHoleStation", "foxholestation", "_maps/map_files/FoxHoleStation/foxholestation.dmm", [1, 2]),
        Map("Tramstation", "tramstation", "_maps/map_files/tramstation/tramstation.dmm", [1, 2]),
        Map("MiniStation", "ministation", "_maps/map_files/MiniStation/MiniStation.dmm", [1]),
        Map("NorthStar", "northstar", "_maps/map_files/NorthStar/north_star.dmm", [1, 2, 3, 4]), 
        Map("IceBox", "icebox", "_maps/map_files/IceBoxStation/IceBoxStation.dmm", [1, 2, 3]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]), 
        Map("RimPoint", "rimpoint", "_maps/map_files/RimPoint/RimPoint.dmm", [1, 2]), 
        Map("SigmaOctantis", "sigmaoctantis", "_maps/map_files/SigmaOctantis/SigmaOctantis.dmm", [1, 2]), 
    ]),
    
    Codebase("Eris", "eris", "https://api.github.com/repos/discordia-space/CEV-Eris/git/trees", "master", "CEV-Eris", False, "maps", [
        Map("CEV Eris", "eris", "maps/CEVEris/_CEV_Eris.dmm", [1,2,3,4,5]),
    ], "--disable smart-cables"),

    Codebase("Foundation19", "foundation19", "https://api.github.com/repos/Foundation-19/Foundation-19/git/trees", "dev", "Foundation-19", False, "maps", [
        Map("Site53-1", "site53", "maps/site53/site53-1.dmm", [1]),
        Map("Site53-2", "site53", "maps/site53/site53-2.dmm", [1]),
        Map("Site53-3", "site53", "maps/site53/site53-3.dmm", [1]),
        Map("Site53-4", "site53", "maps/site53/site53-4.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("Fulpstation", "fulp", "https://api.github.com/repos/fulpstation/fulpstation/git/trees", "master", "fulpstation", False, "_maps", [
        Map("HelioStation", "heliostation", "_maps/map_files/Heliostation/Heliostation.dmm", [1]),
        Map("SeleneStation", "selenestation", "_maps/map_files/SeleneStation/SeleneStation.dmm", [1]),
        Map("PubbyStation", "pubbystation", "_maps/map_files/PubbyStation/PubbyStation.dmm", [1]),
    ]),

    Codebase("Gearstation", "gearstation", "https://api.github.com/repos/sergeirocks100/GearStation_Next/git/trees", "master", "GearStation", True, "_maps", [
        Map("KiloStation", "kilostation", "_maps/map_files/KiloStation/KiloStation.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2.dmm", [1]),
        Map("IceBox", "icebox", "_maps/map_files/IceBoxStation/IceBoxStation.dmm", [1, 2, 3]),
    ]),

    Codebase("Goonstation", "goon", "https://api.github.com/repos/goonstation/goonstation/git/trees", "master", "goonstation", False, "maps", [
        Map("Atlas", "atlas", "maps/atlas.dmm", [1]),
        Map("Clarion", "clarion", "maps/clarion.dmm", [1]),
        Map("Cogmap", "cogmap", "maps/cogmap.dmm", [1]),
        Map("Cogmap2", "cogmap2", "maps/cogmap2.dmm", [1]),
        Map("Destiny", "destiny", "maps/destiny.dmm", [1]),
        Map("Horizon", "horizon", "maps/horizon.dmm", [1]),
        Map("Manta", "manta", "maps/manta.dmm", [1]),
        Map("Oshan", "oshan", "maps/oshan.dmm", [1]),
        Map("Donut", "donut", "maps/donut3.dmm", [1]),
    ]),

    Codebase("Hearth of Hestia", "hoh", "https://api.github.com/repos/HearthOfHestia/Nebula/git/trees", "dev", "Nebula", False, "maps", [
        Map("Torch 1", "torch", "maps/torch/torch1_deck5.dmm", [1]),
        Map("Torch 2", "torch", "maps/torch/torch2_deck4.dmm", [1]),
        Map("Torch 3", "torch", "maps/torch/torch3_deck3.dmm", [1]),
        Map("Torch 4", "torch", "maps/torch/torch4_deck2.dmm", [1]),
        Map("Torch 5", "torch", "maps/torch/torch5_deck1.dmm", [1]),
        Map("Torch Bridge", "torch", "maps/torch/torch6_bridge.dmm", [1]),
    ]),

    Codebase("Lumos SS13", "lumos", "https://api.github.com/repos/Lumos-SS13/Lumos/git/trees", "master", "Lumos", False, "_maps", [
        Map("BoxStation", "boxstation", "_maps/map_files/BoxStation/BoxStation_Lumos.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2_Lumos.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation_Lumos.dmm", [1]),
        Map("OmegaStation", "omegastation", "_maps/map_files/OmegaStation/OmegaStation_Lumos.dmm", [1]),
        Map("PubbyStation", "pubbystation", "_maps/map_files/PubbyStation/PubbyStation_Lumos.dmm", [1]),
        Map("Lavaland", "lavaland", "_maps/map_files/Mining/Lavaland_Lumos.dmm", [1]),
        Map("Snaxi", "snaxi", "_maps/map_files/Snaxi/Snaxi_Lumos.dmm", [1]),
        Map("Snaxi Underground Above", "snaxi", "_maps/map_files/Snaxi/IcemoonUnderground_Above_Lumos.dmm", [1]),
        Map("Snaxi Underground Below", "snaxi", "_maps/map_files/Snaxi/IcemoonUnderground_Below_Lumos.dmm", [1]),
        Map("FridgeStation", "fridgestation", "_maps/map_files/FridgeStation/FridgeStation.dmm", [1]),
        Map("FridgeStation Underground Above", "fridgestation", "_maps/map_files/FridgeStation/IcemoonUnderground_Fridge_Above.dmm", [1]),
        Map("FridgeStation Underground Below", "fridgestation", "_maps/map_files/FridgeStation/IcemoonUnderground_Fridge_Below.dmm", [1]),
    ], "--disable smart-cables"),

    Codebase("NovaSector", "nova", "https://api.github.com/repos/NovaSector/NovaSector/git/trees", "master", "NovaSector", True, "_maps", [
        Map("VoidRaptor", "voidraptor", "_maps/map_files/VoidRaptor/VoidRaptor.dmm", [1]), 
        Map("Blueshift", "blueshift", "_maps/map_files/NSVBlueshift/Blueshift.dmm", [1, 2]),
        Map("Ouroboros", "ouroboros", "_maps/map_files/Ouroboros/Ouroboros.dmm", [1, 2]),
    ]),

    Codebase("NSV13", "nsv", "https://api.github.com/repos/BeeStation/NSV13/git/trees", "master", "NSV13", True, "_maps", [
        Map("Hammerhead", "hammerhead", "_maps/map_files/Hammerhead/Hammerhead.dmm", [1]),
        Map("Tycoon 1", "tycoon", "_maps/map_files/Tycoon/Tycoon1.dmm", [1]),
        Map("Tycoon 2", "tycoon", "_maps/map_files/Tycoon/Tycoon2.dmm", [1]),
        Map("Aetherwhisp 1", "aetherwhisp", "_maps/map_files/Aetherwhisp/Aetherwhisp1.dmm", [1]),
        Map("Aetherwhisp 2", "aetherwhisp", "_maps/map_files/Aetherwhisp/Aetherwhisp2.dmm", [1]),
        Map("Gladius 1", "gladius", "_maps/map_files/Gladius/Gladius1.dmm", [1]),
        Map("Gladius 2", "gladius", "_maps/map_files/Gladius/Gladius2.dmm", [1]),
        Map("Atlas 1", "atlas", "_maps/map_files/Atlas/atlas.dmm", [1]),
        Map("Atlas 2", "atlas", "_maps/map_files/Atlas/atlas2.dmm", [1]),
        Map("Eclipse 1", "eclipse", "_maps/map_files/Eclipse/Eclipse1.dmm", [1]),
        Map("Eclipse 2", "eclipse", "_maps/map_files/Eclipse/Eclipse2.dmm", [1]),
        Map("Galactica 1", "galactica", "_maps/map_files/Galactica/Galactica1.dmm", [1]),
        Map("Galactica 2", "galactica", "_maps/map_files/Galactica/Galactica2.dmm", [1]),
        Map("Shrike 1", "shrike", "_maps/map_files/Shrike/Shrike1.dmm", [1]),
        Map("Shrike 2", "shrike", "_maps/map_files/Shrike/Shrike2.dmm", [1]),
        Map("Snake Upper", "snake", "_maps/map_files/Snake/snake_upper.dmm", [1]),
        Map("Snake Lower", "snake", "_maps/map_files/Snake/snake_lower.dmm", [1]),
        Map("Serendipity Upper", "serendipity", "_maps/map_files/Serendipity/Serendipity1.dmm", [1]),
        Map("Serendipity Lower", "serendipity", "_maps/map_files/Serendipity/Serendipity2.dmm", [1]),
    ], "--disable smart-cables,icon-smoothing"),

    Codebase("ParadiseSS13", "paradise", "https://api.github.com/repos/ParadiseSS13/Paradise/git/trees", "master", "Paradise", True, "_maps", [
        Map("Cyberiad", "cyberiad", "_maps/map_files/stations/boxstation.dmm", [1]),
        Map("CereStation", "cerestation", "_maps/map_files/stations/cerestation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/stations/deltastation.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files/stations/metastation.dmm", [1]),
    ]),

    Codebase("SinguloStation", "singulo", "https://api.github.com/repos/SinguloStation13/SinguloStation13/git/trees", "master", "SinguloStation13", False, "_maps", [
        Map("ConstructionStation", "construction", "_maps/map_files/ConstructionStation/ConstructionStation.dmm", [1]),
        Map("CryoStation", "cryo", "_maps/map_files/CryoStation/CryoStation.dmm", [1]),
    ]),

    Codebase("Skyrat TG", "skyrat-tg", "https://api.github.com/repos/Skyrat-SS13/Skyrat-tg/git/trees", "master", "Skyrat-tg", True, "_maps", [
        Map("VoidRaptor", "voidraptor", "_maps/map_files/VoidRaptor/VoidRaptor.dmm", [1]), 
        Map("BlueShift Lower Deck", "blueshift", "_maps/map_files/Blueshift/BlueShift_lower.dmm", [1]),
        Map("BlueShift Middle Deck", "blueshift", "_maps/map_files/Blueshift/BlueShift_middle.dmm", [1]),
        Map("BlueShift Upper Deck", "blueshift", "_maps/map_files/Blueshift/BlueShift_upper.dmm", [1]),
    ]),

    Codebase("SS1984", "ss1984", "https://api.github.com/repos/ss220-space/Paradise/git/trees", "master220", "SS220-Paradise", True, "_maps", [
        Map("Cyberiad", "cyberiad", "_maps/map_files/cyberiad/cyberiad.dmm", [1]),
        Map("CereStation", "cerestation", "_maps/map_files/cerestation/cerestation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files/Delta/delta.dmm", [1]),
    ]),

    Codebase("SS220", "ss220", "https://api.github.com/repos/ss220club/Paradise-SS220/git/trees", "master", "Paradise-SS220", False, "_maps", [
        Map("BoxStation", "boxstation", "_maps/map_files220/stations/boxstation.dmm", [1]),
        Map("DeltaStation", "deltastation", "_maps/map_files220/stations/deltastation.dmm", [1]),
        Map("MetaStation", "metastation", "_maps/map_files220/stations/metastation.dmm", [1]),
    ]),

    Codebase("TaleStation", "talestation", "https://api.github.com/repos/TaleStation/TaleStation/git/trees", "master", "TaleStation", True, "_maps", [
        Map("Lima", "lima", "_maps/map_files/LimaStation/LimaStation.dmm", [1, 2]), 
        Map("PubbyStation", "pubby", "_maps/map_files/PubbyStation/PubbyStation.dmm", [1]),
        Map("KiloStation", "kilo", "_maps/map_files/KiloStation/KiloStation.dmm", [1]),
    ]),

    Codebase("Tau Ceti Classic", "tcc", "https://api.github.com/repos/TauCetiStation/TauCetiClassic/git/trees", "master", "TauCetiClassic", True, "maps", [
        Map("Asteroid", "asteroid", "maps/asteroid/asteroid.dmm", [1]),
        Map("BoxStation", "box", "maps/boxstation/boxstation.dmm", [1]),
        Map("Gamma", "gamma", "maps/gamma/gamma.dmm", [1]),
        Map("Falcon", "falcon", "maps/falcon/falcon.dmm", [1]),
        Map("Prometheus", "prometheus", "maps/prometheus/prometheus.dmm", [1]),
        Map("Prometheus Asteroid", "prometheus_asteroid", "maps/prometheus_asteroid/prometheus_asteroid.dmm", [1]),
    ], "--disable smart-cables,icon-smoothing"),

    Codebase("tgstation", "tgstation", "https://api.github.com/repos/tgstation/tgstation/git/trees", "master", "tgstation", True, "_maps", [
        Map("DeltaStation", "deltastation", "_maps/map_files/Deltastation/DeltaStation2.dmm", [1]),
        Map("IceBox", "icebox", "_maps/map_files/IceBoxStation/IceBoxStation.dmm", [1, 2, 3]),
        Map("MetaStation", "metastation", "_maps/map_files/MetaStation/MetaStation.dmm", [1]),
        Map("TramStation", "tramstation", "_maps/map_files/tramstation/tramstation.dmm", [1, 2]),
        Map("NorthStar", "northstar", "_maps/map_files/NorthStar/north_star.dmm", [1, 2, 3, 4]),
        Map("BirdShot", "birdshot", "_maps/map_files/Birdshot/birdshot.dmm", [1]),
    ]),
    
    Codebase("TGMC", "tgmc", "https://api.github.com/repos/tgstation/terragov-marine-corps/git/trees", "master", "TerraGov-Marine-Corps", True, "_maps", [
        Map("TGS Theseus", "theseus", "_maps/map_files/Theseus/TGS_Theseus.dmm", [1]),
        Map("Big Red", "bigred", "_maps/map_files/BigRed_v2/BigRed_v2.dmm", [1]),
        Map("Ice Colony", "icecolony", "_maps/map_files/Ice_Colony_v2/Ice_Colony_v2.dmm", [1]),
        Map("LV624", "lv624", "_maps/map_files/LV624/LV624.dmm", [1]),
        Map("Prison Station", "prisonstation", "_maps/map_files/Prison_Station_FOP/Prison_Station_FOP.dmm", [1]),
        Map("Pillar Of Spring", "pillarofspring", "_maps/map_files/Pillar_of_Spring/TGS_Pillar_of_Spring.dmm", [1]),
        Map("Icy Caves", "icycaves", "_maps/map_files/icy_caves/icy_caves.dmm", [1]),
        Map("Whiskey Outpost", "whiskey_outpost", "_maps/map_files/Whiskey_Outpost/Whiskey_Outpost_v2.dmm", [1]),
        Map("Research Outpost", "researchoutpost", "_maps/map_files/Research_Outpost/Research_Outpost.dmm", [1]),
        Map("Sulaco", "sulaco", "_maps/map_files/Sulaco/Sulaco.dmm", [1]),
        Map("Desert", "desert", "_maps/map_files/desert/desert.dmm", [1]),
        Map("Barrenquilla Mining Facility", "barrenquilla", "_maps/map_files/Barrenquilla_Mining/Barrenquilla_Mining_Facility.dmm", [1]),
        Map("Magmoor Digsite IV", "magmoordigsiteiv", "_maps/map_files/Magmoor_Digsite_IV//Magmoor_Digsite_IV.dmm", [1]),
        Map("Minerva", "minerva", "_maps/map_files/Minerva/TGS_Minerva.dmm", [1]),
        Map("Chigusa", "chigusa", "_maps/map_files/desertdam/desertdam.dmm", [1]),
        Map("Orion", "orion", "_maps/map_files/Orion_Military_Outpost/orionoutpost.dmm", [1]),
        Map("GelidaIV", "gelidaiv", "_maps/map_files/gelida_iv/gelida_iv.dmm", [1]),
        Map("LawankaOutpost", "lawankaoutpost", "_maps/map_files/Lawanka_Outpost/LawankaOutpost.dmm", [1]),
        Map("Slumbridge", "slumbridge", "_maps/map_files/slumbridge/slumbridge.dmm", [1]),
        Map("Arachne", "arachne", "_maps/map_files/Arachne/TGS_Arachne.dmm", [1]),
    ]),

    Codebase("Yogstation", "yog", "https://api.github.com/repos/Yogstation13/Yogstation/git/trees", "master", "Yogstation", True, "_maps", [
        Map("Yogs Meta", "yogsmeta", "_maps/map_files/Yogsmeta/Yogsmeta.dmm", [1]),
        Map("YogStation", "yogstation", "_maps/map_files/YogStation/YogStation.dmm", [1]),
        Map("GaxStation", "gaxstation", "_maps/map_files/GaxStation/GaxStation.dmm", [1]),
        Map("AsteroidStation", "asteroid", "_maps/map_files/AsteroidStation/AsteroidStation.dmm", [1]),
    ], "--disable smart-cables"),
]

logProgress("Codebases registered within {}s".format(round((datetime.now() - tempTime).total_seconds())))

namesToProcess = []

try:
    tempTime = datetime.now()
    logProgress("Checking all codebases for update...")
    for CB in codebases:
        CB.checkForUpdate()
    logProgress("Update check complete within {}s".format(round((datetime.now() - tempTime).total_seconds())))


    for CB in codebasesToProcess:
        namesToProcess.append(CB.name)

    # Sort
    namesToProcess = sorted(namesToProcess)

    logProgress("Codebases to process ({}): {}".format(len(namesToProcess), ", ".join(namesToProcess)))

    for CB in codebasesToProcess:
        codebaseProcessingTime = datetime.now()
        logProgress("Processing {}...".format(CB.name))
        try:
            CB.process()
            logProgress("Processed {} successfully within {}s".format(CB.name, round((datetime.now() - codebaseProcessingTime).total_seconds())))
        except Exception as e:
            CB.exit_code = 2
            CB.setExitCode()
            failCode = 2
            print(e)
            logProgress("Failed to process {}. Continuing to next codebase.".format(CB.name))

    if len(codebasesToProcess) > 0:
        # Sync to remote server
        logProgress("Starting sync...")
        syncTime = datetime.now()
        os.chdir(BASEDIR)
        os.system("./sync.sh")
        logProgress("Sync complete within {}s".format(round((datetime.now() - syncTime).total_seconds())))
    else:
        logProgress("No maps were updated. Sync aborted.")

    # Were done here
    logProgress("Webmap update complete within {}s".format(round((datetime.now() - startTime).total_seconds())))


except Exception as e:
    logProgress("A fatal error occured during the webmap update. Please inform AA07.")
    print(traceback.format_exc())
    failCode = 3

# Save logs
with DB() as dbi:
    dbc = dbi.cursor(buffered=True)
    stmt = "INSERT INTO job_log (success, start_time, job_log, codebases_processed) VALUES (%s, %s, %s, %s)"
    data = (int(failCode), startTime.isoformat(), "\n".join(jobLog), ", ".join(namesToProcess))
    dbc.execute(stmt, data)
