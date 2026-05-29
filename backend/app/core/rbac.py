from pathlib import Path

import casbin

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_CONF = BASE_DIR / "casbin" / "model.conf"
POLICY_CSV = BASE_DIR / "casbin" / "policy.csv"

enforcer = casbin.SyncedEnforcer(str(MODEL_CONF), str(POLICY_CSV))

def authorize(role: str, path: str, method: str) -> bool:
    return enforcer.enforce(role, path, method)
