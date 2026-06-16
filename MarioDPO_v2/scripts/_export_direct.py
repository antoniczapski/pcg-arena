"""Stage 8 equivalent: export the already-generated valid levels as arena seed bundle."""
import hashlib, json
from mariodpo_v2.constants import OUTPUTS_DIR
from mariodpo_v2.level_io import load_level, level_to_text
from mariodpo_v2.utils import load_dotenv
from mariodpo_v2.validate import validate_level

load_dotenv()
gen_dir = OUTPUTS_DIR / "generated" / "dpo"
out_dir = OUTPUTS_DIR / "seed" / "mariodpo_v2"
out_dir.mkdir(parents=True, exist_ok=True)

manifest = []
kept = 0
for p in sorted(gen_dir.glob("*.txt")):
    rows = load_level(p)
    errors = validate_level(rows, min_width=150)
    if errors:
        print(f"SKIP {p.name}: {errors}")
        continue
    text = level_to_text(rows)
    fname = f"level_{kept:03d}.txt"
    (out_dir / fname).write_text(text, encoding="utf-8")
    manifest.append({
        "file": fname,
        "content_hash": hashlib.sha256(text.encode()).hexdigest(),
        "width": len(rows[0]),
        "height": len(rows),
        "judge_score": None,  # filled below
        "valid": True,
    })
    kept += 1

# Fill judge scores from existing manifest
import joblib, random
from mariodpo_v2.constants import MODELS_DIR
from mariodpo_v2.features import extract_features
from mariodpo_v2.utils import normalised_compression_distance
from mariodpo_v2.level_io import iter_seed_levels
judge = joblib.load(MODELS_DIR / "judge.pkl")["judge"]
rng = random.Random(42)
refs = [level_to_text(load_level(q)) for g,f,q in iter_seed_levels(["original"])]
refs = rng.sample(refs, min(8, len(refs)))
for i, p in enumerate(sorted(gen_dir.glob("*.txt"))):
    rows = load_level(p)
    if i >= kept:
        break
    feats = extract_features(rows)
    feats["ncd_to_original"] = sum(normalised_compression_distance(level_to_text(rows), r) for r in refs) / len(refs)
    feats["generator"] = "mariodpo_v2"
    manifest[i]["judge_score"] = round(judge.score(feats), 4)

generator_stub = {
    "id": "mariodpo_v2",
    "name": "MarioDPO v2",
    "description": (
        "GPT-2 (MarioGPT checkpoint) continue-pretrained on PCG Arena levels "
        "and DPO-aligned on oversampled human preference votes plus judge-labelled "
        "synthetic pairs. LoRA adapter fine-tuning on 816 human pairs (x10 weight) "
        "+ 2000 synthetic pairs."
    ),
    "paradigm": "ML + DPO",
    "level_count": kept,
}
(out_dir / "generator.json").write_text(json.dumps(generator_stub, indent=2))
(out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Exported {kept} levels -> {out_dir}")
print(f"Mean judge score: {sum(m['judge_score'] for m in manifest)/len(manifest):.3f}")
for m in manifest:
    print(f"  {m['file']} w={m['width']} score={m['judge_score']}")
