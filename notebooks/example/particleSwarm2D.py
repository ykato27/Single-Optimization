# 粒子群最適化（Particle Swarm Optimization）
#  ただし，最低値を最適とみなす
import math
import random
import time
from tkinter import *


def array(N1, N2=0, N3=0):  # ■配列宣言
    if N2 == 0:
        return [0 for i in range(N1)]
    if N3 == 0:
        return [[0 for i in range(N2)] for j in range(N1)]
    return [[[0 for i in range(N3)] for j in range(N2)] for k in range(N1)]


NUMLOOP = 300  # 最大繰返し回数
NUM = 10  # 粒子の数
c1 = 0.2
c2 = 0.8
w = 0.9  # 実行パラメータ
loopFlag = True  # 最適適合度のチェックでループ完了
eps = 0.000001  # 最適適合度のチェック値
debug = False  # デバッグフラグ
draw = True  # 描画フラグ
# --------------(共通関数)------------------------
def setInitX(NUM):  # ■座標値初期化
    X = array(NUM, 2)  # 　粒子群の座標値
    for i in range(NUM):
        X[i][0] = random.random() * 10
        X[i][1] = random.random() * 10
    return X


def setInitV(NUM):  # ■速度初期化
    V = array(NUM, 2)  #  粒子群の速度
    for i in range(NUM):
        V[i][0] = random.random() - 0.5
        V[i][1] = random.random() - 0.5
    return V


def fitV(X):  # ■適合度計算
    X1 = X[0] - 1
    X2 = X[0] - 4
    X3 = X[0] - 7
    X4 = X[0] - 9
    Y1 = X[1] - 9
    Y2 = X[1] - 4
    Y3 = X[1] - 5
    Y4 = X[1] - 1
    return X1 * X2 * X3 * X4 + Y1 * Y2 * Y3 * Y4 + 158


#    DX=X[0]-5; DY=X[1]-5
#    return DX*DX+DY*DY
def initFit(X):  # ■適合度の初期化
    NUM = len(X)
    F = array(NUM, 2)
    for i in range(NUM):
        F[i][0] = fitV(X[i])
        F[i][1] = X[i]
    return F


def bestAll(F):  # ■全体の最適値を求める
    ID = 0
    Mn = F[0][0]  # （ここでは最低値を最適とする）
    for i in range(1, len(F)):
        if F[i][0] < Mn:
            ID = i
            Mn = F[i][0]
    return [F[ID][0], F[ID][1]]


def printX(i, X):  # ■Xとその適合度を表示
    NUM = len(X)
    S = "%4d" % i
    for k in range(len(X)):
        S += ", %6.4f, %6.4f" % (X[k][0], X[k][1])
    for k in range(len(X)):
        S += ", %6.4f" % fitV(X[k])
    print(S)


# --------(描画用関数)------------------
def cCode(V):  # ■RBG値チェック
    VV = int(V)
    if VV < 0:
        return 0
    if VV > 255:
        return 255
    return int(VV)


def setColor(V, av, dV):  # ■色コード表示
    if V >= av:
        DC = (V - av) / dV
        R = 2 * DC
        G = 255 - DC
        B = 0
    else:
        R = 0
        DC = (av - V) / dV
        G = 255 - DC / 2
        B = DC / 2
    return "#%02X%02X%02X" % (cCode(R), cCode(G), cCode(B))
    # return "#%02X77%02X" % (ID,ID)


def colorMap(canvas):  # ■適合度による色地図表示
    X0 = 0
    mn = 1e32
    mx = -1e32
    xy = array(2)
    for i in range(101):  # 最大・最小を求める
        Y0 = 0
        xy[0] = X0
        for j in range(101):
            xy[1] = Y0
            V = fitV(xy)
            if V < mn:
                mn = V
            if V > mx:
                mx = V
            Y0 += 0.1
        X0 += 0.1
    av = (mx + mn) / 2
    dV = (mx - av) / 255
    X0 = 0
    for i in range(101):
        XX = X0 * 20 + 20
        Y0 = 0
        xy[0] = X0
        for j in range(101):
            xy[1] = Y0
            YY = Y0 * 20 + 20
            V = fitV(xy)

            CL = setColor(V, av, dV)
            canvas.create_rectangle(
                XX, YY, XX + 2, YY + 2, fill=CL, outline=""
            )
            Y0 += 0.1
        X0 += 0.1
    # print("max=",mx,"min=",mn, mnID,mxID)


def drawPoint(X):  # ■粒子の表示
    N = len(X)
    dID = array(N)
    for i in range(N):
        XX = X[i][0] * 20 + 20
        YY = X[i][1] * 20 + 20
        dID[i] = canvas.create_rectangle(XX, YY, XX + 2, YY + 2, fill="red")
    return dID


def movePoint(canvas, dID, X):  # ■粒子表示位置の変更
    N = len(X)
    for i in range(N):
        XX = X[i][0] * 20 + 20
        YY = X[i][1] * 20 + 20
        canvas.coords(dID[i], XX, YY, XX + 2, YY + 2)


# ------------(粒子群最適化処理)---------------
def execP(c1, c2, w, debug=False):  # ■一回の計算
    global X, V, canvas, bestX, F, NUM
    EPS = 999
    for k in range(NUM):  # 粒子数で繰返し
        X[k][0] += V[k][0]
        X[k][1] += V[k][1]  # 座標変更
        nF = fitV(X[k])  # 座標変更と適合度計算
        if nF < F[k][0]:  # 小さいほうを最適とみなす
            F[k][0] = nF
            F[k][1][0] = X[k][0]
            F[k][1][1] = X[k][1]
            if debug:
                print("\n set 適合度", nF, X[k])
        if nF < bestX[0]:  # 小さいほうを最適とみなす
            if debug:
                print(" set befor nF", nF, "X", X[k])
            EPS = bestX[0] - nF
            bestX[0] = nF
            bestX[1][0] = X[k][0]
            bestX[1][1] = X[k][1]
            if debug:
                print(" set bestX", bestX)
        r1 = random.random()
        r2 = random.random()
        V[k][0] = (
            w * V[k][0]
            + c1 * r1 * (F[k][1][0] - X[k][0])
            + c2 * r2 * (bestX[1][0] - X[k][0])
        )  # X速度変更
        V[k][1] = (
            w * V[k][1]
            + c1 * r1 * (F[k][1][1] - X[k][1])
            + c2 * r2 * (bestX[1][1] - X[k][1])
        )  # Y速度変更
    return EPS


# -------(メインプログラム)--------------------
random.seed(19561)  # 動きを一定化するための乱数シーズ設定
if draw:  # 描画準備
    root = Tk()
    root.title("Particle Swarm 2D")
    canvas = Canvas(root, width=240, height=240, bg="white")
    canvas.pack()
    colorMap(canvas)
X = setInitX(NUM)
V = setInitV(NUM)  # 初期化
F = initFit(X)
bestX = bestAll(F)
if draw:
    dID = drawPoint(X)
    root.update()  # 粒子群初期表示
if debug:
    print("init fit値", F)
if debug:
    print("init bestX", bestX)
for i in range(NUMLOOP):  # 繰返し計算
    EPS = execP(c1, c2, w, debug)  #  1回の計算
    if debug:
        printX(i, X)
    if draw:
        movePoint(canvas, dID, X)  #  粒子位置変更
        root.update()
        time.sleep(0.01)
    if loopFlag and EPS < eps:
        break  # 全体最適値収れん
ts = "回数%d 結果 %6.4f, 座標(%6.4f, %6.4f)" % (
    i,
    bestX[0],
    bestX[1][0],
    bestX[1][1],
)
print(ts)
if draw:
    canvas.create_text(120, 230, text=ts, font=("times", 8))
