## Overview
The repository contains datasets related to papers "Data-driven university examination timetabling with consideration of student stress" and a result checker.

Use these data to reproduce the experimental results of the paper or explore other efficient solving methods. Checking procedures can help and analyze solution quality.

## Structure
- `Checker/`: Including: a check procedure for checking the feasibility and quality of the results, and its use will be followed later; An instance of characteristic data (I (number of classrooms), S (number of students), M (number of courses), J (number of exam slots), R (classroom area), K (number of teachers)).
- `Instances/`: Including the experimental part of the paper is all the example data.
- `Solutions/`: Including the best results obtained by the paper using the ALNS algorithm.
-
- ├── 📁 Checker/                    # Checker module: solution validation
- │   ├── checker.py                 # Core checking script
- │   └── data_list.csv              # Data inventory/index file
- │
- ├── 📁 Instances.zip/                  # Instance data folder
- │   └── 📁 QX1/                    # Specific instance (eg QX1)
- │       ├── Classroom_campus_matrix.csv      # S_il: Classroom-campus affiliation matrix
- │       ├── Classroom_capacity.csv           # C_i: Classroom capacity data
- │       ├── Classroom_region_matrix.csv      # T_ir: Classroom-region distribution matrix
- │       ├── Course_campus_matrix.csv         # Course-campus offering matrix ,By combining T_ir, R_im(binary value R_im = 1 if course m is taught at the same campus of classroom i, and R_im = 0 otherwise.
classroom i ∈ I, and Rim = 0 otherwise.) can be obtained.
- │       ├── Limit_invigilators.csv           # D_l: Invigilator limit constraints
- │       ├── Same_time_teacher_course_matrix.csv  # Q_mm: Teacher simultaneous course conflict matrix
- │       ├── Student_course_matrix.csv        # H_ms: Student-course enrollment matrix
- │       └── Teacher_course_matrix.csv        # G_mk: Teacher-course assignment matrix
- │
- └── 📁 Solutions/                  # Solution output folder (eg QX1)
- │   ├── out_QX1_pim.csv            # ALNS output: classroom assignment for exams
- │   └── out_QX1_zjm.csv            # ALNS output: timeslot assignment for exams

## Data description

### Instances data
| Filename | Description | Key Fields |
|:---|:---|:---|
| Classroom_campus_matrix.csv | Matrix describing which campus each classroom belongs to | (m, l): Whether course m is offered at campus l (1 = Yes, 0 = No) |
| Classroom_capacity.csv | Records the number of students each classroom can accommodate | Each row represents the capacity of classroom i |
| Classroom_region_matrix.csv | Describes the regional distribution within classrooms | (i, r): Whether classroom i is located in region r (1 = Yes, 0 = No) |
| Course_campus_matrix.csv | Describes the course offerings at each campus | (m, l): Whether course m is offered at campus l (1 = Yes, 0 = No) |
| Student_course_matrix.csv | Records the registration relationship between students and courses | (s, m): Whether student s is registered for course m (1 = Yes, 0 = No) |
| Limit_invigilators.csv | Limits on the number of invigilators for each exam time slot | Each row represents the limit for time slot j |
| Teacher_course_matrix.csv | Records the relationship between teachers and courses | (k, m): Whether teacher k teaches course m (1 = Yes, 0 = No) |
| Same_time_teacher_course_matrix.csv | Course combinations that need to be examined at the same time | Courses in each row are scheduled in the same time slot |
  

### Solutions data

| Filename | Description | Key Fields |
|:---|:---|:---|
| out_{instances}_pim.csv | Indicates which classroom i is used by course m for the exam | 1 indicates course m takes the exam in classroom i, 0 indicates otherwise |
| out_{instances}_zjm.csv | Indicates which time slot j is used by course m for the exam | 1 indicates course m takes the exam in time slot j, 0 indicates otherwise |

## Checker
The `check_feasible` function is used to verify the feasibility of an exam scheduling plan and calculate the objective function value. When calling it, you need to provide 11 parameters: the number of classrooms I, the number of time slots J, the number of courses M, the number of students S, the student-course matrix H_sm, the number of teachers K, the teacher-course matrix Q_km, the simultaneous exam course groups TK, the time slot assignment matrix zjm, the classroom assignment matrix pim, and the classroom region matrix T_ir. It returns a tuple (feasible, val): if feasible is True, it means all constraints are satisfied, and val is the computed objective function value; if False, val contains a string with specific violation information, which can be used to identify the reason for the conflict. Before calling, ensure that classroom capacities C_i, course enrollments B_m, and related data frames such as campus matches and invigilation restrictions have been loaded via pandas. At runtime, you need to input the name of the test case to check, such as QX1 or XY1.



