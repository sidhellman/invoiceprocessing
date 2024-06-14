import os
import tempfile
import json
import streamlit as st
from marker.convert import convert_single_pdf
from marker.models import load_all_models
from ollama import Client
import yaml

# Set Streamlit page config
st.set_page_config(page_title="Invoice Processing", layout="wide")

# Set up environment variables
os.environ["IN_STREAMLIT"] = "true"
os.environ["PDFTEXT_CPU_WORKERS"] = "1"

# Load configuration from YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Load all models
@st.cache_resource
def load_models():
    return load_all_models()

model_lst = load_models()

# Create a custom Ollama client with the specified host and model from the configuration
ollama_client = Client(host=config['ollama']['host'])
ollama_model = config['ollama']['model']

# Define the Streamlit app
def main():
    st.title("Invoice Processing")

    # File upload
    uploaded_file = st.file_uploader("Choose an invoice PDF file", type="pdf")

    if uploaded_file is not None:
        # Save uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            filepath = temp_file.name

        # Process the PDF
        with st.spinner("Processing invoice..."):
            try:
                full_text, images, out_metadata = convert_single_pdf(filepath, model_lst)
                if len(full_text.strip()) > 0:
                    st.success("Invoice processed successfully!")

                    # Convert markdown to JSON
                    invoice_data = {
                        "invoice_details": full_text,
                        "metadata": out_metadata
                    }
                    invoice_json = json.dumps(invoice_data)

                    # Generate formatted table, summary, and financial analysis using Ollama
                    message = f'''
                    Here is the JSON representation of an invoice:

                    {invoice_json}

                    Please do the following:
                    1. Generate an extremely well-formatted table with all the specifics from the invoice, including the invoice number, due date, items, quantities, prices, and total amount due.
                    2. Include the following information:
                       - If the invoice is pending to be paid, state "Status: Pending"
                       - Include the extracted email address separately before the table
                       - Include the extracted physical address separately before the table
                       - If the invoice amount is greater than 5000, state "Requires Approval"
                       - If the invoice amount is less than or equal to 5000, state "Submitted for Pass-Through Settlement"
                    3. Provide a detailed summary of what the invoice is about, for whom it is, and whether it requires further inquiry and processing based on the services or goods mentioned.
                    4. Perform a financial analysis of the invoice, including:
                       - Determine if the invoice is eligible for factoring based on the due date and total amount
                       - Estimate the risk associated with the invoice based on the customer's payment history and credit score (if available)
                       - Provide recommendations for optimizing cash flow and minimizing risk in processing the invoice
                       - Identify any potential discrepancies or red flags in the invoice that may require further investigation

                    Generate the financial analysis separately from the table and summary.
                    Do not include any other text or explanation, just the requested information.
                    '''

                    stream = ollama_client.chat(
                        model=ollama_model,
                        messages=[{'role': 'user', 'content': message}],
                        stream=True,
                    )

                    # Display the generated table, summary, and financial analysis in real-time
                    output_container = st.empty()
                    generated_output = ""
                    for chunk in stream:
                        chunk_content = chunk['message']['content']
                        generated_output += chunk_content
                        output_container.markdown(generated_output)

                else:
                    st.error("Empty file. Could not process.")
            except Exception as e:
                st.error(f"Error processing invoice: {e}")
            finally:
                # Remove the temporary PDF file
                os.unlink(filepath)

if __name__ == "__main__":
    main()
