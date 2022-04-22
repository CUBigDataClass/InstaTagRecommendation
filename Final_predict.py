import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
import matplotlib.image as mpimg
from PIL import Image
import io
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS, ALSModel
from sklearn.model_selection import train_test_split
from functools import reduce
from functions import prepare_image, extract_features
import os
from tqdm import tqdm
from scipy.spatial.distance import cosine
np.random.seed(0)



import pandas as pd

file_name = "/all_hashtags.pk1"
all_hashtags = pd.read_pickle(file_name)


hashtag_metadata = pd.read_pickle("/hashtag_metadata.pkl")


pics = pd.read_pickle("/content/drive/MyDrive/tag_pic_features.pkl")


hashtag_lookup = pd.read_pickle("/hashtag_lookup.pkl")


hashtag_index = list(all_hashtags)
def lookup_hashtag(hashtag_id):
    return hashtag_index[hashtag_id]

def lookup_hashtag_recs(rec_scores):
    return [lookup_hashtag(rec) for (rec, score) in rec_scores


            
recs['recommended_hashtags'] = recs['recommendations'].apply(lookup_hashtag_recs)
recs.index = recs['image_id']
recs = recs.join(hashtag_metadata, how='left')[['recommendations',
                                                 'recommended_hashtags',
                                                 'hashtags',
                                                 'image_local_name',
                                                 'search_hashtag']]
            
            
recs.drop('recommendations', axis=1, inplace=True)
image_factors = als_model.userFactors.toPandas()
image_factors.index = image_factors['id']
recs.join(image_factors);
            
            
            
# Add deep features information to recs dataframe
recs_deep = recs.join(pics, on='image_local_name', how='inner')
recs_deep.info()
            
            
            
ashtags_df = pd.DataFrame.from_dict(hashtag_lookup, orient='index')
hashtags_df.head()
hashtags_df = hashtags_df.reset_index()
hashtags_df.columns = ['hashtag', 'id']
hashtags_df.index = hashtags_df['id']
hashtags_df.drop('id', axis=1, inplace=True)
            
### create our neural network ###
img_shape = (160, 160, 3)

# Create the base model from the pre-trained model MobileNet V2
base_model = MobileNetV2(input_shape=img_shape, include_top=False, weights='imagenet')

global_average_layer = tf.keras.layers.GlobalAveragePooling2D()

neural_network = tf.keras.Sequential([
  base_model,
  global_average_layer,
])
            
            


### ALS MODEL #####            
spark = SparkSession.builder.master('local').getOrCreate()


als_model = ALSModel.load("/content/drive/MyDrive/ALS_MODEL/als")


recs = als_model.recommendForAllUsers(numItems=10).toPandas()
            


            

img_features = als_model.userFactors.toPandas()
hashtag_features = als_model.itemFactors.toPandas()

# Only use certain columns
recs_deep_clean = recs_deep[['image_local_name', 'hashtags', 'deep_features']]

img_features.index = img_features['id']
img_features.drop(['id'], axis=1)

# Add image feature into dataframe
recommender_df = recs_deep_clean.join(img_features, how='inner')
recommender_df.head()
            
            
            
            
# Function that finds k nearest neighbors by cosine similarity
def find_neighbor_vectors(image_path, k=5, recommender_df=recommender_df):
    """Find image features (user vectors) for similar images."""
    prep_image = prepare_image(image_path, where='local')
    pics = extract_features(prep_image, neural_network)
    rdf = recommender_df.copy()
    rdf['dist'] = rdf['deep_features'].apply(lambda x: cosine(x, pics))
    rdf = rdf.sort_values(by='dist')
    return rdf.head(k)


def generate_hashtags(image_path):
    fnv = find_neighbor_vectors(image_path, k=5, recommender_df=recommender_df)
    # Find the average of the 5 user features found based on cosine similarity.
    features = []
    for item in fnv.features.values:
        features.append(item)

    avg_features = np.mean(np.asarray(features), axis=0)
    
    # Add new column to the hashtag features which will be the dot product with the average image(user) features
    hashtag_features['dot_product'] = hashtag_features['features'].apply(lambda x: np.asarray(x).dot(avg_features))

    # Find the 10 hashtags with the highest feature dot products
    final_recs = hashtag_features.sort_values(by='dot_product', ascending=False).head(10)
    # Look up hashtags by their numeric IDs
    output = []
    for hashtag_id in final_recs.id.values:
        output.append(hashtags_df.iloc[hashtag_id]['hashtag'])
    return output


def show_results(test_image):
    img = mpimg.imread(f'{test_image}.jpg')
    plt.figure(figsize=(9, 9))
    plt.title(f'Original Hashtag: {test_image.upper()}', fontsize=32)        
    plt.imshow(img)
    
    recommended_hashtags = generate_hashtags(f'{test_image}.jpg')
    print(', '.join(recommended_hashtags))
            
            
            
show_results('/architecture')
