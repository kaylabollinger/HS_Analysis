# -*- coding: utf-8 -*-
"""
HS Analysis

@author = Kayla Bollinger
"""

# import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(layout = 'wide')

# define functions
def list2series(series):
    return pd.Series([x for list_ in series for x in list_])

def plot_wordfreq(df_current,df_top_deck):
    fig = go.Figure()
    
    def check_text(text,w):
        if w in text:
            return 1
        else:
            return 0
                
    df_current_temp = df_current.sort_values('format')#.drop_duplicates(['name','type'])
    df_top_temp = df_top_deck.sort_values('deck_format')#.drop_duplicates(['name','type'])    
    
    w_curr = pd.value_counts(list2series(df_current.drop_duplicates(['name','type'])['text'].dropna()))
    w_top = pd.value_counts(list2series(df_top_deck['text'].dropna()))
    
    num_words = 10
    w_all = list(set(w_curr.index[:num_words]).union(set(w_top.index[:num_words])))
    w_all = [w for w in w_all if not w.isdigit()] # remove words that are also numbers (causes indexing issues and not needed)
        
    plt_curr = w_curr.loc[w_curr.index.isin(w_all)]    
    plt_top = w_top.loc[w_top.index.isin(w_all)]
    df_all = pd.concat([plt_curr,
                        plt_top]).sort_values(0,ascending=False)     
        
    blue = 'rgb(85,181,255)'
    orange = 'rgb(255,163,32)'
    dict_list = []
    for w in df_all.index.unique():
        d = {'w':w}
        
        df_current_temp['w_check'] = df_current_temp['text'].apply(lambda text: check_text(text,w)).copy()
        df_w_ct = df_current_temp['w_check'].sum()
        df_n_ct = df_current_temp['name'].count()
        
        x0 = df_w_ct/df_n_ct
        d['current_freq'] = x0*100
        
        
        df_top_temp['w_check'] = df_top_temp['text'].apply(lambda text: check_text(text,w)).copy()
        df_w_ct = df_top_temp['w_check'].sum()
        df_n_ct = df_top_temp['name'].count()
        
        x1 = df_w_ct/df_n_ct
        d['top_freq'] = x1*100
        
        if x0<x1:
            color = orange
        else:
            color = 'white'
            
        d['line_color'] = color
        dict_list.append(d)
        
    df_plt = pd.DataFrame(dict_list).set_index('w').sort_values('current_freq',ascending=False)
    for w in reversed(df_plt.index):
        fig.add_trace(go.Scatter(x=[df_plt.at[w,'current_freq'],df_plt.at[w,'top_freq']], 
                                 y=[w,w],
                                 mode='lines',
                                 showlegend=False,
                                 marker_color=df_plt.at[w,'line_color'],
                                 hovertemplate='%{x}<extra></extra>',
                                 line=dict(width=5)))
    
    fig.add_trace(go.Scatter(x=df_plt['current_freq'], 
                             y=df_plt.index,
                             mode='markers',
                             showlegend=True,
                             name='all cards',
                             marker_color=blue,
                             hovertemplate='%{x}<extra></extra>'))
    fig.add_trace(go.Scatter(x=df_plt['top_freq'], 
                             y=df_plt.index,
                             mode='markers',
                             showlegend=True,
                             name='top decks',
                             marker_color=orange,
                             hovertemplate='%{x}<extra></extra>'))

    fig.update_traces(marker=dict(size=15,
                                  line=dict(width=1,
                                            color='white')),
                                  selector=dict(mode='markers'))
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        autosize=False,
        width=1300,
        height=500)
    
    fig.update_layout(title_text='Frequency of Words In: All Cards VS Cards in Top Decks',title_font_size=24)    
    fig.update_xaxes(title='frequency (%)',title_font_size=18,tickfont_size=18)
    fig.update_yaxes(tickfont_size=18)
    fig.update_layout(legend_font_size=16)
    
    st.plotly_chart(fig)  
    
    return df_plt.index.unique()

def plot_topword_freq(df_current,word):
    
    df_temp = df_current.sort_values('date_released').drop_duplicates(['name','type'])
    
    def check_text(text,w):
        if w in text:
            return 1
        else:
            return 0
        
    fig = go.Figure()
    blue = 'rgb(85,181,255)'

        
    df_temp['w_check'] = df_temp['text'].apply(lambda text: check_text(text,word)).copy()
    df_w_ct = df_temp[['format','w_check']].groupby(df_temp['format']).sum()
    df_n_ct = df_temp[['format','name']].groupby(df_temp['format']).count()
    
    y = list(df_w_ct['w_check']/df_n_ct['name'])    

    fig.add_trace(go.Scatter(x=[format_name.title() for format_name in df_w_ct.index], 
                              y=[val*100 for val in y],
                              mode='lines',
                              showlegend=True,
                              name=word,
                              line=dict(width=5,color='white'),
                              hovertemplate='<extra></extra>'))
    fig.add_trace(go.Scatter(x=[format_name.title() for format_name in df_w_ct.index], 
                              y=[val*100 for val in y],
                              mode='markers',
                              showlegend=False,
                              marker_color=blue,
                              hovertemplate='%{y}<extra></extra>'))
    
    fig.update_traces(marker=dict(size=15,
                                  line=dict(width=1,
                                            color='white')),
                                  selector=dict(mode='markers'))
    
    fig.update_layout(
        autosize=False,
        width=1000,
        height=500,
        title='word compare')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    fig.update_layout(title_text='Frequency of Words In All Cards Over Time',title_font_size=24)    
    fig.update_xaxes(tickfont_size=18)
    fig.update_yaxes(title='frequency (%)',title_font_size=18,tickfont_size=18)
    fig.update_layout(legend_font_size=16)
    
    st.plotly_chart(fig)  


def plot_manacurve(df_full,att_type,att_name,class_colors):
            
    df_temp = df_full.loc[df_full[att_type]==att_name,:].sort_values('deck_format')
    format_list = df_temp['deck_format'].unique()
    
    fig = make_subplots(rows=len(format_list), cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02)
    
    blue = 'rgb(85,181,255)'
    orange = 'rgb(255,163,32)'
    opacity_ratio = len(df_temp['deck_format'].unique())/len(df_temp['deck_url'].unique())
    row = 0
    x = np.arange(0,8) # x axis values--same for every graph
    for deck_format in format_list:
        row += 1
        
        df_format = df_temp.loc[df_temp['deck_format']==deck_format,:].copy()
        y_list = []
        for deck in df_format['deck_url'].unique():
            df_deck = df_format.loc[df_format['deck_url']==deck,:].copy()
            df_deck['cost'] = df_deck['cost'].apply(lambda x: 7 if x >= 7 else x)
            costs = []
            for idx, card in df_deck.iterrows():
                if card['deck_ct']==2:
                    costs.extend([card['cost'],card['cost']])
                else:
                    costs.append(card['cost'])
            data = pd.value_counts(costs)
            
            y = np.zeros(8)
            y[[int(cost) for cost in data.index.values]] = data.values
            fig.add_trace(go.Bar(x=x, 
                                 y=y,
                                 marker_color=blue,
                                 showlegend=False,
                                 # opacity=1/len(df_format['deck_url'].unique()),
                                 opacity=opacity_ratio,
                                 hovertemplate='<extra></extra>'),
                                 row=row, col=1)  
            y_list.append(y) # to calculate average later
            
            fig.update_yaxes(title_text=deck_format.title(), row=row, col=1, range=[0,15])
    
            # Overlay both histograms
            fig.update_layout(barmode='overlay')
        
        # plot average
        y_perc = np.percentile(y_list,[25,50,75],axis=0)
        
        fig.add_trace(go.Scatter(x=x, y=y_perc[1], 
                                 error_y=dict(
                                     array=y_perc[2]-y_perc[1],
                                     arrayminus=y_perc[1]-y_perc[0]
                                     ),
                                 showlegend=False,
                                 mode='lines',
                                 line=dict(width=2,color=orange),
                                 hovertemplate='%{y}<extra></extra>'),
                                 row=row, col=1)
        
    
    fig.update_layout(
        autosize=False,
        width=700,
        height=900)
    
    fig.update_layout(title_text='Mana Curve for '+att_name.title()+'s',title_font_size=24)    
    fig.update_xaxes(tickfont_size=18)
    fig.update_yaxes(title_font_size=18,tickfont_size=12)
    fig.update_layout(legend_font_size=16)
    
    st.plotly_chart(fig)   
    
def plot_mana_changeovertime_allclasses(df_mana_gb,cost_list,class_boxes):
    fig = go.Figure()
        
    idx=1    
    for class_box in class_boxes:
        if class_box['checked']:
            class_name = class_box['class_name']
            df_class = df_mana_gb.loc[df_mana_gb.index.get_level_values(idx)==class_name]
            df_class = df_class.reset_index(level=idx,drop=True)
            format_list = df_class.index

            y_diff = []
            for cost in range(cost_list[0],cost_list[1]+1):
                y = [df_class[str(cost)].at[deck_format] for deck_format in format_list]
                y_diff.append(y)
                
                
            y = np.sum(y_diff,axis=0)
            x = [name.title() for name in format_list]
        
            fig.add_trace(go.Scatter(x=x, 
                                      y=y,
                                      mode='lines',
                                      line=dict(width=5,color=class_box['class_color']),
                                      name=class_name.title()))
            fig.add_trace(go.Scatter(x=x, 
                                      y=y,
                                      mode='markers',
                                      marker=dict(size=10,color=class_box['class_color']),
                                      hovertemplate='%{y}<extra></extra>',
                                      showlegend=False))

        
    fig.update_layout(
        autosize=False,
        width=1000,
        height=700)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    fig.update_layout(title_text=f'Number of Cards with Cost in [{cost_list[0]},{cost_list[1]}]',title_font_size=24)    
    fig.update_xaxes(tickfont_size=18)
    fig.update_yaxes(tickfont_size=18)
    fig.update_layout(legend_font_size=16)


    st.plotly_chart(fig)

# load data
@st.cache
def load_data():
    date_current = '2022.10.11'
    df_current = pd.read_pickle(f'card_data_current_{date_current}_cleaned.pkl')
    
    # add format to df_current
    def format_check(date_released):
        year = date_released.year
        if year < 2016:
            return None
        elif year < 2017:
            return 'kraken'
        elif year < 2018:
            return 'mammoth'
        elif year < 2019:
            return 'raven'
        elif year < 2020:
            return 'dragon'
        elif year < 2021:
            return 'pheonix'
        elif year < 2022:
            return 'gryphon'
        elif year < 2023:
            return 'hydra'
        else:
            return 'unknown'
        
    df_current['format'] = df_current['date_released'].apply(format_check)
    categories = df_current[['format','date_released']].groupby('format').quantile(.5).sort_values('date_released').index
    df_current['format'] = pd.Categorical(df_current['format'],categories=categories,ordered=True)
    
    # get top deck data
    date_top_deck = '2022.11.07'
    df_top_deck = pd.read_pickle(f'top_deck_data_{date_top_deck}_merged.pkl')
    
    # for some reason categories are lost in streamlit? redefine them here
    categories = df_top_deck[['deck_format','deck_date_published']].groupby('deck_format').quantile(.5).sort_values('deck_date_published').index
    df_top_deck['deck_format'] = pd.Categorical(df_top_deck['deck_format'],categories=categories,ordered=True)
    
    ###### do something about this
    df_top_deck.dropna(subset=['type','classes'],inplace=True)
    
    # mana curve
    df_temp = df_top_deck.copy().sort_values('deck_format')
    df_temp['cost'] = df_temp['cost'].apply(lambda x: 7 if x >= 7 else x)
    class_list = df_temp['deck_class'].unique()
    
    dict_list = []
    for deck in df_temp['deck_url'].unique():
        df_deck = df_temp.loc[df_temp['deck_url']==deck]

        d = {'deck_format':df_deck['deck_format'].values[0]}
        d['deck_class'] = df_deck['deck_class'].values[0]
        
        costs = []
        for idx, card in df_deck.iterrows():
            if card['deck_ct']==2:
                costs.extend([card['cost'],card['cost']])
            else:
                costs.append(card['cost'])
        data = pd.value_counts(costs)
        
        y = np.zeros(8)
        y[[int(cost) for cost in data.index.values]] = data.values
        for cost in range(0,8):
            d[str(cost)] = y[cost]
                    
        dict_list.append(d)
        
    df_mana = pd.DataFrame(dict_list)
    df_mana_gb = df_mana.groupby(['deck_format','deck_class'],sort=False).quantile(0.5)
    
    return df_current, df_top_deck, df_mana_gb, class_list

df_current, df_top_deck, df_mana_gb, class_list = load_data()

# Power Creep
st.title('Power Creep in Hearthstone')

st.markdown("""
        Wiktionary definition of **"Power Creep"**:
        The gradual unbalancing of a game due to 
        successive releases of new content, leaving the older ones under powered.
        """)
        
st.markdown("""
        This phenomenon occurs by design as new content in games must be more 
        powerful to guarantee the content is used (and not ignored in favor of 
        the old content). Hearthstone, a strategy card game from Blizzard Entertainment, 
        is most certainly affected by this phenomenon. To put it simply, players 
        need strong cards to defeat opponents, so when new cards are added to the game 
        (from new expansions every few months) they need to be stronger than cards that 
        are already in the game. Power creep is a bit like inflation--if a low, steady 
        level of inflation is necessary to drive economic growth, then so to is a low, 
        steady level of power creep necessary to drive player engagement. The key words 
        being "low" and "steady". If too much power is added to a game too quickly, 
        this can reduce player engagement (e.g., the game may feel too unbalanced or too complex).
        """)
        
st.markdown("""
            Because power creep can be a tricky necessity in games, and because I happen 
            to be a fan of Hearthstone, I thought it would be an interesting excercise 
            in data analytics to take a closer look at this phenomenon through a more objective lens.
            """)
            
st.subheader('Data Used in this Work')

st.markdown("""
            The main source of data used here is Hearthstone card data via [RapidAPI](https://rapidapi.com/omgvamp/api/hearthstone). 
            The other source of data was scraped from decks posted publicly on [Hearthstone Top Decks](https://www.hearthstonetopdecks.com/). 
            This data was used as an indication of which hearthstone cards are considered 
            good/powerful (if a card is used in a highly rated deck, then we consider it 
            powerful). Hearthstone Top Decks is an awesome site for Hearthstone related articles, 
            news, guides, and other content.
            """)
            
st.markdown("""
            **NOTE**: When this data was acquired, the last Hearthstone expansion 
            available was "Murder at Castle Nathria".
            """)
            
st.subheader('Results Shown Here')

st.markdown("""
            Here we analyze power creep through two card properties: card text and card cost.
            I hope to expand this analysis in the future, but these are the two properties I 
            thought would be most indicitave of power creep in the game.
            """)
            
st.markdown("""
            When we analyze changes in cards over time, we use the names of Hearthstone years 
            (mostly for fun). If unfamiliar with Hearthstone years, just note that 
            "Kraken" = 2016, ..., "Hydra" = 2022. Years will always be presented in 
            ascending order.
            """)
            
st.markdown('')
st.markdown('')
st.markdown('')
st.markdown('')


# Card Text
st.header('Card Text')

st.markdown("""
            Here we observe the frequency of the most common words found in the text of 
            Hearthstone cards. "Common" words were determined by calculating their frequency 
            of occurrence in two sets of card data: (1) "all cards" = every Hearthstone card 
            printed, (2) "top decks" = cards found in highly rated decks. If a word was in the 
            top ten most frequently used in either set, it is included in the graph below.
            """)
st.markdown("""
            **NOTE**: The words shown here are from after pre-processing of the text data. Stemming 
            was used to reduce words to a common base form to more
            accurately measure the frequency of a word (e.g., reducing "minions" to "minion", since 
            we would want to count "minions" and "minion" as the same word in the context of this analysis). 
            This pre-processing sometimes leads to seemingly incorrect spelling of a word (e.g., "damag" vs "damage"), 
            but hopefully not so much that the word is unrecognizable.
            """)

col1, col2, col3 = st.columns([1,1,10])

with col1:
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')

    st.write('Filter by:')

    card_types = ['all','spell','minion','weapon']
    player_class = list(list2series(df_current['classes']).unique())
    player_class.insert(0,'all')    

    type_select = st.selectbox('Card Type',tuple(type_name.title() for type_name in card_types))
    class_select = st.selectbox('Player Class',tuple(class_name.title() for class_name in player_class))

    if type_select == 'All':
        df_current_plot = df_current
        df_top_deck_plot = df_top_deck
    else:
        df_current_plot = df_current.loc[df_current['type']==type_select.lower()]
        df_top_deck_plot = df_top_deck.loc[df_top_deck['type']==type_select.lower()]
                
    def check_list(list_,element):
        if element in list_:
            return True
        else:
            return False           
        
    if class_select == 'All':
        pass
    else:
        df_current_plot = df_current_plot[df_current_plot['classes'].apply(lambda list_: check_list(list_,class_select.lower()))]
        df_top_deck_plot = df_top_deck_plot[df_top_deck_plot['classes'].apply(lambda list_: check_list(list_,class_select.lower()))]


with col3:
    w_all = plot_wordfreq(df_current_plot,df_top_deck_plot)
    
st.markdown('')
st.markdown("""
            Words like "battlecry", "damage", "deal", "card", and "draw" occur more 
            frequently in top decks. If these words are indicitave of a card being 
            more powerful than average, we may expect to see an uptick of cards 
            containing these words over time (due to power creep). Indeed, there are 
            signs of this in the graph below.
            """)
st.markdown('')
st.markdown('')

col1, col2, col3 = st.columns([1,1,10])
    
with col1:
    word = st.radio('Choose Word',w_all)
with col3:
    plot_topword_freq(df_current,word)


# Card Cost
class_colors = {'warlock':'rgb(140,77,156)',
                'shaman':'rgb(90,97,174)',
                'mage':'rgb(114,157,197)',
                'priest':'rgb(222,223,222)',
                'druid':'rgb(116,75,36)',
                'rogue':'rgb(255,79,173)',
                'warrior':'rgb(173,59,41)',
                'paladin':'rgb(247,174,74)',
                'hunter':'rgb(101,145,55)',
                'demon hunter':'rgb(200,245,55)'}

st.header('Card Cost')

st.markdown("""
            Here we observe how mana curves of different classes change over time in 
            highly rated decks. 
            All else being equal, a lower cost card is more "powerful" than a higher 
            cost card as it uses fewer resources to play. We expect that power creep 
            may show itself in the cost of cards by lowering mana curves. 
            Indeed, we tend to see that curves for every class start to lean towards the lower cost side 
            over time. 
            To more closely inspect the mana curves and compare different classes, 
            the second figure below offers a view of how many cards within a chosen 
            cost range are typical of each class over time. By using this figure, 
            we can again see that each class trends towards using more low cost cards 
            over time.
            """)
            
st.markdown("""
            **NOTE**: The card cost labeled "7" refers to "7+", that is, it refers 
            to all cards with cost greater than or equal to 7.
            """)

col1, col2, col3 = st.columns([1,1,10])

with col1:
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    deck_class = tuple(class_name.title() for class_name in df_top_deck['deck_class'].unique())
    class_select = st.selectbox('Select Class',deck_class)

with col3:
    plot_manacurve(df_top_deck,'deck_class',class_select.lower(),class_colors)
    
col1, col2, col3 = st.columns([2,1,8])

with col1:
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    st.write('Choose Cost Range (7 = 7+)')
    cost_values = st.slider('', 0, 7, (3,5))
    
    st.write('')
    st.write('Choose Classes')
    
    class_boxes = []
    for class_name in class_list:
        d = {'class_name':class_name}
        d['class_color'] = class_colors[class_name]
        d['checked'] = st.checkbox(class_name.title(),value=True)
        class_boxes.append(d)
        
        

with col3:
    plot_mana_changeovertime_allclasses(df_mana_gb,cost_values,class_boxes)
    
    
    
    
    
    
    
    
    
    