"""Rebuild manifest for already-generated DPO levels."""
import json, joblib, random
from mariodpo_v2.constants import OUTPUTS_DIR, MODELS_DIR
from mariodpo_v2.level_io import load_level, level_to_text, iter_seed_levels
from mariodpo_v2.features import extract_features
from mariodpo_v2.utils import normalised_compression_distance, load_dotenv
from mariodpo_v2.validate import validate_level

load_dotenv()
judge = joblib.load(MODELS_DIR / "judge.pkl")["judge"]
rng = random.Random(42)
refs = [level_to_text(load_level(p)) for g,f,p in iter_seed_levels(["original"])]
refs = rng.sample(refs, min(8, len(refs)))

gen_dir = OUTPUTS_DIR / "generated" / "dpo"
manifest = []
for p in sorted(gen_dir.glob("*.txt")):
    rows = load_level(p)
    feats = extract_features(rows)
    feats["ncd_to_original"] = sum(normalised_compression_distance(level_to_text(rows), r) for r in refs) / len(refs)
    feats["generator"] = "mariodpo_v2"
    score = judge.score(feats)
    errors = validate_level(rows)
    manifest.append({"file": p.name, "judge_score": round(score,4), "valid": not errors, "width": len(rows[0]) if rows else 0, "errors": errors})

(gen_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Wrote manifest for {len(manifest)} levels")
for m in manifest:
    print(f"  {m['file']}: score={m['judge_score']:.3f} valid={m['valid']} w={m['width']}")
