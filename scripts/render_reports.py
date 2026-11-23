"""Render offline companions from the same source as the bilingual research website."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs"
source = json.loads((DOC / "companion.json").read_text(encoding="utf-8"))


def emit(locale):
    def local(value):
        return value[locale] if isinstance(value, dict) else str(value)

    copy = source["locales"][locale]
    article = source["article"]
    out = ["# " + copy["title"], f"Wenzhang Du · arXiv:2611.24975v1 · v{article['version']} · {article['updated']}", copy["summary"]]
    for part in source["sections"]:
        out.append("## " + local(part["title"]))
        out.extend(part["paragraphs"][locale])
        for block in part["blocks"]:
            kind = block["type"]
            if kind == "figure":
                out.append(f"![{local(block['alt'])}](figures/{Path(block['file']).name})")
                out.append(local(block["caption"]))
            elif kind == "table":
                def row(cells):
                    return "| " + " | ".join(local(c).replace("|", "\\|") for c in cells) + " |"
                rows = [row(block["columns"]), row(["---"] * len(block["columns"]))]
                out.append("\n".join(rows + [row(c) for c in block["rows"]]))
                out.append(local(block["caption"]))
            elif kind == "steps":
                for i, step in enumerate(block["steps"], 1):
                    out.append(f"{i}. **{local(step['title'])}**  {local(step['text'])}" +
                               ("  `" + step["formula"] + "`" if "formula" in step else ""))
            elif kind == "code":
                out.append("```sh\n" + block["code"] + "\n```")
            else:
                raise ValueError(kind)
    out.append("## " + ("Sources" if locale == "en" else "资料来源"))
    out.append("\n".join(f"- [{local(s['label'])}]({s['url']})" for s in source["sources"]))
    (DOC / f"report.{locale}.md").write_bytes(("\n\n".join(out) + "\n").encode())


if __name__ == "__main__":
    for language in ("en", "zh"):
        emit(language)
