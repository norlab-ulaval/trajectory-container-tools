# coding=utf-8
import numpy as np
import pytest


@pytest.fixture
def setup_mock_trajectory_data():
    def generate_trajectory_data(state_obs_ndim):
        trj_len = 9
        state_obs_ndim_trj = np.ones(trj_len * state_obs_ndim).reshape(trj_len, state_obs_ndim)
        if state_obs_ndim == 1:
            state_obs_ndim_trj = state_obs_ndim_trj.squeeze()
        time_obs_trj = np.arange(trj_len)
        return trj_len, state_obs_ndim, state_obs_ndim_trj, time_obs_trj

    return generate_trajectory_data
