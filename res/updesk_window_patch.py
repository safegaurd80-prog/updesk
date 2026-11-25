# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk 고객용 창 동작 패치 — 설정에서 홈으로 갈 때 홈 화면으로 먼저 바꾼 뒤 창을 줄인다 | @KEY: python3 res/updesk_patch.py 끝에서 실행(보관함 safegaurd80-prog/updesk 의 res/)
# res/updesk_window_patch.py — 창 동작(화면 전환 순서). 값(주소·키) 없음. 화면 모양은 updesk_ui_patch.py 에 있다.
# 원본 글이 바뀌면 assert 로 멈춘다(조용히 잘못 만들지 않음).
import pathlib

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("window patched", path, len(pairs))

# ① 2026-11-25 강규진 주임(영상): 설정에서 '홈'을 누르면 창이 먼저 줄고 화면은 0.1초 뒤에 바뀌어, 그 사이 설정 글이 좁은 창에 찌그러져 보였다.
#    원인 = 원본 tabbar_widget.dart jumpTo() 가 jumpToPage 를 100ms 늦추는데, 받기 전용 onSelected 는 창 크기를 바로 바꾼다.
#    고침 = 홈으로 갈 때는 홈 화면으로 먼저 바꾸고(같은 자리에서 바로) 그다음 창을 줄인다. 처음 켤 때는 화면이 아직 없어 hasClients 가 거짓 → 건너뜀.
edit("flutter/lib/desktop/pages/desktop_tab_page.dart", [
    ("          windowManager.setSize(getIncomingOnlyHomeSize());\n          setResizable(false);",
     "          final pc = tabController.state.value.pageController;\n"
     "          if (pc.hasClients) pc.jumpToPage(0); // 홈 = 첫 탭\n"
     "          windowManager.setSize(getIncomingOnlyHomeSize());\n          setResizable(false);"),
])
print("UP-Desk window patch OK")
