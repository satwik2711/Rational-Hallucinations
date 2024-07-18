import logging
import os
from pyswip import Prolog
import re
from scripts.models import gemini, gpt
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Create the prolog interface
prolog = Prolog()

# Choose model
llm = gpt

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_unique_rules(prolog_kb):
    # Define a regex pattern for capturing rules and facts
    pattern = r"([a-z]+\([^)]*\)\s*:-?\s*[^.\n]*)\."

    # Find all matches for the pattern
    matches = re.findall(pattern, prolog_kb, re.MULTILINE)

    # Use a set to keep track of unique predicates
    unique_predicates = set()

    # Dictionary to store unique rules with their representative
    unique_rules = {}

    for match in matches:
        # Extract the predicate name which is the first word before '('
        predicate = match.split('(')[0].strip()
        
        if predicate not in unique_predicates:
            unique_predicates.add(predicate)
            unique_rules[predicate] = match + "."

    return list(unique_rules.values())

def translate_natural_language_to_prolog(natural_language_query, n=1):
    try:
        # Logging the translation request
        logging.info(f"Requesting translation for: {natural_language_query}")

        rule_string = "\n".join(unique_rules)
        
        system_prompt = f'''Translate natural language queries into Prolog. ONLY RETURN PROLOG CODE, NOTHING ELSE. If it's a query, use '?-'; if it needs a rule (ONLY CONSTRUCT RULES THAT USE EXISTING RULES OR FACTS), use ':-'. Use these rules: {rule_string}'''
        
        user_prompt = "Translate the following natural language query into Prolog: " + natural_language_query
        
        # Generate the response
        completion = llm.generate_response(system_prompt, user_prompt, n=n)

        # Extract the Prolog translations from the completion
        translations = []
        for prolog_translation in completion:
            logging.info(f"Candidate translation: {prolog_translation}")

            if "```prolog" in prolog_translation and "```" in prolog_translation:
                prolog_translation = prolog_translation.split("```prolog")[1].split("```")[0].strip() # Extract the Prolog code
            else:
                # get anything starting with ?- or :- and ending with a period
                logging.info(f"Used regex to extract Prolog code.")
                prolog_translation = re.findall(r"(\?-.*\.)", prolog_translation, re.MULTILINE)

                if len(prolog_translation) > 0:
                    prolog_translation = prolog_translation[0]
                else:
                    prolog_translation = None

            logging.info(f"Processed translation: {prolog_translation}")
            translations.append(prolog_translation)

        return translations
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
    
def run_prolog(prolog_command):
    if not prolog_command:
        logging.error("No Prolog command provided.")
        return None
    
    logging.info("Running the Prolog query...")

    if ":-" in prolog_command:
        sections = prolog_command.split("?-")
        rule = sections[0].strip(":-").strip()

        if len(sections) > 1:
            command = sections[1].strip()
        else:
            command = None

        if rule not in unique_rules:
            logging.info(f"Adding rule to the knowledge base: {rule}")

            # add rule to file
            with open("kb.pl", "a") as file:
                file.write("\n" + rule + "\n")

            unique_rules.append(rule)

            # reload the knowledge base
            prolog.consult("kb.pl")

        if command:
            logging.info(f"Executing the Prolog query: {command}")
            query = prolog.query(command)
        else:
            logging.error("No query provided.")
            return [{}]

    elif "?-" in prolog_command:
        command = prolog_command.replace("?-", "").strip()

        logging.info(f"Executing the Prolog query: {command}")
        query = prolog.query(command)

    else:
        logging.error("Invalid Prolog query.")
        return None

    try:
        results = list(query)  # Convert the result to a list to make it Python-friendly
        query.close()  # Close the query to free resources
        logging.info("Prolog query executed successfully.")
        return results
    except Exception as e:
        logging.error(f"An error occurred during Prolog execution: {e}")
        return None
    
def run_candidate_prolog_queries(candidate_prolog_queries):
    try:
        results = []
        for i, query in enumerate(candidate_prolog_queries):
            result = run_prolog(query)

            answers = []
            
            if result is not None:
                # process result
                if len(result) == 0:
                    result = "False."
                    answers = [result]
                else:
                    if {} in result:
                        result = "True."
                        answers = [result]
                    else:
                        answers = [str(list(res.values())[0]) for res in result]
                        result = "\n".join(set(answers))

            logging.info(f"Result for query {i} | '{query}' - {answers}")
            results.append(result)
        
        # get counts of results
        counts = {result: results.count(result) for result in results}

        logging.info(f"Counts of results: {counts}")

        # return most common result
        return max(counts, key=counts.get)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
    
if __name__ == "__main__":
    # Load the knowledge base
    with open("kb.pl", "r") as file:
        prolog_kb = file.read()     
    
    # Extract unique rules from the knowledge base
    unique_rules = extract_unique_rules(prolog_kb)
    print("\nUnique rules extracted from the knowledge base:\n")
    for rule in unique_rules:
        print(rule)
    print()

    # Set the working directory and load the knowledge base
    prolog.query("working_directory(_, 'C:/Users/denni/Desktop/LLM Logic').")
    prolog.consult("kb.pl")  # Load your knowledge base

    try:
        while True:
            # Get the user query``
            query = input("Enter a natural language query to translate into Prolog: ")
            print()
            translations = translate_natural_language_to_prolog(query, n=5)
            
            if translations and len(translations) > 0:
                print("\nProlog translations:\n")
                for i, translation in enumerate(translations):
                    print(f"Translation {i+1}: {translation}")
                print()

                # Run the Prolog queries
                result = run_candidate_prolog_queries(translations)

                if result is not None:
                    print("\nResult:\n")
                    print(result.title())
                else:
                    print("\nQuery returned no result.")

            else:
                print("\nFailed to translate the query into Prolog.")

            print("\n-----------------------------------\n")
    
    except KeyboardInterrupt:
        # Restore the knowledge base
        with open("kb.pl", "w") as file:
            file.write(prolog_kb)

        print("\nProgram terminated by the user.")