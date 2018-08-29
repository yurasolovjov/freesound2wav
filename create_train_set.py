import sys, os
import argparse
import termcolor
import shutil
import ffmpeg
import subprocess
import ffmpeg
import wave
import contextlib
import librosa
import soundfile as sf
from glob import glob

from pydub import AudioSegment

# Заголовок метафайла
header = "filename,event_label,database,begin,end"

tokens_class = ["engine","door","glass","idling","car","others"]
tokens_database = ["audioset","freesound","urbansound","youtube","unknown","dcase"]

def getListCatalogs(catalog):
    fusionCatalogs = list()

    token = catalog + "/*/"
    Catalogs = glob(token);

    # if len(Catalogs) == 0:
    #     return [catalog]

    fusionCatalogs += Catalogs

    for incatalog in Catalogs:
        fusionCatalogs += getListCatalogs(incatalog)

    return fusionCatalogs

def makeWaveFilesList(catalog):
    tokens = ["//*.wav","//*.mp3","//*.mp4"]

    Catalogs = getListCatalogs(catalog)
    Catalogs += [catalog]
    # Catalog = catalog + "/*/"
    # Catalogs = glob(Catalog);
    #
    # Catalogs = Catalogs + [catalog]
    listWavFiles = list()

    for catalog in Catalogs:
        for token in tokens:
            template = str(os.path.normpath(catalog) + token)
            sounds = glob(template);

            for sound in sounds:
                listWavFiles.append(sound);

    return listWavFiles, len(listWavFiles)

def main():
    parser = argparse.ArgumentParser(description="Options");
    parser.add_argument("-i", "--input", help="in-catalog", action="append", default=None, nargs="*")
    parser.add_argument("-o", "--output", help="out-catalog with wav-files", default=None)
    parser.add_argument("--only_csv_create", help="create csv-meta file", default=bool(False))
    parser.add_argument("--ignore", help="ignore input catalog. Only converted files and create csv metafile", default=bool(False))
    parser.add_argument("--convert", help="Convert files to other pcm", default=bool(False))
    parser.add_argument("--pcm", help="Convert files to pcm 16 or pcm 8", default=int(16000))

    args = parser.parse_args()

    inputCatalogs = args.input
    outputCatalog = args.output
    only_csv = bool(args.only_csv_create)
    convert_files = bool(args.convert)
    pcm = int(args.pcm)
    ignore = bool(args.ignore)

    if pcm != 16000 and pcm != 8000 and convert_files == True:
        raise Exception("pcm is incorrected !")

    if outputCatalog == None:
        raise Exception("Output catalog is None");
    else:
        outputCatalog = os.path.abspath(outputCatalog)

    if inputCatalogs == None:
        raise Exception("Input catalog is None");

    search_tokens = list()

    for input in inputCatalogs:
        fusion_input = str()
        for k in input:
            fusion_input += k + ' '

        if fusion_input[-1] == ' ':
            fusion_input = fusion_input[:-1]

        search_tokens.append(fusion_input)

    if not os.path.exists(outputCatalog):
        os.makedirs(outputCatalog)

    fusionListFiles = list()

    if only_csv == False and ignore == False :
        for inputCatalog in search_tokens:
            listFiles,_ = makeWaveFilesList(str(inputCatalog))
            fusionListFiles += listFiles


        all_files = len(fusionListFiles)
        exists_files = glob(outputCatalog +"//*.wav")

        if len(exists_files) > 0:
            counter = len(exists_files) + 1
        else:
            counter = int(0)

        all_files += counter - 1
        subtract = list()

        for file in fusionListFiles:
            t,h = os.path.split(file)
            h = str(h).lower().split(".")
            t = str(t).lower()

            name = str("")

            info = "in: "+str(file)

            for token in tokens_class:
                token = str(token).lower()
                if( h[0].find(token) >= 0 or t.find(token) >= 0):
                        name = str(token) + "_"
                        break
                else:
                    name = str("unknown") + "_"

            db_type = str("")

            for token in tokens_database:
                token = str(token).lower()

                if( t.find(token) >= 0):
                    db_type = token
                    break
                else:
                    db_type = str("unknown")

            name += str(db_type)+str("_")
            name += '{0:05}'.format(counter)
            name += "."+ "wav"

            if name == "":
                subtract.append(file)

            outfile = os.path.normpath(outputCatalog + "//" + name)
            info += " out: "+str(outfile)
            info += str(" ") + str(counter) +"/" + str(all_files)

            counter += 1

            try:
                if not os.path.exists(outfile):
                    if h[1] != "wav":
                        soa = AudioSegment.from_file(file)
                        soa.export(outfile, format="wav")
                    else:
                        shutil.copy(file, outfile)

                info += " - successful"
                color = "green"
            except:
                info += " - failed"
                color = "red"

            print(termcolor.colored(info, color))

    csv_file = list()

    csv_file.append(header)

    all_conv_files = glob(outputCatalog +"//*.wav")

    all_files= len(all_conv_files)

    counter = int(0)
    counter_err = int(0)

    converted_info = str(" ")

    if only_csv == False and convert_files == True:
        counter = int(0)
        counter_err = int(0)
        t,h = os.path.split(outputCatalog)
        outputConvCatalog = os.path.normpath(t + "//" + h + str("_") + str(pcm)+str("Hz"))

        if not os.path.exists(outputConvCatalog):
            os.makedirs(outputConvCatalog)


        for file in all_conv_files:
            info = str("")
            _,h = os.path.split(file)
            outputConvFile = os.path.join(outputConvCatalog,h)

            try:
                f, s = librosa.load(os.path.normpath(file))

                if pcm == 16000:
                    str_pcm = "PCM_16"
                elif pcm == 8000:
                    str_pcm = "PCM_8"
                else:
                    raise Exception("pcm in incorrected")

                fconv = librosa.resample(f, s, pcm) # преобразовываем в 16кГц
                sf.write(outputConvFile, fconv, pcm, str_pcm)

                info += "CONVERTED "+str_pcm+" - OK: " + outputConvFile + "    " +str(counter) + "/"+str(all_files)
                color = "green"
            except:
                counter_err += 1
                info += "CONVERTED - FAILED: "+ outputConvFile
                color = "red"

            print(termcolor.colored(info, color))
            info = str("")
            counter += 1

        converted_info += " converted files: " +str(counter) + " bad converted files: "+str(counter_err)
        counter = int(0)
        counter_err = int(0)

        outputCatalog = outputConvCatalog
        all_conv_files = glob(outputConvCatalog +"//*.wav")

    for file in all_conv_files:

        t,h = os.path.split(file)

        name_arr = str(h).split("_")
        kind = str(name_arr[0]).lower()

        db = str(name_arr[1])

        duration = float(0.0)

        info = str("")

        try:
            with contextlib.closing(wave.open(file,'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()

                duration = frames/float(rate)

            info += "CSV - OK: "+str(file) +"  "+ str(counter) +"/"+str(all_files)
            color = "green"
        except:
            info += "CSV - Error: "+str(file) +"  "+ str(counter) +"/"+str(all_files)
            color = "red"
            counter_err += int(1)


        print(termcolor.colored(info, color))

        csv_file.append( str(h)+","+kind+","+db+","+str(0)+","+str(duration))
        counter += int(1)

    meta_file = os.path.normpath(outputCatalog + "//meta.csv")

    with open(meta_file,"w") as f:
        for item in csv_file:
            f.write("%s\n" % item)


    common_info = "Created cvs-meta file: " + str(meta_file) + " processed files: "+str(counter) + " bad processed files: "+str(counter_err)
    common_info += converted_info
    print(termcolor.colored(common_info, "yellow"))

if __name__ == "__main__":
    main()
