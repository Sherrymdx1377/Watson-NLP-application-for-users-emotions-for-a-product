from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/getsentiment', methods=['POST'])
def getsentiment():
    # get the URL from the form
    url = request.form['url']

    # Prepare the list needed
    names = []
    reviews = []
    rate = []
    data_string = ""
    
    # Get the whole web content of the product page
    response_pre = requests.get(url,headers={'User-Agent': 'My User Agent 1.0','From': 'personal@domain.com'})
    soup_pre = BeautifulSoup(response_pre.text, 'html.parser')
    scrapped_review_url = soup_pre.find("a",string="See all reviews").get('href')
    url_review_page = "https://www.amazon.ca"+ scrapped_review_url

    # Get the whole web content of the review page
    response = requests.get(url_review_page,headers={'User-Agent': 'My User Agent 1.0','From': 'personal@domain.com'})
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate every user's comment block
    soup1 = soup.find_all("div", {"id":"cm_cr-review_list"})
    for soup2 in soup1:

        # Locate every user's comment block
        soup3 = soup2.find_all("div", {"class":"a-section review aok-relative"})
        for soup4 in soup3:

            # Get every user's rate
            item=soup4.find("span", class_="a-icon-alt")
            data_string = data_string + item.get_text()
            rate.append(data_string)
            data_string = ""

            # Get every user's name
            item=soup4.find("span", class_="a-profile-name")
            data_string = data_string + item.get_text()
            names.append(data_string)
            data_string = ""  

            # Get every user's review which will be used for emotion analysis
            item = soup4.find("span", {"data-hook": "review-body"})
            data_string = data_string + item.get_text()
            data_string = data_string.replace('\n', '')
            data_string = data_string.replace('\t', '')
            reviews.append(data_string)
            data_string = ""	

    # Varible used to store emotion results and emotion scores
    results=[]
    anger = []
    disgust = []
    fear = []
    joy = []
    sadness = []

    # Getting the emotion scores for the scrapped reviews
    for content in reviews:
        url_nlp = "https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
        headers_nlp = {"Content-Type": "application/json", "Accept": "application/json", "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}
        data_nlp = {"rawDocument":{"text": content}, "languageCode": "en", "showNeutralScores": True, "documentSentiment": True}
        response = requests.post(url_nlp, headers=headers_nlp, json=data_nlp)
        test=json.loads(response.text)

        #scores list for every emotions
        anger_temp=test['emotionPredictions'][0]['emotion']['anger']
        disgust_temp=test['emotionPredictions'][0]['emotion']['disgust']
        fear_temp=test['emotionPredictions'][0]['emotion']['fear']
        joy_temp=test['emotionPredictions'][0]['emotion']['joy']
        sadness_temp=test['emotionPredictions'][0]['emotion']['sadness']
        sum_temp = test['emotionPredictions'][0]['emotion']['anger']+test['emotionPredictions'][0]['emotion']['disgust']+test['emotionPredictions'][0]['emotion']['fear']+test['emotionPredictions'][0]['emotion']['joy']+test['emotionPredictions'][0]['emotion']['sadness']

        #scores normalize
        anger.append(round(anger_temp/sum_temp,3))
        disgust.append(round(disgust_temp/sum_temp,3))
        fear.append(round(fear_temp/sum_temp,3))
        joy.append(round(joy_temp/sum_temp,3))
        sadness.append(round(sadness_temp/sum_temp,3))

        results.append('Joy: '+str(round(joy_temp/sum_temp,3))+' \tSadness: '+str(round(sadness_temp/sum_temp,3))+' \tAnger:'+str(round(anger_temp/sum_temp,3))+' \tDisgust:'+str(round(disgust_temp/sum_temp,3))+' \tFear:'+str(round(fear_temp/sum_temp,3)))

    # Sum score for each emotions
    anger_score = round(sum(anger)/len(reviews),3)
    disgust_score = round(sum(disgust)/len(reviews),3)
    fear_score = round(sum(fear)/len(reviews),3)
    joy_score = round(sum(joy)/len(reviews),3)
    sadness_score = round(sum(sadness)/len(reviews),3)
    score = [joy_score, sadness_score, anger_score, disgust_score, fear_score]
    #store the averaged score of each emotions
    results.append('Joy:'+str(joy_score)+' \tSadness:'+str(sadness_score)+' \tAnger:'+str(anger_score)+' \tDisgust:'+str(disgust_score)+' \tFear:'+str(fear_score))

    # Return template with data
    return render_template('getsentiment.html', url=url, reviews=reviews, results=results, score=score)

if __name__ == '__main__':
    app.run()


