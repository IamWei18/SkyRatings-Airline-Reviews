import pandas as pd
import nltk
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.tree import Tree
from nltk import word_tokenize, pos_tag, ne_chunk, WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
import string
from transformers import pipeline
import numpy as np # linear algebra
import warnings
warnings.filterwarnings('ignore')

# Download the required NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

!unzip /usr/share/nltk_data/corpora/wordnet.zip -d /usr/share/nltk_data/corpora/

from sklearn.model_selection import train_test_split, cross_val_score,cross_val_predict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_curve, RocCurveDisplay, accuracy_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, MinMaxScaler



from google.colab import drive
drive.mount('/content/drive')

airline_data = pd.read_csv('/content/drive/MyDrive/Text Mining/Airline_Reviews.csv')

# Display the first few rows of the dataframe to understand its structure and contents

airline_data.head()

# Checking for missing values and data types
missing_values = airline_data.isnull().sum()
data_types = airline_data.dtypes

missing_values, data_types

# Data Cleaning and Organization

# Converting 'Overall_Rating' to a numerical type
# We first need to ensure that all values in 'Overall_Rating' can be converted to numbers
# We will replace non-numeric values with NaN and then convert the column to float
airline_data['Overall_Rating'] = pd.to_numeric(airline_data['Overall_Rating'], errors='coerce')

# Renaming the 'Unnamed: 0' column to 'Review_ID'
airline_data.rename(columns={'Unnamed: 0': 'Review_ID'}, inplace=True)

# Checking for non-numeric values in 'Overall_Rating' and the updated DataFrame structure
non_numeric_ratings = airline_data['Overall_Rating'].isnull().sum()
updated_structure = airline_data.dtypes

non_numeric_ratings, updated_structure

# Converting 'Overall_Rating' to a numerical type
airline_data['Overall_Rating'] = pd.to_numeric(airline_data['Overall_Rating'], errors='coerce')

# Renaming the 'Unnamed: 0' column to 'Review_ID'
airline_data.rename(columns={'Unnamed: 0': 'Review_ID'}, inplace=True)

# Handling missing values for ratings by imputing with the median
rating_columns = ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages',
                  'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 'Value For Money']

for col in rating_columns:
    median_value = airline_data[col].median()
    airline_data[col].fillna(median_value, inplace=True)

# Converting 'Review Date' and 'Date Flown' to datetime format
airline_data['Review Date'] = pd.to_datetime(airline_data['Review Date'], errors='coerce')
airline_data['Date Flown'] = pd.to_datetime(airline_data['Date Flown'], errors='coerce')

# Creating a new column 'Rating Category' to categorize overall ratings
airline_data['Rating Category'] = pd.cut(airline_data['Overall_Rating'], bins=[0, 3, 7, 10], labels=['Low', 'Medium', 'High'])

# Checking the updated DataFrame and summary of changes
updated_summary = airline_data[['Overall_Rating', 'Review Date', 'Date Flown', 'Rating Category']].describe(include='all')
updated_summary, airline_data.dtypes

# Converting 'Overall_Rating' to a numerical type and renaming 'Unnamed: 0' to 'Review_ID'
airline_data['Overall_Rating'] = pd.to_numeric(airline_data['Overall_Rating'], errors='coerce')
airline_data.rename(columns={'Unnamed: 0': 'Review_ID'}, inplace=True)

# Removing all columns except the specified ones
columns_to_keep = ['Airline Name', 'Overall_Rating', 'Review_Title', 'Review', 'Recommended']
airline_data_reduced = airline_data[columns_to_keep]

# Displaying the first few rows of the updated DataFrame
airline_data_reduced.head()

# Setting the style for the plots
sns.set(style="whitegrid")

# Visualizations

# 1. Distribution of Overall Ratings
plt.figure(figsize=(10, 6))
sns.countplot(x='Overall_Rating', data=airline_data)
plt.title('Distribution of Overall Ratings')
plt.xlabel('Overall Rating')
plt.ylabel('Count')
plt.show()

# 2. Distribution of Ratings by Category
plt.figure(figsize=(10, 6))
sns.countplot(x='Rating Category', data=airline_data, order=['Low', 'Medium', 'High'])
plt.title('Distribution of Ratings by Category')
plt.xlabel('Rating Category')
plt.ylabel('Count')
plt.show()

# 3. Number of Reviews Over Time (Year)
plt.figure(figsize=(12, 6))
airline_data['Review Date'].groupby(airline_data["Review Date"].dt.year).count().plot(kind='bar')
plt.title('Number of Reviews Over Years')
plt.xlabel('Year')
plt.ylabel('Number of Reviews')
plt.show()

# 4. Average Rating for Top 10 Airlines (with most reviews)
top_airlines = airline_data['Airline Name'].value_counts().head(10).index
avg_ratings_top_airlines = airline_data[airline_data['Airline Name'].isin(top_airlines)].groupby('Airline Name')['Overall_Rating'].mean()
plt.figure(figsize=(12, 6))
avg_ratings_top_airlines.sort_values().plot(kind='barh')
plt.title('Average Rating for Top 10 Airlines')
plt.xlabel('Average Rating')
plt.ylabel('Airline Name')
plt.show()

# Combining 'Review_Title' and 'Review' into a single column
airline_data_reduced['Combined_Review'] = airline_data_reduced['Review_Title'] + " " + airline_data_reduced['Review']

# Displaying the first few rows of the updated DataFrame to verify the combination
airline_data_reduced.head()

import re
from nltk.corpus import stopwords

def preprocess_text_simple(text):

    # Removing special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenization
    tokens = text.split()
    # Removing stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Then apply this function to your DataFrame column
airline_data_reduced['Processed_Review'] = airline_data_reduced['Combined_Review'].apply(preprocess_text_simple)

# Display the first few rows of the DataFrame to show the results
print(airline_data_reduced[['Combined_Review', 'Processed_Review']].head())

from sklearn.feature_extraction.text import TfidfVectorizer

# Create a TF-IDF Vectorizer instance
tfidf_vectorizer = TfidfVectorizer(max_features=1000)  # You can adjust max_features as needed

# Fit and transform the 'Processed_Review' column
tfidf_matrix = tfidf_vectorizer.fit_transform(airline_data_reduced['Processed_Review'])

# Inspect the resulting matrix
print(tfidf_matrix.shape)  # This shows the shape of the TF-IDF matrix

# To get feature names (words)
feature_names = tfidf_vectorizer.get_feature_names_out()
print(feature_names)  # This will print the words corresponding to each column in the matrix

# Named Entity Recognition

# Install spaCy if havent
# !pip install spacy

import spacy
nlp = spacy.load('en_core_web_sm')

# Function to extract named entities using spaCy
def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Assuming airline_data_reduced is your DataFrame and 'Processed_Review' is the column with processed text
# Apply the extract_entities function to each review
airline_data_reduced['Spacy_Entities'] = airline_data_reduced['Processed_Review'].apply(extract_entities)

# Now, your DataFrame has a new column 'Spacy_Entities' with the extracted entities
print(airline_data_reduced[['Processed_Review', 'Spacy_Entities']].head())

# Displaying output with displacy
from IPython.display import HTML

# Function to highlight entities in the text with improved styling
def highlight_entities(doc):
    colors = {
        'ORG': '#E74C3C',   # Bright red
        'PERSON': '#2ECC71', # Vivid green
        'GPE': '#3498DB',    # Bright blue
        'DATE': '#F39C12',   # Vivid orange
        'TIME': '#9B59B6'    # Vivid purple
    }
    style = "border-radius: 3px; padding: 2px 4px; margin: 0 2px; display: inline-block;"
    text_style = "font-weight: bold; color: #333;"  # Dark text color for better readability
    highlighted_text = ""

    for token in doc:
        color = colors.get(token.ent_type_, '#f2f2f2')  # Light grey for non-entities
        highlighted_text += f"<mark style='background-color: {color}; {style}'>" \
                            f"<span style='{text_style}'>{token}</span></mark>"

    return highlighted_text

# Display the first 10 reviews with highlighted entities and list of entities
# For the header Color
header_style = "color: #ffffff; font-weight: bold; font-size: 1.2em;"

# For the entity list items:
list_item_style = "background-color: #f0f0f0; color: #000; padding: 2px 4px; margin: 2px 0; border-radius: 3px;"

# Apply the styles in the display code
for index, row in airline_data_reduced.head(10).iterrows():
    doc = nlp(row['Processed_Review'])
    entities_html = "".join([f"<li style='{list_item_style}'>{ent.text} ({ent.label_})</li>" for ent in doc.ents])
    entities_html = f"<ul style='list-style-type: none; padding: 0;'>{entities_html}</ul>"

    display(HTML(f"<div style='margin-bottom: 20px;'><h3 style='{header_style}'>Review {index + 1}:</h3>"))
    display(HTML(f"<div style='background: #f9f9f9; border-left: 6px solid #ccc; padding: 15px; margin: 10px 0;'>{highlight_entities(doc)}{entities_html}</div>"))

# Sentiment Analysis
# from google.colab import drive
# drive.mount('/content/drive')
airline_df = pd.read_csv('/content/drive/MyDrive/Text Mining/Airline_Reviews.csv')

# Find the count of unique values in the index
airline_df['Overall_Rating'].value_counts()

# Since there are some ratings with n value, then replace n with 0
def convert(rating):
    if rating == 'n':
        return '0'
    else:
        return rating

airline_df['Overall_Rating'] = airline_df['Overall_Rating'].apply(lambda x: convert(x))
airline_df['Overall_Rating'].value_counts()

airline_df['Overall_Rating'] = airline_df['Overall_Rating'].astype(int)

# Convert Overall_Rating columns into only 4 different values
airline_df['New_Ratings'] = pd.cut(airline_df['Overall_Rating'], 4, labels = [1,2,3,4])
airline_df['New_Ratings'].unique()

# Get rid of Overall_Rating column since New_Ratings column available
airline_df = airline_df.drop(['Overall_Rating', 'Unnamed: 0'], axis = 1)

airline_df.info()

# Handle the NULL values

# Dropping 'Aircraft', 'Wifi & Connectivity', 'Route' and 'Inflight Entertainment' columns.
airline_df = airline_df.drop(['Aircraft', 'Wifi & Connectivity', 'Route', 'Inflight Entertainment'], axis = 1)

# Dropping the rows which 'Food & Beverages' is null.
airline_df = airline_df.dropna(axis = 0, subset = ['Food & Beverages'])

airline_df.head()

# Count the number of missing values in the dataset
airline_df.isnull().sum()

# Drop the Airline Name column as it has over 400 different names
airline_df = airline_df.drop('Airline Name', axis = 1)

# Plot of Verified and New_Ratings
sns.set_theme(style = 'darkgrid', palette = 'pastel')
plt.figure(figsize = (10, 4))
sns.countplot(data = airline_df, x = 'Verified', hue = 'New_Ratings')

# Plot of Recommended and New_Ratings
sns.set_theme(style = 'darkgrid', palette = 'pastel')
plt.figure(figsize = (10, 4))
sns.countplot(data = airline_df, x = 'Recommended', hue = 'New_Ratings')

# From the above plot show that about 2000 people write a 'Very bad review' but still recommending the company. These are clearly an outlier case!

# len() function returns the number of items in an object.
len(airline_df[(airline_df['Recommended'] == 'yes') & (airline_df['New_Ratings'] == 1)])

# It seems like that there is something happened when they submit their reviews. These are clearly good reviews!
# But since do not know exactly how they rate the company? Then, need to drop the realted rows.
i = airline_df[(airline_df['Recommended'] == 'yes') & (airline_df['New_Ratings'] == 1)].index
airline_df = airline_df.drop(i)

# Plot the final results with the same graph
sns.set_theme(style = 'darkgrid', palette = 'pastel')
plt.figure(figsize = (10, 4))
sns.countplot(data = airline_df, x = 'Recommended', hue = 'New_Ratings')

# convert 'Verified' from bool into int type
airline_df['Verified'] = airline_df['Verified'].astype(int)

# Dropping 'Review' columns.
airline_df = airline_df.drop('Review', axis = 1)

# Data Preprocessing for sentiment analysis
#Lowering all the letters and then saving it in the new column(Review Title).
airline_df['Review Title'] = airline_df['Review_Title'].apply(lambda x: x.lower())

# Removing all punctuation marks.
airline_df['Review Title'] = airline_df['Review Title'].replace(r'[^\w\s\d+]', '', regex = True)

# Tokenizing the titles.
airline_df['Review_Title_Tokenized'] = airline_df['Review Title'].apply(lambda x: word_tokenize(x))

# Removing the stopwords.
stopwords = set(stopwords.words('english'))
airline_df['Review_Title_Tokenized'] = airline_df['Review_Title_Tokenized'].apply(lambda x: [word for word in x if word not in stopwords])

# Pos tagging words. (for more info check this: https://en.wikipedia.org/wiki/Part-of-speech_tagging)
airline_df['Title_pos_tag'] = airline_df['Review_Title_Tokenized'].apply(lambda x: nltk.pos_tag(x))

# It is a function for converting pos tag into wordnet tags.
def to_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    elif tag.startswith('V'):
        return wordnet.VERB
    else:
        return None
airline_df['Title_wordnet_tags'] = airline_df['Title_pos_tag'].apply(lambda x: [(word, to_wordnet_pos(tag)) for (word, tag) in x])

# Lemmatizing the words. (if you don't know what is lemmatizing check this: https://en.wikipedia.org/wiki/Lemmatisation)
lemmatizer = WordNetLemmatizer()
airline_df['Title_lemmatized'] = airline_df['Title_wordnet_tags'].apply(lambda x: [lemmatizer.lemmatize(word, tag) if tag is not None else
                                                                             word for word, tag in x])

# Let's put it together.
airline_df['title_filtered'] = airline_df['Title_lemmatized'].apply(lambda x: ' '.join(x))

airline_df.head()

# Removing unnecessary columns.
airline_df = airline_df.drop(['Review_Title','Review Date', 'Date Flown', 'Verified', 'Review Title', 'Review_Title_Tokenized', 'Title_pos_tag',
                        'Title_wordnet_tags', 'Title_lemmatized', 'Type Of Traveller'], axis = 1)

airline_df.head()

# Filling null values
airline_df.isnull().sum()

# Since most of the people flight in Economy Class, then fill null values with this.
airline_df['Seat Type'] = airline_df['Seat Type'].fillna('Economy Class')
airline_df['Cabin Staff Service'] = airline_df['Cabin Staff Service'].fillna(airline_df['Cabin Staff Service'].mode())
airline_df['Seat Comfort'] = airline_df['Seat Comfort'].fillna(airline_df['Seat Comfort'].mode())

#@ There are more than 1000 null values for 'Ground Service' column, it is not that many,
# because it's very 'sensitive' feature, wrong 'fillings' may decrease model's performance.
# So, we're going to drop the rows where 'Ground Service's values is null!
airline_df = airline_df.dropna(subset = 'Ground Service', axis = 0)
airline_df.info()

# Create dummy variables (Seat Comfort = Business Class, Economy Class, First Class, Premium Economy)
dummie_seat_type = pd.get_dummies(airline_df['Seat Type'])

df_new = pd.concat([airline_df, dummie_seat_type], axis = 1)
# Then remove the previous seat type
df_new = df_new.drop('Seat Type', axis = 1)
df_new.reset_index(drop = True)

# Due to machine can only understand numbers. So, need to convert categorical features into numbers.
# LabelEncoder helps us to convert categorical features into numbers
le = LabelEncoder()

df_new['Recommended'] = le.fit_transform(df_new['Recommended'])
df_new['Recommended'] = df_new['Recommended'].astype(int)

df_new['New_Ratings'] = df_new['New_Ratings'].astype(int)

df_new['Economy Class'] = le.fit_transform(df_new['Economy Class'])
df_new['Economy Class'] = df_new['Economy Class'].astype(int)

df_new['First Class'] = le.fit_transform(df_new['First Class'])
df_new['First Class'] = df_new['First Class'].astype(int)

df_new['Premium Economy'] = le.fit_transform(df_new['Premium Economy'])
df_new['Premium Economy'] = df_new['Premium Economy'].astype(int)

df_new['Business Class'] = le.fit_transform(df_new['Business Class'])
df_new['Business Class'] = df_new['Business Class'].astype(int)

df_new.info()

# CountVectorizer converts a collection of text documents to a matrix of token counts.
# Setting min_df = 0.001 means, that any word which can used under 0.001 of samples will be removed.
vectorizer = CountVectorizer(min_df = 0.001)

# Created a pandas dataframe with all the worlds in 'title_filtered' column. Each word represents as a column.
vectorized = vectorizer.fit_transform(df_new['title_filtered'])
vectorized_df = pd.DataFrame(vectorized.toarray(), columns = vectorizer.get_feature_names_out())

vectorized_df.head()

df_new = df_new.reset_index(drop = True)

# Concatinating 'main' dataframe with 'vectorized_df'
df_final = pd.concat([df_new, vectorized_df], axis = 1)
df_final = df_final.drop('title_filtered', axis = 1)

df_final.head()

# Use MinMaxScaler for feature scaling because MultinomialNaiveBayes does not allow negative values.
scaler = MinMaxScaler()
X = scaler.fit_transform(df_final.drop('New_Ratings', axis = 1))
y = df_final['New_Ratings']
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state = 42)

# Modeling using different algorithms

# Multinomial Naive Bayes - This is very good when dealing with text data.
# Gradient Boosting Classifier - GB can handle many type of data
# Voting Classifier - Using voting classifier we can combine different models.

mnb = MultinomialNB()

gb_clf = GradientBoostingClassifier()

# Setting 'voting' parameter to soft will make the classifier to classify by probobalities.
vot_clf = VotingClassifier(estimators = [('mnb', mnb), ('gb_clf', gb_clf)], voting = 'soft')

model_names = ['MultinomialNB', 'GradientBoost', 'VotingClassifier']
models = [mnb, gb_clf, vot_clf]
count = 0
for model in models:
    cvalscore = cross_val_score(model, X_train, y_train, scoring = 'accuracy', cv = 5)
    print('Accuracy of {}: '.format(model_names[count]), cvalscore.mean())
    count = count + 1

# Gradient Boost fit to the data and then measure the accuracy score.
gb_clf.fit(X_train, y_train)
y_pred = gb_clf.predict(X_test)
print('Accuracy of GradientBoost: ', accuracy_score(y_test, y_pred))

# Confusion Matrix
classes = ['Very Bad', 'Bad', 'Average', 'Good']
scores = confusion_matrix(y_test, y_pred)
sns.set_theme(palette = 'pastel')
sns.heatmap(scores, annot = True, fmt = 'd', xticklabels = classes, yticklabels = classes)
plt.xlabel('Expected')
plt.ylabel('Predicted')
plt.title('Confusion Matrix')

# Commented out IPython magic to ensure Python compatibility.
###################################################################
# Alternative METHOD
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
import nltk
import sklearn
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook
# %matplotlib inline

# Make confirmation
# Displaying the first few rows of the updated DataFrame to verify the combination
airline_data_reduced.head()

# Create a new dataset and select certain column for Sentiment Analysis
airline_sentiment = airline_data_reduced.loc[:, ['Processed_Review','Recommended']]

airline_sentiment.head(10)

airline_sentiment.Recommended.value_counts()

# Bag of Words features (BOW)
# The preprocessed dataset is now ready. One last step is to convert it to numerical form (as machines only understand mathematical operations).
# Apply the bag-of-words technique to convert the dataset into numerical form.

# Bag of Words is a natural language processing(NLP) technique that is used to represent
# a text document into numerical form by considering the occurrence of words in the given document.
# It considers only two things - 1. A vocabulary of words, 2. presence(or frequency) of a word in a given document ignoring the order of the words(or grammar).
airline_train = airline_sentiment[:18000]
airline_test = airline_sentiment[18000:]

# Method 1 - use CountVectorizer from the sklearn package to get the bag-of-words representation of the training and testing dataset.
# Note: Will only consider training dataset to define the vocabulary and use the same vocabulary to represent the test dataset (as test data is supposed to be hidden).
# Thus, fit the vectorizer on the training data and use it to transform the test data
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,1))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

# (18000, 35972) means that there are 35972 unique English words in the vocabulary (derived from the training dataset)
# and each word is represented with a unique column in the dataset.

# Note: binary=False argument means that it fill the vocabulary vector with term-frequency.
# If binary=True, the vocabulary vector is filled by the presence of words (1 if the word is present and 0 otherwise).

# Let’s convert the output labels into the numerical form.
# Yes Recommended is represented by 1, while No Recommended is represented with 0.

train_labels = [1 if Recommended=='yes' else 0 for Recommended in airline_train['Recommended']]
test_labels = [1 if Recommended=='yes' else 0 for Recommended in airline_test['Recommended']]
print (len(train_labels), len(test_labels))

# Logistic Regression for sentiment analysis

# Bag-of-words features
# Unigrams: All unique words in a document
# BiGrams: All permutations of two consecutive words in a document
# TriGrams: All permutations of three consecutive words in a document

# UniGram bag-of-words features
# When the Bag of Words algorithm considers only single unique words in the vocabulary, the feature set is said to be UniGram.
# Let’s define train Logistic Regression classifier on unigram features:

clf = sklearn.linear_model.LogisticRegression()
clf.fit(tf_features_train, train_labels)

# Unigrams (Logistic Regression)
predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# Unigrams + Bigrams (Logistic Regression)
# Let’s repeat the same exercise with UniGram +BiGram features.
# This time the Bag-of-Words algorithm also considers consecutive pairs of words in the dictionary along with unique words.
# Then calculate these features by simply changing the ngram_range parameter to (1,2).

vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,2))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = sklearn.linear_model.LogisticRegression()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# The feature set size increases as there are considering Bi-Grams also.
# This time the model performs a little better as it have passed more information. Accuracy on test-set is now 91%.

# Unigrams + Bigrams + Trigrams (Logistic Regression)
# Repeat the same exercise after adding Tri-Gram features also into the feature set.
# This time also consider three consecutive word permutations also into the vocabulary.
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,3))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = sklearn.linear_model.LogisticRegression()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# This time do not see any significant increase in the accuracy.

# Linear Support Vector Machine (LSVM) for sentiment analysis
# Repeat the same exercise with Linear support vector machine(LSVM) classification result
# in order to check that which algorithms gives to best results.

# Unigram (LSVM)
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,1))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = sklearn.svm.LinearSVC()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# Using this model achieves 86% accuracy on test dataset which is slightly lower to what Logistic regression achieved.

# UniGrams + BiGrams (LSVM)
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,2))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = sklearn.svm.LinearSVC()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# And Yes. This time model achieves an accuracy of 90% on test set. Now LSVM is very close to the Logistic Regression results.

# UniGrams + BiGrams + TriGrams (LSVM)
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,3))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = sklearn.svm.LinearSVC()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# Again, similar to Logistic Regression results, model improve slightly after addition of TriGram features. Accuracy stands at 91% only.

# Naive Bayes for sentiment analysis
# So far that Logistic Regression and LSVM are giving an almost similar performance on test set and achieve an accuracy of 90% with UniGram + BiGram feature sets.
# And will do a similar iterations for the Multinomial Naive Bayes algorithm also.

# Unigrams (Naive Bayes)
from sklearn.naive_bayes import MultinomialNB

vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,1))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = MultinomialNB()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# Results are not much encouraging this time. It get the lowest accuracy with MNB classifier on the test data.
# Let’s try adding more information to check if it improves from existing 87% accuracy.

# Unigram+BiGrams (Naive Bayes)

vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,2))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = MultinomialNB()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# Accuracy has improved only 1% from the previous iteration but it still 2% below the results the other two approaches have given

# UniGrams + BiGrams + TriGrams (Naive Bayes)
vectorizer = sklearn.feature_extraction.text.CountVectorizer(binary=False,ngram_range=(1,3))
tf_features_train = vectorizer.fit_transform(airline_train['Processed_Review'])
tf_features_test = vectorizer.transform(airline_test['Processed_Review'])
print (tf_features_train.shape, tf_features_test.shape)

clf = MultinomialNB()
clf.fit(tf_features_train, train_labels)

predictions = clf.predict(tf_features_test)
print(sklearn.metrics.classification_report(test_labels, predictions, target_names=['Negative', 'Positive']))
print(sklearn.metrics.confusion_matrix(test_labels, predictions, labels=[0, 1]))

# And NO, this model is not any better from the last iteration.
# Do not see any accuracy improvements after adding TriGrams into the feature set. Result stands at 87%.

# Summary– (Sentiment Analysis)

# Model - (UniGrams), (Uni+BiGrams), (Uni+Bi+TriGrams)
# Logistic Regression - 89%, 91%, 91%
# Linear SVM - 87%, 90%, 91%
# MultiNomial Naive Bayes - 87%, 88%, 87%

# It can see that Logistic Regression and LSVM perform equally well and achieve an accuracy of 90% while the MNB classifier gives a slightly lower accuracy of 88%.
# Logistic Regression model with Unigram+BiGram bag-of-words features can be considered as the best model from this case study.

# Text summarization
import nltk
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer

def getTextFromDataFrameRow(row):
    # Assuming the row contains text data
    if pd.notna(row):  # Check if the row is not empty
        return str(row)
    return ""

def getSentScores(text, sentences, mode):
    sentence_scores = {}

    if not text.strip():
        # If the text is empty or contains only whitespace, return an empty dictionary
        return sentence_scores

    if mode == 'nltk':
        stopwords = nltk.corpus.stopwords.words('english')
        word_freqs = {}

        # calculate word frequencies in the main text
        for word in nltk.word_tokenize(text):
            if word not in stopwords:
                if word not in word_freqs.keys():
                    word_freqs[word] = 1
                else:
                    word_freqs[word] += 1

        # Check if word_freqs is not empty
        if word_freqs:
            # normalize word frequencies
            max_freq = max(word_freqs.values())

            for word in word_freqs.keys():
                word_freqs[word] = (word_freqs[word] / max_freq)

            # iterate over sentences and calculate sentence scores
            for sent in sentences:
                # skip sentences with more than or equal to 30 words
                if len(sent.split(' ')) >= 30:
                    continue
                # tokenize and lowercase words in the sentence
                for word in nltk.word_tokenize(sent.lower()):
                    # check if the word is in word_freqs
                    if word in word_freqs.keys():
                        # update sentence_scores dictionary wwith word frequencies
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_freqs[word]
                        else:
                            sentence_scores[sent] += word_freqs[word]

    return sentence_scores

def getSummaryForTopAndLastRows(data_frame, column_name, mode, top_rows=10, last_rows=10):
    total_rows = len(data_frame)

    # Summarize top rows
    print(f"Summarizing the top {top_rows} rows:")
    for index in range(top_rows):
        row = data_frame.iloc[index]
        text = getTextFromDataFrameRow(row[column_name])

        if not text.strip():
            print(f"Skipping empty row {index}")
            print("*********************************************")
            continue

        # tokenized text into a list of sentences
        sentences = nltk.sent_tokenize(text)
        # calculate sentence scores based on word frequencies
        sentence_scores = getSentScores(text, sentences, mode)
        # select top 7 sentences based on their scores
        summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
        # selected top sentences are joined into summary
        summary = ' '.join(summary_sentences)

        if summary:
            print(f"Row {index}: {summary}")
            print("*********************************************")
        else:
            print(f"No summary for Row {index}")
            print("*********************************************")

    # Summarize last rows
    print(f"\nSummarizing the last {last_rows} rows:")
    for index in range(total_rows - last_rows, total_rows):
        row = data_frame.iloc[index]
        text = getTextFromDataFrameRow(row[column_name])

        if not text.strip():
            print(f"Skipping empty row {index}")
            print("*********************************************")
            continue

        sentences = nltk.sent_tokenize(text)
        sentence_scores = getSentScores(text, sentences, mode)
        summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)

        if summary:
            print(f"Summary for Row {index}: {summary}")
            print("*********************************************")
        else:
            print(f"No summary for Row {index}")
            print("*********************************************")

# name of the column that want to summarize
column_name = 'Review'

print("\nText Summarization using NLTK:\n")
getSummaryForTopAndLastRows(airline_data_reduced, column_name, 'nltk', top_rows=10, last_rows=10)