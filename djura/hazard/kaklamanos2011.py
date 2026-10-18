"""
Rupture geometry relations (Kaklamanos et al. 2011)

Notes
-----
Assumptions:

- Planar rupture with a straight top edge.
- Style of faulting from rake: strike-slip for |rake| <= 45 or >= 135,
  otherwise reverse (rake > 0) or normal.
- Width from magnitude and style of faulting (Wells and Coppersmith 1994,
  as given by Kaklamanos et al.).
- Distances are for a site perpendicular to strike (ry0 = 0): on the
  footwall rx = -rjb, on a vertical fault |rx| = rjb.
- The hypocentre lies on the same perpendicular line as the site, i.e. no
  along-strike offset between them.

References
----------
Kaklamanos J, Baise LG, Boore DM (2011) Estimating unknown input parameters
when implementing the NGA ground-motion prediction equations in engineering
practice. Earthquake Spectra 27(4): 1219-1235.
"""
import numpy as np
from scipy.optimize import brentq


def style_of_faulting(rake) -> np.ndarray:
    """'SS', 'R' or 'N' from rake"""
    rake = np.asarray(rake, dtype=float)
    ss = (np.abs(rake) <= 45) | (np.abs(rake) >= 135)
    return np.where(ss, "SS", np.where(rake > 0, "R", "N"))


def rupture_width(mag, style):
    """Down-dip rupture width [km] from magnitude and style of faulting"""
    return np.where(style == "SS", 10 ** (-0.76 + 0.27 * mag),
                    np.where(style == "R", 10 ** (-1.61 + 0.41 * mag),
                             10 ** (-1.14 + 0.35 * mag)))


def rrup_from_rx(rx: float, ztor: float, dip: float, width: float) -> float:
    """Rrup of a site perpendicular to strike (Ry = 0)"""
    d = np.radians(dip)
    if dip >= 90 or rx < ztor * np.tan(d):
        return np.hypot(rx, ztor)
    if rx <= ztor * np.tan(d) + width / np.cos(d):
        return rx * np.sin(d) + ztor * np.cos(d)
    return np.hypot(rx - width * np.cos(d), ztor + width * np.sin(d))


def rjb_rx_from_rrup(rrup: float, ztor: float, dip: float, width: float,
                     side: str = "footwall") -> tuple:
    """Solve rjb and rx of a site perpendicular to strike from rrup

    Parameters
    ----------
    rrup : float
        Closest distance to the rupture [km]
    ztor : float
        Depth to top of rupture [km]
    dip : float
        Dip [deg]
    width : float
        Down-dip width [km]
    side : str, optional
        'footwall' or 'hanging_wall', by default 'footwall'

    Returns
    -------
    tuple
        rjb, rx [km]
    """
    if rrup <= ztor:  # closer than the top of the rupture
        return 0.0, 0.0
    if side == "footwall" or dip >= 90:
        rjb = np.sqrt(rrup ** 2 - ztor ** 2)
        return float(rjb), float(-rjb if side == "footwall" else rjb)

    # Hanging wall: rjb = 0 above the rupture, rx = rjb + W cos(dip) beyond
    edge = width * np.cos(np.radians(dip))
    if rrup <= rrup_from_rx(edge, ztor, dip, width):
        rx = brentq(lambda x: rrup_from_rx(x, ztor, dip, width) - rrup,
                    0.0, edge)
        return 0.0, float(rx)
    rjb = brentq(lambda r: rrup_from_rx(r + edge, ztor, dip, width) - rrup,
                 0.0, rrup)
    return float(rjb), float(rjb + edge)


def hypocentral_distances(rx: float, ztor: float, dip: float,
                          hypo_depth: float) -> tuple:
    """Repi and rhypo of a site perpendicular to strike through the
    hypocentre

    Parameters
    ----------
    rx : float
        Horizontal distance from the top edge, positive on the hanging
        wall [km]
    ztor : float
        Depth to top of rupture [km]
    dip : float
        Dip [deg]
    hypo_depth : float
        Hypocentral depth [km]

    Returns
    -------
    tuple
        repi, rhypo [km]
    """
    # Horizontal offset of the hypocentre from the top edge
    offset = 0.0 if dip >= 90 else \
        (hypo_depth - ztor) / np.tan(np.radians(dip))
    repi = abs(rx - offset)
    return float(repi), float(np.hypot(repi, hypo_depth))
