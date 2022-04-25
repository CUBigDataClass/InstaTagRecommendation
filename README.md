# InstaTagRecommendation

<h3> <em> "Stop racking your brains, trying to guess trending hashtags. We have got you covered." </em> </h3>

Instagram is a fast-moving platform, so you need to make your content easy to discover. The best hashtags for Instagram, boost your post impressions by 2-3 times, making them viewable on the Explore section. Feel exhausted from guessing hashtags each time you post on Facebook, Twitter, Youtube, or Instagram? Embrace the power of our AI-based searcher — generate hashtags for social media automatically. This hashtag generator for Instagram provides you with relevant hashtags by analyzing your photo.

<br>

<h2> Software Architecture Diagram </h2>
Our Software Architecture diagram looks as follows:

![softwareArchitect](https://user-images.githubusercontent.com/10383141/165064227-30c441fe-0486-4399-839f-3a3819a81c3c.jpeg)


<br><br><hr>
As part of this project, we implemented <b>three API </b> funcitonalities.
<li> <b> Hash Tags Generator </b> </li>
<li><b> Captions Generator </b> </li>
<li> <b> Top 15 trending hash tags </b> </li>
<br><br>
Our home page has all the three supported APIs and looks as follows:

![Homepage](https://user-images.githubusercontent.com/10383141/165058637-23f888ef-09f4-4e0a-ae85-3e464e1fa784.png)

<br><br>
<h2> Top trending hash tags </h2>

We have a CRON Job (Scraping Job) that is deployed on cloud scheduler which is periodically executed to scrape top trending instagram tags and captions. 
This data is then stored in MongoDb which would be later used to write to Redis Db.
We also have another CRON job (Redis Job) that continously checks for an update in MongoDb. Once the scraping job updates our instagram tags and captions, this Redis Cron Job shall update the Redis Cache with the top trending instagram tags thus making it real time. 
Since these CRON Jobs are async tasks, we are using GCP queues. The scraping job makes sure the suggested hash tags are real time and up-to-date.

<li><b>Working Demo</b><br></li>
Our Top 15 hash tags generator looks as follows:

![app-hashtag-list](https://user-images.githubusercontent.com/10383141/165059068-652d57df-3692-475f-96a1-c81ab42fbbac.png)

Upon choosing the particular hashtag, we shall display the top 15 trending hash tags in real time. 
![HashTag-list](https://user-images.githubusercontent.com/10383141/165059097-83a526b1-b0e1-43bd-b150-0aa9457d9bfb.png)

We sorted trending hashtags by categories to speed up your research.

<h2> Hash Tags Generator </h2>

Our AI based model suggests recommended hash tags for your image using popular and state-of-the-art ALS model.
We trained our model using the scraped Instagram data. Please check the references folder for more information about the model.

<li><b>Working Demo</b><br></li>
Our Hash Tags generator looks as follows:

![app-tag-generator](https://user-images.githubusercontent.com/10383141/165058743-1aedb484-4f2a-43ee-8f67-ab45c40a39c9.png)

Upon uploading the image and clicking on submit, a request shall be sent to the REST server and the hash tags are displayed for that image as follows:

![app-tags-display](https://user-images.githubusercontent.com/10383141/165069789-06a32e11-85f5-4fa5-80ed-797fb2a72f36.png)


<br><br>
<h2> Captions Generator </h2>

Our AI based model suggests recommended hash tags for your image using popular and state-of-the-art ML model.
We trained our model using the scraped Instagram data. Please check the references folder for more information about the model.

<li><b>Working Demo</b><br></li>
Our Captions generator API looks as follows:

![app-caption-generator](https://user-images.githubusercontent.com/10383141/165059006-ee637c1c-3afe-41e9-a2d1-63d3f4d00a6b.png)

Upon uploading the image and clicking on submit, a request shall be sent to the REST server and the captions are displayed for that image as follows:
![app-caption-display](https://user-images.githubusercontent.com/10383141/165059034-ed3ec5ee-15ee-440b-97e7-468477d26321.png)

<br><br>
<h2> Deployement </h2>
  <li>We used Google Cloud platform to deploy our VMs.</li>
  <li>For deploying our Databases, we used the MongoDb - Cloud MarketPlace API. </li>
  <li>We preferred to use Redis Cache as a service in the GCP VM rather than an external server or Cloud MarketPlace API considering the size of our data. </li>
  <li>We used RabbitMQ and GCP queues as our queue service</li>
  <li>We also used Cloud Scheduler to schedule our CRON Josbs</li>

<br><br>
<h2> Future Scope </h2>
  <li>Our Caption recommender algorithm can be improved to learn the instagram knowledge.</li>
  <li>The logs that are created from all the software componenets are stored in the MongoDb can be displayed on the Dashboard.</li>
  <li>This logs data can also be visually displayed in the Dashboard using Kibana post analysis.</li>


<br><br><hr>  
  
<b> NOTE: </b>
<li> The original scope of this project was to only recommend tags for an Instagram post. However, we have extended it to also suggest captions. </li>
<li> Using this tool, you can find Instagram hashtags to go viral and boost followers count. Don't use these hashtags without niche hashtags, otherwise, your post may be overlooked among the spam. Adding 3-4 of these hashtags to the rest of the niche hashtags is vital to attract only organic and interested followers. </li>
