"""
Contains function to convert dataframe to recommendation HTML page response.
"""

import pandas as pd

from django.conf import settings


def get_html_from_dataframe(
    catalog_df: pd.DataFrame, query: str, output_file_path: str
) -> None:
    """
    Generate html page using the catalog vs query comparison

    Args:
    -----
            None
    Returns:
    --------
            None
    """

    catalog_df = catalog_df[settings.SERP_PRODUCT_CATALOG_HEADERS]
    html_start_str = (
        f"Our Recommendation from various platforms for: {query} "
        + """<style type="text/css">
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
	</style>"""
    )

    row_counter = 1

    def get_html_table_row_content(row: pd.Series) -> None:
        """
        Add each catalog dataframe row to the HTML table td element

        Args:
        -----
                row (pd.Series): dataframe row
        Returns:
        --------
                None
        """
        nonlocal row_counter, html_start_str
        table_row = f"<tr><td><center>{row_counter}</center></td>"

        for key in row.index.tolist():
            row_data = row[key]
            if key == "Image":
                image_path = row["Image"]
                product_url = row["Url"]
                table_row += f'<td><a href={product_url}><center><img src={image_path} \
                				height="50" width="50" /></center></a></td>'
            else:
                if key != "Url":
                    table_row += f"<td><center>{row_data}</center></td>"

        table_row = table_row + "</tr>"

        html_start_str = html_start_str + table_row
        row_counter += 1

    html_start_str += (
        '<table class="tableizer-table"><thead><tr class="tableizer-firstrow">'
    )
    # for columns
    html_start_str += "<th>S.N.</th>"

    for col in settings.SERP_PRODUCT_CATALOG_HEADERS:
        if col != "Url":
            col_header = f"<th>{col}</th>"
            html_start_str += col_header

    html_start_str += "</tr></thead><tbody>"

    catalog_df.apply(get_html_table_row_content, axis=1)
    html_start_str += "</tbody></table>"
    with open(output_file_path, "w") as f_out:
        f_out.write(html_start_str)
