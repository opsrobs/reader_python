import PyPDF2
import mysql.connector
from mysql.connector import Error
import re
from datetime import datetime

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'database': 'ctfl_api',
    'user': 'root',
    'password': 'root',
    'port': 3306,
    'auth_plugin': 'caching_sha2_password',
    'connect_timeout': 5
}

def format_table_text(text):
    """Replace two or more spaces with pipes to format tables"""
    # Replace sequences of 2+ spaces with a pipe, but preserve single spaces
    return re.sub(r' {2,}', ' | ', text.strip())

def extract_complete_questions(pdf_path):
    questions = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        # Concatenate all text first for multi-page questions
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Improved regex pattern to capture from (1 ponto) to ?
        pattern = r'(Questão [A-Z]?\d+ \(1 ponto\)[\s\S]*?\?)([\s\S]*?)(?=(Questão [A-Z]?\d+ \(1 ponto\)|\Z))'
        matches = re.findall(pattern, full_text)
        
        for match in matches:
            question_text = match[0]
            has_complement = match[1].split('\nA)')[0]
            question_text = question_text + has_complement
            # question_text = re.split(r'\nA\)', question_text)[0]
            options_text = match[1].strip()
            
            # Format tables in question text

            question_text = format_table_text(question_text)
            
            # Extract options with their complete text
            options = {}
            current_option = None
            
            for line in options_text.split('\n'):
                option_match = re.match(r'^([A-D])\)(.*)', line)
                if option_match:
                    current_option = option_match.group(1)
                    options[current_option] = format_table_text(option_match.group(2))
                elif current_option:
                    # Format tables in option text as well
                    options[current_option] += " " + format_table_text(line)
            
            questions.append({
                'question': question_text,
                'options': options
            })
    
    return questions

def store_questions_in_db(questions):
    """Store extracted questions in MySQL database
    
    Args:
        questions (list): List of question dictionaries to store
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Create tables if not exists with proper structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Questionnaires (
                IdQuestionnaire INT AUTO_INCREMENT PRIMARY KEY,
                TittleQuestionnaire VARCHAR(255),
                DescriptionQuestionnaire TEXT,
                CreatAt DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asksquestionnaires (
                IdAsks INT AUTO_INCREMENT PRIMARY KEY,
                Ask TEXT,
                optionA TEXT,
                optionB TEXT,
                optionC TEXT,
                optionD TEXT
            )
        """)
        
        # Insert questionnaire
        cursor.execute("""
            INSERT INTO Questionnaires (TittleQuestionnaire, DescriptionQuestionnaire, CreatAt)
            VALUES (%s, %s, %s)
        """, (
            "ISTQB Foundation Level Sample Exam - Set A",
            "Sample questions for ISTQB CTFL certification",
            datetime.now()
        ))
        
        # Insert questions with properly extracted options
        for q in questions:
            # Check if question contains table data (has pipes)
            cursor.execute("""
                INSERT INTO asksquestionnaires 
                (Ask, optionA, optionB, optionC, optionD)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                q['question'],
                q['options'].get('A', '').strip(),
                q['options'].get('B', '').strip(),
                q['options'].get('C', '').strip(),
                q['options'].get('D', '').strip()
            ))
        
        connection.commit()
        print(f"Successfully stored {len(questions)} questions with complete options.")
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """Main function to execute the extraction and storage process"""
    pdf_path = r"C:\Users\robso\Downloads\exam_sample_ctfl_A_1br.pdf"
    
    print("Extracting questions with complete options from PDF...")
    questions = extract_complete_questions(pdf_path)
    print(f"Found {len(questions)} questions.")
    
    # Debug print to verify extraction
    for i, q in enumerate(questions[:1]):  # Print first question for verification
        print(f"\nSample Question {i+1}:")
        print(q['question'])
        print("\nOptions:")
        for opt in ['A', 'B', 'C', 'D']:
            if opt in q['options']:
                print(f"{opt}) {q['options'][opt]}")
    
    print("\nStoring in database...")
    store_questions_in_db(questions)
    print("Process completed successfully.")

if __name__ == "__main__":
    main()