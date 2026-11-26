# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk Pro(기사용) 빌드 패치 — 우리 서버·열쇠 고정(환경변수)·이름 UP-Desk Pro·파일 속성·전용 폴더·파란 아이콘 · 접속하는 쪽이라 받기 전용/설정 잠금은 넣지 않음 | @KEY: python3 res/updesk_pro_patch.py (updesk-pro.yml 에서만)
# 2026-11-26 강규진 주임 결정: 기사 PC 는 원본 RustDesk 대신 우리 기사용 판 — 고객용(UP-Desk)과 이름·색·아이콘·파일 이름·폴더로 구분.
# 고객용 updesk_patch.py 와 따로 둔다(고객용 정책 — 받기 전용·1회용 번호·설정 잠금 — 이 기사용에 섞이면 안 되고, 반대도 마찬가지).
import os, pathlib, runpy, shutil
host = os.environ["UPDESK_RELAY_HOST"].strip()
key  = os.environ["UPDESK_PUB_KEY"].strip()
assert host and key and '"' not in host + key, "UPDESK_RELAY_HOST / UPDESK_PUB_KEY 비었거나 따옴표 포함"

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("pro patched", path, len(pairs))

# ① 서버 주소·공개키·앱 이름 — 공개 중계 서버가 프로그램에서 사라진다
edit("libs/hbb_common/src/config.rs", [
    ('pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{host}"];'),
    ('pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     f'pub const RS_PUB_KEY: &str = "{key}";'),
    ('RwLock::new("RustDesk".to_owned())', 'RwLock::new("UP-Desk Pro".to_owned())'),
])

# ② 정책 — 우리 서버·열쇠만 고정(기사가 4칸 입력 안 함 · 바꿀 수 없음). 기사는 접속하는 쪽이라 나머지 설정은 원본 그대로 둔다.
BLOCK = '''pub fn load_custom_client() {
    // ── UP-Desk Pro(기사용) 고정: 우리 중계 서버·열쇠만 · 공식 업데이트 확인 끔
    {
        let host = "__H__";
        let key = "__K__";
        let fixed = [
            ("custom-rendezvous-server", host), ("relay-server", host), ("key", key),
            ("enable-check-update", "N"),
        ];
        let mut o = config::OVERWRITE_SETTINGS.write().unwrap();
        let mut l = config::OVERWRITE_LOCAL_SETTINGS.write().unwrap();
        for (k, v) in fixed {
            o.insert(k.to_owned(), v.to_owned());
            l.insert(k.to_owned(), v.to_owned());
        }
        drop(o);
        drop(l);
        config::DEFAULT_LOCAL_SETTINGS.write().unwrap().insert("theme".to_owned(), "light".to_owned());
        let mut b = config::BUILTIN_SETTINGS.write().unwrap();
        b.insert("hide-powered-by-me".to_owned(), "Y".to_owned());
        b.insert("hide-server-settings".to_owned(), "Y".to_owned());
        drop(b);
    }
'''.replace("__H__", host).replace("__K__", key)
edit("src/common.rs", [("pub fn load_custom_client() {\n", BLOCK)])

# ③ 파일 속성(우클릭 → 속성 → 자세히) — ASCII 만
edit("flutter/windows/runner/Runner.rc", [
    ('VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"', 'VALUE "FileDescription", "UP-Desk Pro Remote Support" "\\0"'),
    ('VALUE "InternalName", "rustdesk" "\\0"',                   'VALUE "InternalName", "UP-Desk-Pro" "\\0"'),
    ('VALUE "OriginalFilename", "rustdesk.exe" "\\0"',           'VALUE "OriginalFilename", "UP-Desk-Pro-64bit.exe" "\\0"'),
    ('VALUE "ProductName", "RustDesk" "\\0"',                    'VALUE "ProductName", "UP-Desk Pro" "\\0"'),
])
edit("libs/portable/Cargo.toml", [
    ('ProductName = "RustDesk"',                   'ProductName = "UP-Desk Pro"'),
    ('OriginalFilename = "rustdesk.exe"',          'OriginalFilename = "UP-Desk-Pro-64bit.exe"'),
    ('FileDescription = "RustDesk Remote Desktop"', 'FileDescription = "UP-Desk Pro Remote Support"'),
])
# ④ 풀리는 폴더 — 고객용(updesk)·원본(rustdesk)과 다른 자리(같은 PC 에서 서로 덮어쓰지 않게)
edit("libs/portable/src/main.rs", [
    ("dir.join(app_dir_name(&reader.exe))", 'dir.join(app_dir_name(&reader.exe).replace("rustdesk", "updesk-pro"))'),
])

# ⑤ 아이콘 — 파란 화살표판(res/updesk/pro/)
for src, dsts in {
    "res/updesk/pro/icon.ico":      ["res/icon.ico", "flutter/windows/runner/resources/app_icon.ico"],
    "res/updesk/pro/tray-icon.ico": ["res/tray-icon.ico"],
    "res/updesk/pro/icon.png":      ["res/icon.png", "flutter/assets/icon.png"],
}.items():
    assert pathlib.Path(src).is_file(), f"아이콘 파일 없음: {src}"
    for d in dsts:
        shutil.copyfile(src, d); print("icon", src, "->", d)

# ⑥ 화면 — 남색 제목줄 · 파랑 · '기사용' 표시(따로 둔 파일)
runpy.run_path("res/updesk_pro_ui_patch.py")
print("UP-Desk Pro patch OK")
