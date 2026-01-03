from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer, BeautifulSoupTransformer


FILE_TO_PARSE = "data/links.txt"
DIR_TO_STORE = "docs"


def getLinks2Parse() -> list:
    try:
        with open(FILE_TO_PARSE, "r") as f:
            return [link.strip() for link in f.readlines()]
    except:
        return []


def asyncLoader(links):
    loader = AsyncHtmlLoader(links)
    docs = loader.load()

    # Transform
    bs_transformer = BeautifulSoupTransformer()

    for doc in docs:
        doc.page_content = bs_transformer.remove_unwanted_classnames(doc.page_content,
                                                                     ['new-footer', 'main-header',
                                                                      'main-top-block', 'callback__form',
                                                                      'new-footer-bottom', 'blog-article-share', 'blog-article-slider',
                                                                      'blog-article-menu', 'blog__subscribe',
                                                                      'main-top-block__info', 'breadcrumbs'])

    html2text = Html2TextTransformer(ignore_links=True, ignore_images=True)
    docs_transformed = html2text.transform_documents(docs)

    for idx, doc in enumerate(docs_transformed):
        with open(f"{DIR_TO_STORE}/document_{idx}.txt", "w+", encoding="utf-8") as f:
            f.write(doc.page_content)
            print(f"File {DIR_TO_STORE}/document_{idx}.txt saved")


if __name__ == "__main__":
    ls = getLinks2Parse()
    asyncLoader(ls)