import tensorflow as tf
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
from flask import Flask, jsonify, request
from flask_cors import CORS
from joblib import load

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import spacy

presence_classifier = load('presence_classifier.joblib')
presence_vect = load('presence_vectorizer.joblib')
category_classifier = load('category_classifier.joblib')
category_vect = load('category_vectorizer.joblib')


app = Flask(__name__)
CORS(app)

model_name = 'distilbert-base-uncased'  # or bert-base-cased
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = TFAutoModelForSequenceClassification.from_pretrained(
    r"content/transformer_model")

ecommerce_url = ""


@app.route('/', methods=['POST'])
def main():
    if request.method == 'POST':
        output = []
        data = request.get_json().get('tokens')

        for token in data:
            result = presence_classifier.predict(
                presence_vect.transform([token]))
            if result == 'Dark':
                cat = category_classifier.predict(
                    category_vect.transform([token]))
                output.append(cat[0])
            else:
                output.append(result[0])

        dark = [data[i] for i in range(len(output)) if output[i] == 'Dark']
        for d in dark:
            print(d)
        print()
        print(len(dark))

        message = '{ \'result\': ' + str(output) + ' }'
        print(message)

        json = jsonify(message)

        return json


@app.route('/analyze', methods=['POST'])
def analyze():
    global ecommerce_url

    data = request.json
    ecommerce_url = data.get('ecommerce_url')
    print("ecommerce_url:", ecommerce_url)

    nlp = spacy.load("en_core_web_md")
    fetched_text_cleaned = ""

    def find_privacy_policy_link(driver, keywords):
        for link in driver.find_elements(By.TAG_NAME, 'a'):
            for keyword in keywords:
                if keyword.lower() in link.text.lower():
                    return link.get_attribute('href')
        return None

    def fetch_privacy_policy_text(driver, privacy_policy_url):
        driver.get(privacy_policy_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text_content = soup.get_text()
        return text_content

    def clean_text(text):
        return re.sub(r'\s+', ' ', text).strip()

    def read_text_file(file_path):
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            return file.read()

    def analyze_text(document_rules, fetched_text_cleaned):
        doc_rules = nlp(document_rules)
        doc_fetched_text = nlp(fetched_text_cleaned)

        similarities = doc_rules.similarity(doc_fetched_text)

        fetched_entities = [ent.text for ent in doc_fetched_text.ents]

        rules_entities = [ent.text for ent in doc_rules.ents]

        positive_points = []
        negative_points = []

        for sentence in doc_fetched_text.sents:
            if any(keyword in sentence.text.lower() for keyword in ['security', 'protect', 'safeguard']):
                positive_points.append(sentence.text)
            if any(keyword in sentence.text.lower() for keyword in ['disclose', 'share', 'sell']):
                negative_points.append(sentence.text)

        return similarities, fetched_entities, rules_entities, positive_points, negative_points

    try:
        file_path = r'E-Rules.txt'
        document_rules = read_text_file(file_path)

        keywords = ['Privacy Notice', 'Privacy',
                    'Privacy Policy', 'We Respect Your Privacy']

        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()))

        driver.get(ecommerce_url)
        main_page_url = driver.current_url

        privacy_policy_url = find_privacy_policy_link(driver, keywords)

        if privacy_policy_url:
            privacy_policy_url = urljoin(main_page_url, privacy_policy_url)
            privacy_policy_text = fetch_privacy_policy_text(
                driver, privacy_policy_url)

            document_rules_cleaned = clean_text(document_rules)
            fetched_text_cleaned = clean_text(privacy_policy_text)

            similarities, fetched_entities, rules_entities, positive_points, negative_points = analyze_text(
                document_rules_cleaned, fetched_text_cleaned
            )

            # Print results
            print("Similarity between document rules and fetched text:", similarities)
            print("\nEntities extracted from fetched text:", fetched_entities)
            print("\nEntities extracted from document rules:", rules_entities)
            print("\nPositive Points based on document rules:", positive_points)
            print("\nNegative Points based on document rules:", negative_points)

        else:
            print("Privacy policy link not found on the main page.")

    finally:
        if 'driver' in locals():
            driver.quit()

    print(fetched_text_cleaned)

    nlp = spacy.load("en_core_web_sm")

    document_rules = ["Every e-commerce entity shall provide the following information in a clear and accessible manner on its platform, displayed prominently to its users",
                      "namely:-- legal name of the e-commerce entity; principal geographic address of its headquarters and all branches;  name and details of its website; and contact details like e-mail address, fax, landline and mobile numbers of customer care as well as of grievance officer.",
                      "E-Commerce Entity shall display terms of contract between e-Commerce entity and the seller relating to return, refund, exchange, warranty / guarantee, delivery / shipment, mode of payments, grievance redressal mechanism etc. to enable consumers to make informed decisions.",
                      "E-Commerce Entity shall if the ecommerce entity is informed by the consumer or comes to know by itself or through another source about any counterfeit product being sold on its platform, and is satisfied after due diligence, it shall notify the seller and if the seller is unable to provide any evidence that the product is genuine, it shall take down the said listing and notify the consumers of the same.",
                      "E-Commerce Entity shall be held guilty of contributory or secondary liability if it makes an assurance vouching for the authenticity of the goods sold on its market place – or if it guarantees that goods are authentic.",
                      "No e-commerce entity shall discriminate between consumers of the same class or make any arbitrary classification of consumers affecting their rights under the Act.",
                      "E-Commerce Entity shall provide  information on available payment methods, the security of those payment methods, any fees or charges payable by users, the procedure to cancel regular payments under those methods, charge-back options, if any, and the contact information of the relevant payment service provider;",
                      "Every marketplace e-commerce entity shall include in its terms and conditions generally governing its relationship with sellers on its platform, a description of any differentiated treatment which it gives or might give between goods or services or sellers of the same category.",

                      "Every marketplace e-commerce entity shall require sellers through an undertaking to ensure that descriptions, images, and other content pertaining to goods or services on their platform is accurate and corresponds directly with the appearance, nature, quality, purpose and other general features of such good or service",
                      "Details about the sellers supplying the goods and services, including identity of their business, legal name, principal geographic address, name of website, e-mail address, contact details, including clarification of their business identity, the products they sell, and how they can be contacted by customers shall be displayed in the web site.",
                      "E-Commerce Entity shall provide information relating to return, refund, exchange, warranty and guarantee, delivery and shipment, modes of payment, and grievance redressal mechanism, and any other similar information which may be required by consumers to make informed decisions;",
                      "E-Commerce Entity shall provide an explanation of the main parameters which, individually or collectively, are most significant in determining the ranking of goods or sellers on its platform and the relative importance of those main parameters through an easily and publicly available description drafted in plain and intelligible language.",
                      "No e-commerce entity shall manipulate the price of the goods or services offered on its platform in such a manner as to gain unreasonable profit by imposing on consumers any unjustified price having regard to the prevailing market conditions, the essential nature of the good or service, any extraordinary circumstances under which the good or service is offered, and any other relevant consideration in determining whether the price charged is justified",
                      "E-Commerce Entity shall ensure that the advertisements for marketing of goods or services are consistent with the actual characteristics, access and usage conditions of such of goods or services .",
                      "E-Commerce Entity shall mention safety and health care information of the goods and service advertised for sale;",
                      "entity should not  adopt any trade practice which for the purpose of promoting the sale, use or supply of any goods or for the provision of any service, or composite supply, adopts any unfair methods or unfair or deceptive practice that may influence transactional decisions of consumers in relation to products and services;",
                      "entity should not  falsely represent themselves as consumers or post reviews about goods and services in their name; or misrepresent or exaggerate the quality or the features of goods and services.",
                      "E-Commerce Entity shall provide total price in single figure of any good or service along with the breakup price for the good or service, showing all the compulsory and voluntary charges, such as delivery charges, postage and handling charges, conveyance charges and the applicable tax;",

                      "Every e-commerce entity shall effect all payments towards accepted refund requests of the consumers as prescribed by the Reserve Bank of India or any other competent authority under any law for the time being in force, within a reasonable period of time, or as prescribed under applicable laws.",
                      "E-Commerce Entity shall Accept return of goods if delivered late from the stated delivery schedule or delivery of defective, wrong or spurious products, and/or not of the characteristics/features as advertised. Provided that in the case of late delivery, this sub rule shall not apply if such late delivery was due to force majeure. (5) Any inventory e-c",
                      "E-Commerce Entity shall Effect all payments towards accepted refund requests of the customers within a period of maximum of 14 days.",
                      "No e-commerce entity shall impose cancellation charges on consumers cancelling after confirming purchase unless similar charges are also borne by the e- commerce entity, if they cancel the purchase order unilaterally for any reason.",

                      "Every e-commerce entity shall only record the consent of a consumer for the purchase of any good or service offered on its platform where such consent is expressed through an explicit and affirmative action, and no such entity shall record such consent automatically, including in the form of pre-ticked checkboxes.",
                      "E-Commerce Entity shall Ensure that personally identifiable information of customers are protected, and that such data collection and storage and use comply with provisions of the Information Technology (Amendment) Act, 2008.",
                      "E-Commerce Entity shall Provide consumers with transparent and effective consumer protection that is not less than the level of protection offered in other forms of commerce;",
                      "a ticket number for each complaint lodged through which the consumer can track the status of the complaint;",

                      "E-Commerce Entity shall Publish on its website the name of the Grievance Officer and his contact details as well as mechanism by which users can notify their complaints about products and services availed through their web site.",
                      "E-Commerce Entity shall The Grievance Officer shall redress the complaints within one month from the date of receipt of complaint",
                      "E-Commerce Entity shall provide facility to consumers to register their complaints over phone, email or website and shall provide complaint number for tracking the complaint;",
                      "E-Commerce Entity shall Provide mechanism/system to converge with NCH in grievance redress process"]

    rules = document_rules

    sentence = fetched_text_cleaned

    def calculate_rule_similarity(rules, sentence):
        doc = nlp(sentence)

        tokens = [token.text.lower() for token in doc]

        rule_similarities = {rule: sum(1 for word in rule.lower().split(
        ) if word in tokens) / len(rule.split()) for rule in rules}

        sorted_rules = sorted(rule_similarities.items(),
                              key=lambda x: x[1], reverse=True)

        followed_rules = [rule[0] for rule in sorted_rules if rule[1] > 0.5]
        not_followed_rules = [rule[0]
                              for rule in sorted_rules if rule[1] <= 0.5]

        adherence_percentage = len(followed_rules) / len(rules) * 100

        return adherence_percentage, followed_rules, not_followed_rules

    adherence_percentage, followed_rules, not_followed_rules = calculate_rule_similarity(
        rules, sentence)

    print(f"\n The sentence follows {adherence_percentage:.2f}% of the rules.")
    print(f"\n Followed Rules: {followed_rules}")
    print(f"\n Not Followed Rules: {not_followed_rules}")

    response = {
        'adherencePercentage': adherence_percentage,
        'fetchedData': fetched_text_cleaned,
        'followedRules': followed_rules,
        'notFollowedRules': not_followed_rules
    }

    return jsonify(response)


@app.route('/review', methods=['POST'])
def review():
    data = request.json
    text = data.get('review')

    res_dict = {0: 'real', 1: 'fake'}
    y = tokenizer(text, padding="max_length", truncation=True)
    y['input_ids'] = tf.convert_to_tensor([y['input_ids']])
    if model_name == 'bert-base-cased':
        y['token_type_ids'] = tf.convert_to_tensor([y['token_type_ids']])
    y['attention_mask'] = tf.convert_to_tensor([y['attention_mask']])

    label = model(y)
    probs = tf.nn.softmax(label.logits)
    result = res_dict[tf.argmax(probs)[0].numpy()]

    return result


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
