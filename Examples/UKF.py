"""
Unscented Kalman Filter Example
=================================

"""

import time
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
import StatOD
from StatOD.data import get_measurements
from StatOD.dynamics import *
from StatOD.filters import * 
from StatOD.measurements import *
from StatOD.visualizations import *
from StatOD.constants import * 

def main():

    ep = EarthParams()
    cart_state = np.array([-3515.4903270335103, 8390.716310243395, 4127.627352553683,
                           -4.357676322178153, -3.3565791387645487, 3.111892927869902])
                                  
    t, Y, X_stations_ECI = get_measurements("Data/Measurements/range_rangerate_w_J2_w_noise.data")

    # Decrease scenario length
    M_end = len(t) // 5
    t = t[:M_end]
    Y = Y[:M_end]

    # Initialize state and filter parameters
    dx0 = np.array([0.1, 0.0, 0.0, 1E-4, 0.0, 0.0]) 
    x0 = cart_state + dx0

    P_diag = np.array([1, 1, 1, 1E-3, 1E-3, 1E-3])**2
    R_diag = np.array([1E-3, 1E-6])**2
    P0 = np.diag(P_diag) 
    R0 = np.diag(R_diag)
    t0 = 0.0

    # Initialize Process Noise
    Q0 = np.eye(3) * 5e-8 ** 2
    Q_args = []
    Q_fcn = process_noise(x0, Q0, get_Q, Q_args, use_numba=False)

    # Initialize Dynamics and Measurements
    f_args = np.array([ep.R, ep.mu, ep.J2])
    f, dfdx = dynamics(x0, f_J2, f_args)
    f_dict = {
        "f": f,
        "dfdx": dfdx,
        "f_args": f_args,
        "Q_fcn": Q_fcn,
        "Q": Q0,
        "Q_args": Q_args,
    }

    h_args = X_stations_ECI[0]
    h, dhdx = measurements(x0, h_rho_rhod, h_args)
    h_dict = {'h': h, 'dhdx': dhdx, 'h_args': h_args}

    #########################
    # Generate f/h_args_vec #
    #########################

    f_args_vec = np.full((len(t), len(f_args)), f_args)
    h_args_vec = X_stations_ECI
    R_vec = np.repeat(np.array([R0]), len(t), axis=0)

    ##############
    # Run Filter #
    ##############

    alpha = 1E-3
    beta = 2.0
    kappa = 0.0

    start_time = time.time()
    logger = FilterLogger(len(x0), len(t))
    filter = UnscentedKalmanFilter(t0, x0, dx0, P0, alpha, kappa, beta, f_dict, h_dict, logger=logger)
    filter.run(t, Y[:,1:], R_vec, f_args_vec, h_args_vec)
    print("Time Elapsed: " + str(time.time() - start_time))

    ##################################
    # Gather measurement predictions #
    ##################################
    package_dir = os.path.dirname(StatOD.__file__) + "/../"
    with open(package_dir + 'Data/Trajectories/trajectory_J2.data', 'rb') as f:
        traj_data = pickle.load(f)

    x_truth = traj_data['X'][:M_end]
    y_hat_vec = np.zeros((len(t), 2))
    for i in range(len(t)):
        y_hat_vec[i] = filter.predict_measurement(logger.x_hat_i_plus[i], h_args_vec[i])

    directory = "Plots/" + filter.__class__.__name__ + "/"
    y_labels = np.array([r'$\rho$', r'$\dot{\rho}$'])
    vis = VisualizationBase(logger, directory, False)
    vis.plot_state_errors(x_truth)
    vis.plot_residuals(Y[:,1:], y_hat_vec, R_vec, y_labels)
    plt.show()


if __name__ == "__main__":
    main()
