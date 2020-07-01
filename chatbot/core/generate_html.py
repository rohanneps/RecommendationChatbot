import pandas as pd

import os
from django.conf import settings

def get_html_from_dataframe(df, query, output_file_path):
	df = df[settings.SERP_PRODUCT_CATALOG_HEADERS]
	HTML_START = 'Our Recommendation from various platforms for: {} '.format(query)+'''<style type="text/css">
	table.tableizer-table {
		font-size: 12px;
		border: 1px solid #CCC; 
		font-family: Arial, Helvetica, sans-serif;
	} 
	.tableizer-table td {
		padding: 4px;
		margin: 3px;
		border: 1px solid #CCC;
	}
	.tableizer-table th {
		background-color: #104E8B; 
		color: #FFF;
		font-weight: bold;
	}
	</style>'''
	ROW_COUNTER = 1

	def getHtmlBodyContent(row):
		nonlocal ROW_COUNTER,HTML_START
		table_row = '<tr><td><center>{}</center></td>'.format(ROW_COUNTER)
		
		for key in row.index.tolist():
			td = row[key]
			if key == 'Image':
				image_path = row['Image']
				product_url = row['Url']
				table_row += '<td><a href={}><center><img src={} height="50" width="50" /></center></a></td>'.format(product_url,image_path)
			else:
				if key !='Url':
					table_row += '<td><center>{}</center></td>'.format(td)

		table_row = table_row+'</tr>'

		HTML_START = HTML_START + table_row
		ROW_COUNTER += 1

	HTML_START +='<table class="tableizer-table"><thead><tr class="tableizer-firstrow">'
	# for columns
	HTML_START += '<th>S.N.</th>'
	
	for col in settings.SERP_PRODUCT_CATALOG_HEADERS:
		if col !='Url':
			col_header = '<th>{}</th>'.format(col)
			HTML_START += col_header

	HTML_START += '</tr></thead><tbody>'

	df.apply(getHtmlBodyContent, axis=1)
	HTML_START += '</tbody></table>'
	with open(output_file_path, 'w') as f:
		f.write(HTML_START)
