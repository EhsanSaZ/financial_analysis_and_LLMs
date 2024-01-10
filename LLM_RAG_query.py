# import os
#
# os.environ["OPENAI_API_KEY"] = "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"

from llama_index import VectorStoreIndex, SimpleDirectoryReader


def synthesize_docs(articles_dir, user_query):
    documents = SimpleDirectoryReader(articles_dir).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(response_mode='tree_summarize')
    response = query_engine.query(user_query)
    return response

if __name__ == "__main__":
    import Config as Conf

    response = synthesize_docs(articles_dir=Conf.articles_dir, user_query=user_query)
    print(response)


