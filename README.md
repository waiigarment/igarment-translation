# Program to analyze translate and sentences

python version - 3.10.13
spacy version - 3.7.4

## commands to install spacy

pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
python -m spacy download ja_core_news_sm

## programs and features

The command to run the program is as follow. Currently running at port 8080.

``` python
python app.py
```

- ./app.py is main entry file to run web services.
- ./core.py is main core program for processing.
- ./datafiles is a directory that has some data files for testing.
- Other files are the ones related to the web service.
