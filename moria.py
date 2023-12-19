import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter  # Importe diretamente a classe PercentFormatter
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
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fundo Sistemático e Quantitativo</title>
    </head>
    <body>

    <h1>Bem-vindo ao nosso Fundo Sistemático e Quantitativo</h1>

    <p>Projetado para buscar desempenho superior ao CDI, mantendo uma volatilidade cuidadosamente controlada em torno de 10%. Com uma abordagem baseada em algoritmos e análise de dados, nosso fundo é estruturado para otimizar oportunidades de investimento, adaptando-se dinamicamente às condições de mercado em constante mudança.</p>

    <p>Em um cenário financeiro cada vez mais complexo, nossa estratégia quantitativa utiliza modelos matemáticos avançados e algoritmos preditivos para identificar padrões e oportunidades de mercado. Este enfoque sistemático nos permite tomar decisões baseadas em dados, minimizando a interferência emocional e proporcionando uma execução disciplinada de nossas estratégias.</p>

    <p>Nosso compromisso com a volatilidade controlada destaca-se como uma característica fundamental. Buscamos oferecer aos investidores uma experiência estável e previsível, mitigando os riscos inerentes aos mercados financeiros. Mantendo uma volatilidade média em torno de 10%, visamos proporcionar um equilíbrio entre retorno potencial e preservação de capital.</p>

    <p>A transparência é um pilar essencial de nossa filosofia. Oferecemos relatórios detalhados e análises regulares, permitindo que os investidores compreendam plenamente a lógica por trás de nossas decisões de investimento. Nossa equipe experiente e dedicada está comprometida em fornecer um serviço personalizado, adaptando continuamente nossas estratégias para atender às expectativas de nossos investidores.</p>

    <p>Se você busca um fundo que combine inovação, disciplina quantitativa e a busca por retornos sólidos com uma volatilidade controlada, convidamos você a explorar as oportunidades que nosso fundo sistemático oferece. Estamos prontos para embarcar nessa jornada de investimento consistente e perspicaz ao seu lado.</p>

    </body>
    </html>

    """
    st.markdown(html_code, unsafe_allow_html = True)

def backtest():
    st.title('Resultados Backtest')
    st.header('Rentabilidade do Fundo vs CDI')
    
    comparacao = pd.read_csv('comparacao.csv')
    comparacao.index = comparacao.DATA
    comparacao.drop(columns='DATA', inplace=True)
    lsita_datas = list(comparacao.index)
  
    data = st.select_slider('Selecione data inicial e final',options = lsita_datas, value=(lsita_datas[0],lsita_datas[-1]))
    st.subheader('Rentabilidade Acumulada no perído')
    comaparacao_datas = comparacao.loc[data[0]:data[1]]
    comaparacao_datas = comaparacao_datas/comaparacao_datas.iloc[0]
    retorno_acumulado = comaparacao_datas['Fundo'][-1]
    retorno_acumulado_cdi = comaparacao_datas['CDI'][-1]
    st.write(f'Retorno Acumulado do Fundo **{round(retorno_acumulado*100,2)}%**')
    st.write(f'Retorno Acumulado do CDI **{round(retorno_acumulado_cdi*100,2)}%**')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(name = 'CDI', x= comaparacao_datas.index,y=comaparacao_datas['CDI'], line= dict(color = 'rgb(42,255,57)')))
    fig.add_trace(go.Scatter(name = 'Fundo', x= comaparacao_datas.index,y=comaparacao_datas['Fundo'], line= dict(color = 'rgb(58,25,223)')))
    fig.update_layout(title = 'Resultado Acumulado', height = 600 , width = 650)
    st.plotly_chart(fig)

    st.markdown('---')
    st.subheader('Comparação da rentabilidade do fundo contra a o CDI, para cada período')
    
    comaparacao_datas.index = pd.to_datetime(comaparacao_datas.index)
    comaparacao_datas['Ano'] = comaparacao_datas.index.year
    comaparacao_datas.dropna(inplace=True)
    

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

    fig2.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_pl,text = razoes_por_pl,textposition='auto', name='Fundo', marker_color = 'rgb(58,25,233)'))
    fig2.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_cdi,text = razoes_por_cdi,textposition='auto', name='CDI', marker_color = 'rgb(42,255,57)'))
    # fig.add_trace(go.Bar(x=razoes_por_pl.index, y=razoes_por_plgatilho,text = razoes_por_plgatilho,textposition='auto', name='PL Pos Gatilho'))

    # Atualizar o layout do gráfico
    fig2.update_layout(yaxis_tickformat = '2%f')
    fig2.update_traces(texttemplate = '%{text:.2%}',textposition = 'auto')

    fig2.update_layout(height = 600,width = 600,barmode='group', xaxis_title='Ano', yaxis_title='Razão (Último/Primeiro Valor)',
                    title='Comparação Retorno YoY ')
    st.plotly_chart(fig2)

    st.markdown('---')
    st.subheader('Sensibilidade de performance do Fundo vs CDI')

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
    # ax.set_title('CDI vs PL do Fundo', fontsize = 18)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '12')
    ax.set_xticklabels(ax.get_xticklabels(), fontsize = '12')
    ax.xaxis.tick_top() #colocar o x axis em cima
    plt.ylabel('')
    st.pyplot(fig3)

    st.markdown('---')
    st.header('Análise da Volatilidade')
    st.subheader('Distribuição da Volatilidade do Fundo')
    st.write('A volatilidade é calculada como desvio-padrão dos retornos diários da cota do fundo')

    df_volatilidade = (comaparacao_datas['Fundo'].pct_change().rolling(21).std()*np.sqrt(252)).fillna(0)
    
    # Plotar o histograma
    

    fig4 = plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    sns.histplot(df_volatilidade, kde=True, color='#0B58DC', bins=80) 

    # Formatando o eixo X em percentual
    plt.gca().xaxis.set_major_formatter(PercentFormatter(1, decimals=0))

    plt.title('Distribuição de Dados')
    plt.xlabel('Valores (em percentual)')
    plt.ylabel('Frequência')

    st.pyplot(fig4)

    st.markdown('---')
    st.subheader('Volatilidade ao longo do tempo')
    
    df_volatilidade = pd.DataFrame(df_volatilidade)
    df_volatilidade.columns = ['Volatilidade do Fundo']
    df_volatilidade['Vol Média'] = df_volatilidade['Volatilidade do Fundo'].mean()
    df_volatilidade['Vol Min'] = 0.05
    df_volatilidade['Vol Target'] = 0.1
    df_volatilidade['Vol Max'] = 0.12

    # Criando o gráfico de linha com Plotly Express
    fig = px.line(df_volatilidade[['Volatilidade do Fundo', 'Vol Média', 'Vol Target', 'Vol Min', 'Vol Max']],
                title='Volatilidade do Fundo<br><sup>Volatilidade Móvel 21, anualizada</sup>')

    # Formatando o eixo Y como percentual
    fig.update_layout(yaxis_tickformat=".2%")

    # Adicionando uma referência ao percentual no eixo Y (opcional)
    # fig.update_layout(annotations=[dict(xref='paper', yref='paper', x=0.02, y=0.98)])

    # Mostrando o gráfico
    st.plotly_chart(fig)
def refazer():
    st.title('Refazer BT em Construção...')

def equipe():
    st.title('Equipe')
    col1, col2 = st.columns(2)
    with col1:
        st.header('Eduardo Alves Moreira')
        st.image('Eduardo.png', width= 100)
        st.write('Eduardo Moreira é um profissional com graduação em Economia pela UnB em 2014, com uma carreira dedicada ao Mercado Financeiro e especialização em trading e investimentos sistemáticos. Ele possui o certificado CNPI e uma expertise destacada em Python para Mercado Financeiro, Quatitative Trading, e otimização de portfólio./nA trajetória de Eduardo incluiu um papel fundamental na criação e gestão da estratégia de Investimento no Exterior para o 3º maior Fundo de Pensão do país, a FUNCEF. Ele utilizou ativamente Python e técnicas quantitativas, incluindo otimização de portfólio, durante todo o processo de criação e desenvolvimento da estratégia. Além disso, Eduardo foi responsável pela criação de dashboards para acompanhamento do mercado internacional, proporcionando uma visão analítica abrangente.')
        st.markdown('---')
        st.header('Marco Túlio Coutinho')
        st.image('Marco Tulio.png', width= 100)
        st.write('Marco Tulio é a pessoa dedicada a capacitar gestores de ativos para se destacarem na captação de capital, proporcionando a eles as ferramentas e conhecimentos necessários para navegar com confiança pelas complexidades das mais sofisticadas Solicitações de Propostas (RFPs)./nComo investidor institucional experiente e consultor de investimentos, essa pessoa traz consigo uma vasta quantidade de conhecimento e experiência. Com quinze anos de atuação na indústria, ela aprimorou suas habilidades na redação de RFPs, na seleção e monitoramento de gestores de ativos, na coordenação da devida diligência de investimentos e na tomada de decisões de alocação de ativos.')

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

