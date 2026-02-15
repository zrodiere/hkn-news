import markdown2, datetime, re, sys, yaml

COLORS = {
    'navy': '#003057',
    'gold': '#B3A369',
    'bg': '#F3F3F3',
    'link': '#00629B',
    'text': '#222222',
    'border': '#DDDDDD'
}

CATEGORY_COLORS = {
    "Talk": "#003057",
    "Speaker Series": "#003057",
    "Networking": "#00629B",
    "Professional": "#00629B",
    "Social": "#B3A369",
    "Service": "#5C8727",
    "Competition": "#C0392B",
    "Committees": "#D35400"
}

CALENDAR_LINK = "https://example.com/"
DISCORD_LINK = "https://example.com/"

TEMPLATE_START = """<!DOCTYPE html>
<html><body style="background:#EEEEEE;font-family:sans-serif;margin:0;padding:20px;color:{text};">
<table width="640" align="center" cellpadding="0" cellspacing="0"
style="background:#FFFFFF;border-radius:8px;overflow:hidden;
box-shadow:0 4px 15px rgba(0,0,0,0.1);">

<tr><td height="8" style="background:{gold};"></td></tr>

<tr><td style="padding:22px 40px 8px 16px;background:{navy};">
<table width="100%">
<tr>
<td width="95" valign="top">
[HEADER_IMG]
</td>

<td align="right" valign="top">
<div style="margin-top:-4px;">
<h1 style="margin:0;color:#FFF;font-size:22px;text-transform:uppercase;font-weight:800;">
[TITLE]
</h1>
<p style="margin:4px 0 12px;color:{gold};font-size:11px;letter-spacing:2px;font-weight:600;">
[DATE]
</p>
</div>
</td>
</tr>

<tr>
<td colspan="2" align="center" style="padding-top:0;">
<a href="{calendar}" target="_blank"
style="color:{gold};text-decoration:none;font-size:12px;font-weight:semi-bold;letter-spacing:0.5px"
onmouseover="this.style.color='#d4b86a'"
onmouseout="this.style.color='{gold}'">
📅 Calendar
</a>
<span style="
  display:inline-block;
  width:0.5px;
  height:14px;
  background:rgba(255,255,255,0.6);
  margin:0 14px;
  vertical-align:middle;
  position:relative;
  top:0.5px;
"></span>
<a href="{discord}" target="_blank"
style="color:{gold};text-decoration:none;font-size:12px;font-weight:semi-bold;letter-spacing:0.5px"
onmouseover="this.style.color='#d4b86a'"
onmouseout="this.style.color='{gold}'">
Discord
</a>
</td>
</tr>

</table>
</td></tr>

<tr><td style="padding:28px 40px 40px 40px;">
<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;">
<tr>
<td width="360" valign="top" style="padding-right:30px;">
[MAIN_CONTENT]
</td>
<td width="200" valign="top" style="border-left:1px solid #EEE;padding-left:25px;">
<h3 style="font-size:14px;color:{navy};text-transform:uppercase;margin:0 0 15px 0;
border-bottom:2px solid {gold};padding-bottom:5px;">
Quick Updates
</h3>
[SIDEBAR_CONTENT]
</td></tr></table></td></tr>

<tr><td style="padding:20px 30px 30px 30px;background:#F8F8F8;text-align:center;border-top:1px solid #DDD;">
[FOOTER_IMG]

<p style="font-size:10px;color:#999;margin-top:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:bold;">
ETA KAPPA NU • BETA MU CHAPTER • GEORGIA INSTITUTE OF TECHNOLOGY
</p>

<p style="font-size:11px;color:#777;margin:8px 0 0 0;">
© [YEAR] IEEE-HKN Beta Mu • 
<a href="mailto:hkn@ece.gatech.edu"
style="color:{link};text-decoration:none;font-weight:600;">
hkn@ece.gatech.edu
</a>
</p>

</td></tr>

</table></body></html>
""".format(calendar=CALENDAR_LINK, discord=DISCORD_LINK, **COLORS)


def md_to_html(text):
    if not text:
        return ""

    html = markdown2.markdown(text.strip(), extras=["links", "target-blank-links"])

    html = html.replace(
        '<p>',
        '<p style="margin:0 0 12px 0;font-size:14px;line-height:1.5;">'
    )
    html = html.replace('<ul>', '<ul style="padding-left:20px;margin-bottom:15px;">')
    html = html.replace('<li>', '<li style="margin-bottom:6px;">')

    html = re.sub(
        r'<a href="(.*?)">(.*?)</a>',
        r'<a href="\1" target="_blank" '
        r'style="color:#00629B;font-weight:bold;text-decoration:underline;">\2</a>',
        html
    )

    return html


def parse_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---", 2)
    meta = yaml.safe_load(parts[1]) if len(parts) > 2 else {}
    body = parts[2] if len(parts) > 2 else content

    events, current, intro = [], None, []

    logistics_pattern = r'^(Date|Time|Location|Room|Speaker|RSVP|MIGS|Category):\s*(.*)$'

    for line in body.split("\n"):
        if line.startswith("# "):
            if current:
                events.append(current)
            current = {
                "title": line[2:].strip(),
                "details": {},
                "desc": [],
                "img": "",
                "side": "(Sidebar)" in line,
                "category": None
            }
        elif current:
            m = re.match(logistics_pattern, line.strip(), re.I)
            if m:
                key = m.group(1).capitalize()
                value = m.group(2).strip()

                if key.lower() == "category":
                    current["category"] = value
                else:
                    current["details"][key] = value

            elif line.strip().lower().startswith("image:"):
                current["img"] = line.strip()[6:].strip()
            else:
                current["desc"].append(line)
        else:
            if line.strip() or intro:
                intro.append(line)

    if current:
        events.append(current)

    return meta, "\n".join(intro), events


def main():
    if len(sys.argv) < 2:
        return

    meta, intro, events = parse_md(sys.argv[1])

    icons = {
        'Date': '📅',
        'Time': '🕐',
        'Location': '📍',
        'Room': '🚪',
        'Speaker': '👤',
        'RSVP': '✉️'
    }

    main_list = [e for e in events if not e["side"]]
    side_list = [e for e in events if e["side"]]

    def render_items(items):
        blocks = []

        for i, ev in enumerate(items):
            title = ev["title"].replace("(Sidebar)", "").strip()
            category = ev.get("category")
            cat_color = CATEGORY_COLORS.get(category) if category else None

            img = f'<div style="text-align:center;"><img src="{ev["img"]}" style="max-width:100%;border-radius:4px;margin-bottom:15px;border:1px solid #EEE;"></div>' if ev["img"] else ""

            dets_html = ""
            for k, v in ev["details"].items():
                if k == "Migs":
                    continue
                icon = icons.get(k, "•")

                v_c = markdown2.markdown(
                    v.strip(),
                    extras=["links", "target-blank-links"]
                )

                v_c = re.sub(r'^<p>|</p>$', '', v_c.strip())

                v_c = re.sub(
                    r'<a href="(.*?)"',
                    r'<a href="\1" target="_blank" '
                    r'style="color:#00629B;font-weight:bold;text-decoration:underline;"',
                    v_c
                )

                dets_html += (
                    f'<div style="font-size:12px;margin-bottom:4px;line-height:1.4;">'
                    f'<b>{icon} {k}:</b> {v_c}'
                    f'</div>'
                )

            pills = ""
            if category and cat_color:
                pills += f'<span style="display:inline-block;background:{cat_color};color:#FFF;font-size:10px;font-weight:bold;padding:3px 8px;border-radius:10px;margin-right:6px;text-transform:uppercase;">{category}</span>'

            migs = ev["details"].get("Migs")
            if migs:
                pills += f'<span style="display:inline-block;background:{COLORS["gold"]};color:#FFF;font-size:10px;padding:3px 8px;border-radius:10px;font-weight:bold;">+{migs} MIGS</span>'

            pills_row = f'<div style="margin-top:8px;">{pills}</div>' if pills else ""

            dets_box = f'''
            <div style="background:{COLORS["bg"]};
                padding:12px;
                border-left:4px solid {cat_color if cat_color else COLORS["border"]};
                margin-bottom:15px;">
                {dets_html}
                {pills_row}
            </div>
            ''' if dets_html or pills else ""

            divider = '<div style="border-bottom:1px solid #EEEEEE;margin:20px 0;"></div>' if i < len(items) - 1 else ""

            item_html = '<div style="margin-bottom:10px;">'
            item_html += f'<h2 style="font-size:18px;color:{COLORS["navy"]};margin:5px 0 10px 0;text-transform:uppercase;font-weight:800;">{title}</h2>'
            item_html += f'{img}{dets_box}'
            item_html += md_to_html("\n".join(ev["desc"]))
            item_html += '</div>' + divider

            blocks.append(item_html)

        return "".join(blocks)

    main_final = md_to_html(intro) + render_items(main_list)
    side_final = render_items(side_list)
    current_year = datetime.date.today().year

    final = TEMPLATE_START.replace("[TITLE]", meta.get("newsletter_title", "Newsletter"))
    final = final.replace("[DATE]", datetime.date.today().strftime("%B %d, %Y"))
    final = final.replace("[MAIN_CONTENT]", main_final)
    final = final.replace("[SIDEBAR_CONTENT]", side_final)

    final = final.replace(
        "[HEADER_IMG]",
        f'''
        <div style="margin-top:-4px;margin-left:-6px;">
            <img src="{meta.get("header_image")}" height="62" style="display:block;">
        </div>
        '''
    )

    final = final.replace(
        "[FOOTER_IMG]",
        f'''
        <div style="margin-bottom:2px;">
            <img src="{meta.get("footer_image")}" height="50" style="opacity:0.4;display:block;margin:0 auto;">
        </div>
        '''
    )

    final = final.replace("[YEAR]", str(current_year))

    with open("news.html", "w", encoding="utf-8") as f:
        f.write(final)

    print("Newsletter generated successfully → news.html")


if __name__ == "__main__":
    main()

