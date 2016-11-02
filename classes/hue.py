
from phue import Bridge, Light
import config

bridge = None
LIGHTS = [config.LIGHT_ONE, config.LIGHT_TWO]


def activate(connect=False):
    global bridge
    if bridge is None:
        bridge = Bridge(config.IP_ADDRESS)
        bridge.set_light(LIGHTS, 'on', True)

    if connect:
        bridge.connect()


def get_light(light_id):
    global bridge
    return Light(bridge, light_id)


def rgb_convert(rgb):
    """Converts RGB tuple per specs http://www.developers.meethue.com/documentation/color-conversions-rgb-xy"""
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0
    red = pow((r + 0.055) / (1.0 + 0.055), 2.4) if r > 0.04045 else r / 12.92
    green = pow((g + 0.055) / (1.0 + 0.055), 2.4) if g > 0.04045 else g / 12.92
    blue = pow((b + 0.055) / (1.0 + 0.055), 2.4) if b > 0.04045 else b / 12.92
    x = red * 0.664511 + green * 0.154324 + blue * 0.162028
    y = red * 0.283881 + green * 0.668433 + blue * 0.047685
    z = red * 0.000088 + green * 0.072310 + blue * 0.986039
    return (x / (x + y + z), y / (x + y + z))
