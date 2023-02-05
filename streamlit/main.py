from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

import spacy

import os

nlp = spacy.load('en_core_web_lg')

# Code Starts Here------------------------------------------------


def clean(val):
    '''
    Clean the row description
    '''
    doc = nlp(val)
    text = ''
    for w in doc:
        if not w.is_stop and not w.is_punct and not w.like_num: 
            text += w.lemma_.lower() + ' '
    text = text.strip()
    return text


df = pd.read_csv(os.getcwd() + '\\..\\data\\data_clean.csv')
df['Cleaned_Description'] = df['Description'].apply(clean)


def clean_prompt(prompt):
    '''
    Clean the Prompt

    Change: Concatenated TfIdf
    - Cut into a threshold number
    - Less than 10 words etc.
    '''
    doc = nlp(prompt)
    txt = ''
    for w in doc:
        if not w.is_stop and not w.is_punct and not w.like_num:
            txt += w.lemma_.lower() + ' '
    txt = txt.strip()

    vect = TfidfVectorizer()
    X = vect.fit_transform([txt])
    df = pd.DataFrame(X.toarray(), columns=vect.get_feature_names_out()).T.sort_values(by=0).iloc[:min(10, X.shape[1])]
    
    new_txt = ''
    for val in df.index:
        new_txt += val + ' '

    return new_txt


def generate_undirected(recommendations):
    place_list = list(df['Location'])
    top_n = list(recommendations['Location'])
    similarity = list(df['Similarity'])

    G = nx.Graph()

    for place in place_list:
        G.add_node(place)

    for place1 in place_list:
        for place2 in place_list:
            if place1 == place2:
                continue
            else:
                G.add_edge(place1, place2)

    colors = []
    for i in range(len(similarity)):
        if place_list[i] in top_n:
            colors.append('r')
            similarity[i] *= 1000
        elif similarity[i] >= max(similarity) / 2:
            colors.append('y')
            similarity[i] *= 500
        else:
            colors.append('b')
            similarity[i] *= 100

    edge_width = []
    for i in range(len(place_list)):
        for j in range(i+1, len(place_list)):
            if place_list[i] in top_n and place_list[j] in top_n:
                edge_width.append(0.95)
            elif similarity[i] >= max(similarity)/2 and similarity[j] >= max(similarity)/2:
                edge_width.append(0.5)
            else:
                edge_width.append(0)

    pos = nx.spring_layout(G)

    f = plt.figure(figsize=(20,20))
    nx.draw_networkx(G, pos=pos, width=edge_width, node_size=similarity, node_color=colors, font_size=10, font_color='black')
    # Adding the Objects
    f.savefig(os.getcwd() + '\\..\\fig\\undirected_temp.jpg')


def generate_directed(recommendations):
    edges=[]
    for i in range((recommendations.shape[0])-1):
        edges.append(((recommendations["Location"][i], recommendations["Location"][i+1])))
    

    G = nx.DiGraph(edges)

    f = plt.figure()
    nx.draw(G, with_labels=True)
    plt.margins(x=0.4)
    f.savefig(os.getcwd() + '\\..\\fig\\directed_temp.jpg')


def generate_recommendations(prompt, n):
    # Clean the Prompt
    cleaned_prompt = clean_prompt(prompt)

    # Clean the Description in each place
    doc = nlp(cleaned_prompt)

    # Calculate the Similarity for each
    df['Similarity'] = df['Cleaned_Description'].apply(lambda x: doc.similarity(nlp(x)))

    # Generate top_n recommendations
    top_n = df.sort_values(by='Similarity', ascending=False)[['Location', 'Similarity']].reset_index(drop=True).head(n)
    
    # Show the top n recommendations
    st.table(top_n)

    # Generate Graphs of Similarity
    generate_undirected(top_n)

    # Generate Path
    generate_directed(top_n)

    # Get the paths
    undirected = Image.open(os.getcwd() + '\\..\\fig\\undirected_temp.jpg')
    directed = Image.open(os.getcwd() + '\\..\\fig\\directed_temp.jpg')

    # Show the images
    st.image(undirected, 'Look at out similar different places are to your travel!')
    st.image(directed, 'This is your Trip Itenerary!')


def main():
    st.title("CaLaBarZon Trip Itenerary Generator!")
    st.markdown("Come let's go to one of the most visited regions of the country! Just put what you want and how many places you want to go to, and we will recommend places for you to go to in order!")
    inp = st.text_input("What do you fancy today?")
    n = int(st.number_input("How many places do you want to go to?", min_value=1, value=5, step=1))

    if inp != '':
        generate_recommendations(inp, n)


if __name__ == '__main__':
    main()