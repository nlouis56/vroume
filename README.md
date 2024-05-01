# VROUME

Virtual Realm Of Useful Music Evaluation

## install the dependencies

`pip install -r ./features_extraction/requirements.txt`

## run the feature extractor

`python3 feature_extractor.py -i ../data/genres_original -o ../features -d 5 `

will extract the features from the songs present in subfolders of `../data/genres_original` (sorted by genre) and save them in `../features` with a frame duration of 5 (the song will be analysed 5 seconds at a time, a 20-second song will create 4 frames).

## run the cleanser

`python3 data_cleaner.py -i ../features `

will clean the features present in `../features` and save them in the same folder, appending `.cleaned.csv` to the filename.
