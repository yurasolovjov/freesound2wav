import sys, os
import argparse
import termcolor

# Подключение модуля freesound
mainfile = os.path.abspath(sys.modules['__main__'].__file__)

t,h = os.path.split(mainfile)

path2fs = os.path.normpath(t + '//freesound-python')
sys.path.insert(0,path2fs)

import freesound

# Ключ доступа к Freesound API
GEN_KEY_FREESOUND = str("PYqNLRWMA9URy55hSbzK5lGxJsgVJaBsvRx6giFG")

# Ограничение на максимальное количество страниц
LIMIT_PAGE = int(10)

def main():

    parser = argparse.ArgumentParser(description="Options");
    parser.add_argument("-s", "--search", help="Keyword for search", action="append", default=None, nargs="*")
    parser.add_argument("-o", "--out", help="Output catalog", default="../freesound")
    parser.add_argument("-l", "--lim_page", help="Limit of page", default=LIMIT_PAGE)

    args = parser.parse_args()

    search_tokens = list()
    keywords = args.search
    lim_page_count =  args.lim_page

    output = os.path.normpath(args.out)

    for keyword in keywords:
        fusion_keyword = str()
        for k in keyword:
            fusion_keyword += k + ' '

        if fusion_keyword[-1] == ' ':
            fusion_keyword = fusion_keyword[:-1]

        search_tokens.append(fusion_keyword)

    if not os.path.exists(output):
        os.makedirs(output)

    if search_tokens == None:
        raise Exception("Not found keywords");

    try:
        client = freesound.FreesoundClient()
        client.set_token(GEN_KEY_FREESOUND,"token")
        print(termcolor.colored("Authorisation successful ", "green"))
    except:
        print(termcolor.colored("Authorisation failed ", "red"))

    for token in search_tokens:
        try:

            results = client.text_search(query=token,fields="id,name,previews")

            output_catalog = os.path.normpath(output + "\\" + str(token))

            if not os.path.exists(output_catalog):
                os.makedirs(output_catalog)

            page_count = int(0)

            while True:
                for sound in results:
                    try:
                        sound.retrieve_preview(output_catalog)
                        info = "Saved file: " + str(output_catalog) + str(sound.name)
                        print(termcolor.colored(info, "green"))
                    except:
                        info = str("Sound can`t be saved to " + str(output_catalog) + str(sound.name) )
                        print(termcolor.colored(info, "red"))

                page_count += 1

                if not results.next or lim_page_count == page_count:
                    page_count = 0
                    break

                results = results.next_page()
        except:
            print(termcolor.colored(" Search is failed ", "red"))

if __name__ == "__main__":
    main()
