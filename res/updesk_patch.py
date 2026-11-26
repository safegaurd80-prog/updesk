# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk 고객용 빌드 패치 — 우리 서버·열쇠(환경변수)·이름·정책(받기 전용·1회용 번호·설정 잠금·설치 끔)·파일 속성·아이콘 | @KEY: python3 res/updesk_patch.py (보관함 safegaurd80-prog/updesk 의 res/ 에 둔다)
# res/updesk_patch.py — UP-Desk 빌드 패치(빌드 러너에서 1회 실행). 값은 환경변수로만 받는다. 이 파일에 값 없음.
import os, pathlib, shutil
host = os.environ["UPDESK_RELAY_HOST"].strip()
key  = os.environ["UPDESK_PUB_KEY"].strip()
assert host and key and '"' not in host + key, "UPDESK_RELAY_HOST / UPDESK_PUB_KEY 비었거나 따옴표 포함"

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("patched", path, len(pairs))

# ① 서버 주소·공개키·앱 이름 상수 — 공개 릴레이(rs-ny.rustdesk.com) 자체가 바이너리에서 사라진다
edit("libs/hbb_common/src/config.rs", [
    ('pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{host}"];'),
    ('pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     f'pub const RS_PUB_KEY: &str = "{key}";'),
    ('RwLock::new("RustDesk".to_owned())', 'RwLock::new("UP-Desk".to_owned())'),
])

# ② 정책 강제 — 프로세스 시작 직후 load_custom_client() 첫 줄에 박는다(core_main.rs:36 에서 호출됨)
BLOCK = '''pub fn load_custom_client() {
    // ── UP-Desk 고정(빌드 시 박힘 · 사용자 변경 불가): 우리 릴레이만 · 1회용 코드만 · 수신 전용 · 설정화면 숨김
    {
        let host = "__H__";
        let key = "__K__";
        let fixed = [
            ("custom-rendezvous-server", host), ("relay-server", host), ("key", key),
            ("approve-mode", "password"),                       // 승인 = 비밀번호로만
            ("verification-method", "use-temporary-password"),  // 비밀번호 = 1회용(임시)만 → 고정 비번 기능 자체 OFF
            ("allow-remote-config-modification", "N"),          // 원격에서 설정 변경 금지
            ("direct-server", "N"),                             // 직접 IP 접속 OFF
            ("enable-lan-discovery", "N"),                      // LAN 탐색 OFF
            ("enable-check-update", "N"),                       // 공식 업데이트 확인 OFF(우리 배포본이 덮이면 안 됨)
        ];
        let mut o = config::OVERWRITE_SETTINGS.write().unwrap();
        let mut l = config::OVERWRITE_LOCAL_SETTINGS.write().unwrap();
        for (k, v) in fixed {
            o.insert(k.to_owned(), v.to_owned());
            l.insert(k.to_owned(), v.to_owned());
        }
        drop(o);
        drop(l);
        let mut h = config::HARD_SETTINGS.write().unwrap();
        for (k, v) in [("conn-type", "incoming"), ("disable-settings", "Y"), ("disable-account", "Y"),
                       ("disable-installation", "Y")] {   // 설치 기능 끔 — 실행만 쓴다(--install·--silent-install·--update 무시)
            h.insert(k.to_owned(), v.to_owned());
        }
        drop(h);
        // 처음 테마 = 라이트(고객이 설정 → 일반 → 테마에서 다크로 바꿀 수 있음 · 덮어쓰기 아님)
        config::DEFAULT_LOCAL_SETTINGS.write().unwrap().insert("theme".to_owned(), "light".to_owned());
        // "RustDesk 제공" 글자 숨김(누르면 rustdesk.com 이 열리던 것 · 저작권 안내는 '정보' 화면·파일 속성에 남음)
        config::BUILTIN_SETTINGS.write().unwrap().insert("hide-powered-by-me".to_owned(), "Y".to_owned());
    }
'''.replace("__H__", host).replace("__K__", key)
edit("src/common.rs", [("pub fn load_custom_client() {\n", BLOCK)])

# ③ 윈도우 파일 속성(우클릭 → 속성 → 자세히) — ASCII 만 쓴다(.rc 인코딩 안전) · 원본 파일 이름에 64bit(이 빌드는 64비트 전용 — 2026-11-24 강규진 주임)
edit("flutter/windows/runner/Runner.rc", [
    ('VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"', 'VALUE "FileDescription", "UP-Desk Remote Support" "\\0"'),
    ('VALUE "InternalName", "rustdesk" "\\0"',                   'VALUE "InternalName", "UP-Desk" "\\0"'),
    ('VALUE "OriginalFilename", "rustdesk.exe" "\\0"',           'VALUE "OriginalFilename", "UP-Desk-64bit.exe" "\\0"'),
    ('VALUE "ProductName", "RustDesk" "\\0"',                    'VALUE "ProductName", "UP-Desk" "\\0"'),
])
# ④ 받는 파일(겉포장) 속성 — 손님이 우클릭 → 속성에서 보는 이름(11/19 실기에서 RustDesk 로 나왔던 곳) · 저작권 줄은 그대로(AGPL 표기)
edit("libs/portable/Cargo.toml", [
    ('ProductName = "RustDesk"',                   'ProductName = "UP-Desk"'),
    ('OriginalFilename = "rustdesk.exe"',          'OriginalFilename = "UP-Desk-64bit.exe"'),
    ('FileDescription = "RustDesk Remote Desktop"', 'FileDescription = "UP-Desk Remote Support"'),
])
# ④-1 풀리는 폴더 — %LOCALAPPDATA%\\rustdesk → updesk(2026-11-25 강규진 주임). 공식 RustDesk·옛 판과 같은 자리면 윈도우가 그 자리의 옛 이름·아이콘을 기억해 작업표시줄에 보여 준다
edit("libs/portable/src/main.rs", [
    ("dir.join(app_dir_name(&reader.exe))", 'dir.join(app_dir_name(&reader.exe).replace("rustdesk", "updesk"))'),
])

# ⑤ 아이콘 — res/updesk/ 의 우리 아이콘으로 덮는다(원본 파일은 저장소에서 안 바꿈 → 공식 동기화 때 충돌 없음)
for src, dsts in {
    "res/updesk/icon.ico":      ["res/icon.ico", "flutter/windows/runner/resources/app_icon.ico"],  # 받는 파일·실행 창·작업 표시줄
    "res/updesk/tray-icon.ico": ["res/tray-icon.ico"],                                              # 알림 영역(시계 옆)
    "res/updesk/icon.png":      ["res/icon.png", "flutter/assets/icon.png"],                        # 프로그램 안 작은 아이콘
}.items():
    assert pathlib.Path(src).is_file(), f"아이콘 파일 없음: {src}"
    for d in dsts:
        shutil.copyfile(src, d); print("icon", src, "->", d)
# ⑥ 화면 모양(제목줄·색·첫 화면) — 따로 둔 파일(원본 글이 바뀌면 거기서 멈춤)
import runpy
runpy.run_path("res/updesk_ui_patch.py")
# ⑦ 창 동작(설정 → 홈 전환 순서) — 따로 둔 파일
runpy.run_path("res/updesk_window_patch.py")
print("UP-Desk patch OK")
