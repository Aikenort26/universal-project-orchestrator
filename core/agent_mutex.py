#!/usr/bin/env python
"""Modulo de Cerrojos Mutex y Registro de Eventos Inter-Agente (Costo Cero).

Permite la coordinacion asincrona y exclusion mutua entre Claude Code,
Antigravity, Codex y scripts locales para evitar colisiones en Google Drive
y el vault compartido.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import platform
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.abspath(os.path.join(HERE, "..", ".."))
LOCKS_DIR = os.path.join(VAULT, ".brain", "locks")
EVENTS_DIR = os.path.join(VAULT, ".brain", "events")
EVENTS_FILE = os.path.join(EVENTS_DIR, "events.jsonl")


def ensure_dirs():
    os.makedirs(LOCKS_DIR, exist_ok=True)
    os.makedirs(EVENTS_DIR, exist_ok=True)


def normalize_resource(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name.strip())
    return cleaned.lower()


def get_lock_path(resource: str) -> str:
    norm = normalize_resource(resource)
    return os.path.join(LOCKS_DIR, f"{norm}.lock")


def parse_iso(ts_str: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(ts_str)


def acquire_lock(resource: str, agent_id: str, reason: str = "", ttl_minutes: int = 15) -> tuple[bool, dict]:
    """Intenta adquirir un cerrojo exclusivo para un recurso."""
    ensure_dirs()
    lock_file = get_lock_path(resource)
    now = datetime.datetime.now()
    expires_at = now + datetime.timedelta(minutes=ttl_minutes)

    if os.path.isfile(lock_file):
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
            exp = parse_iso(existing.get("expires_at", "1970-01-01T00:00:00"))
            
            # Si el cerrojo expiró, se revoca automáticamente
            if now > exp:
                log_event(agent_id, "revoke_expired_lock", resource, {"previous_agent": existing.get("agent_id")})
            elif existing.get("agent_id") == agent_id:
                # El mismo agente renueva su cerrojo
                pass
            else:
                # Bloqueado por otro agente activo
                return False, existing
        except Exception:
            # Archivo corrupto o ilegible; se sobreescribe de forma segura
            pass

    lock_data = {
        "resource": resource,
        "normalized": normalize_resource(resource),
        "agent_id": agent_id,
        "hostname": platform.node(),
        "pid": os.getpid(),
        "reason": reason,
        "created_at": now.isoformat(timespec="seconds"),
        "expires_at": expires_at.isoformat(timespec="seconds"),
        "ttl_minutes": ttl_minutes
    }

    temp_file = lock_file + f".{os.getpid()}.tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2, ensure_ascii=False)
    
    # Reemplazo atomico en el sistema de archivos
    os.replace(temp_file, lock_file)
    log_event(agent_id, "acquire_lock", resource, {"reason": reason, "expires_at": lock_data["expires_at"]})
    return True, lock_data


def release_lock(resource: str, agent_id: str, force: bool = False) -> tuple[bool, str]:
    """Libera un cerrojo existente."""
    ensure_dirs()
    lock_file = get_lock_path(resource)

    if not os.path.isfile(lock_file):
        return True, "El cerrojo no existia o ya estaba liberado."

    try:
        with open(lock_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
        
        owner = existing.get("agent_id", "")
        if owner != agent_id and not force:
            return False, f"Cerrojo retenido por '{owner}'. Use --force para revocar."
        
        os.remove(lock_file)
        log_event(agent_id, "release_lock", resource, {"forced": force})
        return True, "Cerrojo liberado correctamente."
    except Exception as e:
        return False, f"Error al liberar cerrojo: {e}"


def list_locks() -> list[dict]:
    """Lista todos los cerrojos registrados con su estado de vigencia."""
    ensure_dirs()
    results = []
    now = datetime.datetime.now()

    for item in os.listdir(LOCKS_DIR):
        if not item.endswith(".lock"):
            continue
        p = os.path.join(LOCKS_DIR, item)
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            exp = parse_iso(data.get("expires_at", "1970-01-01T00:00:00"))
            data["is_expired"] = (now > exp)
            data["remaining_seconds"] = max(0, int((exp - now).total_seconds()))
            results.append(data)
        except Exception:
            results.append({"resource": item, "corrupted": True})
    return results


def clean_expired_locks() -> int:
    """Elimina cerrojos que hayan superado su TTL."""
    ensure_dirs()
    cleaned = 0
    now = datetime.datetime.now()

    for item in os.listdir(LOCKS_DIR):
        if not item.endswith(".lock"):
            continue
        p = os.path.join(LOCKS_DIR, item)
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            exp = parse_iso(data.get("expires_at", "1970-01-01T00:00:00"))
            if now > exp:
                os.remove(p)
                cleaned += 1
                log_event("SYSTEM", "auto_clean_expired_lock", data.get("resource", item))
        except Exception:
            try:
                os.remove(p)
                cleaned += 1
            except Exception:
                pass
    return cleaned


def log_event(agent_id: str, action: str, target: str, details: dict | None = None):
    """Registra una accion en el bus continuo de eventos JSON Lines."""
    ensure_dirs()
    record = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "agent": agent_id,
        "action": action,
        "target": target,
        "hostname": platform.node(),
        "details": details or {}
    }
    line = json.dumps(record, ensure_ascii=False) + "\n"
    try:
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Gestor de cerrojos y eventos inter-agente")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # acquire
    p_acq = sub.add_parser("acquire", help="Adquirir cerrojo sobre un recurso")
    p_acq.add_argument("resource", help="Nombre del recurso o proyecto")
    p_acq.add_argument("--agent", required=True, help="Identificador del agente")
    p_acq.add_argument("--reason", default="", help="Motivo de la reserva")
    p_acq.add_argument("--ttl", type=int, default=15, help="Minutos de vigencia (defecto: 15)")

    # release
    p_rel = sub.add_parser("release", help="Liberar cerrojo")
    p_rel.add_argument("resource", help="Nombre del recurso")
    p_rel.add_argument("--agent", required=True, help="Identificador del agente")
    p_rel.add_argument("--force", action="store_true", help="Forzar liberacion si es de otro agente")

    # list
    sub.add_parser("list", help="Listar cerrojos actuales")

    # clean
    sub.add_parser("clean", help="Limpiar cerrojos expirados")

    # log
    p_log = sub.add_parser("log", help="Registrar evento en el bus continuo")
    p_log.add_argument("--agent", required=True, help="Identificador del agente")
    p_log.add_argument("--action", required=True, help="Accion ejecutada")
    p_log.add_argument("--target", required=True, help="Recurso objetivo")
    p_log.add_argument("--info", default="{}", help="Detalles adicionales en JSON")

    args = parser.parse_args()

    if args.cmd == "acquire":
        ok, info = acquire_lock(args.resource, args.agent, args.reason, args.ttl)
        if ok:
            print(f"[OK] Cerrojo adquirido para '{args.resource}' por {args.agent}. Expira en {args.ttl} min.")
            sys.exit(0)
        else:
            print(f"[BLOQUEADO] Recurso '{args.resource}' retenido por '{info.get('agent_id')}'. Expira: {info.get('expires_at')}.")
            sys.exit(1)

    elif args.cmd == "release":
        ok, msg = release_lock(args.resource, args.agent, args.force)
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
        sys.exit(0 if ok else 1)

    elif args.cmd == "list":
        locks = list_locks()
        if not locks:
            print("No hay cerrojos registrados.")
        else:
            print(f"Total cerrojos: {len(locks)}")
            for lk in locks:
                estado = "EXPIRADO" if lk.get("is_expired") else f"ACTIVO ({lk.get('remaining_seconds')}s)"
                print(f"- Recurso: {lk.get('resource')} | Agente: {lk.get('agent_id')} | Estado: {estado} | Motivo: {lk.get('reason')}")

    elif args.cmd == "clean":
        n = clean_expired_locks()
        print(f"Cerrojos expirados eliminados: {n}")

    elif args.cmd == "log":
        try:
            det = json.loads(args.info)
        except Exception:
            det = {"raw": args.info}
        log_event(args.agent, args.action, args.target, det)
        print(f"[OK] Evento registrado en {EVENTS_FILE}")


if __name__ == "__main__":
    main()
