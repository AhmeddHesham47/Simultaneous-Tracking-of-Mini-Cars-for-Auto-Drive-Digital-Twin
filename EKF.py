import numpy as np 

class ExtendedKalmanFilter:
    def __init__(self, dt=1/70):
        # Define the state space dimensions
        self.state_dim = 3  # State vector: [x, y, θ] (position and orientation)
        self.measurement_dim = 3  # Measurement vector: [x, y, θ]
        self.dt = dt  # Time step duration

        # Dictionary to store states and covariance matrices for each AprilTag
        self.states = {}  # Stores estimated states per tag ID
        self.P = {}  # Stores covariance matrices per tag ID

        # Process noise covariance matrix (Q) - represents system uncertainty
        self.Q = np.diag([0.55, 0.05, 0.552])  # Diagonal elements define variance for [x, y, θ]

        # Measurement noise covariance matrix (R) - represents sensor uncertainty
        self.R = np.diag([0.01, 0.01, 0.005])  # Small values indicate high confidence in measurements

    def f(self, x):
        """
        State transition function: Defines how the state evolves over time.
        Here, we assume a static model where the state remains unchanged.
        """
        F = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        return F @ x  # Predict next state using the transition matrix

    def h(self, x):
        """Measurement function: Directly returns the state as the measurement."""
        return x  # Assumes measurement directly corresponds to state

    def jacobian_F(self, x):
        """Jacobian of the state transition function: Identity matrix for a static model."""
        return np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    def jacobian_H(self, x):
        """Jacobian of the measurement function: Identity matrix since measurements directly map to state."""
        return np.eye(self.state_dim)  # 3x3 identity matrix

    def normalize_angle(self, angle):
        """Ensures angles remain within [0, 360) degrees."""
        return angle % 360

    def initialize_state(self, tag_id, measurement):
        """Initialize state and covariance for a newly detected AprilTag."""
        self.states[tag_id] = np.asarray(measurement)  # Store initial measurement as state
        self.P[tag_id] = np.diag([1.0, 1.0, 0.1])  # Initial covariance matrix with some uncertainty

    def predict_and_update(self, tag_id, measurement):
        """Performs both the prediction and update steps of the Kalman filter."""
        measurement = np.asarray(measurement)  # Convert input to NumPy array

        # If tag is seen for the first time, initialize it
        if tag_id not in self.states:
            self.initialize_state(tag_id, measurement)
            return self.states[tag_id]

        # Retrieve previous state and covariance matrix
        x = self.states[tag_id]
        P = self.P[tag_id]

        # Prediction step
        x_pred = self.f(x)  # Predict next state
        F = self.jacobian_F(x)  # Compute state transition Jacobian
        P_pred = F @ P @ F.T + self.Q  # Predict covariance matrix with added process noise

        # Update step
        H = self.jacobian_H(x_pred)  # Compute measurement Jacobian
        S = H @ P_pred @ H.T + self.R  # Compute system uncertainty
        K = P_pred @ H.T @ np.linalg.pinv(S)  # Compute Kalman Gain

        # Compute residual (difference between measurement and predicted state)
        residual = measurement - x_pred
        residual[2] = self.normalize_angle(measurement[2] - x_pred[2])  # Normalize angle error

        # Correct state estimate using Kalman Gain
        updated_state = x_pred + K @ residual
        updated_P = (np.eye(self.state_dim) - K @ H) @ P_pred  # Update covariance matrix

        # Normalize final angle estimate
        updated_state[2] = self.normalize_angle(updated_state[2])

        # Store updated state and covariance
        self.states[tag_id] = updated_state
        self.P[tag_id] = updated_P

        return updated_state  # Return filtered state
