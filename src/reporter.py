"""Prend les résultats d'analyse et génère: Excel (pandas.ExcelWriter) et PDF (ReportLab/WeasyPrint)."""
import pandas as pd
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet




def generate_excel(summary_df: pd.DataFrame, top_errors, spikes_df, out_path: str):
out = Path(out_path)
out.parent.mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
summary_df.to_excel(writer, sheet_name='timeseries')
pd.DataFrame(top_errors).to_excel(writer, sheet_name='top_errors')
spikes_df.to_excel(writer, sheet_name='spikes')
return out




def generate_pdf(short_summary: str, top_errors, out_path: str):
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(out_path)
story = [Paragraph('Rapport hebdomadaire — Analyse incidents', styles['Title']), Spacer(1,12), Paragraph(short_summary, styles['Normal']), Spacer(1,12)]
# erreurs
rows = [(k, v) for k,v in top_errors.items()]
if rows:
story.append(Paragraph('Top erreurs', styles['Heading2']))
story.append(Table([['Erreur', 'Occurrences']] + rows))
doc.build(story)
return out_path