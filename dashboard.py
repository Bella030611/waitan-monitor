import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import base64
import io
import os

app = dash.Dash(__name__)

def load_data():
    if os.path.exists('hot_words_with_sentiment.csv'):
        return pd.read_csv('hot_words_with_sentiment.csv')
    elif os.path.exists('hot_words.csv'):
        return pd.read_csv('hot_words.csv')
    else:
        return pd.DataFrame(columns=['title', 'platform', 'sentiment'])

app.layout = html.Div([
    html.H1("外滩舆情平行世界监控", style={'textAlign': 'center'}),
    html.Hr(),
    dcc.Interval(id='interval', interval=10*60*1000),  # 每10分钟刷新
    
    html.Div([
        html.Div([
            html.H3("情感分布"),
            dcc.Graph(id='sentiment-pie')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("热词云图"),
            html.Img(id='wordcloud-img', style={'width': '100%'})
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),
    
    html.Div([
        html.H3("各平台热词数量"),
        dcc.Graph(id='platform-bar')
    ]),
    
    html.Div([
        html.H3("最新热词列表"),
        html.Div(id='hot-words-table')
    ])
])

@app.callback(
    [Output('sentiment-pie', 'figure'),
     Output('wordcloud-img', 'src'),
     Output('platform-bar', 'figure'),
     Output('hot-words-table', 'children')],
    Input('interval', 'n_intervals')
)
def update_dashboard(n):
    df = load_data()
    
    # 情感饼图
    if 'sentiment' in df.columns:
        df['label'] = df['sentiment'].apply(lambda x: '正面' if x>0.6 else ('中性' if x>0.3 else '负面'))
        sentiment_counts = df['label'].value_counts()
        pie_fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title='情感分布')
    else:
        pie_fig = px.pie(title='暂无数据')
    
    # 词云
    if len(df) > 0:
        text = ' '.join(df['title'].tolist())
        try:
            wc = WordCloud(font_path='simhei.ttf', width=600, height=400, background_color='white')
            wc.generate(text)
            img = io.BytesIO()
            wc.to_image().save(img, format='PNG')
            img_src = 'data:image/png;base64,' + base64.b64encode(img.getvalue()).decode()
        except:
            img_src = ''
    else:
        img_src = ''
    
    # 平台柱状图
    if 'platform' in df.columns:
        platform_counts = df['platform'].value_counts()
        bar_fig = px.bar(x=platform_counts.index, y=platform_counts.values, 
                         labels={'x': '平台', 'y': '热词数量'}, title='各平台热词数量')
    else:
        bar_fig = px.bar(title='暂无数据')
    
    # 热词列表
    if len(df) > 0:
        table = html.Table([
            html.Thead(html.Tr([html.Th('平台'), html.Th('标题'), html.Th('情感')])),
            html.Tbody([
                html.Tr([
                    html.Td(row.get('platform', '')),
                    html.Td(row.get('title', '')),
                    html.Td(row.get('sentiment_label', ''))
                ]) for _, row in df.head(20).iterrows()
            ])
        ])
    else:
        table = html.P("暂无数据，请先运行 crawler.py")
    
    return pie_fig, img_src, bar_fig, table

if __name__ == '__main__':
    print("看板启动中，请打开浏览器访问 http://127.0.0.1:8050")
    app.run_server(debug=True)