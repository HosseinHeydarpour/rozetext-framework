import json, shutil, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from scripts.rozetext_scoring_engine_v3 import evaluate_script_v3

db_path = 'data/scripts-db.json'
backup_path = 'data/archive/scripts-db-pre-v3-calibration.json'

os.makedirs('data/archive', exist_ok=True)
shutil.copy2(db_path, backup_path)
print(f"Backed up {db_path} to {backup_path}")

with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts = db.get('scripts', [])
print(f"Total scripts in DB to recalibrate: {len(scripts)}")

updated_count = 0
recalculated_scores = []

for s in scripts:
    eval_res = evaluate_script_v3(s, slot=s.get('scheduled_slot'))
    old_score = s.get('score')
    new_score = eval_res['final_score']
    
    # Store old score in meta if needed
    s['v2_score'] = old_score
    s['score'] = new_score
    s['score_breakdown'] = eval_res['breakdown']
    s['verdict'] = eval_res['verdict']
    s['tier'] = eval_res['tier']
    s['expected_views'] = eval_res['expected_views']
    
    # Update reasons if bonuses/penalties exist
    reasons = []
    if eval_res['penalties']:
        for p_name, p_val in eval_res['penalties']:
            reasons.append(f"⚠️ {p_name} ({p_val})")
    if eval_res['bonuses']:
        for b_name, b_val in eval_res['bonuses']:
            reasons.append(f"✨ {b_name} (+{b_val})")
    if eval_res['slot_note']:
        reasons.append(f"⏰ {eval_res['slot_note']}")
        
    if reasons:
        s['v3_audit_notes'] = " | ".join(reasons)
        
    updated_count += 1
    recalculated_scores.append((old_score, new_score, s.get('title', '')[:35]))

db['meta']['scoring_engine_version'] = "v3.0-calibrated"
db['meta']['last_calibration_date'] = "2026-10-18"
db['meta']['calibration_dataset_size'] = "358 reels (up to 18-10-2026)"

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Successfully recalibrated {updated_count} scripts in {db_path} with Engine v3.0.")

print("\nSample 10 Recalibrated Scores (Old -> New):")
for old, new, title in recalculated_scores[:10]:
    print(f"  {old} -> {new:>2} | {title}")
