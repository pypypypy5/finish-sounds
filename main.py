#!/usr/bin/env python3
import json
import sys
import subprocess
import shutil
import os
import random
import glob
from datetime import datetime

DEBUG = os.environ.get("FINISH_SOUNDS_DEBUG", "").lower() in {"1", "true", "yes", "on"}


def log(msg: str) -> None:
    if DEBUG:
        print(f"[finish-sounds] {msg}", file=sys.stderr)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "hook.log")


def persist(msg: str) -> None:
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


if len(sys.argv) < 2:
    log("no event argument; use --self-test or pass JSON event")
    persist("no event argument")
    sys.exit(0)

self_test = sys.argv[1] == "--self-test"

try:
    event = {"type": "agent-turn-complete"} if self_test else json.loads(sys.argv[1])
except Exception as e:
    log(f"failed to parse event JSON: {e}")
    persist(f"event parse failed: {e}")
    sys.exit(0)

if event.get("type") != "agent-turn-complete":
    log(f"ignored event type: {event.get('type')}")
    persist(f"ignored event type: {event.get('type')}")
    sys.exit(0)

# 훅 파일 기준 디렉토리의 오디오 파일 목록
sounds_dir = BASE_DIR
if os.path.exists(sounds_dir):
    audio_files = glob.glob(os.path.join(sounds_dir, "*.wav")) + glob.glob(os.path.join(sounds_dir, "*.mp3"))
    if audio_files:
        sound_file = random.choice(audio_files)
        ext = os.path.splitext(sound_file)[1].lower()
        log(f"selected file: {sound_file}")
        persist(f"selected file: {sound_file}")

        # 사용 가능한 플레이어 탐색: paplay -> ffplay -> aplay(wav만) -> PowerShell -> 벨
        players = []
        if shutil.which("paplay"):
            players.append(["paplay", sound_file])
        if shutil.which("ffplay"):
            players.append(["ffplay", "-nodisp", "-autoexit", sound_file])
        if ext == ".wav" and shutil.which("aplay"):
            players.append(["aplay", sound_file])
        # Windows PowerShell (WSL에서도 powershell.exe가 PATH에 있을 수 있음)
        pwsh = shutil.which("powershell.exe") or shutil.which("powershell")
        if pwsh:
            ps_cmd = (
                "Add-Type -AssemblyName PresentationCore;"
                "$p=New-Object System.Windows.Media.MediaPlayer;"
                f"$p.Open([Uri]::new('{os.path.abspath(sound_file)}'));"
                "$p.Volume=1;"
                "$p.Play();Start-Sleep -Milliseconds 1500"
            )
            players.append([pwsh, "-NoProfile", "-Command", ps_cmd])

        log("available players: " + (", ".join(cmd[0] for cmd in players) if players else "none"))
        persist("available players: " + (", ".join(cmd[0] for cmd in players) if players else "none"))

        for cmd in players:
            try:
                log("trying: " + " ".join(cmd[:2]))
                if DEBUG:
                    result = subprocess.call(cmd)
                else:
                    result = subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log(f"exit code from {cmd[0]}: {result}")
                persist(f"player {cmd[0]} exited with {result}")
                if result == 0:
                    persist("playback success")
                    sys.exit(0)
            except FileNotFoundError:
                log(f"not found: {cmd[0]}")
                persist(f"player not found: {cmd[0]}")
                continue
            except Exception as e:
                log(f"error from {cmd[0]}: {e}")
                persist(f"player error from {cmd[0]}: {e}")
                continue

        # 모든 시도가 실패하면 터미널 벨
        log("all players failed; fallback to terminal bell")
        persist("all players failed; bell fallback")
        print("\a", end="", flush=True)
        # 재생 실패를 명확히 드러내기 위해 실패 코드 반환
        sys.exit(1)

log(f"no audio files found in: {sounds_dir}")
persist(f"no audio files found in: {sounds_dir}")
print("\a", end="", flush=True)
sys.exit(1)
