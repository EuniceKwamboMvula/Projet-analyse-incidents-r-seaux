"""Algorithme d'analyse: détection d'erreurs fréquentes, pics de latence, pertes de paquets, agrégations par fenêtre temporelle."""
import pandas as pd




def detect_frequent_errors(df: pd.DataFrame, top_n=10):
# tokeniser messages pour grouper
df_err = df[df['level']=='ERROR']
top = df_err['msg'].value_counts().head(top_n)
return top




def detect_latency_spikes(df: pd.DataFrame, threshold_ms=200):
spikes = df[df['latency_ms'].notnull() & (df['latency_ms'] >= threshold_ms)]
return spikes.sort_values('latency_ms', ascending=False)




def detect_packet_loss(df: pd.DataFrame, threshold_pct=1.0):
losses = df[df['packet_loss'].notnull() & (df['packet_loss'] >= threshold_pct)]
return losses.sort_values('packet_loss', ascending=False)




def summarize_time_series(df: pd.DataFrame, freq='1H'):
df['ts'] = pd.to_datetime(df['ts'], errors='coerce')
agg = df.set_index('ts').resample(freq).agg({
'msg': 'count',
'latency_ms': 'mean',
'packet_loss': 'mean'
}).rename(columns={'msg': 'events_count'})
return agg