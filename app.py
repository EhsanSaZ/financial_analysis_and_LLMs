import os
from flask import Flask, render_template, request, jsonify
from selenium_scrape import search_financial_times
from LLM_RAG_query import synthesize_docs
import Config as Conf


app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = Conf.OPENAI_API_KEY


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['user_question']
    # Example usage
    # user_query = "What is the equities market outlook for 2024?"
    search_financial_times(query=user_question,
                           articles_saving_dir=Conf.articles_dir,
                           read_local_mock_articles=Conf.read_local_mock_articles,
                           use_mul_process=Conf.use_mul_process,
                           num_processes=Conf.num_processes,
                           mock_articles_dir=Conf.mock_data_file_path,
                           num_pages=Conf.num_pages,
                           log_level=Conf.log_level)
    #
    response = synthesize_docs(articles_dir=Conf.articles_dir, user_query=user_question)

    # Add your logic to process the user's question and generate a response here
    # For simplicity, let's just echo the user's question for now
    bot_response = f"{response}"
    return jsonify({'bot_response': bot_response})


if __name__ == '__main__':
    app.run(debug=True)
