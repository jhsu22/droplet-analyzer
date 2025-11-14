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

        self.g = 9.81  # Acceleration due to gravity
        self.delta_rho = initial_parameters["delta_rho"]
        self.calibration_factor = initial_parameters["calibration_factor"]

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

        # Flip profile vertically to make droplet hanging
        profile_z = -profile_z

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
        # Define bounds for the parameters:
        bounds = (
            [1, 0.001, -np.inf, -np.inf, -np.pi / 4],  # Lower bounds
            [np.inf, np.inf, np.inf, np.inf, np.pi / 4],  # Upper bounds
        )
        result = least_squares(
            fun=self._scipy_residuals, x0=initial_guess, bounds=bounds
        )

        # Update the parameters with the optimized values
        self.apex_radius, self.bond_number, self.apex_x, self.apex_y, self.rotation = (
            result.x
        )

        self.iterations = result.nfev

        self.is_converged = result.success

    def calculate_surface_tension(self):
        # Calculate surface tension using the fitted parameters

        # Convert apex radius from pixels to physical units
        apex_radius_physical = self.apex_radius * self.calibration_factor

        surface_tension = (
            self.delta_rho * self.g * apex_radius_physical**2 / self.bond_number
        )

        return surface_tension

    def calculate_volume(self):
        # Calculate the volume of the droplet using the fitted parameters

        self.generate_profile()

        # Get droplet solution
        s = self.solution.t
        phi = self.solution.y[0]
        r_dimensionless = self.solution.y[1]

        # Integrate the generated profile to get volume
        integrand = np.pi * r_dimensionless**2 * np.sin(phi)
        vol_dimensionless = np.trapz(integrand, s)

        # Convert dimensionless volume to physical volume
        apex_radius_physical = self.apex_radius * self.calibration_factor
        volume_physical = vol_dimensionless * apex_radius_physical**3

        return volume_physical

    def get_results(self):
        # Calculate surface tension
        surface_tension = self.calculate_surface_tension()

        # Calculate volume
        volume = self.calculate_volume()

        # Convert apex radius from pixels to physical units
        apex_radius_physical = self.apex_radius * self.calibration_factor

        return {
            "surface_tension": surface_tension,
            "volume": volume,
            "bond_number": self.bond_number,
            "apex_radius_pixels": self.apex_radius,
            "apex_radius_physical": apex_radius_physical,
            "apex_x": self.apex_x,
            "apex_y": self.apex_y,
            "rotation": self.rotation,
            "is_converged": self.is_converged,
            "iterations": self.iterations,
        }

    def get_fitted_profile(self):
        # Generate and transform theoretical profile
        profile_r, profile_z = self.generate_profile()
        r_translated, z_translated = self.transform_profile(profile_r, profile_z)

        # Combine into points
        fitted_points = np.column_stack((r_translated, z_translated)).astype(np.int32)

        return fitted_points
