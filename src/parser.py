"""Lit des fichiers de logs et produit un DataFrame standardisé: columns = [ts, source, level, msg, latency_ms, packet_loss]"""
import re
import pandas as pd
from datetime import datetime
from pathlib import Path


LOG_PATTERNS = {
'core': re.compile(r'(?P<ts>\S+)\s+(?P<level>ERROR|WARN|INFO)\s+\[(?P<source>CORE)\]\s+(?P<msg>.*)'),
'transmission': re.compile(r'(?P<ts>\S+)\s+(?P<level>ERROR|WARN|INFO)\s+\[(?P<source>TRANSMISSION)\]\s+(?P<msg>.*)'),
'ip': re.compile(r'(?P<ts>\S+)\s+(?P<level>ERROR|WARN|INFO)\s+\[(?P<source>IP)\]\s+(?P<msg>.*)')
}




def parse_log_file(path: str):
rows = []
p = Path(path)
for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
for name, pat in LOG_PATTERNS.items():
m = pat.match(line)
if m:
d = m.groupdict()
# essayer extraire latence / packet loss
latency = None
loss = None
lat_m = re.search(r"latency[:= ]+(?P<lat>\d+(?:\.\d+)?)ms", d['msg'], re.I)
if lat_m:
latency = float(lat_m.group('lat'))
loss_m = re.search(r"loss[:= ]+(?P<loss>\d+(?:\.\d+)?)%", d['msg'], re.I)
if loss_m:
loss = float(loss_m.group('loss'))
rows.append({
'ts': d['ts'],
'source': d.get('source', name),
'level': d.get('level'),
'msg': d.get('msg'),
'latency_ms': latency,
'packet_loss': loss
})
break
return pd.DataFrame(rows)




if __name__ == '__main__':
import sys
df = parse_log_file(sys.argv[1])
print(df.head())