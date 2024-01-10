import json
import os
import traceback
from multiprocessing import Pool
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from Config import log_level

logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def prepare_data_source(folder_path):
    # Ensure the 'articles' folder exists and remove any existing files
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"An error occurred while removing existing files: {e}")
    else:
        os.makedirs(folder_path)


def get_links_to_articles(query, num_pages=1):
    # Set up Selenium with Chrome driver (you can use other drivers as well)
    # Set up Selenium with Chrome driver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    all_contents = {}
    try:
        # Open Financial Times search page and Get contents for top 3 pages
        for page_num in range(1, num_pages + 1):
            logger.info("Get contents for page {}. Wait 2 seconds for the page to load".format(page_num))
            address = f"https://www.ft.com/search?q={'+'.join(query.split())}&page={page_num}&sort=relevance"
            driver.get(address)
            # Wait for the page to load (you might need to adjust the wait time)
            time.sleep(2)
            # get the link to the articles
            link_xpath = '//li//div[contains(@class, "o-teaser__heading")]//a'
            links = driver.find_elements(By.XPATH, link_xpath)
            # Print the extracted links
            for link in links:
                href = link.get_attribute('href')
                all_contents[href] = link.get_attribute('text')

        logger.info("Finished scraping {} contents".format(len(list(all_contents.keys()))))
    except Exception as e:
        logger.error(f"An error occurred when getting the links of all articles in top 3 pages: {e}")

    finally:
        # Close the browser window
        driver.quit()
    return all_contents


def get_article_contents(args):
    all_content_part, process_name, folder_path, log_level = args
    # Configure logging for each process
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    logger.info("{} is loading {} links...".format(process_name, len(all_content_part)))
    link_counter = 1

    for content in all_content_part:
        title = sanitize_filename(all_content_part[content])
        href = content
        logger.info("{} Get contents for content {}: {}, {}".format(process_name, link_counter, title, href))
        try:
            driver.get(href)
            time.sleep(1)
            # Find the paywall script tag
            paywall_text = '//script[contains(text(),"window.Zephr.outcomes[\'paywall\']")]'
            paywall_script = driver.find_elements(By.XPATH, paywall_text)
            # Check if the paywall script is present
            article_text = ""

            if paywall_script:
                logger.info("Paywall detected, Use archive to scrape content {}".format(href))
                driver.get(f'https://archive.is/{href}')
                time.sleep(2)
                # Find all div elements with class TEXT-BLOCK
                text_blocks = driver.find_elements(By.CLASS_NAME, "TEXT-BLOCK")
                logger.info("found text_blocks = {}".format(text_blocks))
                for text_block in text_blocks:
                    # Find the first anchor element within each TEXT-BLOCK
                    anchor = text_block.find_element(By.TAG_NAME, 'a')
                    # Extract the href attribute
                    # Open the linked page and load its contents
                    driver.get(anchor.get_attribute('href'))
                    # Find all text within the inner <article> tag
                    # XPATH = '//article//div[@data-trackable="article-body" or @data-component="article-body"]'
                    XPATH = '//article//*//article'
                    article_elements = driver.find_elements(By.XPATH, XPATH)

                    for article_element in article_elements:
                        article_text += article_element.text
                        article_text += "\n"
            else:
                # Find all text within the inner <article> tag
                # XPATH = '//article//div[@class="article__content" or @data-trackable="article-body" or @data-component="article-body"]'
                XPATH = '//article//*//article'
                article_elements = driver.find_elements(By.XPATH, XPATH)
                for article_element in article_elements:
                    article_text += article_element.text
                    article_text += "\n"

            # Sanitize the output_file_name to remove invalid characters
            output_file_path = os.path.join(folder_path, f'{process_name}_{content.split("/")[-1]}_{title}.txt')
            # Save content to a text file within the 'articles' folder
            with open(output_file_path, 'w', encoding="utf-8") as file:
                file.write(article_text)
            link_counter += 1
        except Exception as e:
            logger.info(f"An error occurred when getting content: {e}")
            traceback.print_exc()
    else:
        driver.quit()


def search_financial_times(query, articles_saving_dir, read_local_mock_articles, mock_articles_dir, use_mul_process,
                           num_processes, num_pages, log_level):
    # create or clean the previous collected articles
    prepare_data_source(articles_saving_dir)

    # Specify the file path
    if read_local_mock_articles:
        # Read JSON data from the file
        with open(mock_articles_dir, 'r') as file:
            all_contents = json.load(file)
    else:
        all_contents = get_links_to_articles(query, num_pages)

    if use_mul_process:
        # Number of processes to create (adjust as needed)
        num_processes = num_processes
        total_contents = len(all_contents)
        # Check if the length of original_json is less than num_processes
        if total_contents < num_processes:
            num_processes = total_contents

        # Split the original JSON into chunks for parallel processing
        json_chunks = [dict(list(all_contents.items())[i:i + total_contents // num_processes]) for i in
                       range(0, total_contents, total_contents // num_processes)]

        # Create a multiprocessing pool
        with Pool(processes=num_processes) as pool:
            # Map each JSON chunk to the get_article_contents function
            pool.map(get_article_contents,
                     [(chunk, f"Process_{i + 1}", articles_saving_dir, log_level) for i, chunk in enumerate(json_chunks)])
    else:
        get_article_contents([all_contents, "Process 1", articles_saving_dir, log_level])


def main():
    import Config as Conf
    import os
    from LLM_RAG_query import synthesize_docs
    # Example usage
    user_query = "What is the equities market outlook for 2024?"
    # search_financial_times(user_query,
    #                        articles_saving_dir=Conf.articles_dir,
    #                        read_local_mock_articles=Conf.read_local_mock_articles,
    #                        use_mul_process=Conf.use_mul_process,
    #                        num_processes=Conf.num_processes,
    #                        mock_articles_dir=Conf.mock_data_file_path,
    #                        num_pages=Conf.num_pages,
    #                        log_level=Conf.log_level)

    os.environ["OPENAI_API_KEY"] = Conf.OPENAI_API_KEY
    logger.info(" USING LLM TO SYNTHESIZE DOCS AND GENERATE RESPONSE")
    response = synthesize_docs(articles_dir=Conf.articles_dir, user_query=user_query)
    print(response)

if __name__ == "__main__":
    main()
