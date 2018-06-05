from bs4 import BeautifulSoup
import requests
import click
from nltk.tokenize import TweetTokenizer


class tokenizer:

    def __init__(self,text):
        self.tokens = []
        self.parser_text = text
        self.error = ""
        self.count = 0

    def convert_text_to_lines(self):
        self.lines = self.parser_text.splitlines()
        self.line_count = len(self.lines)
        return True

    def set_error(self,text):
        self.error = self.error + "\n" + text

    def save_token(self,token):
        self.tokens.append(token)

    # def save_token(self,type):
    #     self.tokens[type] = self.curr_token
    #     self.curr_token = ""

    def generate_tokens(self):
        if self.start_token_parsing():
            return True
        else:
            self.set_error("Could not complete token generation due to some error")
            return False

    def start_token_parsing(self):
        punkt_word_tokenizer = TweetTokenizer()
        tokens = punkt_word_tokenizer.tokenize(self.parser_text)
        self.refined_tokens(tokens)
        # # print(self.tokens)

    def operators_check(self,token):
        if token == ":" or token == "[" or token == "]" or token == "{" or token == "}" or token == "(" or token == ")" or token == "*" or token == "." or token == "," or token == ">" or token == "<" or token == "=":
            return True
        return False

    def refined_tokens(self,tokens):
        for index in range(len(tokens)):
            if tokens[index] != "\"":
                self.refined_it(tokens[index])



    def refined_it(self,token):
        curr_character = ""
        curr_token = ""
        for index in range(len(token)):
            curr_character = token[index]

            if self.operators_check(curr_character):
                if curr_token != "":
                    self.save_token(curr_token)
                    curr_token = ""
                else:
                    self.save_token(curr_character)
                    curr_character = ""
                    continue
            if index == len(token)-1:
                curr_token += curr_character
                self.save_token(curr_token)
                curr_token = ""
                continue

            curr_token += curr_character



class semantic_tokenizer:

    def __init__(self,tokens):
        self.tokens = tokens
        self.semantic_tokens = []
        self.error = ""
        self.tags = []
        self.curr_token = ""
        self.bracket_type = ""
        self.operator_type = ""
        self.is_selector = False
        self.is_value = False
        self.is_attr = False
        self.is_return_attr = False
        self.is_return_property = False
        self.is_keyword = False
        self.is_rule = False

    def set_error(self, text):
        self.error = self.error + "\n" + text

    def load_tags(self, filename):
        with open(filename) as f:
            for line in f:
                self.tags.append(line.replace("\n",""))
        return True

    def reset(self):
        self.is_selector = False
        self.is_value = False
        self.is_attr = False
        self.is_return_attr = False
        self.is_return_property = False
        self.is_keyword = False

    def save_token(self,type):
        self.semantic_tokens.append(type)

    def generate_tokens(self):
        if self.load_tags("tags"):
            if self.start_asignment():
                # # print(self.semantic_tokens)
                return True
            else:
                # print(self.error)
                return False
        else:
            self.set_error("Could not complete token generation due to file missing of Html tags")
            return False

    def start_asignment(self):
        for index in range(len(self.tokens)):
            if self.error == "":
                self.curr_token = self.tokens[index]
                if self.tag():
                    self.save_token("tag")
                    continue
                if self.colon():
                    self.save_token("colon")
                    continue
                if self.brackets():
                    self.save_token(self.bracket_type)
                    continue
                if self.value_attr():
                    self.save_token("value_attr")
                    continue
                if self.attr():
                    self.save_token("attr")
                    continue
                if self.operator():
                    self.save_token(self.operator_type)
                    continue
                if self.return_attr():
                    self.save_token("return_attr")
                    continue
                if self.selector():
                    self.save_token("selector")
                    continue
                if self.comma():
                    if self.is_rule:
                        self.save_token("parent_comma_op")
                        self.is_rule = False
                        continue
                    self.save_token("comma")
                    continue
                if self.semi_colons():
                    continue
                else:
                    self.set_error("Could not complete token generation due to unable token (" + self.curr_token + ")")
                    return False
            else:
                return False
        return True

    def semi_colons(self):
        if self.curr_token == "\"":
            return True
        return False

    def tag(self):
        for word in self.tags:
                if self.curr_token == word and (self.is_attr == True or self.is_return_attr == True or self.is_return_property == True or self.is_selector == True):
                    self.set_error("Cannot use html5 tag keyword as attr or return attr  ("+ self.curr_token +") in line "+ self.count)
                    return False
                elif self.curr_token == word:
                    return True
        return False

    def return_attr(self):
        if self.is_return_attr == True and self.curr_token.isalpha():
            return True
        return False

    def attr(self):
        if self.is_attr == True and self.is_value == False and self.curr_token.isalpha():
            return True
        return False

    def value_attr(self):
        if self.is_attr == False and self.is_value == True:
            return True
        return False


    def operator(self):
        if self.curr_token == "=":
            self.operator_type = "asignment_op"
            if self.is_attr == True:
                self.is_attr = False
                self.is_value = True
            return True

        if self.curr_token == ">":
            self.operator_type = "parent_op"
            self.reset()
            return True

        if self.curr_token == "~":
            self.operator_type = "parent_op"
            self.reset()
            return True

        if self.curr_token == "." and self.is_attr == False and self.is_value == False and self.is_return_attr == False :
            self.operator_type = "dot_op"
            self.is_selector = True
            return True

        return False

    def selector(self):
        if self.curr_token == "*":
            return True
        if self.is_selector == True and self.curr_token.isalpha():
            self.is_selector = False
            return True


    def colon(self):
        if self.curr_token == ":":
            return True
        return False

    def comma(self):
        if self.curr_token == ",":
            if self.is_value == True:
                self.is_attr = True
                self.is_value = False
            elif self.is_attr == False and self.is_return_attr == False and self.is_selector == False and self.is_return_property == False:
                self.is_rule = True
            return True
        return False

    def brackets(self):
        if self.curr_token == "[" or self.curr_token == "]":
            if self.curr_token == "[":
                self.is_attr = True
            if self.curr_token == "]":
                self.is_attr = False
                self.is_value = False
            self.bracket_type = "square_brac"
            return True
        if self.curr_token == "{" or self.curr_token == "}":
            if self.curr_token == "{":
                self.is_return_property = True
            if self.curr_token == "}":
                self.is_return_property = False
            self.bracket_type = "curly_brac"
            return True
        if self.curr_token == "(" or self.curr_token == ")":
            if self.curr_token == "(":
                self.is_return_attr = True
            if self.curr_token == ")":
                self.is_return_attr = False
            self.bracket_type = "circle_brac"
            return True

class extractor:

    def __init__(self,tokens,semantic_tokens):
        self.tag = ""
        self.tokens = tokens
        self.semantic_tokens = semantic_tokens
        self.rules = []
        self.count_rules = 0
        self.result_object = {}
        self.seperators = []
        self.dom = None

    def get_main_page(self,url):
        return requests.get(url).text

    def break_rules(self):
        temp = []
        for index in range(len(self.tokens)):
            if self.semantic_tokens[index] == "parent_op" or self.semantic_tokens[index] == "parent_comma_op":
                self.rules.append(temp)
                self.seperators.append(self.tokens[index])
                temp = []
            else:
                temp.append(self.tokens[index])
        self.rules.append(temp)
        self.count_rules = len(self.rules)

    def execute_rules(self):
        result = ""
        for index in range(len(self.rules)):
            if index == 0:
                result = self.single_rule(self.rules[index],None,None)
            else:
                result = self.single_rule(self.rules[index],result,self.seperators[index-1])

        # print(result)
        objs = self.get_results(result)
        # print(objs)
        self.get_field(objs,self.rules[self.count_rules-1])

    def get_field(self,objs,rule):
        temp_array = []
        attr = self.get_return_attr(rule)
        for index in range(len(attr)):
            self.result_object[attr[index]] = self.get_field_values(objs,attr[index])


    def get_field_values(self,obj,attr):
        result = []
        for index in range(len(obj)):
            if attr == "text":
                result.append(obj[index].text)
            else:
                result.append(obj[index][attr])
        return result

    def get_return_attr(self,rule):
        attr = []
        flag = False
        for index in range(len(rule)):
            if rule[index] == "(":
                flag = True
                continue
            if rule[index] == ")":
                flag = False
            if rule[index] == ",":
                continue
            if flag:
                attr.append(rule[index])
        return attr

    def single_rule(self,rule,parent,seperator):
        lang = ""
        if parent == None:
            lang += self.get_filters(rule, self.get_tag(rule))
        else:
            lang += parent + self.convert_seperator(seperator)
            lang += self.get_filters(rule,self.get_tag(rule))
        return lang

    def get_tag(self,rule):
        return rule[0]

    def convert_seperator(self,seperator):
        if seperator == ",":
            return " "
        else:
            return " "+seperator+" "

    def get_filters(self,rule,tag):
        lang = ""
        temp_array = []
        flag = False
        is_value = False
        is_filter = True
        for index in range(len(rule)):
            if rule[index] == "[":
                flag = True
                continue
            if rule[index] == "]":
                flag = False
            if flag:
                temp_array.append(rule[index])

        lang = tag

        for index in range(len(temp_array)):
            if temp_array[index] == ",":
                is_filter = True
                is_value = False
                lang += temp_array[index] + tag
                continue
            if temp_array[index] == "=":
                is_filter = False
                is_value = True
                continue
            if is_filter:
                if str.lower(temp_array[index]) == "class":
                    lang += "."
                if str.lower(temp_array[index]) == "id":
                    lang += "#"
            if is_value:
                lang += temp_array[index]
        return lang

    def get_results(self,lang):
        return self.dom.select(lang)

    def start_extract(self,link):
        page_html = self.get_main_page(link)
        self.dom = BeautifulSoup(page_html,"lxml")
        self.break_rules()
        self.execute_rules()
        # print(self.result_object)
        return self.result_object

    def start_extract_without_fetch(self,page_html):
        self.dom = BeautifulSoup(page_html, "lxml")
        self.break_rules()
        self.execute_rules()
        # print(self.result_object)
        return self.result_object

    def extract_from_file(self,file):
        page_html = ""
        import codecs
        with codecs.open(file,"r","utf-8") as f:
            for line in f:
                page_html = page_html + line
        self.dom = BeautifulSoup(page_html, "lxml")
        self.break_rules()
        self.execute_rules()
        # print(self.result_object)
        return self.result_object

def get_main_page_from_file(file):
    page_html = ""
    import codecs
    with codecs.open(file, "r", "utf-8") as f:
        for line in f:
            page_html = page_html + line
    return page_html

def get_main_page(url):
    return requests.get(url).text