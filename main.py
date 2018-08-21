import sys, os
import argparse
import termcolor

mainfile = os.path.abspath(sys.modules['__main__'].__file__)

t,h = os.path.split(mainfile)

path2fs = os.path.normpath(t + '//freesound-python')
sys.path.insert(0,path2fs)

import freesound

GEN_KEY_FREESOUND = str("PYqNLRWMA9URy55hSbzK5lGxJsgVJaBsvRx6giFG")

def main():

    parser = argparse.ArgumentParser(description="Options");
    parser.add_argument("-s", "--search", help="Keyword for search", action="append", default=None, nargs="*")
    parser.add_argument("-o", "--out", help="Output catalog", default="../freesound")

    args = parser.parse_args()

    search_tokens = list()
    keywords = args.search
    output = os.path.normpath(args.out)

    for keyword in keywords:
        fusion_keyword = str()
        for k in keyword:
            fusion_keyword += k + ' '

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

            for sound in results:
                try:
                    sound.retrieve_preview(output)
                    info = "Saved file: " + str(output) + str(sound.name)
                    print(termcolor.colored(info, "green"))
                except:
                    print(termcolor.colored("Sound can`t be saved", "red"))
        except:
            print(termcolor.colored(" Search is failed ", "red"))



if __name__ == "__main__":
    main()
