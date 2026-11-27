# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk 고객용 입력 패치 — 맵·번역 방식에서 Caps Lock 을 글자마다 눌렀다 되돌리지 않음(한글 낱자 문제) | @KEY: python3 res/updesk_patch.py 끝에서 실행
# res/updesk_input_patch.py — 손님 PC(받는 쪽)의 키 넣기 동작. 값(주소·키) 없음. 64·32비트 고객용 공통.
# 원본 글이 바뀌면 assert 로 멈춘다(조용히 잘못 만들지 않음).
import pathlib

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("input patched", path, len(pairs))

# ① 2026-11-27 강규진 주임 실기: 손님 PC 의 Caps Lock 이 켜져 있으면 기사가 치는 한글이 'ㅁㅔㅁㅗ' 처럼 낱자로 찍힘(끄면 정상).
#    원인 = 원본 src/server/input_service.rs LockModesHandler 가 기사·손님 Caps Lock 이 다르면 키마다 Caps Lock 을 눌렀다가
#    (drop 에서) 다시 눌러 되돌린다 → 그 사이 한글 입력기 조합이 끊긴다.
#    고침 = 맵·번역 방식에서는 한 번 맞춘 뒤 되돌리지 않는다(기사 쪽 상태로 남음 → 다음 키부터 다시 누르지 않음). 옛 방식(레거시)은 원본 그대로.
edit("src/server/input_service.rs", [
    ("        Self {\n            caps_lock_changed,\n            num_lock_changed,\n        }",
     "        Self {\n            caps_lock_changed: caps_lock_changed && is_legacy_mode(key_event),\n            num_lock_changed,\n        }"),
])
print("UP-Desk input patch OK")
