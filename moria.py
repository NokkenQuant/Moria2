import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
import sgs

warnings.filterwarnings('ignore')

import pypfopt as pf
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
import cvxpy

def home():
    st.title('Home')

def backtest():
    st.title('Resultados Backtest')
    comparacao = pd.read_csv('comparacao.csv')
    comparacao.index = comparacao.DATA
    comparacao.drop(columns='DATA', inplace=True)
    lsita_datas = list(comparacao.index)
  
    data = st.select_slider('Selecione data inicial e final',options = lsita_datas, value=(lsita_datas[0],lsita_datas[-1]))
    comaparacao_datas = comparacao.loc[data[0]:data[1]]
    comaparacao_datas = comaparacao_datas/comaparacao_datas.iloc[0]
    # st.write(comaparacao_datas        )
    fig = go.Figure()
    fig.add_trace(go.Scatter(name = 'CDI', x= comaparacao_datas.index,y=comaparacao_datas['CDI'], line= dict(color = 'rgb(42,255,57)')))
    fig.add_trace(go.Scatter(name = 'Fundo', x= comaparacao_datas.index,y=comaparacao_datas['Fundo'], line= dict(color = 'rgb(58,25,223)')))
    fig.update_layout(title = 'Resultado Acumulado', height = 600 , width = 650)
    st.plotly_chart(fig)

    st.markdown('---')

    
    comaparacao_datas.index = pd.to_datetime(comaparacao_datas.index)
    comaparacao_datas['Ano'] = comaparacao_datas.index.year

    # Função para calcular a razão entre o último e o primeiro valor de um grupo
    def calcular_razao(group, ativo):
        ultimo_valor = group.iloc[-1][ativo]
        primeiro_valor = group.iloc[0][ativo]
        return ultimo_valor / primeiro_valor

    # Calcular a razão para cada ano
    razoes_por_pl = comaparacao_datas.groupby('Ano').apply(calcular_razao, 'Fundo')
    razoes_por_cdi = comaparacao_datas.groupby('Ano').apply(calcular_razao, 'CDI')
    # razoes_por_plgatilho = comaparacao_datas.groupby('Ano').apply(calcular_razao, 'PL Gatilhado')

    razoes_por_cdi = round((razoes_por_cdi-1),2)
    razoes_por_pl = round((razoes_por_pl-1),2)
    # razoes_por_plgatilho = round((razoes_por_plgatilho-1),2)
    # Criar um gráfico de barras lado a lado
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_pl,text = razoes_por_pl,textposition='auto', name='PL Fundo', marker_color = 'rgb(58,25,233)'))
    fig2.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_cdi,text = razoes_por_cdi,textposition='auto', name='CDI', marker_color = 'rgb(42,255,57)'))
    # fig.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_plgatilho,text = razoes_por_plgatilho,textposition='auto', name='PL Pos Gatilho'))

    # Atualizar o layout do gráfico
    fig2.update_layout(height = 600,width = 600,barmode='group', xaxis_title='Ano', yaxis_title='Razão (Último/Primeiro Valor)',
                    title='Comparação Retorno YoY ')
    st.plotly_chart(fig2)

    st.markdown('---')

    sensibilidade_cdi = comaparacao_datas[['CDI', 'Fundo']]

    sensibilidade_cdi = sensibilidade_cdi.groupby([sensibilidade_cdi.index.year.rename('Ano'), sensibilidade_cdi.index.month.rename('Mes')]).mean()#.pct_change().dropna()

    sensibilidade_cdi = sensibilidade_cdi.pct_change().dropna()

    sensibilidade_cdi['Diff'] =( (1+sensibilidade_cdi['Fundo']) / (1+sensibilidade_cdi['CDI']))-1

    cdi_pl = pd.DataFrame(sensibilidade_cdi['Diff'])
    cdi_pl =  pd.pivot_table(cdi_pl, index= 'Mes', columns= 'Ano',values= 'Diff').fillna(0)
    cdi_pl.index = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

    #criacao do heatmap
    fig3, ax = plt.subplots(figsize = (12,10)) #cria 2 figuras
    cmap = sns.color_palette('RdYlGn', 50) # define as cores 
    sns.heatmap(cdi_pl, cmap = cmap, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02, cbar = False, linewidths=1, xticklabels = True, yticklabels = True, ax = ax)
    ax.set_title('CDI vs PL do Fundo', fontsize = 18)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '12')
    ax.set_xticklabels(ax.get_xticklabels(), fontsize = '12')
    ax.xaxis.tick_top() #colocar o x axis em cima
    plt.ylabel('')
    st.pyplot(fig3)
     

def refazer():
    st.title('Refazer BT')

def equipe():
    st.title('Equipe')

def main():
    st.sidebar.image ('imagem.png', width = 200)
    st.sidebar.title('Fundo Moria')
    st.sidebar.markdown('---')
    lista_menu = ['Home','Resultados Backtest', 'Refazer BT', 'Equipe']
    escolha = st.sidebar.radio('Menu', lista_menu)

    if escolha == 'Home':
        home()
    if escolha == 'Resultados Backtest':
        backtest()
    if escolha == 'Refazer BT':
        refazer()
    if escolha == 'Equipe':
        equipe()
    
main()
