from bs4 import BeautifulSoup, Doctype, element
import re
from datetime import datetime
from parser_base import ParserBase


class KYParseHtml(ParserBase):
    def __init__(self, input_file_name):
        super().__init__()
        self.class_regex = {'ul': '^CHAPTER', 'head2': '^CHAPTER', 'title': '^(TITLE)', 'sec_head': r'^([^\s]+[^\D]+)',
                            'junk': '^(Text)', 'ol': r'^(\(1\))', 'head4': '^(NOTES TO DECISIONS)'}
        self.title_id = None
        self.soup = None
        self.junk_tag_class = ['Apple-converted-space', 'Apple-tab-span']
        self.html_file_name = input_file_name
        self.start_parse()

    def create_page_soup(self):

        with open(f'transforms/ky/ocky/r{self.release_number}/raw/{self.html_file_name}') as open_file:
            html_data = open_file.read()
        self.soup = BeautifulSoup(html_data, features="lxml")
        self.soup.contents[0].replace_with(Doctype("html"))
        self.soup.html.attrs['lang'] = 'en'
        print('created soup')

    def get_class_name(self):
        for key, value in self.class_regex.items():
            tag_class = self.soup.find(
                lambda tag: tag.name == 'p' and re.search(self.class_regex.get(key), tag.get_text().strip()) and
                            tag.attrs["class"][0] not in self.class_regex.values())
            if tag_class:
                self.class_regex[key] = tag_class.get('class')[0]
        # print(self.class_regex)
        print('updated class dict')

    def remove_junk(self):
        for junk_tag in self.soup.find_all():
            if junk_tag.get("class") == ['Apple-converted-space'] or junk_tag.name == "i":
                junk_tag.unwrap()
            elif junk_tag.get("class") == ['Apple-tab-span'] or junk_tag.name == "br":
                junk_tag.decompose()

        [text_junk.decompose() for text_junk in self.soup.find_all("p", class_=self.class_regex["junk"])]
        for b_tag in self.soup.findAll("b"):
            b_tag.name = "span"
            b_tag["class"] = "boldspan"

        print('junk removed')

    # replace title tag to "h1" and wrap it with "nav" tag
    def set_appropriate_tag_name_and_id(self):
        cnav = 0
        snav = 0
        for header_tag in self.soup.body.find_all():
            if header_tag.get("class") == [self.class_regex["title"]]:
                header_tag.name = "h1"
                header_tag.wrap(self.soup.new_tag("nav"))
                self.title_id = re.search(r'^(TITLE)\s(?P<title_id>\w+)', header_tag.text.strip()).group('title_id')


            elif header_tag.get("class") == [self.class_regex["head2"]]:
                if re.search("^(CHAPTER)|^(Chapter)", header_tag.text):
                    chap_nums = re.search(r'^(CHAPTER|Chapter)\s(?P<chapter_id>\w+)', header_tag.text.strip()).group(
                        'chapter_id').zfill(2)
                    header_tag.name = "h2"
                    header_tag['id'] = f"t{self.title_id}c{chap_nums}"
                else:
                    header_tag.name = "h3"
                    header_id = re.sub(r'\s+', '', header_tag.get_text()).lower()
                    chap_nums = re.search(r'^(CHAPTER|Chapter)\s(?P<chapter_id>\w+)',
                                          header_tag.find_previous("h2").text.strip()).group('chapter_id').zfill(2)
                    header_tag["id"] = f"t{self.title_id}c{chap_nums}{header_id}"

            elif header_tag.get("class") == [self.class_regex["sec_head"]]:
                header_tag.name = "h3"

                # sec_pattern = re.compile(r'^(\d+\.\d+\.)')
                if re.match(r'^(\d+\.\d+\.)', header_tag.text.strip()):
                    chap_num = re.search(r'^(\d+)', header_tag.text.strip()).group().zfill(2)
                    sec_num = re.search(r'^(\d+\.\d+)', header_tag.text.strip()).group().zfill(2)
                    header_pattern = re.search(r'^(\d+\.\d+)', header_tag.text.strip()).group()
                    if header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"]):
                        prev_tag = header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"])
                        if header_pattern not in prev_tag.text.split()[0]:
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}"
                        else:
                            count = 0
                            prev_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count + 1}"
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count + 2}"

                    else:
                        header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}"

                elif re.match(r'^(\d+\D\.\d+)', header_tag.text):
                    chap_num = re.search(r'^([^\.]+)', header_tag.text).group().zfill(2)
                    sec_num = re.search(r'^(\d+\D\.\d+)', header_tag.text).group().zfill(2)
                    header_pattern = re.search(r'^(\d+\D\.\d+)', header_tag.text.strip()).group()
                    if header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"]):
                        prev_tag = header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"])
                        if header_pattern in prev_tag.text.split()[0]:
                            count = 0
                            count = count + 1
                            prev_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count}"
                            count = count + 1
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count}"
                        else:
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}"

                elif re.match(r'^(\d+\D\.\d+\-\d+)|^((\d+\.\d+\-\d+))', header_tag.text):
                    chap_num = re.search(r'^([^\.]+)', header_tag.text).group().zfill(2)
                    sec_num = re.search(r'^(\d+\D\.\d+\-\d+)|^((\d+\.\d+\-\d+))', header_tag.text).group().zfill(2)
                    header_pattern = re.search(r'^(\d+\D\.\d+\-\d+)|^((\d+\.\d+\-\d+))',
                                               header_tag.text.strip()).group()
                    if header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"]):
                        prev_tag = header_tag.find_previous(name="h3", class_=self.class_regex["sec_head"])
                        if header_pattern in prev_tag.text.split()[0]:
                            count = 0
                            count = count + 1
                            prev_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count}"
                            count = count + 1
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}-{count}"
                        else:
                            header_tag["id"] = f"t{self.title_id}c{chap_num}s{sec_num}"

            elif header_tag.get("class") == [self.class_regex["ul"]]:
                header_tag.name = "li"

                if re.search("^(CHAPTER)|^(Chapter)", header_tag.text):
                    chap_nums = re.search(r'^(CHAPTER|Chapter)\s(?P<chapter_id>\w+)', header_tag.text.strip()).group(
                        'chapter_id').zfill(2)
                    header_tag['id'] = f"t{self.title_id}c{chap_nums}-cnav{chap_nums}"

                else:
                    prev_chapter_id = header_tag.find_previous("h2").get("id")
                    if re.match(r'^(\d+\D*\.\d+)', header_tag.text.strip()):
                        sec_id = re.search(r'^(\d+\D*\.\d+)', header_tag.text.strip()).group()
                        chapter_id = re.search(r'^([^\.]+)', header_tag.text).group().zfill(2)
                        if header_tag.find_previous_sibling().name != "li":
                            snav = 0
                        snav = snav + 1
                        header_tag["id"] = f"{prev_chapter_id}s{sec_id}-snav{snav}"

                    else:
                        previous_tag = header_tag.find_previous().get("id")
                        if re.match(r'^(\d+\D*\.\d+)', header_tag.find_previous().text.strip()):
                            sec_id = re.search("(snav)(?P<id>\d+)", previous_tag.strip()).group("id").zfill(2)
                            sec_id = int(sec_id) + 1
                            section_id = re.sub(r'\s+', '', header_tag.get_text()).lower()
                            header_tag["id"] = f"{prev_chapter_id}s{section_id}-snav{sec_id}"

                        elif header_tag.find_previous().get("id"):
                            previous_tag_id = header_tag.find_previous().get("id")
                            sec_id = re.search("(snav)(?P<id>\d+)", previous_tag_id.strip()).group("id").zfill(2)
                            sec_id = int(sec_id) + 1
                            section_id = re.sub(r'\s+', '', header_tag.get_text()).lower()
                            header_tag["id"] = f"{prev_chapter_id}s{section_id}-snav{sec_id}"

                        else:
                            chap_nums = re.search(r'^(CHAPTER|Chapter)\s(?P<chapter_id>\w+)',
                                                  header_tag.find_previous("h2").text.strip()).group(
                                'chapter_id').zfill(2)
                            section_id = re.sub(r'\s+', '', header_tag.get_text()).lower()
                            if re.match(r'^CHAPTER', header_tag.find_previous().text):
                                snav = 0
                            snav = snav + 1
                            header_tag["id"] = f"t{self.title_id}c{chap_nums}s{section_id}-snav{snav}"

            elif header_tag.get('class') == [self.class_regex["head4"]]:
                if re.match(r'^(\d+\.)', header_tag.text.strip()):
                    header_tag.name = "h5"
                else:
                    header_tag.name = "h4"

                if header_tag.name == "h4":
                    prev_tag = header_tag.find_previous("h3").get("id")
                    note_to_decision_text = re.sub(r'\s+', '', header_tag.get_text()).lower()
                    header_tag["id"] = f"{prev_tag}{note_to_decision_text}"
                else:
                    if not re.match(r'^(\d+\.\s*—)', header_tag.text.strip()):
                        prev_head_tag = header_tag.find_previous("h4").get("id")
                        sub_sec_text = re.sub(r'[\d\W]', '', header_tag.get_text()).lower()
                        sub_sec_id = f"{prev_head_tag}-{sub_sec_text}"
                        header_tag["id"] = sub_sec_id

                    elif re.match(r'^(\d+\.\s*—\s*[a-zA-Z]+)', header_tag.text.strip()):
                        prev_sub_tag = sub_sec_id
                        child_sec_text = re.sub(r'[\d\W]', '', header_tag.get_text()).lower()
                        child_sec_id = f"{prev_sub_tag}-{child_sec_text}"
                        header_tag["id"] = child_sec_id

                    elif re.match(r'^(\d+\.\s*—\s*—\s*[a-zA-Z]+)', header_tag.text.strip()):
                        prev_child_tag = child_sec_id
                        grandchild_sec_text = re.sub(r'[\d\W]', '', header_tag.get_text()).lower()
                        grandchild_sec_id = f"{prev_child_tag}-{grandchild_sec_text}"
                        header_tag["id"] = grandchild_sec_id

                    elif re.match(r'^(\d+\.\s*—\s*—\s*—\s*[a-zA-Z]+)', header_tag.text.strip()):
                        grandchild_id = grandchild_sec_id
                        super_grandchild_subsec_header_id = re.sub(r'[\d\W]', '', header_tag.get_text()).lower()
                        super_grandchild_subsec_header_tag_id = f"{grandchild_id}-{super_grandchild_subsec_header_id}"
                        header_tag["id"] = super_grandchild_subsec_header_tag_id

        print("tags are replaced")

    # wrap list items with ul tag
    def create_ul_tag(self):
        ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
        for list_item in self.soup.find_all("li"):
            if list_item.find_previous().name == "li":
                ul_tag.append(list_item)
            else:
                ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                list_item.wrap(ul_tag)
        print("ul tag is created")

    # wrap the main content
    def create_main_tag(self):
        section_nav_tag = self.soup.new_tag("main")
        first_chapter_header = self.soup.find(class_=self.class_regex["head2"])
        for main_tag in self.soup.find_all("p"):
            if re.match(r'^(TITLE)', main_tag.text.strip()):
                continue
            elif re.match(r'^CHAPTER|^Chapter', main_tag.text.strip()) and main_tag.get("class") == [
                self.class_regex["ul"]]:
                continue
            elif main_tag == first_chapter_header:
                main_tag.wrap(section_nav_tag)
            else:
                section_nav_tag.append(main_tag)

        print("main tag is created")

    # create a reference
    def create_chap_sec_nav(self):
        count = 0
        for list_item in self.soup.find_all("li"):
            if re.match(r'^(CHAPTER)|^(Chapter)', list_item.text.strip()):
                chap_nav_nums = re.search(r'(\s+[^\s]+)', list_item.text.strip())
                chap_nums = re.search(r'(\s+[^\s]+)', list_item.text).group(0)
                chap_num = re.sub(r'\s+', '', chap_nums).zfill(2)
                if chap_nav_nums:
                    nav_list = []
                    nav_link = self.soup.new_tag('a')
                    nav_link.append(list_item.text)
                    nav_link["href"] = f"#t{self.title_id}c{chap_num}"
                    nav_list.append(nav_link)
                    list_item.contents = nav_list
            else:
                if re.match(r'^(\d+\.\d+)', list_item.text.strip()):
                    chap_num = re.search(r'^([^\.]+)', list_item.text.strip()).group().zfill(2)
                    sec_num = re.search(r'^(\d+\.\d+)', list_item.text.strip()).group(1).zfill(2)
                    sec_pattern = re.search(r'^(\d+\.\d+)', list_item.text.strip()).group()
                    sec_next_tag = list_item.find_next('li')
                    sec_prev_tag = list_item.find_previous("li")
                    sec_prev_tag_text = sec_prev_tag.a
                    if sec_next_tag:
                        if sec_pattern in sec_next_tag.text:
                            list_link = self.soup.new_tag('a')
                            list_link.string = list_item.text
                            count = count + 1
                            list_link["href"] = f"#t{self.title_id}c{chap_num}s{sec_num}-{count}"
                            list_item.contents = [list_link]

                        elif sec_prev_tag_text:
                            if sec_pattern in sec_prev_tag.a.text:
                                list_link = self.soup.new_tag('a')
                                list_link.string = list_item.text
                                count + 2
                                list_link["href"] = f"#t{self.title_id}c{chap_num}s{sec_num}-{count}"
                                list_item.contents = [list_link]

                            else:
                                nav_link = self.soup.new_tag('a')
                                nav_link.string = list_item.text
                                nav_link["href"] = f"#t{self.title_id}c{chap_num}s{sec_num}"
                                list_item.contents = [nav_link]
                    else:
                        nav_link = self.soup.new_tag('a')
                        nav_link.string = list_item.text
                        nav_link["href"] = f"#t{self.title_id}c{chap_num}s{sec_num}"
                        list_item.contents = [nav_link]

                elif re.match(r'^(\d+\D\.\d+)', list_item.text.strip()):
                    chap_num = re.search(r'^([^\.]+)', list_item.text.strip()).group().zfill(2)
                    sec_num = re.search(r'^(\d+\D\.\d+)', list_item.text.strip()).group().zfill(2)
                    nav_link = self.soup.new_tag('a')
                    nav_link.string = list_item.text
                    nav_link["href"] = f"#t{self.title_id}c{chap_num}s{sec_num}"
                    list_item.contents = [nav_link]

                else:
                    chapter_header = list_item.find_previous("h2")
                    chap_nums = re.search(r'(\s+[^\s]+)', chapter_header.text.strip()).group(0)
                    chap_num = re.sub(r'\s+', '', chap_nums).zfill(2)
                    sec_id = re.sub(r'[\s+\.]', '', list_item.get_text()).lower()
                    new_link = self.soup.new_tag('a')
                    new_link.string = list_item.text
                    new_link["href"] = f"#t{self.title_id}c{chap_num}{sec_id}"
                    list_item.contents = [new_link]

    # create ol tag for note to decision nav
    def create_ul_tag_to_notes_to_decision1(self):
        new_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
        new_nav_tag = self.soup.new_tag("nav")
        child_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
        grandchild_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
        super_grandchild_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})

        for note_tag in self.soup.find_all(class_=self.class_regex["ol"]):
            if re.match(r'^(\d+\.)', note_tag.text.strip()) and note_tag.find_previous(
                    "h4") is not None and note_tag.find_previous("h4").text.strip() == 'NOTES TO DECISIONS':
                note_tag.name = "li"
                
            # parent
            if re.match(r'^(\d+\.\s*[a-zA-Z]+)', note_tag.text.strip()) and note_tag.name == "li":
                if re.match(r'^(1\.)', note_tag.text.strip()) and note_tag.name == "li":
                    new_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                    note_tag.wrap(new_ul_tag)
                    new_ul_tag.wrap(self.soup.new_tag("nav"))
                else:
                    new_ul_tag.append(note_tag)

            # child
            if re.match(r'^(\d+\.\s*—\s*[a-zA-Z]+)', note_tag.text.strip()) and note_tag.name == "li":
                if re.match(r'^(\d+\.\s*[a-zA-Z]+)', note_tag.find_previous().text.strip()) and note_tag.name == "li":
                    child_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                    note_tag.wrap(child_ul_tag)
                    new_ul_tag.append(child_ul_tag)
                    note_tag.find_previous("li").append(child_ul_tag)
                else:
                    child_ul_tag.append(note_tag)

            # # grand child
            if re.match(r'^(\d+\.\s*—\s*—\s*[a-zA-Z]+)', note_tag.text.strip()) and note_tag.name == "li":
                if re.match(r'^(\d+\.\s*—\s*—\s*[a-zA-Z]+)', note_tag.find_previous().text.strip()) and note_tag.name == "li":
                    grandchild_ul_tag.append(note_tag)
                else:
                    grandchild_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                    note_tag.wrap(grandchild_ul_tag)
                    note_tag.find_previous("li").append(grandchild_ul_tag)

            # # super grand child
            if re.match(r'^(\d+\.\s*—\s*—\s*—\s*[a-zA-Z]+)', note_tag.text.strip()) and note_tag.name == "li":
                if re.match(r'^(\d+\.\s*—\s*—\s*—\s*[a-zA-Z]+)', note_tag.find_previous().text.strip()) and note_tag.name == "li":
                    super_grandchild_ul_tag.append(note_tag)
                else:
                    super_grandchild_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                    note_tag.wrap(super_grandchild_ul_tag)
                    grandchild_ul_tag.append(super_grandchild_ul_tag)

            if re.match(r'^(\d+\.)', note_tag.text.strip()) and note_tag.find_previous(
                    "p") is not None and note_tag.find_previous("p").text.strip() == 'Analysis':
                note_tag.name = "li"

                if note_tag.find_previous().text.strip() == 'Analysis':
                    new_ul_tag = self.soup.new_tag("ul", **{"class": "leaders"})
                    note_tag.wrap(new_ul_tag)
                    new_ul_tag.wrap(self.soup.new_tag("nav"))
                else:
                    new_ul_tag.append(note_tag)

    # add links to notes to decision nav
    def create_link_to_notetodecision_nav(self):
        for p_tag in self.soup.find_all(class_=self.class_regex["ol"]):
            if re.match(r'^(\d+\.)', p_tag.text.strip()):
                if p_tag.find_previous("h4") is not None and p_tag.find_previous(
                        "h4").text.strip() == 'NOTES TO DECISIONS':

                    if not re.match(r'^(\d+\.\s*—)', p_tag.text.strip()):
                        prev_head_tag = p_tag.find_previous("h4").get("id")
                        sub_sec_id = re.sub(r'[\d\W]', '', p_tag.get_text()).lower()
                        nav_link = self.soup.new_tag('a')
                        nav_link.string = p_tag.text
                        nav_link["href"] = f"#{prev_head_tag}-{sub_sec_id}"
                        p_tag.string = ''
                        p_tag.insert(0, nav_link)


                    elif re.match(r'^(\d+\.\s*—\s*[a-zA-Z]+)', p_tag.text.strip()):
                        prev_id = nav_link["href"]
                        sub_sec_id = re.sub(r'[\d\W]', '', p_tag.get_text()).lower()
                        child_nav_link = self.soup.new_tag('a')
                        child_nav_link.string = p_tag.text
                        child_nav_link["href"] = f"{prev_id}-{sub_sec_id}"
                        p_tag.string = ''
                        p_tag.insert(0, child_nav_link)

                    elif re.match(r'^(\d+\.\s*—\s*—\s*[a-zA-Z]+)', p_tag.text.strip()):
                        child_id = child_nav_link["href"]
                        sub_sec_id = re.sub(r'[\d\W]', '', p_tag.get_text()).lower()
                        grandchild_nav_link = self.soup.new_tag('a')
                        grandchild_nav_link.string = p_tag.text
                        grandchild_nav_link["href"] = f"{child_id}-{sub_sec_id}"
                        p_tag.string = ''
                        p_tag.insert(0, grandchild_nav_link)

                    elif re.match(r'^(\d+\.\s*—\s*—\s*—\s*[a-zA-Z]+)', p_tag.text.strip()):
                        grand_child_id = grandchild_nav_link["href"]
                        sub_sec_id = re.sub(r'[\d\W]', '', p_tag.get_text()).lower()
                        grandchild_child_nav_link = self.soup.new_tag('a')
                        grandchild_child_nav_link.string = p_tag.text
                        grandchild_child_nav_link["href"] = f"{grand_child_id}-{sub_sec_id}"
                        p_tag.string = ''
                        p_tag.insert(0, grandchild_child_nav_link)

                elif re.match(r'^(\d+\.\s*—\s*[a-zA-Z]+)', p_tag.text.strip()):
                    sub_sec = re.sub(r'[\d\W]', '', p_tag.get_text()).lower()
                    sub_sec_id = p_tag.find_previous("h5").get("id")
                    child_nav_link = self.soup.new_tag('a')
                    child_nav_link.string = p_tag.text
                    child_nav_link["href"] = f"#{sub_sec_id}-{sub_sec}"
                    p_tag.string = ''
                    p_tag.insert(0, child_nav_link)

    # wrapping with ol tag
    def wrap_with_ordered_tag1(self):
        pattern = re.compile(r'^(\d+)|^([(]\d+[)]|^[(]\D[)])|^(\D\.)')
        Num_bracket_pattern = re.compile(r'^\(\d+\)')
        alpha_pattern = re.compile(r'^\(\D+\)')
        alp_pattern = re.compile(r'\(\D+\)')
        num_pattern = re.compile(r'^\d+\.')
        num_pattern1 = re.compile(r'^1\.')
        numAlpha_pattern = re.compile(r'^\(\d+\)\s\(\D+\)')
        alphanum_pattern = re.compile(r'^\(\D+\)\s(\d)+')

        ol_tag2 = self.soup.new_tag("ol", type="a", **{"class": "alpha"})
        ol_tag = self.soup.new_tag("ol")
        ol_tag3 = self.soup.new_tag("ol")
        ol_tag1 = self.soup.new_tag("ol")
        ol_tag4 = self.soup.new_tag("ol", type="a",**{"class": "alpha"})
        ol_tag5 = self.soup.new_tag("ol")

        olcount = 0
        main_olcount = 0
        inner_olcount = 1


        for tag in self.soup.findAll("p", class_=self.class_regex["ol"]):
            if re.match(pattern, tag.text.strip()):
                tag.name = "li"

            # (1)
            if re.match(Num_bracket_pattern, tag.text.strip()):
                pattern1 = re.findall(r'^\(\d+\)', tag.text.strip())
                index = re.findall(r'\d+', str(pattern1))
                tag_strings = [str(integer) for integer in index]
                tag_string = "".join(tag_strings)
                tag_int = int(tag_string)

                if tag_int > 1:
                    ol_tag.append(tag)
                elif tag_int == 1:
                    ol_tag = self.soup.new_tag("ol")
                    tag.wrap(ol_tag)
                    main_olcount = 1

                if re.match(numAlpha_pattern, tag.find_previous().text.strip()):
                    main_olcount = 1


                prev_header_id = tag.find_previous("h3").get("id")
                tag["id"] = f"{prev_header_id}ol1{main_olcount}"
                main_olcount += 1



             # (1)(a)
            if re.match(numAlpha_pattern, tag.text.strip()):
                prev_tag_id = tag.get("id")
                ol_tag2 = self.soup.new_tag("ol", type="a", **{"class": "alpha"})
                li_tag = self.soup.new_tag("li")
                li_tag.append(tag.text.strip())
                inner_olcount = 97
                li_tag["id"] = f"{prev_tag_id}{chr(inner_olcount)}"
                inner_olcount += 1
                ol_tag2.append(li_tag)
                tag.contents = []
                tag.append(ol_tag2)


            # (a)
            if re.match(r'^\(\D\)', tag.text.strip()):
                if re.match(r'^\(a\)', tag.text.strip()):
                    ol_tag2 = self.soup.new_tag("ol", type="a",  **{"class": "alpha"})
                    prev_header_id = tag.find_previous("li").get("id")
                    inner_olcount = 97
                    tag.wrap(ol_tag2)
                    tag.find_previous("li").append(ol_tag2)
                else:
                    ol_tag2.append(tag)

                prev_header_id = tag.find_previous("h3").get("id")
                tag["id"] = f"{prev_header_id}{chr(inner_olcount)}"
                inner_olcount += 1



             # (4)(a)1.
            if re.match(r'\(\d+\)\s*\(\D\)\s*\d\.', tag.text.strip()):
                ol_tag4 = self.soup.new_tag("ol")
                inner_li_tag = self.soup.new_tag("li")
                inner_li_tag.append(tag.text.strip())
                ol_tag4.append(inner_li_tag)
                tag.insert(1, ol_tag4)
                # ol_tag4.find_previous().insert(0, ol_tag4)
                ol_tag4.find_previous().string.replace_with(ol_tag4)
                # print(ol_tag4.find_previous())



            # a
            if re.match(r'\D\.', tag.text.strip()):
                if re.match(r'a\.', tag.text.strip()):
                    ol_tag3 = self.soup.new_tag("ol", type="a", **{"class": "alpha"})
                    tag.wrap(ol_tag3)
                    ol_tag.append(ol_tag3)
                    tag.find_previous("li").append(ol_tag3)
                    inr_olcount = 97
                else:
                    tag.find_previous("li").append(tag)

                prev_header_id = tag.find_previous("li").get("id")
                tag["id"] = f"{prev_header_id}{chr(inr_olcount)}"
                inr_olcount += 1




             # (a) 1.
            if re.match(alphanum_pattern, tag.text.strip()):
                ol_tag5 = self.soup.new_tag("ol")
                li_tag = self.soup.new_tag("li")
                li_tag.append(tag.text.strip())
                ol_tag5.append(li_tag)
                tag.contents = []
                tag.append(ol_tag5)
            elif re.match(num_pattern, tag.text.strip()):
                tag.find_previous("li").append(tag)

            # 1. and previous (1)(a)
            if re.match(num_pattern, tag.text.strip()):
                if re.match(r'^1\.', tag.text.strip()):
                    ol_tag6 = self.soup.new_tag("ol")
                    tag.wrap(ol_tag6)
                    tag.find_previous("li").append(ol_tag6)

                    main_olcount = 1
                    prev_header_id = tag.find_previous("li").get("id")

                elif tag.find_previous("li"):
                    tag.find_previous("li").append(tag)

                # prev_header_id = tag.find_previous("h3").get("id")
                tag["id"] = f"{prev_header_id}{main_olcount}"
                main_olcount += 1

        print("ol tag is wrapped")




    def write_soup_to_file(self):
        soup_str = str(self.soup.prettify(formatter=None))
        with open(f"../cic-code-ky/transforms/ky/ocky/r{self.release_number}/{self.html_file_name}", "w") as file:
            file.write(soup_str)

    # add css file
    def css_file(self):
        head = self.soup.find("head")
        style = self.soup.head.find("style")
        style.decompose()
        css_link = self.soup.new_tag("link")
        css_link.attrs[
            "href"] = "https://unicourt.github.io/cic-code-ga/transforms/ga/stylesheet/ga_code_stylesheet.css"
        css_link.attrs["rel"] = "stylesheet"
        css_link.attrs["type"] = "text/css"
        head.append(css_link)

    def start_parse(self):
        self.release_label = f'Release-{self.release_number}'
        print(self.html_file_name)
        start_time = datetime.now()
        print(start_time)
        self.create_page_soup()
        self.css_file()
        self.get_class_name()
        self.remove_junk()
        self.create_main_tag()
        self.set_appropriate_tag_name_and_id()
        self.create_ul_tag()
        self.create_chap_sec_nav()
        self.create_link_to_notetodecision_nav()
        self.create_ul_tag_to_notes_to_decision1()
        self.wrap_with_ordered_tag1()




        self.write_soup_to_file()
        print(datetime.now() - start_time)
