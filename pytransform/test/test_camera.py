import numpy as np
from pytransform.camera import (make_world_line, make_world_grid, cam2sensor,
                                sensor2img, world2image)
from pytransform.rotations import matrix_from_euler_xyz
from pytransform.transformations import transform_from
from nose.tools import (assert_raises_regexp, assert_false, assert_in,
                        assert_equal)
from numpy.testing import assert_array_almost_equal


def test_make_world_line():
    line = make_world_line(np.array([0, 0, 0]), np.array([1, 1, 1]), 11)
    assert_equal(len(line), 11)
    assert_in(np.array([0, 0, 0, 1]), line)
    assert_in(np.array([0.5, 0.5, 0.5, 1]), line)
    assert_in(np.array([1, 1, 1, 1]), line)


def test_make_world_grid():
    grid = make_world_grid(3, 3, xlim=(-1, 1), ylim=(-1, 1))
    assert_in(np.array([-1, -1, 0, 1]), grid)
    assert_in(np.array([-1, 0, 0, 1]), grid)
    assert_in(np.array([-1, 1, 0, 1]), grid)
    assert_in(np.array([0, -1, 0, 1]), grid)
    assert_in(np.array([0, 0, 0, 1]), grid)
    assert_in(np.array([0, 1, 0, 1]), grid)
    assert_in(np.array([1, -1, 0, 1]), grid)
    assert_in(np.array([1, 0, 0, 1]), grid)
    assert_in(np.array([1, 1, 0, 1]), grid)


def test_cam2sensor_wrong_dimensions():
    P_cam = np.ones((1, 2))
    assert_raises_regexp(ValueError, "3- or 4-dimensional points",
                         cam2sensor, P_cam, 0.1)
    P_cam = np.ones((1, 5))
    assert_raises_regexp(ValueError, "3- or 4-dimensional points",
                         cam2sensor, P_cam, 0.1)


def test_cam2sensor_wrong_focal_length():
    P_cam = np.ones((1, 3))
    assert_raises_regexp(ValueError, "must be greater than 0",
                         cam2sensor, P_cam, 0.0)


def test_cam2sensor_points_behind_camera():
    P_cam = np.ones((1, 3))
    P_cam[0, 2] = -1.0
    P_sensor = cam2sensor(P_cam, 0.1)
    assert_false(np.any(np.isfinite(P_sensor)))


def test_cam2sensor_projection():
    P_cam = np.array([[-0.56776587, 0.03855521, 0.81618344, 1.0]])
    P_sensor = cam2sensor(P_cam, 0.0036)
    assert_array_almost_equal(P_sensor, np.array([[-0.00250429, 0.00017006]]))


def test_sensor2img():
    P_sensor = np.array([[-0.00367 / 2, -0.00274 / 2],
                         [0.0, 0.0],
                         [0.00367 / 2, 0.00274 / 2]])
    P_image = sensor2img(P_sensor, (0.00367, 0.00274), (640, 480))
    assert_array_almost_equal(P_image, np.array([[0, 0],
                                                 [320, 240],
                                                 [640, 480]]))

    P_sensor = np.array([[0.0, 0.0],
                         [0.00367, 0.00274]])
    P_image = sensor2img(P_sensor, (0.00367, 0.00274), (640, 480), (0, 0))
    assert_array_almost_equal(P_image, np.array([[0, 0], [640, 480]]))


def test_world2image():
    cam2world = transform_from(matrix_from_euler_xyz([np.pi, 0, 0]),
                               [0, 0, 1.5])
    focal_length = 0.0036
    sensor_size = (0.00367, 0.00274)
    image_size = (640, 480)

    world_grid = make_world_grid()
    image_grid = world2image(world_grid, cam2world, sensor_size, image_size,
                             focal_length)
    expected_grid = make_world_grid(xlim=(110.73569482, 529.26430518),
                                    ylim=(450.2189781, 29.7810219))
    assert_array_almost_equal(image_grid, expected_grid[:, :2])
