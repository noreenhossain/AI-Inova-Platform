# Importing necessary libraries
import streamlit as st
import openai
from PyPDF2 import PdfReader
import docx2txt
import pandas as pd
import plotly as Plotly
import plotly.express as px
from datetime import datetime
from pytz import timezone
import numpy as np


# import clipman 
# import pyclip
# import pyperclip

# broadcasting and set host for streamlit app 
st.set_page_config(layout="wide")

# get api key from gitignored api_key file
def get_file_contents(filename):
    """ Given a filename,
        return the contents of that file
    """
    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)


# Method to process uploaded PDFs
def read_pdf(file):
	pdfReader = PdfReader(file)
	count = len(pdfReader.pages)
	all_page_text = ""
	for i in range(count):
		page = pdfReader.pages[i]
		all_page_text += page.extract_text()

	return all_page_text

# Home page that the tool allows user to pick which tool they want to use
def main_page():
     st.header("Please select which tool you would like to use using the dropdown to the left!", anchor=False)
     st.caption("Descriptions of each tool are listed below:")
     st.subheader('GPT Summarizer', anchor=False)
     st.write("The **GPT Summarizer** allows you to upload a deck or other text and receive a summary of the text using a preset prompt. The prompt can be adjusted, and the summary is generated using an OpenAI GPT model!")
     with st.expander("Click here to get the instructions for use of the GPT Summarizer"):
            st.write("[Link to documentation!](https://cerevel-my.sharepoint.com/:w:/p/noreen_hossain/EQ42gF8fpGlLq_vYxsCVJqsBwXFLgtMpBIFvM-0kFl7QOQ?e=KfJs7Q)")
     st.subheader('Inova Dashboard', anchor=False)
     st.write("The **Inova Dashboard** allows you to upload exported data from Inova, and produces a series of visualizations describing the data. The data is also listed at the end, for ease of understanding.")
     
# Page for GPT summarizer tool
def summarizer():

    # Main page with 3 rows and 2 columns
    st.title("Search and Evaluation GPT Deck Summarizer")

    # OpenAI API Key
    openai.api_key = get_file_contents("api_key")


    # Default prompt text that can be modified in Streamlit window
    prompt_text = """Please provide the name of the key asset described in the text in the format "Name of Asset (Name of Company)". Next, describe the key asset in two paragraphs, including key information about the stage it is in, and any future milestones mentioned. Next, describe how it compares to similar assets that exist. Next, repeat description for all other assets mentioned in the text. Finally, print "Summary Complete" """
    # gpt_model = "gpt-4"


    # Setting up the document
    document_text = ""

    # Add a file uploader
    docx_file = st.file_uploader("Upload File",type=['txt','docx', 'pdf'])

    # Checks the uploaded file and stores information about it
    if docx_file is not None:
        file_details = {"Filename":docx_file.name,"FileType":docx_file.type,"FileSize":docx_file.size}
        # Confirmation that file was uploaded successfully if file details written
        st.write(file_details)
        # Check File Type
        # TXT
        if docx_file.type == "text/plain":
            st.text(str(docx_file.read(),"utf-8")) # empty
            document_text = str(docx_file.read(),"utf-8") # works with st.text and st.write,used for futher processing
        # PDF
        elif docx_file.type == "application/pdf":
            document_text = read_pdf(docx_file) 
        # DOCX
        elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Use the right file processor ( Docx,Docx2Text,etc)
            document_text = docx2txt.process(docx_file) # Parse in the uploadFile Class directory
            # st.text(type(document_text))

    # Make Columns for Propmpt box and summary box
    col1_1, col1_2 = st.columns([2, 3])

    # Prompt Box
    with col1_1:
        with st.expander("Prompt", expanded=True):
                prompt_box = st.text_area("Here is the prompt to summarize a deck. Feel free to adjust the prompt if needed.", height = 300, key = "prompt_box", value=prompt_text)

        # method to reset prompt when button is pressed
        def reset_prompt():
            st.session_state.prompt_box = prompt_text

        st.button("Reset Prompt Text", on_click = reset_prompt)

        # select which gpt model will be used to summarize text
        gpt_model = st.selectbox(
        'Which GPT Model do you want to use?',
        ("gpt-4", 'gpt-3.5-turbo-16k'))


    # Generated Summary Box
    with col1_2:
        # Box for generated summary
        output = ""
        a = st.text_area(f"GPT Summary of Deck using the {gpt_model} model",
            output,
            height=500,
            key="output_text",
            placeholder="Please click \'Get GPT Summary\' to generate summary")

        # Function to generate GPT Response using prompt and document
        def on_gpt_indication_click():
            response = openai.ChatCompletion.create(
                model= gpt_model,
                messages=[{"role": "user", "content": f"{prompt_box}: {document_text}"}],
                temperature=0,
                # max_tokens=500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            # return response['choices'][0]['message']['content']
            st.session_state.output_text = response['choices'][0]['message']['content']

        # Function to clear text box
        def clear_box():
            st.session_state.output_text = output

        # Make action buttons
        summary, clear = st.columns([1,1])

        # Get GPT summary and replace output with generated response
        with summary:
            st.button("Get GPT Summary", key="get_gpt_button", on_click=on_gpt_indication_click)
            
        # Clear the text in the output box
        with clear:
            if st.button("Clear Output", on_click = clear_box):
                del st.session_state.output_text
                st.session_state.output_text = "Blank"
        # Copy the text in the output box
        # Pyperclip not working with Linux!!
        # with copy:
        #     if st.button('Copy Summary Text'):
        #         # clipman.init()
        #         # clipman.copy(a)
        #         # copy_clipboard(a)
        #         pyperclip.copy(a)
        #         # clipboard.copy(a)

        #         st.success('Text copied successfully!')



# function to produce pie visualizations within the dashboard page
def pie_visualization(inova_df, filtered_by, colorway=px.colors.sequential.Aggrnyl):
    # Group the assets we want to look at 
    assets_by = inova_df.groupby([filtered_by], dropna = True).count().reset_index()
    # Plot those assets in a pie chart
    fig = px.pie(assets_by, values=assets_by["Company"], names=assets_by[filtered_by], title=f'Assets by {filtered_by}', hole=.3, color_discrete_sequence=colorway)
    fig.update_traces(textposition='inside', 
                     text=assets_by["Company"],
                     textinfo='text', textfont_size=22)
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    font=dict(size=14)
    ))
    fig.update_layout(height = 750)
    # Plotly.react(gd, data, layout, {toImageButtonOptions: {width: null, height: null}
# })
    return fig

# Function to save filtered dataframes
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


# Create page for the Inova Visualization Dashboards
def dashboard():
    # Title and subtitle
    st.header("Inova Dashboard", anchor=False)
    st.write("Here is a visual dashboard of the data stored in the Inova ")
    # File Uploader
    docx_file = st.file_uploader("Upload File",type=['xls'])
    st.subheader("Please upload exported data to produce visualizations!", anchor=False)
    st.caption("Note: Visualizations can all be expanded and filtered. You can also save the view of a graph as a PNG.")
    
    # Create empty df as a placeholder
    inova_data_df = pd.DataFrame()

    # File reader
    # Read the exported Inova Data into a a dataframe, then used for generating visualizations
    if docx_file is not None:
        st.divider()
        inova_data = pd.read_html(docx_file)
        inova_data_df = inova_data[2]
        
        # Visualizations

        # Set the colors for all graph
        colorway = px.colors.sequential.Aggrnyl

        # Assets by Status dropdowns
        st.header("Number of Assets by Status", anchor=False)
        st.caption("Click on the expanders to view the asset information.")
        status_df = inova_data_df.groupby(["Status"], dropna = True).count().reset_index()[["Status", "Company"]]
        ncol = len(status_df)
        cols = st.columns(ncol)

        # For each status that exists, create a dropdown and list the assets that have that status
        for i, x in enumerate(cols):
            status = status_df.iloc[i][0]
            num = status_df.iloc[i][1]
            with x.expander(f"{status}: {num}"):
                assets_df = inova_data_df.loc[inova_data_df["Status"] == status]
                assets_csv = convert_df(assets_df)
                # tz = timezone('EST')
                file_name=f'{status}_{datetime.now().strftime("%m/%d/%Y %H:%M")}.csv'
                st.text(file_name)
                st.download_button(
                        label=f"Download {status} assets list as CSV",
                        data=assets_csv,
                        file_name=f'{status}_{datetime.now().strftime("%m/%d/%Y")}.csv',
                        mime='text/csv',
                )
                st.dataframe(assets_df)
                
        st.divider()

        # Pie charts start here

        st.header("Pie Charts", anchor=False)

        # The columns were part of old view, with 2 visualizations per row
        # They now are listed one after another 
        # by_indication, by_secondary_indication = st.columns([1,1])
        # with by_indication:
        st.subheader("Assets by Indication", anchor=False)
        fig_ind = pie_visualization(inova_data_df, "Primary Indication")
        st.plotly_chart(fig_ind,  use_container_width=True)
        # st.button(fig_ind.write_image("contour2.png"))
        # with by_secondary_indication:
        st.subheader("Assets by Secondary indication", anchor=False)
        st.plotly_chart(pie_visualization(inova_data_df, "Secondary Indication"),  use_container_width=True)

        # by_moa, by_modality= st.columns([1,1])
        # with by_moa:
        st.subheader("Assets by Mechanism of Action", anchor=False)           
        st.plotly_chart(pie_visualization(inova_data_df, "Mechanism of Action"),  use_container_width=True)

        # with by_modality:
        st.subheader("Assets by Modality", anchor=False)
        st.plotly_chart(pie_visualization(inova_data_df, "Modality"),  use_container_width=True)


       # "Custom" pie chart, filtered by any column in the data df
        attribute = st.selectbox("Select value to produce 'Assets by _____' visualization.", (inova_data_df.loc[:, ~inova_data_df.columns.isin(['Name', 'Company', 'Last Modified On', 'Created On'])]).columns)  
        st.plotly_chart(pie_visualization(inova_data_df, attribute), use_container_width=True)


        # Bar Charts begin
        st.divider()
        st.header("Bar Charts", anchor=False)


        # Bar chart showing number of assets per indication, broken down further by their modality
        indication_modality = inova_data_df.groupby(["Primary Indication", "Modality"], dropna = True).count().reset_index()
        indication_modality_fig = px.bar(indication_modality, x="Primary Indication", y="Company", color="Modality", title="Assets by Primary Indication and Modality", height = 900, color_discrete_sequence=colorway, labels={'Primary Indication': 'Primary Indication', 'Company':'Number of Assets'})
        indication_modality_fig.update_layout(legend=dict(
            font=dict(size= 12)
            ))
        st.plotly_chart(indication_modality_fig, use_container_width=True)
        
        # Bar chart showing number of assets per development phase, broken down further by their indication
        indication_stage = inova_data_df.groupby(["Highest Development Phase","Primary Indication"], dropna = True).count().reset_index()
        indication_stage_fig = px.bar(indication_stage, x="Highest Development Phase", y="Company", color="Primary Indication", title="Assets by Development Phase and Indication", height=900, color_discrete_sequence=colorway, labels={'Highest Development Phase': 'Development Phase', 'Company':'Number of Assets'})
        indication_stage_fig.update_layout(legend=dict(
            font=dict(size= 12)
            ))
        # change the order of the column labels    
        indication_stage_fig.update_xaxes(categoryorder='array', categoryarray= ["Discovery", "Research Tool", "Hit Finding", "Hit to Lead", "Lead to Candidate", "Preclinical/IND-Stage", "Clinical", "Phase 1 Clinical", "Phase 2 Clinical", "Phase 3 Clinical", "Approved"])
        st.plotly_chart(indication_stage_fig, use_container_width=True)


        # Dot plot of assets 
        st.divider()

        # Set title as default
        graph_title = f"Creation Date, Status, and Development Phase of All Assets"

        # Filling null values so they graph properly
        inova_data_df = inova_data_df.replace(np.nan, None)
        inova_data_df["Highest Development Phase"] = inova_data_df["Highest Development Phase"].fillna('None Listed')

        # Make copy of the original df
        df_filtered_subset = inova_data_df

        # Set placeholder for filtering 
        subset_filter = ""

        # Create the two filters for data used to make graph
        column_filter, value_filter= st.columns([1,1])

        # initial filter based on columns of data
        with column_filter:
            columns_list = list(inova_data_df.columns)
            # add option to show every asset
            columns_list.insert(0, "Show All Assets")
            # Let user pick which column to filter by
            column = st.selectbox("Select which column you want to filter by", columns_list)
        # If user picks a more specific filter
        if column != "Show All Assets":
            # Set filters for data to be more specific, change the graph title, and filter the df
            with value_filter:
                subset_filter = st.selectbox(f"Select which {column} you want to filter by.", (list(inova_data_df[column].unique())))
                graph_title = f"Creation Date, Status, and Development Phase of {column}: {subset_filter} Assets"
                df_filtered_subset = inova_data_df.loc[inova_data_df[column]==subset_filter]

        # Clean the filtered df to make graph more informative
        df_filtered_subset["Asset Discovery Date"] = pd.to_datetime(df_filtered_subset["Asset Discovery Date"])
        df_filtered_subset["Last Modified On"] = pd.to_datetime(df_filtered_subset["Last Modified On"])
        df_filtered_subset["Highest Development Phase"] = df_filtered_subset["Highest Development Phase"].fillna('None Listed')
        df_filtered_subset["Modality"] = df_filtered_subset["Modality"].fillna('None Listed')

        # Graph the scatterplot with the appropriately filtered data
        filtered_graph= px.scatter(df_filtered_subset, x="Asset Discovery Date", y="Status", color = "Highest Development Phase", title=graph_title, color_discrete_sequence=px.colors.qualitative.Prism, hover_data=['Name', 'Status', 'Modality', 'Highest Development Phase'])
        # filtered_graph.add_vline()

        # Show the plot after filtering 
        st.plotly_chart(filtered_graph, use_container_width=True)
        # Show filtered df
        with st.expander(f"Click here to view assets by the selected filter: {column} {subset_filter}"):
            st.dataframe(df_filtered_subset)

        # Show df of all data from original df
        st.divider()
        with st.expander("Click here to view the uploaded raw data"):
            st.dataframe(inova_data_df)
        


# Pages of the platform
# Functions are run when page is selected, displaying all the code within each function
page_names_to_funcs = {
    "Home": main_page,
    "GPT Summarizer": summarizer,
    "Inova Data Dashboard": dashboard
}

# Dropdown to select which page you want displayed
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()

