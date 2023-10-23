from langchain.llms import CTransformers
from langchain.chains import QAGenerationChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
import os
import time
from PyPDF2 import PdfReader
import streamlit as st

def loadLLM():
    llm = CTransformers(
        model="mistral-7b-instruct-v0.1.Q3_K_S.gguf",
        model_type='mistral',
        max_new_tokens = 1048,
        temperature = 0.2
    )
    return llm


def processing(file_path):
    # Load data from PDF
    loader = PyPDFLoader(file_path)
    data = loader.load()

    question_gen = ''

    for page in data:
        question_gen += page.page_content

    splitter_ques_gen = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)

    document_ques_gen = [Document(page_content=t) for t in chunks_ques_gen]

    splitter_ans_gen = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )

    document_answer_gen = splitter_ans_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen


def pipeline(file_path):

    document_ques_gen, document_answer_gen = processing(file_path)



    llm_ques_gen_pipeline = loadLLM()


    refine_template = ("""
    You are an expert at creating practice questions based on coding material and documentation.
    Your goal is to help for a test.
    We have received some questions to a certain extent: {existing_answer}.
    We have the option to refine the existing questions or add new ones.
    (only if necessary) with some more context below.
    ------------
    {text}
    ------------

    Given the new context, refine the original questions in English.
    If the context is not helpful, please provide the original questions.
    QUESTIONS:
    """
    )

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
    )

    ques_gen_chain = load_summarize_chain(llm = llm_ques_gen_pipeline,
                                            chain_type = "refine",
                                            verbose = True,
                                            refine_prompt=REFINE_PROMPT_QUESTIONS)

    ques = ques_gen_chain.run(document_ques_gen)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    vector_store = FAISS.from_documents(document_answer_gen, embeddings)

    llm_answer_gen = loadLLM()

    ques_list = ques.split("\n")
    filtered_ques_list = [element for element in ques_list if element.endswith('?') or element.endswith('.')]

    answer_generation_chain = RetrievalQA.from_chain_type(llm=llm_answer_gen,
                                                chain_type="stuff",
                                                retriever=vector_store.as_retriever())

    return answer_generation_chain, filtered_ques_list

def getTxt(file_path):
    answer_generation_chain, ques_list = pipeline(file_path)
    base_folder = './static/output/'
    if not os.path.isdir(base_folder):
        os.mkdir(base_folder)
    output_file = base_folder + "QA.txt"
    with open(output_file, 'w') as f:
        for question in ques_list:
            content="Question: "+ question+'\n'
            answer = answer_generation_chain.run(question)
            content+="Answer: "+ answer+"\n--------------------------------------------------\n\n"
            f.write(content)
    return output_file

getTxt("./absd.pdf")
