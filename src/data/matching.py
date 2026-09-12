from rapidfuzz import fuzz

def match_player(target_name: str, candidates: list[dict], threshold: int = 85) -> dict | None:
    best_match = None
    best_score = 0

    for candidate in candidates:
        score = fuzz.partial_ratio(target_name, candidate["name"])
        if score >= threshold and score > best_score:
            best_score = score
            best_match = candidate
            if best_score == 100:
                break

    return best_match, best_score

candidates = [
    {"id": 19012, "name": "M. Bettinelli"},
    {"id": 1622, "name": "G. Donnarumma"},
    {"id": 567, "name": "Rúben Dias"},
    {"id": 129033, "name": "J. Gvardiol"},
    {"id": 631, "name": "P. Foden"},
    {"id": 1422, "name": "J. Doku"},
    {"id": 1100, "name": "E. Haaland"},
    {"id": 5996, "name": "E. Fernández"},
    {"id": 41621, "name": "Matheus Nunes"},
]

tests = [
    "Erling Haaland",
    "Hąland",
    "E. Halaand",
    "Phil Foden",
    "Rodri",                       # nie ma go w liście - powinno dać None
    "Ruben Dias",
    "Enzo Fernandez",
    "Jeremy Doku",
    "Kompletnie Obcy Człowiek",    # kompletnie obcy - powinno dać None
    "Matheus Nunes",
]

for t in tests:
    match, score = match_player(t, candidates)
    name = match["name"] if match else None
    print(f"{t!r:30} -> {name!r:20} score={score:.0f}")