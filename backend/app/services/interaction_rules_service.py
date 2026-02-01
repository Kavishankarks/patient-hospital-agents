from __future__ import annotations

RULES = [
    {'a': 'warfarin', 'b': 'ibuprofen', 'risk': 'increased bleeding risk'},
    {'a': 'lisinopril', 'b': 'potassium supplement', 'risk': 'hyperkalemia risk'},
]

class InteractionRulesService:
    def check(self, meds: list[str]) -> list[str]:
        meds_lower = {m.lower() for m in meds}
        findings = []
        for rule in RULES:
            if rule['a'] in meds_lower and rule['b'] in meds_lower:
                findings.append(f"{rule['a']} + {rule['b']}: {rule['risk']}")
        return findings
