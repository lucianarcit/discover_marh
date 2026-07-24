import json

with open('phase_3_probe/artifacts/02_all_models_inventory.json') as f:
    models = json.load(f)

print("=== Modelos de geração ON_DEMAND com lifecycle ===")
for m in models:
    if ('TEXT' in m.get('outputModalities', [])
            and 'EMBEDDING' not in m.get('outputModalities', [])
            and 'ON_DEMAND' in m.get('inferenceTypesSupported', [])):
        lc = m.get('modelLifecycle', {})
        eol = lc.get('endOfLifeTime', '')
        print(f"{m['modelId']:<55} lifecycle={lc.get('status'):<10} eol={eol or '-'}")
