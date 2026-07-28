import pandas as pd
from snownlp import SnowNLP

# 读取爬虫生成的热词数据
df = pd.read_csv('hot_words.csv')

# 对每条热词的标题进行情感打分（0~1，越接近1越正面）
df['sentiment'] = df['title'].apply(lambda x: SnowNLP(x).sentiments)

# 打标签
def label_sentiment(score):
    if score < 0.3:
        return '负面'
    elif score < 0.6:
        return '中性'
    else:
        return '正面'

df['sentiment_label'] = df['sentiment'].apply(label_sentiment)

# 保存带情感分析的结果
df.to_csv('hot_words_with_sentiment.csv', index=False, encoding='utf-8-sig')

# 打印统计
print("情感分析完成！")
print(df['sentiment_label'].value_counts())
print(f"共分析 {len(df)} 条热词")