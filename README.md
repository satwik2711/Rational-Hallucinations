# Natural Language to Prolog Converter w/ Simpsons Knowledge Base

## Description
This project is a natural language to Prolog converter that uses a knowledge base of Simpsons characters and their relationships. The converter takes in a natural language query and converts it to Prolog code that can be run on the knowledge base to answer the query. The knowledge base is a list of facts and rules about the Simpsons characters and their relationships. The converter uses an LLM to generate the Prolog code from the natural language query, as well as a LINC/MoE-style technique to generate multiple Prolog code outputs for the same query, which are then run on the knowledge base, and the most common answer is returned.

## Usage
1. Download the required packages by running the following command (virtual environment recommended):
```
pip install -r requirements.txt
```

2. Make sure your API keys are set in your .env file. You can use the .env.template file to know which keys are required.

3. Run the following command to start the program:
```python
python main.py
```