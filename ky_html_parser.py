from bs4 import BeautifulSoup
import re

class KyHtmlOperations:
    # # create a soup
    # def create_soup(self):
    #     with open("/home/mis/gov.ky.krs.title.01.html") as fp:
    #         soup = BeautifulSoup(fp, "lxml")
    #         return soup

    # soup initialization
    def __init__(self,soup):
        self.soup = soup

    #def start_function(self):



    # assign id to chapter header
    def chapter_header_id(self, soup):
        all_chapter_header = soup.findAll("p", class_="p3")
        for chap_head in all_chapter_header:
            chap_nums = re.findall(r'\d', chap_head.text)
            chap_head['id'] = f"t01c0{chap_nums}"
            chap_head.name = "h2"

    # assign id to Section header
    def section_header_id(self, soup):
        all_section_header = soup.findAll("p", class_="p4")
        for sec_head in all_section_header:
            chap_num = re.findall(r'^([^\.]+)', sec_head.text)
            chap_id = "".join(chap_num)
            sec_num = re.findall(r'^([^\s]+)', sec_head.text)
            sec_id = "".join(sec_num)
            sec_head['id'] = f"t01c0{chap_id}s{sec_id}"
            sec_head.name = "h3"


    # replace with appropriate tag
    def set_appropriate_tag(self, soup):
        title_header = soup.find(name="p", text=re.compile("^(TITLE)"))
        title_header.name = "h1"
        title_header.wrap(soup.new_tag("nav"))

    # set as unordered list and wrap it with anchor tag
    def set_ul_tag(self, soup):
        ul_tag = soup.new_tag("ul", **{'class': 'leaders'})
        chapter_nav = soup.findAll("p")
        chapter_header_break = soup.find("p", class_="p3")
        for nav in chapter_nav:
            if nav != chapter_header_break:
                if nav["class"] != ['p1']:
                    nav.wrap(ul_tag)
                    nav.name = "li"
            else:
                break

    # Assign id to chapter nav items
    def chapter_nav_id(self, soup):
        for chapter_nav_item in soup.findAll("li"):
            #del (chapter_nav_item["class"])
            chapter_nav_item["class"] = []
            chap_dic = chapter_nav_item.attrs
            #chap_dic.clear()
            chap_dic.pop('class')
            chap_nav_nums = re.findall(r'\d', chapter_nav_item.text)
            chap_nav_id = "".join(chap_nav_nums)
            chapter_nav_item['id'] = f"t01c0{chap_nav_id}-cnav0{chap_nav_id}"

        soup.find("nav").append(soup.find("ul", class_="leaders"))


    # wrap chapter nav items with anchor tag
    def chapter_nav(self, soup):

        all_nav_headers = soup.find_all("li")
        for nav_head in all_nav_headers:
            chap_nav_nums = re.findall(r'\d', nav_head.text)
            chap_nav_id = "".join(chap_nav_nums)

            new_list = []
            new_link = soup.new_tag('a')
            new_link.append(nav_head.text)
            new_link["href"] = f"#t01c0{chap_nav_id}"
            new_list.append(new_link)
            nav_head.contents = new_list


    # wrap the main content
    def main_tag(self, soup):
        section_nav_tag = soup.new_tag("main")
        tags = [tags.wrap(section_nav_tag) for tags in soup.find_all(['p', 'h2', 'h3'])]

    # wrap section   with nav tag
    def section_nav(self, soup):
        for tag in soup.findAll("p", class_="p2"):
            tag.name = "li"

        chap_div = [tag.wrap(soup.new_tag("div")) for tag in soup.findAll("h2")]

        # newlist = []
        #
        # new_link = soup.new_tag("ul")
        # main_content = soup.main.findAll(["li", "div"])
        # for main in main_content:
        #     # print(main.find_previous().name)
        #     print(main.find_previous().name)
        #     print(main.name)
        #
        #     try:
        #         if (main.name == "li" and main.find_previous().name == "b") or (main.name == "li" and main.find_previous().name == "li" ):
        #             ul_tag = soup.new_tag("ul")
        #             main.wrap(ul_tag)
        #         else:
        #             ul_tag.append(main)
        #     except Exception:
        #         pass










    # wrap div
    def div_tag(self, soup):
        div_tag = soup.new_tag("div")
        mains = soup.find_all("main")
        chapter_title = soup.main.findAll()
        for chpter in chapter_title:
            if chpter.name == 'h2' and chpter.find_previous_sibling("p") == None :
                chpter.wrap(div_tag)


    # add chapter name
    def chap_name(self, soup):





        all_chapter_header = soup.findAll("p", class_="p3")
        for chap_head in all_chapter_header:
            chap_nums = re.findall(r'\d', chap_head.text)
            if chap_nums != []:
                chap_head['id'] = f"t01c0{chap_nums[0]}"

            #chap_id = int(chap_nums)
            #print(chap_nums)
            # print(chap_nums)
            #chap_id = "".join(chap_nums)
            #chap_head['id'] = f"t01c0{chap_id}"
            #chap_head.name = "h2"




# ordered list---------(a)
    def wrap_with_ordered_list(self):
        pattern2 = re.compile(r'^[(]\D[)]')
        pattern1 = re.compile(r'^(\d+)|^([(]\d+[)])')
        pattern = re.compile(r'^(\d+)|^([(]\d+[)])|^[(].[)]')

        # convert p into li
        for tag in self.soup.findAll("p", class_="p6"):
            if re.match(pattern, tag.text):
                tag.name = "li"

            if re.match(pattern2, tag.text):
                if not re.match(pattern, tag.find_previous().text):
                    ol_tag.append(tag)
                else:
                    ol_tag = self.soup.new_tag("ol")
                    tag.wrap(ol_tag)

            # ol_tag = self.soup.new_tag("ol")
            # if re.match(pattern, tag.text):
            #     if tag.find_previous().name == "li":
            #         if re.match(pattern1, tag.next):
            #             if re.match(pattern1, tag.find_previous().text) or re.match(pattern2, tag.find_previous().text):
            #                 ol_tag.append(tag)
            #         else:
            #             if re.match(pattern2,tag.find_previous().text):
            #                 ol_tag.append(tag)
            #             else:
            #                 tag.wrap(ol_tag)
            #                 ol_tag.append(tag)
            #     else:
            #         ol_tag = self.soup.new_tag("ol")
            #         tag.wrap(ol_tag)

    # ordered list------------(1)(a)
    def ordered_list(self):
        for tag in self.soup.findAll("p", class_="p8"):
            tag.name = "h4"

        pattern2 = re.compile(r'^[(]\D[)]')
        pattern1 = re.compile(r'^(\d+)|^([(]\d+[)])')
        pattern = re.compile(r'^(\d+)|^([(]\d+[)])|^[(].[)]')

        # convert p into li
        for tag in self.soup.findAll("p", class_="p6"):
            if re.match(pattern, tag.text):
                tag.name = "li"

        # list
        ol_tag1 = self.soup.new_tag("ol")
        ol_tag2 = self.soup.new_tag("ol")
        for tag in self.soup.findAll("li", class_="p6"):
            if re.match(pattern1, tag.text):
                if re.match(pattern1, tag.find_previous().text) or re.match(pattern2, tag.find_previous().text):
                    ol_tag1.append(tag)
                else:
                    ol_tag1 = self.soup.new_tag("ol")
                    tag.wrap(ol_tag1)
            else:
                if re.match(pattern2, tag.find_previous().text):
                    ol_tag2.append(tag)
                else:
                    ol_tag2 = self.soup.new_tag("ol")
                    tag.wrap(ol_tag2)
                    # ol_tag1.append(tag)


with open("/home/mis/gov.ky.krs.title.01.html") as fp:
    soup = BeautifulSoup(fp, "lxml")

KyHtmlOperations_obj = KyHtmlOperations(soup)  # create a class object

KyHtmlOperations_obj.chap_name(soup)


#KyHtmlOperations_obj. set_ul_tag(soup)

#KyHtmlOperations_obj.chapter_header_id(soup)
#KyHtmlOperations_obj.section_header_id(soup)
#KyHtmlOperations_obj.set_appropriate_tag(soup)
#KyHtmlOperations_obj.chapter_nav_id(soup)
#KyHtmlOperations_obj.chapter_nav(soup)
#KyHtmlOperations_obj.main_tag(soup)
#KyHtmlOperations_obj.section_nav(soup)
#KyHtmlOperations_obj.clear_tag(soup)
#KyHtmlOperations_obj.div_tag(soup)
#KyHtmlOperations_obj.nav_wrap(soup)
#KyHtmlOperations_obj.remove_class_attribute(soup)

with open("ky.html", "w") as file:
    file.write(str(soup))
