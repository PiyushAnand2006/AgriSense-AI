"""Agricultural knowledge base (educational demo content).

This is the information service behind the disease / pest / treatment and
fertilizer endpoints. All content is general educational guidance that
deliberately contains **no chemical dosages** and must be replaced with a
verified agricultural source before production use.

Entities are exposed with stable slug ids (e.g. "leaf-rust") via the
``*_for_api`` helpers so the REST layer never deals with raw dict shapes.
"""

SOURCE_NOTE = "Educational information — not verified agricultural guidance."


def slugify(name: str) -> str:
    return name.strip().lower().replace(" / ", "-").replace("/", "-").replace(" ", "-")


# --- Seasons (metadata only; crops are database-driven) -----------------------

SEASONS: dict[str, dict[str, str]] = {
    "rabi": {"name": "Rabi", "label": "Winter season (Oct–Mar)"},
    "kharif": {"name": "Kharif / Monsoon", "label": "Monsoon season (Jun–Oct)"},
    "zaid": {"name": "Zaid / Summer", "label": "Summer season (Mar–Jun)"},
}


# --- Crop disease catalogs ---------------------------------------------------

CROP_DISEASES: dict[str, list[str]] = {
    # --- Rabi Crops ---
    "wheat": ["Leaf Rust", "Powdery Mildew", "Loose Smut"],
    "chickpea": ["Fusarium Wilt", "Ascochyta Blight"],
    "mustard": ["Alternaria Blight", "White Rust"],
    "potato": ["Early Blight", "Late Blight"],
    "lentil": ["Fusarium Wilt", "Ascochyta Blight"],
    "apple": ["Apple Scab", "Powdery Mildew", "Early Blight"],
    # --- Kharif Crops ---
    "rice": ["Rice Blast", "Brown Spot", "Sheath Blight", "Bacterial Leaf Blight"],
    "maize": ["Turcicum Leaf Blight", "Downy Mildew", "Common Rust"],
    "cotton": ["Bacterial Blight", "Alternaria Blight", "Fusarium Wilt"],
    "jute": ["Stem Rot", "Anthracnose"],
    "pigeonpeas": ["Fusarium Wilt", "Sterility Mosaic Virus"],
    "blackgram": ["Yellow Mosaic Virus", "Cercospora Leaf Spot"],
    "mothbeans": ["Yellow Mosaic Virus", "Cercospora Leaf Spot"],
    # --- Zaid Crops ---
    "watermelon": ["Anthracnose", "Downy Mildew"],
    "cucumber": ["Downy Mildew", "Cucumber Mosaic Virus"],
    "muskmelon": ["Powdery Mildew", "Fusarium Wilt"],
    "moong": ["Yellow Mosaic Virus", "Cercospora Leaf Spot"],
    "banana": ["Panama Wilt", "Sigatoka Leaf Spot", "Anthracnose"],
    "mango": ["Powdery Mildew", "Anthracnose"],
    "papaya": ["Papaya Ring Spot Virus", "Anthracnose", "Powdery Mildew"],
    "pomegranate": ["Bacterial Blight", "Anthracnose"],
    "orange": ["Citrus Canker", "Anthracnose"],
    "grapes": ["Powdery Mildew", "Downy Mildew", "Anthracnose"],
    "coconut": ["Bud Rot", "Stem Bleeding", "Fusarium Wilt"],
    "coffee": ["Coffee Leaf Rust", "Anthracnose"],
}

# --- Pest catalogs -----------------------------------------------------------

CROP_PESTS: dict[str, list[str]] = {
    # --- Rabi Crops ---
    "wheat": ["Aphid", "Termite"],
    "chickpea": ["Pod Borer", "Cutworm"],
    "mustard": ["Mustard Aphid", "Sawfly"],
    "potato": ["Tuber Moth", "Aphid"],
    "lentil": ["Pod Borer", "Aphid"],
    "apple": ["Woolly Apple Aphid", "Red Spider Mite"],
    # --- Kharif Crops ---
    "rice": ["Yellow Stem Borer", "Brown Planthopper", "Rice Hispa"],
    "maize": ["Fall Armyworm", "Cutworm", "Stem Borer"],
    "cotton": ["Pink Bollworm", "Whitefly", "Cotton Aphid"],
    "jute": ["Jute Semilooper", "Red Spider Mite", "Whitefly"],
    "pigeonpeas": ["Pod Borer", "Pod Fly"],
    "blackgram": ["Whitefly", "Pod Borer"],
    "mothbeans": ["Whitefly", "Pod Borer"],
    # --- Zaid Crops ---
    "watermelon": ["Red Pumpkin Beetle", "Fruit Fly"],
    "cucumber": ["Whitefly", "Red Spider Mite"],
    "muskmelon": ["Fruit Fly", "Whitefly"],
    "moong": ["Whitefly", "Pod Borer"],
    "banana": ["Banana Pseudostem Borer", "Aphid"],
    "mango": ["Mango Hopper", "Fruit Fly"],
    "papaya": ["Fruit Fly", "Red Spider Mite"],
    "pomegranate": ["Fruit Borer", "Anar Butterfly", "Fruit Fly"],
    "orange": ["Citrus Psylla", "Fruit Fly"],
    "grapes": ["Flea Beetle", "Red Spider Mite", "Fruit Fly"],
    "coconut": ["Rhinoceros Beetle", "Red Palm Weevil", "Termite"],
    "coffee": ["Coffee Berry Borer", "White Stem Borer", "Aphid"],
}


def _reverse_catalog(catalog: dict[str, list[str]]) -> dict[str, list[str]]:
    reversed_map: dict[str, list[str]] = {}
    for crop_id, names in catalog.items():
        for name in names:
            reversed_map.setdefault(name, []).append(crop_id)
    return reversed_map


DISEASE_CROPS = _reverse_catalog(CROP_DISEASES)
PEST_CROPS = _reverse_catalog(CROP_PESTS)

# --- Disease knowledge (educational demo) --------------------------------------

DISEASE_KNOWLEDGE: dict[str, dict] = {
    "Leaf Rust": {
        "symptoms": [
            "Small orange-brown pustules on leaves",
            "Pustules feel dusty when rubbed",
            "Yellowing and early drying of leaves",
        ],
        "recommended_action": "Inspect the field and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for a suitable fungicide program. Remove heavily infected plant debris.",
        "organic_alternatives": "Educational guidance: improve air circulation, remove infected leaves, and consider approved bio-fungicide options.",
        "prevention": [
            "Use rust-tolerant varieties where available",
            "Avoid excess nitrogen",
            "Rotate crops between seasons",
        ],
    },
    "Powdery Mildew": {
        "symptoms": [
            "White powdery spots on upper leaf surfaces",
            "Leaves may curl and dry out",
            "Reduced plant vigor in dry spells",
        ],
        "recommended_action": "Improve airflow and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for suitable treatment options.",
        "organic_alternatives": "Educational guidance: spray-approved sulfur or potassium bicarbonate formulations may help when applied early.",
        "prevention": ["Avoid overcrowded sowing", "Remove crop residues", "Monitor during dry, humid weather"],
    },
    "Loose Smut": {
        "symptoms": [
            "Black powdery spore masses replacing grain heads",
            "Infected heads emerge earlier than healthy ones",
        ],
        "recommended_action": "Remove and destroy infected spikes immediately.",
        "treatment": "Educational guidance: there is no in-field cure; manage through certified seed and seed treatment before sowing.",
        "organic_alternatives": "Educational guidance: use certified disease-free seed.",
        "prevention": ["Use certified treated seed", "Rotate crops", "Remove smutted heads before they burst"],
    },
    "Fusarium Wilt": {
        "symptoms": [
            "Yellowing and drooping of lower leaves",
            "Browning of vascular tissue when stem is cut",
            "Plants wilt during warm parts of the day",
        ],
        "recommended_action": "Remove affected plants and avoid spreading soil.",
        "treatment": "Educational guidance: no effective in-field cure; focus on soil health and resistant varieties.",
        "organic_alternatives": "Educational guidance: soil solarization and bio-control agents such as Trichoderma may help suppress the pathogen.",
        "prevention": ["Use resistant varieties", "Practice 3-4 year crop rotation", "Avoid waterlogging"],
    },
    "Ascochyta Blight": {
        "symptoms": [
            "Brown lesions with concentric rings on leaves and pods",
            "Stem girdling at affected nodes",
            "Pod and seed discoloration",
        ],
        "recommended_action": "Begin appropriate disease management and avoid working in wet fields.",
        "treatment": "Educational guidance: consult your local agricultural officer for a suitable fungicide program.",
        "organic_alternatives": "Educational guidance: remove infected debris and use certified seed.",
        "prevention": ["Sow certified seed", "Avoid dense canopy", "Rotate with non-host crops"],
    },
    "Alternaria Blight": {
        "symptoms": [
            "Dark concentric ring spots on leaves",
            "Blackening of pods and stems",
            "Premature leaf drop",
        ],
        "recommended_action": "Remove infected plant material and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for a suitable fungicide program.",
        "organic_alternatives": "Educational guidance: improve drainage and remove crop residues.",
        "prevention": ["Timely sowing", "Balanced fertilization", "Destroy crop residues after harvest"],
    },
    "White Rust": {
        "symptoms": [
            "White creamy pustules on underside of leaves",
            "Swollen and distorted stems and flowers",
        ],
        "recommended_action": "Remove infected plant parts and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for suitable treatment options.",
        "organic_alternatives": "Educational guidance: remove infected parts and improve field drainage.",
        "prevention": ["Rotate crops", "Avoid excess irrigation", "Use clean seed"],
    },
    "Early Blight": {
        "symptoms": [
            "Brown spots with target-like rings on older leaves",
            "Yellow halos around lesions",
        ],
        "recommended_action": "Remove infected lower leaves and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for a suitable fungicide program.",
        "organic_alternatives": "Educational guidance: mulching and drip irrigation reduce leaf wetness.",
        "prevention": ["Avoid overhead irrigation", "Maintain potassium nutrition", "Rotate crops"],
    },
    "Late Blight": {
        "symptoms": [
            "Water-soaked dark lesions on leaves",
            "White fungal growth under leaves in humid weather",
            "Rapid crop collapse in cool wet conditions",
        ],
        "recommended_action": "Act quickly — late blight spreads fast in cool, wet weather.",
        "treatment": "Educational guidance: consult your local agricultural officer immediately for area-appropriate management.",
        "organic_alternatives": "Educational guidance: remove and destroy infected plants; improve drainage.",
        "prevention": ["Monitor fields after cool rainy spells", "Use healthy certified seed tubers", "Avoid dense planting"],
    },
    "Anthracnose": {
        "symptoms": [
            "Sunken water-soaked lesions on fruits",
            "Pinkish spore masses in lesions",
            "Leaf spotting and vine dieback",
        ],
        "recommended_action": "Remove infected fruits and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for a suitable fungicide program.",
        "organic_alternatives": "Educational guidance: remove diseased fruits, avoid overhead watering.",
        "prevention": ["Use disease-free seed", "Rotate fields", "Avoid wounding fruits at harvest"],
    },
    "Downy Mildew": {
        "symptoms": [
            "Yellow angular patches on upper leaves",
            "Purple-grey fuzz on leaf undersides",
            "Stunted vine growth",
        ],
        "recommended_action": "Improve airflow and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for suitable treatment options.",
        "organic_alternatives": "Educational guidance: remove infected leaves; avoid evening irrigation.",
        "prevention": ["Water in the morning", "Space plants for airflow", "Rotate crops"],
    },
    "Cucumber Mosaic Virus": {
        "symptoms": [
            "Mottled light-dark green mosaic on leaves",
            "Curled, distorted leaves",
            "Stunted growth and misshapen fruit",
        ],
        "recommended_action": "Remove infected plants — viruses cannot be cured in the field.",
        "treatment": "Educational guidance: no cure; remove infected plants and control aphid vectors.",
        "organic_alternatives": "Educational guidance: use reflective mulches and remove weeds that host the virus.",
        "prevention": ["Control aphids and whiteflies", "Remove weeds", "Use resistant varieties"],
    },
    "Yellow Mosaic Virus": {
        "symptoms": [
            "Bright yellow-green mosaic pattern on leaves",
            "Pod deformation and reduced seed size",
        ],
        "recommended_action": "Remove infected plants and control whitefly vectors.",
        "treatment": "Educational guidance: no cure; focus on vector control and removal of infected plants.",
        "organic_alternatives": "Educational guidance: yellow sticky traps help monitor and reduce whitefly pressure.",
        "prevention": ["Control whiteflies", "Use resistant varieties", "Remove weed hosts"],
    },
    "Cercospora Leaf Spot": {
        "symptoms": [
            "Small circular grey-brown spots with dark borders",
            "Spots merge causing leaf blight",
        ],
        "recommended_action": "Remove infected debris and begin appropriate disease management.",
        "treatment": "Educational guidance: consult your local agricultural officer for suitable treatment options.",
        "organic_alternatives": "Educational guidance: crop rotation and residue removal reduce inoculum.",
        "prevention": ["Rotate crops", "Avoid overhead irrigation", "Use clean seed"],
    },
    "Rice Blast": {
        "symptoms": [
            "Spindle/diamond-shaped lesions with grey centres and dark brown margins",
            "Neck rot / blackening of node causing lodging and empty panicles",
            "Seedling blighting in nursery beds",
        ],
        "recommended_action": "Avoid excess nitrogen fertilizer and scout fields early in foggy or humid weather.",
        "treatment": "Educational guidance: consult your local agricultural extension officer for recommended blast fungicide schedule.",
        "organic_alternatives": "Educational guidance: treat seeds with Pseudomonas fluorescens or Trichoderma viride.",
        "prevention": ["Use blast-tolerant rice varieties", "Avoid late transplanting", "Balanced split nitrogen doses"],
    },
    "Brown Spot": {
        "symptoms": [
            "Oval brown spots with grey or yellow halo on leaves and glumes",
            "Discolored and unfilled paddy grains",
        ],
        "recommended_action": "Correct soil nutrient deficiency, particularly potassium and silicon.",
        "treatment": "Educational guidance: consult local agricultural extension for foliar fungicide options.",
        "organic_alternatives": "Educational guidance: soak seeds in bio-agent slurry prior to sowing.",
        "prevention": ["Seed treatment with bio-agents", "Balanced NPK and potash application", "Use certified disease-free seed"],
    },
    "Sheath Blight": {
        "symptoms": [
            "Greenish-grey oval water-soaked lesions on leaf sheath near water line",
            "Lesions enlarge and merge with dark brown borders",
            "Panicle choking and lodging in severe attack",
        ],
        "recommended_action": "Maintain optimal hill spacing to improve canopy airflow.",
        "treatment": "Educational guidance: consult your local extension officer for recommended sheath blight management.",
        "organic_alternatives": "Educational guidance: apply neem cake to soil and spray bio-fungicide formulations.",
        "prevention": ["Avoid dense transplanting", "Apply recommended split potassium", "Destroy weed hosts around bunds"],
    },
    "Bacterial Leaf Blight": {
        "symptoms": [
            "Water-soaked stripes along leaf margins turning yellow-white with wavy borders",
            "Bacterial ooze droplets on leaves in early morning",
            "Kresek seedling wilting",
        ],
        "recommended_action": "Drain standing water from paddy field and withhold top-dressed urea.",
        "treatment": "Educational guidance: apply copper-based bactericide or validamycin as advised by agricultural officers.",
        "organic_alternatives": "Educational guidance: spray 5% neem seed kernel extract (NSKE) or bio-bactericide.",
        "prevention": ["Use BLB-resistant varieties", "Avoid clipping seedling tips at transplanting", "Provide balanced potash"],
    },
    "Turcicum Leaf Blight": {
        "symptoms": [
            "Long elliptical grayish-green or tan lesions on maize leaves",
            "Lesions coalesce causing premature burning of foliage",
        ],
        "recommended_action": "Scout maize fields before tasseling and manage crop residue.",
        "treatment": "Educational guidance: consult local extension officer for foliar fungicide recommendations.",
        "organic_alternatives": "Educational guidance: spray Trichoderma harzianum or bio-formulations.",
        "prevention": ["Plant resistant maize hybrids", "Destroy infected stubble", "Crop rotation"],
    },
    "Common Rust": {
        "symptoms": [
            "Small powdery brownish-red pustules on both leaf surfaces",
            "Pustules turn dark brownish-black late in the season",
        ],
        "recommended_action": "Monitor cool humid pockets and spray upon disease threshold.",
        "treatment": "Educational guidance: consult agricultural extension for suitable rust fungicides.",
        "organic_alternatives": "Educational guidance: maintain optimal plant spacing and balanced fertility.",
        "prevention": ["Use rust-tolerant hybrids", "Timely planting"],
    },
    "Bacterial Blight": {
        "symptoms": [
            "Angular water-soaked leaf spots bordered by veinlets",
            "Black arm lesions on stems and bolls",
            "Premature boll shedding in cotton and oily spots on pomegranate",
        ],
        "recommended_action": "Prune infected twigs and avoid sprinkler irrigation.",
        "treatment": "Educational guidance: spray copper bactericide combined with streptocycline as recommended.",
        "organic_alternatives": "Educational guidance: spray 1% Bordeaux mixture or cow dung filtrate.",
        "prevention": ["Acid-delinted certified seed", "Hot water seed treatment", "Field sanitation"],
    },
    "Stem Rot": {
        "symptoms": [
            "Brown water-soaked patches on lower stem near ground level",
            "Softening, shredding, and blackening of stem fibers",
        ],
        "recommended_action": "Improve field drainage and avoid water stagnation.",
        "treatment": "Educational guidance: drench base with approved protective fungicide.",
        "organic_alternatives": "Educational guidance: soil application of Trichoderma enriched in farmyard manure.",
        "prevention": ["Avoid waterlogging", "Rotate with non-susceptible crops", "Crop residue burning/removal"],
    },
    "Sterility Mosaic Virus": {
        "symptoms": [
            "Bushy pale green leaves with mild mosaic mottling",
            "Complete suppression of flowering and pod setting (sterility)",
        ],
        "recommended_action": "Uproot infected plants early and control eriophyid mite vectors.",
        "treatment": "Educational guidance: spray acaricides/miticides to control vector population.",
        "organic_alternatives": "Educational guidance: spray wettable sulfur or neem oil formulations.",
        "prevention": ["Use SMD-resistant arhar varieties", "Control mite vectors early in season"],
    },
    "Panama Wilt": {
        "symptoms": [
            "Yellowing of lower leaves of banana progressing upward",
            "Longitudinal splitting of pseudostem base",
            "Reddish-brown vascular discoloration inside corm",
        ],
        "recommended_action": "Uproot and destroy infected banana mats; do not take suckers from diseased fields.",
        "treatment": "Educational guidance: no chemical in-field cure; focus on disease-free tissue culture and soil biocontrol.",
        "organic_alternatives": "Educational guidance: enrich soil with Trichoderma viride and Pseudomonas.",
        "prevention": ["Plant certified disease-free tissue culture plants", "Improve drainage", "Crop rotation with paddy"],
    },
    "Sigatoka Leaf Spot": {
        "symptoms": [
            "Yellow-brown streaks on leaves turning into dark brown spots with grey centers",
            "Extensive leaf necrosis and premature ripening of banana bunches",
        ],
        "recommended_action": "De-leaf heavily infected leaves and burn them outside the orchard.",
        "treatment": "Educational guidance: spray systemic and contact fungicides in rotation with mineral oil.",
        "organic_alternatives": "Educational guidance: spray neem oil and potassium silicate solutions.",
        "prevention": ["Ensure proper orchard drainage", "Maintain wider plant spacing", "Remove diseased trash"],
    },
    "Papaya Ring Spot Virus": {
        "symptoms": [
            "Prominent yellow mosaic and shoe-stringing of papaya leaves",
            "Concentric rings and water-soaked oily streaks on fruits and petioles",
        ],
        "recommended_action": "Rogue out infected plants immediately to protect the remaining orchard.",
        "treatment": "Educational guidance: viral disease has no cure; control aphid vectors using approved sprays.",
        "organic_alternatives": "Educational guidance: grow border crops (maize/sorghum) and apply silver reflective mulch.",
        "prevention": ["Border barrier cropping", "Vector management", "Use ring-spot tolerant hybrids"],
    },
    "Citrus Canker": {
        "symptoms": [
            "Raised corky brown lesions with bright yellow halo on leaves, twigs, and fruits",
            "Premature fruit drop and unmarketable blemished peel",
        ],
        "recommended_action": "Prune cankered twigs before monsoon flush and spray protective copper.",
        "treatment": "Educational guidance: spray copper oxychloride with streptocycline during new flush emergence.",
        "organic_alternatives": "Educational guidance: spray 1% Bordeaux mixture and neem oil.",
        "prevention": ["Plant canker-resistant citrus cultivars", "Erect windbreaks around orchard", "Prune diseased shoots"],
    },
    "Apple Scab": {
        "symptoms": [
            "Olive-green to velvety dark spots on apple leaves and sepals",
            "Corky cracked scab lesions on mature fruit surface",
        ],
        "recommended_action": "Collect and destroy fallen leaves in autumn to reduce overwintering spores.",
        "treatment": "Educational guidance: follow state horticulture university spray schedule for scab management.",
        "organic_alternatives": "Educational guidance: liquid lime sulfur or sulfur wettable powder during early green tip.",
        "prevention": ["Prune tree canopy for air movement", "Spray urea (5%) on fallen autumn leaves to speed decomposition"],
    },
    "Bud Rot": {
        "symptoms": [
            "Yellowing and withering of central coconut spindle leaf",
            "Soft foul-smelling rot of the growing bud leading to palm death",
        ],
        "recommended_action": "Clean affected crowns and apply protective paste immediately.",
        "treatment": "Educational guidance: apply copper oxychloride or Bordeaux paste on cleaned bud area.",
        "organic_alternatives": "Educational guidance: placement of perforated sachets containing Mancozeb or biocontrol agent in crown.",
        "prevention": ["Pre-monsoon crown cleaning and protective Bordeaux spray", "Improve grove aeration"],
    },
    "Stem Bleeding": {
        "symptoms": [
            "Exudation of dark reddish-brown liquid from longitudinal cracks on coconut trunk",
            "Rotting of underlying cortical tissues",
        ],
        "recommended_action": "Chisel out affected rotting bark tissue and apply coal tar or Bordeaux paste.",
        "treatment": "Educational guidance: root feeding with approved systemic fungicides.",
        "organic_alternatives": "Educational guidance: application of neem cake and Trichoderma to palm root basin.",
        "prevention": ["Avoid mechanical injury to trunk", "Ensure balanced potassium nutrition and drainage"],
    },
    "Coffee Leaf Rust": {
        "symptoms": [
            "Yellowish-orange powdery circular spots on the underside of coffee leaves",
            "Severe defoliation and dieback of bearing branches",
        ],
        "recommended_action": "Maintain optimal shade tree regulation and spray protective copper.",
        "treatment": "Educational guidance: pre-monsoon and post-monsoon spray of 0.5% Bordeaux mixture or systemic triazoles.",
        "organic_alternatives": "Educational guidance: spray bio-fungicide formulations and regulate shade canopy.",
        "prevention": ["Plant rust-resistant coffee cultivars (Selection 795 / Cauvery)", "Proper shade and pruning"],
    },
}

_DEFAULT_DISEASE = {
    "symptoms": ["General stress symptoms"],
    "recommended_action": "Monitor the crop and consult local advisory services.",
    "treatment": "Educational guidance: consult your local agricultural officer.",
    "organic_alternatives": "Educational guidance: maintain field hygiene and balanced nutrition.",
    "prevention": ["Regular field scouting", "Balanced irrigation"],
}


def get_disease_knowledge(disease: str) -> dict:
    return DISEASE_KNOWLEDGE.get(disease, _DEFAULT_DISEASE)


def list_diseases() -> list[dict]:
    """All known diseases with ids and affected crops, API-shaped."""
    return [
        {
            "id": slugify(name),
            "name": name,
            "crop_ids": DISEASE_CROPS.get(name, []),
            "knowledge": DISEASE_KNOWLEDGE.get(name, _DEFAULT_DISEASE),
        }
        for name in DISEASE_KNOWLEDGE
    ]


def get_disease(disease_id: str) -> dict | None:
    for entry in list_diseases():
        if entry["id"] == disease_id:
            return entry
    return None


def diseases_for_crop(crop_id: str) -> list[dict]:
    names = CROP_DISEASES.get(crop_id, [])
    return [entry for entry in list_diseases() if entry["name"] in names]


# --- Pest knowledge (educational demo) -------------------------------------------

PEST_KNOWLEDGE: dict[str, dict] = {
    "Aphid": {
        "symptoms": ["Clusters of small soft-bodied insects on shoots", "Sticky honeydew and sooty mold", "Curling of young leaves"],
        "recommended_action": "Monitor population growth; natural enemies often control light infestations.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: ladybird beetles and neem-based sprays are commonly used supports.",
        "prevention": ["Encourage natural enemies", "Avoid excess nitrogen", "Monitor shoots weekly"],
    },
    "Mustard Aphid": {
        "symptoms": ["Curling leaves and sticky shoots", "Stunted pods", "Sooty mold on surfaces"],
        "recommended_action": "Scout fields twice weekly during flowering and act on thresholds.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: neem-based formulations and predator conservation.",
        "prevention": ["Early sowing", "Aphid-tolerant varieties", "Avoid late irrigation"],
    },
    "Termite": {
        "symptoms": ["Wilting plants with damaged roots", "Hollowed stems near soil", "Dead patches in field"],
        "recommended_action": "Remove termite mounds and crop stubble that harbor colonies.",
        "treatment": "Educational guidance: consult your local agricultural officer for safe soil-management practices.",
        "organic_alternatives": "Educational guidance: remove stubble between seasons; flood nests where practical.",
        "prevention": ["Remove crop residues", "Avoid raw manure near sowing", "Deep summer ploughing"],
    },
    "Pod Borer": {
        "symptoms": ["Holes bored into pods", "Larvae inside pods", "Head-feeding in crops"],
        "recommended_action": "Hand-pick larvae in small fields; use pheromone traps for monitoring.",
        "treatment": "Educational guidance: consult your local agricultural officer for integrated pest management options.",
        "organic_alternatives": "Educational guidance: bird perches, pheromone traps and Bt-based bio-pesticides are common supports.",
        "prevention": ["Pheromone trap monitoring", "Intercropping with non-host crops", "Timely sowing"],
    },
    "Cutworm": {
        "symptoms": ["Seedlings cut at soil level at night", "Larvae hidden in soil during day"],
        "recommended_action": "Search soil near cut seedlings in the morning and remove larvae.",
        "treatment": "Educational guidance: consult your local agricultural officer for safe control options.",
        "organic_alternatives": "Educational guidance: light traps and hand-picking in small fields.",
        "prevention": ["Remove weeds before sowing", "Deep ploughing exposes larvae"],
    },
    "Sawfly": {
        "symptoms": ["Leaf margins eaten by larvae", "Defoliation of lower leaves"],
        "recommended_action": "Remove larvae manually in small infestations.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: natural parasites often keep sawfly in check; avoid broad spraying.",
        "prevention": ["Early sowing", "Field sanitation"],
    },
    "Tuber Moth": {
        "symptoms": ["Tunnels in tubers", "Frass in stored potatoes", "Leaf mining in foliage"],
        "recommended_action": "Sort and remove infested tubers before storage.",
        "treatment": "Educational guidance: consult your local agricultural officer for safe storage treatment.",
        "organic_alternatives": "Educational guidance: cool, dark, well-ventilated storage reduces damage.",
        "prevention": ["Harvest promptly", "Avoid tuber exposure in field", "Sanitize storage"],
    },
    "Red Pumpkin Beetle": {
        "symptoms": ["Holes in leaves and flowers", "Beetles visible on vines in morning"],
        "recommended_action": "Hand-pick beetles in small fields during cool morning hours.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: neem-based sprays and fine netting over young plants.",
        "prevention": ["Use netting on nursery beds", "Remove crop residues", "Early sowing"],
    },
    "Fruit Fly": {
        "symptoms": ["Punctures on fruit skin", "Maggots inside fruits", "Premature fruit drop"],
        "recommended_action": "Remove and destroy fallen infested fruits.",
        "treatment": "Educational guidance: consult your local agricultural officer for area-appropriate management.",
        "organic_alternatives": "Educational guidance: pheromone/cuelure traps and fruit bagging are common supports.",
        "prevention": ["Trap monitoring", "Remove fallen fruits", "Timely harvest"],
    },
    "Whitefly": {
        "symptoms": ["Tiny white insects fly up when disturbed", "Yellowing leaves and sticky honeydew", "Sooty mold"],
        "recommended_action": "Use yellow sticky traps and monitor the undersides of leaves.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: yellow sticky traps and neem-based sprays are common supports.",
        "prevention": ["Sticky traps from sowing", "Avoid dense canopy", "Remove weed hosts"],
    },
    "Red Spider Mite": {
        "symptoms": ["Fine yellow stippling on leaves", "Silken webs on undersides", "Bronzing in dry weather"],
        "recommended_action": "Increase humidity with light irrigation; mites thrive in dry dust.",
        "treatment": "Educational guidance: consult your local agricultural officer before any chemical control.",
        "organic_alternatives": "Educational guidance: strong water sprays on leaf undersides suppress light populations.",
        "prevention": ["Avoid water stress", "Reduce dust on leaves", "Monitor in dry spells"],
    },
    "Yellow Stem Borer": {
        "symptoms": [
            "Dead hearts (drying of central shoot) in vegetative stage",
            "White ears (empty upright white panicles) at heading stage",
            "Bore holes with frass on lower stem nodes",
        ],
        "recommended_action": "Set up light traps and pheromone traps (8/ha) to monitor moth emergence.",
        "treatment": "Educational guidance: apply recommended systemic granular or spray insecticides at ETL (1 egg mass/sq.m).",
        "organic_alternatives": "Educational guidance: release egg parasitoid Trichogramma japonicum (100,000/ha).",
        "prevention": ["Clip seedling tips before transplanting to remove egg masses", "Avoid excess nitrogen", "Deep summer ploughing"],
    },
    "Brown Planthopper": {
        "symptoms": [
            "Hopper burn — circular patches of drying and lodged rice plants in the center of the field",
            "Sooty mold growth on stem bases due to honeydew secretion",
        ],
        "recommended_action": "Create alleyways every 2-3 meters and drain standing water for 3-4 days.",
        "treatment": "Educational guidance: spray recommended planthopper insecticides directed strictly at the base of plants.",
        "organic_alternatives": "Educational guidance: conserve spiders and mirid bugs; avoid prophylactic broad-spectrum sprays.",
        "prevention": ["Alternate wetting and drying (AWD)", "Avoid excessive synthetic pyrethroids which cause resurgence", "Resistant varieties"],
    },
    "Rice Hispa": {
        "symptoms": [
            "White parallel streaks along leaves due to leaf scraping by adult spiny beetles",
            "Mined blistering on upper leaf surfaces caused by grub burrowing",
        ],
        "recommended_action": "Sweep net adults from field borders and spray along early infestation patches.",
        "treatment": "Educational guidance: consult local extension officer for hispa management.",
        "organic_alternatives": "Educational guidance: clip damaged leaf tips containing grubs and bury them.",
        "prevention": ["Keep field bunds free from weed hosts", "Avoid excess nitrogen"],
    },
    "Fall Armyworm": {
        "symptoms": [
            "Pinholes and window-pane feeding on young maize whorls",
            "Heavy sawdust-like fecal frass in central whorl",
            "Damaged tassels and ears",
        ],
        "recommended_action": "Scout maize whorls weekly from seedling emergence.",
        "treatment": "Educational guidance: apply recommended biologicals or insecticides directed into the plant whorl.",
        "organic_alternatives": "Educational guidance: application of sand mixed with wood ash (9:1) or Bacillus thuringiensis (Bt) in whorls.",
        "prevention": ["Deep summer ploughing", "Intercrop with pulses (cowpea/blackgram)", "Erect bird perches (10/acre)"],
    },
    "Stem Borer": {
        "symptoms": [
            "Shot-hole feeding on leaves and dead hearts in young maize/sorghum plants",
            "Bore holes in stem with chewed frass",
        ],
        "recommended_action": "Apply whorl application of bio-agents or granular formulations at 15-20 days after emergence.",
        "treatment": "Educational guidance: consult agricultural extension for IPM stem borer schedule.",
        "organic_alternatives": "Educational guidance: release Trichogramma chilonis and spray neem seed kernel extract (NSKE 5%).",
        "prevention": ["Timely sowing", "Intercropping with legumes", "Destroy stubble after harvest"],
    },
    "Pink Bollworm": {
        "symptoms": [
            "Rosetted flowers on cotton plants",
            "Bored entry holes in bolls and premature boll opening",
            "Stained lint and double seeds inside mature bolls",
        ],
        "recommended_action": "Install pheromone traps (8/ha) for mass trapping and monitoring.",
        "treatment": "Educational guidance: consult local extension officer for IPM bollworm protocol.",
        "organic_alternatives": "Educational guidance: release egg parasitoid Trichogramma bactrae and spray neem oil (1500 ppm).",
        "prevention": ["Install pheromone traps early", "Avoid extending cotton crop past December", "Destroy crop residue immediately after harvest"],
    },
    "Cotton Aphid": {
        "symptoms": [
            "Downward cupping and crinkling of tender cotton leaves",
            "Shiny sticky honeydew on foliage attracting black sooty mold",
        ],
        "recommended_action": "Monitor shoot tips and encourage ladybird beetle predators.",
        "treatment": "Educational guidance: spray recommended sucking-pest insecticides upon reaching 10% infested plants.",
        "organic_alternatives": "Educational guidance: spray 5% NSKE or soap solution (5g/L).",
        "prevention": ["Avoid excess nitrogen", "Conserve natural predatory bugs"],
    },
    "Jute Semilooper": {
        "symptoms": [
            "Looping caterpillars feeding voraciously on top tender leaves and apical buds",
            "Side branching and stunted fibrous stalk growth",
        ],
        "recommended_action": "Erect bamboo bird perches (20/acre) to encourage predatory birds.",
        "treatment": "Educational guidance: spray contact insecticide when 2-3 larvae per plant are observed.",
        "organic_alternatives": "Educational guidance: spray neem formulation (1500 ppm) or Bacillus thuringiensis.",
        "prevention": ["Early weed control", "Monitor crop at 3-4 weeks age"],
    },
    "Pod Fly": {
        "symptoms": [
            "Maggots feeding inside pigeonpea pods without any external hole",
            "Seeds shriveled, striped, and unmarketable",
        ],
        "recommended_action": "Install fly traps and scout for adult flies during flowering.",
        "treatment": "Educational guidance: spray systemic insecticide at pod formation stage.",
        "organic_alternatives": "Educational guidance: spray 5% NSKE at 50% flowering.",
        "prevention": ["Grow pod-fly resistant cultivars", "Avoid staggered sowing in the same village"],
    },
    "Woolly Apple Aphid": {
        "symptoms": [
            "White cottony/woolly wax masses on apple branches and root collar",
            "Gall-like swellings and knots on twigs reducing tree vigor",
        ],
        "recommended_action": "Scout root collars and graft unions in spring.",
        "treatment": "Educational guidance: root drenching or trunk banding with recommended systemic insecticides.",
        "organic_alternatives": "Educational guidance: release parasitoid Aphelinus mali and spray neem formulation.",
        "prevention": ["Use woolly aphid resistant rootstocks (Merton 793 / MM106)", "Paint pruning cuts with Bordeaux paste"],
    },
    "Banana Pseudostem Borer": {
        "symptoms": [
            "Small pinhead holes on pseudostem exuding transparent jelly-like gum",
            "Yellowing and rotting of inner pseudostem causing plant to snap in wind",
        ],
        "recommended_action": "Remove dried leaf sheaths and maintain clean pseudostems.",
        "treatment": "Educational guidance: stem injection or leaf axil application of recommended insecticides.",
        "organic_alternatives": "Educational guidance: swab pseudostem with neem oil (3%) or Beauveria bassiana.",
        "prevention": ["Field sanitation", "Use clean suckers", "Trap adults with longitudinally split pseudostem traps"],
    },
    "Mango Hopper": {
        "symptoms": [
            "Large numbers of wedge-shaped nymphs and adults sucking sap from floral panicles",
            "Heavy blossom drop and sooty mold coating flower buds and leaves",
        ],
        "recommended_action": "Scout flower panicles at bud emergence (pre-bloom).",
        "treatment": "Educational guidance: spray recommended systemic insecticide at panicle emergence before flowers open.",
        "organic_alternatives": "Educational guidance: spray 5% NSKE or Beauveria bassiana bio-pesticide.",
        "prevention": ["Prune overcrowded inner branches to allow sunlight into tree canopy"],
    },
    "Fruit Borer": {
        "symptoms": [
            "Caterpillars boring into pomegranate/citrus fruits",
            "Exudation of dark sticky frass and rotting of arils/segments",
        ],
        "recommended_action": "Bag developing fruits with parchment paper bags when fruits reach marble size.",
        "treatment": "Educational guidance: spray ovicides or contact insecticides during egg-laying peak.",
        "organic_alternatives": "Educational guidance: butterfly trapping and botanical neem sprays.",
        "prevention": ["Fruit bagging", "Destroy infested fallen fruits"],
    },
    "Anar Butterfly": {
        "symptoms": [
            "Single larvae boring into pomegranate fruit leaving a round hole",
            "Foul smell and fungal rotting inside fruit",
        ],
        "recommended_action": "Bag fruits with butter paper bags before oviposition.",
        "treatment": "Educational guidance: spray recommended protective insecticide at flower initiation.",
        "organic_alternatives": "Educational guidance: release egg parasitoid Trichogramma chilonis.",
        "prevention": ["Clip calyx cups after fruit set", "Cover fruit with polythene or paper covers"],
    },
    "Citrus Psylla": {
        "symptoms": [
            "Nymphs crowd on young tender flush secreting waxy white threads",
            "Vector for deadly Citrus Greening (HLB) disease",
        ],
        "recommended_action": "Scout new flush in spring and autumn.",
        "treatment": "Educational guidance: spray recommended systemic insecticide on new vegetative flush.",
        "organic_alternatives": "Educational guidance: spray 1% hort oil or 5% neem extract.",
        "prevention": ["Prune water sprouts", "Monitor yellow sticky traps"],
    },
    "Flea Beetle": {
        "symptoms": [
            "Tiny shot holes chewed in grape leaves and tender buds",
            "Bud drying and reduced cluster emergence in spring",
        ],
        "recommended_action": "Scout grape vines after forward pruning.",
        "treatment": "Educational guidance: spray contact insecticide immediately upon bud swell stage.",
        "organic_alternatives": "Educational guidance: loose bark removal during dormancy reduces overwintering beetles.",
        "prevention": ["Remove loose bark from vines after pruning", "Sticky bands on trunks"],
    },
    "Rhinoceros Beetle": {
        "symptoms": [
            "V-shaped cuts and geometric clipping on open coconut fronds",
            "Bored holes in crown with shredded fiber residues",
        ],
        "recommended_action": "Hook out beetles from crowns using an iron rod.",
        "treatment": "Educational guidance: fill top 3-4 leaf axils with sevidol/sand mixture (1:2).",
        "organic_alternatives": "Educational guidance: treat manure pits with Metarhizium anisopliae fungus; erect Rhinolure pheromone traps.",
        "prevention": ["Crown cleaning twice a year", "Sanitize farmyard manure pits"],
    },
    "Red Palm Weevil": {
        "symptoms": [
            "Small holes in palm trunk oozing brownish viscous liquid",
            "Extruded chewed fibers and gnawing sound audible from trunk",
            "Toppling of crown in advanced attack",
        ],
        "recommended_action": "Act immediately upon detecting early trunk oozing.",
        "treatment": "Educational guidance: trunk injection or root feeding with recommended systemic insecticides.",
        "organic_alternatives": "Educational guidance: install Ferrolure pheromone bucket traps with food baits (banana/sugarcane).",
        "prevention": ["Avoid making steps or wounds on trunk", "Seal pruning wounds with copper paste"],
    },
    "Coffee Berry Borer": {
        "symptoms": [
            "Small round entry holes near the navel/calyx of green and ripe coffee berries",
            "Powdery bean frass and premature berry drop",
        ],
        "recommended_action": "Install Brocap funnel traps containing ethanol-methanol lures across the plantation.",
        "treatment": "Educational guidance: consult coffee board extension for approved IPM protocols.",
        "organic_alternatives": "Educational guidance: spray Beauveria bassiana bio-pesticide during early berry stage.",
        "prevention": ["Maintain shade regulation", "Strip picking (gleaning) of left-over berries after harvest", "Field hygiene"],
    },
    "White Stem Borer": {
        "symptoms": [
            "Ridges or ring-like swellings on main coffee stem",
            "Yellowing and wilting of foliage, dying of top branches",
        ],
        "recommended_action": "Trace and uproot borer-infested bushes before flight periods (Oct-Dec and Apr-May).",
        "treatment": "Educational guidance: stem swabbing with 10% lime wash before flight season.",
        "organic_alternatives": "Educational guidance: bark scraping of mature stems to remove egg-laying crevices.",
        "prevention": ["Maintain optimum 2-tier shade canopy", "Stem swabbing with lime paste"],
    },
}

_DEFAULT_PEST = {
    "symptoms": ["General pest activity"],
    "recommended_action": "Monitor the field and consult local advisory services.",
    "treatment": "Educational guidance: consult your local agricultural officer.",
    "organic_alternatives": "Educational guidance: maintain field hygiene and use monitoring traps.",
    "prevention": ["Regular scouting", "Field sanitation"],
}


def get_pest_knowledge(pest: str) -> dict:
    return PEST_KNOWLEDGE.get(pest, _DEFAULT_PEST)


def list_pests() -> list[dict]:
    return [
        {
            "id": slugify(name),
            "name": name,
            "crop_ids": PEST_CROPS.get(name, []),
            "knowledge": PEST_KNOWLEDGE.get(name, _DEFAULT_PEST),
        }
        for name in PEST_KNOWLEDGE
    ]


def get_pest(pest_id: str) -> dict | None:
    for entry in list_pests():
        if entry["id"] == pest_id:
            return entry
    return None


def pests_for_crop(crop_id: str) -> list[dict]:
    names = CROP_PESTS.get(crop_id, [])
    return [entry for entry in list_pests() if entry["name"] in names]


# --- Treatments (derived from the knowledge entries) ----------------------------

def list_treatments() -> list[dict]:
    treatments: list[dict] = []
    for target_type, entries in (("DISEASE", list_diseases()), ("PEST", list_pests())):
        for entry in entries:
            knowledge = entry["knowledge"]
            treatments.append(
                {
                    "id": f"{entry['id']}-treatment",
                    "target_type": target_type,
                    "target_name": entry["name"],
                    "recommended_action": knowledge["recommended_action"],
                    "chemical_guidance": knowledge["treatment"],
                    "organic_alternatives": knowledge["organic_alternatives"],
                    "prevention": knowledge["prevention"],
                }
            )
    return treatments


def get_treatment(treatment_id: str) -> dict | None:
    for treatment in list_treatments():
        if treatment["id"] == treatment_id:
            return treatment
    return None


def treatments_for_disease(disease_id: str) -> list[dict]:
    disease = get_disease(disease_id)
    if disease is None:
        return []
    return [t for t in list_treatments() if t["target_name"] == disease["name"]]


def treatments_for_pest(pest_id: str) -> list[dict]:
    pest = get_pest(pest_id)
    if pest is None:
        return []
    return [t for t in list_treatments() if t["target_name"] == pest["name"]]


def treatments_for_crop(crop_id: str) -> list[dict]:
    targets = {e["name"] for e in diseases_for_crop(crop_id)} | {
        e["name"] for e in pests_for_crop(crop_id)
    }
    return [t for t in list_treatments() if t["target_name"] in targets]


# --- Fertilizer catalog + rules (educational demo) -------------------------------

GROWTH_STAGES = ["SOWING", "VEGETATIVE", "FLOWERING", "GRAIN_FILLING", "FRUITING", "HARVEST_READY"]
SOIL_CONDITIONS = ["LOAMY", "SANDY", "CLAY", "SALINE", "BLACK"]

FERTILIZER_CATALOG: list[dict] = [
    {
        "id": "npk-basal",
        "name": "Balanced NPK basal mix",
        "category": "BALANCED",
        "growth_stages": ["SOWING"],
        "guidance": "Apply as a basal dose at or before sowing, placed below the seed line.",
    },
    {
        "id": "nitrogen-topdress",
        "name": "Nitrogen-rich top dressing",
        "category": "NITROGEN",
        "growth_stages": ["VEGETATIVE"],
        "guidance": "Apply when plants establish active growth, typically 2-3 weeks after emergence.",
    },
    {
        "id": "pk-flowering",
        "name": "Phosphorus and potassium mix",
        "category": "PHOSPHORUS_POTASSIUM",
        "growth_stages": ["FLOWERING"],
        "guidance": "Apply just before flowering to support flower and pod/ear set.",
    },
    {
        "id": "potassium-grainfill",
        "name": "Potassium-focused dressing",
        "category": "POTASSIUM",
        "growth_stages": ["GRAIN_FILLING"],
        "guidance": "Apply at early grain filling if the crop shows deficiency signs.",
    },
    {
        "id": "potassium-fruiting",
        "name": "Potassium and micronutrient mix",
        "category": "MICRONUTRIENT",
        "growth_stages": ["FRUITING"],
        "guidance": "Apply at fruit set; potassium is important for fruit development.",
    },
    {
        "id": "none-harvest",
        "name": "No application near harvest",
        "category": "NONE",
        "growth_stages": ["HARVEST_READY"],
        "guidance": "No further fertilization is recommended close to harvest.",
    },
]

_STAGE_TO_FERTILIZER = {entry["growth_stages"][0]: entry for entry in FERTILIZER_CATALOG}

_SOIL_NOTES = {
    "LOAMY": "Loamy soils hold nutrients well; split applications improve efficiency.",
    "SANDY": "Sandy soils leach nitrogen quickly; prefer smaller split applications.",
    "CLAY": "Clay soils release nutrients slowly; avoid waterlogging after application.",
    "SALINE": "Saline soils need salt-tolerant practices; prefer organic matter additions.",
    "BLACK": "Black soils retain moisture; time applications after irrigation.",
}

CROP_FERTILIZER_PROFILES: dict[str, str] = {
    "rice": "Paddy requires balanced NPK (120:60:40 kg/ha) with Zinc Sulfate (25 kg/ha) basal dose. Split Nitrogen across basal, active tillering, and panicle initiation.",
    "maize": "Maize is a heavy nitrogen feeder (120-150 kg N/ha). Apply 1/3 N + full P & K basal, 1/3 N at knee-high stage (V6), and 1/3 N at tasseling.",
    "cotton": "Cotton benefits from NPK (100:50:50) in 3 splits (sowing, square formation, and boll development) with Magnesium Sulfate (20 kg/ha) to prevent leaf reddening.",
    "jute": "Jute requires 60:30:30 NPK kg/ha with Urea top-dressing 3-4 weeks after germination for strong vegetative stalk development.",
    "pigeonpeas": "Legume crop fixing atmospheric nitrogen; apply 20 kg N and 50 kg P2O5 (Single Super Phosphate) at sowing with Rhizobium seed inoculation.",
    "blackgram": "Short-duration pulse; apply 20 kg N and 40 kg P2O5 at sowing with Rhizobium inoculation. Avoid excessive nitrogen to prevent lush vegetative growth.",
    "mothbeans": "Arid legume; requires minimal fertilization (10-15 kg P2O5 at sowing). Thrives on residual fertility.",
    "wheat": "Standard fertilizer schedule is 120:60:40 NPK kg/ha. Apply half N and full P & K at sowing, with remaining N top-dressed at first irrigation (CRI stage) and jointing.",
    "chickpea": "Apply 20 kg N and 40-50 kg P2O5 at sowing. Single Super Phosphate (SSP) is preferred as it also supplies 11% Sulfur.",
    "mustard": "Apply 80:40:40 NPK kg/ha with 20-30 kg Sulfur/ha (gypsum or bentonite sulfur) to maximize seed oil content.",
    "potato": "High potassium feeder (150:100:150 NPK kg/ha). Apply full P and half N & K at planting, and remaining N & K during earthing-up (30 days).",
    "lentil": "Apply 20 kg N and 40 kg P2O5 at sowing with sulfur. Highly responsive to phosphorus for root nodulation.",
    "apple": "Apply balanced NPK (70:35:70 g/tree/year of age) along with Boron and Zinc foliar sprays prior to flowering.",
    "watermelon": "Apply balanced NPK (100:50:50 kg/ha) with higher Potash and Calcium during fruit development to ensure fruit sweetness and thick rind.",
    "cucumber": "Requires 100:50:50 NPK kg/ha. Split Nitrogen applications every 2 weeks through drip or furrow irrigation.",
    "muskmelon": "Apply Potash and Calcium during fruit sizing. Withhold heavy nitrogen after fruit set to maintain fruit brix sweetness.",
    "moong": "Apply 20 kg N and 40 kg P2O5 (DAP/SSP) as basal application. Seed treatment with Rhizobium and PSB culture increases yield.",
    "banana": "Heavy potassium feeder (200g N, 50g P, 300g K per plant). Apply in monthly split doses with regular drip irrigation.",
    "mango": "Apply FYM (25-50 kg) with 1 kg N, 0.5 kg P, and 1 kg K per mature tree post-monsoon. Provide paclobutrazol if alternate bearing occurs.",
    "papaya": "Fast-growing fruit (250g N, 250g P, 500g K per plant per year) in bi-monthly split applications.",
    "pomegranate": "Apply 625g N, 250g P, and 500g K per plant per year with Boron and Zinc sprays during Bahar flowering.",
    "orange": "Apply 600g N, 200g P, and 400g K per tree per year in 3 splits with micronutrient sprays (Zinc, Iron, Manganese).",
    "grapes": "High potassium and micronutrient requirement. Apply Potash during berry enlargement and post-pruning balanced nutrition.",
    "coconut": "Apply 500g N, 320g P, and 1200g K per palm annually in two splits (pre-monsoon and post-monsoon) with organic manure.",
    "coffee": "Apply balanced NPK (120:90:120 kg/ha) in 3-4 splits with Zinc and Magnesium.",
}


def get_fertilizer(fertilizer_id: str) -> dict | None:
    for entry in FERTILIZER_CATALOG:
        if entry["id"] == fertilizer_id:
            return entry
    return None


def list_fertilizers() -> list[dict]:
    return list(FERTILIZER_CATALOG)


def fertilizers_for_crop(crop_id: str) -> list[dict]:
    """The full catalog is crop-agnostic today; kept for API symmetry."""
    return list(FERTILIZER_CATALOG)


def get_fertilizer_guidance(crop_name: str, growth_stage: str, soil_condition: str, npk: str | None) -> dict:
    fertilizer = _STAGE_TO_FERTILIZER.get(growth_stage, _STAGE_TO_FERTILIZER["VEGETATIVE"])
    soil_note = _SOIL_NOTES.get(soil_condition, "")
    npk_note = ""
    if npk:
        npk_note = f" Your soil note ({npk}) should be confirmed with a soil test before application."

    # Look up crop-specific fertilizer recommendation profile
    clean_crop_key = crop_name.lower().split("/")[0].strip().replace(" ", "").replace("-", "")
    crop_specific_tip = ""
    for key, tip in CROP_FERTILIZER_PROFILES.items():
        if key in clean_crop_key or clean_crop_key in key:
            crop_specific_tip = f" {tip}"
            break

    guidance = (
        f"Educational guidance for {crop_name} at the {growth_stage.lower().replace('_', ' ')} stage "
        f"in {soil_condition.lower()} soil. {soil_note}{crop_specific_tip}{npk_note} Always base final doses on a "
        "recent soil test report and local agricultural extension advice."
    )
    return {
        "recommended_category": fertilizer["name"],
        "recommended_fertilizer_id": fertilizer["id"],
        "application_timing": fertilizer["guidance"],
        "soil_note": soil_note,
        "guidance": guidance,
    }
