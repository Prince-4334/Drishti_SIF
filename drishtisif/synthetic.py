import random
from datetime import date, timedelta

import pandas as pd

from .lexicon import SITES

EQUIPMENT = [
    "pump P-204", "compressor C-11", "GGS feed pump", "mud pump", "generator set",
    "heater treater", "separator unit", "transfer pump", "air compressor", "well pad panel",
]

SIF_SCENARIOS = {
    "energy_isolation": {
        "rule": "Energy Isolation",
        "openers": [
            "During maintenance of {eq}, technician started work",
            "Electrician opened the control panel of {eq}",
            "Fitter began repairing {eq}",
            "Mechanic removed the coupling guard of {eq} for repair",
        ],
        "faults": [
            "without confirming electrical isolation",
            "without lockout tag",
            "before isolation was verified",
            "and the breaker was found ON",
            "though the motor was not isolated",
        ],
        "closers": [
            "Power was still live.", "Stored pressure was still in the line.",
            "No injury occurred.", "Supervisor stopped the job.",
            "Noticed by a co-worker in time.", "",
        ],
    },
    "hot_work": {
        "rule": "Hot Work",
        "openers": [
            "Welder started gas cutting near {eq}",
            "Grinding work was going on close to the flare line",
            "Welding was carried out on the pipe near {eq}",
            "Contractor started hot work on the skid",
        ],
        "faults": [
            "without hot work permit",
            "without gas testing",
            "with flammable vapour present nearby",
            "and no fire watch was posted",
            "with a hydrocarbon leak in the area",
        ],
        "closers": [
            "Sparks fell near the drain.", "No fire occurred.", "Gas alarm was ringing.",
            "Stopped by the safety officer.", "",
        ],
    },
    "confined_space": {
        "rule": "Confined Space",
        "openers": [
            "Two workers entered the crude oil tank for cleaning",
            "Worker went inside the sump pit",
            "Contractor entered the vessel for inspection",
            "Helper climbed into the manhole of the storage tank",
        ],
        "faults": [
            "without oxygen testing",
            "without standby person at the entry point",
            "without entry permit",
            "and the gas detector was not used",
            "before ventilation was completed",
        ],
        "closers": [
            "One worker felt dizzy.", "No injury occurred.", "Supervisor called them out.", "",
        ],
    },
    "line_of_fire": {
        "rule": "Line of Fire",
        "openers": [
            "Rigger was standing under the suspended load",
            "Crew member stood in the swing path of the pipe",
            "Worker walked under the raised load on the rig floor",
            "Helper was positioned in the line of fire while releasing pressure",
            "Worker stood near the hammer union during pressure testing",
        ],
        "faults": [
            "while the crane was lifting",
            "as the pipe swung on the sling",
            "with no barricade",
            "and the tag line was not used",
            "while the line was still pressurised",
        ],
        "closers": [
            "The load moved sideways.", "Object missed him by a metre.", "No injury occurred.", "",
        ],
    },
    "lifting": {
        "rule": "Safe Mechanical Lifting",
        "openers": [
            "Crane lifted the separator skid",
            "Forklift carried a loaded pipe bundle",
            "Mobile crane started lifting the generator",
            "Derrick hoist was used to raise the casing",
        ],
        "faults": [
            "without a lift plan",
            "with a damaged sling",
            "beyond the load chart limit",
            "with an uncertified rigger",
            "without checking the ground condition",
        ],
        "closers": [
            "Sling snapped and the load dropped.", "Load tilted during the lift.",
            "No injury occurred.", "Lift was stopped midway.", "",
        ],
    },
    "height": {
        "rule": "Working at Height",
        "openers": [
            "Worker climbed the derrick platform",
            "Painter worked on the tank roof",
            "Fitter went up the scaffold to reach the pipe rack",
            "Rig crew worked on the monkey board",
        ],
        "faults": [
            "without a safety harness",
            "without anchoring the lanyard",
            "on an incomplete scaffold",
            "with the handrail removed",
            "without a fall arrest plan",
        ],
        "closers": [
            "Tool fell from height.", "Worker slipped but caught the rail.",
            "No injury occurred.", "",
        ],
    },
    "driving": {
        "rule": "Driving",
        "openers": [
            "Tanker driver was moving the truck on the lease road",
            "Contract driver reversed the vehicle in the well site",
            "Driver was driving the crew van to the rig",
            "Heavy vehicle entered the site gate",
        ],
        "faults": [
            "above the speed limit",
            "without wearing a seatbelt",
            "while using a mobile phone",
            "with no banksman guiding",
            "after a long shift without rest",
        ],
        "closers": [
            "Vehicle nearly hit a pedestrian.", "Skidded near the pipeline.",
            "No injury occurred.", "",
        ],
    },
    "work_authorization": {
        "rule": "Work Authorization",
        "openers": [
            "Contractor began pipeline modification work",
            "Crew started work on the live gas line",
            "Team carried out well servicing job",
            "Workers opened the flange on the process line",
        ],
        "faults": [
            "without a work permit",
            "without a job safety analysis",
            "without permit sign-off from the area owner",
            "with an expired permit",
            "without a toolbox talk",
        ],
        "closers": [
            "Hydrocarbon leaked from the flange.", "Gas smell was noticed.",
            "No injury occurred.", "",
        ],
    },
    "bypass": {
        "rule": "Bypassing Safety Controls",
        "openers": [
            "Operator bypassed the high pressure trip on the separator",
            "Technician put a jumper on the gas detector",
            "Operator overrode the interlock of {eq}",
            "Alarm on the compressor was disabled by the crew",
        ],
        "faults": [
            "to keep the plant running",
            "without approval",
            "and forgot to restore it",
            "during the night shift",
        ],
        "closers": [
            "Pressure rose above the limit.", "Alarm did not sound.", "No injury occurred.", "",
        ],
    },
}

ROUTINE_SCENARIOS = {
    "housekeeping": {
        "openers": [
            "Loose cables were lying on the walkway near {eq}",
            "Oil spill was seen on the floor of the pump house",
            "Scrap material was kept in the passage",
            "Store room shelves were not arranged properly",
            "Wet floor near the canteen entrance",
        ],
        "faults": ["", "in the maintenance shop", "outside the control room", "in the workshop"],
        "closers": ["Area was cleaned.", "Reported to supervisor.", "Housekeeping team informed.", "No injury occurred.", ""],
    },
    "minor_ppe": {
        "openers": [
            "Worker was found without ear plugs in the generator room",
            "Helper not wearing safety glasses while sweeping",
            "Employee walking without hand gloves in the store",
            "Visitor entered the office area without a badge",
        ],
        "faults": ["for a short time", "in a low risk area", ""],
        "closers": ["Counselled on the spot.", "PPE was issued.", "No injury occurred.", ""],
    },
    "minor_injury": {
        "openers": [
            "Worker got a small cut on the finger while opening a box",
            "Employee twisted his ankle while walking on the stairs",
            "Helper had a minor bruise from the tool box",
            "Staff member slipped on the wet floor of the pantry",
        ],
        "faults": ["", "and received first aid", "at the site office"],
        "closers": ["Returned to duty after first aid.", "No lost time.", ""],
    },
    "paperwork": {
        "openers": [
            "Daily checklist was not signed in the control room",
            "Fire extinguisher inspection tag was overdue in the office block",
            "Register entry was missed by the security guard",
            "Training record was not updated for one employee",
        ],
        "faults": ["", "during the weekly audit", "in the admin building"],
        "closers": ["Corrected the same day.", "Reminder issued.", ""],
    },
    "good_practice": {
        "openers": [
            "Crane lift of {eq} was done as per the lift plan",
            "Isolation of {eq} was verified and locked out before repair",
            "Hot work was carried out with a valid permit and fire watch",
            "Tank entry was done after gas testing with a standby person",
            "Welding job completed with gas test and fire watch in place",
        ],
        "faults": ["", "by a trained team", "after the toolbox talk"],
        "closers": ["Job completed safely.", "Good practice observed.", "No issue found.", "No injury occurred.", ""],
    },
    "minor_vehicle": {
        "openers": [
            "Vehicle was parked in the wrong bay at the gate",
            "Driver forgot to carry the vehicle papers",
            "Bus was late reaching the colony",
            "Two wheeler parked near the fence",
        ],
        "faults": ["", "during the morning shift", "near the main gate"],
        "closers": ["Driver was reminded.", "Security informed.", "No injury occurred.", ""],
    },
    "low_energy_tools": {
        "openers": [
            "Worker used a hammer with a loose handle",
            "Ladder of the store had a missing rubber foot",
            "Extension board had a broken cover in the office",
            "Chair in the control room was broken",
        ],
        "faults": ["", "in the workshop", "in the admin block"],
        "closers": ["Item was replaced.", "Sent for repair.", "No injury occurred.", ""],
    },
}

SITE_SIF_SHARE = {
    "Duliajan": 0.32, "Naharkatiya": 0.30, "Jaisalmer": 0.26,
    "Moran": 0.20, "Kumchai": 0.18, "Tinsukia": 0.12,
}

SITE_LEANS = {
    "Duliajan": {"line_of_fire": 4, "lifting": 4},
    "Naharkatiya": {"energy_isolation": 5, "work_authorization": 2},
    "Jaisalmer": {"hot_work": 5, "driving": 2},
    "Moran": {"confined_space": 4},
    "Kumchai": {"height": 4},
    "Tinsukia": {},
}


def _sentence(scenario, rng):
    opener = rng.choice(scenario["openers"]).format(eq=rng.choice(EQUIPMENT))
    fault = rng.choice(scenario["faults"])
    closer = rng.choice(scenario["closers"])
    text = f"{opener} {fault}".strip() + "."
    if closer:
        text += " " + closer
    return text


def _roughen(text, rng):
    if rng.random() < 0.2:
        text = text.replace(" the ", " ").replace(" a ", " ")
    if rng.random() < 0.08:
        words = text.split()
        pick = rng.randrange(len(words))
        word = words[pick]
        if len(word) > 5:
            i = rng.randrange(1, len(word) - 2)
            words[pick] = word[:i] + word[i + 1] + word[i] + word[i + 2:]
        text = " ".join(words)
    return text


def _report_type(text, rng):
    if "No injury" in text:
        return rng.choice(["Near miss", "Near miss", "Unsafe act"])
    return rng.choice(["Unsafe act", "Unsafe condition", "Near miss", "Incident"])


def make_reports(count, seed, with_dates=True, label_noise=0.0):
    rng = random.Random(seed)
    start = date(2025, 10, 1)
    rows = []
    for number in range(count):
        site = rng.choice(SITES)
        is_sif = rng.random() < SITE_SIF_SHARE[site]
        if is_sif:
            names = list(SIF_SCENARIOS)
            weights = [1 + SITE_LEANS[site].get(name, 0) for name in names]
            name = rng.choices(names, weights)[0]
            scenario = SIF_SCENARIOS[name]
            rule = scenario["rule"]
        else:
            name = rng.choice(list(ROUTINE_SCENARIOS))
            scenario = ROUTINE_SCENARIOS[name]
            rule = ""
        text = _roughen(_sentence(scenario, rng), rng)
        label = 1 if is_sif else 0
        if rng.random() < label_noise:
            label = 1 - label
        row = {
            "report_id": f"R{number + 1:04d}",
            "site": site,
            "report_type": _report_type(text, rng),
            "description": text,
            "sif_label": label,
            "true_rule": rule,
        }
        if with_dates:
            row["date"] = (start + timedelta(days=rng.randrange(365))).isoformat()
        rows.append(row)
    frame = pd.DataFrame(rows)
    if with_dates:
        frame = frame.sort_values("date").reset_index(drop=True)
    return frame
