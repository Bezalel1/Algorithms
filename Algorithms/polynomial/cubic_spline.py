import numpy as np
import sympy as sp


def cubic_spline4_matrix(points):
    """
    calculate the coefficients for cubic spline

    points: (n+1)x2 Matrix of points when Matrix[:,1]=x points and Matrix[:,2] = y points,
            n is the rank of the polynomial

    :return: [lambdify(sympy Matrix)] foe each S=[s0,s1,...,sn] where s_i(x)=a_i*x^3+b_i*x^2+c_i*x+d_i

    :complexity: O((4n)^3) where n is points number -1
     """
    # init
    points = np.array(points)
    points = points[points[:, 0].argsort()]
    x, y, n = points[:, 0], points[:, 1], points.shape[0] - 1
    X = np.vander(x, N=4, increasing=False)

    # build M,A
    M, A, idx = np.zeros((4 * n, 4 * n)), np.zeros((4 * n,)), np.arange(n * 4).reshape((-1, 4))
    M[idx // 4, idx] = X[:-1, :]
    M[idx // 4 + n, idx] = X[1:, :]
    idx = idx[:-1, :-1]
    M[idx // 4 + n * 2, idx] = X[1:-1, 1:] * np.array([3, 2, 1])
    M[idx // 4 + n * 2, idx + 4] = -M[idx // 4 + n * 2, idx]
    idx = idx[:, :-1]
    M[idx // 4 + n * 3 - 1, idx] = X[1:-1, 2:] * np.array([6, 2])
    M[idx // 4 + n * 3 - 1, idx + 4] = -M[idx // 4 + n * 3 - 1, idx]
    M[-2, :2], M[-1, -4:-2] = X[0, 2:] * np.array([6, 2]), X[-1, 2:] * np.array([6, 2])
    A[:n], A[n:2 * n] = y[:-1], y[1:]

    # calculate the coefficients
    coeff = np.linalg.solve(M, A).reshape((-1, 4))
    x_ = sp.symbols('x')
    S = coeff[:, 0] * x_ ** 3 + coeff[:, 1] * x_ ** 2 + coeff[:, 2] * x_ + coeff[:, 3]

    # return function
    return map_S(S, x_, points)


def cubic_spline4(points):
    """
    calculate the coefficients for cubic spline

    points: (n+1)x2 Matrix of points when Matrix[:,1]=x points and Matrix[:,2] = y points,
            n is the rank of the polynomial

    :return: [lambdify(sympy Matrix)] foe each S=[s0,s1,...,sn] where s_i(x)=a_i*x^3+b_i*x^2+c_i*x+d_i


    :complexity: O(n) where n is points number
     """
    # init
    points = np.array(points, dtype=np.float64)
    points = points[points[:, 0].argsort()]
    x, y, n = points[:, 0], points[:, 1], points.shape[0] - 1
    h = x[1:] - x[:-1]
    b = (y[1:] - y[:-1]) * (6 / h)
    u, v = 2 * (h[1:] + h[:-1]), b[1:] - b[:-1]

    # rank
    u[1:] -= h[1:-1] ** 2 / u[:-1]
    v[1:] -= v[:-1] * (h[1:-1] / u[:-1])
    z = np.empty((n + 1,))
    z[0], z[-1] = 0, 0

    # solve
    for i in range(n - 1, 0, -1):
        z[i] = (v[i - 1] - h[i] * z[i + 1]) / u[i - 1]

    # calc S
    c = y[1:] / h - (z[1:] * h) / 6
    d = y[:-1] / h - (z[:-1] * h) / 6
    x_ = sp.symbols('x')
    S = (z[:-1]) / (6 * h) * (x[1:] - x_) ** 3 + z[1:] / (6 * h) * (x_ - x[:-1]) ** 3
    S += c * (x_ - x[:-1]) + d * (x[1:] - x_)

    return map_S(S, x_, points)
    # return sp.lambdify(x_, sp.Matrix(S), 'numpy')


def map_S(S, x, points):
    n = points.shape[0] - 1
    func = [sp.lambdify(x, S[i], 'numpy') for i in range(len(S))]
    start, end = np.min(points[:, 0]), np.max(points[:, 0])
    rang = end - start
    map_points = lambda p: int((p - start) // (rang / n)) if p != end else n - 1
    splines = np.vectorize(lambda p: func[map_points(p)](p))
    return splines


if __name__ == '__main__':
    # print('-------------------  cubic spline: n=4  ----------------------------')
    # points = [(1, 1), (2, 2), (3, 3), (4, 4)]
    # print(cubic_spline4(points))
    # cubic_spline4(points)
    #
    # points = [(0, 0.3), (1, 1), (2, 5), (5, 7)]
    # print(cubic_spline4_matrix(points)(0.7))
    # print(cubic_spline4(points)(0.7))
    # print('-------------------  cubic spline: n=4, test 3  ----------------------------')
    # # points = [(3, 5), (1, 2), (2, 9), (3, -1)]
    # points = [(3, 5), (1, 2), (2, 9), (6, -1)]
    # print(cubic_spline4_matrix(points)(1))
    # print(cubic_spline4(points)(1))
    #
    # print('-------------------  cubic spline: n=4, test 4  ----------------------------')
    # points = [(4, 0), (1, 1), (2, 0), (3, -1)]
    # print(cubic_spline4_matrix(points)(1))
    # print(cubic_spline4(points)(1))
    print('-------------------  n=n  ----------------------------')
    points = np.linspace(7, 12, num=4)
    # points = np.arange(4)
    # print(points)
    x = sp.symbols('x')
    f = sp.lambdify(x, sp.sin(x), 'numpy')
    points = np.concatenate((points[:, None], f(points)[:, None]), axis=1)
    # print(points)
    real_points = np.linspace(7, 12, num=1000)
    # points = [(1, 1), (2, 0), (3, -1), (4, 0)]
    # print(cubic_spline4(points)(1))
    spline_mat = cubic_spline4_matrix(points)
    spline = cubic_spline4(points)

    import matplotlib.pyplot as plt

    plt.plot(real_points, spline_mat(real_points), c='k')
    plt.plot(real_points, spline(real_points), c='b')
    plt.plot(real_points, f(real_points), c='r')
    plt.show()
