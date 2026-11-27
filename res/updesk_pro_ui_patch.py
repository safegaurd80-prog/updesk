# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk Pro(기사용) 화면 패치 — 남색 제목줄(UHDPRO | UP-Desk Pro + '기사용' 표시) · 강조색 파랑 · 원본 기사 화면 배치는 그대로 | @KEY: updesk_pro_patch.py 끝에서 runpy 로 실행
# 2026-11-26 강규진 주임: 고객용(검정 제목줄·빨강)과 한눈에 구분 — 예상 그림 UP-Desk_Pro_기사용_예상_20261126.png
# 원본 글이 바뀌면 assert 로 멈춘다(조용히 잘못 만들지 않음).
import pathlib

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("pro ui patched", path, len(pairs))

BLUE = "2F6FD8"
NAVY = "0xFF14213D"
# ① 색 — 원본 파랑을 우리 기사용 파랑으로(입력칸 테두리·연결 단추·선택 표시)
edit("flutter/lib/common.dart", [
    ("static const Color accent = Color(0xFF0071FF);", f"static const Color accent = Color(0xFF{BLUE});"),
    ("static const Color accent50 = Color(0x770071FF);", f"static const Color accent50 = Color(0x77{BLUE});"),
    ("static const Color accent80 = Color(0xAA0071FF);", f"static const Color accent80 = Color(0xAA{BLUE});"),
    ("static const Color button = Color(0xFF2C8CFF);", f"static const Color button = Color(0xFF{BLUE});"),
])

# ② 제목줄 — 남색 바탕 + 아이콘 · UHDPRO(빨강) | UP-Desk Pro(흰색) + 파란 '기사용' 표시 · 탭 글자는 밝게
edit("flutter/lib/desktop/widgets/tabbar_widget.dart", [
    ("child: _buildBar(),", f"child: ColoredBox(color: const Color({NAVY}), child: _buildBar()),"),
    ('''                        Offstage(
                            offstage: !showTitle,
                            child: const Text(
                              "RustDesk",
                              style: TextStyle(fontSize: 13),
                            ).marginOnly(left: 2))''',
     f'''                        Row(children: [
                          const Text("UHDPRO",
                                  style: TextStyle(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w900,
                                      color: Color(0xFFCC0000)))
                              .marginOnly(left: 6),
                          const Text("|",
                                  style: TextStyle(
                                      fontSize: 13, color: Color(0x88FFFFFF)))
                              .marginOnly(left: 6, right: 6),
                          const Text("UP-Desk Pro",
                              style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white)),
                          Container(
                            margin: const EdgeInsets.only(left: 8),
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 1),
                            decoration: BoxDecoration(
                                color: const Color(0xFF{BLUE}),
                                borderRadius: BorderRadius.circular(9)),
                            child: const Text("기사용",
                                style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.white)),
                          ),
                        ])'''),
    ("      unSelectedIconColor: Color.fromARGB(255, 96, 96, 96),",
     "      unSelectedIconColor: Color.fromARGB(255, 221, 221, 221),"),
    ("      hoverColor: Colors.white54,", "      hoverColor: Colors.white24,"),
    ("      selectedTextColor: Colors.black,", "      selectedTextColor: Colors.white,"),
    ("      unSelectedTextColor: Color.fromARGB(255, 112, 112, 112),", "      unSelectedTextColor: Color.fromARGB(255, 170, 170, 170),"),
    ("      selectedIconColor: Color.fromARGB(255, 26, 26, 26),", "      selectedIconColor: Color.fromARGB(255, 221, 221, 221),"),
    ("      selectedTabBackgroundColor: Colors.white54);", "      selectedTabBackgroundColor: Colors.white24);"),
])

# ③ 정보 화면 — 고객용과 같이 번역자 문구를 빼고, 라이선스 글이 비면 빈 줄을 만들지 않음(저작권·라이선스 줄은 그대로)
edit("flutter/lib/desktop/pages/desktop_setting_page.dart", [
    ("                          Text(\n                            translate('Slogan_tip'),\n                            style: TextStyle(\n"
     "                                fontWeight: FontWeight.w800,\n                                color: Colors.white),\n                          )",
     "                          const SizedBox.shrink()"),
    ("Purslane Tech Pte. Ltd.\\n$license'", "Purslane Tech Pte. Ltd.${license.isEmpty ? '' : '\\n$license'}'"),
])
print("UP-Desk Pro ui patch OK")
