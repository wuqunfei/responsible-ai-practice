import os
import openai
from dotenv import load_dotenv
import json
from collections import defaultdict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

class AzureOpenAIPIIDetector:
    def __init__(self):
        """
        Initializes the Azure OpenAI PII Detector.
        """
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://cog-adt-0002-dev-ext002-oai.openai.azure.com/")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
        self.api_version = "2024-05-01-preview"

        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        self.client = openai.AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            azure_ad_token_provider=token_provider,
        )
        self.pii_types = [
            "firstname", "middlename", "lastname", "sex", "dob", "age", "gender",
            "height", "eyecolor", "email", "phonenumber", "url", "username",
            "useragent", "street", "city", "state", "county", "zipcode", "country",
            "secondaryaddress", "buildingnumber", "ordinaldirection",
            "nearbygpscoordinate", "companyname", "jobtitle", "jobarea", "jobtype",
            "accountname", "accountnumber", "creditcardnumber", "creditcardcvv",
            "creditcardissuer", "iban", "bic", "currency", "currencyname",
            "currencysymbol", "currencycode", "amount", "pin", "ssn", "imei", "mac",
            "vehiclevin", "vehiclevrm", "bitcoinaddress", "litecoinaddress",
            "ethereumaddress", "ip", "ipv4", "ipv6", "maskednumber", "password",
            "time", "prefix"
        ]

    def _call_openai(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.azure_deployment,
                messages=[
                    {"role": "system", "content": "You are an expert in identifying and extracting Personally Identifiable Information (PII) from text. Your response must be only the JSON content, without any markdown formatting or other text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            return None

    def detect(self, text: str, language: str = "en"):
        prompt = f'''
        Analyze the following text and identify any Personally Identifiable Information (PII).
        The PII types to detect are: {', '.join(self.pii_types)}.

        Return the results as a JSON object with a single key "pii_results".
        The value of "pii_results" should be a list of JSON objects, where each object represents a detected PII entity and has the following keys:
        - "type": The PII entity type (e.g., "PERSON", "EMAIL").
        - "text": The detected PII text.
        - "score": A confidence score between 0.0 and 1.0. Since you are a deterministic model for this task, please use a score of 0.95 for all detections.

        Text to analyze:
        ---
        {text}
        ---
        '''
        response_content = self._call_openai(prompt)
        if not response_content:
            return []

        try:
            results = json.loads(response_content)
            return results.get("pii_results", [])
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON from OpenAI response.")
            return []

    def anonymize(self, text, **kwargs):
        detected_pii = self.detect(text, **kwargs)

        anonymized_text = text
        sorted_pii = sorted(detected_pii, key=lambda x: len(x['text']), reverse=True)

        for pii in sorted_pii:
            anonymized_text = anonymized_text.replace(pii['text'], f"<{pii['type']}>")

        return anonymized_text, detected_pii

    def get_summary(self, results):
        summary = defaultdict(int)
        for item in results:
            summary[item['type']] += 1
        return summary

    def get_detailed_results(self, results):
        return results