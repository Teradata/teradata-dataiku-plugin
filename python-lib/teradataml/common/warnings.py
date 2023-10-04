# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: PankajVinod.Purandare@teradata.com
Secondary Owner:

teradataml.common.warnings
----------
A Warnings class for the teradataml Python module
"""
import warnings
class VantageRuntimeWarning(RuntimeWarning):
    """
    VantageRuntimeWarning is thrown whenever SQL execution on Vantage raises a warning.
    """
    pass

class TeradataMlRuntimeWarning(RuntimeWarning):
    """
    The TeradataMlRuntimeWarning is thrown whenever there are Warnings in runtime execution of objects in teradataml.
    """
    # For future purpose
    pass
