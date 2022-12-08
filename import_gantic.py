import pandas as pd 
import datetime
import numpy as np
from process_data import get_unique_names
import plotly.express as px

def name2fullname(name, list_fullnames):
    first_names = [n.split()[0] for n in list_fullnames]
    special_cases = {
        'PabloR': 'Pablo Rodriguez-Sanchez',
        'PabloL': 'Pablo Lopez-Tarifa',
        'PeterKal': 'Peter Kalvera',
        'PeterKok': 'Peter Kok'
    }
    if name in special_cases:
        return special_cases[name]
    else:
        if name in first_names:
            return list_fullnames[first_names.index(name)]
        else:
            return name


def fullname2name(fullname, list_names):
    first_name = fullname.split()[0]
    special_cases = {
        'Pablo Rordriguez-Sanchez': 'PabloR',
        'Pablo Lopez-Tarifa': 'PabloL',
        'Peter Kalvera': 'PeterKal',
        'Peter Kok': 'PeterKok'
    }
    if fullname in special_cases:
        return special_cases[n]
    else:
        return list_names(list_names.index(first_name))

def gantic2pandas(filename):

    data = [line for line in open(filename) if "Resource" not in line]
    clean_data = []
    for line in data:
        line = line.split(',')
        line = [ word.strip("\"") if isinstance(word,str) else word for word in line[:-2]] 
        clean_data.append(line)

    col_names = ['Employee', 'Project', 'Project Numbner', 'Type', 'Start Date', 'End Date', 'number of tasks', 'Duration', 'Quantity']    

    return pd.DataFrame(clean_data, columns=col_names)

def date2week(date:str):
    week =  int(datetime.date(*tuple(int(x) for x in date.split('-'))).strftime('%W'))
    year = int(date.split('-')[0])
    return year, week

def date2date(date:str):
    return datetime.date(*tuple(int(x) for x in date.split('-')))

def create_weekly_tasks(df):
    names = get_unique_names(df,'Employee')
    weekly_tasks = []
    for name in names:

        data = df[df['Employee']==name].values.tolist()
        
        for task in data:
            project = task[1]
            project_number = task[2]
            total_hours = float(task[8].split(":")[0])
            start_date, end_date = task[4], task[5]
            year_start, week_start = date2week(start_date) 
            year_end, week_end = date2week(end_date)

            if year_end != year_start:
                week_end += (year_end-year_start)*52

            number_weeks = (week_end - week_start + 1 )
            weekly_hours = total_hours/number_weeks
            for w in range(week_start, week_end+1):
                weekly_tasks.append([ name, w, project, project_number, weekly_hours])

    colnames=['Employee', 'Week', 'Project', 'Projet Number', 'Quantity']
    df = pd.DataFrame(weekly_tasks, columns=colnames)
    return df.sort_values(by=['Employee','Week'])


def create_cummulative_project_timeline_project(gantic_weekly_tasks, exact_df, project_name, cummulative_planning):

    df_planning = gantic_weekly_tasks[gantic_weekly_tasks['Project']==project_name]
    total_cumsum_planning = df_planning.groupby(['Week']).sum().cumsum()['Quantity']
    total_sum_planning = df_planning.groupby(['Week']).sum()['Quantity']
    df_planning['Employee_cumsum'] = df_planning.groupby(['Employee'])['Quantity'].cumsum()

    eng_name_list = get_unique_names(exact_df, 'Employee')
    
    week_planning = []
    employee_planning = []
    hours_planning = []
    planning_dict = dict()
    for item in df_planning.values.tolist():
        _employee, _week, _, _, _hours, _cumsum = item
        _employee = name2fullname(_employee, eng_name_list)
        if _employee not in planning_dict:
            planning_dict[_employee] = dict()
        planning_dict[_employee][_week] = _hours 

    planning_dict['Total'] = dict() 
    for w, h in zip(total_sum_planning.index.tolist(), total_sum_planning.values.tolist()):
        planning_dict['Total'][w] = h 

    val_week = np.sort(list(set(week_planning)))
    text_week = [str(w)[4:]+'-'+str(w)[:4] for w in val_week]
    
    df_written = exact_df[exact_df['Project']==project_name].groupby([exact_df['Date'].dt.strftime('%W'),'Employee']).sum()
    df_written.sort_values(by=['Employee','Date'])
    total_cumsum_written = df_written.groupby(['Date']).sum().cumsum()['Quantity']
    total_sum_written = df_written.groupby(['Date']).sum()['Quantity']
    df_written['Employee_cumsum'] = df_written.groupby(['Employee'])['Quantity'].cumsum()

    written_dict = dict()
    for key, value in zip(df_written.index.tolist(), df_written.values.tolist()):
        _week, _employee = key 
        _week = int(_week)
        _, _hour, _, _, _cumsum = value
        
        if _employee not in written_dict:
            written_dict[_employee] = dict() 
        written_dict[_employee][_week] = _hour

    written_dict['Total'] = dict() 
    for w,h in zip(total_sum_written.index.tolist(), total_sum_written.values.tolist()):
        written_dict['Total'][w] = h 

    diff_dict = dict()
    for emp, data in written_dict.items():
        diff_dict[emp] = dict() 
        for w, h in data.items():
            w = int(w)
            if emp in planning_dict:
                if w in planning_dict[emp]:
                    diff_dict[emp][w] = h - planning_dict[emp][w]
                else:
                    diff_dict[emp][w] = h
            else:
                diff_dict[emp][w] = h

    for emp, data in planning_dict.items():
        if emp not in diff_dict:
            diff_dict[emp] = dict()
        for w, h in data.items():
            if w not in diff_dict[emp]:
                diff_dict[emp][w] = -h

    employee, week, hours = [],[],[]
    for emp, data in diff_dict.items():
        for w,h in data.items():
            employee += [emp]
            week += [w]
            hours += [h]


    val_week = np.sort(list(set(week)))
    text_week = [str(w)[:4] for w in val_week]

    newdf = pd.DataFrame(
    dict(employee=employee, week=week, hours=hours)
        )
    newdf = newdf.sort_values(by=['employee','week'])
    newdf['cumsum'] = newdf.groupby(['employee'])['hours'].cumsum()

    if cummulative_planning:
        fig = px.line(newdf, x='week', y='cumsum', color='employee', markers=True)
    else:
        fig = px.line(newdf, x='week', y='hours', color='employee', markers=True)
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = val_week,
        ticktext = text_week,
        range=[0, 52]
        )
    )
    return fig

if __name__ == "__main__":
    data = gantic2pandas('planning2022.csv')
    wt = create_weekly_tasks(data)

    project = 'Unravelling Proton Structure'
    pdf = wt[wt['Project']==project]

    total_cumsum = pdf.groupby(['Week']).sum().cumsum()
    pdf['employee_cumsum'] = pdf.groupby(['Employee'])['Quantity'].cumsum()

