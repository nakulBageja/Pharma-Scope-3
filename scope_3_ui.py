import pandas as pd
import streamlit as st
import plotly.express as px
# import pdfkit

st.set_page_config(page_title="ZedAI",
                   page_icon="🧊",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Define function to download report
# def download_report(fig1, fig2, fig3, fig4):
#     with st.beta_container():
#             st.markdown('---')
#             st.markdown('## Download Report')
#             st.markdown('Download a PDF report containing the graphs.')
#             download = st.button('Download PDF')
#             if download:
#                 # Create a HTML file containing the title and graphs
#                 html = f"""
#                 <html>
#                 <head><title>Pharma Company's Transportation Emissions in 2012</title></head>
#                 <body>
#                     <h1>Pharma Company's Transportation Emissions in 2012</h1>
#                     <h2>Top 10 Customers with highest emissions</h2>
#                     {fig1.to_html()}
#                     <h2>Distribution of Emissions per Mode of Transport</h2>
#                     {fig2.to_html()}
#                     <h2>Emissions per Month by each Mode of Transport</h2>
#                     {fig3.to_html()}
#                     <h2>Top 10 Manufacturing Sites with highest emissions</h2>
#                     {fig4.to_html()}
#                 </body>
#                 </html>
#                 """

#                 # Convert the HTML file to a PDF file and download it
#                 pdfkit.from_string(html, 'report.pdf')
#                 with open('report.pdf', 'rb') as f:
#                     pdf_data = f.read()
#                 st.download_button('Download PDF', pdf_data, 'report.pdf')


def generate_graphs(data):
    """
    This function generates the graph once the file is uploaded
    """
    st.title("Pharma Company's Transportation Emissions in 2012")

    # Set the page layout
    col1, col2 = st.columns(
        2,
        gap="large",
    )
    # Load the data
    df = data

    # Convert date column to datetime format
    df['Delivery_Date'] = pd.to_datetime(df['Delivery_Date'],
                                         format="%d-%m-%Y")

    # Group the data by customer and get the sum of emissions for each customer
    grouped_customer = df.groupby('Destination_Country')[
        'total_emissions'].sum().reset_index().sort_values(
            by='total_emissions', ascending=False).head(10)

    # Group the data by month and mode and get the sum of emissions for each combination
    # Define the order of the months
    month_order = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]
    df['Month'] = df['Delivery_Date'].dt.month_name()
    df['Month'] = pd.Categorical(df['Month'],
                                 categories=month_order,
                                 ordered=True)
    grouped_month_mode = df.groupby(['Month', 'Mode'
                                     ])['total_emissions'].sum().reset_index()

    # Group the data by manufacturing site and get the sum of emissions for each site
    grouped_site = df.groupby('Manufacturing_site')['total_emissions'].sum(
    ).reset_index().sort_values(by='total_emissions', ascending=False).head(10)

    with col1:
        # Bar chart for top 10 customers with highest emissions
        st.header("Top 10 Customers with highest emissions")
        fig1 = px.bar(grouped_customer,
                      x="Destination_Country",
                      y="total_emissions",
                      labels={
                          "Destination_Country": "Customers",
                          "total_emissions": "Emissions (Metric Tons CO2e)"
                      })
        st.plotly_chart(fig1)

        # Vertical bar chart for emissions per month by each mode of transport
        st.header("Emissions per Month by each Mode of Transport")
        fig3 = px.bar(
            grouped_month_mode,
            x="Month",
            y="total_emissions",
            color='Mode',
            barmode='group',
            labels={"total_emissions": "Emissions (Metric Tons CO2e)"},
            height=400,
            width=650)
        fig3.update_layout(legend=dict(x=0, y=1, orientation="v"))
        st.plotly_chart(fig3)

    with col2:
        # Pie chart for distribution of emissions per mode of transport
        st.header("Distribution of Emissions per Mode of Transport")
        grouped_mode = df.groupby(
            'Mode')['total_emissions'].sum().reset_index()
        fig2 = px.pie(grouped_mode, values='total_emissions', names='Mode')
        fig2.update_layout(legend=dict(x=0, y=1, orientation="v"))
        st.plotly_chart(fig2)

        # Vertical bar chart for top 10 manufacturing sites with highest emissions
        st.header("Top 10 Manufacturing Sites with highest emissions")
        fig4 = px.bar(
            grouped_site,
            x="Manufacturing_site",
            y="total_emissions",
            labels={"total_emissions": "Emissions (Metric Tons CO2e)"})
        st.plotly_chart(fig4)

        return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    st.title("Carbon Accounting & Reporting")
    st.write("Please upload your CSV file below:")

    # Upload the file
    file = st.file_uploader("Choose a file", type=["csv"])

    # If the user uploaded a file
    if file is not None:
        # Read the data
        data = pd.read_csv(file)

        # Generate the graphs
        fig1, fig2, fig3, fig4 = generate_graphs(data)
