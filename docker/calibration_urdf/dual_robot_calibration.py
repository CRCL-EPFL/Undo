###############################
#For calculating transformation matrix
#Jingwen Wang
#jingwen.wang@epfl.ch
###############################

import numpy as np
from compas.geometry import Rotation, Transformation, Translation, Vector, Frame, Point
from scipy.optimize import minimize
from compas.geometry import matrix_from_frame_to_frame as ma
import copy
import compas
compas.PRECISION = '12f'
##############################################################
###################### Data                  #################
##############################################################
# Round 2
x0 = [ 1032.41, 641.95, 477.18, 329.80, 348.06, 378.09, 895.68, 733.84]
y0 = [ -220.80, -424.63, -800.41, -619.13, -741.31, -288.52, -41.75, -699.27]
z0 = [ 229.30, 228.35, 234.27, 229.92, 553.77, 546.76, 549.95, 555.84]
x1 = [ 217.68, 614.20, 783.85, 927.85, 908.47, 869.93, 347.35, 522.34]
y1 = [ -408.23, -212.18, 159.51, -25.77, 101.16, -350.35, -587.30, 67.92]
z1 = [ 223.46, 225.50, 226.47, 227.70, 546.82, 548.47, 546.66, 543.34]

def norm_sum(array):
    sum = 0
    for i in range(array.shape[1]):
        sum = sum + np.linalg.norm((array.T)[i])
    return sum

dummy = [1.0]* len(x0)

p0 = np.array([x0,y0,z0,dummy])
p1 = np.array([x1,y1,z1,dummy])

#para = [1262.0378729827137, -628.7939125704166, 15.695121310209212, 0.016297469442821823, 0.013700033089713789, -3.121272822775666]
#para = [6314.5407117326, 3605.5713815320, 1.9451919106, -0.0068641574, -0.0049381995, -3.1408819909]
para = [6318.237045961799, 3603.4628770189765, 2.2994658244023287, -0.004381630413253641, -0.003018537904062979, -3.140871179506357]
#para = [1200, 0, 0, 1, 1, 1]

def error_func(para):
    xyz = para[0:3]
    rpy = para[3:]
    rot = Rotation.from_euler_angles(rpy,static = True, axes='xyz')
    transl = Translation.from_vector(Vector(*xyz))
    matrix = np.array(transl * rot)
    error = matrix @ p1 - p0
    return norm_sum(error)

##############################################################
###################### Method 1 Optimization #################
##############################################################

para_updated = minimize(error_func, para, method='Nelder-Mead', tol=1e-7, options = {'maxiter':10000})
precision = 10  # Set the desired precision
formatted_numbers = [f"{num:.{precision}f}" for num in para_updated.x]

print("result")
for num in formatted_numbers:
    print(num)

print("message",para_updated.message)
print("error",error_func(para_updated.x))


##############################################################
###################### Method 2 Average ######################
##############################################################

# combination calculation for point lists C5_2
def comb2(n):
    comb2= []
    for i in range(n-1):
        for j in range(i+1,n):
            comb2.append((i,j))
    return comb2
# combination calculation for point lists C5_3
def comb3(n):
    comb3= []
    for i in range(n-2):
        for (a,b) in comb2(n-i-1):
            comb3.append((i,a+i+1,b+i+1))
    return comb3

#quaternion matrix average calculation
def ave_Matrix(list_M):
    M_ave = copy.deepcopy(list_M[0])
    for i in range(4):
        for j in range(4):
            M_ave[i][j] = 0
    for M in list_M:
        for i in range(4):
            for j in range(4):
                M_ave[i][j] += 1/len(list_M) * M[i][j]
    T = Transformation.from_matrix(M_ave)
    return T
list_a = []
list_b = []
for x,y,z in zip(x0,y0,z0):
    list_a.append(Point(x,y,z))
for x,y,z in zip(x1,y1,z1):
    list_b.append(Point(x,y,z))

list_M = []
error_l = []
for i,j,k in comb3(len(list_a)):
    #print(i,j,k)
    F_A = Frame.from_points(list_a[i],list_a[j],list_a[k])
    F_B = Frame.from_points(list_b[i],list_b[j],list_b[k])
    T_bta = ma(F_B,F_A)
    #print(T_bta)
    list_M.append(T_bta)
T = ave_Matrix(list_M)
print("________Average__________")
print(T)
Scale, Shear, Rotation, Translation, Projection = T.decomposed()
rpy = Rotation.euler_angles(static=True, axes ='xyz')
xyz = Translation.translation_vector[0],Translation.translation_vector[1],Translation.translation_vector[2]
T_update = Translation.from_vector(Vector(*xyz)) * Rotation.from_euler_angles(rpy,static = True, axes = "xyz")
print("________Update__________")
print(T_update)
print([*xyz,*rpy])
print("Total Error", error_func([*xyz,*rpy]))
sum_new = 0
# Calculation for the calibration error
for pa,pb in zip(list_a, list_b):
    pa_c = Point(pa[0], pa[1], pa[2])
    pb_c = Point(pb[0], pb[1], pb[2])
    pb_t = pb_c.transformed(T_update)
    error = pow((pb_t[0]-pa_c[0]),2)+pow((pb_t[1]-pa_c[1]),2)+pow((pb_t[2]-pa_c[2]),2)
    error_l.append(error)
    sum_new = sum_new + pow(error,0.5)

print("new", sum_new)