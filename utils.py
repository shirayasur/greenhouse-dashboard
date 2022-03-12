#!/usr/bin/env python
# coding: utf-8

# In[1]:


from grnhse import Harvest
import pandas as pd
import datetime
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
pd.options.mode.chained_assignment = None
from time import sleep


api_key = 'e9eccf15761fc48fd4cb3c592b089d31-4'
hvst = Harvest(api_key)

#Change this order according to your organization's recruitment pipeline
stages_order = {
    'Application Review' : 0,
    'Preliminary Phone Screen' : 1,
    'Codility Test': 2,
    'Phone Interview' : 3,
    'Face to Face' : 4,
    'Reference Check' : 5,
    'Offer' : 6
}


def create_cands_df():
    cands = hvst.candidates
    all_cands = cands.get()
    while cands.records_remaining:
        sleep(1.5)
        all_cands.extend(cands.get_next())
    df = pd.DataFrame(all_cands)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at'] = df.created_at.apply(lambda x: x.date())
    INTERESTING_COLUMNS = ['id', 'created_at', 'last_name', 'first_name']
    candidate_df = df[INTERESTING_COLUMNS]
    candidate_df.columns = ['candidate_id', 'created_at', 'last_name', 'first_name']    
    apps = hvst.applications
    all_apps = apps.get()
    
    while apps.records_remaining:
        sleep(1.5)
        all_apps.extend(apps.get_next())
    df = pd.DataFrame(all_apps)
    df['applied_at'] = pd.to_datetime(df['applied_at'],errors = 'coerce')
    df['applied_at'] = df.applied_at.apply(lambda x: x.date())
    df['rejected_at'] = pd.to_datetime(df['rejected_at'],errors = 'coerce')
    df['rejected_at'] = df.rejected_at.apply(lambda x: x.date())
    df['last_activity_at'] = pd.to_datetime(df['last_activity_at'],errors = 'coerce')
    df['last_activity_at'] = df.last_activity_at.apply(lambda x: x.date())
    df['rejection_status'] = df.rejection_reason.dropna().apply(lambda x: x['type']['name'])
    df['rejection_reason'] = df.rejection_reason.dropna().apply(lambda x: x['name'])
    df['source'] = df.source.dropna().apply(lambda x: x['public_name'])
    df['job'] = df.jobs.apply(lambda x: x[0]['name'] if len(x) > 0 else None)
    df['job_id'] = df.jobs.apply(lambda x: x[0]['id'] if len(x) > 0 else None)
    df['credited_to'] = df.credited_to.dropna().apply(lambda x: x["name"])
    df['current_stage'] = df.current_stage.dropna().apply(lambda x: x["name"])
    INTERESTING_COLUMNS = [
     'id',
     'candidate_id',
     'job',
     'job_id',
     'source',
     'status',
     'applied_at',
     'rejected_at',
     'last_activity_at',
     'rejection_status',
     'rejection_reason',
     'prospect',
     'current_stage',
     'credited_to'
    ]
    apps_df = df[INTERESTING_COLUMNS]
    cands_df = pd.merge(candidate_df, apps_df, on='candidate_id')
    return cands_df


# In[5]:
## Helper Function for Job df
def create_flat_jobs_df(raw_df):
    all_row = []
    #for each row of jobs df
    for ind,row in raw_df.iterrows():
        openings = row['openings']
        #create opening dict for each opening
        for opening in openings:
            row_dict = row.to_dict()
            opening2 = {}
            #rename opening columns for each key in opening_dict
            for k in opening.keys():
                opening2['opening_'+k] = opening[k]
            row_dict.update(opening2)
            all_row.append(row_dict)
    return pd.DataFrame(all_row)

def create_jobs_df():
    jobs = hvst.jobs
    all_jobs = jobs.get()
    while jobs.records_remaining:
        sleep(1.5)
        all_jobs.extend(jobs.get_next())
    raw_df = pd.DataFrame(all_jobs)
    df = create_flat_jobs_df(raw_df)
    df["department_name"] = df.departments.apply(lambda x: x[0]["name"])
    df["location"] = df.offices.apply(lambda x: x[0]["name"])
    df["employment_type"] = df.keyed_custom_fields.apply(lambda x: x['employment_type']['value'])
    INTERESTING_COLUMNS = ['id', 'opening_id','opening_opening_id', 'name','opening_status','opening_opened_at','opening_closed_at','department_name','location']
    jobs_df = df[INTERESTING_COLUMNS]
    jobs_df.columns = ['job_id','opening_id_backup','opening_id','name','job_status','opened_at','closed_at','department_name','location']
    jobs_df['opened_at'] = pd.to_datetime(jobs_df['opened_at'])
    jobs_df['closed_at'] = pd.to_datetime(jobs_df['closed_at'])
    jobs_df['opened_at'] = jobs_df.opened_at.apply(lambda x: x.date())
    jobs_df['closed_at'] = jobs_df.closed_at.apply(lambda x: x.date())
    return jobs_df


#############################
#Filled Roles - Hiring Speed#
#############################

def create_hiring_speed_df(jobs_df):
# Takes jobs_df and returns how many days each job was open 
# Used in 'Filled Roles - Hiring Speed' tab (both table and averages graph)
    df = jobs_df[(jobs_df.job_status == 'closed')]
    df['days_open'] = (df.closed_at - df.opened_at)
    df["days_open"] = df.days_open.apply(lambda x: x.days)
    df = df[['name', 'department_name', 'opened_at', 'closed_at', 'days_open', 'location']]
    return df


def create_speed_by_dep(speed_df, value):
# Takes department as user input and returns hiring speed by department
# Used in 'Filled Roles - Hiring Speed' tab for dropdown table  
    df = speed_df[(speed_df.department_name==value)]
    return df

def create_hiring_average_dep_graph(hiring_speed_df):
# Takes hiring speed df and returns graph of the average hiring speed per department
# Used in 'Filled Roles - Hiring Speed' tab 
    hiring_average_dep = hiring_speed_df.groupby('department_name').mean('days_open').reset_index()
    fig = px.bar(hiring_average_dep, x='department_name', y='days_open', labels={
                     "department_name": "Department Name",
                     "days_open": "Days Open"},title=f'Average Hiring Speed Time by Department')
    fig.update_traces(marker_color='mediumturquoise')
    return fig

def create_hiring_average_loc_graph(hiring_speed_df):
# Takes hiring speed df and returns graph of the average hiring speed per location
# Used in 'Filled Roles - Hiring Speed' tab 
    hiring_average_loc = hiring_speed_df.groupby('location').mean('days_open').reset_index()
    fig = px.bar(hiring_average_loc, x='location', y='days_open', labels={
                     "location": "Location",
                     "days_open": "Days Open"}, title='Average Hiring Speed Time by Location')
    fig.update_traces(marker_color='darkorange')
    return fig


############
#Open Roles#
############


def create_tth_df(jobs_df):
# Takes jobs_df and returns df of open roles and how long they've been open
# Used in 'Open Roles' tab and used to create all tables and graphs 
    df = jobs_df[(jobs_df.job_status == 'open')]
    df['days_open'] = (datetime.now().date() - df.opened_at)
    df["days_open"] = df.days_open.apply(lambda x: x.days)
    df = df[['name','department_name','opened_at','days_open','location']]
    return df

def create_tth_by_dep(tth_df, value):
# Takes open roles df (tth) and department name and returns df per department
    df = tth_df[(tth_df.department_name==value)]
    return df

def create_tth_average_dep_graph(tth_df):
# Takes open roles df and returns graph of total open days by department
    hiring_average_dep = tth_df.groupby('department_name').mean('days_open').reset_index()
    fig = px.bar(hiring_average_dep, x='department_name', y='days_open', labels={
                     "department_name": "Department Name",
                     "days_open": "Days Open"}, title='Average Duration of Open Roles by Department')
    fig.update_traces(marker_color='mediumturquoise')
    return fig

def create_tth_average_loc_graph(tth_df):
# Takes open roles df and returns graph of total open days by location  
    hiring_average_loc = tth_df.groupby('location').mean('days_open').reset_index()
    fig = px.bar(hiring_average_loc, x='location', y='days_open', labels={
                     "location": "Location",
                     "days_open": "Days Open"}, title='Average Duration of Open Roles by Location')
    fig.update_traces(marker_color='darkorange')
    return fig

###########################
#Candidates' Current Stage#
###########################


def create_ccs_df(jobs_df, cands_df):
# Takes jobs df and cands df and returns df of current candidate stage
# Used for all tables and graphs in this tab
    job_dup_df = jobs_df.drop_duplicates(subset ="job_id")
    df = cands_df.merge(job_dup_df, on='job_id', how='left')
    df = df[df.status=='active']
    df = df[df.prospect==False]
    df = df[['last_name','first_name','job', 'current_stage','department_name','location']]
    return df

def sort_stage(x):
# Helper function used to sort candidate stage according to pipeline
    if x in stages_order:
        return stages_order[x]
    else:
        return 2

def create_ccs_by_dep(ccs_df, value):
#takes candidate df and department name and returns df of candidate stage by department
    df = ccs_df[(ccs_df.department_name==value)]
    df['sort'] = df.current_stage.apply(sort_stage)
    df = df.sort_values(['sort','current_stage','job','last_name'])
    return df

def create_ccs_graph(ccs_df,value):
# Takes candidate df and department name, and returns graph of amount of cands in each department
    ccs_by_dep = create_ccs_by_dep(ccs_df, value)
    ccs_by_stage = ccs_by_dep.groupby(['current_stage','sort']).count()[['last_name']].reset_index()
    ccs_by_stage = ccs_by_stage.sort_values(['sort','current_stage'])
    fig = px.bar(ccs_by_stage, x='current_stage', y='last_name', labels={
                     "current_stage": "Current Stage",
                     "last_name": "Amount of Applicants"}, title='Amount of Candidates in Each Stage')
    fig.update_traces(marker_color='darkorange')
    return fig

################################
#Recruitment Sources Statistics#
################################

def create_color_dictionary(cands_df):
# Helper function which takes candidate df and assigns each source a color for consistency
# Add more colors for more sources
    color_list = ['mediumturquoise', 'darkorange', 'lightgreen', 'aliceblue', 'gold', 'Cornflower Blue', 'aquamarine', 'cyan', 'crimson', 'darkred', 'darksalmon', 'fuchsia','forestgreen', 'mediumorchid', 'powderblue', 'olive', 'moccasin', 'hotpink', '#DC143C', 'Heliotrope', 'yellowgreen', 'violet', 'peachpuff']
    cands_df = cands_df[cands_df.prospect==False]
    source_df = cands_df[['source']]
    sources_count = source_df.source.value_counts()
    sources = sources_count.index.tolist()
    color_map_dict = {'Other Sources':color_list.pop()}
    for i in range(len(sources)):
        source = sources[i]
        color = color_list[i%len(color_list)]
        color_map_dict[source] = color
    return color_map_dict

def create_sources_graph(cands_df, SOURCES_COLOR_MAP):
#Takes cands df and colors dictionary and returns pie chart of *only hired* sources
    cands_df = cands_df[cands_df.prospect==False]
    source_hired_df = cands_df[(cands_df.status=='hired')][['source']]
    hired_counts = source_hired_df.source.value_counts()
    hired_counts_df = pd.DataFrame(hired_counts)
    names = hired_counts_df.index.tolist()
    values = hired_counts_df.source.tolist()
    color_list = []
    for name in names:
        if name in SOURCES_COLOR_MAP:
            color_list.append(SOURCES_COLOR_MAP[name])
    fig = go.Figure(data=[go.Pie(labels=names, values=values, hole=.4)])
    fig.update_layout(title_text="Sources of Hired Employees")
    fig.update_traces(marker=dict(colors=color_list))
    return fig

def create_all_sources_graph(cands_df, SOURCES_COLOR_MAP):
#Takes cands df and colors dictionary and returns pie chart of *all* sources
    cands_df = cands_df[cands_df.prospect==False]
    source_df = cands_df[['source']]
    sources_count = source_df.source.value_counts()
    bottom_counts = source_df.source.value_counts()[7:].sum()
    top_counts = source_df.source.value_counts()[:7]
    top_counts.loc['Other Sources'] = bottom_counts
    index_list = top_counts.index.tolist()
    counts_list = top_counts.tolist()
    color_list = []
    for name in index_list:
        if name in SOURCES_COLOR_MAP:
            color_list.append(SOURCES_COLOR_MAP[name])
    fig = go.Figure(data=[go.Pie(labels=index_list, values=counts_list, hole=.4)])
    fig.update_layout(title_text="Top Sources of all Candidates")
    fig.update_traces(marker=dict(colors=color_list))
    return fig

def quarter_func(x):
# Helper function that defines Quarters
    if x.month in [1,2,3]:
        return ('Q1')
    elif x.month in [4,5,6]:
        return ('Q2')
    elif x.month in [7,8,9]:
        return ('Q3')
    else:
        return ('Q4')

def create_source_quarterly(cands_df):
#Takes candidates df and returns df of candidates *hired* by quarters
    cands_df = cands_df[cands_df.prospect==False]
    cands_df['created_at'] = pd.to_datetime(cands_df['created_at'])
    cands_df = cands_df.set_index('created_at')
    total_sources = cands_df.groupby([cands_df.source, pd.Grouper(freq='M')])['candidate_id'].count()
    hired_df = cands_df[cands_df.status=='hired']
    hired_sources = hired_df.groupby([hired_df.source, pd.Grouper(freq='M')])['candidate_id'].count()
    total_df = pd.DataFrame(total_sources)
    hired_df = pd.DataFrame(hired_sources)
    source_by_m = total_df.join(hired_df, how='left', lsuffix='total', rsuffix='hired').fillna(0)
    source_m = source_by_m.reset_index()
    source_m.columns=['Source','Date','Total','Hired']
    source_m['Quarter'] = source_m.Date.apply(quarter_func)
    source_m['Year'] = source_m.Date.apply(lambda x: x.year)
    source_by_m = source_m.groupby(['Source','Quarter','Year']).sum()
    source_by_m['Percentage'] = source_by_m.Hired/source_by_m.Total*100
    source_by_m = source_by_m.reset_index()
    return source_by_m

def create_total_cands_graph(quarterly_df, source, year):
#Takes quarterly df, source name and year, and returns graph of how many cands were brought in 
    df = quarterly_df.copy()
    df = df[(df.Source == source) & (df.Year == year)]
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    df_qlist = df.Quarter.unique()
    for q in quarters:
        if q not in df_qlist:
            q_dict = {'Source': source, 'Quarter': q, 'Year': year, 'Total': 0, 'Hired': 0, 'Percentage': 0}
            df = df.append(q_dict, ignore_index=True)
    df = df.sort_values('Quarter')
    fig = px.bar(df, x='Quarter', y='Total', title=f'Total Candidates Brought by {source} in {year}')
    fig.update_traces(marker_color='mediumturquoise')
    return fig

def create_hired_cands_graph(quarterly_df, source, year):
#Takes quarterly df, source name and year, and returns graph of how many *hired* cands were brought in 
    df = quarterly_df.copy()
    df = df[(df.Source == source) & (df.Year == year)]
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    df_qlist = df.Quarter.unique()
    for q in quarters:
        if q not in df_qlist:
            q_dict = {'Source': source, 'Quarter': q, 'Year': year, 'Total': 0, 'Hired': 0, 'Percentage': 0}
            df = df.append(q_dict, ignore_index=True)
    df = df.sort_values('Quarter')
    fig = px.bar(df, x='Quarter', y='Hired', title=f'Hired Candidates Brought by {source} in {year}')
    fig.update_traces(marker_color='darkorange')
    return fig

#############################
#Dashboard general dropdowns#
#############################

def get_dropdown_dep(df):
    dep_names = df.department_name.unique().tolist()
    dep_names.sort()
    dropdown_list=[]
    for name in dep_names:
        dropdown_list.append({'label': name, 'value' : name})
    return dropdown_list

def get_dropdown_org(df):
    org_names = df.organization.unique().tolist()
    org_names.sort()
    dropdown_list=[]
    for name in org_names:
        dropdown_list.append({'label': name, 'value' : name})
    return dropdown_list

def get_dropdown_sources(df):
    source_names = df.Source.unique().tolist()
    source_names.sort()
    dropdown_list=[]
    for source in source_names:
        dropdown_list.append({'label': source, 'value' : source})
    return dropdown_list

def get_dropdown_year(df):
    years = df.Year.unique().tolist()
    years.sort()
    dropdown_list=[]
    for year in years:
        dropdown_list.append({'label': year, 'value' : year})
    return dropdown_list