import pandas as pd 
import datetime 
from process_data import get_unique_names

def name2fullname(name, list_fullnames):
    first_names = [n.split()[0] for n in list_fullnames]
    special_cases = {
        'PabloR': 'Pablo Rordriguez-Sanchez',
        'PabloL': 'Pablo Lopez-Tarifa',
        'PeterKal': 'Peter Kalvera',
        'PeterKok': 'Peter Kok'
    }
    if name in special_cases:
        return special_cases[n]
    else:
        return list_fullnames(first_names.index(name))


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

if __name__ == "__main__":
    data = gantic2pandas('planning2022.csv')
    wt = create_weekly_tasks(data)

    project = 'Unravelling Proton Structure'
    pdf = wt[wt['Project']==project]

    total_cumsum = pdf.groupby(['Week']).sum().cumsum()
    pdf['employee_cumsum'] = pdf.groupby(['Employee'])['Quantity'].cumsum()
