import transformers
import shap
import requests
from huggingface_hub import configure_http_backend
import certifi

def backend_factory() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session

configure_http_backend(backend_factory=backend_factory)


model = transformers.pipeline(task="sentiment-analysis", return_all_scores=True)
explainer = shap.Explainer(model)
shap_values = explainer(["What a great movie! ... if you have no taste"])
print(shap_values)
shap.plots.text(shap_values[0, :, "POSITIVE"])
