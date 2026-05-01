package namegen

import (
	"math/rand/v2"
	"strings"
)

var adjectives = []string{
	"Ancient", "Arcane", "Arctic", "Ashen", "Astral", "Atomic", "Bitter",
	"Blazing", "Bleak", "Boiling", "Bold", "Bronze", "Burning", "Calm",
	"Chaos", "Cinder", "Cobalt", "Comet", "Cosmic", "Crescent", "Crimson",
	"Crystal", "Cursed", "Daring", "Dark", "Deadly", "Diamond", "Divine",
	"Doomed", "Dread", "Dreaded", "Drift", "Dusk", "Eerie", "Electric",
	"Elusive", "Ember", "Energetic", "Eternal", "Exotic", "Fading", "Fallen",
	"Feral", "Fierce", "Flame", "Flash", "Flickering", "Frozen", "Furious",
	"Galactic", "Giant", "Glacial", "Gloom", "Golden", "Grim", "Heavy",
	"Hidden", "Hollow", "Howling", "Hyper", "Imperial", "Infinite", "Infernal",
	"Intense", "Iron", "Ivory", "Jagged", "Jolting", "Karmic", "Keen",
	"Kinetic", "Lava", "Legendary", "Lethal", "Livid", "Looming", "Lunar",
	"Manic", "Massive", "Mighty", "Misty", "Molten", "Murky", "Mystic",
	"Mythic", "Nano", "Nebula", "Neon", "Noble", "Nocturnal", "Noxious",
	"Obsidian", "Ominous", "Onyx", "Phantom", "Plasma", "Primal", "Prism",
	"Quantum", "Quick", "Radiant", "Raging", "Reckless", "Rift", "Rogue",
	"Rugged", "Ruthless", "Sacred", "Savage", "Shadow", "Shattered", "Sly",
	"Solar", "Soaring", "Spike", "Stealthy", "Storm", "Swift", "Thunder",
	"Titan", "Toxic", "Trembling", "Turbo", "Ultra", "Umber", "Uncanny",
	"Undying", "Unstable", "Unveiled", "Vile", "Violet", "Vivid", "Void",
	"Vortex", "Wandering", "Warping", "Wicked", "Wild", "Wraith", "Zealous",
	"Zenith", "Brave", "Bright", "Crimson", "Drifting", "Eclipse", "Frosty",
	"Glowing", "Haunted", "Jade", "Kryptic", "Molten", "Nefarious", "Obscure",
	"Perilous", "Pulsing", "Roaming", "Scorched", "Tangled", "Vibrant",
	"Warring", "Xenon", "Abyssal", "Blazed", "Crumbling", "Dazzling", "Errant",
	"Frenzied", "Gritty", "Hollow", "Jaded", "Knotted", "Lurking", "Nimble",
	"Primal", "Rattling", "Sinister", "Torrid", "Unyielding", "Venomous",
	"Withering", "Zealous", "Amber", "Burnished", "Charred", "Desolate",
	"Frantic", "Gilded", "Harrowing", "Icy", "Jagged", "Locked", "Mangled",
	"Necrotic", "Opalescent", "Putrid", "Rabid", "Scorching", "Twisted",
	"Unearthed", "Volatile", "Warped",
}

var nouns = []string{
	"Anvil", "Arrow", "Axe", "Badger", "Basilisk", "Bat", "Bear", "Beetle",
	"Boulder", "Bison", "Blade", "Blaze", "Boar", "Bomb", "Bone", "Brick",
	"Bull", "Bullet", "Cactus", "Cannon", "Centaur", "Chain", "Citadel",
	"Claw", "Cobra", "Comet", "Condor", "Crab", "Crater", "Crow", "Crystal",
	"Dagger", "Demon", "Dire", "Dragon", "Drake", "Eagle", "Eclipse", "Eel",
	"Ember", "Engine", "Falcon", "Fang", "Ferret", "Flint", "Flux", "Forge",
	"Fox", "Frog", "Fungus", "Gargoyle", "Gear", "Ghost", "Glacier", "Golem",
	"Gorilla", "Gravel", "Griffin", "Hammer", "Harpy", "Hawk", "Hydra",
	"Inferno", "Jackal", "Jaguar", "Javelin", "Kraken", "Lance", "Lava",
	"Leopard", "Leviathan", "Lizard", "Lobster", "Magma", "Mantis", "Marble",
	"Mole", "Monolith", "Moon", "Moose", "Moth", "Mummy", "Nebula", "Needle",
	"Nova", "Oak", "Ogre", "Onyx", "Orca", "Osprey", "Otter", "Panther",
	"Phoenix", "Pike", "Piranha", "Plank", "Porcupine", "Prism", "Pulsar",
	"Puma", "Python", "Quartz", "Raven", "Rhino", "Ripple", "Rock", "Rune",
	"Salamander", "Shard", "Shark", "Skull", "Slime", "Snake", "Spark",
	"Sphinx", "Spike", "Squid", "Stone", "Storm", "Talon", "Thunder", "Tiger",
	"Toad", "Tornado", "Troll", "Turret", "Tusk", "Typhoon", "Urchin",
	"Venom", "Viper", "Void", "Volcano", "Vulture", "Wasp", "Weasel",
	"Werewolf", "Wolf", "Worm", "Wyvern", "Yak", "Zombie", "Donut", "Burrito",
	"Taco", "Bagel", "Noodle", "Muffin", "Pretzel", "Waffle", "Biscuit",
	"Dumpling", "Pancake", "Pickle", "Radish", "Turnip", "Cabbage", "Cactus",
	"Mushroom", "Pebble", "Pineapple", "Walnut", "Acorn", "Broom", "Bucket",
	"Candle", "Chisel", "Cog", "Compass", "Crowbar", "Drum", "Funnel",
	"Lantern", "Ladle", "Mallet", "Piston", "Plunger", "Pulley", "Rivet",
	"Shovel", "Sickle", "Spatula", "Spool", "Sprocket", "Stamp", "Staple",
	"Torch", "Trowel", "Valve", "Wrench",
}

var actors = []string{
	"Annihilator", "Aggressor", "Ambusher", "Avenger", "Basher", "Bender",
	"Blaster", "Blitzer", "Bouncer", "Breaker", "Bruiser", "Builder",
	"Carver", "Catcher", "Challenger", "Charger", "Chomper", "Climber",
	"Clubber", "Conqueror", "Controller", "Cruncher", "Crusher", "Dasher",
	"Decimator", "Defender", "Demolisher", "Destroyer", "Digger", "Dominator",
	"Drifter", "Driver", "Eliminator", "Enforcer", "Executor", "Feeder",
	"Fighter", "Flattener", "Flexer", "Flyer", "Forager", "Gladiator",
	"Glider", "Gobbler", "Grinder", "Grappler", "Guardian", "Hacker",
	"Handler", "Harbinger", "Hunter", "Interceptor", "Invader", "Jabber",
	"Juggler", "Juggernaut", "Jumper", "Keeper", "Kicker", "Knocker",
	"Launcher", "Leaper", "Liberator", "Lurker", "Marauder", "Marcher",
	"Masher", "Mercenary", "Miner", "Navigator", "Nomad", "Obliterator",
	"Operator", "Piler", "Pioneer", "Planner", "Plunger", "Pounder",
	"Prowler", "Pulverizer", "Puncher", "Pursuer", "Raider", "Rambler",
	"Rampager", "Ranger", "Ravager", "Roller", "Runner", "Scavenger",
	"Screamer", "Seeker", "Shredder", "Slasher", "Slayer", "Smasher",
	"Stalker", "Stomper", "Striker", "Taker", "Tamer", "Thrower", "Thrasher",
	"Tracker", "Trampler", "Twister", "Undertaker", "Usurper", "Vanquisher",
	"Vaulter", "Vindicator", "Walker", "Wanderer", "Warrior", "Watcher",
	"Whomper", "Wrecker", "Zapper", "Brawler", "Sprinter", "Tumbler",
	"Guzzler", "Rattler", "Mauler", "Chomper", "Snapper", "Howler",
	"Ripper", "Shaker", "Bounder", "Skimmer", "Blazer", "Scorcher",
	"Floater", "Hopper", "Charger", "Lancer", "Skewer", "Splitter",
	"Fanatic", "Devourer", "Plunderer", "Ransacker", "Pillager", "Fuser",
	"Collider", "Impactor", "Deflector", "Absorber", "Emitter", "Projector",
	"Diffuser", "Disruptor", "Extractor", "Propeller", "Resonator", "Reactor",
}

func Generate() string {
	adj := adjectives[rand.IntN(len(adjectives))]
	noun := nouns[rand.IntN(len(nouns))]
	actor := actors[rand.IntN(len(actors))]
	return strings.Join([]string{adj, noun, actor}, " ")
}
