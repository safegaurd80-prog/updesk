# @LAYER: 도구 | @PORT: 없음(빌드 러너) | @ROLE: UP-Desk 고객용 화면 패치 — 색·제목줄·첫 화면·새 비밀번호 단추 색·고객센터 번호 칸 | @KEY: updesk_patch.py 끝에서 runpy 로 실행
# res/updesk_ui_patch.py — UP-Desk 화면 모양 패치(updesk_patch.py 끝에서 실행). 값(주소·키) 없음.
# 2026-11-20 강규진 주임 결정: 지금 고객용 화면의 칸·글은 그대로 + 제목줄(아이콘·UHDPRO·UP-Desk) + 시안 모양(라이트 기본 / 다크 선택)
# 원본 글이 바뀌면 assert 로 멈춘다(조용히 잘못 만들지 않음).
import pathlib

def edit(path, pairs):
    p = pathlib.Path(path); s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        c = s.count(old)
        assert c == 1, f"{path}: 기대 문자열이 {c}회 발견됨(원본이 바뀐 듯) → {old[:60]!r}"
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8"); print("ui patched", path, len(pairs))

DARK = "Theme.of(context).brightness == Brightness.dark"

# ① 색 — 파랑 → 브랜드 빨강(#CC0000) · 바탕 라이트=흰색 / 다크=#141517
edit("flutter/lib/common.dart", [
    # 2026-11-25 가운데 맞춤: 받기 전용 창이 안쪽 폭 280 을 다 보여 주게(창 테두리 몫 11 → 16 · 실측: 보이는 폭 275~276 → 오른쪽 4~5 잘려 왼쪽 16 / 오른쪽 7)
    ("final magicWidth = isWindows ? 11.0 : 2.0;", "final magicWidth = isWindows ? 16.0 : 2.0;"),
    ("static const Color accent = Color(0xFF0071FF);", "static const Color accent = Color(0xFFCC0000);"),
    ("static const Color accent50 = Color(0x770071FF);", "static const Color accent50 = Color(0x77CC0000);"),
    ("static const Color accent80 = Color(0xAA0071FF);", "static const Color accent80 = Color(0xAACC0000);"),
    ("static const Color button = Color(0xFF2C8CFF);", "static const Color button = Color(0xFFCC0000);"),
    ("primary: Colors.blue, secondary: accent, background: grayBg),",
     "primary: accent, secondary: accent, background: Colors.white),"),
    ("      primary: Colors.blue,\n      secondary: accent,\n      background: Color(0xFF24252B),",
     "      primary: accent,\n      secondary: accent,\n      background: Color(0xFF141517),"),
])

# ② 제목줄 — 검정 바탕 + 아이콘 · UHDPRO(빨강) | UP-Desk(흰색) · 창 단추는 밝은 회색
edit("flutter/lib/desktop/widgets/tabbar_widget.dart", [
    ("child: _buildBar(),",
     f"child: ColoredBox(color: {DARK} ? const Color(0xFF1D1E21) : const Color(0xFF111111), child: _buildBar()),"),
    ('''                        Offstage(
                            offstage: !showTitle,
                            child: const Text(
                              "RustDesk",
                              style: TextStyle(fontSize: 13),
                            ).marginOnly(left: 2))''',
     '''                        Row(children: [
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
                          const Text("UP-Desk",
                              style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white)),
                        ])'''),
    ("      unSelectedIconColor: Color.fromARGB(255, 96, 96, 96),",
     "      unSelectedIconColor: Color.fromARGB(255, 221, 221, 221),"),
    ("      hoverColor: Colors.white54,", "      hoverColor: Colors.white24,"),
    # 라이트에서도 제목줄이 검정이라 탭 글자(예: 설정 창을 열면 생기는 탭)를 밝게
    ("      selectedTextColor: Colors.black,", "      selectedTextColor: Colors.white,"),
    ("      unSelectedTextColor: Color.fromARGB(255, 112, 112, 112),", "      unSelectedTextColor: Color.fromARGB(255, 170, 170, 170),"),
    ("      selectedIconColor: Color.fromARGB(255, 26, 26, 26),", "      selectedIconColor: Color.fromARGB(255, 221, 221, 221),"),
    ("      selectedTabBackgroundColor: Colors.white54);", "      selectedTabBackgroundColor: Colors.white24);"),
    # 2026-11-25: 받기 전용 홈 화면(작은 창)에서는 탭을 안 그림 — 설정에 갔다 오면 탭이 2개라 잘린 '홈' 단추가 눌렸음 · 안 고른 탭 아이콘 = 라이트 짙은 회색 / 다크 파랑
    ("children: isHideSingleItem()", "children: (isHideSingleItem() ||\n                (bind.isIncomingOnly() && isInHomePage()))"),
    ("      unSelectedTabIconColor: Color.fromARGB(255, 162, 203, 241),", "      unSelectedTabIconColor: Color.fromARGB(255, 119, 119, 119),"),
    ("      unSelectedTabIconColor: Color.fromARGB(255, 30, 65, 98),", "      unSelectedTabIconColor: Color.fromARGB(255, 63, 127, 208),"),
])

# ③ 첫 화면 — 굵은 제목 · ID 테두리 상자(다크는 빨간 막대 상자) · 비밀번호 입력칸 모양 · 설치 안내 상자 + 빨간 단추
edit("flutter/lib/desktop/pages/desktop_home_page.dart", [
    # 좌우 여백 16 · 16(가운데 맞춤) — '내 데스크탑' 글도 상자 왼쪽 줄에(글 폭은 그대로 244)
    ("const EdgeInsets.only(left: 20.0, right: 16, top: 16.0, bottom: 5),", "const EdgeInsets.only(left: 16.0, right: 20, top: 16.0, bottom: 5),"),
    ("style: Theme.of(context).textTheme.titleLarge,",
     "style: Theme.of(context)\n                        .textTheme\n                        .titleLarge\n                        ?.copyWith(fontWeight: FontWeight.w800),"),
    ('''    return Container(
      margin: const EdgeInsets.only(left: 20, right: 11),
      height: 57,''',
     f'''    final isDark = {DARK};
    return Container(
      margin: const EdgeInsets.only(left: 16, right: 16, top: 10),
      padding: const EdgeInsets.fromLTRB(10, 6, 2, 6),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF232428) : Colors.white,
        border: isDark ? null : Border.all(color: const Color(0xFFD6D8DC)),
        borderRadius: BorderRadius.circular(9),
      ),
      height: 80,'''),
    ('''          Container(
            width: 2,
            decoration: const BoxDecoration(color: MyTheme.accent),''',
     '''          Container(
            width: isDark ? 4 : 0,
            decoration: const BoxDecoration(color: MyTheme.accent),'''),
    ('''                        style: TextStyle(
                          fontSize: 22,
                        ),''',
     '''                        style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                        ),'''),
    # 2026-11-25 '가' 규격: ID 숫자 뒤 회색 띠(입력칸 기본 바탕색) 없앰 · 비밀번호 칸도 ID 와 같은 폭의 상자
    ("                          border: InputBorder.none,\n                          contentPadding: EdgeInsets.only(top: 10, bottom: 10),",
     "                          filled: false,\n                          border: InputBorder.none,\n                          contentPadding: EdgeInsets.only(top: 10, bottom: 10),"),
    ("margin: EdgeInsets.only(left: 20.0, right: 16, top: 13, bottom: 13),",
     f"""margin: EdgeInsets.only(left: 16.0, right: 16, top: 13, bottom: 13),
      padding: EdgeInsets.fromLTRB({DARK} ? 14 : 10, 6, 8, 10),
      decoration: BoxDecoration(
        color: {DARK} ? const Color(0xFF232428) : Colors.white,
        border: {DARK} ? null : Border.all(color: const Color(0xFFD6D8DC)),
        borderRadius: BorderRadius.circular(9),
      ),"""),
    ('''          Container(
            width: 2,
            height: 52,
            decoration: BoxDecoration(color: MyTheme.accent),''',
     '''          Container(
            width: 0,
            height: 52,
            decoration: BoxDecoration(color: MyTheme.accent),'''),
    ('''                            decoration: InputDecoration(
                              border: InputBorder.none,
                              contentPadding:
                                  EdgeInsets.only(top: 14, bottom: 10),
                            ),
                            style: TextStyle(fontSize: 15),''',
     f'''                            decoration: InputDecoration(
                              filled: true,
                              fillColor: {DARK}
                                  ? const Color(0xFF2A2B30)
                                  : const Color(0xFFF3F4F6),
                              enabledBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(6),
                                  borderSide: BorderSide(
                                      color: {DARK}
                                          ? const Color(0xFF3A3B40)
                                          : const Color(0xFFD6D8DC))),
                              focusedBorder: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(6),
                                  borderSide: BorderSide(
                                      color: {DARK}
                                          ? const Color(0xFF3A3B40)
                                          : const Color(0xFFD6D8DC))),
                              isDense: true,
                              contentPadding:
                                  EdgeInsets.fromLTRB(12, 10, 12, 10),
                            ),
                            style: TextStyle(
                                fontSize: 18, fontWeight: FontWeight.w700),'''),
    # 설치 안내 칸: 분홍 그라데이션 → 상자(라이트 흰+테두리 / 다크 #232428)
    ('''          margin: EdgeInsets.fromLTRB(
              0, marginTop, 0, bind.isIncomingOnly() ? marginTop : 0),''',
     '''          margin: EdgeInsets.fromLTRB(
              16, marginTop, 16, bind.isIncomingOnly() ? marginTop : 0),'''),
    ('''              decoration: BoxDecoration(
                  gradient: LinearGradient(
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
                colors: [
                  Color.fromARGB(255, 226, 66, 188),
                  Color.fromARGB(255, 244, 114, 124),
                ],
              )),
              padding: EdgeInsets.all(20),''',
     f'''              decoration: BoxDecoration(
                  color: {DARK}
                      ? const Color(0xFF232428)
                      : Colors.white,
                  border: {DARK}
                      ? null
                      : Border.all(color: const Color(0xFFD6D8DC)),
                  borderRadius: BorderRadius.circular(9)),
              padding: EdgeInsets.all(14),'''),
    ('''                                style: TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15),''',
     '''                                style: TextStyle(
                                    color: Theme.of(context)
                                        .textTheme
                                        .titleLarge
                                        ?.color,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15),'''),
    ('''                            style: TextStyle(
                                height: 1.5,
                                color: Colors.white,
                                fontWeight: FontWeight.normal,
                                fontSize: 13),
                          ).marginOnly(bottom: 20)''',
     '''                            style: TextStyle(
                                height: 1.5,
                                color: Theme.of(context)
                                    .textTheme
                                    .titleLarge
                                    ?.color
                                    ?.withOpacity(0.8),
                                fontWeight: FontWeight.normal,
                                fontSize: 13),
                          ).marginOnly(bottom: 14)'''),
    ('''                                      width: 150,
                                      padding: 8,
                                      isOutline: true,
                                      text: translate(btnText),
                                      textColor: Colors.white,
                                      borderColor: Colors.white,
                                      textSize: 20,
                                      radius: 10,''',
     '''                                      width: 220,
                                      padding: 8,
                                      isOutline: false,
                                      text: translate(btnText),
                                      textColor: Colors.white,
                                      borderColor: MyTheme.accent,
                                      textSize: 16,
                                      radius: 6,'''),
    ('''                                        style: TextStyle(
                                            decoration:
                                                TextDecoration.underline,
                                            color: Colors.white,
                                            fontSize: 12),''',
     '''                                        style: TextStyle(
                                            decoration:
                                                TextDecoration.underline,
                                            color: MyTheme.accent,
                                            fontSize: 12),'''),
    ('''              icon: Icon(
                Icons.close,
                color: Colors.white,
                size: 20,
              ),''',
     '''              icon: Icon(
                Icons.close,
                color: Theme.of(context).textTheme.titleLarge?.color,
                size: 20,
              ),'''),
])
# ④ 2026-11-24 강규진 주임: 새 비밀번호 단추를 라이트·다크 모두 잘 보이게 · '설치하기' 칸 자리에 고객센터 번호 칸(설치 기능은 updesk_patch.py 에서 끔)
# 2026-11-25: 칸을 ID 상자와 같은 폭으로(width 무한 — 안 주면 글 길이만큼만 넓어져 가운데로 몰림 · #3 실기) + 상자·글자 키움(#4) → '가' 규격(#5): 세 칸 같은 폭·같은 글 시작 줄(라이트 33 · 다크 37) · 번호 = ID 숫자 크기 26 · 칸 간격 13
SUPPORT_CARD = """  // UP-Desk: 설치 안내 칸 자리 - 고객센터 번호(설치 기능은 꺼 둠)
  Widget buildUpdeskSupportCard() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = Theme.of(context).textTheme.titleLarge?.color;
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 20),
      padding: EdgeInsets.fromLTRB(isDark ? 21 : 17, 14, 17, 16),
      decoration: BoxDecoration(
          color: isDark ? const Color(0xFF232428) : Colors.white,
          border: isDark ? null : Border.all(color: const Color(0xFFD6D8DC)),
          borderRadius: BorderRadius.circular(9)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('UHDPRO 고객센터',
              style: TextStyle(
                  color: textColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 15)),
          const Text('1666-4331',
                  style: TextStyle(
                      color: MyTheme.accent,
                      fontWeight: FontWeight.w900,
                      fontSize: 26))
              .marginOnly(top: 2, bottom: 4),
          Text('통화 중인 상담 기사에게만\\nID와 비밀번호를 알려 주세요.',
              style: TextStyle(
                  height: 1.5,
                  color: textColor?.withOpacity(0.8),
                  fontSize: 13)),
        ],
      ),
    );
  }

"""
edit("flutter/lib/desktop/pages/desktop_home_page.dart", [
    ("""                                  color: refreshHover.value
                                      ? textColor
                                      : Color(0xFFDDDDDD),""",
     f"""                                  color: refreshHover.value
                                      ? textColor
                                      : ({DARK}
                                          ? const Color(0xFFBBBBBB)
                                          : const Color(0xFF555555)),"""),
    ("    if (isWindows && !bind.isDisableInstallation()) {\n",
     "    if (isWindows && !bind.mainIsInstalled()) {\n      return buildUpdeskSupportCard();\n    }\n\n"
     "    if (isWindows && !bind.isDisableInstallation()) {\n"),
    ("  Widget buildInstallCard(String title, String content, String btnText,\n",
     SUPPORT_CARD + "  Widget buildInstallCard(String title, String content, String btnText,\n"),
])
# ⑤ 2026-11-26 강규진 주임: 정보 화면의 번역자 문구(Slogan_tip) 뺌 — 저작권·라이선스 줄은 그대로(32비트도 같음)
edit("flutter/lib/desktop/pages/desktop_setting_page.dart", [("                          Text(\n                            translate('Slogan_tip'),\n                            style: TextStyle(\n                                fontWeight: FontWeight.w800,\n                                color: Colors.white),\n                          )", "                          const SizedBox.shrink()")])
print("UP-Desk ui patch OK")
