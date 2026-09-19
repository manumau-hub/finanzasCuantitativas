import random
import numpy as np
from datetime import datetime, date, timedelta

class Resource:
    def __init__(self, name, hourly_rate):
        self.name = name
        self.hourly_rate = hourly_rate
        
class Project:
    def __init__(self, client, name, project_type, start_date, end_date, resources, hours):
        self.name = name
        self.client = client
        self.project_type = project_type
        self.start_date = start_date
        self.end_date = end_date
        self.resources = resources
        self.hours = hours
        self.total_cost = sum([r.hourly_rate * h for r, h in zip(resources, hours)])
        
def resource_allocation_per_month(resource, projects):
    allocation_per_month = {i: 0 for i in range(1,13)}
    for project in projects:
        if resource in project.resources:
            project_start_month = project.start_date.month
            project_end_month = project.end_date.month
            project_duration_in_months = (project.end_date.year - project.start_date.year) * 12 + project_end_month - project_start_month + 1
            allocation_per_month_for_project = resource.allocation / project_duration_in_months
            for i in range(project_start_month, project_end_month + 1):
                allocation_per_month[i] += allocation_per_month_for_project
    return allocation_per_month

#def generate_projects(n_projects, start_date, end_date, resources, min_hours, max_hours, n_resources_per_project):
#    projects = []
#    names = ["Project" + str(i) for i in range(1, n_projects + 1)]
#    clients = ["Client" + str(i) for i in range(1, n_projects + 1)]
#    for name, client in zip(names, clients):
#        project_resources = random.sample(resources, n_resources_per_project)
#        project_hours = [random.randint(min_hours, max_hours) for _ in range(n_resources_per_project)]
#        projects.append(Project(name, client, "Validation", start_date, end_date, project_resources, project_hours))
#    return projects

def main():


    
    resources = [Resource("Pablo", 70), Resource("Fede", 45), Resource("Jeison", 70), Resource("Monica", 45), Resource("Sofia", 45)]
    projects = [
        Project("Forbright", "CECL", "Validation", datetime(2023, 2, 1), datetime(2023, 4, 30), [resources[2], resources[3]], [105, 245]),
        Project("Forbright", "Verafin", "Validation", datetime(2023, 2, 15), datetime(2023, 5, 15), [resources[0], resources[1]], [120, 280]),
        Project("USBank", "Bonds", "Validation", datetime(2023, 3, 1), datetime(2023, 3, 31), [resources[0], resources[4]], [50, 100]),
        Project("USBank", "Bonds II", "Validation", datetime(2023, 3, 1), datetime(2023, 3, 31), [resources[0], resources[4]], [50, 100])]
    
    #print(projects[0].client)

    #print(resources[0].name)
    print(resource_allocation_per_month(Resource("Pablo", 70), projects))
    
if __name__ == "__main__":
    main()

