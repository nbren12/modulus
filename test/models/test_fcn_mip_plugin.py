from modulus.utils.sfno.YParams import ParamsBase
from modulus.models.fcn_mip_plugin import sfno
from modulus.models.registry import Package
from modulus.models.sfno.sfnonet import SphericalFourierNeuralOperatorNet
import datetime
import torch
import json


def save_checkpoint(model, check_point_path):
    model_state = {f"module.{k}": v for k, v in model.state_dict().items()}
    # This buffer is not present in some trained model checkpoints
    del model_state['module.device_buffer']
    checkpoint = {'model_state': model_state}
    torch.save(checkpoint, check_point_path)


def save_mock_package(path):

    config = {
        "N_in_channels": 2,
        "N_out_channels": 1,
        "img_shape_x": 4,
        "img_shape_y": 5,
        "scale_factor": 1,
        "num_layers": 2,
        "num_blocks": 2,
        "embed_dim": 2,
        "nettype": "sfno",
        "add_zenith": True
    }
    params = ParamsBase()
    params.update_params(config)
    model = SphericalFourierNeuralOperatorNet(params)

    config_path = path / "config.json"
    with config_path.open("w") as f:
        json.dump(params.to_dict(), f)

    check_point_path = path / "weights.tar"
    save_checkpoint(model, check_point_path)

    url = f"file://{path.as_posix()}"
    package = Package(url, seperator="/")
    return package


def test_sfno(tmp_path):
    # Can be tested against this URL too (but it is slow):
    # url = "s3://sw_climate_fno/nbrenowitz/model_packages/sfno_coszen"
    # package = Package(url, "/")
    package = save_mock_package(tmp_path)

    model = sfno(package, pretrained=True)
    x = torch.ones(1, 1, model.model.h, model.model.w)
    time = datetime.datetime(2018, 1, 1)
    with torch.no_grad():
        out = model(x, time=time)

    assert out.shape == x.shape
