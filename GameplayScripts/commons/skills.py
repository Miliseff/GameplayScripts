from lview import *
import math, itertools, time
from . import items
from commons.byLib import *
from enum import Enum
import numpy as np

Version = "experimental version"
MissileToSpell = {}
SpellsToEvade = {}
Spells = {}
ChampionSpells = {}


class SFlag:
    Targeted = 1
    Line = 2
    Cone = 4
    Area = 8

    CollideWindwall = 16
    CollideChampion = 32
    CollideMob = 64

    CollideGeneric = CollideMob | CollideChampion | CollideWindwall
    SkillshotLine = CollideGeneric | Line


class HitChance(Enum):
    Immobile = 8
    Dashing = 7
    VeryHigh = 6
    High = 5
    Medium = 4
    Low = 3
    Impossible = 2
    OutOfRange = 1
    Collision = 0


_HitChance = HitChance.Impossible


class DangerLevels:
    Easy = 1
    Fastes = 2
    UseSpell = 3
    VeryDangerous = 4


class Spell:
    def __init__(
        self, name, missile_names, flags, delay=0.0, danger=DangerLevels.Fastes
    ):
        global MissileToSpell, Spells

        self.flags = flags
        self.name = name
        self.missiles = missile_names
        self.delay = delay
        self.danger = danger
        Spells[name] = self
        for missile in missile_names:
            if len(missile) < 1:
                MissileToSpell[name] = self
            MissileToSpell[missile] = self

    delay = 0.0
    danger = DangerLevels.Fastes
    flags = 0
    name = "?"
    missiles = []
    skills = []


ChampionSpells = {
    "aatrox": [
        Spell("aatroxw", ["aatroxw"], SFlag.SkillshotLine),
        Spell("aatroxq", ["aatroxq1"], SFlag.SkillshotLine),
        Spell("aatroxq2", ["aatroxq2"], SFlag.SkillshotLine),
        Spell("aatroxq3", ["aatroxq3"], SFlag.SkillshotLine),
    ],
    "rell": [Spell("rellq", ["rellq_vfxmis"], SFlag.SkillshotLine)],
    "twistedfate": [Spell("wildcards", ["sealfatemissile"], SFlag.SkillshotLine)],
    "zoe": [
        Spell("zoeqmissile", ["zoeqmissile"], SFlag.SkillshotLine),
        Spell("zoeqmis2", ["zoeqmis2"], SFlag.SkillshotLine),
        Spell("zoee", ["zoeemis"], SFlag.SkillshotLine),
        Spell("zoeebubble", ["zoeec"], SFlag.Area),
    ],
    "ornn": [
        Spell("ornnq", ["ornnqmissile", "ornnq"], SFlag.SkillshotLine),
        Spell("ornnrwave2", ["ornnrwave2"], SFlag.Line),
        Spell("ornnrwave", ["ornnrwave"], SFlag.Line),
    ],
    "kassadin": [
        Spell("riftwalk", ["riftwalk"], SFlag.Area),
        Spell("forcepulse", [], SFlag.Cone),
    ],
    "katarina": [
        Spell("katarinaw", ["katarinadaggerarc"], SFlag.Area),
    ],
    "quinn": [Spell("quinnq", ["quinnq"], SFlag.CollideGeneric)],
    "aurelionsol": [
        Spell("aurelionsolq", ["aurelionsolqmissile"], SFlag.SkillshotLine),
        Spell("aurelionsolr", ["aurelionsolrbeammissile"], SFlag.SkillshotLine),
    ],
    "ahri": [
        Spell("ahriorbofdeception", ["ahriorbmissile"], SFlag.SkillshotLine),
        Spell("ahriseduce", ["ahriseducemissile"], SFlag.SkillshotLine),
    ],
    "ashe": [
        Spell(
            "enchantedcrystalarrow",
            ["enchantedcrystalarrow"],
            SFlag.SkillshotLine,
        ),
        Spell("volleyrank1", ["volleyrank1"], SFlag.SkillshotLine),
        Spell("volleyrank2", ["volleyrank2"], SFlag.SkillshotLine),
        Spell("volleyrank3", ["volleyrank3"], SFlag.SkillshotLine),
        Spell("volleyrank4", ["volleyrank4"], SFlag.SkillshotLine),
        Spell("volleyrank5", ["volleyrank5"], SFlag.SkillshotLine),
    ],
    "shen": [Spell("shene", ["shene"], SFlag.Line)],
    "elise": [Spell("elisehumane", ["elisehumane"], SFlag.SkillshotLine)],
    "sylas": [
        Spell("sylase2", ["sylase2"], SFlag.SkillshotLine),
        Spell("sylasq", [], SFlag.Area),
        Spell("sylasqline", [], SFlag.Line),
    ],
    "camille": [Spell("camillee", ["camilleemissile"], SFlag.SkillshotLine)],
    "kennen": [
        Spell(
            "kennenshurikenhurlmissile1",
            ["kennenshurikenhurlmissile1"],
            SFlag.SkillshotLine,
        )
    ],
    "darius": [
        Spell("dariuscleave", [], SFlag.Area),
        Spell("dariusaxegrabcone", ["dariusaxegrabcone"], SFlag.Cone),
    ],
    "brand": [
        Spell("brandq", ["brandqmissile"], SFlag.SkillshotLine),
        Spell("brandw", ["brandw"], SFlag.Area),
    ],
    "pyke": [
        Spell("pykeqrange", ["pykeqrange", "pykeq"], SFlag.Line),
        Spell("pykee", ["pykeemissile"], SFlag.Line),
    ],
    "amumu": [
        Spell(
            "bandagetoss", ["sadmummybandagetoss"], SFlag.Line | SFlag.CollideWindwall
        )
    ],
    "caitlyn": [
        Spell(
            "caitlynpiltoverpeacemaker",
            ["caitlynpiltoverpeacemaker", "caitlynpiltoverpeacemaker2"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("caitlynyordletrap", [], SFlag.Area),
        Spell("caitlynentrapment", ["caitlynentrapmentmissile"], SFlag.SkillshotLine),
    ],
    "chogath": [
        Spell("rupture", ["rupture"], SFlag.Area),
        Spell("feralscream", ["feralscream"], SFlag.Cone | SFlag.CollideWindwall),
    ],
    "drmundo": [
        Spell(
            "infectedcleavermissilecast",
            ["infectedcleavermissile"],
            SFlag.SkillshotLine,
        )
    ],
    "bard": [
        Spell("bardq", ["bardqmissile"], SFlag.SkillshotLine),
        Spell("bardr", ["bardrmissile"], SFlag.Area),
    ],
    "diana": [
        Spell(
            "dianaq",
            ["dianaqinnermissile", "dianaqoutermissile", "dianaq"],
            SFlag.Cone | SFlag.Area,
        ),
        Spell("dianaarcarc", ["dianaarcarc"], SFlag.Cone | SFlag.Area),
    ],
    "qiyana": [
        Spell(
            "qiyanaq_rock",
            ["qiyanaq_rock"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell(
            "qiyanaq_grass",
            ["qiyanaq_grass"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell(
            "qiyanaq_water",
            ["qiyanaq_water"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell("qiyanar", ["qiyanarmis"], SFlag.Cone, 0.25, DangerLevels.UseSpell),
        Spell(
            "dianaarcarc",
            ["dianaarcarc"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
    ],
    "ekko": [
        Spell("ekkoq", ["ekkoqmis"], SFlag.Line | SFlag.Area, 0.0, DangerLevels.Easy),
        Spell("ekkow", ["ekkowmis"], SFlag.Area, 0.0, DangerLevels.Fastes),
        Spell("ekkor", ["ekkor"], SFlag.Area, 0.0, DangerLevels.UseSpell),
    ],
    "kogmaw": [
        Spell("kogmawq", ["kogmawq"], SFlag.SkillshotLine),
        Spell("kogmawvoidooze", ["kogmawvoidoozemissile"], SFlag.SkillshotLine),
        Spell("kogmawlivingartillery", ["kogmawlivingartillery"], SFlag.Area),
    ],
    "fizz": [
        Spell(
            "fizzr", ["fizzrmissile"], SFlag.SkillshotLine, 0.0, DangerLevels.UseSpell
        )
    ],
    "vi": [
        Spell("vi-q", ["viqmissile"], SFlag.Line),
        Spell("viq", ["viqmissile"], SFlag.Line),
    ],
    "viktor": [
        Spell("viktorgravitonfield", ["viktordeathraymissile"], SFlag.SkillshotLine)
    ],
    "irelia": [
        Spell("ireliaeparticle", ["ireliaeparticlemissile"], SFlag.Line),
        Spell("ireliaw2", ["ireliaw2"], SFlag.SkillshotLine),
        Spell("ireliar", ["ireliar"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell),
    ],
    "katarina": [Spell("katarinae", [], SFlag.Targeted)],
    "illaoi": [
        Spell("illaoiq", [], SFlag.Line),
        Spell("illaoie", ["illaoiemis"], SFlag.SkillshotLine),
    ],
    "heimerdinger": [
        Spell(
            "heimerdingerwm",
            ["heimerdingerwattack2", "heimerdingerwattack2ult"],
            SFlag.SkillshotLine,
        ),
        Spell("heimerdingere", ["heimerdingerespell"], SFlag.Area),
    ],
    "jarvaniv": [
        Spell("jarvanivdemacianstandard", [], SFlag.Area),
        Spell("jarvanivdragonstrike", [], SFlag.SkillshotLine),
        Spell(
            "jarvanivqe", [], SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall
        ),
    ],
    "janna": [
        Spell("jannaq", ["howlinggalespell"], SFlag.SkillshotLine),
        Spell("howlinggalespell", ["howlinggalespell"], SFlag.SkillshotLine),
    ],
    "jayce": [
        Spell("jayceshockblast", ["jayceshockblastmis"], SFlag.SkillshotLine),
        Spell("jayceqaccel", ["jayceshockblastwallmis"], SFlag.SkillshotLine),
    ],
    "khazix": [
        Spell("khazixw", ["khazixwmissile"], SFlag.SkillshotLine),
        Spell("khazixwlong", ["khazixwmissile"], SFlag.SkillshotLine),
        Spell("khazixe", ["khazixe"], SFlag.Area),
    ],
    "ezreal": [
        Spell("ezrealq", ["ezrealq"], SFlag.SkillshotLine),
        Spell("ezrealw", ["ezrealw"], SFlag.SkillshotLine),
        Spell("ezrealr", ["ezrealr"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell),
    ],
    "kalista": [
        Spell(
            "kalistamysticshot",
            ["kalistamysticshotmis", "kalistamysticshotmistrue"],
            SFlag.SkillshotLine,
        ),
    ],
    "alistar": [
        Spell("pulverize", ["koco_missile"], SFlag.Area),
    ],
    "lissandra": [
        Spell("lissandraq", ["lissandraqmissile"], SFlag.SkillshotLine),
        Spell("lissandraqshards", ["lissandraqshards"], SFlag.SkillshotLine),
        Spell("lissandrae", ["lissandraemissile"], SFlag.SkillshotLine),
    ],
    "galio": [
        Spell("galioq", ["galioqmissile"], SFlag.Area),
        Spell("galioe", [], SFlag.SkillshotLine),
    ],
    "evelynn": [
        Spell("evelynnq", ["evelynnq"], SFlag.SkillshotLine),
        Spell("evelynnr", ["evelynnr"], SFlag.Cone),
    ],
    "graves": [
        Spell(
            "gravesqlinespell",
            ["gravesqlinemis", "gravesqreturn"],
            SFlag.Line | SFlag.CollideChampion | SFlag.CollideWindwall,
        ),
        Spell(
            "gravessmokegrenade",
            ["gravessmokegrenadeboom"],
            SFlag.Area | SFlag.CollideWindwall,
        ),
        Spell(
            "graveschargeshot",
            ["graveschargeshotshot"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("graveschargeshotfxmissile2", ["graveschargeshotfxmissile2"], SFlag.Cone),
    ],
    "leesin": [Spell("blindmonkqone", ["blindmonkqone"], SFlag.SkillshotLine)],
    "leona": [
        Spell(
            "leonazenithblade",
            ["leonazenithblademissile"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell("leonasolarflare", ["leonasolarflare"], SFlag.Area),
    ],
    "leblanc": [
        Spell("leblancslide", ["leblancslide"], SFlag.Area),
        Spell("leblancr", ["leblancslidem"], SFlag.Area),
        Spell("leblance", ["leblancemissile"], SFlag.SkillshotLine),
        Spell("leblancre", ["leblancremissile"], SFlag.SkillshotLine),
        Spell("leblancsoulshacklem", ["leblancsoulshacklem"], SFlag.SkillshotLine),
    ],
    "lucian": [
        Spell("lucianq", ["lucianqmis"], SFlag.SkillshotLine, 0.4, DangerLevels.Fastes),
        Spell("lucianw", ["lucianwmissile"], SFlag.SkillshotLine),
        Spell(
            "lucianrmis",
            ["lucianrmissile", "lucianrmissileoffhand"],
            SFlag.SkillshotLine,
        ),
    ],
    "gragas": [
        Spell("gragasq", ["gragasqmissile"], SFlag.Area),
        Spell("gragasr", ["gragasrboom"], SFlag.Area, 0, DangerLevels.UseSpell),
    ],
    "kled": [
        Spell("kledq", ["kledqmissile"], SFlag.Line),
        Spell("kledriderq", ["kledriderqmissile"], SFlag.Cone),
    ],
    "tristana": [Spell("tristanaw", ["rocketjump"], SFlag.Area)],
    "rengar": [
        Spell("rengare", ["rengaremis"], SFlag.SkillshotLine),
        Spell("rengareemp", ["rengareempmis"], SFlag.SkillshotLine),
    ],
    "ryze": [Spell("ryzeq", ["ryzeq"], SFlag.SkillshotLine)],
    "blitzcrank": [
        Spell(
            "rocketgrab",
            ["rocketgrabmissile"],
            SFlag.SkillshotLine,
            0.0,
            DangerLevels.Fastes,
        ),
    ],
    "corki": [
        Spell("phosphorusbomb", ["phosphorusbombmissile"], SFlag.Area),
        Spell("missilebarrage", ["missilebarragemissile"], SFlag.SkillshotLine),
        Spell("missilebarrage2", ["missilebarragemissile2"], SFlag.SkillshotLine),
    ],
    "varus": [
        Spell("varusq", ["varusqmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("varuse", ["varusemissile"], SFlag.Area),
        Spell("varusr", ["varusrmissile"], SFlag.Line, 0, DangerLevels.UseSpell),
    ],
    "tryndamere": [Spell("slashcast", ["slashcast"], SFlag.SkillshotLine)],
    "twitch": [
        Spell("twitchvenomcask", ["twitchvenomcaskmissile"], SFlag.Area),
        Spell("twitchsprayandprayattack", ["twitchsprayandprayattack"], SFlag.Line),
    ],
    "nocturne": [Spell("nocturneduskbringer", ["nocturneduskbringer"], SFlag.Line)],
    "velkoz": [
        Spell("velkozqmissilesplit", ["velkozqmissilesplit"], SFlag.SkillshotLine),
        Spell("velkozq", ["velkozqmissile"], SFlag.SkillshotLine),
        Spell(
            "velkozqsplitactivate",
            ["velkozqmissilesplit"],
            SFlag.Line | SFlag.CollideWindwall,
        ),
        Spell("velkozw", ["velkozwmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("velkoze", ["velkozemissile"], SFlag.Area),
    ],
    "lux": [
        Spell(
            "luxlightbinding",
            ["luxlightbindingmis", "luxlightbindingdummy"],
            SFlag.SkillshotLine,
        ),
        Spell("luxlightstrikekugel", ["luxlightstrikekugel"], SFlag.Area),
        Spell("luxprismaticwave", ["luxprismaticwave"], SFlag.Area),
        Spell("luxlightstriketoggle", ["luxlightstriketoggle"], SFlag.Area),
        Spell("luxmalicecannon", ["luxmalicecannon"], SFlag.Line),
        Spell("luxr", ["luxr"], SFlag.Area),
    ],
    "nautilus": [
        Spell(
            "nautilusanchordragmissile",
            ["nautilusanchordragmissile"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes | DangerLevels.UseSpell,
        )
    ],
    "malzahar": [Spell("malzaharq", ["malzaharq"], SFlag.SkillshotLine)],
    "skarner": [
        Spell("skarnerfracturemissile", ["skarnerfracturemissile"], SFlag.SkillshotLine)
    ],
    "karthus": [
                Spell("karthuslaywastea1", ["karthuslaywastea1"], SFlag.Area),
                Spell("karthuslaywaste", ["karthuslaywaste"], SFlag.Area),
                Spell("karthuslaywasteextra", ["karthuslaywasteextra"], SFlag.Area),
                Spell("karthuslaywastea2", ["karthuslaywastea2"], SFlag.Area),
                Spell("karthuslaywastea3", ["karthuslaywastea3"], SFlag.Area),
                Spell("karthuslaywastedeada2", ["karthuslaywastedeada2"], SFlag.Area),
                Spell("karthuslaywaste2", ["karthuslaywaste2"], SFlag.Area),
                Spell("karthuslaywastedeada3", ["karthuslaywastedeada3"], SFlag.Area),
                Spell("karthuslaywastedeada1", ["karthuslaywastedeada1"], SFlag.Area),
    ],
    "sejuani": [Spell("sejuanir", ["sejuanirmissile"], SFlag.SkillshotLine)],
    "talon": [
        Spell("talonw", ["talonwmissileone"], SFlag.Line),
        Spell("talonwtwo", ["talonwmissiletwo"], SFlag.Line),
        Spell("talonrakereturn", ["talonwmissiletwo"], SFlag.Line),
    ],
    "ziggs": [
        Spell("ziggsq", ["ziggsqspell", "ziggsqspell2", "ziggsqspell3"], SFlag.Area),
        Spell("ziggsw", ["ziggsw"], SFlag.Area),
        Spell("ziggse", ["ziggse2"], SFlag.Area),
        Spell(
            "ziggsr",
            ["ziggsrboom", "ziggsrboommedium", "ziggsrboomlong", "ziggsrboomextralong"],
            SFlag.Area,
        ),
    ],
    "jhin": [
        Spell("jhinw", ["jhinwmissile"], SFlag.Line),
        Spell("jhine", ["jhinetrap"], SFlag.Area),
        Spell("jhinrshot", ["jhinrshotmis4", "jhinrshotmis"], SFlag.SkillshotLine),
    ],
    "swain": [
        Spell("swainw", ["swainw"], SFlag.Area | SFlag.CollideWindwall),
        Spell(
            "swainshadowgrasp", ["swainshadowgrasp"], SFlag.Area | SFlag.CollideWindwall
        ),
        Spell("swaine", ["swaine"], SFlag.SkillshotLine),
        Spell("swainereturn", ["swainereturnmissile"], SFlag.SkillshotLine),
    ],
    "nasus": [Spell("nasuse", [], SFlag.Area)],
    "nami": [
        Spell("namiq", ["namiqmissile"], SFlag.Area),
        Spell("namir", ["namirmissile"], SFlag.Line | SFlag.CollideWindwall),
    ],
    "nidalee": [
        Spell(
            "javelintoss",
            ["javelintoss"],
            SFlag.SkillshotLine,
            0.25,
            DangerLevels.Fastes,
        ),
        Spell("bushwhack", [], SFlag.Area),
    ],
    "malphite": [Spell("ufslash", ["ufslash"], SFlag.SkillshotLine)],
    "reksai": [Spell("reksaiqburrowed", ["reksaiqburrowedmis"], SFlag.SkillshotLine)],
    "thresh": [
        Spell("threshq", ["threshqmissile"], SFlag.SkillshotLine),
        Spell("thresheflay", ["threshemissile1"], SFlag.SkillshotLine),
    ],
    "morgana": [
        Spell("morganaq", ["morganaq"], SFlag.SkillshotLine),
        Spell("morganaw", [], SFlag.Area),
    ],
    "mordekaiser": [
        Spell("mordekaiserq", [], SFlag.SkillshotLine),
        Spell("mordekaisere", ["mordekaiseremissile"], SFlag.SkillshotLine),
    ],
    "samira": [
        Spell("samiraq", ["samiraq"], SFlag.SkillshotLine),
        Spell("samiraqgun", ["samiraqgun"], SFlag.SkillshotLine),
    ],
    "pantheon": [
        Spell("pantheonq", ["pantheonqmissile"], SFlag.Line | SFlag.CollideWindwall),
        Spell("pantheonr", ["pantheonrmissile"], SFlag.Line),
    ],
    "annie": [
        Spell("anniew", [], SFlag.Cone | SFlag.CollideWindwall),
        Spell("annier", [], SFlag.Area),
    ],
    "hecarim": [
        Spell(
            "hecarimult",
            ["hecarimultmissile"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
        Spell("hecarimrcircle", [], SFlag.Area),
    ],
    "olaf": [
        Spell("olafaxethrowcast", ["olafaxethrow"], SFlag.Line | SFlag.CollideWindwall)
    ],
    "anivia": [
        Spell("flashfrost", ["flashfrostspell"], SFlag.Line | SFlag.CollideWindwall)
    ],
    "zed": [
        Spell("zedq", ["zedqmissile"], SFlag.Line),
        Spell("zedw", ["zedwmissile"], SFlag.Area),
    ],
    "xerath": [
        Spell("xeratharcanopulse", ["xeratharcanopulse"], SFlag.Area),
        Spell("xeratharcanopulsechargup", ["xeratharcanopulsechargup"], SFlag.Area),
        Spell("xeratharcanebarrage2", ["xeratharcanebarrage2"], SFlag.Area),
        Spell(
            "xerathmagespear",
            ["xerathmagespearmissile"],
            SFlag.SkillshotLine | SFlag.CollideWindwall,
        ),
        Spell("xerathr", ["xerathlocuspulse"], SFlag.Area),
    ],
    "urgot": [
        Spell("urgotq", ["urgotqmissile"], SFlag.Area),
        Spell("urgotr", ["urgotr"], SFlag.Line),
    ],
    "poppy": [
        Spell("poppyq", ["poppyq"], SFlag.SkillshotLine | SFlag.CollideWindwall),
        Spell(
            "poppyrspell",
            ["poppyrmissile"],
            SFlag.SkillshotLine | SFlag.CollideWindwall,
            0,
            DangerLevels.VeryDangerous,
        ),
        Spell(
            "poppyrlong",
            ["poppyrmissile"],
            SFlag.SkillshotLine | SFlag.CollideWindwall,
            0,
            DangerLevels.VeryDangerous,
        ),
    ],
    "gnar": [
        Spell("gnarq", ["gnarqmissile"], SFlag.SkillshotLine),
        Spell("gnarqreturn", ["gnarqmissilereturn"], SFlag.SkillshotLine),
        Spell("gnarbigq", ["gnarbigqmissile"], SFlag.SkillshotLine),
        Spell("gnarbigw", ["gnarbigw"], SFlag.SkillshotLine),
        Spell("gnare", ["gnare"], SFlag.Area),
        Spell("gnarbige", ["gnarbige"], SFlag.Area),
        Spell("gnarr", ["gnarr"], SFlag.Area),
    ],
    "senna": [
        Spell("sennaqcast", ["sennaqcast"], SFlag.SkillshotLine),
        Spell("sennaw", ["sennaw"], SFlag.SkillshotLine),
        Spell("sennar", ["sennarwarningmis"], SFlag.Line),
    ],
    "shyvana": [
        Spell("shyvanafireball", ["shyvanafireballmissile"], SFlag.SkillshotLine),
        Spell(
            "shyvanafireballdragon2",
            ["shyvanafireballdragonmissile"],
            SFlag.SkillshotLine,
        ),
    ],
    "singed": [Spell("megaadhesive", ["singedwparticlemissile"], SFlag.Area)],
    "fiora": [Spell("fioraw", ["fiorawmissile"], SFlag.SkillshotLine)],
    "sivir": [
        Spell("sivirq", ["sivirqmissile"], SFlag.SkillshotLine),
        Spell("sivirqreturn", ["sivirqmissilereturn"], SFlag.SkillshotLine),
    ],
    "kaisa": [Spell("kaisaw", ["kaisaw"], SFlag.Line | SFlag.CollideWindwall)],
    "karma": [
        Spell(
            "karmaq",
            ["karmaqmissile", "karmaqmissilemantra"],
            SFlag.SkillshotLine | SFlag.Area,
        ),
        Spell("karmaqmantracircle", [], SFlag.SkillshotLine | SFlag.Area),
    ],
    "braum": [
        Spell("braumq", ["braumqmissile"], SFlag.SkillshotLine),
        Spell(
            "braumrwrapper",
            ["braumrmissile"],
            SFlag.SkillshotLine,
            0,
            DangerLevels.UseSpell,
        ),
    ],
    "soraka": [
        Spell("sorakaq", ["sorakaq"], SFlag.Area),
        Spell("sorakae", ["sorakae"], SFlag.Area),
        Spell("sorakaqmissile", ["sorakaqmissile"], SFlag.Area),
        Spell("sorakaqreturnmissile", ["sorakaqreturnmissile"], SFlag.Area),
        
    ],
    "rakan": [
        Spell("rakanq", ["rakanqmis"], SFlag.SkillshotLine),
        Spell("rakanw", [], SFlag.Area, delay=0.5),
    ],
    "xayah": [
        Spell(
            "xayahq",
            ["xayahq", "xayahqmissile1", "xayahqmissile2"],
            SFlag.Line,
        ),
        Spell(
            "xayahq1",
            ["xayahqmissile1"],
            SFlag.Line,
        ),
        Spell(
            "xayahq2",
            ["xayahqmissile2"],
            SFlag.Line,
        ),
        Spell(
            "xayahe",
            ["xayahemissile"],
            SFlag.Line,
        ),
        Spell(
            "xayahr",
            ["xayahrmissile"],
            SFlag.Line,
        ),
    ],
    "sona": [Spell("sonar", ["sonar"], SFlag.Line | SFlag.CollideWindwall)],
    "akali": [Spell("akalie", ["akaliemis"], SFlag.Line | SFlag.CollideWindwall)],
    "kayle": [Spell("kayleq", ["kayleqmis"], SFlag.SkillshotLine)],
    "taliyah": [
        Spell("taliyahqmis", ["taliyahqmis"], SFlag.SkillshotLine),
        Spell("taliyahr", ["taliyahrmis"], SFlag.SkillshotLine),
    ],
    "yasuo": [
        Spell("yasuoq1wrapper", [], SFlag.SkillshotLine),
        Spell("yasuoq2wrapper", [], SFlag.SkillshotLine),
        Spell("yasuoq3wrapper", ["yasuoq3mis"], SFlag.SkillshotLine),
        Spell("yasuoq3", ["yasuoq3mis"], SFlag.SkillshotLine),
    ],
    "yone": [
        Spell("yoneq3", ["yoneq3missile"], SFlag.SkillshotLine),
    ],
    "yuumi": [Spell("yuumiq", [], SFlag.Cone)],
    "zac": [
        Spell("zacq", ["zacqmissile"], SFlag.SkillshotLine),
        Spell("zace", [], SFlag.Area),
    ],
    "zyra": [
        Spell("zyraq", ["zyraq"], SFlag.Cone),
        Spell("zyraw", ["zyraw"], SFlag.Area),
        Spell("zyrae", ["zyrae"], SFlag.SkillshotLine),
        Spell(
            "zyrapassivedeathmanager", ["zyrapassivedeathmanager"], SFlag.SkillshotLine
        ),
    ],
    "zilean": [
        Spell("zileanq", ["zileanqmissile"], SFlag.Area | SFlag.CollideWindwall)
    ],
    "veigar": [Spell("veigarbalefulstrike", ["veigarbalefulstrikemis"], SFlag.Line),
               Spell("veigarw", ["veigarw"],                            SFlag.Area)],
    "maokai": [Spell("maokaiq", ["maokaiqmissile"], SFlag.SkillshotLine)],
    "orianna": [
        Spell(
            "orianaizunacommand",
            ["orianaizuna"],
            SFlag.Line | SFlag.Area | SFlag.CollideWindwall,
        )
    ],
    "warwick": [
        Spell("warwickr", [], SFlag.Area | SFlag.CollideChampion),
        Spell("warwickrchannel", [], SFlag.Area | SFlag.CollideChampion),
    ],
    "taric": [Spell("tarice", ["tarice"], SFlag.SkillshotLine)],
    "cassiopeia": [
        Spell("cassiopeiar", ["cassiopeiar"], SFlag.Cone),
        Spell("cassiopeiaq", ["cassiopeiaq"], SFlag.Area),
    ],
    "viego": [
        Spell("viegoq", [], SFlag.Line | SFlag.CollideWindwall),
        Spell("viegowcast", ["viegowmis"], SFlag.Line | SFlag.CollideWindwall),
        Spell("viegorr", [], SFlag.Area),
    ],
    "syndra": [
        Spell("syndraqspell", ["syndraqspell"], SFlag.Area),
        Spell("syndraespheremissile", ["syndraespheremissile"], SFlag.Line),
    ],
    "draven": [
        Spell("dravendoubleshot", ["dravendoubleshotmissile"], SFlag.SkillshotLine),
        Spell("dravenrcast", ["dravenr"], SFlag.SkillshotLine),
    ],
    "sion": [
        Spell("sione", ["sionemissile"], SFlag.SkillshotLine),
    ],
    "kayn": [
        Spell("kaynq", [], SFlag.CollideWindwall),
        Spell("kaynw", ["kaynw_1234"], SFlag.SkillshotLine),
        Spell("kaynassw", [], SFlag.SkillshotLine),
    ],
    "jinx": [
        Spell("jinxw", ["jinxw"], SFlag.SkillshotLine),
        Spell("jinxwmissile", ["jinxwmissile"], SFlag.SkillshotLine),
        Spell("jinxe", ["jinxehit"], SFlag.Line),
        Spell("jinxr", ["jinxr"], SFlag.SkillshotLine),
    ],
    "seraphine": [
        Spell("seraphineqcast", ["seraphineqinitialmissile"], SFlag.Area),
        Spell("seraphineecast", ["seraphineemissile"], SFlag.SkillshotLine),
        Spell("seraphiner", ["seraphiner"], SFlag.SkillshotLine),
    ],
    "lulu": [
        Spell("luluq", ["luluqmissile"], SFlag.SkillshotLine),
        Spell("luluqpix", ["luluqmissiletwo"], SFlag.SkillshotLine),
    ],
    "rumble": [
        Spell("rumblegrenade", ["rumblegrenademissile"], SFlag.SkillshotLine),
    ],
    "aphelios": [
        Spell("aphelioscalibrumq", ["aphelioscalibrumq"], SFlag.SkillshotLine),
        Spell(
            "apheliosr", ["apheliosrmis"], SFlag.SkillshotLine, 0, DangerLevels.UseSpell
        ),
    ],
    "neeko": [
        Spell("neekoq", ["neekoq"], SFlag.Area),
        Spell("neekoe", ["neekoe"], SFlag.Line | SFlag.CollideWindwall),
    ],
    "allchampions": [
        Spell(
            "arcanecomet",
            ["perks_arcanecomet_mis", "perks_arcanecomet_mis_arc"],
            SFlag.Area,
        )
    ],
    "lillia": [
        Spell("lilliaw", [], SFlag.Area | SFlag.CollideWindwall),
        Spell("lilliae", ["lilliae"], SFlag.SkillshotLine),
        Spell("lilliae2", ["lilliaerollingmissile"], SFlag.SkillshotLine),
    ],
    "tahmkench": [Spell("tahmkenchq", ["tahmkenchqmissile"], SFlag.SkillshotLine)],
    "sett": [
        Spell("settw", ["settw"], SFlag.Cone),
        Spell("sette", [], SFlag.SkillshotLine),
    ],
    "azir": [
        Spell("azirsoldier", ["azirsoldiermissile"], SFlag.Line),
    ],
    "riven": [
        Spell(
            "rivenizunablade",
            [
                "rivenwindslashmissileleft",
                "rivenwindslashmissileright",
                "rivenwindslashmissilecenter",
            ],
            SFlag.Line,
        ),
    ],
    "yuumi": [
        Spell("yuumiq", ["yuumiqskillshot"], SFlag.Line),
        Spell("yuumiqcast", ["yuumiqcast"], SFlag.Line),
    ],
}

def get_range(game, skill_name, slot):
	# convertedSkillName = None
	spelldb_range = 0
	with open("SpellDB.json", "r") as read_file:
		champ = json.loads(read_file.read())
		convertedSkillShot = {k.lower() if isinstance(k, str) else k: v.lower() if isinstance(v, str) else v for k,v in champ[game.player.name.capitalize()][slot].items()}
		if convertedSkillShot['name'] == skill_name:
			spelldb_range = convertedSkillShot['rangeburn']
			# convertedSkillName = search(convertedSkillShot['name'], skill_name)

	return spelldb_range
def draw_prediction_info(game, ui):
    global ChampionSpells, Version

    ui.separator()
    ui.text("Using LPrediction " + Version, Color.PURPLE)
    if is_champ_supported(game.player):
        ui.text(
            game.player.name.upper() + " has skillshot prediction support", Color.GREEN
        )
    else:
        ui.text(
            game.player.name.upper() + " doesnt have skillshot prediction support",
            Color.RED,
        )

    if ui.treenode(f"Supported Champions ({len(ChampionSpells)})"):
        for champ, spells in sorted(ChampionSpells.items()):
            ui.text(
                f"{champ.upper()} {' '*(20 - len(champ))}: {str([spell.name for spell in spells])}"
            )

        ui.treepop()


def clamp_2d(v3, max):
    vx = v3.x
    vy = v3.y
    vz = v3.z
    n = math.sqrt(pow(vx, 2.0) + pow(vz, 2.0))
    f = min(n, max) / n
    return Vec3(f * vx, vy, f * vz)


def get_evade_pos(game, current, br, missile, spell):
    player = game.player
    direction = missile.end_pos.sub(missile.start_pos)
    pos3 = missile.end_pos.add(Vec3(-direction.z, direction.y, direction.x * 1.0))
    pos4 = missile.end_pos.add(Vec3(direction.z * 1.0, direction.y, -direction.x))

    direction2 = pos3.sub(pos4) 
    direction2 = clamp_2d(direction2, br)

    direction3    = Vec3(0, 0, 0)
    direction4    = Vec3(0, 0, 0)
    evadePosition = Vec3(0, 0, 0)
    direction3.x  = -direction2.x
    direction3.y  = -direction2.y
    direction3.z  = -direction2.z
    #bIsLeft = is_left(game.world_to_screen(missile.start_pos), game.world_to_screen(missile.end_pos), game.world_to_screen(player.pos))
    #if bIsLeft:
        #direction4 = direction3
    #else:
        #direction4 = direction2
    #evadePosition = player.pos.add(direction4)
        #points = list()
        #for k in range(-8, 8, 2):
    if is_left(
        game.world_to_screen(missile.start_pos),
        game.world_to_screen(missile.end_pos),
        game.world_to_screen(player.pos),
    ):
        direction4 = direction3
        evadePosition = player.pos.add(direction4)
        #points.append(direction4)
    else:
        direction4 = direction2
        evadePosition = player.pos.add(direction4)
        #points.append(direction4)
    #if len(points) > 0 and not SRinWall(game,evadePosition):
    if not SRinWall(game,evadePosition):
        #points = sorted(points, key=lambda a: player.pos.distance(a))
        return evadePosition
    return None


def is_danger(game, point):
    for missile in game.missiles:
        if not game.player.is_alive or missile.is_ally_to(game.player):
            continue
        if not is_skillshot(missile.name):
            continue
        spell = get_missile_parent_spell(missile.name)
        if not spell:
            continue
        if in_skill_shot(
            game, point, missile, spell, game.player.gameplay_radius
        ) and game.is_point_on_screen(missile.pos):
            return True
        else:
            return False


def is_left(v2a, v2b, v2c) -> bool:
    return ((v2b.x - v2a.x) * (v2c.y - v2a.y) - (v2b.y - v2a.y) * (v2c.x - v2a.x)) > 0


def vector_point_projection_on_line_segment(v1, v2, v):
    cx, cy, ax, ay, bx, by = v.x, v.z, v1.x, v1.z, v2.x, v2.z
    rL = ((cx - ax) * (bx - ax) + (cy - ay) * (by - ay)) / (
        math.pow((bx - ax), 2) + math.pow((by - ay), 2)
    )
    pointLine = Vec3(ax + rL * (bx - ax), 0, ay + rL * (by - ay))
    rS = rL < 0 and 0 or (rL > 1 and 1 or rL)
    isOnSegment = rS == rL
    pointSegment = (
        isOnSegment and pointLine or Vec3(ax + rS * (bx - ax), 0, ay + rS * (by - ay))
    )
    return pointSegment, pointLine, isOnSegment


def point_on_line_segment(v2a, v2b, v2c, double) -> bool:
    epsilon = double if double else 0.001

    if (
        v2c.x - max(v2a.x, v2b.x) > epsilon
        or min(v2a.x, v2b.x) - v2c.x > epsilon
        or v2c.y - max(v2a.y, v2b.y) > epsilon
        or min(v2a.y, v2b.y) - v2c.y > epsilon
    ):
        return False

    if abs(v2b.x - v2a.x) < epsilon:
        return abs(v2a.x - v2c.x) < epsilon or abs(v2b.x - v2c.x) < epsilon

    if abs(v2b.y - v2a.y) < epsilon:
        return abs(v2a.y - v2c.y) < epsilon or abs(v2b.y - v2c.y) < epsilon

    x = v2a.x + (v2c.y - v2a.y) * (v2b.x - v2a.x) / (v2b.y - v2a.y)
    y = v2a.y + (v2c.x - v2a.x) * (v2b.y - v2a.y) / (v2b.x - v2a.x)

    return abs(v2c.x - x) < epsilon or abs(v2c.y - y) < epsilon


def in_skill_shot(game, pos, missile, spell, radius) -> bool:
    pointSegment, pointLine, isOnSegment = vector_point_projection_on_line_segment(
        missile.start_pos, missile.end_pos, pos
    )

    if spell.flags & SFlag.Line or spell.flags & SFlag.SkillshotLine:
        #return isOnSegment and pointSegment.distance(pos) <= (game.player.gameplay_radius * 2)
        return point_on_line_segment(
            game.world_to_screen(missile.start_pos),
            game.world_to_screen(missile.end_pos),
            game.world_to_screen(pos),
            radius +20,
            #(radius * 2) + 25,
        )
        #(
            #isOnSegment
            #and pointSegment.distance(pos) <= (game.player.gameplay_radius * 2) + 20
            #and pointSegment.distance(pos) <= (game.player.gameplay_radius * 2)
        #)

    if spell.flags & SFlag.Area:
        #return isOnSegment and pointSegment.distance(pos) <= (game.player.gameplay_radius * 2)
        return point_on_line_segment(
            game.world_to_screen(missile.start_pos),
            game.world_to_screen(missile.end_pos),
            game.world_to_screen(pos),
            radius +20,
            #(radius * 2),
        )

    return (
        isOnSegment
        and pointSegment.distance(pos)
        <= (missile.width or missile.cast_radius) + radius + game.player.gameplay_radius
    )


def get_skillshot_range(game, skill_name):
    global Spells
    if skill_name not in Spells:
        raise Exception("Not a skillshot")

    # Get the range of the missile if it has a missile
    skillshot = Spells[skill_name]
    if len(skillshot.missiles) > 0:
        return game.get_spell_info(skillshot.missiles[0]).cast_range

    # If it doesnt have a missile get simply the cast_range from the skill
    info = game.get_spell_info(skill_name)
    return info.cast_range * 2.0 if is_skillshot_cone(skill_name) else info.cast_range


def is_skillshot(skill_name):
    global Spells, MissileToSpell
    return skill_name in Spells or skill_name in MissileToSpell


def get_missile_parent_spell(missile_name):
    global MissileToSpell
    return MissileToSpell.get(missile_name, None)


def is_champ_supported(champ):
    global ChampionSpells
    return champ.name in ChampionSpells


def is_skillshot_cone(skill_name):
    if skill_name not in Spells:
        return False
    return Spells[skill_name].flags & SFlag.Cone


def is_last_hitable(game, player, enemy):
    missile_speed = player.basic_missile_speed + 1

    hit_dmg = items.get_onhit_physical(player, enemy) + items.get_onhit_magical(
        player, enemy
    )

    hp = enemy.health
    atk_speed = player.base_atk_speed * player.atk_speed_multi
    t_until_basic_hits = (
        game.distance(player, enemy) / missile_speed
    )  # (missile_speed*atk_speed/player.base_atk_speed)

    for missile in game.missiles:
        if missile.dest_id == enemy.id:
            src = game.get_obj_by_id(missile.src_id)
            if src:
                t_until_missile_hits = game.distance(missile, enemy) / (
                    missile.speed + 1
                )

                if t_until_missile_hits < t_until_basic_hits:
                    hp -= src.base_atk

    return hp - hit_dmg <= 0
def Length(vec):
    return math.sqrt((vec.x * vec.x) + (vec.y * vec.y) + (vec.z * vec.z))

def getLinePrediction(game, spell, caster, target):
    global Spells
    spell_extra = Spells[spell.name]
    if spell.name not in Spells:
        return target.pos
    if (target == 0):
        return None
  
    #if not target.isMoving:
        #return game.world_to_screen(target.pos)

    if len(spell_extra.missiles) > 0:
        missile = game.get_spell_info(spell_extra.missiles[0])
    else:
        missile = spell
  
    if missile.travel_time > 0.0:
        t_missile = missile.travel_time
    else:
      t_missile = (
            (missile.delay + missile.cast_range / missile.speed)
            if len(spell_extra.missiles) > 0 and missile.speed > 0.0
            else 0.0
        )

    t_delay = spell.delay + spell_extra.delay
    t = Length((target.pos.sub(caster.pos))) / missile.speed
    t += t_missile
 
    champ_dir = target.pos.sub(target.prev_pos).normalize()
    navend = target.pos.add(champ_dir.scale((t_delay + t) * target.movement_speed))
    navend.y = 0;

    orientation = navend.normalize()


 

    orientationresult = Vec3(0, 0, 0)
    orientationresult.x = orientationresult.x + target.movement_speed * orientationresult.x * t
    orientationresult.y = orientationresult.y + target.movement_speed * orientationresult.y * t
    orientationresult.z = orientationresult.z + target.movement_speed * orientationresult.z * t

    predictedPosition = Vec3(0, 0, 0)
    predictedPosition.x = target.pos.x + orientationresult.x
    predictedPosition.y = target.pos.y + orientationresult.y
    predictedPosition.z = target.pos.z + orientationresult.z

    predictedPosition.y = target.pos.y;
    predict2d = game.world_to_screen(predictedPosition);
    local2d = game.world_to_screen(target.pos);
    
    if spell_extra.flags & SFlag.Line:
        iterations = int(missile.cast_range / 43.0)
        step = t_missile / iterations

        last_dist = 9999999
        last_target_pos = None
        for i in range(iterations):
            t = i * step
            navend = target.pos.add(
                champ_dir.scale((t_delay + t) * target.movement_speed)
            )
            spell_dir = (
                navend.sub(caster.pos).normalize().scale(t * missile.speed)
            )
            spell_future_pos = caster.pos.add(spell_dir)

            dist = navend.distance(spell_future_pos)
            if not math.isnan(navend.x) and not math.isnan(navend.y) and not math.isnan(navend.z) and(navend.distance(game.player.pos) > missile.cast_range):
                return None
    
            if (navend.x == 0 and navend.z == 0):
                return game.world_to_screen(target.pos)
            if dist < missile.width / 3.0:
                return game.world_to_screen(navend)
                game.draw_line(game.world_to_screen(navend), game.world_to_screen(game.player.pos), 15, Color.RED)
            elif dist > last_dist:
                return game.world_to_screen(last_target_pos)
                game.draw_line(game.world_to_screen(last_target_pos), game.world_to_screen(game.player.pos), 15, Color.BLUE)
            else:
                last_dist = dist
                last_target_pos = navend

        return None
    elif spell_extra.flags & SFlag.Area:

        return game.world_to_screen(target.pos)

# Returns a point where the mouse should click to cast a spells taking into account the targets movement speed
def castpoint_for_collision(game, spell, caster, target):
    global Spells

    # print("spell name: " +spell.name+" - Se cumple?: "+ str(spell.name not in Spells))
    if spell.name not in Spells:
        return None

    # Get extra data for spell that isnt provided by lview
    spell_extra = Spells[spell.name]
    if len(spell_extra.missiles) > 0:
        missile = game.get_spell_info(spell_extra.missiles[0])
    else:
        missile = spell

    t_delay = spell.delay + spell_extra.delay
    if missile.travel_time > 0.0:
        t_missile = missile.travel_time
    else:
        t_missile = (
            (missile.cast_range / missile.speed)
            if len(spell_extra.missiles) > 0 and missile.speed > 0.0
            else 0.0
        )

    # Get direction of target
    target_dir = target.pos.sub(target.prev_pos).normalize()
    if math.isnan(target_dir.x):
        target_dir.x = 0.0
    if math.isnan(target_dir.y):
        target_dir.y = 0.0
    if math.isnan(target_dir.z):
        target_dir.z = 0.0
    # print(f'{target_dir.x} {target_dir.y} {target_dir.z}')

    # If the spell is a line we simulate the main missile to get the collision point
    if spell_extra.flags & SFlag.Line:

        iterations = int(missile.cast_range / 30.0)
        step = t_missile / iterations

        last_dist = 9999999
        last_target_pos = None
        for i in range(iterations):
            t = i * step
            target_future_pos = target.pos.add(
                target_dir.scale((t_delay + t) * target.movement_speed)
            )
            spell_dir = (
                target_future_pos.sub(caster.pos).normalize().scale(t * missile.speed)
            )
            spell_future_pos = caster.pos.add(spell_dir)

            dist = target_future_pos.distance(spell_future_pos)
            # print(dist)
            if dist < missile.width / 2.0:
                return target_future_pos
            elif dist > last_dist:
                return last_target_pos
            else:
                last_dist = dist
                last_target_pos = target_future_pos

        return None

    # If the spell is an area spell we return the position of the player when the spell procs
    elif spell_extra.flags & SFlag.Area:
        return target.pos.add(
            target_dir.scale((t_delay + t_missile) * target.movement_speed)
        )
    else:
        return target.pos

def GetSpellHitTime(game, missile, spell, pos):
    spellPos = game.world_to_screen(missile.pos)
    if spell.flags & SFlag.Line:
        if missile.speed == 0:
            return max(0, spellPos.distance(pos))
        return 1000 * spellPos.distance(pos) / missile.speed
    if spell.flags & SFlag.Area:
        return max(0, spellPos.distance(pos))
    return float("inf")

def CanHeroEvade(game, missile, spell, evadePos):
    self = game.player

    heroPos = game.world_to_screen(self.pos)
    projection = game.world_to_screen(evadePos)

    evadeTime = 0
    spellHitTime = 0
    speed = self.movement_speed
    delay = 0.0

    if spell.flags & SFlag.Line: # or spell.flags & SFlag.SkillshotLine: # or spell.flags & SFlag.Area or spell.flags & SFlag.Cone:
        evadeTime = (
            missile.cast_radius
            - heroPos.distance(projection)
            + self.gameplay_radius
            + 10
        ) / (missile.pos.distance(self.pos) or speed)
        spellHitTime = GetSpellHitTime(game, missile, spell, projection)

    if spell.flags & SFlag.SkillshotLine: #######
        evadeTime = (
            missile.cast_radius
            - heroPos.distance(projection)
            + self.gameplay_radius
            + 10
        ) / (missile.pos.distance(self.pos) or speed)
        spellHitTime = GetSpellHitTime(game, missile, spell, projection) ########

    if spell.flags & SFlag.Area: ########
        evadeTime = (
            missile.cast_radius
            - heroPos.distance(projection)
            + self.gameplay_radius
            + 10
        ) / (missile.pos.distance(self.pos) or speed)
        spellHitTime = GetSpellHitTime(game, missile, spell, projection) ##########
        #evadeTime = (missile.cast_radius - self.pos.distance(missile.end_pos)) / (
        #    missile.pos.distance(self.pos) or speed
        #)
        #spellHitTime = GetSpellHitTime(game, missile, spell, projection)

    if spell.flags & SFlag.Cone: ########
        evadeTime = (
            missile.cast_radius
            - heroPos.distance(projection)
            + self.gameplay_radius
            + 10
        ) / (missile.pos.distance(self.pos) or speed)
        spellHitTime = GetSpellHitTime(game, missile, spell, projection) #######
        #evadeTime = (heroPos.distance(projection) + self.gameplay_radius) / (
        #    missile.pos.distance(self.pos) or speed
        #)
        #spellHitTime = GetSpellHitTime(game, missile, spell, projection)
    return spellHitTime - delay > evadeTime