from pathlib import Path
from typing import Union
import numpy as np
from openquake.commonlib.datastore import DataStore
from openquake.hazardlib.contexts import read_cmakers, read_ctx_by_grp
from openquake.baselib.python3compat import decode
from openquake.hazardlib import valid
import numpy.lib.recfunctions as rfn


def get_context_from_dstore(dstore_path: Union[str, Path], im_ref: str = None,
                            n_rups: int = None, site_id: int = 0):
    """
    Extracts rupture context and hazard information from an OpenQuake
    datastore.

    This function reads and organizes contextual data, ground motion models,
    and hazard curves from an OpenQuake datastore for a specified site.
    It supports filtering of ruptures based on occurrence probabilities
    and converts ground motion intensity measure types (IMTs) to a consistent
    format. The result can be used for further record selection or hazard
    analysis.

    Parameters
    ----------
    dstore_path : str or Path
        Path to the OpenQuake datastore (`.hdf5`) file or directory.
    im_ref : str, optional
        Reference intensity measure type (IMT) to check for availability
        in the datastore. Used for validation.
    n_rups : int, optional
        Number of ruptures with the highest occurrence probability to consider
        (e.g., for record selection). If None, no filtering is applied.
    site_id : int, optional
        Index of the site for which the context is extracted.
        Default is 0 (first site in the datastore).

    Returns
    -------
    tuple
        A tuple containing:
        - result : dict
            A dictionary with the following keys:
                - 'ctx_by_grp': Contexts grouped by source model.
                - 'hazard-curves': Hazard curves (mean or realization).
                - 'lt-weights': Logic tree branch weights.
                - 'gsims': GSIMs and their configuration from the datastore.
                - 'gsim-weights': Weights associated with each GSIM.
                - 'data': Detailed GSIM type and initialization parameters.
                - 'im_ref': Reference IMT used.
                - 'imt': Dictionary of available IMTs in the hazard model.
                - 'invtime': Investigation time used in the analysis.
                - 'oq-poes': Probabilities of exceedance used in hazard
                computation.
                - 'phi_b': ndtr(truncation_level), assuming greater than 0.5.
                - 'totrups': Total number of ruptures in the model.
                - 'site-parameters': Site-specific parameters required by
                GSIMs.
                - 'required-parameters': Set of parameters required by GMPEs.
                - 'n_rups': Number of top ruptures to consider (if specified).
        - oq : openquake.commonlib.oqvalidation.OqParam
            The parsed OpenQuake input parameter object.

    Raises
    ------
    ValueError
        If `im_ref` is provided but not found among available IMTs in the
        datastore.

    Notes
    -----
    - The function currently supports a single logic tree branching level.
    - All IMTs are converted from `AvgSA` to `Sa_avg` to maintain consistency.
    - Only the specified `site_id` is used. Support for multiple sites via
      OpenQuake's `SiteCollection` may be added in the future.

    Example
    -------
    >>> ctx_data, oq = get_context_from_dstore("job-1234.hdf5", im_ref="PGA")
    >>> ctx_data["hazard-curves"].shape
    (1, 1, 20)  # (IMT, site, number of poes)
    """

    # n_rups = number of ruptures with highest weight to consider
    # will be used and processed during record selection

    def _get_gsim_parameters(dstore_gsims):
        all_gsims = []
        for item in dstore_gsims:
            decoded = item.decode('utf-8')
            if '[' in decoded and ']' in decoded:
                key = decoded[decoded.find('[') + 1:decoded.find(']')]
                content = decoded[decoded.find(']') + 1:].strip()

                # Parse the content into dictionary
                values = {}
                for line in content.split('\n'):
                    if '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip('"')
                        # Convert numbers to float if possible
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                        values[k] = v

                all_gsims.append({key: values})

        return all_gsims

    def _get_gsim_init_parameters(instance):
        import inspect

        init_method = instance.__init__

        # Get the signature of the __init__ method
        init_signature = inspect.signature(init_method)

        # Get the parameter names of __init__ (excluding 'self')
        init_params = [
            param for param in init_signature.parameters if param != "self"]

        # Extract variables and their values from the instance's __dict__
        variables_dict = {
            # Use getattr to safely fetch the attribute
            param: getattr(instance, param, None)
            for param in init_params
            if hasattr(instance, param)  # Ensure the attribute exists
        }

        return variables_dict

    def _convert_avgsa_to_sa_avg(s: str):
        if s is None:
            return s
        return s.replace('AvgSA', 'Sa_avg')

    def _convert_rsds_to_ds(s: str):
        if s is None:
            return s
        return s.replace('RSD', 'Ds')

    def _replace_dict_keys(data, old='AvgSA', new='Sa_avg'):
        new_dict = {}
        for key, value in data.items():
            new_key = key.replace(old, new)
            new_dict[new_key] = value
        return new_dict

    dstore = DataStore(str(dstore_path))

    # Context by each group (source model)
    ctx_by_grp = read_ctx_by_grp(dstore)
    oq = dstore["oqparam"]
    imtls = dict(oq.imtls)
    cmakers = read_cmakers(dstore)
    toms = decode(dstore['toms'][:])

    # for avgsa
    imtls = _replace_dict_keys(imtls)
    # for rsds
    imtls = _replace_dict_keys(imtls, 'RSD', 'Ds')

    try:
        im_ref = oq.im_ref
    except AttributeError:
        im_ref = im_ref

    im_ref = _convert_avgsa_to_sa_avg(im_ref)
    im_ref = _convert_rsds_to_ds(im_ref)

    if im_ref is not None:
        if im_ref not in imtls.keys():
            raise ValueError(f"IM*: {im_ref} not in the list of available IMs,"
                             " adjust input!")

    # Those correspond to outputs of OQ
    # hazard_curve-mean-<IMT>_<job_id>.csv
    if 'hcurves-stats' in dstore:  # shape (N, S, M, L1)
        curves = dstore.sel('hcurves-stats', stat='mean')
    else:  # there is only 1 realization
        curves = dstore.sel('hcurves-rlzs', rlz_id=0)

    all_gsims = _get_gsim_parameters(dstore['gsims'][:])

    add_data = {}
    for grp_id, ctxt in ctx_by_grp.items():
        # Site IDs, only one site allowed
        # TODO, add possibility to use SiteCollection of OQ
        ctx = ctxt[ctxt.sids == site_id]

        tom = valid.occurrence_model(toms[grp_id])
        cmaker = cmakers[grp_id]
        # poes = cmaker.poes
        phi_b = cmaker.phi_b
        invtime = cmaker.investigation_time
        gsims = cmaker.gsims

        gsims_type_converted = []
        gsim_parameters = []
        for key in gsims:
            gmm_name = key.__class__.__name__
            _gsim = {
                gmm_name: gsims[key]
            }

            gsim_parameter = _get_gsim_init_parameters(key)

            if list(_gsim.keys())[0] == "GmpeIndirectAvgSA":
                gsim_parameter = gsim_parameter['kwargs']
                _gsim = _replace_dict_keys(
                    _gsim, 'GmpeIndirectAvgSA',
                    gsim_parameter['gmpe_name']
                )

            gsims_type_converted.append(_gsim)
            gsim_parameters.append(gsim_parameter)

        add_data[grp_id] = {
            'gsims': gsims_type_converted,
            'parameters': gsim_parameters,
        }

        if len(ctx.probs_occur[0]):
            probs = np.array([np.sum(p[1:]) for p in ctx.probs_occur])
        else:
            probs = tom.get_probability_one_or_more_occurrences(
                ctx.occurrence_rate)

        ctx = rfn.append_fields(ctx, "probs", probs,
                                usemask=False).view(np.recarray)

        ctx_by_grp[grp_id] = ctx

    # Same GSIMs (i.e., required parameters) for all source models
    req_pars = cmaker.REQUIRES_DISTANCES | cmaker.REQUIRES_RUPTURE_PARAMETERS

    # Logic tree branch weights
    weights = dstore['weights'][:]

    return {
        'ctx_by_grp': ctx_by_grp,
        'hazard-curves': curves,
        'lt-weights': weights,
        'gsims': all_gsims,
        'gsim-weights': dstore['gweights'][:],
        'data': add_data,
        'im_ref': im_ref,
        'imt': imtls,
        'invtime': invtime,
        'oq-poes': oq.poes,
        'phi_b': phi_b,
        'totrups': len(dstore['rup/mag']),
        'site-parameters': oq.req_site_params,
        'required-parameters': req_pars,
        'n_rups': n_rups,
    }, oq
