import time
import pandas as pd
import numpy as np
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
filePath = os.path.join(current_dir, '../Instances')
resultPath = os.path.join(current_dir, '../Solutions')
data_list = pd.read_csv('data_list.csv')
Instance_name = input("Please enter the Instance name (e.g., XY1 or QX1): ")
I = data_list[data_list['Instance'] == Instance_name]['I'].values[0]
J = data_list[data_list['Instance'] == Instance_name]['J'].values[0]
M = data_list[data_list['Instance'] == Instance_name]['M'].values[0]
R = data_list[data_list['Instance'] == Instance_name]['R'].values[0]
S = data_list[data_list['Instance'] == Instance_name]['S'].values[0]
K = data_list[data_list['Instance'] == Instance_name]['K'].values[0]
zjm = pd.read_csv(resultPath+rf"\out_{Instance_name}_zjm.csv")
zjm = np.array(zjm)[:, 1:]
pim = pd.read_csv(resultPath+rf"\out_{Instance_name}_pim.csv")
pim = np.array(pim)[:, 1:]
# manual:Only use Instances with the prefix QX
# zjm = pd.read_csv(resultPath + rf"\manual_{Instance_name}_zjm.csv")
# zjm = np.array(zjm)[:, 1:]
# pim = pd.read_csv(resultPath + rf"\manual_{Instance_name}_pim.csv")
# pim = np.array(pim)[:, 1:]

temp_path = filePath + fr'\{Instance_name}'

df1 = pd.read_csv(temp_path + r'\Classroom_capacity.csv')
C_i1 = df1.iloc[:, :].values.tolist()
C_i = []
for i in range(len(C_i1)):
    for j in range(len(C_i1[i])):
        C_i.append(C_i1[i][j])
C_i = C_i[0:I]
# print('CI', C_i)

df2 = pd.read_csv(temp_path + r'\Student_course_matrix.csv')
A_s1 = df2.iloc[0:S, M:].values.tolist()
B_m1 = df2.iloc[S:, 0:M].values.tolist()
B_m = []
for i in range(len(B_m1)):
    for j in range(len(B_m1[i])):
        B_m.append(B_m1[i][j])
H_sm = df2.iloc[0:S, 0:M].values.tolist()

df3 = pd.read_csv(temp_path + r'\Classroom_region_matrix.csv')
T_ir = df3.iloc[0:I, 0:R].values.tolist()

df5 = pd.read_csv(temp_path + r'\Teacher_course_matrix.csv')
Q_km = df5.iloc[0:, 0:M].values.tolist()


df = pd.read_csv(temp_path + r'\Same_time_teacher_course_matrix.csv')
df11 = df.values.tolist()
TK = []
for i in range(0, len(df11[:])):
    List = [elem if not np.isnan(elem) else None for elem in df11[i][:]]
    while None in List:
        List.remove(None)
    TK.append(List)
for i in range(0, len(TK)):
    for k in range(0, len(TK[i])):
        TK[i][k] = int(TK[i][k])

df4 = pd.read_csv(temp_path + r'\Classroom_campus_matrix.csv')
df6 = pd.read_csv(temp_path + r'\Course_campus_matrix.csv')
df7 = pd.read_csv(temp_path + r'\Limit_invigilators.csv')
# check
from math import fsum


def check_feasible(I, J, M, S, H_sm, K, Q_km, TK, zjm, pim, T_ir):
    """
    Return (feasible: bool, obj: float or error message: str)
    """
    A, B = J - 1, J - 2
    # --- Each course must be examined in exactly one time period ---
    for m in range(M):
        if fsum(zjm[:, m]) != 1:
            return False, f"Constraint violated: course m={m} assigned {fsum(zjm[:, m])} time solt"

    # --- Courses in the same TK group must be scheduled simultaneously ---
    for k in range(len(TK)):
        idx = [i - 1 for i in TK[k]]  # 0-based
        for j in range(J):
            flag = zjm[j][idx[0]]
            if any(zjm[j][i] != flag for i in idx):
                return False, f"Constraint violated: group course_idx={idx} not simultaneous at period j={j}"

    # --- Teacher k cannot examine more than one course in the same period ---
    Q_kj = np.array(Q_km @ zjm.T)
    for j in range(J):
        for k in range(K):
            if Q_kj[k][j] > 1:
                return False, f"Constraint violated: teacher k={k} has {Q_kj[k][j]} courses in period j={j}"

    # --- Compute lower bound u[j][s] ---
    conflicts = np.dot(zjm, np.array(H_sm).T)  # shape: (J, S)
    u = np.maximum(0, conflicts - 1).astype(int)

    # --- y[j][s] indicates whether student s has an exam in period j ---
    y = (conflicts > 0).astype(int)

    # --- Consecutive exam pressure g1 ---
    g1 = np.zeros((A, S), dtype=int)
    if A > 0:
        g1 = (y[:A] & y[1:A + 1]).astype(int)

    # --- Skip-one exam pressure g2 ---
    g2 = np.zeros((B, S), dtype=int)
    if B > 0:
        g2 = (y[:B] & y[2:B + 2]).astype(int)

    # --- Objective 1 ---
    obj1 = (90 * fsum(u[j][s] for j in range(J) for s in range(S)) +
            1.5 * 1.959 * fsum(g1[j][s] for j in range(A) for s in range(S)) +
            1.5 * fsum(g2[j][s] for j in range(B) for s in range(S)))

    # --- One classroom can host at most one course per period ---
    classroom_schedule = np.dot(zjm, pim.T)  # shape: (J, I)
    if np.any(classroom_schedule >= 2):
        violation_idx = np.where(classroom_schedule >= 2)
        if len(violation_idx[0]) > 0:
            j_violation, i_violation = violation_idx[0][0], violation_idx[1][0]
            course_count = classroom_schedule[j_violation, i_violation]
            return False, f"Constraint violated: classroom i={i_violation} hosts {course_count} courses in period j={j_violation}"

    # --- Classroom capacity must accommodate students ---
    course_capacity = np.dot(C_i, pim)  # shape: (M,)
    capacity_violations = course_capacity < B_m
    if np.any(capacity_violations):
        m_violation = np.where(capacity_violations)[0][0]
        CII = np.where(pim[:, m_violation])[0]
        return False, f"Constraint violated: course m={m_violation} classroom {CII} capacity {course_capacity[m_violation]} < {B_m[m_violation]} students"

    # --- Campus matching between course and classroom ---
    classroom_campus = df4.values  # (I, campus_count)
    course_campus = df6.values  # (M, campus_count)
    I, M = pim.shape
    for m in range(M):
        assigned_classrooms = np.where(pim[:, m] == 1)[0]
        if len(assigned_classrooms) > 0:
            course_campuses = np.where(course_campus[m, :] == 1)[0]
            for classroom_idx in assigned_classrooms:
                classroom_campuses = np.where(classroom_campus[classroom_idx, :] == 1)[0]
                if not any(campus in course_campuses for campus in classroom_campuses):
                    return False, f"Campus mismatch: course {m} assigned classroom {classroom_idx} not in same campus"

    # --- Each time slot has a limited number of invigilators ---
    for campus_idx in range(len(course_campus[0])):
        temp_ji_num = zjm * course_campus[:, campus_idx] @ pim.T
        for j in range(J):
            if fsum(temp_ji_num[j]) > df7.iloc[0][campus_idx]:
                return False, f"Constraint violated: time slot j={j} exceed limited number of invigilators {df7.iloc[j][0]} of campus {campus_idx}"

    # --- Relationship v_r^m and x_{ij}^m ---
    pim_array = np.array(pim)  # (I, M)
    T_ir_array = np.array(T_ir)  # (I, R)
    v_rm = (np.dot(T_ir_array.T, pim_array) >= 1).astype(int)  # (R, M)

    # --- Objective 2 ---
    obj2_part1 = np.sum(pim)
    obj2_part2 = 1.3 * (np.sum(v_rm) - np.sum(zjm))
    obj2 = obj2_part1 + obj2_part2

    return True, obj1 + obj2





# Timing
start_time = time.time()
feasible, val = check_feasible(I, J, M, S, H_sm, K, Q_km, TK, zjm, pim, T_ir)
end_time = time.time()
print("Running time:", end_time - start_time)
if feasible:
    print("All constraints passed, objective value =", val)
else:
    print("Constraint violation:", val)

