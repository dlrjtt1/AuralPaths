"""
Rebuild index.html from viewer_template.html and engine_geom.js, keeping the page data (const D = ...) and the first
two lines of the current index.html (export_viewer.py writes the data; this only refreshes code and layout).
    python tools/build_page.py           # write index.html
    python tools/build_page.py --check   # exit 1 if index.html is not what the template and engine give
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def build():
    rd = lambda f: open(os.path.join(ROOT, f), encoding="utf-8").read()
    idx, tpl, eng = rd("index.html"), rd("viewer_template.html"), rd("engine_geom.js")
    a = idx.index("const D = ") + len("const D = ")
    data = idx[a:idx.index(";\n", a)]
    head = "\n".join(idx.split("\n")[:2]) + "\n"
    body = tpl.replace("/*__DATA__*/null", data, 1).replace("/*__GEOM__*/", eng, 1)
    tail = idx[idx.rindex("</script>") + len("</script>"):]
    return idx, head + body.rstrip("\n") + tail


if __name__ == "__main__":
    old, new = build()
    if "--check" in sys.argv:
        print("index.html is up to date" if old == new else "index.html differs from viewer_template.html + engine_geom.js: run tools/build_page.py")
        sys.exit(0 if old == new else 1)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(new)
    print("index.html written")
