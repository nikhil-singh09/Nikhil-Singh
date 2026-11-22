# Invoice Intelligence — Configurable Document Demo

A local-first document workflow with optional website sources, PyTesseract OCR and selectable language-model providers.

> This is a portfolio starter, not a production deployment or a claim of a deployed RAG system. The default is offline lexical retrieval. It uses fictional inputs and does not connect to employer systems.

![Workflow diagram](docs/workflow.svg)

## Demo input

The folder contains fictional text invoices and a vector sample invoice image. From this project directory:

~~~bash
python src/assistant.py --query "payment terms" --input data
python src/assistant.py --query "invoice total" --input data --ocr
~~~

The first command searches text. The second also runs OCR on the sample SVG image. Outputs are saved under outputs/.

## Choose a provider

Set the provider in the command or in your environment:

| Provider | Selection | Requirements |
| --- | --- | --- |
| Offline | --provider offline | No model service; returns ranked source excerpts |
| Local open-source model | --provider ollama | Ollama running locally; set OLLAMA_MODEL |
| Azure OpenAI | --provider azure-openai | Azure endpoint and deployment; configure authentication below |

Example with a local model:

~~~bash
ollama pull qwen2.5:7b
python src/assistant.py --query "payment terms" --input data --provider ollama
~~~

Example with Azure OpenAI:

~~~bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
export AZURE_OPENAI_API_KEY="set-this-in-your-shell-or-secret-store"
python src/assistant.py --query "invoice total" --input data --provider azure-openai
~~~

For Azure environments, the code can use Microsoft Entra ID instead of an API key by setting AZURE_OPENAI_USE_ENTRA=true and configuring DefaultAzureCredential. Prefer managed identity or a secret manager for deployment. Never commit a populated .env file or API key.

## Use a website source

The loader fetches only URLs you pass explicitly. Set an exact domain allowlist first:

~~~bash
export ALLOWED_WEB_HOSTS="learn.microsoft.com"
python src/assistant.py --query "Azure OpenAI Python" --input data --url "https://learn.microsoft.com/en-us/azure/foundry/openai/supported-languages"
~~~

Only HTTPS pages on the allowlist are accepted. The loader checks resolved addresses, limits redirects, response size and request time, and skips non-text content. Do not use it to bypass logins, paywalls, robots rules or site terms. Source text is sent to the selected LLM provider when you choose Ollama or Azure OpenAI.

## OCR example

~~~bash
python src/ocr_demo.py --input data/sample_invoice.svg --output demo-output/ocr.txt
~~~

Install the Python dependencies with pip install -r requirements.txt. The Tesseract engine must also be installed on the computer and available on PATH. The Python package is a wrapper, so installing pytesseract alone is not enough. See the [PyTesseract usage guide](https://github.com/madmaze/pytesseract#usage) and [Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation).

## Configuration

Copy .env.example to .env if you use a dotenv-aware shell, or export the variables directly. The application reads process environment variables and never reads secrets from the example file. A populated .env is excluded by .gitignore.

Azure's current Python examples use the OpenAI SDK with the Azure OpenAI v1 endpoint; this project uses the deployment name as the model value. See [Microsoft's Azure OpenAI Python examples](https://learn.microsoft.com/en-us/azure/foundry/openai/supported-languages?tabs=secure%2Cpython-secure) and the [Ollama chat API](https://docs.ollama.com/api/chat).

## Production checklist

Before using real documents, add identity and document-level authorization, private storage, retention rules, monitoring, structured audit logs, provider quotas, retries, evaluation, human review and deployment-specific network controls. The public-website loader is deliberately allowlist-based; it is not a general-purpose crawler. Confirm privacy and data-handling requirements before sending documents to any model provider.

## Bundled demo output

A sample run using the included fictional inputs is saved in `demo-output/`: answer.json, retrieval_results.json. Run commands from this project folder to regenerate the artifacts.
