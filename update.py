import os
import datetime
import pytz
import yaml
import re

DEFAULT_CONTENT = """[WIP]\n\n"""

UPDATE_TIME_START_COMMENT = "<!-- update-time-start -->"
UPDATE_TIME_END_COMMENT = "<!-- update-time-end -->"
MAIN_START_COMMENT = "<!-- main-start -->"
MAIN_END_COMMENT = "<!-- main-end -->"


def get_markdown_url(
    title: str, abbr: str = None, conf: str = None, links: dict = None
) -> str:
    """Get markdown url"""
    links_str = ""
    if links is not None:
        for link_item in links:
            links_str += f" [[{link_item}]]({links[link_item]})"
    abbr_str = "" if abbr is None or abbr == "" else f"**[{abbr}]** "
    conf_str = "" if conf is None else f"(_{conf}_)"
    return f"{abbr_str}{title} {conf_str}{links_str}"


def generate_new_readme(
    src: str, content: str, start_comment: str, end_comment: str
) -> str:
    """Generate a new Readme.md"""
    pattern = f"{start_comment}[\\s\\S]+{end_comment}"
    repl = f"{start_comment}\n\n{content}\n\n{end_comment}"
    if re.search(pattern, src) is None:
        print(
            f"can not find section in src, please check it, it should be {start_comment} and {end_comment}"
        )
    return re.sub(pattern, repl, src)


def write_content(content: str, start_comment: str, end_comment: str):
    with open("README.md", "r", encoding="utf-8") as f:
        src = f.read()
    new_src = generate_new_readme(src, content, start_comment, end_comment)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_src)


def generate_main():
    papers = yaml.safe_load(open("papers.yaml", encoding="utf-8"))
    # print(papers)
    content = ""
    for topic in papers:
        topic = papers[topic]
        # print(topic)
        title = topic["title"]
        list = topic["list"]
        split_by_year = topic.get("split_by_year", False)
        topic_content = f"## {title}\n\n"
        if list is None:
            print(f"list is None for {title}")
            topic_content += DEFAULT_CONTENT
            content += topic_content
            continue

        paper_meta = []
        for paper in list:
            title = paper["title"]
            abbr = paper.get("abbr", None)
            year = paper.get("year", None)
            conf = paper.get("conf", None)
            links = paper.get("links", None)
            if links is not None:
                links = {k: v for k, v in links.items() if v is not None}
            paper_meta.append(
                {
                    "title": title,
                    "abbr": abbr,
                    "year": year,
                    "conf": conf,
                    "links": links,
                }
            )

        if split_by_year:
            for year in sorted(set([p["year"] for p in paper_meta]), reverse=True):
                year_papers = [p for p in paper_meta if p["year"] == year]
                year_content = f"### {year}\n\n"
                for paper in year_papers:
                    paper_str = get_markdown_url(
                        paper["title"], paper["abbr"], paper["conf"], paper["links"]
                    )
                    year_content += f"- {paper_str}\n"
                topic_content += year_content + "\n"
        else:
            for paper in paper_meta:
                paper_str = get_markdown_url(
                    paper["title"], paper["abbr"], paper["conf"], paper["links"]
                )
                topic_content += f"- {paper_str}\n"

        content += topic_content + "\n"

    print(content)
    write_content(content, MAIN_START_COMMENT, MAIN_END_COMMENT)


def update_time():
    tz = pytz.timezone("Asia/Shanghai")
    update_time_str = datetime.datetime.now(tz).strftime("%b %d, %Y %H:%M:%S")
    update_time_str = f"**Last Update: {update_time_str}**"
    print(update_time_str)
    write_content(update_time_str, UPDATE_TIME_START_COMMENT, UPDATE_TIME_END_COMMENT)


if __name__ == "__main__":
    generate_main()
    update_time()
