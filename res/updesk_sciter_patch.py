# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk 32비트(옛날 화면 Sciter) 화면 패치 — 64비트와 같은 모양(검정 제목줄·빨강·ID/비번 상자·고객센터 칸) + '⋮' 메뉴 정리 + 32비트 파일 속성 | @KEY: 32비트 빌드에서 updesk_patch.py 다음에 실행
# 2026-11-25 강규진 주임 결정: 32비트도 64비트 예상 그림대로. 64비트는 새 화면 도구(Flutter)가 32비트 윈도우를 못 만들어 옛날 화면을 쓴다.
# 원본 글이 바뀌면 assert 로 멈춘다(조용히 잘못 만들지 않음). 64비트 빌드에서는 실행하지 않는다.
import base64, pathlib

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("sciter patched", path, len(pairs))

# ① 파일 속성 — 32비트 표기(updesk_patch.py 가 64bit 로 박은 것을 바꿈) · 안쪽 rustdesk.exe 도 UP-Desk
edit("libs/portable/Cargo.toml", [('OriginalFilename = "UP-Desk-64bit.exe"', 'OriginalFilename = "UP-Desk-32bit.exe"')])
edit("Cargo.toml", [
    ('ProductName = "RustDesk"\nFileDescription = "RustDesk Remote Desktop"\nOriginalFilename = "rustdesk.exe"',
     'ProductName = "UP-Desk"\nFileDescription = "UP-Desk Remote Support"\nOriginalFilename = "UP-Desk-32bit.exe"'),
])

# ② 제목줄 아이콘 — 옛날 화면은 아이콘 그림이 프로그램 안에 박혀 있음 → 우리 아이콘
s = pathlib.Path("src/ui.rs").read_text(encoding="utf-8")
mark = '#[cfg(not(target_os = "macos"))] // 128x128 no padding\n    {\n        "data:image/png;base64,'
assert s.count(mark) == 1, "src/ui.rs: 아이콘 자리를 못 찾음"
i = s.index(mark) + len(mark); j = s.index('"', i)
s = s[:i] + base64.b64encode(pathlib.Path("res/updesk/icon.png").read_bytes()).decode() + s[j:]
pathlib.Path("src/ui.rs").write_text(s, encoding="utf-8"); print("sciter icon patched")

# ③ 색 — 파랑 → 브랜드 빨강 · 다크 바탕 #141517
edit("src/ui/common.css", [
    ("    var(accent): #0071ff;\n    var(button): #2C8CFF;", "    var(accent): #CC0000;\n    var(button): #CC0000;"),
    ("    var(menu-hover): #D7E4F2;", "    var(menu-hover): #F6DADA;"),
    ("html.darktheme {\n    var(bg): #252525;", "html.darktheme {\n    var(bg): #141517;"),
])

# ④ 검정 제목줄 — 원본 원격 화면(remote.html)과 같은 방식(창 테두리를 직접 그림)
edit("src/ui/index.html", [
    ("<html>", '<html window-resizable window-frame="extended">'),
    ("</head>\n", '</head>\n<header>\n    <div.window-icon role="window-icon"><icon /></div>\n'
                  '    <caption role="window-caption"><span.brand>UHDPRO</span>&nbsp;&nbsp;<span.sep>|</span>&nbsp;&nbsp;<span.app>UP-Desk</span></caption>\n'
                  '    <div.window-buttons />\n</header>\n'),
])

# ⑤ 첫 화면 — 창 폭·높이 · ID/비밀번호 상자 · 고객센터 칸 · '⋮' 메뉴는 테마·언어·정보만
def esc(t):  # 한글은 \uXXXX 로 넣는다(옛날 화면 도구가 화면 원본의 한글 바이트를 윈도우 기본 글자표로 읽어 깨짐 · 11/25 실기)
    return '{"' + "".join(c if ord(c) < 128 else "\\u%04X" % ord(c) for c in t) + '"}'
SUPPORT = ('{incoming_only ? <div .updesk-support><div .t>' + esc("UHDPRO 고객센터") + '</div><div .tel>1666-4331</div>'
           '<div .d>' + esc("통화 중인 상담 기사에게만") + '</div><div .d>' + esc("ID와 비밀번호를 알려 주세요.") + '</div></div> : ""}')
edit("src/ui/index.tis", [
    ("const incoming_only_width = 180;", "const incoming_only_width = 300;"),
    ('const hide_stop_service = handler.get_builtin_option("hide-stop-service") == "Y";',
     'const hide_stop_service = handler.get_builtin_option("hide-stop-service") == "Y" || disable_settings;'),
    ("disable_installation) ? 300 : 390));", "disable_installation) ? 560 : 560));"),
    ("scaleIt(incoming_only ? 390 : 600));", "scaleIt(incoming_only ? 560 : 600));"),
    ("        audioInputMenu = this;\n    }\n\n    function render() {\n",
     "        audioInputMenu = this;\n    }\n\n    function render() {\n        if (disable_settings) return <li style=\"display:none\" />;\n"),
    ("    function render() {\n        var has_hwcodec = handler.has_hwcodec();",
     "    function render() {\n        if (disable_settings) return <li style=\"display:none\" />;\n        var has_hwcodec = handler.has_hwcodec();"),
    ("<li #about>{translate('About')} {\" \"}{handler.get_app_name()}</li>",
     "<li #about>{handler.get_app_name()} {\" \"}{translate('About')}</li>"),
    ("{!outgoing_only && <div .your-desktop>", "{!outgoing_only && <div .your-desktop .updesk-id>"),
    ("{!outgoing_only && <PasswordArea />}", "{!outgoing_only && <PasswordArea />}\n                        " + SUPPORT),
    ("        <div .your-desktop>\n            <div>{translate('One-time Password')}</div>",
     "        <div .your-desktop .updesk-pw>\n            <div>{translate('One-time Password')}</div>"),
])
pathlib.Path("src/ui/index.tis").write_text(pathlib.Path("src/ui/index.tis").read_text(encoding="utf-8") + '''
// UP-Desk: black title bar - minimize/close buttons + our icon
if (!is_osx) {
    $(div.window-buttons).content(<div>
        <button.window tabindex="-1" role="window-minimize" #minimize><div /></button>
        <button.window tabindex="-1" role="window-close" #close><div /></button>
    </div>);
    $(div.window-icon>icon).style.set { "background-image": "url('" + handler.get_icon() + "')" };
    adjustBorder();
    view << event statechange { adjustBorder(); }
}
''', encoding="utf-8")

CLOSE_WHITE = ("iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMBAMAAACkW0HUAAAAD1BMVEUAAAD///////////////+PQt5oAAAABXRSTlMAO+hBqp3RzLsAAAAuSURBVAjXY3BkAAIRBiEDBgZGZRACMkEYxAJyQRwgV5EBSsEEoUqgGqDaoYYBALKmBEEnAGy8AAAAAElFTkSuQmCC")
CSS = '''
/* UP-Desk 32-bit: same look as 64-bit */
html { font-family: "Malgun Gothic", "Segoe UI", system; }
header { background: #111111; height: 32px; border-bottom: none; }
html.darktheme header { background: #1D1E21; }
header div.window-icon { size: 32px; }
header div.window-icon icon { size: 18px; }
header caption { padding-left: 4px; line-height: 32px; white-space: nowrap; }
header caption span.brand { color: #CC0000; font-weight: 900; font-size: 15px; }
header caption span.sep { color: #888888; font-size: 13px; padding: 0 6px; }
header caption span.app { color: white; font-weight: bold; font-size: 13px; }
header button.window { height: 32px; }
header button.window:hover { background: #333333; }
header button.window#minimize { right: 42px; }
header button.window#minimize div { border-bottom: #dddddd solid 1px; }
header button.window#close div { background-image: url('data:image/png;base64,__CLOSE__'); }
.left-pane > div:nth-child(1) { padding: 16px; padding-bottom: 60px; border-spacing: 13px; }
.left-pane .title { font-weight: bold; font-size: 1.6em; }
.left-pane div.lighter-text { word-wrap: normal; margin-bottom: 4px; }
div.updesk-id, div.updesk-pw, div.updesk-support { background: white; border: #D6D8DC 1px solid; border-radius: 9px; padding: 8px 10px; }
html.darktheme div.updesk-id, html.darktheme div.updesk-pw, html.darktheme div.updesk-support { background: #232428; border: none; padding-left: 14px; }
html.darktheme div.updesk-id { border-left: #CC0000 solid 4px; padding-left: 12px; }
div.updesk-id div#myid svg#menu { right: 0; }
div.updesk-id input[type=text] { font-size: 26px; font-weight: bold; height: 1.3em; color: color(text); }
div.updesk-pw div.eye-area { flow: horizontal; }
div.updesk-pw div.eye-area > input { width: *; height: auto; padding: 6px 10px; border: #D6D8DC 1px solid; border-radius: 6px; background: #F3F4F6; color: color(text); font-size: 18px; font-weight: bold; }
html.darktheme div.updesk-pw div.eye-area > input { background: #2A2B30; border-color: #3A3B40; }
div.updesk-pw svg#refresh-password { stroke: #555555; size: 18px; margin: * 0 * 8px; }
html.darktheme div.updesk-pw svg#refresh-password { stroke: #BBBBBB; }
div.updesk-support { padding: 14px 16px 16px; }
div.updesk-support .t { font-weight: bold; font-size: 15px; }
div.updesk-support .tel { color: #CC0000; font-weight: 900; font-size: 26px; margin: 2px 0 4px; }
div.updesk-support .d { font-size: 13px; line-height: 1.5em; color: color(light-text); }
menu#config-options > div.separator { display: none; }
menu#config-options > li#allow-darktheme.line-through { text-decoration-line: none; color: color(text); }
'''.replace("__CLOSE__", CLOSE_WHITE)
p = pathlib.Path("src/ui/index.css"); p.write_text(p.read_text(encoding="utf-8") + CSS, encoding="utf-8")
print("UP-Desk sciter patch OK")
