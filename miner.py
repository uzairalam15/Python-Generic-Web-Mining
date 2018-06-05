import tokenizer

def get_main_page_from_file(file):
    page_html = ""
    import codecs
    with codecs.open(file, "r", "utf-8") as f:
        for line in f:
            page_html = page_html + line
    return page_html

def get_main_page(url):
    return requests.get(url).text

def get_language(file):
    text = ""
    with open(file) as f:
        for line in f:
            text = text +'\n'+ line
    return text

def tokenizer_execute(language,page_html,link):
    obj = tokenizer.tokenizer(language)
    obj.generate_tokens()
    obj2 = tokenizer.semantic_tokenizer(obj.tokens)
    obj2.generate_tokens()
    obj3 = tokenizer.extractor(obj.tokens, obj2.semantic_tokens)
    if not page_html:
        returned_result = obj3.start_extract(link)
        return returned_result
    else:
        returned_result = obj3.start_extract_without_fetch(page_html)
        return returned_result

language = get_language("language")
print(tokenizer_execute(language, None, "https://tribune.com.pk/"))