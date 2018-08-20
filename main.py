import sys, os
import argparse

mainfile = os.path.abspath(sys.modules['__main__'].__file__)

t,h = os.path.split(mainfile)

path2fs = os.path.normpath(t + '//freesound-python')
sys.path.insert(0,path2fs)

import freesound

GEN_KEY_FREESOUND = str("PYqNLRWMA9URy55hSbzK5lGxJsgVJaBsvRx6giFG")

def main():

    parser = argparse.ArgumentParser(description="Options");
    parser.add_argument("-s", "--search", help="Word for search", default=None);
    parser.add_argument("-o", "--out", help="Output catalog", default="../freesound");

    args = parser.parse_args()

    search_tokens = args.search
    output = os.path.normpath(args.out)

    if not os.path.exists(output):
        os.makedirs(output)

    if search_tokens == None:
        raise Exception("Not found word");

    client = freesound.FreesoundClient()
    client.set_token(GEN_KEY_FREESOUND,"token")

    results = client.text_search(query="glass",fields="id,name,previews")

    for sound in results:
        sound.retrieve_preview(output)
        print(sound.name)



if __name__ == "__main__":
    main()
