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
    "zaid": {"name": "Zaid / Summer", "label": "Summer season (Mar–Jun)"},
}


# --- Crop disease catalogs ---------------------------------------------------

CROP_DISEASES: dict[str, list[str]] = {
    "wheat": ["Leaf Rust", "Powdery Mildew", "Loose Smut"],
    "chickpea": ["Fusarium Wilt", "Ascochyta Blight"],
    "mustard": ["Alternaria Blight", "White Rust"],
    "potato": ["Early Blight", "Late Blight"],
    "watermelon": ["Anthracnose", "Downy Mildew"],
    "cucumber": ["Downy Mildew", "Cucumber Mosaic Virus"],
    "muskmelon": ["Powdery Mildew", "Fusarium Wilt"],
    "moong": ["Yellow Mosaic Virus", "Cercospora Leaf Spot"],
}

# --- Pest catalogs -----------------------------------------------------------

CROP_PESTS: dict[str, list[str]] = {
    "wheat": ["Aphid", "Termite"],
    "chickpea": ["Pod Borer", "Cutworm"],
    "mustard": ["Mustard Aphid", "Sawfly"],
    "potato": ["Tuber Moth", "Aphid"],
    "watermelon": ["Red Pumpkin Beetle", "Fruit Fly"],
    "cucumber": ["Whitefly", "Red Spider Mite"],
    "muskmelon": ["Fruit Fly", "Whitefly"],
    "moong": ["Whitefly", "Pod Borer"],
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
    guidance = (
        f"Educational guidance for {crop_name} at the {growth_stage.lower().replace('_', ' ')} stage "
        f"in {soil_condition.lower()} soil. {soil_note}{npk_note} Always base final doses on a "
        "recent soil test report and local agricultural extension advice."
    )
    return {
        "recommended_category": fertilizer["name"],
        "recommended_fertilizer_id": fertilizer["id"],
        "application_timing": fertilizer["guidance"],
        "soil_note": soil_note,
        "guidance": guidance,
    }
