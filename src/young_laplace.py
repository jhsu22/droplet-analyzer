"""
Young-Laplace Fitter

Takes the edge detection result and iteratively fits the Young-Laplace equation to it to calculate bond number and surface tension.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from scipy.spatial.distance import cdist


class YoungLaplaceFitter:
    def __init__(self, edge_data, initial_parameters):
        self.edge_data = edge_data

        self.apex_radius = initial_parameters["apex_radius"]
        self.apex_x = initial_parameters["apex_x"]
        self.apex_y = initial_parameters["apex_y"]
        self.rotation = initial_parameters["rotation"]
        self.bond_number = initial_parameters["bond_number"]
        self.lmf_parameter = initial_parameters["lmf_parameter"]

        self.iterations = 0
        self.is_converged = False

    def _young_laplace_odes(self, s, state, bo):
        # ODEs for the Young-Laplace equation
        phi, r, z = state

        if r < 1e-9:  # Handle the singularity at the apex
            dphi_ds = 2 - bo * z - 1
        else:
            dphi_ds = 2.0 - bo * z - np.sin(phi) / r

        dr_ds = np.cos(phi)
        dz_ds = np.sin(phi)

        return [dphi_ds, dr_ds, dz_ds]

    def generate_profile(self):
        # Generate a theoretical edge profile using guessed parameters

        bo = self.bond_number  # Bond number guess
        initial_state = [0, 0, 0]  # [phi, r, z] at the apex

        s_span = [0, 5]  # Integration range for arc length
        s_eval = np.linspace(s_span[0], s_span[1], 200)  # Points for evaluation

        solution = solve_ivp(
            fun=self._young_laplace_odes,
            t_span=s_span,
            y0=initial_state,
            args=(bo,),  # Pass bond number to ODE function
            t_eval=s_eval,
            dense_output=True,
        )
        self.solution = solution

        # Get solution profile
        profile_r = solution.y[1]
        profile_z = solution.y[2]

        return profile_r, profile_z

    def transform_profile(self, profile_r, profile_z):
        # Scale, rotate, and translate the generated profile to match the edge points

        # Create the full droplet profile by flipping and concatenating
        r_left = -np.flip(profile_r[1:])
        r_full = np.concatenate((r_left, profile_r))

        z_left = np.flip(profile_z[1:])
        z_full = np.concatenate((z_left, profile_z))

        # Scale the profile to units of pixels
        r_scaled = r_full * self.apex_radius
        z_scaled = z_full * self.apex_radius

        # Rotate the profile
        cos_rot = np.cos(self.rotation)
        sin_rot = np.sin(self.rotation)

        r_rotated = r_scaled * cos_rot - z_scaled * sin_rot
        z_rotated = r_scaled * sin_rot + z_scaled * cos_rot

        # Translate the profile to the apex location
        r_translated = r_rotated + self.apex_x
        z_translated = z_rotated + self.apex_y

        return r_translated, z_translated

    def _scipy_residuals(self, params):
        self.apex_radius, self.bond_number, self.apex_x, self.apex_y, self.rotation = (
            params
        )

        return self.calculate_residuals()

    def calculate_residuals(self):
        # Compare edge data with generated profile

        # Generate and transform theoretical profile
        profile_r, profile_z = self.generate_profile()
        r_translated, z_translated = self.transform_profile(profile_r, profile_z)

        # Bring data into one array
        theoretical_data = np.column_stack((r_translated, z_translated))

        # Calculate distances between edge data and theoretical data
        distances = cdist(self.edge_data, theoretical_data)

        # Find minimum distances (residuals)
        residuals = np.min(distances, axis=1)

        return residuals

    def fit_profile(self):
        # Define initial guess for the solver
        initial_guess = np.array(
            [
                self.apex_radius,
                self.bond_number,
                self.apex_x,
                self.apex_y,
                self.rotation,
            ]
        )

        # Fit the profile using scipy.optimize.least_squares
        result = least_squares(fun=self._scipy_residuals, x0=initial_guess)

        # Update the parameters with the optimized values
        self.apex_radius, self.bond_number, self.apex_x, self.apex_y, self.rotation = (
            result.x
        )

        self.is_converged = result.success
