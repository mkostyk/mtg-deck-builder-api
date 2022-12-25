# MTG Deck Builder API

This is an API built for Magic The Gathering Deck Builder. You can access this API's documentation on localhost:8000/docs. 

### Project is still in development.

### Developer setup:
Step 0: Make sure you have python3 installed. If you don't you can download Python3 from [here](https://www.python.org/downloads/release/python-3110/)  
Step 0.5: Install pip and pipenv
```
python -m ensurepip --upgrade
pip install pipenv
```

Step 1: Clone this repo from github
```
git clone https://github.com/mkostyk/mtg-deck-builder-api.git
```

Step 2: Start pipenv shell
```
cd mtg-deck-builder-api
pipenv shell
```  

Step 3: Install all required packages
```
pipenv install
```  

Step 4: Run development server
```
python ./mtg_deck_builder_api/manage.py runserver
```  

And you are ready to go!